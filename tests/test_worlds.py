"""The examples in Webots: each world runs headless, and the robots report what they computed."""
import contextlib
import math
import os
import shutil
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

import pytest

WEBOTS = shutil.which("webots")
WORLDS = Path(__file__).resolve().parent.parent / "worlds"
TIMEOUT = 300  # seconds of real time: a world that takes longer is stuck
ROBOTS = 32
PRINTED = 1e-3  # metres: the robots print their positions rounded

pytestmark = [
    pytest.mark.webots,
    pytest.mark.skipif(WEBOTS is None, reason="webots is not on the PATH"),
]


@dataclass(frozen=True)
class Report:
    """What a robot printed: where it was and what it computed, at a time of the simulation."""

    time: float
    x: float
    y: float
    result: str


def run_world(world: str, until: float) -> dict[str, Report]:
    """
    Run ``worlds/<world>.wbt`` in Webots until every robot reported at ``until`` seconds or later.

    Returns:
        The last report of each robot, by name.
    """
    # Webots runs the controllers with the python3 on the PATH: this one, with phyelds.
    environment = {**os.environ, "PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ['PATH']}"}
    command = [WEBOTS, "--batch", "--mode=fast", "--no-rendering", "--minimize", "--stdout", "--stderr",
               str(WORLDS / f"{world}.wbt")]
    reports: dict[str, Report] = {}
    lines: list[str] = []
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          env=environment, start_new_session=True) as webots:

        def stop() -> None:
            # The launcher, webots-bin and the controllers share a new session: kill them all, even
            # a webots-bin stuck writing to this pipe, which would ignore a polite SIGTERM.
            with contextlib.suppress(ProcessLookupError):
                os.killpg(webots.pid, signal.SIGKILL)

        timer = threading.Timer(TIMEOUT, stop)
        timer.start()
        try:
            for line in webots.stdout:
                lines.append(line)
                if line.startswith("phyelds "):
                    _, name, time, x, y, result = line.split()
                    reports[name] = Report(float(time), float(x), float(y), result)
                if len(reports) == ROBOTS and all(report.time >= until for report in reports.values()):
                    break
        finally:
            timer.cancel()
            stop()
    assert len(reports) == ROBOTS, "".join(lines[-50:])
    return reports


def test_gradient_world_measures_the_distance_from_the_robots_under_the_red_light():
    reports = run_world("gradient", until=3.0)

    distances = {name: float(report.result) for name, report in reports.items()}
    sources = [report for name, report in reports.items() if distances[name] == 0.0]
    assert sources
    for name, report in reports.items():
        closest = min(math.dist((report.x, report.y), (source.x, source.y)) for source in sources)
        assert closest - PRINTED <= distances[name] < math.inf, name


def any_within(reports: list[Report], point: tuple[float, float], radius: float) -> bool:
    """Whether a robot is within ``radius`` of ``point``."""
    return any(math.dist((report.x, report.y), point) <= radius for report in reports)


def connected(reports: list[Report], reach: float) -> bool:
    """Whether the robots form one network, with a link between those within ``reach``."""
    unvisited, frontier = reports[1:], reports[:1]
    while frontier:
        robot = frontier.pop()
        near = [other for other in unvisited if math.dist((robot.x, robot.y), (other.x, other.y)) <= reach]
        unvisited = [other for other in unvisited if other not in near]
        frontier.extend(near)
    return not unvisited


def test_channel_world_lights_a_path_of_robots_from_the_red_to_the_blue_light():
    red_spot, blue_spot, spot, radio = (-0.40, -0.20), (0.40, 0.20), 0.09, 0.17  # as in worlds/channel.wbt

    reports = run_world("channel", until=3.0)

    inside = [report for report in reports.values() if report.result == "True"]
    assert any_within(inside, red_spot, spot)
    assert any_within(inside, blue_spot, spot)
    assert len(inside) < ROBOTS / 2
    assert connected(inside, radio)

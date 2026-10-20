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

from phyelds_webots_examples.formation import SHAPES

WEBOTS = shutil.which("webots")
WORLDS = Path(__file__).resolve().parent.parent / "worlds"
TIMEOUT = 300  # seconds of real time: a world that takes longer is stuck
ROBOTS = 32
PRINTED = 1e-3  # metres: the robots print their positions rounded
TIPPED = 0.5  # radians: a robot leaning this much is no longer on its wheels

pytestmark = [
    pytest.mark.webots,
    pytest.mark.skipif(WEBOTS is None, reason="webots is not on the PATH"),
]


@dataclass(frozen=True)
class Report:
    """What a robot printed at a time of the simulation: where it was, its tilt, what it computed."""

    time: float
    x: float
    y: float
    tilt: float
    result: str


def run_world(world: str, until: float) -> dict[str, list[Report]]:
    """
    Run ``worlds/<world>.wbt`` in Webots until every robot reported at ``until`` seconds or later.

    Returns:
        The reports of each robot, by name, from the first to the last.
    """
    # Webots runs the controllers with the python3 on the PATH: this one, with phyelds.
    environment = {**os.environ, "PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ['PATH']}"}
    command = [WEBOTS, "--batch", "--mode=fast", "--no-rendering", "--minimize", "--stdout", "--stderr",
               str(WORLDS / f"{world}.wbt")]
    reports: dict[str, list[Report]] = {}
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
                    _, name, time, x, y, tilt, result = line.split()
                    report = Report(float(time), float(x), float(y), float(tilt), result)
                    reports.setdefault(name, []).append(report)
                if len(reports) == ROBOTS and all(history[-1].time >= until for history in reports.values()):
                    break
        finally:
            timer.cancel()
            stop()
    assert len(reports) == ROBOTS, "".join(lines[-50:])
    return reports


def upright(histories: dict[str, list[Report]]) -> bool:
    """Whether every robot stayed on its wheels all along."""
    return all(report.tilt < TIPPED for history in histories.values() for report in history)


def last(histories: dict[str, list[Report]]) -> dict[str, Report]:
    """The last report of each robot, by name."""
    return {name: history[-1] for name, history in histories.items()}


def test_gradient_world_measures_the_distance_from_the_robots_under_the_red_light():
    reports = last(run_world("gradient", until=10.0))

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

    reports = last(run_world("channel", until=10.0))

    inside = [report for report in reports.values() if report.result == "True"]
    assert any_within(inside, red_spot, spot)
    assert any_within(inside, blue_spot, spot)
    assert len(inside) < ROBOTS / 2
    assert connected(inside, radio)


def test_flocking_world_moves_the_swarm_as_one_without_leaving_the_arena():
    half_arena, radio = 0.75, 0.17  # as in worlds/flocking.wbt

    histories = run_world("flocking", until=40.0)

    assert upright(histories)

    reports = list(last(histories).values())
    travelled = [
        sum(math.dist((a.x, a.y), (b.x, b.y)) for a, b in zip(history, history[1:]))
        for history in histories.values()
    ]
    assert min(travelled) > 1.0
    assert all(abs(report.x) < half_arena and abs(report.y) < half_arena for report in reports)
    agreement = [polarisation([float(history[second].result) for history in histories.values()])
                 for second in range(20, 40)]
    assert sum(agreement) / len(agreement) > 0.8
    assert all(any_within([other for other in reports if other is not report], (report.x, report.y), radio)
               for report in reports)


def polarisation(headings: list[float]) -> float:
    """How much the headings agree: 1 when all are the same, about 0 when they are scattered."""
    return math.hypot(sum(map(math.cos, headings)), sum(map(math.sin, headings))) / len(headings)


def test_formation_world_gathers_most_robots_inside_the_star():
    star = SHAPES[0][1]

    histories = run_world("formation", until=50.0)

    assert upright(histories)
    reports = last(histories).values()
    inside = [report for report in reports if star((report.x, report.y)) <= 0]
    assert len(inside) >= 0.75 * ROBOTS

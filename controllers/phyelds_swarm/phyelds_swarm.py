"""
The controller of every robot: it runs the aggregate program its argument names, round by round.

The program senses where the robot is on the floor and the light that falls on it from above,
and sets the colour of the LED on its top. Once a second of simulated time the robot prints
what it computed, for the tests: ``phyelds <name> <time> <x> <y> <result>``.

Webots runs it with the ``python3`` on the PATH, which needs phyelds: open the worlds with
``poetry run webots worlds/<example>.wbt``.
"""
import sys
from collections.abc import Callable
from typing import Any

from controller import Robot  # pylint: disable=import-error

from phyelds.webots import AggregateController

from phyelds_webots_examples.channel import channel
from phyelds_webots_examples.gradient import gradient
from phyelds_webots_examples.lights import blue_light, led, red_light

PROGRAMS: dict[str, Callable[[], Any]] = {"gradient": gradient, "channel": channel}
STEPS_PER_ROUND = 4  # 128 ms between rounds: enough to steer, and the simulation runs far faster
REPORT_PERIOD = 1.0  # seconds of simulated time between two reports


def main() -> None:
    """Run the program named by the first argument, a round every few steps of the simulation."""
    robot = Robot()
    time_step = int(robot.getBasicTimeStep())
    gps, red, blue = (robot.getDevice(name) for name in ("gps", red_light.name, blue_light.name))
    for device in (gps, red, blue):
        device.enable(time_step)

    def sensors() -> dict[str, Any]:
        x, y, _ = gps.getValues()
        return {
            "position": (x, y),
            red_light.name: red.getValue(),
            blue_light.name: blue.getValue(),
        }

    aggregate_controller = AggregateController(
        robot, PROGRAMS[sys.argv[1]], emitter="radio_tx", receiver="radio_rx", sensors=sensors
    )
    top = robot.getDevice("ledrgb")
    next_report = 0.0
    while robot.step(STEPS_PER_ROUND * time_step) != -1:
        result = aggregate_controller.run_round()
        top.set(led.read(aggregate_controller.outputs, default=0))
        if robot.getTime() >= next_report:
            x, y, _ = gps.getValues()
            report = f"{robot.getName()} {robot.getTime():.3f} {x:.4f} {y:.4f} {result}"
            print("phyelds", report, flush=True)
            next_report += REPORT_PERIOD


if __name__ == "__main__":
    main()

"""
The controller of every robot: it runs the aggregate program its argument names, round by round.

The other arguments describe the wheels, for robots other than the Elisa-3:
``--wheel-radius`` in metres, and ``--wheels`` with the names of the left and right motor.

The program senses where the robot is on the floor and the light that falls on it from above;
it sets the colour of the LED on top of the robot, and the velocity the wheels follow, which
``phyelds.webots.Body`` applies. Once a second of simulated time the robot prints where it is,
how much it tilts and what it computed, for the tests:
``phyelds <name> <time> <x> <y> <tilt> <result>``.

Webots runs it with the ``python3`` on the PATH, which needs phyelds: open the worlds with
``poetry run webots worlds/<example>.wbt``.
"""
import argparse
import random
from collections.abc import Callable
from typing import Any

from controller import Robot  # pylint: disable=import-error

from phyelds.webots import AggregateController, Body
from phyelds.webots.body import WHEELS

from phyelds_webots_examples.channel import channel
from phyelds_webots_examples.flocking import flocking
from phyelds_webots_examples.formation import formation
from phyelds_webots_examples.gradient import gradient
from phyelds_webots_examples.lights import blue_light, red_light

PROGRAMS: dict[str, Callable[[], Any]] = {
    "gradient": gradient,
    "channel": channel,
    "flocking": flocking,
    "formation": formation,
}
STEPS_PER_ROUND = 4  # 128 ms between rounds: enough to steer, and the simulation runs far faster
REPORT_PERIOD = 1.0  # seconds of simulated time between two reports
WHEEL_RADIUS = 0.0045  # metres, as in the Elisa3 proto


def arguments() -> argparse.Namespace:
    """The program the robot runs, and its wheels, as the world gives them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("program", choices=PROGRAMS)
    parser.add_argument("--wheel-radius", type=float, default=WHEEL_RADIUS)
    parser.add_argument("--wheels", nargs=2, default=WHEELS)
    return parser.parse_args()


def main() -> None:
    """Run the program named by the first argument, a round every few steps of the simulation."""
    given = arguments()
    robot = Robot()
    random.seed(robot.getName())
    time_step = int(robot.getBasicTimeStep())
    body = Body(robot, wheel_radius=given.wheel_radius, wheels=given.wheels)
    gps, imu = robot.getDevice("gps"), robot.getDevice("inertial unit")
    lights = {name: robot.getDevice(name) for name in (red_light.name, blue_light.name)}
    for sensor in (gps, *lights.values()):
        sensor.enable(time_step)

    def sense() -> dict[str, Any]:
        """Where the robot is on the floor, and the light from above."""
        x, y, _ = gps.getValues()
        return {"position": (x, y), **{name: light.getValue() for name, light in lights.items()}}

    aggregate_controller = AggregateController(
        robot, PROGRAMS[given.program], emitter="radio_tx", receiver="radio_rx", sensors=sense
    )
    next_report = 0.0
    while robot.step(STEPS_PER_ROUND * time_step) != -1:
        result = aggregate_controller.run_round()
        body.act(aggregate_controller.outputs)
        if robot.getTime() >= next_report:
            report(robot, gps, imu, result)
            next_report += REPORT_PERIOD


def report(robot: Robot, gps: Any, imu: Any, result: Any) -> None:
    """Print where the robot is on the floor, how far it leans, and what it computed."""
    x, y, _ = gps.getValues()
    roll, pitch, _ = imu.getRollPitchYaw()
    where = f"{x:.4f} {y:.4f} {max(abs(roll), abs(pitch)):.3f}"
    print("phyelds", robot.getName(), f"{robot.getTime():.3f}", where, result, flush=True)


if __name__ == "__main__":
    main()

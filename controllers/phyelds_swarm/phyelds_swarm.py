"""
The controller of every robot: it runs the aggregate program its argument names, round by round.

The program senses where the robot is on the floor and the light that falls on it from above;
it sets the colour of the LED on top of the robot, and the velocity the wheels follow. Once a
second of simulated time the robot prints what it computed, for the tests:
``phyelds <name> <time> <x> <y> <result>``.

Webots runs it with the ``python3`` on the PATH, which needs phyelds: open the worlds with
``poetry run webots worlds/<example>.wbt``.
"""
import math
import random
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from controller import Robot  # pylint: disable=import-error

from phyelds.libraries.device import velocity
from phyelds.webots import AggregateController

from phyelds_webots_examples.channel import channel
from phyelds_webots_examples.drive import wheel_speeds
from phyelds_webots_examples.flocking import flocking
from phyelds_webots_examples.gradient import gradient
from phyelds_webots_examples.lights import blue_light, led, red_light

PROGRAMS: dict[str, Callable[[], Any]] = {
    "gradient": gradient,
    "channel": channel,
    "flocking": flocking,
}
STEPS_PER_ROUND = 4  # 128 ms between rounds: enough to steer, and the simulation runs far faster
REPORT_PERIOD = 1.0  # seconds of simulated time between two reports


@dataclass(frozen=True)
class Body:
    """The devices of a SwarmElisa that the programs sense and drive."""

    gps: Any
    imu: Any
    lights: dict[str, Any]
    top: Any
    wheels: tuple[Any, Any]

    @classmethod
    def of_robot(cls, robot: Robot, time_step: int) -> "Body":
        """The devices of ``robot``, the sensors enabled and the wheels still."""
        gps, imu = robot.getDevice("gps"), robot.getDevice("inertial unit")
        lights = {name: robot.getDevice(name) for name in (red_light.name, blue_light.name)}
        for sensor in (gps, imu, *lights.values()):
            sensor.enable(time_step)
        wheels = (robot.getDevice("left wheel motor"), robot.getDevice("right wheel motor"))
        for wheel in wheels:
            wheel.setPosition(math.inf)  # velocity control, which starts at full speed: stop it
            wheel.setVelocity(0.0)
        return cls(gps, imu, lights, robot.getDevice("ledrgb"), wheels)

    def position(self) -> tuple[float, float]:
        """Where the robot is on the floor, in metres."""
        x, y, _ = self.gps.getValues()
        return x, y

    def sense(self) -> dict[str, Any]:
        """The sensors of the program: the position, and the light from above."""
        lights = {name: light.getValue() for name, light in self.lights.items()}
        return {"position": self.position(), **lights}

    def act(self, outputs: Mapping[str, Any]) -> None:
        """Light the LED and drive the wheels as the program says: dark and still if it does not."""
        self.top.set(led.read(outputs, default=0))
        target = velocity.read(outputs, default=(0.0, 0.0))
        for wheel, speed in zip(self.wheels, wheel_speeds(target, self.imu.getRollPitchYaw()[2])):
            wheel.setVelocity(speed)


def main() -> None:
    """Run the program named by the first argument, a round every few steps of the simulation."""
    robot = Robot()
    random.seed(robot.getName())
    time_step = int(robot.getBasicTimeStep())
    body = Body.of_robot(robot, time_step)
    aggregate_controller = AggregateController(
        robot, PROGRAMS[sys.argv[1]], emitter="radio_tx", receiver="radio_rx", sensors=body.sense
    )
    next_report = 0.0
    while robot.step(STEPS_PER_ROUND * time_step) != -1:
        result = aggregate_controller.run_round()
        body.act(aggregate_controller.outputs)
        if robot.getTime() >= next_report:
            x, y = body.position()
            report = f"{robot.getName()} {robot.getTime():.3f} {x:.4f} {y:.4f} {result}"
            print("phyelds", report, flush=True)
            next_report += REPORT_PERIOD


if __name__ == "__main__":
    main()

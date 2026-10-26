"""
Flocking: the boids of Reynolds, every robot steering as its neighbours do, so that the swarm
moves as one.

Three rules turn the heading of a robot, each by how much it counts: keep apart from the
closest robots (separation), head as the neighbours head (alignment) and towards them
(cohesion); and turn back near the walls of the arena. The robot drives along its heading at
a cruise speed, and its LED shows the heading: a flock that agrees has one colour.
"""
import math

from phyelds.calculus import aggregate, remember_and_evolve
from phyelds.experimental.swarm import (
    Vector,
    alignment,
    avoid_obstacles,
    brownian,
    cohesion,
    separation,
)
from phyelds.libraries.device import led, local_position, velocity

from phyelds_webots_examples.lights import hue

HALF_ARENA = 0.75
"""Half the side of the square arena, in metres: its walls are this far from the centre."""

SPEED = 0.08
"""The cruise speed, in m/s."""

SPACE = 0.08
"""How close, in metres, a robot lets another come: the Elisa-3 are 5 cm wide."""

SEPARATION, ALIGNMENT, COHESION = 0.4, 0.6, 0.02
"""How much each rule turns the heading of a robot in a round."""

MARGIN = 0.15
"""How close to a wall, in metres, a robot starts turning back."""

WALL_PUSH = 0.1
"""How gently the walls push: at ``d`` metres from a wall, ``(MARGIN - d) / WALL_PUSH``."""


def walls() -> list[Vector]:
    """The vector from the robot to each wall of the arena."""
    x, y = local_position()
    return [
        Vector(-HALF_ARENA - x, 0),
        Vector(HALF_ARENA - x, 0),
        Vector(0, -HALF_ARENA - y),
        Vector(0, HALF_ARENA - y),
    ]


def steer(heading: Vector) -> Vector:
    """The new heading of the robot, from the one it had: the three rules, and off the walls."""
    turn = (
        separation(heading, within=SPACE) * SEPARATION
        + alignment(heading) * ALIGNMENT
        + cohesion(heading) * COHESION
    )
    return (heading + turn + avoid_obstacles(walls(), MARGIN, norm=WALL_PUSH)).normalize()


@aggregate
def flocking() -> float:
    """Fly with the flock: send the velocity of the robot, and return its heading, in radians."""
    heading = remember_and_evolve(brownian(), lambda previous: steer(previous.value)).value
    angle = math.atan2(heading.y, heading.x)
    velocity.send(heading * SPEED)
    led.send(hue(angle / math.tau))
    return angle

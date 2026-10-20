"""How an Elisa-3 follows a velocity: it turns towards it and drives, as its wheels allow."""
import math
from collections.abc import Iterable

WHEEL_RADIUS = 0.0045
"""The radius of the wheels, in metres, as in the Elisa3 proto."""

AXLE = 0.04
"""The distance between the wheels, in metres."""

MAX_WHEEL_SPEED = 133.33
"""The top speed of the wheels, in rad/s."""

TURN_GAIN = 4.0
"""How fast the robot turns, in rad/s, for each radian between its heading and the velocity."""


def wheel_speeds(velocity: Iterable[float], heading: float) -> tuple[float, float]:
    """
    The speeds of the wheels that take the robot along ``velocity``.

    The robot turns towards the velocity, and drives forward as much as it already heads along
    it, never backwards. When a wheel would go faster than it can, both slow down by the same
    factor, so that the robot keeps turning on the same arc.

    Args:
        velocity: Where to go, in m/s, in the frame of the world: x and y (a z is ignored).
        heading: Where the robot faces, in radians from the x axis of the world.

    Returns:
        The speeds of the left and of the right wheel, in rad/s.
    """
    x, y, *_ = velocity
    speed = math.hypot(x, y)
    if speed == 0:
        return 0.0, 0.0
    error = math.remainder(math.atan2(y, x) - heading, math.tau)
    forward = speed * max(0.0, math.cos(error))
    turn = TURN_GAIN * error * AXLE / 2
    left, right = (forward - turn) / WHEEL_RADIUS, (forward + turn) / WHEEL_RADIUS
    scale = max(1.0, abs(left) / MAX_WHEEL_SPEED, abs(right) / MAX_WHEEL_SPEED)
    return left / scale, right / scale

"""The lights of a robot: the colours of the LED on its top, and the spots it senses from above."""
import colorsys

from phyelds.libraries.device import Sensor

red_light: Sensor[float] = Sensor("red light")
"""How much red light falls on the robot from above, in W/m²."""

blue_light: Sensor[float] = Sensor("blue light")
"""How much blue light falls on the robot from above, in W/m²."""

LIGHT_THRESHOLD = 0.5
"""The irradiance, in W/m², above which a robot is in the spot of a light."""


def is_lit(light: Sensor[float]) -> bool:
    """Whether the robot is in a spot of ``light``; a robot without the sensor is not."""
    return (light.sense() or 0.0) > LIGHT_THRESHOLD


def hue(turn: float) -> tuple[int, int, int]:
    """
    The bright colour a ``turn`` round the colour wheel.

    Args:
        turn: The fraction of the wheel: 0 is red, 1/3 green, 2/3 blue, and 1 red again.

    Returns:
        The colour, as red, green and blue channels in 0–255, as ``led`` takes it.
    """
    red, green, blue = colorsys.hsv_to_rgb(turn % 1.0, 1.0, 1.0)
    return round(red * 255), round(green * 255), round(blue * 255)

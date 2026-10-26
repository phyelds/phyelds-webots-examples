"""
The gradient: every robot learns how far it is from the red light, and shows it.

The robots under the spot of the red light sense it; the others only know how far their
neighbours are, and the distance spreads from robot to robot. The LED goes from red,
under the light, to blue, far from it.
"""
from phyelds.calculus import aggregate
from phyelds.libraries.device import led
from phyelds.libraries.distances import neighbors_distances
from phyelds.libraries.spreading import distance_to

from phyelds_webots_examples.lights import hue, is_lit, red_light

FAR = 0.8
"""The distance, in metres, from which a robot is as blue as it gets."""


@aggregate
def gradient() -> float:
    """The distance, in metres, from the closest robot in the spot of the red light."""
    distance = distance_to(is_lit(red_light), neighbors_distances())
    led.send(hue(2 / 3 * min(distance / FAR, 1.0)))
    return distance

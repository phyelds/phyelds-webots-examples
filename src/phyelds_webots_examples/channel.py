"""
The channel: the robots on the shortest path between the red and the blue light light up.

A red spot and a blue one shine on a few robots each, the ends of the channel. Every robot
learns how far it is from either end and how far the ends are from each other, through its
neighbours only: a robot whose two distances add up to the one between the ends is on a
shortest path, and turns its LED yellow. The ends show the colour of their light.
"""
from phyelds.calculus import aggregate
from phyelds.libraries import spreading
from phyelds.libraries.device import led
from phyelds.libraries.distances import neighbors_distances

from phyelds_webots_examples.lights import blue_light, is_lit, red_light

WIDTH = 0.001
"""How much longer than the shortest, in metres, a path through the channel can be: only as
much as the rounding of the distances takes, or a swarm on a grid would light up a band."""

RED, BLUE, YELLOW, OFF = (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 0, 0)


@aggregate
def channel() -> bool:
    """Whether the robot is on a shortest path between the red and the blue light."""
    source, target = is_lit(red_light), is_lit(blue_light)
    inside = spreading.channel(source, target, WIDTH, neighbors_distances())
    if source:
        led.send(RED)
    elif target:
        led.send(BLUE)
    else:
        led.send(YELLOW if inside else OFF)
    return inside

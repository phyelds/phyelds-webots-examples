"""
Formation: the swarm spreads evenly over a star.

The star is a signed distance function, negative inside. Every robot knows where it is and
moves to spread evenly over the star with its neighbours: inside, towards the centre of the
space it has to itself; outside, back in across the border. The LED tells whether the robot is
inside the star. The swarm fills the body of the star in seconds, and takes a few minutes to
reach into the tips.
"""
from phyelds.calculus import aggregate
from phyelds.experimental import formation as sdf
from phyelds.libraries.device import led, local_position, velocity

from phyelds_webots_examples.lights import hue

RADIO = 0.17
"""How far the radio of the robots reaches, in metres, as in SwarmElisa."""

STAR = sdf.star((0, 0), 0.5, 5)
"""The shape the swarm takes: a star with five points, 0.5 m from its centre to a tip."""

INSIDE, OUTSIDE = hue(1 / 3), hue(1 / 12)
"""The colours of a robot inside the star, green, and outside it, orange."""


@aggregate
def formation() -> bool:
    """Spread over the star; whether the robot is inside it."""
    velocity.send(sdf.formation(STAR, reach=RADIO / 2))
    inside = STAR(local_position()) <= 0
    led.send(INSIDE if inside else OUTSIDE)
    return inside

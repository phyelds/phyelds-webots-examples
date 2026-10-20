"""
Formation: the swarm takes one shape after another, a star, a ring, then two crossed strokes.

Each shape is a signed distance function, negative inside. Every robot knows where it is and
moves to spread evenly over the shape with its neighbours: inside, towards the centre of the
space it has to itself; outside, back in across the border. The LED tells whether the robot is
inside the shape of the moment.
"""
from phyelds.calculus import aggregate
from phyelds.experimental import formation as sdf
from phyelds.libraries.device import local_position, velocity
from phyelds.libraries.time import local_time

from phyelds_webots_examples.lights import hue, led

RADIO = 0.17
"""How far the radio of the robots reaches, in metres, as in SwarmElisa."""

CROSS = sdf.segment((-0.45, -0.45), (0.45, 0.45)) | sdf.segment((-0.45, 0.45), (0.45, -0.45))

SHAPES: list[tuple[float, sdf.Shape]] = [
    (0.0, sdf.star((0, 0), 0.5, 5)),
    (60.0, sdf.circle((0, 0), 0.45).ring(0.1)),
    (120.0, CROSS.expand(0.08)),
]
"""The shapes, each with the second it starts at."""

INSIDE, OUTSIDE = hue(1 / 3), hue(1 / 12)
"""The colours of a robot inside the shape, green, and outside it, orange."""


def shape_at(time: float) -> sdf.Shape:
    """The shape the swarm takes at ``time``, in seconds: the last one started."""
    return [shape for start, shape in SHAPES if start <= time][-1]


@aggregate
def formation() -> bool:
    """Spread over the shape of the moment; whether the robot is inside it."""
    shape = shape_at(local_time())
    velocity.send(sdf.formation(shape, reach=RADIO / 2))
    inside = shape(local_position()) <= 0
    led.send(INSIDE if inside else OUTSIDE)
    return inside

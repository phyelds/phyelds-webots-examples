import math
import random

import pytest

from phyelds.libraries.device import led, velocity

from phyelds_webots_examples.flocking import SPEED, flocking
from phyelds_webots_examples.lights import hue
from tests.simulation import grid, outputs, results, run


@pytest.fixture(autouse=True)
def seed():
    random.seed(0)


def polarisation(headings: list[float]) -> float:
    """How much the headings agree: 1 when all are the same, about 0 when they are scattered."""
    return math.hypot(sum(map(math.cos, headings)), sum(map(math.sin, headings))) / len(headings)


def test_flocking_aligns_the_headings_of_the_robots():
    simulator = grid(4, 4, spacing=0.1)

    run(simulator, flocking, rounds=60)

    assert polarisation(results(simulator)) > 0.95


def test_flocking_moves_every_robot_at_the_cruise_speed_along_its_heading():
    simulator = grid(3, 3, spacing=0.1)

    run(simulator, flocking, rounds=5)

    for heading, (x, y, _) in zip(results(simulator), outputs(simulator, velocity.name)):
        assert (x, y) == pytest.approx((SPEED * math.cos(heading), SPEED * math.sin(heading)))


def test_flocking_colours_a_robot_by_its_heading():
    simulator = grid(3, 3, spacing=0.1)

    run(simulator, flocking, rounds=5)

    assert outputs(simulator, led.name) == [hue(heading / math.tau) for heading in results(simulator)]

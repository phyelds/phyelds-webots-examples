import pytest

from phyelds_webots_examples.gradient import FAR, gradient
from phyelds_webots_examples.lights import LIGHT_THRESHOLD, led, red_light
from tests.simulation import line, outputs, results, run

UNDER_THE_LIGHT = {0: {red_light.name: 2 * LIGHT_THRESHOLD}}


def test_gradient_is_the_distance_from_the_robots_under_the_red_light():
    simulator = line(4, spacing=0.1, sensors=UNDER_THE_LIGHT)

    run(simulator, gradient, rounds=10)

    assert results(simulator) == pytest.approx([0.0, 0.1, 0.2, 0.3])


def test_gradient_colours_the_robots_from_red_under_the_light_to_blue_far_from_it():
    simulator = line(3, spacing=FAR, sensors=UNDER_THE_LIGHT)

    run(simulator, gradient, rounds=10)

    assert outputs(simulator, led.name) == [0xFF0000, 0x0000FF, 0x0000FF]


def test_gradient_is_infinite_without_a_red_light():
    simulator = line(2, spacing=0.1)

    run(simulator, gradient, rounds=10)

    assert results(simulator) == [float("inf"), float("inf")]

from phyelds_webots_examples.formation import INSIDE, OUTSIDE, SHAPES, formation
from phyelds_webots_examples.lights import led
from tests.simulation import grid, outputs, positions, results, run

ROUND = 0.128  # seconds between two rounds, as in Webots
STAR = SHAPES[0][1]


def test_formation_brings_the_robots_into_the_star_first():
    simulator = grid(4, 3, spacing=0.1, origin=(0.7, 0.7))

    run(simulator, formation, rounds=150, period=ROUND, moving=True)

    assert all(STAR(position) <= 0 for position in positions(simulator))


def test_formation_tells_whether_a_robot_is_inside_the_shape_and_colours_it():
    simulator = grid(2, 1, spacing=0.1, origin=(-0.05, 0.0))

    run(simulator, formation, rounds=1, period=ROUND)

    assert results(simulator) == [True, True]
    assert outputs(simulator, led.name) == [INSIDE, INSIDE]


def test_formation_colours_the_robots_outside_the_shape_apart():
    simulator = grid(2, 1, spacing=0.1, origin=(0.9, 0.9))

    run(simulator, formation, rounds=1, period=ROUND)

    assert results(simulator) == [False, False]
    assert outputs(simulator, led.name) == [OUTSIDE, OUTSIDE]

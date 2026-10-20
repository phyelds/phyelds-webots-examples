from phyelds_webots_examples.formation import INSIDE, OUTSIDE, STAR, formation
from phyelds_webots_examples.lights import led
from tests.simulation import grid, outputs, positions, results, run

ROUND = 0.128  # seconds between two rounds, as in Webots


def test_formation_brings_the_robots_into_the_star():
    simulator = grid(4, 3, spacing=0.1, origin=(0.7, 0.7))

    run(simulator, formation, rounds=150, period=ROUND, moving=True)

    assert all(STAR(position) <= 0 for position in positions(simulator))


def test_formation_keeps_to_the_star_however_long_it_runs():
    simulator = grid(1, spacing=0.1, origin=(0.0, 0.35))

    run(simulator, formation, rounds=2, period=200.0)

    assert results(simulator) == [True]


def test_formation_tells_whether_a_robot_is_inside_the_star_and_colours_it():
    simulator = grid(2, 1, spacing=0.1, origin=(-0.05, 0.0))

    run(simulator, formation, rounds=1, period=ROUND)

    assert results(simulator) == [True, True]
    assert outputs(simulator, led.name) == [INSIDE, INSIDE]


def test_formation_colours_the_robots_outside_the_star_apart():
    simulator = grid(2, 1, spacing=0.1, origin=(0.9, 0.9))

    run(simulator, formation, rounds=1, period=ROUND)

    assert results(simulator) == [False, False]
    assert outputs(simulator, led.name) == [OUTSIDE, OUTSIDE]

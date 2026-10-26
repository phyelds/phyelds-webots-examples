from phyelds.libraries.device import led

from phyelds_webots_examples.channel import channel
from phyelds_webots_examples.lights import LIGHT_THRESHOLD, blue_light, red_light
from tests.simulation import grid, outputs, results, run

# Five columns and three rows: the red light on the left of the middle row, the blue on its right.
SOURCE, TARGET = 0 * 3 + 1, 4 * 3 + 1
MIDDLE_ROW = [column * 3 + 1 for column in range(5)]
LIGHTS = {SOURCE: {red_light.name: 2 * LIGHT_THRESHOLD}, TARGET: {blue_light.name: 2 * LIGHT_THRESHOLD}}


def test_channel_is_the_shortest_path_between_the_red_and_the_blue_light():
    simulator = grid(5, 3, spacing=0.1, sensors=LIGHTS)

    run(simulator, channel, rounds=20)

    assert [robot for robot, inside in enumerate(results(simulator)) if inside] == MIDDLE_ROW


def test_channel_lights_the_ends_red_and_blue_the_path_yellow_and_turns_the_others_off():
    simulator = grid(5, 3, spacing=0.1, sensors=LIGHTS)

    run(simulator, channel, rounds=20)

    colours = outputs(simulator, led.name)
    assert (colours[SOURCE], colours[TARGET]) == ((255, 0, 0), (0, 0, 255))
    assert {colours[robot] for robot in MIDDLE_ROW[1:-1]} == {(255, 255, 0)}
    assert {colour for robot, colour in enumerate(colours) if robot not in MIDDLE_ROW} == {(0, 0, 0)}


def test_channel_is_empty_without_a_blue_light():
    simulator = grid(5, 3, spacing=0.1, sensors={SOURCE: LIGHTS[SOURCE]})

    run(simulator, channel, rounds=20)

    assert not any(results(simulator))

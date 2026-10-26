from phyelds_webots_examples.lights import hue


def test_hue_goes_round_the_colour_wheel_from_red():
    turns = (0, 1 / 3, 2 / 3, 1)

    colours = [hue(turn) for turn in turns]

    assert colours == [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0)]

from phyelds_webots_examples.lights import hue


def test_hue_goes_round_the_colour_wheel_from_red():
    turns = (0, 1 / 3, 2 / 3, 1)

    colours = [hue(turn) for turn in turns]

    assert colours == [0xFF0000, 0x00FF00, 0x0000FF, 0xFF0000]

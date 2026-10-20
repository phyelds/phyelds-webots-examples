import math

import pytest

from phyelds_webots_examples.drive import MAX_WHEEL_SPEED, WHEEL_RADIUS, wheel_speeds


def test_wheel_speeds_stop_the_robot_when_the_velocity_is_zero():
    assert wheel_speeds((0.0, 0.0), heading=1.0) == (0.0, 0.0)


def test_wheel_speeds_go_straight_when_the_robot_heads_along_the_velocity():
    left, right = wheel_speeds((0.0, 0.1), heading=math.pi / 2)

    assert left == pytest.approx(right)
    assert left == pytest.approx(0.1 / WHEEL_RADIUS)


def test_wheel_speeds_turn_left_while_moving_when_the_velocity_points_ahead_on_the_left():
    left, right = wheel_speeds((0.1, 0.1), heading=0.0)

    assert right > left > 0


def test_wheel_speeds_turn_on_the_spot_when_the_velocity_points_behind():
    left, right = wheel_speeds((-0.1, 0.0), heading=0.0)

    assert right > 0
    assert left == pytest.approx(-right)


def test_wheel_speeds_do_not_depend_on_how_many_turns_the_heading_counts():
    same = wheel_speeds((0.1, 0.05), heading=-0.3 + 4 * math.pi)

    assert wheel_speeds((0.1, 0.05), heading=-0.3) == pytest.approx(same)


def test_wheel_speeds_slow_both_wheels_down_to_the_top_speed_and_keep_turning():
    left, right = wheel_speeds((10.0, 10.0), heading=0.0)

    assert right == pytest.approx(MAX_WHEEL_SPEED)
    assert 0 < left < right

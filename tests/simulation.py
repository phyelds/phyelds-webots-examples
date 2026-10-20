"""Small simulations of the programs on phyelds-simulator: robots on a grid, rounds in step."""
from collections.abc import Callable, Mapping
from typing import Any

from phyelds.simulator import Simulator
from phyelds.simulator.actions import follow_velocity
from phyelds.simulator.deployments import grid_generation
from phyelds.simulator.neighborhood import radius_neighborhood
from phyelds.simulator.runner import schedule_program_for_all


def grid(
    columns: int,
    rows: int = 1,
    *,
    spacing: float,
    origin: tuple[float, float] = (0.0, 0.0),
    sensors: Mapping[int, Mapping[str, Any]] | None = None,
) -> Simulator:
    """
    Robots on a grid from ``origin``, ``spacing`` metres apart, each one hearing only the next ones.

    The robot in column ``x`` and row ``y`` is ``x * rows + y``; ``sensors`` maps some robots to
    the values of their sensors.
    """
    simulator = Simulator()
    grid_generation(simulator, columns, rows, spacing=spacing)
    for node in simulator.environment.node_list():
        node.position = (node.position[0] + origin[0], node.position[1] + origin[1])
    simulator.environment.set_neighborhood_function(radius_neighborhood(spacing * 1.1))
    for robot, values in (sensors or {}).items():
        simulator.environment.nodes[robot].data.update(values)
    return simulator


def run(
    simulator: Simulator, program: Callable[[], Any], rounds: int, *, period: float = 1.0, moving: bool = False
) -> Simulator:
    """
    Run ``rounds`` rounds of ``program`` on every robot, one every ``period`` seconds.

    Robots that are ``moving`` follow the velocity their program sends, in m/s, at any heading.
    """
    schedule_program_for_all(simulator, 0.0, period, program)
    if moving:
        for node in simulator.environment.node_list():
            simulator.schedule_event(period / 2, follow_velocity, simulator, period, node)
    simulator.run(rounds * period)
    return simulator


def positions(simulator: Simulator) -> list[tuple[float, float]]:
    """Where each robot is, in the order of the robots."""
    nodes = simulator.environment.nodes
    return [nodes[robot].position for robot in sorted(nodes)]


def results(simulator: Simulator) -> list[Any]:
    """What each robot computed in its last round, in the order of the robots."""
    nodes = simulator.environment.nodes
    return [nodes[robot].data["result"] for robot in sorted(nodes)]


def outputs(simulator: Simulator, name: str) -> list[Any]:
    """The output ``name`` of each robot, in the order of the robots."""
    nodes = simulator.environment.nodes
    return [nodes[robot].data["outputs"].get(name) for robot in sorted(nodes)]

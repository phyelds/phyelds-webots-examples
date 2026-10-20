"""Small simulations of the programs on phyelds-simulator: robots in a line, rounds in step."""
from collections.abc import Callable, Mapping
from typing import Any

from phyelds.simulator import Simulator
from phyelds.simulator.deployments import grid_generation
from phyelds.simulator.neighborhood import radius_neighborhood
from phyelds.simulator.runner import schedule_program_for_all


def line(
    robots: int, spacing: float, sensors: Mapping[int, Mapping[str, Any]] | None = None
) -> Simulator:
    """Robots ``spacing`` metres apart on the x axis, each one hearing only the next ones."""
    simulator = Simulator()
    grid_generation(simulator, robots, 1, spacing=spacing)
    simulator.environment.set_neighborhood_function(radius_neighborhood(spacing * 1.1))
    for robot, values in (sensors or {}).items():
        simulator.environment.nodes[robot].data.update(values)
    return simulator


def run(simulator: Simulator, program: Callable[[], Any], rounds: int) -> Simulator:
    """Run ``rounds`` rounds of ``program`` on every robot."""
    schedule_program_for_all(simulator, 0.0, 1.0, program)
    simulator.run(rounds)
    return simulator


def results(simulator: Simulator) -> list[Any]:
    """What each robot computed in its last round, in the order of the robots."""
    nodes = simulator.environment.nodes
    return [nodes[robot].data["result"] for robot in sorted(nodes)]


def outputs(simulator: Simulator, name: str) -> list[Any]:
    """The output ``name`` of each robot, in the order of the robots."""
    nodes = simulator.environment.nodes
    return [nodes[robot].data["outputs"].get(name) for robot in sorted(nodes)]

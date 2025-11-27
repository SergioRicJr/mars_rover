from dataclasses import replace
from typing import Callable

from app.domain.rover import Rover
from app.infrastructure.exceptions import InvalidCommandError


# Factory de comandos: mapeia caracteres para métodos do Rover
def _get_command_handlers(rover: Rover) -> dict[str, Callable[[], None]]:
    """Returns the command mapping for the given rover's handlers."""
    return {
        "M": rover.move,
        "L": rover.turn_left,
        "R": rover.turn_right,
    }


def execute_commands(rover: Rover, sequence: str) -> None:
    """
    Executes a command sequence on the probe.
    
    Args:
        rover: The probe that will run the commands
        sequence: String containing commands (M, L, R)
        
    Raises:
        InvalidCommandError: If an invalid command is found
        OutOfBoundsError: If a movement leaves the plateau bounds
        
    Note:
        Execution stops immediately when an error occurs (fail-fast).
        No command after the error will be executed.
    """
    handlers = _get_command_handlers(rover)

    for command in sequence.upper():
        if command not in handlers:
            raise InvalidCommandError(command)
        handlers[command]()


def validate_and_execute_commands(rover: Rover, sequence: str) -> None:
    """
    Validates and executes a command sequence atomically.
    
    It first simulates the entire sequence on a copy of the rover.
    If the simulation succeeds, the changes are applied to the original rover.
    If it fails at any point, the original rover remains untouched.
    
    Args:
        rover: The probe that will run the commands
        sequence: String containing commands (M, L, R)
        
    Raises:
        InvalidCommandError: If an invalid command is found
        OutOfBoundsError: If a movement leaves the plateau bounds
        
    Note:
        This is an atomic operation: either all commands run,
        or none do.
    """
    simulation_rover = replace(
        rover,
        x=rover.x,
        y=rover.y,
        direction=rover.direction,
    )

    execute_commands(simulation_rover, sequence)

    rover.x = simulation_rover.x
    rover.y = simulation_rover.y
    rover.direction = simulation_rover.direction


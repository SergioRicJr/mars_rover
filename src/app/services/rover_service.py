from uuid import uuid4

from app.domain.direction import Direction
from app.domain.plateau import Plateau
from app.domain.rover import Rover
from app.domain.commands import validate_and_execute_commands
from app.repositories.sql_repository import SqlRepository
from app.infrastructure.exceptions import ProbeNotFoundError
from app.domain.plateau import Plateau
from app.domain.direction import Direction
from app.infrastructure.logger import Logger

class RoverService:
    """Service responsible for orchestrating probe operations."""

    def __init__(self, rover_repository: SqlRepository, logger: Logger) -> None:
        self._repository = rover_repository
        self._logger = logger

    def _to_domain(self, model) -> Rover:
        """Converts the ORM model into a Rover entity."""
        plateau = Plateau(max_x=model.plateau_max_x, max_y=model.plateau_max_y)
        return Rover(
            id=model.id,
            plateau=plateau,
            x=model.x,
            y=model.y,
            direction=Direction(model.direction),
        )

    def _to_model(self, rover: Rover) -> dict:
        """Converts a Rover entity into a payload compatible with the ORM model."""
        return {
            "id": rover.id,
            "x": rover.x,
            "y": rover.y,
            "direction": rover.direction.value,
            "plateau_max_x": rover.plateau.max_x,
            "plateau_max_y": rover.plateau.max_y,
        }

    def launch_probe(self, max_x: int, max_y: int, direction: Direction) -> Rover:
        """
        Launches a new probe on the plateau.
        
        Args:
            max_x: Maximum X coordinate of the plateau
            max_y: Maximum Y coordinate of the plateau
            direction: Initial direction of the probe

        Returns:
            The created probe starting at (0, 0)
        """
        plateau = Plateau(max_x=max_x, max_y=max_y)
        rover_id = str(uuid4())

        rover = Rover(
            id=rover_id,
            plateau=plateau,
            x=0,
            y=0,
            direction=direction,
        )

        self._repository.create(self._to_model(rover))
        return rover

    def move_probe(self, rover_id: str, commands: str) -> Rover:
        """
        Executes movement commands on a probe atomically.
        
        The sequence is validated before execution. If any command
        fails (e.g., goes out of bounds), no movement is persisted.
        
        Args:
            rover_id: Probe ID
            commands: Command string (M, L, R)
            
        Returns:
            The probe with an updated state
            
        Raises:
            ProbeNotFoundError: If the probe does not exist
            InvalidCommandError: If an invalid command is found
            OutOfBoundsError: If a movement goes out of bounds
        """
        model = self._repository.get_by_id(rover_id)
        
        if model is None:
            raise ProbeNotFoundError(rover_id)

        rover = self._to_domain(model)
        
        validate_and_execute_commands(rover, commands)
        
        self._repository.update(rover_id, {
            "x": rover.x,
            "y": rover.y,
            "direction": rover.direction.value,
            "plateau_max_x": rover.plateau.max_x,
            "plateau_max_y": rover.plateau.max_y,
        })

        return rover

    def get_all_probes(self) -> list[Rover]:
        """Returns all registered probes."""
        models = self._repository.get_all()
        return [self._to_domain(model) for model in models]

    def get_probe(self, rover_id: str) -> Rover:
        """
        Fetches a probe by ID.
        
        Raises:
            ProbeNotFoundError: If the probe does not exist
        """
        model = self._repository.get_by_id(rover_id)
        
        if model is None:
            raise ProbeNotFoundError(rover_id)
        
        return self._to_domain(model)

from dataclasses import dataclass, field

from app.domain.direction import Direction
from app.domain.plateau import Plateau
from app.infrastructure.exceptions import OutOfBoundsError


@dataclass
class Rover:
    """
    Represents an exploratory probe on Mars.
    Tracks its position (x, y), direction, and the plateau where it operates.
    """
    id: str
    plateau: Plateau
    x: int = field(default=0)
    y: int = field(default=0)
    direction: Direction = field(default=Direction.NORTH)

    def move(self) -> None:
        """
        Moves the probe one step in the current direction.
        Raises OutOfBoundsError if the movement leaves the bounds (fail-fast).
        """
        dx, dy = self.direction.movement_delta
        new_x = self.x + dx
        new_y = self.y + dy

        if not self.plateau.is_within_bounds(new_x, new_y):
            raise OutOfBoundsError(
                new_x, new_y, self.plateau.max_x, self.plateau.max_y
            )

        self.x = new_x
        self.y = new_y

    def turn_left(self) -> None:
        """Rotates the probe 90° to the left."""
        self.direction = self.direction.turn_left()

    def turn_right(self) -> None:
        """Rotates the probe 90° to the right."""
        self.direction = self.direction.turn_right()

    def get_position(self) -> dict:
        """Returns the probe's current state as a dictionary."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "direction": self.direction.value,
        }

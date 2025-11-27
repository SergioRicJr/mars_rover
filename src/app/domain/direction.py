from enum import Enum


class Direction(Enum):
    """
    Enum representing the cardinal directions with rotation behavior (State Pattern).
    Each direction knows how to rotate left/right and what the movement delta is.
    """
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"

    def turn_left(self) -> "Direction":
        """Returns the direction after rotating 90° to the left."""
        rotations = {
            Direction.NORTH: Direction.WEST,
            Direction.WEST: Direction.SOUTH,
            Direction.SOUTH: Direction.EAST,
            Direction.EAST: Direction.NORTH,
        }
        return rotations[self]

    def turn_right(self) -> "Direction":
        """Returns the direction after rotating 90° to the right."""
        rotations = {
            Direction.NORTH: Direction.EAST,
            Direction.EAST: Direction.SOUTH,
            Direction.SOUTH: Direction.WEST,
            Direction.WEST: Direction.NORTH,
        }
        return rotations[self]

    @property
    def movement_delta(self) -> tuple[int, int]:
        """Returns (dx, dy) to move one step in the current direction."""
        deltas = {
            Direction.NORTH: (0, 1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, -1),
            Direction.WEST: (-1, 0),
        }
        return deltas[self]


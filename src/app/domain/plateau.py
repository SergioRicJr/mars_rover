from dataclasses import dataclass


@dataclass(frozen=True)
class Plateau:
    """
    Represents the rectangular plateau where the probes operate.
    Defines the maximum grid limits from (0, 0) to (max_x, max_y).
    """
    max_x: int
    max_y: int

    def __post_init__(self) -> None:
        if self.max_x < 0 or self.max_y < 0:
            raise ValueError("Coordenadas do planalto devem ser não-negativas")

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Checks whether position (x, y) is within the plateau bounds."""
        return 0 <= x <= self.max_x and 0 <= y <= self.max_y


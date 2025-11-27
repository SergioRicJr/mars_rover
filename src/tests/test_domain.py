import pytest

from app.domain.direction import Direction
from app.domain.plateau import Plateau
from app.domain.rover import Rover
from app.domain.commands import execute_commands, validate_and_execute_commands
from app.infrastructure.exceptions import (
    InvalidCommandError,
    OutOfBoundsError,
)


class TestDirection:
    """Tests for the Direction class (State Pattern)."""

    def test_turn_left_from_north_returns_west(self):
        assert Direction.NORTH.turn_left() == Direction.WEST

    def test_turn_left_from_west_returns_south(self):
        assert Direction.WEST.turn_left() == Direction.SOUTH

    def test_turn_left_from_south_returns_east(self):
        assert Direction.SOUTH.turn_left() == Direction.EAST

    def test_turn_left_from_east_returns_north(self):
        assert Direction.EAST.turn_left() == Direction.NORTH

    def test_turn_right_from_north_returns_east(self):
        assert Direction.NORTH.turn_right() == Direction.EAST

    def test_turn_right_from_east_returns_south(self):
        assert Direction.EAST.turn_right() == Direction.SOUTH

    def test_turn_right_from_south_returns_west(self):
        assert Direction.SOUTH.turn_right() == Direction.WEST

    def test_turn_right_from_west_returns_north(self):
        assert Direction.WEST.turn_right() == Direction.NORTH

    def test_movement_delta_north(self):
        assert Direction.NORTH.movement_delta == (0, 1)

    def test_movement_delta_east(self):
        assert Direction.EAST.movement_delta == (1, 0)

    def test_movement_delta_south(self):
        assert Direction.SOUTH.movement_delta == (0, -1)

    def test_movement_delta_west(self):
        assert Direction.WEST.movement_delta == (-1, 0)


class TestPlateau:
    """Tests for the Plateau class."""

    def test_create_plateau_with_valid_coordinates(self):
        plateau = Plateau(max_x=5, max_y=5)
        assert plateau.max_x == 5
        assert plateau.max_y == 5

    def test_create_plateau_with_negative_coordinates_raises_error(self):
        with pytest.raises(ValueError):
            Plateau(max_x=-1, max_y=5)

    def test_is_within_bounds_returns_true_for_valid_position(self):
        plateau = Plateau(max_x=5, max_y=5)
        assert plateau.is_within_bounds(0, 0) is True
        assert plateau.is_within_bounds(5, 5) is True
        assert plateau.is_within_bounds(3, 2) is True

    def test_is_within_bounds_returns_false_for_negative_x(self):
        plateau = Plateau(max_x=5, max_y=5)
        assert plateau.is_within_bounds(-1, 0) is False

    def test_is_within_bounds_returns_false_for_negative_y(self):
        plateau = Plateau(max_x=5, max_y=5)
        assert plateau.is_within_bounds(0, -1) is False

    def test_is_within_bounds_returns_false_for_x_above_max(self):
        plateau = Plateau(max_x=5, max_y=5)
        assert plateau.is_within_bounds(6, 0) is False

    def test_is_within_bounds_returns_false_for_y_above_max(self):
        plateau = Plateau(max_x=5, max_y=5)
        assert plateau.is_within_bounds(0, 6) is False


class TestRover:
    """Tests for the Rover class."""

    @pytest.fixture
    def plateau(self):
        return Plateau(max_x=5, max_y=5)

    @pytest.fixture
    def rover(self, plateau):
        return Rover(id="test-rover", plateau=plateau)

    def test_rover_starts_at_origin_facing_north(self, rover):
        assert rover.x == 0
        assert rover.y == 0
        assert rover.direction == Direction.NORTH

    def test_move_north_increases_y(self, rover):
        rover.move()
        assert rover.x == 0
        assert rover.y == 1

    def test_move_east_increases_x(self, plateau):
        rover = Rover(id="test", plateau=plateau, direction=Direction.EAST)
        rover.move()
        assert rover.x == 1
        assert rover.y == 0

    def test_move_south_decreases_y(self, plateau):
        rover = Rover(id="test", plateau=plateau, y=1, direction=Direction.SOUTH)
        rover.move()
        assert rover.x == 0
        assert rover.y == 0

    def test_move_west_decreases_x(self, plateau):
        rover = Rover(id="test", plateau=plateau, x=1, direction=Direction.WEST)
        rover.move()
        assert rover.x == 0
        assert rover.y == 0

    def test_move_out_of_bounds_raises_error(self, rover):
        rover.direction = Direction.SOUTH
        with pytest.raises(OutOfBoundsError):
            rover.move()

    def test_turn_left_changes_direction(self, rover):
        rover.turn_left()
        assert rover.direction == Direction.WEST

    def test_turn_right_changes_direction(self, rover):
        rover.turn_right()
        assert rover.direction == Direction.EAST

    def test_get_position_returns_correct_dict(self, rover):
        position = rover.get_position()
        assert position == {
            "id": "test-rover",
            "x": 0,
            "y": 0,
            "direction": "NORTH",
        }


class TestCommands:
    """Tests for command execution."""

    @pytest.fixture
    def plateau(self):
        return Plateau(max_x=5, max_y=5)

    @pytest.fixture
    def rover(self, plateau):
        return Rover(id="test-rover", plateau=plateau)

    def test_execute_single_move_command(self, rover):
        execute_commands(rover, "M")
        assert rover.x == 0
        assert rover.y == 1

    def test_execute_single_left_command(self, rover):
        execute_commands(rover, "L")
        assert rover.direction == Direction.WEST

    def test_execute_single_right_command(self, rover):
        execute_commands(rover, "R")
        assert rover.direction == Direction.EAST

    def test_execute_sequence_mrm(self, rover):
        """Tests the sample sequence: MRM results in (1, 1, EAST)."""
        execute_commands(rover, "MRM")
        assert rover.x == 1
        assert rover.y == 1
        assert rover.direction == Direction.EAST

    def test_execute_complex_sequence(self, rover):
        """Tests a more complex sequence: MMRMMRMRRM.
        
        Start: (0, 0, NORTH)
        M: (0, 1, NORTH), M: (0, 2, NORTH), R: (0, 2, EAST)
        M: (1, 2, EAST), M: (2, 2, EAST), R: (2, 2, SOUTH)
        M: (2, 1, SOUTH), R: (2, 1, WEST), R: (2, 1, NORTH)
        M: (2, 2, NORTH)
        """
        execute_commands(rover, "MMRMMRMRRM")
        assert rover.x == 2
        assert rover.y == 2
        assert rover.direction == Direction.NORTH

    def test_execute_lowercase_commands(self, rover):
        """Lowercase commands should work."""
        execute_commands(rover, "mrm")
        assert rover.x == 1
        assert rover.y == 1
        assert rover.direction == Direction.EAST

    def test_execute_invalid_command_raises_error(self, rover):
        with pytest.raises(InvalidCommandError) as exc_info:
            execute_commands(rover, "MXM")
        assert exc_info.value.command == "X"

    def test_execute_stops_on_out_of_bounds(self, rover):
        """The probe must not execute commands after going out of bounds."""
        with pytest.raises(OutOfBoundsError):
            # Tenta mover para sul quando y=0
            execute_commands(rover, "LLM")  # L->West, L->South, M->out of bounds

    def test_full_rotation_returns_to_original_direction(self, rover):
        execute_commands(rover, "LLLL")
        assert rover.direction == Direction.NORTH

    def test_empty_sequence_does_nothing(self, rover):
        # String vazia não deveria causar problemas
        execute_commands(rover, "")
        assert rover.x == 0
        assert rover.y == 0
        assert rover.direction == Direction.NORTH


class TestAtomicCommands:
    """Tests for atomic command execution (validate_and_execute_commands)."""

    @pytest.fixture
    def rover(self):
        """Creates a probe on a 5x5 plateau for tests."""
        plateau = Plateau(max_x=5, max_y=5)
        return Rover(id="test", plateau=plateau, x=0, y=0, direction=Direction.NORTH)

    def test_atomic_execution_applies_all_commands_on_success(self, rover):
        """A valid sequence applies all changes."""
        validate_and_execute_commands(rover, "MRM")
        assert rover.x == 1
        assert rover.y == 1
        assert rover.direction == Direction.EAST

    def test_atomic_execution_preserves_state_on_out_of_bounds(self, rover):
        """If it fails midway, the rover remains in the original state."""
        # Começa em (0, 0, N), faz MM (y=2), vira para sul (LL), tenta ir para y=-1
        with pytest.raises(OutOfBoundsError):
            validate_and_execute_commands(rover, "MMLLMMM")  # 2 norte, vira sul, 3 sul = erro em y=-1
        
        # Estado deve permanecer inalterado
        assert rover.x == 0
        assert rover.y == 0
        assert rover.direction == Direction.NORTH

    def test_atomic_execution_preserves_state_on_invalid_command(self, rover):
        """If an invalid command appears, the rover stays in the original state."""
        rover.x = 1
        rover.y = 1
        
        with pytest.raises(InvalidCommandError):
            validate_and_execute_commands(rover, "MMXR")  # X é inválido
        
        # Estado deve permanecer inalterado
        assert rover.x == 1
        assert rover.y == 1
        assert rover.direction == Direction.NORTH

    def test_atomic_execution_with_complex_valid_sequence(self, rover):
        """A valid complex sequence applies all changes."""
        validate_and_execute_commands(rover, "MMRMMRMRRM")
        assert rover.x == 2
        assert rover.y == 2
        assert rover.direction == Direction.NORTH

    def test_atomic_failure_at_last_command_preserves_all_state(self, rover):
        """Even failing on the last command, no previous state changes are applied."""
        # Planalto 5x5, começa em (0,0,N)
        # MMMMM vai para y=5 (limite), mais um M falharia
        with pytest.raises(OutOfBoundsError):
            validate_and_execute_commands(rover, "MMMMMM")  # 6 movimentos para norte
        
        # Nenhum dos 5 movimentos válidos deve ter sido aplicado
        assert rover.x == 0
        assert rover.y == 0


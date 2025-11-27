class MarsRoverError(Exception):
    pass


class InvalidCommandError(MarsRoverError):
    def __init__(self, command: str):
        self.command = command
        super().__init__(f"Comando inválido: '{command}'. Comandos válidos: M, L, R")


class OutOfBoundsError(MarsRoverError):
    def __init__(self, x: int, y: int, max_x: int, max_y: int):
        self.x = x
        self.y = y
        super().__init__(
            f"Movimento inválido: posição ({x}, {y}) está fora dos limites do planalto (0-{max_x}, 0-{max_y})"
        )


class ProbeNotFoundError(MarsRoverError):
    def __init__(self, probe_id: str):
        self.probe_id = probe_id
        super().__init__(f"Sonda não encontrada: '{probe_id}'")

from enum import Enum
from pydantic import BaseModel, Field


class DirectionEnum(str, Enum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"


class LaunchProbeRequest(BaseModel):
    x: int = Field(..., ge=0, description="Coordenada X máxima do planalto")
    y: int = Field(..., ge=0, description="Coordenada Y máxima do planalto")
    direction: DirectionEnum = Field(..., description="Direção inicial da sonda")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"x": 5, "y": 5, "direction": "NORTH"}
            ]
        }
    }


class MoveProbeRequest(BaseModel):
    commands: str = Field(
        ..., 
        min_length=1,
        pattern=r"^[MLRmlr]+$",
        description="Sequência de comandos (M=mover, L=esquerda, R=direita)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"commands": "MRM"},
                {"commands": "MMRMMRMRRM"}
            ]
        }
    }


class ProbeResponse(BaseModel):
    id: str = Field(..., description="Identificador único da sonda")
    x: int = Field(..., description="Posição X atual")
    y: int = Field(..., description="Posição Y atual")
    direction: DirectionEnum = Field(..., description="Direção atual")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"id": "abc123", "x": 1, "y": 1, "direction": "EAST"}
            ]
        }
    }


class ProbesListResponse(BaseModel):
    probes: list[ProbeResponse] = Field(..., description="Lista de sondas")


from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.domain.direction import Direction
from app.infrastructure import Logger
from app.services.rover_service import RoverService
from app.infrastructure.exceptions import (
    InvalidCommandError,
    OutOfBoundsError,
    ProbeNotFoundError,
)
from app.endpoints.rover.schemas import (
    LaunchProbeRequest,
    MoveProbeRequest,
    ProbeResponse,
    ProbesListResponse,
)


router = APIRouter(prefix="/probes", tags=["probes"])


@router.post(
    "",
    response_model=ProbeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Lançar sonda",
    description="Lança uma nova sonda e configura o planalto com as dimensões especificadas.",
)
@inject
def launch_probe(
    request: LaunchProbeRequest,
    service: RoverService = Depends(Provide[Container.rover_service]),
    logger: Logger = Depends(Provide[Container.logger]),
) -> ProbeResponse:
    direction = Direction(request.direction.value)
    rover = service.launch_probe(request.x, request.y, direction)
    logger.info(f"Probe {rover.id} launched successfully")
    return ProbeResponse(
        id=rover.id,
        x=rover.x,
        y=rover.y,
        direction=rover.direction.value,
    )


@router.put(
    "/{probe_id}/commands",
    response_model=ProbeResponse,
    summary="Mover sonda",
    description="Executa uma sequência de comandos de movimento na sonda especificada.",
)
@inject
def move_probe(
    probe_id: str,
    request: MoveProbeRequest,
    service: RoverService = Depends(Provide[Container.rover_service]),
    logger: Logger = Depends(Provide[Container.logger]),
) -> ProbeResponse:
    try:
        rover = service.move_probe(probe_id, request.commands)
        logger.info(f"Probe {probe_id} moved successfully")
        return ProbeResponse(
            id=rover.id,
            x=rover.x,
            y=rover.y,
            direction=rover.direction.value,
        )
    except ProbeNotFoundError as e:
        logger.error(f"Probe {probe_id} not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidCommandError as e:
        logger.error(f"Invalid command: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except OutOfBoundsError as e:
        logger.error(f"Probe {probe_id} went out of bounds: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=ProbesListResponse,
    summary="Listar sondas",
    description="Retorna o estado atual de todas as sondas lançadas.",
)
@inject
def list_probes(
    service: RoverService = Depends(Provide[Container.rover_service]),
    logger: Logger = Depends(Provide[Container.logger]),
) -> ProbesListResponse:
    rovers = service.get_all_probes()
    logger.info(f"Listing {len(rovers)} probes")
    probes = [
        ProbeResponse(
            id=rover.id,
            x=rover.x,
            y=rover.y,
            direction=rover.direction.value,
        )
        for rover in rovers
    ]
    
    return ProbesListResponse(probes=probes)


def configure(app: FastAPI) -> None:
    app.include_router(router)

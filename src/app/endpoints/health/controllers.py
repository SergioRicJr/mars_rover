from fastapi import APIRouter, FastAPI
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    summary="Health Check",
    description="Verifica se a aplicação está funcionando corretamente.",
)
def health_check():
    """
    Health check endpoint to verify the application's status.
    
    Returns:
        dict: Application status with timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Mars Rover API",
        "version": "1.0.0",
    }


def configure(app: FastAPI) -> None:
    """Configures the health routes on the FastAPI app."""
    app.include_router(router)


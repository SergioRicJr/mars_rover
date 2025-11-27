from fastapi import FastAPI
import uvicorn

from app.config import Config
from app.containers import Container


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mars Rover API",
        description="API para controlar sondas exploradoras em Marte",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    container = Container()
    app.container = container

    from app.endpoints.rover import controllers as rover_module
    rover_module.configure(app)

    from app.endpoints.health import controllers as health_module
    health_module.configure(app)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.SERVER_PORT
    )

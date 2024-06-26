from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.router import router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        root_path=settings.api_prefix,
        openapi_url="/openapi.json" if settings.debug else None,
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


app = create_app()

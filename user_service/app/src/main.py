from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.api_v1.api import api_router
from src.core.config import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=JSONResponse
)
# Mount static files directory
app.mount("/static", StaticFiles(directory="/app/src/media"), name="static")


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

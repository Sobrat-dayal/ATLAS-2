from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .config import get_settings
from .lifecycle import lifespan
from .middleware.error_handling import setup_exception_handlers
from .middleware.request_id import RequestIdMiddleware
from .middleware.timing import TimingMiddleware
from .routers import api_router


def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for the ATLAS financial intelligence platform.",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    
    # 1. CORS
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    # 2. Request ID Generation/Propagation
    app.add_middleware(RequestIdMiddleware)
    
    # 3. Access Logging and Timing
    app.add_middleware(TimingMiddleware)
    
    # Setup Exception Handlers
    setup_exception_handlers(app)
    
    # Include main API router
    app.include_router(api_router, prefix=settings.api_prefix)
    
    @app.get("/", include_in_schema=False)
    async def root_redirect():
        if settings.debug:
            return RedirectResponse(url="/docs")
        return {"service": settings.app_name}
    
    return app

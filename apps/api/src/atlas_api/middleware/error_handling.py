import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from atlas.authorization.errors import AuthorizationError
from atlas.core.exceptions import AtlasError as CoreAtlasError
from ..exceptions import AtlasError
from ..logging import request_id_var
from ..schemas.errors import AtlasErrorEnvelope, AtlasErrorModel

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AtlasError)
    @app.exception_handler(CoreAtlasError)
    @app.exception_handler(AuthorizationError)
    async def atlas_error_handler(request: Request, exc: AtlasError | CoreAtlasError | AuthorizationError):
        req_id = getattr(request.state, "request_id", request_id_var.get())
        logger.warning(f"{type(exc).__name__}: {exc.code} - {exc.message}")

        error = AtlasErrorModel(
            code=exc.code, message=exc.message, request_id=req_id, details=exc.details
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=AtlasErrorEnvelope(error=error).model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", request_id_var.get())

        details = []
        for error in exc.errors():
            field_path = ".".join(str(loc) for loc in error.get("loc", []))
            details.append({"field": field_path, "message": error.get("msg", "")})

        logger.warning(f"Validation error for {request.method} {request.url.path}: {details}")

        error = AtlasErrorModel(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            request_id=req_id,
            details=details,
        )
        return JSONResponse(
            status_code=422, content=AtlasErrorEnvelope(error=error).model_dump(exclude_none=True)
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        req_id = getattr(request.state, "request_id", request_id_var.get())
        # Provide mapping for common HTTP exceptions to ATLAS error format
        code_mapping = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
        }
        code = code_mapping.get(exc.status_code, f"HTTP_{exc.status_code}")

        error = AtlasErrorModel(code=code, message=str(exc.detail), request_id=req_id)
        return JSONResponse(
            status_code=exc.status_code,
            content=AtlasErrorEnvelope(error=error).model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", request_id_var.get())
        logger.exception("Unhandled exception occurred", exc_info=exc)

        # Production safe error message
        error = AtlasErrorModel(
            code="INTERNAL_ERROR",
            message="An unexpected internal error occurred.",
            request_id=req_id,
        )
        return JSONResponse(
            status_code=500, content=AtlasErrorEnvelope(error=error).model_dump(exclude_none=True)
        )

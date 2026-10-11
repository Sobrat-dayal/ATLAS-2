"""FastAPI router for ATLAS Command Language v1 parsing."""

import logging
import time

from atlas.authorization import AuthorizationContext, PermissionCode
from atlas.commands.models import AtlasCommandParseRequest, AtlasCommandParseResult
from atlas.commands.natural_language import (
    NaturalLanguageCommandInterpretation,
    NaturalLanguageCommandInterpreter,
    NaturalLanguageCommandInterpretRequest,
)
from atlas.commands.service import AtlasCommandParsingService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.authorization.dependencies import RequirePermission, get_authorization_context
from atlas_api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/commands", tags=["Commands"])


def get_command_parsing_service(
    session: AsyncSession = Depends(get_db_session),
) -> AtlasCommandParsingService:
    return AtlasCommandParsingService(session)


@router.post(
    "/parse",
    response_model=AtlasCommandParseResult,
    summary="Parse ATLAS Command Language v1 text",
    description=(
        "Deterministic, read-only endpoint that tokenizes, parses, binds, and resolves "
        "structured commands."
    ),
)
async def parse_command(
    request: AtlasCommandParseRequest,
    service: AtlasCommandParsingService = Depends(get_command_parsing_service),
    authz_context: AuthorizationContext = Depends(get_authorization_context),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> AtlasCommandParseResult:
    start_time = time.perf_counter()

    result = await service.parse_command(request.text, authz_context=authz_context)

    duration_ms = (time.perf_counter() - start_time) * 1000

    # Privacy-conscious structured logging: excludes raw command text and parameters
    logger.info(
        "command_parse_completed",
        extra={
            "component": "atlas_command_parser",
            "source_kind": result.source_kind.value if result.source_kind else None,
            "status": result.status.value,
            "command_id": result.command_id,
            "duration_ms": round(duration_ms, 2),
        },
    )

    return result


def get_command_interpreter(
    session: AsyncSession = Depends(get_db_session),
) -> NaturalLanguageCommandInterpreter:
    return NaturalLanguageCommandInterpreter(session)


@router.post(
    "/interpret",
    response_model=NaturalLanguageCommandInterpretation,
    summary="Interpret natural-language user instruction into a Stage 47 command",
    description=(
        "Single-turn, read-only endpoint that uses a strictly bounded model to classify intent, "
        "compiles to canonical Stage 47 syntax, and reparses through Stage 47."
    ),
)
async def interpret_command(
    request: NaturalLanguageCommandInterpretRequest,
    interpreter: NaturalLanguageCommandInterpreter = Depends(get_command_interpreter),
    authz_context: AuthorizationContext = Depends(get_authorization_context),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> NaturalLanguageCommandInterpretation:
    start_time = time.perf_counter()

    result = await interpreter.interpret_command(request.text, authz_context=authz_context)

    duration_ms = (time.perf_counter() - start_time) * 1000

    # Privacy-conscious structured logging: excludes raw input text and prompt content
    logger.info(
        "natural_language_command_interpreted",
        extra={
            "component": "natural_language_command",
            "status": result.status.value,
            "intent": result.intent.value if result.intent else None,
            "duration_ms": round(duration_ms, 2),
        },
    )

    return result

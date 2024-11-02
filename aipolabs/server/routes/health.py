from fastapi import APIRouter

from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.server import config

logger = get_logger(__name__)
router = APIRouter()
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


# TODO: add more checks?
@router.get("/")
async def health() -> bool:
    return True

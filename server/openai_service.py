from openai import OpenAI

from server import config
from server.logging import get_logger

logger = get_logger(__name__)


# TODO: if multiple concurrent requests, would this be a bottleneck and potentially banned?
# TODO: backup plan if OpenAI is down?
# TODO: should this be a singleton and inject into routes? and use a thread pool to handle concurrent requests?
class OpenAIService:
    def __init__(self) -> None:
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    # TODO: exponential backoff?
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text using OpenAI's model.
        """
        logger.debug(f"Generating embedding for text: {text}")
        try:
            response = self.openai_client.embeddings.create(
                input=[text],
                model=config.OPENAI_EMBEDDING_MODEL,
                dimensions=config.OPENAI_EMBEDDING_DIMENSION,
            )
            embedding: list[float] = response.data[0].embedding
            return embedding
        except Exception:
            logger.error("Error generating embedding", exc_info=True)
            raise

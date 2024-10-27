from openai import OpenAI

from aipolabs.common.logging import get_logger

logger = get_logger(__name__)


# TODO: if multiple concurrent requests, would this be a bottleneck and potentially banned?
# TODO: backup plan if OpenAI is down?
# TODO: should this be a singleton and inject into routes? and use a thread pool to handle concurrent requests?
class OpenAIService:
    def __init__(self, api_key: str, embedding_model: str, embedding_dimension: int) -> None:
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension

    # TODO: exponential backoff?
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text using OpenAI's model.
        """
        logger.debug(f"Generating embedding for text: {text}")
        try:
            response = self.openai_client.embeddings.create(
                input=[text],
                model=self.embedding_model,
                dimensions=self.embedding_dimension,
            )
            embedding: list[float] = response.data[0].embedding
            return embedding
        except Exception:
            logger.error("Error generating embedding", exc_info=True)
            raise

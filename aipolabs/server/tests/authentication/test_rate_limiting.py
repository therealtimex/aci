import logging
import time

from fastapi.testclient import TestClient

from aipolabs.server.config import RATE_LIMIT_IP_PER_SECOND

logger = logging.getLogger(__name__)


# get RATE_LIMIT_IP_PER_SECOND from config and use it to test rate limiting in a loop
def test_rate_limiting_ip_per_second(test_client: TestClient, dummy_api_key: str) -> None:
    search_params = {"limit": 1}
    # sleep to ensure the rate limit is reset
    time.sleep(2)

    # Test successful requests
    for counter in range(RATE_LIMIT_IP_PER_SECOND):
        logger.info(f"counter: {counter}")
        response = test_client.get(
            "/v1/apps/search", params=search_params, headers={"x-api-key": dummy_api_key}
        )
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Test rate limit exceeded
    response = test_client.get(
        "/v1/apps/search", params=search_params, headers={"x-api-key": dummy_api_key}
    )
    assert (
        response.status_code == 429
    ), f"Expected 429 Too Many Requests, got {response.status_code}"
    logger.info(f"response.headers: {response.headers}")
    logger.info(f"response: {response.json()}")
    # Verify rate limit headers
    assert "X-RateLimit-Limit-ip-per-second" in response.headers
    assert "X-RateLimit-Remaining-ip-per-second" in response.headers
    assert "X-RateLimit-Reset-ip-per-second" in response.headers

    # sleep to reset and test again
    time.sleep(2)
    response = test_client.get(
        "/v1/apps/search", params=search_params, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

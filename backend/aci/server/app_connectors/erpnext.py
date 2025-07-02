from typing import override

import requests
from aci.common.db.sql_models import LinkedAccount
from aci.common.logging_setup import get_logger
from aci.common.schemas.security_scheme import (APIKeyScheme,
                                                APIKeySchemeCredentials)
from aci.server.app_connectors.base import AppConnectorBase

logger = get_logger(__name__)


class ERPNext(AppConnectorBase):
    """
    ERPNext Connector.

    This connector provides methods to interact with the ERPNext API,
    specifically for operations defined with the "connector" protocol.
    """

    def __init__(
        self,
        linked_account: LinkedAccount,
        security_scheme: APIKeyScheme,
        security_credentials: APIKeySchemeCredentials,
    ):
        """
        Initializes the ERPNext connector.

        Args:
            linked_account: The linked account associated with this connector.
            security_scheme: The API key security scheme details.
            security_credentials: The API key credentials for authentication.
        """
        super().__init__(linked_account, security_scheme, security_credentials)
        # Assuming the API key is directly available in the credentials value
        self.api_key = security_credentials.secret_key
        # The server URL is expected to be passed as an environment variable
        # or configured elsewhere and accessed via linked_account or a global config.
        # For now, we'll assume it's part of the linked_account's metadata or a similar mechanism.
        # If not, it would need to be explicitly passed or retrieved.
        # For this example, we'll use a placeholder that would typically be resolved
        # from the environment or a configuration store.
        # In a real scenario, AIPOLABS_ERPNEXT_SERVER_URL would be resolved by the platform.
        self.server_url = linked_account.metadata.get("AIPOLABS_ERPNEXT_SERVER_URL")
        if not self.server_url:
            logger.error("ERPNext server URL not found in linked account metadata.")
            raise ValueError("ERPNext server URL is not configured.")

    @override
    def _before_execute(self) -> None:
        """
        This method is called before any connector method is executed.
        Can be used for pre-execution checks or setup, e.g., token refresh.
        For API Key, typically no action is needed here.
        """
        pass

    def get_doctype_list(self) -> list[str]:
        """
        Fetches a list of all available DocTypes from the ERPNext instance.

        This method corresponds to the ERPNEXT__GET_DOCTYPE_LIST tool.
        It makes a GET request to the /api/resource/DocType endpoint.

        Returns:
            A list of strings, where each string is the name of a DocType.
            Returns an empty list if no DocTypes are found or on error.
        Raises:
            requests.exceptions.RequestException: If the API call fails.
        """
        logger.info("Executing get_doctype_list to fetch all ERPNext DocTypes.")
        url = f"{self.server_url}/api/resource/DocType"
        headers = {"Authorization": f"token {self.api_key}"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # ERPNext API for listing DocTypes typically returns a 'data' key
            # which is a list of dictionaries, each with a 'name' field.
            doctypes = [item["name"] for item in data.get("data", []) if "name" in item]
            logger.info(f"Successfully fetched {len(doctypes)} DocTypes.")
            return doctypes
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching DocTypes from ERPNext: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response format from ERPNext API: Missing key {e}. Response: {data}")
            raise ValueError(f"Unexpected API response format: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

from typing import Any, override

import requests

from aci.common.db.sql_models import LinkedAccount
from aci.common.logging_setup import get_logger
from aci.common.schemas.security_scheme import APIKeyScheme, APIKeySchemeCredentials
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
        # The API key is retrieved from the security credentials.
        self.api_key = security_credentials.secret_key
        # The ERPNext server URL is retrieved from the linked account's metadata.
        # This URL is expected to be configured by the platform or user during account linking.
        # Temporary: Hardcoding the ERPNext server URL for development purposes.
        # In production, this will be dynamically retrieved from linked_account.metadata.
        self.server_url = "https://erp.realtimex.co"
        # The original dynamic retrieval and validation logic is commented out for now:
        # self.server_url = linked_account.metadata.get("AIPOLABS_ERPNEXT_SERVER_URL")
        # if not self.server_url:
        #     logger.error("ERPNext server URL not found in linked account metadata.")
        #     raise ValueError("ERPNext server URL is not configured.")

    @override
    def _before_execute(self) -> None:
        """
        This method is called before any connector method is executed.
        Can be used for pre-execution checks or setup, e.g., token refresh.
        For API Key, typically no action is needed here.
        """
        pass

    def get_doctype_list(
        self, limit_start: int = 0, limit_page_length: int = 20
    ) -> list[dict[str, str]]:
        """
        Fetches a list of all available DocTypes from the ERPNext instance.

        This method corresponds to the ERPNEXT__GET_DOCTYPE_LIST tool.
        It makes a GET request to the /api/resource/DocType endpoint.

        Args:
            limit_start: The number of DocTypes to skip.
            limit_page_length: The number of DocTypes to return.

        Returns:
            A list of dictionaries, where each dictionary contains the name and
            description of a DocType. Returns an empty list if no DocTypes are
            found or on error.
        Raises:
            requests.exceptions.RequestException: If the API call fails.
        """
        logger.info("Executing get_doctype_list to fetch all ERPNext DocTypes.")
        url = f"{self.server_url}/api/resource/DocType"
        headers = {"Authorization": f"token {self.api_key}"}
        params = {
            "fields": '["name", "description"]',
            "limit_start": limit_start,
            "limit_page_length": limit_page_length,
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # ERPNext API for listing DocTypes typically returns a 'data' key
            # which is a list of dictionaries.
            doctypes = data.get("data", [])
            logger.info(f"Successfully fetched {len(doctypes)} DocTypes.")
            return doctypes
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching DocTypes from ERPNext: {e}")
            raise
        except KeyError as e:
            logger.error(
                f"Unexpected response format from ERPNext API: Missing key {e}. Response: {data}"
            )
            raise ValueError(f"Unexpected API response format: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    def get_doctype_schema(self, doctype: str, essentials_only: bool = False) -> dict[str, Any]:
        """
        Get the complete schema for a DocType, including field definitions,
        validations, and linked DocTypes.

        This method uses the '/api/v2/doctype/{doctype}/meta' endpoint for detailed
        metadata.

        Args:
            doctype: The name of the DocType to get the schema for.
            essentials_only: If True, returns a summarized version of the schema,
                including only name, description, module, required fields, and field definitions.
                Defaults to False, returning the complete schema.

        Returns:
            A dictionary representing the processed DocType schema.
        Raises:
            requests.exceptions.RequestException: If the API call fails.
            ValueError: If the doctype is not found or the response is invalid.
        """
        logger.info(f"Executing get_doctype_schema for DocType: {doctype}")
        headers = {"Authorization": f"token {self.api_key}"}

        primary_url = f"{self.server_url}/api/v2/doctype/{doctype}/meta"

        try:
            response = requests.get(primary_url, headers=headers)
            response.raise_for_status()
            metadata = response.json()

            doctype_data = metadata.get("data")
            if not doctype_data:
                raise ValueError(
                    "Invalid response from meta endpoint: response is empty or 'data' key is missing.")

            logger.info(
                f"Successfully fetched and processed schema for DocType '{doctype}' using meta endpoint."
            )
            logger.debug(f"Metadata for DocType '{doctype}': {doctype_data}")
            return self._process_doctype_meta(doctype_data, doctype, essentials_only)

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                logger.error(f"DocType '{doctype}' not found.")
                raise ValueError(f"DocType '{doctype}' not found.") from http_err
            logger.error(f"HTTP error on fallback for DocType '{doctype}': {http_err}")
            raise
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"Failed to get schema for DocType '{doctype}': {e}")
            raise

    def _process_doctype_meta(self, meta: dict[str, Any],
                              doctype_name: str, essentials_only: bool = False) -> dict[str, Any]:
        """Processes the metadata from the meta endpoint, with an option for a minimal response."""
        doctype_info = meta

        processed_fields = []
        required_fields = []

        for field in doctype_info.get("fields", []):
            is_required = field.get("reqd") == 1
            if is_required:
                required_fields.append(field.get("fieldname"))

            field_data = {
                "field_name": field.get("fieldname"),
                "field_type": field.get("fieldtype"),
                "linked_doctype": field.get("options") if field.get("fieldtype") == "Link" else None,
                "required": is_required,
                "description": field.get("description"),
                "default": field.get("default"),
            }

            if not essentials_only:
                field_data.update({
                    "label": field.get("label"),
                    "min_length": field.get("min_length"),
                    "max_length": field.get("max_length"),
                    "min_value": field.get("min_value"),
                    "max_value": field.get("max_value"),
                    "read_only": field.get("read_only") == 1,
                })
            
            processed_fields.append(field_data)

        schema = {
            "name": doctype_info.get("name", doctype_name),
            "description": doctype_info.get("description"),
            "module": doctype_info.get("module"),
            "required_fields": required_fields,
            "fields": processed_fields,
        }

        if not essentials_only:
            schema.update({
                "is_single": doctype_info.get("issingle") == 1,
                "is_table": doctype_info.get("istable") == 1,
                "is_custom": doctype_info.get("custom") == 1,
                "is_submittable": doctype_info.get("is_submittable") == 1,
            })
        
        return schema


# Alias for dynamic import by the ConnectorFunctionExecutor.
# When a tool for the "erpnext" app is executed by an AI Agent,
# the ConnectorFunctionExecutor dynamically imports this module
# and looks for a class named "Erpnext" (case-sensitive from the app name).
# This alias allows us to keep the more descriptive "ERPNext" class name
# while still allowing the dynamic import to work.
Erpnext = ERPNext

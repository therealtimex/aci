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

    def get_doctype_schema(self, doctype: str) -> dict[str, Any]:
        """
        Get the complete schema for a DocType, including field definitions,
        validations, and linked DocTypes.

        This method first attempts to use the '/api/v2/doctype/{doctype}/meta' endpoint for detailed
        metadata and falls back to a direct resource API call if the primary
        method fails.

        Args:
            doctype: The name of the DocType to get the schema for.

        Returns:
            A dictionary representing the processed DocType schema.
        Raises:
            requests.exceptions.RequestException: If all API call attempts fail.
            ValueError: If the doctype is not found or the response is invalid.
        """
        logger.info(f"Executing get_doctype_schema for DocType: {doctype}")
        headers = {"Authorization": f"token {self.api_key}"}

        # Primary method: Use /api/v2/doctype/{doctype}/meta for detailed metadata
        primary_url = f"{self.server_url}/api/v2/doctype/{doctype}/meta"

        try:
            response = requests.get(primary_url, headers=headers)
            response.raise_for_status()
            metadata = response.json()

            if not metadata:
                raise ValueError(
                    "Invalid response from meta endpoint: response is empty.")

            logger.info(
                f"Successfully fetched and processed schema for DocType '{doctype}' using meta endpoint."
            )
            return self._process_doctype_meta(metadata, doctype)

        except (requests.exceptions.RequestException, ValueError) as e:
            logger.warning(
                f"Primary method with meta endpoint failed for DocType '{doctype}': {e}. "
                "Attempting fallback to resource API."
            )

            # Fallback method: Use the resource API
            fallback_url = f"{self.server_url}/api/resource/DocType/{doctype}"
            try:
                response = requests.get(fallback_url, headers=headers)
                response.raise_for_status()
                data = response.json().get("data")

                if not data:
                    raise ValueError(
                        "Invalid response from resource API: 'data' key is missing or empty."
                    )

                logger.info(
                    f"Successfully fetched schema for DocType '{doctype}' using fallback resource API."
                )
                return self._process_doctype_doc(data, doctype)

            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 404:
                    logger.error(
                        f"DocType '{doctype}' not found using both primary and fallback methods."
                    )
                    raise ValueError(
                        f"DocType '{doctype}' not found.") from http_err
                logger.error(
                    f"HTTP error on fallback for DocType '{doctype}': {http_err}")
                raise
            except (requests.exceptions.RequestException, ValueError) as fallback_err:
                logger.error(
                    f"Fallback method also failed for DocType '{doctype}': {fallback_err}")
                raise fallback_err from e

    def _process_doctype_meta(self, meta: dict[str, Any],
                              doctype_name: str) -> dict[str, Any]:
        """Processes the metadata from the meta endpoint."""
        doctype_info = meta.get("doctype", {})
        return {
            "name": doctype_name,
            "label": doctype_info.get("name", doctype_name),
            "description": doctype_info.get("description"),
            "module": doctype_info.get("module"),
            "issingle": doctype_info.get("issingle") == 1,
            "istable": doctype_info.get("istable") == 1,
            "custom": doctype_info.get("custom") == 1,
            "fields": [
                {
                    "fieldname": field.get("fieldname"),
                    "label": field.get("label"),
                    "fieldtype": field.get("fieldtype"),
                    "required": field.get("reqd") == 1,
                    "description": field.get("description"),
                    "default": field.get("default"),
                    "options": field.get("options"),
                    "linked_doctype": field.get("options")
                    if field.get("fieldtype") == "Link"
                    else None,
                    "child_doctype": field.get("options")
                    if field.get("fieldtype") == "Table"
                    else None,
                    "in_list_view": field.get("in_list_view") == 1,
                    "read_only": field.get("read_only") == 1,
                    "hidden": field.get("hidden") == 1,
                }
                for field in meta.get("fields", [])
            ],
            "permissions": meta.get("permissions", []),
            "autoname": doctype_info.get("autoname"),
            "is_submittable": doctype_info.get("is_submittable") == 1,
            "track_changes": doctype_info.get("track_changes") == 1,
        }

    def _process_doctype_doc(self, doc: dict[str, Any],
                             doctype_name: str) -> dict[str, Any]:
        """Processes the document data from /api/resource/DocType."""
        return {
            "name": doctype_name,
            "label": doc.get("name", doctype_name),
            "description": doc.get("description"),
            "module": doc.get("module"),
            "issingle": doc.get("issingle") == 1,
            "istable": doc.get("istable") == 1,
            "custom": doc.get("custom") == 1,
            "fields": doc.get("fields", []),
            "permissions": doc.get("permissions", []),
            "autoname": doc.get("autoname"),
            "is_submittable": doc.get("is_submittable") == 1,
            "track_changes": doc.get("track_changes") == 1,
        }


# Alias for dynamic import by the ConnectorFunctionExecutor.
# When a tool for the "erpnext" app is executed by an AI Agent,
# the ConnectorFunctionExecutor dynamically imports this module
# and looks for a class named "Erpnext" (case-sensitive from the app name).
# This alias allows us to keep the more descriptive "ERPNext" class name
# while still allowing the dynamic import to work.
Erpnext = ERPNext

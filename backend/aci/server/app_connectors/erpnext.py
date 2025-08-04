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
        self.api_key = security_credentials.secret_key
        self.server_url = security_credentials.api_host_url

        if not self.api_key:
            logger.error("ERPNext API key not found in security credentials.")
            raise ValueError("ERPNext API key is not configured.")

        if not self.server_url:
            logger.error("ERPNext server URL not found in security credentials.")
            raise ValueError("ERPNext server URL is not configured.")

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

    def get_instance_config(
        self,
        include_company_details: bool = True,
        include_system_settings: bool = True,
        include_user_defaults: bool = True,
    ) -> dict[str, Any]:
        """
        Retrieves ERPNext instance configuration and settings that provide context
        for AI agents, including company information, system settings, and regional preferences.

        Args:
            include_company_details: Include detailed information about the default company.
            include_system_settings: Include system-wide settings and preferences.
            include_user_defaults: Include current user's default settings.

        Returns:
            A dictionary containing the instance configuration with the following structure:
            {
                "instance": {
                    "base_url": str,
                    "version": str,
                    "title": str
                },
                "company": {
                    "name": str,
                    "abbr": str,
                    "country": str,
                    "currency": str,
                    "domain": str
                },
                "system_settings": {
                    "country": str,
                    "time_zone": str,
                    "date_format": str,
                    "time_format": str,
                    "number_format": str,
                    "float_precision": int,
                    "currency_precision": int
                },
                "user_defaults": {
                    "company": str,
                    "fiscal_year": str,
                    "language": str
                }
            }

        Raises:
            requests.exceptions.RequestException: If any API call fails.
            ValueError: If required data is not found in the response.
        """
        logger.info("Executing get_instance_config to fetch ERPNext instance configuration.")
        headers = {"Authorization": f"token {self.api_key}"}
        config = {}

        try:
            # Get basic instance information
            config["instance"] = self._get_instance_info(headers)

            # Get company details if requested
            if include_company_details:
                config["company"] = self._get_default_company_info(headers)

            # Get system settings if requested
            if include_system_settings:
                config["system_settings"] = self._get_system_settings(headers)

            # Get user defaults if requested
            if include_user_defaults:
                config["user_defaults"] = self._get_user_defaults(headers)

            logger.info("Successfully retrieved ERPNext instance configuration.")
            return config

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching instance configuration from ERPNext: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching instance config: {e}")
            raise

    def _get_instance_info(self, headers: dict[str, str]) -> dict[str, Any]:
        """Get basic instance information."""
        try:
            # Try to get version info from the version endpoint
            version_url = f"{self.server_url}/api/method/frappe.utils.change_log.get_versions"
            response = requests.get(version_url, headers=headers)
            
            instance_info = {
                "base_url": self.server_url,
                "version": "Unknown",
                "title": "ERPNext Instance"
            }

            if response.status_code == 200:
                version_data = response.json()
                if "message" in version_data and isinstance(version_data["message"], dict):
                    # Get ERPNext version
                    erpnext_version = version_data["message"].get("erpnext", "Unknown")
                    instance_info["version"] = erpnext_version

            # Try to get system settings for site title
            try:
                settings_url = f"{self.server_url}/api/resource/System Settings"
                settings_response = requests.get(settings_url, headers=headers)
                if settings_response.status_code == 200:
                    settings_data = settings_response.json()
                    if "data" in settings_data and len(settings_data["data"]) > 0:
                        site_name = settings_data["data"][0].get("site_name")
                        if site_name:
                            instance_info["title"] = site_name
            except Exception:
                # If we can't get the site name, keep the default
                pass

            return instance_info

        except Exception as e:
            logger.warning(f"Could not fetch complete instance info: {e}")
            return {
                "base_url": self.server_url,
                "version": "Unknown",
                "title": "ERPNext Instance"
            }

    def _get_default_company_info(self, headers: dict[str, str]) -> dict[str, Any]:
        """Get information about the default company."""
        try:
            # First, try to get the default company from Global Defaults
            defaults_url = f"{self.server_url}/api/resource/Global Defaults"
            response = requests.get(defaults_url, headers=headers)
            
            default_company = None
            if response.status_code == 200:
                defaults_data = response.json()
                if "data" in defaults_data and len(defaults_data["data"]) > 0:
                    default_company = defaults_data["data"][0].get("default_company")

            # If no default company found, get the first company
            if not default_company:
                companies_url = f"{self.server_url}/api/resource/Company"
                companies_response = requests.get(companies_url, headers=headers, params={"limit_page_length": 1})
                if companies_response.status_code == 200:
                    companies_data = companies_response.json()
                    if "data" in companies_data and len(companies_data["data"]) > 0:
                        default_company = companies_data["data"][0].get("name")

            if not default_company:
                return {"name": "Unknown", "abbr": "", "country": "", "currency": "", "domain": ""}

            # Get detailed company information
            company_url = f"{self.server_url}/api/resource/Company/{default_company}"
            company_response = requests.get(company_url, headers=headers)
            
            if company_response.status_code == 200:
                company_data = company_response.json()
                if "data" in company_data:
                    company = company_data["data"]
                    return {
                        "name": company.get("company_name", company.get("name", "Unknown")),
                        "abbr": company.get("abbr", ""),
                        "country": company.get("country", ""),
                        "currency": company.get("default_currency", ""),
                        "domain": company.get("domain", "")
                    }

            return {"name": default_company, "abbr": "", "country": "", "currency": "", "domain": ""}

        except Exception as e:
            logger.warning(f"Could not fetch company info: {e}")
            return {"name": "Unknown", "abbr": "", "country": "", "currency": "", "domain": ""}

    def _get_system_settings(self, headers: dict[str, str]) -> dict[str, Any]:
        """Get system-wide settings."""
        try:
            settings_url = f"{self.server_url}/api/resource/System Settings"
            response = requests.get(settings_url, headers=headers)
            
            default_settings = {
                "country": "",
                "time_zone": "UTC",
                "date_format": "dd-mm-yyyy",
                "time_format": "HH:mm:ss",
                "number_format": "#,###.##",
                "float_precision": 3,
                "currency_precision": 2
            }

            if response.status_code == 200:
                settings_data = response.json()
                if "data" in settings_data and len(settings_data["data"]) > 0:
                    settings = settings_data["data"][0]
                    return {
                        "country": settings.get("country", default_settings["country"]),
                        "time_zone": settings.get("time_zone", default_settings["time_zone"]),
                        "date_format": settings.get("date_format", default_settings["date_format"]),
                        "time_format": settings.get("time_format", default_settings["time_format"]),
                        "number_format": settings.get("number_format", default_settings["number_format"]),
                        "float_precision": settings.get("float_precision", default_settings["float_precision"]),
                        "currency_precision": settings.get("currency_precision", default_settings["currency_precision"])
                    }

            return default_settings

        except Exception as e:
            logger.warning(f"Could not fetch system settings: {e}")
            return {
                "country": "",
                "time_zone": "UTC",
                "date_format": "dd-mm-yyyy",
                "time_format": "HH:mm:ss",
                "number_format": "#,###.##",
                "float_precision": 3,
                "currency_precision": 2
            }

    def _get_user_defaults(self, headers: dict[str, str]) -> dict[str, Any]:
        """Get current user's default settings."""
        try:
            # Get current user info
            user_url = f"{self.server_url}/api/method/frappe.auth.get_logged_user"
            user_response = requests.get(user_url, headers=headers)
            
            defaults = {
                "company": "",
                "fiscal_year": "",
                "language": "en"
            }

            if user_response.status_code == 200:
                user_data = user_response.json()
                current_user = user_data.get("message")
                
                if current_user:
                    # Get user defaults
                    user_defaults_url = f"{self.server_url}/api/resource/User/{current_user}"
                    user_defaults_response = requests.get(user_defaults_url, headers=headers)
                    
                    if user_defaults_response.status_code == 200:
                        user_defaults_data = user_defaults_response.json()
                        if "data" in user_defaults_data:
                            user_info = user_defaults_data["data"]
                            defaults["language"] = user_info.get("language", "en")

                    # Try to get user's default company from User Permission or Global Defaults
                    try:
                        global_defaults_url = f"{self.server_url}/api/resource/Global Defaults"
                        global_response = requests.get(global_defaults_url, headers=headers)
                        if global_response.status_code == 200:
                            global_data = global_response.json()
                            if "data" in global_data and len(global_data["data"]) > 0:
                                global_defaults = global_data["data"][0]
                                defaults["company"] = global_defaults.get("default_company", "")
                                defaults["fiscal_year"] = global_defaults.get("current_fiscal_year", "")
                    except Exception:
                        pass

            return defaults

        except Exception as e:
            logger.warning(f"Could not fetch user defaults: {e}")
            return {
                "company": "",
                "fiscal_year": "",
                "language": "en"
            }


# Alias for dynamic import by the ConnectorFunctionExecutor.
# When a tool for the "erpnext" app is executed by an AI Agent,
# the ConnectorFunctionExecutor dynamically imports this module
# and looks for a class named "Erpnext" (case-sensitive from the app name).
# This alias allows us to keep the more descriptive "ERPNext" class name
# while still allowing the dynamic import to work.
Erpnext = ERPNext

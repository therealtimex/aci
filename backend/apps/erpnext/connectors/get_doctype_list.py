from typing import List, Dict, Any

from aci.common.processor import AciProcessor, AciProcessorConnector, AciProcessorConnectorConfig


class ErpNextGetDoctypeListConnector(AciProcessorConnector):
    """
    Connector to get a list of all available DocTypes in ERPNext.
    """

    def __init__(self, config: AciProcessorConnectorConfig):
        super().__init__(config)
        self.erpnext_processor = AciProcessor(self.config.get_required_connector("erpnext"))

    async def __call__(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieves all DocTypes from ERPNext and returns a list of their names.
        """
        response = await self.erpnext_processor.process_tool(
            "ERPNEXT__LIST_DOCUMENTS",
            {
                "path": {"doctype": "DocType"},
                "query": {"limit_page_length": 1000} # Assuming there are less than 1000 doctypes
            }
        )

        # The response from ERPNext is a list of dictionaries, where each dictionary represents a DocType.
        # We want to extract the 'name' from each dictionary.
        return [{"name": item["name"]} for item in response]

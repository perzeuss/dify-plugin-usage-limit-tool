# pylint: disable=missing-module-docstring
from typing import Any
from collections.abc import Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.exceptions import FailedToDeleteStorageItemException


class ResetUsageTool(Tool):
    """
    The `ResetUsageTool` class is designed to reset usage limits for users.
    It resets the current usage data based on the specified strategy.

    The tool is invoked with the following parameters:
    - `user_id`: The unique identifier of the user.
    - `tracking_method`: The tracking method to use for identifying usage limits.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        user_id = tool_parameters["user_id"]
        tracking_method = tool_parameters["tracking_method"]

        identifier = user_id
        if tracking_method == "workspace-user":
            identifier = user_id
        elif tracking_method == "app-user":
            identifier = f"{self.session.app_id}{user_id}"
        elif tracking_method == "app":
            identifier = f"{self.session.app_id}"
        elif tracking_method == "conversation":
            identifier = self.session.conversation_id
        elif tracking_method is not None:
            raise ValueError("Invalid tracking method")

        try:
            self.session.storage.delete(identifier)
        except Exception as e:
            # Log the exception, ignore because it could be that the entry does not exist.
            raise FailedToDeleteStorageItemException(identifier, e) from e

        yield self.create_json_message({
            "identifier": identifier,
            "status": "Reset successfully completed"
        })

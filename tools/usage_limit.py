# pylint: disable=missing-module-docstring
import time
from typing import Any, Tuple
from collections.abc import Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.exceptions import UsageLimitExceededException


class UsageLimitTool(Tool):
    """
    The `UsageLimitTool` class is a Dify node designed to track and manage usage limits for users.
    It operates by identifying usage based on a specified tracking method, either by user, app,
    or conversation session. It checks if the current usage exceeds a predefined limit using
    either a fixed window or sliding window strategy.

    The tool is expected to be invoked on each message with the following parameters:
    - `user_id`: The unique identifier of the user.
    - `tracking_method`: The method to use for tracking usage. Can be either "user",
       "app", or "conversation".
    - `limit`: The maximum number of times the usage can occur before being limited.
    - `duration_seconds` (optional): The duration of the window in seconds. Default is 3600 seconds.
    - `limit_strategy` (optional): The windowing strategy to use. Can be "fixed" or "sliding".
       Default is "sliding".
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        user_id = tool_parameters["user_id"]
        tracking_method = tool_parameters["tracking_method"]
        limit = int(tool_parameters["limit"])
        duration_seconds = int(tool_parameters.get("duration_seconds", 3600))
        limit_strategy = tool_parameters.get("limit_strategy", "sliding")

        # Determine identifier based on tracking_method
        identifier = self._get_identifier(user_id, tracking_method)

        if limit_strategy == "fixed":
            current_usage, reset_seconds = self._fixed_window_usage(
                identifier, limit, duration_seconds)
        elif limit_strategy == "sliding":
            current_usage, reset_seconds = self._sliding_window_usage(
                identifier, limit, duration_seconds)
        else:
            raise ValueError("Invalid window strategy")

        remaining_usage = max(0, limit - current_usage)

        yield self.create_json_message({
            "identifier": identifier,
            "limit": limit,
            "current_usage": current_usage,
            "remaining_usage": remaining_usage,
            "reset_seconds": reset_seconds
        })

    def _get_identifier(self, user_id: str, tracking_method: str) -> str:
        """
        Determine the identifier based on the tracking method.

        Parameters:
        - `user_id`: The unique identifier of the user.
        - `tracking_method`: The method to use for tracking usage.
        
        Returns:
        - `identifier`: The computed identifier based on the tracking method.
        """
        if tracking_method == "workspace-user":
            identifier = user_id
        elif tracking_method == "app-user":
            identifier = f"{self.session.app_id}{user_id}"
        elif tracking_method == "app":
            identifier = f"{self.session.app_id}"
        elif tracking_method == "conversation":
            identifier = self.session.conversation_id
        else:
            raise ValueError("Invalid tracking method")
        return identifier

    def _fixed_window_usage(
        self,
        identifier: str,
        limit: int,
        duration_seconds: int
    ) -> Tuple[int, int]:
        """
        Implement fixed window usage tracking.

        Parameters:
        - `identifier`: The identifier for tracking usage.
        - `limit`: The maximum number of allowed usages within the window.
        - `duration_seconds`: The duration of the window in seconds.

        Returns:
        - `current_usage`: The current usage count after incrementing.
        """
        current_time = int(time.time())
        try:
            current_usage_bytes = self.session.storage.get(identifier)
            if current_usage_bytes:
                current_usage, timestamp = map(
                    int, current_usage_bytes.decode().split(':'))
            else:
                current_usage = 0
                timestamp = current_time
        # pylint: disable=broad-except
        except Exception:
            current_usage = 0
            timestamp = current_time

        # Reset usage if the window has expired
        if current_time - timestamp > duration_seconds:
            current_usage = 0
            timestamp = current_time

        reset_seconds = max(0, duration_seconds - (current_time - timestamp))

        if current_usage >= limit:
            raise UsageLimitExceededException(identifier, limit, current_usage)

        current_usage += 1
        self.session.storage.set(identifier, f"{current_usage}:{
                                 timestamp}".encode())
        return current_usage, reset_seconds

    def _sliding_window_usage(
        self,
        identifier: str,
        limit: int,
        duration_seconds: int
    ) -> Tuple[int, int]:
        """
        Implement sliding window usage tracking.

        Parameters:
        - `identifier`: The identifier for tracking usage.
        - `limit`: The maximum number of allowed usages within the window.
        - `duration_seconds`: The duration of the sliding window in seconds.

        Returns:
        - `current_usage`: The current usage count after incrementing.
        """
        current_time = int(time.time())
        try:
            timestamps_bytes = self.session.storage.get(identifier)
            if timestamps_bytes:
                timestamps = list(
                    map(int, timestamps_bytes.decode().split(',')))
            else:
                timestamps = []
        # pylint: disable=broad-except
        except Exception:
            timestamps = []

        window_start = current_time - duration_seconds
        timestamps = [t for t in timestamps if t > window_start]

        if len(timestamps) >= limit:
            raise UsageLimitExceededException(
                identifier, limit, len(timestamps))

        timestamps.append(current_time)

        timestamps_str = ','.join(map(str, timestamps))
        self.session.storage.set(identifier, timestamps_str.encode())

        current_usage = len(timestamps)
        # For sliding window, reset when the oldest timestamp exits the window
        oldest_timestamp = timestamps[0] if timestamps else current_time
        reset_seconds = max(0, duration_seconds -
                            (current_time - oldest_timestamp))

        return current_usage, reset_seconds

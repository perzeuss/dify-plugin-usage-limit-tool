# pylint: disable=protected-access
"""
Unit Tests for Reset Usage Tool
"""
import unittest
from unittest.mock import MagicMock

from tools.reset_usage import ResetUsageTool
from tools.exceptions import FailedToDeleteStorageItemException


class TestResetUsageTool(unittest.TestCase):
    """
    Unit tests for the ResetUsageTool class.
    """
    def setUp(self):
        # Create mock instances of runtime and session
        self.mock_runtime = MagicMock()
        self.mock_session = MagicMock()
        self.mock_session.app_id = "app123"
        self.mock_session.conversation_id = "conv456"
        self.mock_session.storage = MagicMock()
        self.mock_session.storage.delete = MagicMock()

        # Create instance of ResetUsageTool with mocks
        self.tool = ResetUsageTool(
            runtime=self.mock_runtime, session=self.mock_session)

        # Mock create_json_message method
        self.tool.create_json_message = MagicMock(
            return_value="mocked_message")

    def test_invoke_with_tracking_method_workspace_user(self):
        """Test that _invoke resets usage when tracking_method is 'workspace-user'."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": "workspace-user"
        }

        # Call the _invoke method
        result = list(self.tool._invoke(tool_parameters))

        expected_identifier = "user789"
        # Assertions
        self.mock_session.storage.delete.assert_called_once_with(
            expected_identifier)
        self.tool.create_json_message.assert_called_once_with({
            "identifier": expected_identifier,
            "status": "Reset successfully completed"
        })
        self.assertEqual(result, ["mocked_message"])

    def test_invoke_with_tracking_method_app_user(self):
        """Test that _invoke resets usage when tracking_method is 'app-user'."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": "app-user"
        }

        # Call the _invoke method
        result = list(self.tool._invoke(tool_parameters))

        expected_identifier = f"{self.mock_session.app_id}user789"
        # Assertions
        self.mock_session.storage.delete.assert_called_once_with(
            expected_identifier)
        self.tool.create_json_message.assert_called_once_with({
            "identifier": expected_identifier,
            "status": "Reset successfully completed"
        })
        self.assertEqual(result, ["mocked_message"])

    def test_invoke_with_tracking_method_app(self):
        """Test that _invoke resets usage when tracking_method is 'app'."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": "app"
        }

        # Call the _invoke method
        result = list(self.tool._invoke(tool_parameters))

        expected_identifier = self.mock_session.app_id
        # Assertions
        self.mock_session.storage.delete.assert_called_once_with(
            expected_identifier)
        self.tool.create_json_message.assert_called_once_with({
            "identifier": expected_identifier,
            "status": "Reset successfully completed"
        })
        self.assertEqual(result, ["mocked_message"])

    def test_invoke_with_tracking_method_conversation(self):
        """Test that _invoke resets usage when tracking_method is 'conversation'."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": "conversation"
        }

        # Call the _invoke method
        result = list(self.tool._invoke(tool_parameters))

        expected_identifier = self.mock_session.conversation_id
        # Assertions
        self.mock_session.storage.delete.assert_called_once_with(
            expected_identifier)
        self.tool.create_json_message.assert_called_once_with({
            "identifier": expected_identifier,
            "status": "Reset successfully completed"
        })
        self.assertEqual(result, ["mocked_message"])

    def test_invoke_with_invalid_tracking_method(self):
        """Test that _invoke raises ValueError for an invalid tracking_method."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": "invalid_strategy"
        }

        # Expecting a ValueError
        with self.assertRaises(ValueError) as context:
            list(self.tool._invoke(tool_parameters))

        self.assertEqual(str(context.exception), "Invalid tracking method")

    def test_invoke_storage_delete_raises_exception(self):
        """Test that _invoke handles exceptions from storage.delete."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": "workspace-user"
        }

        # Simulate an exception in storage.delete
        self.mock_session.storage.delete.side_effect = Exception(
            "Storage delete failed")

        with self.assertRaises(FailedToDeleteStorageItemException) as context:
            list(self.tool._invoke(tool_parameters))

        exception = context.exception
        self.assertEqual(exception.identifier, "user789")
        self.assertIsInstance(exception.__cause__, Exception)
        self.assertEqual(str(exception.__cause__), "Storage delete failed")

    def test_invoke_without_user_id(self):
        """Test that _invoke raises KeyError when user_id is missing."""
        tool_parameters = {
            "tracking_method": "workspace-user"
        }

        with self.assertRaises(KeyError) as context:
            list(self.tool._invoke(tool_parameters))

        self.assertEqual(str(context.exception), "'user_id'")

    def test_invoke_without_tracking_method(self):
        """Test that _invoke raises KeyError when tracking_method is missing."""
        tool_parameters = {
            "user_id": "user789"
        }

        with self.assertRaises(KeyError) as context:
            list(self.tool._invoke(tool_parameters))

        self.assertEqual(str(context.exception), "'tracking_method'")

    def test_invoke_with_tracking_method_none(self):
        """Test that _invoke uses 'user_id' as identifier when tracking_method is None."""
        tool_parameters = {
            "user_id": "user789",
            "tracking_method": None
        }

        # Call the _invoke method
        result = list(self.tool._invoke(tool_parameters))

        expected_identifier = "user789"
        # Assertions
        self.mock_session.storage.delete.assert_called_once_with(
            expected_identifier)
        self.tool.create_json_message.assert_called_once_with({
            "identifier": expected_identifier,
            "status": "Reset successfully completed"
        })
        self.assertEqual(result, ["mocked_message"])
# pylint: disable=protected-access
"""
Unit Tests for UsageLimitTool
"""

import unittest
from unittest.mock import MagicMock, patch

from tools.usage_limit import UsageLimitTool
from tools.exceptions import UsageLimitExceededException


class TestUsageLimitTool(unittest.TestCase):
    """
    Unit tests for the UsageLimitTool class.
    """

    def setUp(self):
        # Create mock instances of runtime and session
        self.mock_runtime = MagicMock()
        self.mock_session = MagicMock()
        self.mock_session.app_id = "app123"
        self.mock_session.conversation_id = "conv456"
        self.mock_session.storage = MagicMock()
        self.mock_session.storage.get = MagicMock()
        self.mock_session.storage.set = MagicMock()

        # Create instance of UsageLimitTool with mocks
        self.tool = UsageLimitTool(
            runtime=self.mock_runtime, session=self.mock_session)

        # Mock create_json_message method
        self.tool.create_json_message = MagicMock(
            return_value="mocked_message")

        # Patch time.time to return a fixed timestamp
        self.patcher = patch('time.time', return_value=1000000)
        self.mock_time = self.patcher.start()

    def tearDown(self):
        # Stop the time.time patcher
        self.patcher.stop()

    def test_fixed_window_usage_under_limit(self):
        """
        Test fixed window usage under limit.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        # Mock storage.get to return a usage value under limit
        self.mock_session.storage.get.return_value = b"2:999000"
        expected_identifier = "user789"
        expected_usage = b"3:999000"
        # Call the _invoke method
        result = list(self.tool._invoke(tool_parameters))
        # Assertions
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 3,
            "remaining_usage": 2,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_fixed_window_usage_limit_exceeded(self):
        """
        Test fixed window usage when limit is exceeded.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        # Mock storage.get to return current usage equal to limit
        self.mock_session.storage.get.return_value = b"5:999000"
        expected_identifier = "user789"
        with self.assertRaises(UsageLimitExceededException) as context:
            list(self.tool._invoke(tool_parameters))
        exception = context.exception
        self.assertEqual(exception.identifier, expected_identifier)
        self.assertEqual(exception.limit, 5)
        self.assertEqual(exception.current_usage, 5)
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_not_called()

    def test_sliding_window_usage_under_limit(self):
        """
        Test sliding window usage under limit.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'sliding'
        }
        # Mock storage.get to return timestamps within window
        self.mock_session.storage.get.return_value = b"999000,999500,999900"
        expected_identifier = "user789"
        expected_timestamps = [999000, 999500, 999900, 1000000]
        expected_timestamps_str = ','.join(
            map(str, expected_timestamps)).encode()
        result = list(self.tool._invoke(tool_parameters))
        # Assertions
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_timestamps_str)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 4,
            "remaining_usage": 1,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_sliding_window_usage_limit_exceeded(self):
        """
        Test sliding window usage when limit is exceeded.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'sliding'
        }
        # Mock storage.get to return timestamps within window, usage at limit
        self.mock_session.storage.get.return_value = b"996500,997000,998000,999000,999999"
        expected_identifier = "user789"
        with self.assertRaises(UsageLimitExceededException) as context:
            list(self.tool._invoke(tool_parameters))
        exception = context.exception
        self.assertEqual(exception.identifier, expected_identifier)
        self.assertEqual(exception.limit, 5)
        self.assertEqual(exception.current_usage, 5)
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_not_called()

    def test_invalid_tracking_method(self):
        """
        Test invoking with an invalid tracking method.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'invalid_method',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        with self.assertRaises(ValueError) as context:
            list(self.tool._invoke(tool_parameters))
        self.assertEqual(str(context.exception), "Invalid tracking method")

    def test_invalid_limit_strategy(self):
        """
        Test invoking with an invalid limit strategy.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'invalid_strategy'
        }
        with self.assertRaises(ValueError) as context:
            list(self.tool._invoke(tool_parameters))
        self.assertEqual(str(context.exception), "Invalid window strategy")

    def test_missing_user_id(self):
        """
        Test invoking without user_id parameter.
        """
        tool_parameters = {
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        with self.assertRaises(KeyError) as context:
            list(self.tool._invoke(tool_parameters))
        self.assertEqual(str(context.exception), "'user_id'")

    def test_missing_limit(self):
        """
        Test invoking without limit parameter.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        with self.assertRaises(KeyError) as context:
            list(self.tool._invoke(tool_parameters))
        self.assertEqual(str(context.exception), "'limit'")

    def test_tracking_method_workspace_user(self):
        """
        Test invoking with tracking_method 'workspace-user'.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        expected_identifier = "user789"
        self.mock_session.storage.get.return_value = b"1:999000"
        expected_usage = b"2:999000"
        result = list(self.tool._invoke(tool_parameters))
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 2,
            "remaining_usage": 3,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_tracking_method_app_user(self):
        """
        Test invoking with tracking_method 'app-user'.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'app-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        expected_identifier = "app123user789"
        self.mock_session.storage.get.return_value = b"1:999000"
        expected_usage = b"2:999000"
        result = list(self.tool._invoke(tool_parameters))
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 2,
            "remaining_usage": 3,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_tracking_method_app(self):
        """
        Test invoking with tracking_method 'app'.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'app',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        expected_identifier = "app123"
        self.mock_session.storage.get.return_value = b"1:999000"
        expected_usage = b"2:999000"
        result = list(self.tool._invoke(tool_parameters))
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 2,
            "remaining_usage": 3,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_tracking_method_conversation(self):
        """
        Test invoking with tracking_method 'conversation'.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'conversation',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        expected_identifier = "conv456"
        self.mock_session.storage.get.return_value = b"1:999000"
        expected_usage = b"2:999000"
        result = list(self.tool._invoke(tool_parameters))
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 2,
            "remaining_usage": 3,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_fixed_window_usage_reset_after_duration(self):
        """
        Test fixed window usage resets after duration has expired.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        # Simulate old timestamp outside the window
        old_timestamp = 1000000 - 4000  # 4000 seconds ago
        self.mock_session.storage.get.return_value = f"4:{old_timestamp}".encode()
        expected_identifier = "user789"
        expected_usage = f"1:{1000000}".encode()
        result = list(self.tool._invoke(tool_parameters))
        # Assertions
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 1,
            "remaining_usage": 4,
            'reset_seconds': 3600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_sliding_window_usage_reset_old_timestamps(self):
        """
        Test sliding window discards old timestamps outside the window.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'sliding'
        }
        # Mix of old and new timestamps
        self.mock_session.storage.get.return_value = b"996000,997000,999500,999900"
        expected_identifier = "user789"
        expected_timestamps = [997000, 999500, 999900, 1000000]
        expected_timestamps_str = ','.join(
            map(str, expected_timestamps)).encode()
        result = list(self.tool._invoke(tool_parameters))
        # Assertions
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_timestamps_str)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 4,
            "remaining_usage": 1,
            'reset_seconds': 600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_storage_get_exception_handled(self):
        """
        Test that exceptions from storage.get are handled gracefully.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        self.mock_session.storage.get.side_effect = Exception(
            "Storage get failed")
        expected_identifier = "user789"
        expected_usage = f"1:{1000000}".encode()
        result = list(self.tool._invoke(tool_parameters))
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 1,
            "remaining_usage": 4,
            'reset_seconds': 3600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_storage_set_exception_raised(self):
        """
        Test that exceptions from storage.set are raised.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        self.mock_session.storage.set.side_effect = Exception(
            "Storage set failed")
        expected_identifier = "user789"
        with self.assertRaises(Exception) as context:
            list(self.tool._invoke(tool_parameters))
        self.assertEqual(str(context.exception), "Storage set failed")
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        expected_usage = f"1:{1000000}".encode()
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)

    def test_default_limit_strategy(self):
        """
        Test that the default limit strategy is 'sliding'.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': '3600',
            # 'limit_strategy' not provided, should default to 'sliding'
        }
        self.mock_session.storage.get.return_value = b"999000,999500,999900"
        expected_identifier = "user789"
        expected_timestamps = [999000, 999500, 999900, 1000000]
        expected_timestamps_str = ','.join(
            map(str, expected_timestamps)).encode()
        result = list(self.tool._invoke(tool_parameters))
        # Assertions
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_timestamps_str)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 4,
            "remaining_usage": 1,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_missing_duration_seconds_defaults(self):
        """
        Test that the default duration_seconds is 3600 when not provided.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'limit_strategy': 'fixed'
        }
        # Mock storage.get to return usage under limit
        self.mock_session.storage.get.return_value = b"2:999000"
        expected_identifier = "user789"
        expected_usage = b"3:999000"
        result = list(self.tool._invoke(tool_parameters))
        # Assertions
        self.mock_session.storage.get.assert_called_with(expected_identifier)
        self.mock_session.storage.set.assert_called_with(
            expected_identifier, expected_usage)
        self.tool.create_json_message.assert_called_with({
            "identifier": expected_identifier,
            "limit": 5,
            "current_usage": 3,
            "remaining_usage": 2,
            'reset_seconds': 2600
        })
        self.assertEqual(result, ["mocked_message"])

    def test_limit_and_duration_cast_to_int(self):
        """
        Test that limit and duration_seconds are correctly cast to integers.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5.0',
            'duration_seconds': '3600.0',
            'limit_strategy': 'fixed'
        }
        with self.assertRaises(ValueError):
            list(self.tool._invoke(tool_parameters))

    def test_non_integer_limit_raises_exception(self):
        """
        Test that non-integer limit raises a ValueError.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': 'five',
            'duration_seconds': '3600',
            'limit_strategy': 'fixed'
        }
        with self.assertRaises(ValueError):
            list(self.tool._invoke(tool_parameters))

    def test_non_integer_duration_raises_exception(self):
        """
        Test that non-integer duration_seconds raises a ValueError.
        """
        tool_parameters = {
            'user_id': 'user789',
            'tracking_method': 'workspace-user',
            'limit': '5',
            'duration_seconds': 'one_hour',
            'limit_strategy': 'fixed'
        }
        with self.assertRaises(ValueError):
            list(self.tool._invoke(tool_parameters))


if __name__ == '__main__':
    unittest.main()
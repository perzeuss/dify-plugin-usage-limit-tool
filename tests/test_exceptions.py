import unittest

from tools.exceptions import UsageLimitExceededException, FailedToDeleteStorageItemException

class TestUsageLimitExceededException(unittest.TestCase):
    def test_exception_message_and_attributes(self):
        identifier = 'test_user'
        limit = 100
        current_usage = 150
        exception = UsageLimitExceededException(identifier, limit, current_usage)
        expected_message = (
            f'Usage limit exceeded for {identifier}: {current_usage} messages sent, limit is {limit}'
        )
        self.assertEqual(str(exception), expected_message)
        self.assertEqual(exception.identifier, identifier)
        self.assertEqual(exception.limit, limit)
        self.assertEqual(exception.current_usage, current_usage)

class TestFailedToDeleteStorageItemException(unittest.TestCase):
    def test_exception_message_and_attributes(self):
        identifier = 'test_item'
        original_exception = ValueError('Invalid value')
        exception = FailedToDeleteStorageItemException(identifier, original_exception)
        expected_message = (
            f'Failed to delete usage limit for identifier {identifier}: {original_exception}'
        )
        self.assertEqual(str(exception), expected_message)
        self.assertEqual(exception.identifier, identifier)
        self.assertEqual(exception.original_exception, original_exception)

if __name__ == '__main__':
    unittest.main()
class UsageLimitExceededException(Exception):
    """
    Exception raised when a usage limit is exceeded.

    Attributes:
        identifier (str): The unique identifier for the resource or user whose limit was exceeded.
        limit (int): The maximum allowed usage for the resource or user.
        current_usage (int): The current usage count that exceeded the limit.
        
    """

    def __init__(self, identifier, limit, current_usage):
        self.identifier = identifier
        self.limit = limit
        self.current_usage = current_usage
        super().__init__(
            f"Usage limit exceeded for {identifier}: {current_usage} messages sent, limit is {limit}"
        )

class FailedToDeleteStorageItemException(Exception):
    """
    Exception raised when a storage item fails to be deleted.

    Attributes:
        identifier (str): The identifier of the storage item that failed to be deleted.
        original_exception (Exception): The original exception encountered during deletion.
    """

    def __init__(self, identifier, original_exception):
        super().__init__(f"Failed to delete usage limit for identifier {identifier}: {original_exception}")
        self.identifier = identifier
        self.original_exception = original_exception

class RagConfigurationError(Exception):
    def __init__(self, message: str = "Google AI is not configured.") -> None:
        super().__init__(message)


class RagServiceError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RagRateLimitError(RagServiceError):
    def __init__(
        self,
        message: str = "Google AI rate limit reached. Please wait a minute and try again.",
    ) -> None:
        super().__init__(message)

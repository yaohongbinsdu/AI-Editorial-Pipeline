import asyncio
import functools
from typing import Any, Callable, TypeVar

from app.utils.logging import get_logger

logger = get_logger("retry")

F = TypeVar("F", bound=Callable[..., Any])


def async_retry(
    max_retries: int = 3,
    backoff_base: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        wait = backoff_base**attempt
                        logger.warning(
                            "retry_attempt",
                            func=func.__name__,
                            attempt=attempt,
                            max_retries=max_retries,
                            wait_seconds=wait,
                            error=str(exc),
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error(
                            "retry_exhausted",
                            func=func.__name__,
                            max_retries=max_retries,
                            error=str(exc),
                        )
            raise last_exception  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator

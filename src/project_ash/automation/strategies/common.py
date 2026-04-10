from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    wait_ms: int = 1200


def retry_call(fn: Callable[[], T], policy: RetryPolicy) -> T:
    last_error: Exception | None = None
    for _ in range(max(1, policy.attempts)):
        try:
            return fn()
        except Exception as exc:  # pragma: no cover
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_call reached unexpected state")

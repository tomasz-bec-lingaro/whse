from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class FixedWindowRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        if limit <= 0 or window_seconds <= 0:
            return True, 0

        now = monotonic()
        window_start = now - window_seconds

        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= window_start:
                requests.popleft()

            if len(requests) >= limit:
                retry_after = max(1, int(window_seconds - (now - requests[0])))
                return False, retry_after

            requests.append(now)
            return True, 0

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


upload_rate_limiter = FixedWindowRateLimiter()

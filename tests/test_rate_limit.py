from fastapi import HTTPException
import pytest

from app.core.rate_limit import SlidingWindowRateLimiter


def test_rate_limiter_blocks_excess_attempts():
    limiter = SlidingWindowRateLimiter(requests=2, window_seconds=60)
    limiter.check("client:/login")
    limiter.check("client:/login")

    with pytest.raises(HTTPException) as exc_info:
        limiter.check("client:/login")

    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers

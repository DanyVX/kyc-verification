from kyc.api.rate_limit import FixedWindowRateLimiter


def test_rate_limiter_blocks_then_recovers() -> None:
    limiter = FixedWindowRateLimiter(limit=2, window_seconds=10)
    assert limiter.allow("a", now=0)
    assert limiter.allow("a", now=1)
    assert not limiter.allow("a", now=2)
    assert limiter.allow("a", now=11)

from app.retries import backoff_schedule, make_retry, retries_on


def test_default_methods():
    retry = make_retry()
    assert retries_on(retry, "GET", 503)
    assert not retries_on(retry, "POST", 503)


def test_backoff_schedule():
    assert backoff_schedule(make_retry(total=5, backoff=0.5), 4) == [0, 1.0, 2.0, 4.0]

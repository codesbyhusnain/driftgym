from app.retries import backoff_schedule, make_retry, max_backoff, retries_on


def test_custom_methods_and_statuses():
    retry = make_retry(methods=["POST", "PATCH"], statuses=[500])
    assert retries_on(retry, "POST", 500)
    assert retries_on(retry, "patch", 500)
    assert not retries_on(retry, "GET", 500)
    assert not retries_on(retry, "POST", 503)


def test_every_default_method():
    retry = make_retry()
    for method in ["DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE", "get"]:
        assert retries_on(retry, method, 429)
    assert not retries_on(retry, "GET", 404)


def test_backoff_is_capped():
    assert max_backoff() == 120
    assert backoff_schedule(make_retry(total=10, backoff=10), 6) == [0, 20, 40, 80, 120, 120]
    assert backoff_schedule(make_retry(total=2, backoff=0), 2) == [0, 0]

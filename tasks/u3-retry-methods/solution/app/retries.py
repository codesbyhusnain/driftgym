from urllib3.util.retry import Retry

SAFE_METHODS = Retry.DEFAULT_ALLOWED_METHODS


def make_retry(total=3, backoff=0.5, methods=None, statuses=(429, 502, 503, 504)):
    allowed = frozenset(methods) if methods else SAFE_METHODS
    return Retry(total=total, backoff_factor=backoff, allowed_methods=allowed, status_forcelist=statuses)


def retries_on(retry, method, status):
    return retry.is_retry(method, status)


def backoff_schedule(retry, attempts):
    delays = []
    for _ in range(attempts):
        retry = retry.increment(method="GET", url="/")
        delays.append(min(retry.get_backoff_time(), Retry.DEFAULT_BACKOFF_MAX))
    return delays


def max_backoff():
    return Retry.DEFAULT_BACKOFF_MAX

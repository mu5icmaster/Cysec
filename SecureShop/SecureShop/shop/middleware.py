import time
from django.http import HttpResponse

class RateLimitMiddleware:
    """
    Per-IP sliding window limits.
    - POST /login*: 5 req / 60s
    - POST /register/: 5 req / 60s
    - POST others: 20 req / 60s (as before)
    """
    WINDOW = 60
    LIMITS = [
        ("/login", 5),
        ("/login/verify", 5),
        ("/register/", 5),
    ]
    DEFAULT_LIMIT = 20
    _hits = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def _limit_for(self, path):
        for prefix, lim in self.LIMITS:
            if path.startswith(prefix):
                return lim
        return self.DEFAULT_LIMIT

    def __call__(self, request):
        if request.method == "POST":
            now = time.time()
            ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
            key = f"{ip}:{self._limit_for(request.path)}"
            bucket = self._hits.setdefault(key, [])
            while bucket and now - bucket[0] > self.WINDOW:
                bucket.pop(0)
            limit = int(key.split(":")[-1])
            if len(bucket) >= limit:
                return HttpResponse("Too many requests. Try again in a minute.", status=429)
            bucket.append(now)
        return self.get_response(request)

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    db_status = "ok"
    cache_status = "ok"

    try:
        connection.ensure_connection()
    except Exception:
        db_status = "error"

    try:
        cache.set("health", "ok", timeout=5)
        cache.get("health")
    except Exception:
        cache_status = "error"

    return JsonResponse({
        "status": "ok",
        "database": db_status,
        "cache": cache_status
    })

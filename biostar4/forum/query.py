"""
"""
from biostar4.forum import models
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from biostar4.forum.models import *

TRAFFIC_CACHE_KEY = "traffic"

def get_traffic(request, minutes=60):
    """
    Traffic as post views in the last 60 min.
    """
    global TRAFFIC_CACHE_KEY

    count = cache.get(TRAFFIC_CACHE_KEY)
    if not count:
        # Set the cache for traffic.
        now = timezone.now()
        start = now - timedelta(minutes=minutes)
        try:
            count = PostView.objects.filter(date__gt=start).exclude(date__gt=now).distinct('ip').count()
        except NotImplementedError:
            count = PostView.objects.filter(date__gt=start).exclude(date__gt=now).count()
        cache.set(TRAFFIC_CACHE_KEY, count, timeout=600)

    return count



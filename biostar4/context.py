import logging

from django.conf import settings
from biostar4 import VERSION

def extras(request):
    context = {
        "BIOSTAR_VERSION": VERSION,
        "request": request,
        "user": request.user,
        #"recaptcha": settings.RECAPTCHA_PUBLIC_KEY,
        #"TRAFFIC": get_traffic(request),
        #"recent_votes": query.recent_votes(request),
        #"recent_users": query.recent_users(request),
        #"recent_awards": query.recent_awards(request),
        #"recent_replies": query.recent_replies(request),
    }

    return context


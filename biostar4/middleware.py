import logging
from django.conf import settings
from biostar4.forum.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone

logger = logging.getLogger("biostar")

def get_ip(request):
    ip1 = request.META.get('REMOTE_ADDR', '')
    ip2 = request.META.get(' X-Real-IP', '')
    ip = ip1 or ip2 or '0.0.0.0'
    return ip

class BiostarMiddleware(object):
    '''
    Performs tasks that are applied on every request
    '''

    def process_request(self, request):

        # Add the user to each request.
        user = request.user

        # Suspended users are logged out immediately.
        if user.is_authenticated() and user.profile.is_suspended():
            logout(request)
            messages.error(request, 'This account has been suspended!')

        if user.is_authenticated():
            # The time between two count refreshes.
            now = timezone.now()
            elapsed = (now - user.last_login).seconds
            if elapsed > settings.SESSION_UPDATE_SECONDS:
                # Set the last login time.
                User.objects.filter(user_id=user.id).update(last_login=now)
import logging
from django.conf import settings
from biostar4.forum.models import User
from django.contrib import messages

logger = logging.getLogger("biostar")

class BiostarMiddleware(object):
    '''
    Performs tasks that are applied on every request
    '''

    def process_request(self, request):

        return

        # Add the user to each request.
        user = request.user = user

        # Suspended users are logged out immediately.
        if user and user.is_suspended():
            User.logout(request)
            messages.error(request, 'This account has been suspended!')
            request.user = None
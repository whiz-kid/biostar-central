"""

"""
import logging
from datetime import datetime
from django.conf import settings
from django.shortcuts import redirect
from biostar4.forum import utils, html
from functools import wraps
from django.core.urlresolvers import reverse
from django.db import models

logger = logging.getLogger('biostar')


class User(models.Model):
    # File size in megabytes.
    MAX_FILE_SIZE = 5
    MAX_FILE_NUM = 10
    MAX_MESSAGES = 25

    NEW_USER, TRUSTED_USER, MODERATOR, ADMIN = [1, 2, 3, 4]

    USER_ROLES = [
        (NEW_USER, "New user"),
        (TRUSTED_USER, "Trusted user"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    ]

    # User roles.
    role = models.IntegerField(default=NEW_USER, choices=USER_ROLES)

    def get_role(self):
        return self.USER_ROLES.get(self.role, "???")

    ACTIVE, SUSPENDED, BANNED = [100, 200, 300]

    ACCESS_TYPES = [
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (BANNED, "Banned"),
    ]

    # User login permissions.
    access = models.IntegerField(default=ACTIVE, choices=ACCESS_TYPES)

    # A user friendly representation of access permissions.
    def get_access(self):
        return self.ACCESS_TYPES.get(self.access, "???")

    def is_suspended(self):
        return self.access != self.ACTIVE


    # User display name.
    name = models.CharField(max_length=200, default='')

    # The user email address.
    email = models.CharField(max_length=200, unique=True, db_index=True)

    # User password. Set it with set_password()
    password = models.CharField(max_length=200,)

    # Username visible on the site.
    username = models.CharField(max_length=15, unique=True)

    # User geographical location.
    location = models.CharField(max_length=100,  default=' ')

    # Twitter handle.
    twitter = models.CharField(max_length=100,  default='')

    # Google Scholar id.
    scholar = models.CharField(max_length=100,  default='')

    # List us user selected tags.
    my_tags = models.CharField(max_length=500)

    # List of watched tags.
    watched_tags = models.CharField(max_length=500)

    # User score.
    score = models.IntegerField(default=0)

    # How many posts has the user created.
    post_num = models.IntegerField(default=0)

    # New messages for this user.
    new_messages = models.IntegerField(default=0)

    # New votes for the user.
    new_votes = models.IntegerField(default=0)

    # New posts for the user.
    new_posts = models.IntegerField(default=0)

    # The website for the user.
    website = models.CharField(max_length=250, default='')

    # Join and last login dates.
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField()

    # The user's information field as markdown text and as html.
    text = models.CharField(max_length=3000, default='')
    html = models.CharField(max_length=6000, default='')

    # Relative paths to files uploaded by the user.
    #files = ListField(models.CharField(max_length=250, required=False))

    # User related messages.
    #messages = SortedListField(EmbeddedDocumentField(Message), ordering="date", reverse=True)


    def fast(cls, queryset):
        # Fast query that removes the heavy elements
        return queryset.exclude('text', 'html', 'messages')

    def set_password(self, password):
        self.password = utils.encrypt(password)

    def check_password(self, password):
        return self.password == utils.encrypt(password)

    def login(self, request):
        request.session[self.SESSION_NAME] = str(self.uid)

    def add_message(self, content):
        self.messages.append(Message(html=content, new=True, date=datetime.now()))
        self.new_messages += 1
        self.messages = self.messages[-self.MAX_MESSAGES:]
        self.save()

    def save(self, *args, **kwargs):
        self.date_joined = self.date_joined or datetime.now()
        self.last_login = self.last_login or self.date_joined
        self.username = self.username or "user%d" % self.id
        self.html = html.sanitize(self.text)
        super(User, self).save(*args, **kwargs)

    @staticmethod
    def get(request):
        uid = request.session.get(User.SESSION_NAME, None)
        try:
            return User.objects.filter(uid=uid).first()
        except Exception as exc:
            logger.error(exc)
            return None

    @staticmethod
    def logout(request):
        del request.session[User.SESSION_NAME]

    def __unicode__(self):
        return "User: {} ({})".format(self.uid, self.email)


from django.db.models import *
from . import html
from django.contrib.auth.models import User
from functools import wraps
from django.contrib.auth.decorators import login_required

def fill_user(f):
    """
    Fills the user parameter on a wrapped function
    """

    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        user = request.user
        return f(request, user, *args, **kwargs)

    return decorated_function

def create_user(email, password):
    user = User(email=email)
    user.set_password(password)
    user.save()
    # Need to refetch it to get the apply results of
    # of signals.
    user = User.objects.get(pk=user.pk)
    return user


class Profile(Model):
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

    USER_ROLES_MAP = dict(USER_ROLES)

    # User roles.
    role = IntegerField(default=NEW_USER, choices=USER_ROLES)

    def get_role(self):
        return self.USER_ROLES_MAP.get(self.role, "???")

    ACTIVE, SUSPENDED, BANNED = [100, 200, 300]

    ACCESS_TYPES = [
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (BANNED, "Banned"),
    ]
    ACCESS_TYPES_MAP = dict(ACCESS_TYPES)
    # User login permissions.
    access = IntegerField(default=ACTIVE, choices=ACCESS_TYPES)

    # A user friendly representation of access permissions.
    def get_access(self):
        return self.ACCESS_TYPES_MAP.get(self.access, "???")

    def is_suspended(self):
        return self.access != self.ACTIVE


    user = OneToOneField(User)
    name = CharField(max_length=100, default="User")
    score = IntegerField(default=0)
    new_messages = IntegerField(default=0)
    new_votes = IntegerField(default=0)
    post_num = IntegerField(default=0)
    location = CharField(max_length=250, default='')
    twitter = CharField(max_length=250, default='')
    scholar = CharField(max_length=250, default='')
    website = CharField(max_length=250, default='')
    my_tags = CharField(max_length=500, default='')
    watched_tags = CharField(max_length=500, default='')
    files = CharField(max_length=1000, default='')
    text = CharField(max_length=3000, default='')
    html = CharField(max_length=6000, default='')

    def save(self, *args, **kwargs):
        self.html = html.sanitize(self.text)
        super(Profile, self).save(*args, **kwargs)

class FastManager(Manager):
    def get_queryset(self):
        return super(FastManager, self).get_queryset().filter()


class Post(Model):

    fast = FastManager()

    MAX_CHARS = 15000

    DRAFT, PENDING, PUBLISHED, CLOSED, DELETED = [1, 2, 3, 4, 5]

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PENDING, "Pending"),
        (PUBLISHED, "Published"),
        (CLOSED, "Closed"),
        (DELETED, "Deleted"),
    ]

    # The status of the post.
    status = IntegerField(choices=STATUS_CHOICES, default=PUBLISHED)

    def get_status(self):
        return self.STATUS_CHOICES.get(self.status, "???")

    # Valid post types.
    QUESTION, ANSWER, COMMENT, TUTORIAL, FORUM, JOB, TOOL, NEWS = range(1, 9)

    POST_TYPES = [
        (QUESTION, "Question"),
        (ANSWER, "Answer"),
        (COMMENT, "Comment"),
        (TUTORIAL, "Tutorial"),
        (FORUM, "Forum"),
        (JOB, "Job"),
        (TOOL, "Tool"),
        (NEWS, "News"),
    ]

    # Top level posts.
    TOP_LEVEL = {QUESTION, FORUM, TOOL, TUTORIAL, NEWS}

    type = IntegerField(choices=POST_TYPES, default=FORUM)

    author = ForeignKey(User)

    # How many posts has the user created.
    post_num = IntegerField(default=0)

    # New messages for this user.
    new_messages = IntegerField(default=0)

    # New votes for the user.
    new_votes = IntegerField(default=0)

    # New posts for the user.
    new_posts = IntegerField(default=0)
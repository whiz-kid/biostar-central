from django.db.models import *
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
    MAX_FILE_SIZE = 5
    MAX_FILE_NUM = 10
    MAX_MESSAGES = 25

    user = OneToOneField(User)
    name = CharField(max_length=100, default="User")
    new_messages = IntegerField(default=0)
    new_votes = IntegerField(default=0)

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
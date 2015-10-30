from django.db.models import *
from . import html
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.contrib.sites.models import Site
from django.utils import timezone


def create_user(email, password):
    user = User(email=email)
    user.set_password(password)
    user.save()
    # Need to refetch the user because signals may altered the profile.
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

    tags = TaggableManager()

    def save(self, *args, **kwargs):
        self.html = html.sanitize(self.text)
        super(Profile, self).save(*args, **kwargs)


class FastManager(Manager):
    def get_queryset(self):
        return super(FastManager, self).get_queryset().filter()


class Post(Model):
    # Maximal character size for a post.
    MAX_CHARS = 15000

    # A manager to get a reduced amount of filed on posts.
    fast = FastManager()
    objects = Manager()

    DRAFT, PENDING, PUBLISHED, CLOSED, DELETED = [1, 2, 3, 4, 5]

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PENDING, "Pending"),
        (PUBLISHED, "Published"),
        (CLOSED, "Closed"),
        (DELETED, "Deleted"),
    ]

    STATUS_CHOICE_MAP = dict(STATUS_CHOICES)
    # The status of the post.
    status = IntegerField(choices=STATUS_CHOICES, default=PUBLISHED)

    def get_status(self):
        return self.STATUS_CHOICE_MAP.get(self.status, "???")

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

    def is_toplevel(self):
        return self.type in self.TOP_LEVEL

    # The type of the post.
    type = IntegerField(choices=POST_TYPES, default=FORUM)

    # AUthor of the post.
    author = ForeignKey(User)

    # The tag value is the canonical form of the post's tags
    tag_val = CharField(max_length=200, default='')

    # The tag manager for the post
    tags = TaggableManager()

    # Post title.
    title = CharField(max_length=250, null=False)

    # A unique id for the post.
    uuid = CharField(max_length=256, null=True)

    # The user that edited the post most recently.
    lastedit_user = ForeignKey(User, related_name='editor', null=True)

    # Indicates the information value of the post.
    rank = FloatField(default=0, blank=True)

    # Number of upvotes for the post
    vote_count = IntegerField(default=0, blank=True, db_index=True)

    # The number of views for the post.
    view_count = IntegerField(default=0, blank=True)

    # The number of replies that a post has.
    reply_count = IntegerField(default=0, blank=True)

    # The number of comments that a post has.
    comment_count = IntegerField(default=0, blank=True)

    # Bookmark count.
    book_count = IntegerField(default=0)

    # Indicates indexing is needed.
    changed = BooleanField(default=True)

    # How many people follow that thread.
    subs_count = IntegerField(default=0)

    # The total score of the thread (used for top level only)
    thread_score = IntegerField(default=0, blank=True, db_index=True)

    # Date related fields.
    creation_date = DateTimeField(db_index=True, default=timezone.now)
    lastedit_date = DateTimeField(db_index=True, default=timezone.now)
    last_activity = DateTimeField(db_index=True, default=timezone.now)

    # Stickiness of the post.
    sticky = BooleanField(default=False, db_index=True)

    # Indicates whether the post has accepted answer.
    has_accepted = BooleanField(default=False, blank=True)

    # This will maintain the ancestor/descendant relationship bewteen posts.
    root = ForeignKey('self', related_name="descendants", null=True, blank=True)

    # This will maintain parent/child relationships between posts.
    parent = ForeignKey('self', null=True, blank=True, related_name='children')

    # This is the HTML that the user enters.
    text = TextField(default='')

    # This is the  HTML that gets displayed.
    html = TextField(default='')

    # This is the blurb field.
    blurb = TextField(default='')

    # What site does the post belong to.
    site = ForeignKey(Site, null=True)

    # Notification to users
    #notify = ManyToManyField(User)

    def save(self, *args, **kwargs):
        self.html = html.sanitize(self.text)
        self.blurb = html.strip_tags(self.text)[:200]
        super(Post, self).save(*args, **kwargs)

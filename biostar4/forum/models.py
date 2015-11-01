from django.db.models import *
from . import html
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.contrib.sites.models import Site
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import os, random, logging
from django.conf import settings
from django.db.models import F

logger = logging.getLogger('biostar')


def abspath(*args):
    return os.path.abspath(os.path.join(*args))


def create_user(email, password):
    user = User(email=email)
    user.set_password(password)
    user.save()
    # Need to refetch the user because signals may altered the profile.
    user = User.objects.get(pk=user.pk)
    return user


def file_path(instance, filename):
    oid = "%d" % instance.oid()
    now = timezone.now().strftime('%Y-%m-%d')
    rnd = random.randint(100, 900)
    key = "{now}/{oid}-{rnd}-{filename}".format(now=now, oid=oid, rnd=rnd, filename=filename)
    return key


class UserUpload(Model):
    "Represents an uploaded file attached to a user"
    name = CharField(default='File', max_length=500)
    user = ForeignKey(User)
    file = FileField(upload_to=file_path)

    def oid(self):
        # Used to figure out upload paths.
        return self.user.id

    def delete(self, *args, **kwds):
        super(UserUpload, self).delete(*args, **kwds)
        try:
            os.remove(abspath(settings.MEDIA_ROOT, self.file.name))
        except Exception as exc:
            logger.error('*** error deleting upload {} exc:{}'.format(self.id, exc))

    def save(self, *args, **kwargs):
        # Keep the end with extension if possible.
        self.name = self.name[-250:]
        super(UserUpload, self).save(*args, **kwargs)

class Message(Model):
    '''
    Represents a message to the user
    '''
    # How many messages to retain per user.
    MAX_MESSAGES = 50

    user = ForeignKey(User)
    new = BooleanField(default=True)
    content = TextField(null=False, blank=False)
    date = DateTimeField(default=timezone.now)

    @staticmethod
    def create_message(user, text):
        "Creates a message for the user"
        msg = Message.objects.create(user=user, content=text)
        user.profile.messages.add(msg)
        Profile.objects.filter(user=user).update(new_messages=F('new_messages') + 1)

    @staticmethod
    def limit_messages(user):
        "Limits messages per user"
        pks = Message.objects.filter(user=user).values_list("id", flat=True)[
              :Message.MAX_MESSAGES]
        Message.objects.filter(user=user).exclude(pk__in=pks).delete()

    class Meta:
        ordering = ['-date']


class Profile(Model):
    # File size in megabytes.
    MAX_FILE_SIZE = 5

    # How many files may be attached per user.
    MAX_FILE_NUM = 5

    # Valid user roles types.
    NEW_USER, TRUSTED_USER, MODERATOR, ADMIN = [1, 2, 3, 4]

    # User roles with readable labels.
    USER_ROLES = [
        (NEW_USER, "New user"),
        (TRUSTED_USER, "Trusted user"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    ]

    # Moderator roles.
    MODERATOR_ROLES = {MODERATOR, ADMIN}

    # User role quick lookup.
    USER_ROLES_MAP = dict(USER_ROLES)

    # User roles in the database.
    role = IntegerField(default=NEW_USER, choices=USER_ROLES)

    def get_role(self):
        return self.USER_ROLES_MAP.get(self.role, "???")

    def is_moderator(self):
        return self.role in self.MODERATOR_ROLES

    # User access types.
    ACTIVE, SUSPENDED, BANNED = [100, 200, 300]

    # User access type labels.
    ACCESS_TYPES = [
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (BANNED, "Banned"),
    ]

    # User access type lookup.
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
    files = ManyToManyField(UserUpload)
    text = CharField(max_length=3000, default='')
    html = CharField(max_length=6000, default='')

    tags = TaggableManager()

    # Messages for the user.
    messages = ManyToManyField(Message)

    def save(self, *args, **kwargs):
        self.html = html.sanitize(self.text)
        super(Profile, self).save(*args, **kwargs)


class PostManager(Manager):
    def build(self, query):
        "Adds related and prefetch elements to the query."
        return query.select_related("root", "author", "author__profile", "lastedit_user",
                                    "lastedit_user__profile").prefetch_related("tags")

    def defer(self, query):
        "Content that does not need to be present in post lists."
        return query.defer("text", "html")

    def my_posts(self, user):
        "Selects posts by a user"
        query = self.filter(author=user)
        query = self.build(query)
        query = self.defer(query)
        return query

    def top_level(self, user):
        "Selects the toplevel posts for listing"
        is_moderator = user.is_authenticated() and user.profile.is_moderator()
        query = self.filter(type__in=Post.TOP_LEVEL)

        if is_moderator:
            # Moderators see all posts.
            status = (Post.PUBLISHED, Post.DELETED, Post.CLOSED)
        else:
            # Regular users see published and closed posts.
            status = (Post.PUBLISHED, Post.CLOSED)

        query = query.filter(status__in=status)
        query = self.build(query)
        query = self.defer(query)
        return query


class Follower(Model):
    "Represents an uploaded file attached to a post"
    MESSAGES, EMAIL, NOFOLLOW = [1, 2, 3]
    NOTIFY_CHOICES = [
        (MESSAGES, "Messages"),
        (EMAIL, "Email"),
        (NOFOLLOW, "No Messages")
    ]
    user = ForeignKey(User)
    post = ForeignKey('Post')
    type = IntegerField(choices=NOTIFY_CHOICES, default=EMAIL)

    @staticmethod
    def add(user, post, type=None):
        type = type or Follower.EMAIL
        follower = Follower.objects.create(user=user, post=post, type=type)
        post.followers.add(follower)


class PostUpload(Model):
    "Represents an uploaded file attached to a post"
    name = CharField(default='File', max_length=500)
    user = ForeignKey(User)
    post = ForeignKey('Post')
    file = FileField(upload_to=file_path)

    def oid(self):
        # Used to figure out upload paths.
        return self.post.id

    def delete(self, *args, **kwargs):
        super(PostUpload, self).delete(*args, **kwargs)
        try:
            os.remove(abspath(settings.MEDIA_ROOT, self.file.name))
        except Exception as exc:
            logger.error('*** error deleting upload {} exc:{}'.format(self.id, exc))

    def save(self, *args, **kwargs):
        # Keep the end with extension if possible.
        self.name = self.name[-250:]
        super(PostUpload, self).save(*args, **kwargs)

class Post(Model):
    # How many files may be attached to posts.
    MAX_FILE_NUM = 4

    # File size in  megabytes.
    MAX_FILE_SIZE = 5

    # Maximal character size for a post.
    MAX_CHARS = 15000

    # A manager to get a reduced amount of filed on posts.
    objects = PostManager()

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

    # Uploads attached to the post
    files = ManyToManyField(PostUpload, related_name='posts')

    # Notification to users.
    followers = ManyToManyField(Follower, related_name="posts")

    class Meta:
        ordering = ['-lastedit_date']

    def get_files(self):
        return self.files.all()

    def save(self, *args, **kwargs):
        self.lastedit_date = self.lastedit_date or timezone.now()
        self.html = html.sanitize(self.text)
        self.blurb = html.strip_tags(self.text)[:200]
        super(Post, self).save(*args, **kwargs)

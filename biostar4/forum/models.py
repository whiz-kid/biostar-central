"""
This file must remain Python 2.7 compatible to allow imports from Biostar 2.
"""
import logging
from datetime import datetime
from mongoengine import *
from django.conf import settings
from django.shortcuts import redirect
from biostar4.forum import utils, html
from functools import wraps
from django.core.urlresolvers import reverse
from django.db import models as dj

logger = logging.getLogger('biostar')

db = connect(settings.MONGODB_NAME, host=settings.MONGODB_URI)


# db.drop_database(settings.MONGODB_NAME)

def login_required(f):
    "Requires authorized user"

    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        user = User.get(request)
        if not user:
            utils.error(request, "Login required to access that feature")
            return redirect('home')
        return f(request, user, *args, **kwargs)

    return decorated_function


def fill_user(f):
    "Fills the user parameter on a wrapped function"

    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        user = request.user
        return f(request, user, *args, **kwargs)

    return decorated_function


def fill_post(f):
    "Fills the post based on an post id"

    @wraps(f)
    def decorated_function(request, pid, *args, **kwargs):
        user = request.user
        post = Post.objects.filter(pid=pid).first()
        if not post:
            utils.error(request, "The post cannot be found. Perhaps it has been deleted.")
            return redirect("home")

        if not post.is_toplevel():
            return redirect(post.url())

        return f(request, user, post, *args, **kwargs)

    return decorated_function


def parse_tags(text):
    "Parses tags as comma or space separated"

    # Figure out split character.
    tags = text.split(",")
    if len(tags) == 1:
        tags = text.split()
    tags = [t.strip()[:12] for t in tags]
    tags = filter(None, tags)
    # Fix tag case.
    def fixcase(x):
        return x.lower() if len(x) > 1 else x.upper()

    tags = list(map(fixcase, tags))
    return tags


class SearchDoc(dj.Model):
    "Required for haystack to work"
    pid = dj.IntegerField(unique=True, primary_key=True)
    new = dj.BooleanField(db_index=True, default=True)
    title = dj.CharField(max_length=500)
    content = dj.CharField(max_length=20000)


class Message(EmbeddedDocument):
    new = BooleanField(default=True)
    html = StringField(required=True)
    date = DateTimeField(required=True)


class User(Document):
    SESSION_NAME = 'user'
    # File size in megabytes.
    MAX_FILE_SIZE = 5
    MAX_FILE_NUM = 10
    MAX_MESSAGES = 25

    NEW_USER, TRUSTED_USER, MODERATOR, ADMIN = [1, 2, 3, 4]

    USER_ROLES = dict([
        (NEW_USER, "New user"),
        (TRUSTED_USER, "Trusted user"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    ])

    # User roles.
    role = IntField(required=True, default=NEW_USER, choices=list(USER_ROLES.keys()))

    def get_role(self):
        return self.USER_ROLES.get(self.role, "???")

    ACTIVE, SUSPENDED, BANNED = [100, 200, 300]

    ACCESS_TYPES = dict([
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (BANNED, "Banned"),
    ])

    # User login permissions.
    access = IntField(required=True, default=ACTIVE,
                      choices=list(ACCESS_TYPES.keys()))

    # A user friendly representation of access permissions.
    def get_access(self):
        return self.ACCESS_TYPES.get(self.access, "???")

    def is_suspended(self):
        return self.access != self.ACTIVE

    # Autoincrementing sequence.
    seq = SequenceField()

    # The userid for the user. Set automatically.
    uid = IntField(primary_key=True)

    # User display name.
    name = StringField(max_length=200, required=False, default='')

    # The user email address.
    email = StringField(max_length=200, required=True, unique=True)

    # User password. Set it with set_password()
    password = StringField(max_length=200, required=True)

    # Username visible on the site.
    username = StringField(max_length=15, required=False, default='')

    # User geographical location.
    location = StringField(max_length=100, required=False, default=' ')

    # Twitter handle.
    twitter = StringField(max_length=100, required=False, default='')

    # Google Scholar id.
    scholar = StringField(max_length=100, required=False, default='')

    # List us user selected tags.
    my_tags = ListField(StringField(max_length=500))

    # List of watched tags.
    watched_tags = ListField(StringField(max_length=500))

    # User score.
    score = IntField(default=0, required=True)

    # How many posts has the user created.
    post_num = IntField(default=0, required=True)

    # New messages for this user.
    new_messages = IntField(default=0)

    # New votes for the user.
    new_votes = IntField(default=0)

    # New posts for the user.
    new_posts = IntField(default=0)

    # The website for the user.
    website = StringField(max_length=250, required=False, default='')

    # Join and last login dates.
    date_joined = DateTimeField()
    last_login = DateTimeField()

    # The user's information field as markdown text and as html.
    text = StringField(max_length=3000, required=False, default='about me')
    html = StringField(max_length=6000, required=False, default='about me')

    # Relative paths to files uploaded by the user.
    files = ListField(StringField(max_length=250, required=False))

    # User related messages.
    messages = SortedListField(EmbeddedDocumentField(Message),
                               ordering="date", reverse=True)

    meta = {
        'indexes': [
            'email',
            'last_login',
            'date_joined',
        ]
    }

    @queryset_manager
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
        self.uid = self.seq
        self.username = self.username or "user%d" % self.uid
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


class Notify(EmbeddedDocument):
    "Represents notification targets on a document"
    LOCAL, EMAIL, NONE = [ 1, 2,  3]

    user = ReferenceField(User, required=True)
    ntype = IntField(choices=[LOCAL, EMAIL, NONE], default=LOCAL)

    def __repr__(self):
        return "Notify: {}, ntype:{}".format(self.user, self.ntype)

class Post(Document):
    # The maximum number of characters in a post.
    MAX_CHARS = 15000

    DRAFT, PENDING, PUBLISHED, CLOSED, DELETED = [1, 2, 3, 4, 5]

    STATUS_CHOICES = dict([
        (DRAFT, "Draft"),
        (PENDING, "Pending"),
        (PUBLISHED, "Published"),
        (CLOSED, "Closed"),
        (DELETED, "Deleted"),
    ])

    # The status of the post.
    status = IntField(choices=list(STATUS_CHOICES.keys()), required=True, default=PUBLISHED)

    def get_status(self):
        return self.STATUS_CHOICES.get(self.status, "???")

    # Valid post types.
    QUESTION, ANSWER, COMMENT, TUTORIAL, FORUM, JOB, TOOL, NEWS = range(1, 9)

    POST_TYPES = dict([
        (QUESTION, "Question"),
        (ANSWER, "Answer"),
        (COMMENT, "Comment"),
        (TUTORIAL, "Tutorial"),
        (FORUM, "Forum"),
        (JOB, "Job"),
        (TOOL, "Tool"),
        (NEWS, "News"),
    ])

    # Top level posts.
    TOP_LEVEL = {QUESTION, FORUM, TOOL, TUTORIAL, NEWS}

    # Type of the post. There is a clash with a mongodb operator name
    # hence it is called ptype.
    ptype = IntField(choices=list(POST_TYPES.keys()), required=True, default=FORUM)

    def get_ptype(self):
        return self.STATUS_CHOICES.get(self.ptype, "???")

    def is_toplevel(self):
        return self.ptype in Post.TOP_LEVEL

    @queryset_manager
    def fast(cls, queryset):
        # Fast query that removes the heavy elements
        return queryset.exclude('text', 'html', 'notify')

    # Sequence field that autoincrements.
    seq = SequenceField()

    # Post title.
    title = StringField(max_length=250, required=True)

    # Post author.
    author = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)

    # Last user that modified the post or thread.
    lastedit_user = ReferenceField(User, reverse_delete_rule=CASCADE)

    # Users that need to be notified when the threads gets updated.
    notify = ListField(EmbeddedDocumentField(Notify))

    # Tags for the post.
    tags = ListField(StringField(max_length=500))

    # A small blurb on the post
    blurb = StringField(max_length=1000, default='')

    # Post markdown text.
    text = StringField(max_length=30000, required=True)

    # Post body rendered as html.
    html = StringField(max_length=35000, required=True)

    # Post creation date.
    creation_date = DateTimeField()

    # Last modification of the post.
    lastedit_date = DateTimeField()

    # Post id. Posts are accessed via this object.
    pid = IntField(primary_key=True)

    # Post view counts.
    view_count = IntField(default=0)

    # How many replies for the thread.
    reply_count = IntField(default=0)

    # How many votes for the post.
    vote_count = IntField(default=0)

    # Bookmark count.
    book_count = IntField(default=0)

    # Indicates the information value of the post.
    rank = FloatField(default=0)

    # Indicates a new post. Will trigger asynchronous events.
    is_new_post = BooleanField(default=True)

    # How many people follow that thread.
    follow_count = IntField(default=0)

    # The total score of the thread (used for top level only)
    thread_score = IntField(default=0)

    # Stickiness of the post.
    sticky = BooleanField(default=False)

    # Indicates whether the post has accepted answer.
    has_accepted = BooleanField(default=False)

    # This will maintain the ancestor/descendant relationship bewteen posts.
    root = ReferenceField('self', reverse_delete_rule=CASCADE)

    # This will maintain parent/child replationships between posts.
    parent = ReferenceField('self', reverse_delete_rule=CASCADE)

    # Relative paths to files uploaded by the user.
    files = ListField(StringField(max_length=250, required=False))

    meta = {
        'indexes': [
            'creation_date',
            'lastedit_date',
            'is_new_post',
            'thread_score',
            'view_count',
            'reply_count',
            'vote_count',
            'ptype',
        ]
    }


    def url(self):
        uri = reverse("post_detail", kwargs={'pid': self.root.pid})
        return "%s#%s" % (uri, self.pid)


    def add_notification(self, user, ntype=Notify.LOCAL):
        Post.objects(pid=self.root.pid).update_one(pull__notify=Notify(user=user))
        Post.objects(pid=self.root.pid).update_one(push__notify=Notify(user=user, ntype=ntype))

    @staticmethod
    def remove_notification(post, user):
        Post.objects(pid=post.pid).update_one(pull__notify=Notify(user=user))

    def save(self, *args, **kwargs):
        now = datetime.now()
        self.creation_date = self.creation_date or now
        self.lastedit_date = self.lastedit_date or now
        self.pid = self.seq
        self.html = html.sanitize(self.text)
        self.blurb = html.strip_tags(self.text)[:250] + '...'
        self.blurb = self.blurb.strip()
        self.root = self.root or self
        self.parent = self.parent or self

        # Add document to search archive.
        doc, flag = SearchDoc.objects.get_or_create(pid=self.pid)
        SearchDoc.objects.filter(pid=self.pid).update(new=True, content=self.text)

        super(Post, self).save(*args, **kwargs)

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from biostar4.forum.models import *
from django.core.management import call_command
import os, json
from itertools import islice
from html2text import html2text

BATCH_SIZE = 25

def join(*args):
    return (os.path.join(*args))


def abspath(*args):
    return os.path.abspath(os.path.join(*args))


def get_path(dest, date, oid):
    segment = date.strftime("%Y-%m-%d")
    segname = join(segment, oid)
    segpath = join(dest, segment)
    if not os.path.isdir(segpath):
        os.mkdir(segpath)
    fname = join(dest, segname)
    return fname, segname


class B2_Post():
    "Represents a post in Biostar 2"

    # Post statuses.
    PENDING, OPEN, CLOSED, DELETED = range(4)
    STATUS_CHOICES = [(PENDING, "Pending"), (OPEN, "Open"), (CLOSED, "Closed"),
                      (DELETED, "Deleted")]

    # Question types. Answers should be listed before comments.
    QUESTION, ANSWER, JOB, FORUM, PAGE, BLOG, COMMENT, DATA, TUTORIAL, BOARD, TOOL, NEWS = range(
        12)

    TYPE_CHOICES = [
        (QUESTION, "Question"), (ANSWER, "Answer"), (COMMENT, "Comment"),
        (JOB, "Job"), (FORUM, "Forum"), (TUTORIAL, "Tutorial"),
        (DATA, "Data"), (PAGE, "Page"), (TOOL, "Tool"), (NEWS, "News"),
        (BLOG, "Blog"), (BOARD, "Bulletin Board")
    ]

    TOP_LEVEL = set((QUESTION, JOB, FORUM, PAGE, BLOG, DATA, TUTORIAL, TOOL, NEWS, BOARD))


class B2_User():
    "Represents a User in Biostar 2"
    USER, MODERATOR, ADMIN, BLOG = range(4)
    TYPE_CHOICES = [(USER, "User"), (MODERATOR, "Moderator"), (ADMIN, "Admin"),
                    (BLOG, "Blog")]

    NEW_USER, TRUSTED, SUSPENDED, BANNED = range(4)
    STATUS_CHOICES = (
        (NEW_USER, 'New User'), (TRUSTED, 'Trusted'), (SUSPENDED, 'Suspended'),
        (BANNED, 'Banned'))


def migrate_posts(users, dest, limit, batch=25):

    # Delete all posts from Biostar 4.
    Post.objects.all().delete()

    type2type = {
        B2_Post.QUESTION: Post.QUESTION,
        B2_Post.ANSWER: Post.ANSWER,
        B2_Post.JOB: Post.JOB,
        B2_Post.TOOL: Post.TOOL,
        B2_Post.TUTORIAL: Post.TUTORIAL,
        B2_Post.FORUM: Post.FORUM,
        B2_Post.COMMENT: Post.COMMENT,
        B2_Post.NEWS: Post.NEWS,
    }

    status2status = {
        B2_Post.OPEN: Post.PUBLISHED,
        B2_Post.CLOSED: Post.CLOSED,
        B2_Post.DELETED: Post.DELETED,
    }

    toc = open(abspath(dest, "posts.txt"))

    def post_gen():
        for path in islice(toc, limit):
            path = path.strip()
            fname = abspath(dest, path)
            d = json.loads(open(fname).read())
            author_id = d['author_id']
            lastedit_user_id = d['lastedit_user_id']

            if author_id not in users:
                print("!!! skipping author_id=%s" % author_id)
                continue

            if lastedit_user_id not in users:
                print("!!! skipping lastedit_user_id=%s" % lastedit_user_id)
                continue

            author = users[author_id]
            lastedit_user = users[lastedit_user_id]
            text = html2text(d['text'])
            p = Post(
                title=d['title'],
                text=text,
                blurb=text[:200],
                html=d['html'],
                tag_val=d['tag_val'],
                author=author,
                lastedit_user=lastedit_user,
                creation_date=d['creation_date'],
                lastedit_date=d['lastedit_date'],
                view_count=d['view_count'],
                reply_count=d['reply_count'],
                vote_count=d['vote_count'],
                thread_score=d['thread_score'],
                has_accepted=d['has_accepted'],
                type=type2type[d['type']],
                status=status2status[d['status']]
            )
            yield p

    Post.objects.bulk_create(post_gen(), batch_size=batch)

    pc = Post.objects.all().count()
    print('*** Migrated {} posts.'.format(pc))

def migrate_users(dest, limit, batch=25):
    # Maintains the mapping to userid.
    users = dict()

    # Delete all users from Biostar4.
    User.objects.all().delete()

    # Remaps user roles
    type2role = {
        B2_User.BLOG: Profile.NEW_USER,
        B2_User.USER: Profile.TRUSTED_USER,
        B2_User.MODERATOR: Profile.MODERATOR,
        B2_User.ADMIN: Profile.ADMIN,
    }

    # Remaps user access
    status2access = {
        B2_User.NEW_USER: Profile.ACTIVE,
        B2_User.TRUSTED: Profile.ACTIVE,
        B2_User.SUSPENDED: Profile.SUSPENDED,
        B2_User.BANNED: Profile.SUSPENDED,
    }

    def user_gen():
        toc = open(abspath(dest, "users.txt"))

        for path in islice(toc, limit):
            path = path.strip()
            fname = abspath(dest, path)
            d = json.loads(open(fname).read())
            u = User(
                id=d['id'],
                username=str(d['id']),
                email=d['email'],
                password=d['password'],
                date_joined=d['date_joined'],
                last_login=d['last_login'],
            )
            users[u.id] = u
            yield u

    # Bulk insert the users.
    User.objects.bulk_create(user_gen(), batch_size=batch)

    def profile_gen():
        toc = open(abspath(dest, "users.txt"))

        for path in islice(toc, limit):
            path = path.strip()
            fname = abspath(dest, path)
            d = json.loads(open(fname).read())
            text = html2text(d['text'])
            prof = Profile(
                user=users[d['id']],
                name=d['name'],
                score=d['score'],
                text=text,
                scholar=d['scholar'],
                twitter=d['twitter'],
                location=d['location'],
                website=d['website'],
                access=status2access[d['status']],
                role=type2role[d['type']],
            )
            yield prof

    # Bulk inserting the profiles.
    Profile.objects.bulk_create(profile_gen(), batch_size=batch)

    print("*** Migrated %s users." % len(users))

    return users


class Command(BaseCommand):
    help = 'Imports a biostar2 data dump'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100,
                            dest='limit', help='Limit to just these entries')

        parser.add_argument('--dir',
                            dest='dir', help='Import directory')

    def handle(self, *args, **options):
        print("*** DJANGO_SETTINGS_MODULE={}".format(os.getenv("DJANGO_SETTINGS_MODULE")))
        if options['dir']:
            limit = options['limit']
            dest = abspath(options['dir'])
            print('*** Migrating the data from {}, limit={}.'.format(dest, limit))
            users = migrate_users(dest=dest, limit=limit)
            migrate_posts(users=users, dest=dest, limit=limit)
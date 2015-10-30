"""
Exports biostar2 into biostar4.

Must be run within a biostar2 instance.

Must be compatible with django 1.6 and django 1.8
"""
import sys, os, warnings, json, html2text
import click

__PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

sys.path.append(os.getcwd())
sys.path.append(__PATH)

from django.conf import settings

from biostar4.forum.models import User

from itertools import islice

def join(*args):
    return (os.path.join(*args))

def abspath(*args):
    return os.path.abspath(os.path.join(*args))

def get_path(dest, date, oid):
    segment = date.strftime("%Y-%m-%d")
    segname = join(segment, oid )
    segpath = join(dest, segment)
    if not os.path.isdir(segpath):
        os.mkdir(segpath)
    fname = join(dest, segname)
    return fname, segname

@click.command()
@click.option('--dest', help='Migrates the data from this folder.')
@click.option('--limit', type=int, default=200, help='Limit to these many users/posts.')
def main(dest, limit=200):

    if limit == 0:
        limit = None

    if dest:
        dest = abspath(dest)
        print('Migrating the data from {}, limit={}.'.format(dest, limit))
        users = migrate_users(dest=dest, limit=limit)
        #migrate_posts(dest=dest, limit=limit)


class B2_Post():
    "Represents a post in Biostar 2"

    # Post statuses.
    PENDING, OPEN, CLOSED, DELETED = range(4)
    STATUS_CHOICES = [(PENDING, "Pending"), (OPEN, "Open"), (CLOSED, "Closed"), (DELETED, "Deleted")]

    # Question types. Answers should be listed before comments.
    QUESTION, ANSWER, JOB, FORUM, PAGE, BLOG, COMMENT, DATA, TUTORIAL, BOARD, TOOL, NEWS = range(12)

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
    TYPE_CHOICES = [(USER, "User"), (MODERATOR, "Moderator"), (ADMIN, "Admin"), (BLOG, "Blog")]

    NEW_USER, TRUSTED, SUSPENDED, BANNED = range(4)
    STATUS_CHOICES = ((NEW_USER, 'New User'), (TRUSTED, 'Trusted'), (SUSPENDED, 'Suspended'), (BANNED, 'Banned'))


def migrate_posts(users, limit):

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

    pid2ref = dict()
    post_count = 0;
    for p1 in B2_Post.objects.filter(status__in=[B2_Post.OPEN, B2_Post.CLOSED]).order_by(
            'id')[:limit]:

        author = users.get(p1.author_id)
        if not author:
            continue

        pid = p1.id
        nextid = B4_Post.seq.get_next_value()

        if (nextid != p1.id):
            print("*** setting post next id from %d to %d" % (nextid, pid))
            B4_Post.seq.set_next_value(pid-1)

        lastedit_user = users.get(p1.lastedit_user_id) or author
        tags = models4.parse_tags(p1.tag_val)
        p2 = B4_Post(
            title=p1.title,
            text=html2text(p1.content),
            html=p1.html,
            tags=tags,
            author=author,
            lastedit_user=lastedit_user,
            creation_date=p1.creation_date,
            lastedit_date=p1.lastedit_date,
            view_count=p1.view_count,
            reply_count=p1.reply_count,
            vote_count=p1.vote_count,
            thread_score=p1.thread_score,
            has_accepted=p1.has_accepted,
            ptype=type2type[p1.type],
            status=status2status[p1.status]
        )
        p2.save()


        # Post ids must match!
        assert(p1.id == p2.pid)

        # Resave with the references set.
        pid2ref[p1.id] = p2
        p2.root = pid2ref[p1.root_id]
        p2.parent = pid2ref[p1.parent_id]
        p2.root.add_notification(author)
        p2.save()

        #B4_Post.remove_follower(p2, author)

        post_count += 1

    click.echo('Migrated %s posts.' % post_count)


def migrate_users(dest, limit):

    # Maintains the mapping to userid.
    users = dict()

    # Delete all users from Biostar4.
    #User.objects.all().delete()

    # Remaps user roles
    type2role = {
        B2_User.BLOG: User.NEW_USER,
        B2_User.USER: User.TRUSTED_USER,
        B2_User.MODERATOR: User.MODERATOR,
        B2_User.ADMIN: User.ADMIN,
    }

    # Remaps user access
    status2access = {
        B2_User.NEW_USER: User.ACTIVE,
        B2_User.TRUSTED: User.ACTIVE,
        B2_User.SUSPENDED: User.SUSPENDED,
        B2_User.BANNED: User.SUSPENDED,
    }

    toc = open(abspath(dest, "users.txt"))

    for path in islice(toc, limit):
        path = path.strip()

        fname = abspath(dest, path)

        d = json.loads(open(fname).read())

        text = html2text.html2text(d['text'])

        u = User(
            id=d['id'],
            email=d['email'],
            name=d['name'],
            password=d['password'],
            score=d['score'],
            text=text,
            #date_joined=d['date_joined'],
            last_login=d['last_login'],
            scholar=d['scholar'],
            twitter=d['twitter'],
            location=d['location'],
            website=d['website'],
            access=status2access[d['status']],
            role=type2role[d['type']],
        )

        u.save()

        users[u.id] = u

    click.echo("Migrated %s users." % len(users))

    return users

if __name__ == '__main__':
    main()

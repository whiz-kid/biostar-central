"""
Exports biostar2 into biostar4.

Must be run within a biostar2 instance.
"""
import sys, os, warnings
import click

__PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

sys.path.append(os.getcwd())
sys.path.append(__PATH)

from django.conf import settings

from biostar.server import models as models2
from biostar4.forum import models as models4

from biostar4.forum.utils import get_uuid
from html2text import html2text

from biostar.server.models import Post as B2_Post
from biostar.apps.users.models import User as B2_User

from biostar4.forum.models import Post as B4_Post
from biostar4.forum.models import User as B4_User

# Mongoengine raises deprecation warnings.
warnings.simplefilter("ignore")


@click.command()
@click.option('--drop', is_flag=True, default=False,
              help='Drops database. This resets the counters.')
@click.option('--migrate', is_flag=True, default=False, help='Migrates the data.')
@click.option('--limit', type=int, default=200, help='Limit to these many users/posts.')
def main(drop, migrate, limit=200):

    click.echo("Migration script from biostar2 to biostar4")
    click.echo("MONGODB_NAME: {} ".format(settings.MONGODB_NAME))
    click.echo("MONGODB_URI: {} ".format(settings.MONGODB_URI))
    click.echo("DJANGO_SETTINGS_MODULE: {} ".format(os.getenv("DJANGO_SETTINGS_MODULE")))

    if not settings.SOCIALACCOUNT_ADAPTER:
        # The settings file does not seem to be correct.
        click.echo("ERROR: The django settings file is not for biostar2")
        sys.exit()

    user_count = B2_User.objects.all().count()
    post_count = B2_Post.objects.all().count()
    click.echo(
        "Database contains {:d} users and {:d} posts.".format(user_count, post_count))

    click.echo("Connecting to MongoDB: {}".format(settings.MONGODB_URI))

    names = ", ".join(models4.db.database_names())
    click.echo("Found MongoDB databases: {}".format(names))
    click.echo('-' * 20)

    if drop:
        click.echo('Dropped the mongodb database: %s' % settings.MONGODB_NAME)
        models4.db.drop_database(settings.MONGODB_NAME)

    if migrate:
        click.echo('Migrating the data, limit=%d.' % limit)
        users = migrate_users(limit=limit)
        migrate_posts(users=users, limit=limit)

def migrate_posts(users, limit):

    # Delete all posts from Biostar 4.
    B4_Post.objects.all().delete()

    type2type = {
        B2_Post.QUESTION: B4_Post.QUESTION,
        B2_Post.ANSWER: B4_Post.ANSWER,
        B2_Post.JOB: B4_Post.JOB,
        B2_Post.TOOL: B4_Post.TOOL,
        B2_Post.TUTORIAL: B4_Post.TUTORIAL,
        B2_Post.FORUM: B4_Post.FORUM,
        B2_Post.COMMENT: B4_Post.COMMENT,
        B2_Post.NEWS: B4_Post.NEWS,
    }

    status2status = {
        B2_Post.OPEN: B4_Post.PUBLISHED,
        B2_Post.CLOSED: B4_Post.CLOSED,
        B2_Post.DELETED: B4_Post.DELETED,
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


def migrate_users(limit):

    # Maintains the mapping to userid.
    users = dict()

    # Delete all users from Biostar4.
    B4_User.objects.all().delete()

    # Remaps user roles
    type2role = {
        B2_User.BLOG: B4_User.NEW_USER,
        B2_User.USER: B4_User.TRUSTED_USER,
        B2_User.MODERATOR: B4_User.MODERATOR,
        B2_User.ADMIN: B4_User.ADMIN,
    }

    # Remaps user access
    status2access = {
        B2_User.NEW_USER: B4_User.ACTIVE,
        B2_User.TRUSTED: B4_User.ACTIVE,
        B2_User.SUSPENDED: B4_User.SUSPENDED,
        B2_User.BANNED: B4_User.SUSPENDED,
    }

    for u1 in B2_User.objects.all().order_by('id')[:limit]:

        uid = u1.id
        nextid = B4_User.seq.get_next_value()
        if ( nextid != uid):
            print("*** setting user next id from %d to %d" % (nextid, uid))
            B4_User.seq.set_next_value(uid-1)

        u2 = B4_User(
            email=u1.email,
            name=u1.name,
            password=get_uuid(),
            score=u1.score,
            text=u1.profile.info,
            date_joined=u1.profile.date_joined,
            last_login=u1.profile.last_login,
            scholar=u1.profile.scholar,
            twitter=u1.profile.twitter_id,
            location=u1.profile.location,
            website=u1.profile.website,
            access=status2access[u1.status],
            role=type2role[u1.type],
        )
        u2.save()

        users[u1.id] = u2

        # User ids must match
        assert(u1.id == u2.uid)

    click.echo("Migrated %s users." % len(users))
    return users


if __name__ == '__main__':
    main()

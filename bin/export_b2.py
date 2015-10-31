"""
Exports biostar2 as flat files.
Must be run within a biostar2 instance.
"""
import sys, os, json
import argparse

from django.conf import settings

from biostar.server import models
from biostar.server.models import Post
from biostar.apps.users.models import User

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

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100,
                        help="limit export to these many entries")

    parser.add_argument("--dir", type=str,
                        help="destination directory")

    args = parser.parse_args()

    user_count = User.objects.all().count()
    post_count = Post.objects.all().count()
    print("*** Database contains {:d} users and {:d} posts.".format(user_count, post_count))

    if args.dir:
        limit = args.limit
        dest = abspath(args.dir)
        if not os.path.isdir(dest):
            os.mkdir(dest)
        print('*** Migrating the data into {}, limit={}.'.format(dest, limit))
        migrate_users(dest=dest, limit=limit)
        migrate_posts(dest=dest, limit=limit)

def migrate_posts(dest, limit):
    posts = Post.objects.all().order_by('id')[:limit]
    toc = open(join(dest, "posts.txt"), "wt")


    pc = 0;
    for p in posts:

        oid = "p-%s" % p.id
        fname, segname = get_path(dest=dest, date=p.creation_date, oid=oid)

        toc.write("%s\n" % segname)

        data =dict(
            title=p.title,
            text=p.content,
            html=p.html,
            tag_val=p.tag_val,
            author_id=p.author.id,
            lastedit_user_id=p.lastedit_user_id,
            creation_date=p.creation_date.isoformat(),
            lastedit_date=p.lastedit_date.isoformat(),
            view_count=p.view_count,
            reply_count=p.reply_count,
            vote_count=p.vote_count,
            thread_score=p.thread_score,
            has_accepted=p.has_accepted,
            type=p.type,
            status=p.status,
        )

        out = json.dumps(data)
        fp = open(fname, 'wt')
        fp.write(out)
        fp.close()

        pc += 1

    print('*** Migrated %s posts.' % pc)



def migrate_users(dest, limit):

    # Maintains the mapping to userid.
    uc = 0
    users = User.objects.all().order_by('id').select_related('profile')[:limit]
    toc = open(join(dest, "users.txt"), "wt")
    dest = os.path.abspath(dest)

    for u in users:

        oid = "u-%s" % u.id
        fname, segname = get_path(dest=dest, date=u.profile.date_joined, oid=oid)

        toc.write("%s\n" % segname)

        data = dict(
            id = u.id,
            email=u.email,
            name=u.name,
            password=u.password,
            score=u.score,
            text=u.profile.info,
            date_joined=u.profile.date_joined.isoformat(),
            last_login=u.profile.last_login.isoformat(),
            scholar=u.profile.scholar,
            twitter=u.profile.twitter_id,
            location=u.profile.location,
            website=u.profile.website,
            status=u.status,
            type=u.type,
        )
        out = json.dumps(data)
        fp = open(fname, 'wt')
        fp.write(out)
        fp.close()
        uc += 1

    print("*** Migrated %s users." % uc)

if __name__ == '__main__':
    main()

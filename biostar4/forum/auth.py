from .models import *
from .utils import *

def update(obj, data):
    "Sets object attributes from a dictionary"
    for name, value in data.items():
        if hasattr(obj, name):
            setattr(obj, name, value)
    return obj

def edit_user(user, data):
    "Edits a user based on a data dictionary"
    user = update(user, data)
    user.profile = update(user.profile, data)


def manage_user_files(user, files=[], remove_ids=[]):
    "Manages user file uploads"
    for file in files:
        upload = UserUpload.objects.create(file=file, user=user, name=file.name)
        user.profile.files.add(upload)

    for upload in UserUpload.objects.filter(user=user, pk__in=remove_ids):
        # Triggers the delete to remove the file as well.
        upload.delete()


def manage_post_files(user, post, files=[], remove_ids=[]):
    "Manage post file uploads"
    for file in files:
        upload = PostUpload.objects.create(file=file, user=user, post=post, name=file.name)
        post.files.add(upload)

    for upload in PostUpload.objects.filter(user=user, post=post, pk__in=remove_ids):
        # Triggers the delete to remove the file as well.
        upload.delete()

def edit_toplevel_post(user, data, post=None):
    "Edits or creates a toplevel post from incoming parameters"
    get = data.get
    title, text, ptype = get('title'), get('text'), get('type')
    tag_val, status = get('tag_val'), get('status')

    if not post:
        # Creates the post
        post = Post(author=user)

    # Update post attributes.
    post.title = title
    post.text = text
    post.type = ptype
    post.lastedit_user = user
    post.status = status
    post.tag_val = tag_val
    post.save()

    # Set the post tags.
    tags = parse_tags(post.tag_val)
    post.tags.set(*tags)

    return post



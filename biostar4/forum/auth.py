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


def set_user_files(request, user):
    "Manages user file uploads"

    remove_ids = request.POST.getlist('remove_ids')
    files = request.FILES.getlist('uploads')

    for file in files:
        upload = UserUpload.objects.create(file=file, user=user, name=file.name)
        user.profile.files.add(upload)

    for upload in UserUpload.objects.filter(user=user, pk__in=remove_ids):
        # Triggers the delete to remove the file as well.
        upload.delete()


def set_post_files(request, user, post):
    "Manage post file uploads."
    remove_ids = request.POST.getlist('remove_ids')
    files = request.FILES.getlist('uploads')

    for file in files:
        upload = PostUpload.objects.create(file=file, user=user, post=post, name=file.name)
        post.files.add(upload)

    for upload in PostUpload.objects.filter(user=user, post=post, pk__in=remove_ids):
        # Triggers the delete to remove the file as well.
        upload.delete()

def new_toplevel_post(user, data):
    "Creates a toplevel post."
    post = Post(author=user)
    post = edit_toplevel_post(user=user, post=post, data=data)
    return post

def edit_toplevel_post(user, post, data):
    "Edits a toplevel post."
    get = data.get
    title, text, ptype = get('title'), get('text'), get('type')
    tag_val, status = get('tag_val'), get('status')

    # Update post attributes.
    post.title = title
    post.text = text
    post.type = ptype
    post.lastedit_user = user
    post.lastedit_date = None
    post.status = status
    post.tag_val = tag_val
    post.save()

    # Set the post tags.
    tags = parse_tags(post.tag_val)
    post.tags.set(*tags)

    return post

def new_content_post(user, data):
    "Creates a toplevel post."
    post = Post(author=user)
    post = edit_content_post(user=user, post=post, data=data)
    return post

def edit_content_post(user, post, data):
    "Edits a content post"
    get = data.get
    text, parent_id, status = get('text'),  get('parent'), get('status', Post.PUBLISHED)
    parent = Post.objects.get(id=parent_id)
    ptype = Post.ANSWER if parent.is_toplevel() else Post.COMMENT
    post.lastedit_user = user
    post.type = ptype
    post.status = status
    post.parent = parent
    post.text = text
    post.save()

    return post
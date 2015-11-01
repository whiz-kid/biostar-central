from .models import *
from .utils import *


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



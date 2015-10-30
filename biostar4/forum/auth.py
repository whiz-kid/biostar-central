from .models import *
from .utils import *


def create_toplevel_post(user, data):
    "Creates a toplevel post from incoming paramters"
    get = data.get
    title, text, ptype = get('title'), get('text'), get('type')
    tag_val, status = get('tags'), get('status')
    post = Post(title=title, text=text, type=ptype, author=user,
            lastedit_user=user,
            status=status, tag_val=tag_val)
    post.save()
    tags = parse_tags(post.tag_val)
    post.tags.add(*tags)
    return post


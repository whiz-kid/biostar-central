from .models import User, Post
from . import utils
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def fill_user(f):
    """
    Fills the user parameter on a wrapped function
    """

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
        post = Post.objects.filter(pk=pid).first()
        if not post:
            utils.error(request, "The post cannot be found. Perhaps it has been deleted.")
            return redirect("home")

        if not post.is_toplevel():
            return redirect(post.url())

        return f(request, user, post, *args, **kwargs)

    return decorated_function

def edit_post(f):
    "Edits a post based on an post id"

    @wraps(f)
    def decorated_function(request, pid, *args, **kwargs):
        user = request.user
        post = Post.objects.filter(pk=pid).first()
        if not post:
            utils.error(request, "The post cannot be found. Perhaps it has been deleted.")
            return redirect("home")

        if not post.is_toplevel():
            return redirect(post.url())

        return f(request, user, post, *args, **kwargs)

    return decorated_function
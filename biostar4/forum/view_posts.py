from django.shortcuts import render
from biostar4.forum.models import Post, PostUpload
from biostar4.forum import forms, auth
from biostar4.forum.decorators import *
from biostar4.forum import search
from django.core.urlresolvers import reverse


@fill_user
def search_view(request, user):
    query = request.GET.get('q')
    if not query:
        utils.error(request, "please enter a search query")
        redirect("home")

    result, hits = search.do_search(query)
    context = dict(
        user=user,
        result=result,
        hits=hits,
    )
    return render(request, "search.html", context=context)


@fill_post
def post_details(request, user, post):
    answers = Post.objects.filter(parent=post, type=Post.ANSWER).order_by('-vote_count',
                                                                          '-creation_date')

    print(answers)

    context = dict(
        user=user,
        post=post,
        answers=answers,
    )
    return render(request, "post_details.html", context=context)


@login_required
@fill_user
def post_new(request, user):
    "New toplevel post"

    # The is the default form handler.
    form = forms.TopLevel(user=user, post=None)

    if request.method == 'POST':
        form = forms.TopLevel(user, None, request.POST, request.FILES)
        if form.is_valid():
            post = auth.edit_toplevel_post(user=user, post=None, data=form.cleaned_data)

            # Manage uploaded files.
            remove_ids = request.POST.getlist('remove_ids')
            files = request.FILES.getlist('uploads')
            auth.manage_post_files(user=user, post=post, files=files, remove_ids=remove_ids)

            return redirect("post_details", pid=post.id)

    context = dict(
        user=user,
        form=form,
        form_title='Create a new post',
        action=reverse("post_new")
    )

    return render(request, "post_new.html", context=context)


@login_required
@edit_post
def post_edit(request, user, post):
    "Edit toplevel post"

    initial = dict(
        title=post.title, tag_val=post.tag_val,
        type=post.type, status=post.status,
        text=post.text,
    )
    form = forms.TopLevel(user=user, post=post, initial=initial)

    if request.method == 'POST':
        form = forms.TopLevel(user, post, request.POST, request.FILES)
        if form.is_valid():

            # Update the post data.
            post = auth.edit_toplevel_post(user=user, post=post, data=form.cleaned_data)

            # Manage uploaded files.
            remove_ids = request.POST.getlist('remove_ids')
            files = request.FILES.getlist('uploads')
            auth.manage_post_files(user=user, post=post, files=files, remove_ids=remove_ids)

            return redirect("post_details", pid=post.id)

    context = dict(
        user=user,
        form=form,
        form_title='Edit post',
        action=reverse("post_edit", kwargs=dict(pid=post.id))
    )

    return render(request, "post_new.html", context=context)


@fill_user
def planet_list(request, user):
    context = dict(
        user=user,
    )
    return render(request, "planet_list.html", context=context)

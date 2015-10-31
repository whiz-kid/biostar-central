from django.shortcuts import render

from biostar4.forum import forms, auth
from biostar4.forum.decorators import *
from biostar4.forum import search


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

    answers = Post.objects.filter(parent=post, type=Post.ANSWER).order_by('-vote_count','-creation_date')

    print (answers)

    context = dict(
        user=user,
        post=post,
        answers=answers,
    )
    return render(request, "post_details.html", context=context)


@login_required
@fill_user
def post_new(request, user):
    if request.method == 'POST':
        form = forms.TopLevel(request.POST, request.FILES)
        # Save uploaded file.
        stream = request.FILES.get('upload')
        if form.is_valid():
            post = auth.create_toplevel_post(user=user, data=form.cleaned_data)
            return redirect("post_details", pid=post.id)
    else:
        form = forms.TopLevel()

    context = dict(
        user=user,
        form=form,
        form_title='Create a new post'
    )

    return render(request, "post_new.html", context=context)


@fill_user
def planet_list(request, user):
    context = dict(
        user=user,
    )
    return render(request, "planet_list.html", context=context)

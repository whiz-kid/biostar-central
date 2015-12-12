from django.shortcuts import render, redirect, HttpResponse
from biostar4.forum import forms, utils
from biostar4.forum.models import *
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from biostar4.forum.decorators import *

from channels import Channel

@fill_user
def home(request, user):

    #posts = Post.objects.filter(ptype__in=Post.TOP_LEVEL).exclude("html").order_by('-lastedit_date')[:100]

    posts = Post.objects.top_level(user=user)[:10]

    Channel('test').send(dict(a=100))

    context = dict(
        user=user,
        posts=posts
    )
    return render(request, "post_list.html", context=context)

@fill_user
def messages(request, user):

    users = User.objects.all()[:100]

    context = dict(
        user=user,
        users=users
    )
    return render(request, "post_list.html", context=context)


@fill_user
def echo(request, user):

    context = dict(
        user=user,
    )
    return HttpResponse(status=204)

@login_required
def media(request, user):
    from django.core.files.storage import FileSystemStorage

    try:

        key = request.POST.get('key')
        ctype = request.POST.get('Content-Type')
        stream = request.FILES.get('file')

        fs = FileSystemStorage()
        fs.save(key, stream)

        context = dict(
            user=user,
        )
    except Exception as exc:
        print (exc)
        HttpResponse(status=500)

    return HttpResponse(status=204)

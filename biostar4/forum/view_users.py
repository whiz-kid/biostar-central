import random
from datetime import datetime
from django.shortcuts import render, redirect
from biostar4.forum import forms, utils
from biostar4.forum.models import *
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout

@login_required
def me(request, user):
    return redirect("user_profile", uid=user.uid)


@login_required
def my_site(request, user):
    posts = Post.objects.filter(ptype__in=Post.TOP_LEVEL, author=user).exclude("html").order_by('lastedit_date')[:100]
    context = dict(
        user=user,
        posts=posts
    )
    user.add_message("Creating random message at timestamp %s" % datetime.now())
    user.new_votes += 1
    user.save()
    return render(request, "user_mysite.html", context=context)


@fill_user
def user_profile(request, user, uid):
    target = User.objects.filter(uid=uid).first()
    if not target:
        utils.error(request, "The user cannot be found.")
        return redirect("home")

    context = dict(
        user=user,
        target=target,
    )
    return render(request, "user_profile.html", context=context)


@fill_user
def user_list(request, user):
    users = User.objects.all()[:100].exclude("messages", "text", "html", "files").order_by('-last_login')
    context = dict(
        user=user,
        users=users,
    )
    return render(request, "user_list.html", context=context)


@login_required
def messages(request, user):
    user.new_messages = 0
    user.save()
    context = dict(
        user=user,
    )
    return render(request, "user_messages.html", context=context)


@login_required
def votes(request, user):
    user.new_votes = 0
    user.save()
    context = dict(
        user=user,
    )
    return render(request, "user_votes.html", context=context)


@login_required
def user_edit(request, user):
    if request.method == 'POST':
        fs = FileSystemStorage()
        form = forms.UserEditForm(user, request.POST, request.FILES)

        # Save uploaded file.
        stream = request.FILES.get('upload')

        # Raise errors if user has too many files or the file is too large.
        if stream:
            if len(user.files) > User.MAX_FILE_NUM:
                form.add_error(None, "Uploading too many files.  Max number is %s" % User.MAX_FILE_NUM)


        if form.is_valid():
            # This will be used to remove files if needed.
            old_files = list(user.files)

            # Update the user attributes from the form.
            user = forms.update(user, form)

            # Delete files that the user removed
            for path in old_files:
                path = path.strip()
                if path not in user.files:
                    fs.delete(path)

            # Handle the uploaded files.
            if stream:
                name = stream.name
                now = datetime.now().strftime('%Y-%m-%d')
                rnd = random.randint(10000, 90000)
                key = "upload/{now}/{rnd}-{name}".format(now=now, rnd=rnd, name=name)
                fs.save(key, stream)
                user.files.append(key)

            user.save()
            return redirect("user_profile", uid=user.uid)

    else:
        initial = dict(
            name=user.name,
            email=user.email,
            username=user.username,
            twitter=user.twitter,
            scholar=user.scholar,
            text=user.text,
            location=user.location,
            website=user.website,
            my_tags=','.join(user.my_tags),
            watched_tags=','.join(user.watched_tags),
            files=" \n".join(user.files)
        )
        form = forms.UserEditForm(user, initial=initial)

    context = dict(
        user=user,
        form=form
    )
    return render(request, "user_edit.html", context=context)


def reset(request):
    """
    Password reset
    """
    if request.method == 'POST':
        form = forms.ResetForm(request.POST)
        if form.is_valid():
            utils.info(request, "Reset request sent")
            return redirect("home")
    else:
        form = forms.ResetForm()
    user = User.get(request)
    context = dict(
        user=user,
        form=form,
    )
    return render(request, "account/reset.html", context=context)


@fill_user
def user_logout(request, user):

    if request.method == 'POST':
        form = forms.LogoutForm(request.POST)
        if form.is_valid():
            logout(request)
            utils.info(request, "Logout successful")
            return redirect("home")
    else:
        form = forms.LogoutForm()
    context = dict(
        user=user,
        form=form,
    )
    return render(request, "account/logout.html", context=context)


def user_login(request):

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)

        valid, message = forms.validate_captcha(request)
        if not valid:
            form.add_error(None, message)

        if form.is_valid():
            email =  form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.filter(email=email).first()

            if not user:
                utils.error(request, "Invalid email or password")
                return redirect("login")

            user = authenticate(username=user.username, password=password)

            if not user:
                utils.error(request, "Invalid email or password")
                return redirect("login")

            if not user.is_active:
                utils.error(request, "This user account has been inactivated")
                return redirect("login")

            login(request, user)
            utils.info(request, "Login successful")
            return redirect("home")
    else:
        form = forms.LoginForm()

    context = dict(
        form=form,
        captcha=forms.get_captcha_field()
    )

    return render(request, "account/login.html", context=context)


def signup(request):

    # User.objects.all().delete()

    if request.method == 'POST':
        form = forms.SignupForm(request.POST)

        # Check the captcha field.
        valid, message = forms.validate_captcha(request)
        if not valid:
            form.add_error(None, message)

        if form.is_valid():
            # Create account and log in the user.
            get = form.cleaned_data.get
            email = get('email')
            password = get('password')
            user = create_user(email=email, password=password)
            user = authenticate(username=user.username, password=password)
            login(request, user)
            utils.info(request, "Sign up successful")
            return redirect("home")

    else:
        form = forms.SignupForm()

    context = dict(
        form=form,
        captcha=forms.get_captcha_field()
    )

    return render(request, "account/signup.html", context=context)

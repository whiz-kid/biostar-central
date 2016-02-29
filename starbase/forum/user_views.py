from __future__ import (absolute_import, division, print_function, unicode_literals)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from . import user_forms

from biostar.apps.users.models import User

def user_login(request):
    """
    Handles user login
    """

    if request.method == 'POST':
        form = user_forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.filter(email=email).first()
            user = authenticate(email=user.email, password=password)
            login(request, user)
            return redirect("home")
    else:
        form = user_forms.LoginForm()

    context = dict(
        form=form,
    )

    return render(request, "user_login.html", context=context)

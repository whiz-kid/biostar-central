from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView
from django.views.generic.base import TemplateResponseMixin
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from main.server import models
from django.db.models import Q
from main.server import html
from main.server.const import *
from django.conf import settings
from main import middleware

class PageBase(TemplateView):
    url = "default"

    def get_context_data(self, **kwargs):
        context = super(PageBase, self).get_context_data(**kwargs)
        context['url'] = self.url
        return context

class MessageView(TemplateView):
    url = "/show/messages/"
    template_name = "refactored/message.page.html"

    def get_context_data(self, **kwargs):
        context = super(MessageView, self).get_context_data(**kwargs)

        user = self.request.user

        note_types = [ NOTE_USER, NOTE_PRIVATE ]

        q = Q(target=user, type__in=note_types)
        e = Q(sender=user, type=NOTE_USER)

        notes = models.Note.objects.filter(q).exclude(e)
        notes = notes.select_related('author', 'author__profile').order_by('-date')
        page = html.get_page(request=self.request, obj_list=notes, per_page=25)

        # evaluate the query here so that the unread status is kept
        page.object_list = list(page.object_list)

        # reset the counts
        models.Note.objects.filter(target=user, unread=True).update(unread=False)
        models.UserProfile.objects.filter(user=user).update(new_messages=0)

        sess = middleware.Session(self.request)
        counts = sess.get_counts("message_count")
        sess.save()

        # the params object will carry
        layout  = settings.USER_PILL_BAR

        params  = html.Params(tab="", pill="messages",
                              sort='', since='', layout=layout, title="Your Messages")

        context['page'] = page
        context['params'] = params
        context['counts'] = counts

        return context

class AdView(ListView):
    model = models.Ad
    url = "show/ads/"
    template_name = "refactored/show.ads.html"
    paginate_by = 25
    context_object_name = 'ads'

    def get_context_data(self, **kwargs):
        
        context = super(AdView, self).get_context_data(**kwargs)
        user = self.request.user
        user.is_admin = user.email in settings.ADMIN_EMAILS

        layout  = settings.USER_PILL_BAR
        params  = html.Params(tab="", pill="ads", sort='', since='', layout=layout, title="Ad List")

        context['params'] = params
        context['user'] = self.request.user

        return context

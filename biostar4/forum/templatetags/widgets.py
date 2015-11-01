from django.conf import settings
from django.template import Context, Library
from django.core.urlresolvers import reverse
import hashlib
from urllib.parse import urlencode
from datetime import datetime, timedelta
from django.utils import timezone
from biostar4.forum.models import Message, Profile

def now():
    return timezone.now()

register = Library()


@register.simple_tag
def active(request, text):
    try:
        if request.path == reverse(text):
            return "uk-active"
    except Exception as exc:
        print(exc)
    return ""


@register.simple_tag
def notify(value):
    if value:
        return 'notify'
    return ''


@register.simple_tag
def plusnum(value):
    if value > 10:
        return '10+'
    else:
        return str(value)


@register.simple_tag
def mark_messages(user):
    "Marks all messages as read"
    Message.objects.filter(user=user).update(new=False)
    Profile.objects.filter(user=user).update(new_messages=0)
    return ''

@register.inclusion_tag('widgets/nav_bar.html')
def nav_bar(request, user):
    return dict(user=user, request=request)


@register.inclusion_tag('widgets/message_bar.html')
def message_bar(messages):
    return dict(messages=messages)

@register.inclusion_tag('widgets/notify_bar.html')
def notify_bar(post, user):
    return dict(post=post, user=user)


@register.inclusion_tag('widgets/user_box.html')
def user_box(target, date=None, size=80):
    date = date or target.last_login
    return dict(target=target, date=date, size=size)


@register.inclusion_tag('widgets/tag_line.html')
def tag_line(post):
    return dict(post=post)


@register.inclusion_tag('widgets/form_errors.html')
def form_errors(form):
    return dict(form=form)


@register.filter
def hide_email(value):
    "Hides parts of an email"
    try:
        addr, host = value.split('@')
        email = '*' '@' + host
        return email
    except Exception as exc:
        return value

@register.simple_tag
def gravatar(user, size=80):

    if user.profile.is_suspended():
        # Removes spammy images for suspended users
        email = b'suspended@biostars.org'
    else:
        email = bytes(user.email.encode("utf-8"))

    hashid = hashlib.md5(email).hexdigest()
    gravatar_url = "https://secure.gravatar.com/avatar/%s?" % hashid
    gravatar_url += urlencode(dict(s=str(size), d='identicon'))

    return gravatar_url


def pluralize(value, word):
    if value > 1:
        return "%d %ss" % (value, word)
    else:
        return "%d %s" % (value, word)


@register.filter
def time_ago(date):
    # Rare bug. TODO: Need to investigate why this can happen.
    if not date:
        return ''
    delta = now() - date
    if delta < timedelta(minutes=1):
        return 'just now'
    elif delta < timedelta(hours=1):
        unit = pluralize(delta.seconds // 60, "minute")
    elif delta < timedelta(days=1):
        unit = pluralize(delta.seconds // 3600, "hour")
    elif delta < timedelta(days=30):
        unit = pluralize(delta.days, "day")
    elif delta < timedelta(days=90):
        unit = pluralize(int(delta.days / 7), "week")
    elif delta < timedelta(days=730):
        unit = pluralize(int(delta.days / 30), "month")
    else:
        diff = delta.days / 365.0
        unit = '%0.1f years' % diff
    return "%s ago" % unit

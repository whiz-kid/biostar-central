"""
"""
from django.conf.urls import include, url
from django.contrib import admin

from biostar4.forum import views_main, view_users, view_posts

urlpatterns = [
    url(r'^$', views_main.home, name='home'),

    url(r'^site/my/$', view_users.my_site, name='my_site'),
    url(r'^site/me/$', view_users.me, name='me'),
    url(r'^site/search/$', view_posts.search_view, name='search_view'),

    # User view.
    url(r'^u/(?P<uid>\d+)/$', view_users.user_profile, name="user_profile"),

    # Post related actions
    url(r'^site/post/new/$', view_posts.post_new, name='post_new'),
    url(r'^site/post/edit/(?P<pid>\d+)/$', view_posts.post_edit, name='post_edit'),

    url(r'^p/(?P<pid>\d+)/$', view_posts.post_details, name="post_details"),

    # Planet.
    url(r'^planet/$', view_posts.planet_list, name='planet'),

    # User related actions.
    url(r'^user/list/$', view_users.user_list, name='user_list'),

    # User related actions.
    url(r'^site/user/edit/$', view_users.user_edit, name='user_edit'),

    # Site related tasks
    url(r'^site/messages/$', view_users.messages, name='messages'),
    # Site related tasks
    url(r'^site/votes/$', view_users.votes, name='votes'),

    # Account related urls
    url(r'^accounts/signup/$', view_users.signup, name='signup'),
    url(r'^accounts/login/$', view_users.user_login, name='login'),
    url(r'^accounts/logout/$', view_users.user_logout, name='logout'),
    url(r'^accounts/reset/$', view_users.reset, name='reset'),

    # Debug
    url(r'^media/$', views_main.media, name='media'),
    url(r'^echo/$', views_main.echo, name='echo'),
]


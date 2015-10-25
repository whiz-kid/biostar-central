"""
"""
from django.conf.urls import include, url
from django.contrib import admin

from biostar4.forum import views_main, view_users, view_posts

urlpatterns = [
    url(r'^$', views_main.home, name='home'),

    url(r'^my_site/$', view_users.my_site, name='my_site'),
    url(r'^me/$', view_users.me, name='me'),

    # User view.
    url(r'^u/(?P<uid>\w+)/$', view_users.user_profile, name="user_profile"),
    url(r'^messages/$', views_main.messages, name='messages'),

    # Post related actions
    url(r'^post/new/$', view_posts.post_new, name='post_new'),

    url(r'^p/(?P<pid>\w+)/$', view_posts.post_details, name="post_details"),

    # Planet.
    url(r'^planet/$', view_posts.planet_list, name='planet'),


    # User related actions.
    url(r'^user/list/$', view_users.user_list, name='user_list'),

    # User related actions.
    url(r'^user/edit/$', view_users.user_edit, name='user_edit'),

    # Site related tasks
    url(r'^user/messages/$', view_users.messages, name='messages'),
    # Site related tasks
    url(r'^user/votes/$', view_users.votes, name='votes'),

    # Account related urls
    url(r'^signup/$', view_users.signup, name='signup'),
    url(r'^login/$', view_users.login, name='login'),
    url(r'^logout/$', view_users.logout, name='logout'),
    url(r'^reset/$', view_users.reset, name='reset'),

    # Debug
    url(r'^media/$', views_main.media, name='media'),
    url(r'^echo/$', views_main.echo, name='echo'),
]


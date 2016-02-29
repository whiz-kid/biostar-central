# Apply all previous urls
from biostar.urls import *
from django.conf.urls import include, url

# Create the new urls
from starbase.forum import user_views

urlpatterns += [

    # User authentication
    url(r'^user/login/$', user_views.user_login, name="login"),
    url(r'^user/signup/$', user_views.user_login, name="signup"),
    url(r'^user/password/reset/$', user_views.user_login, name="reset"),
]

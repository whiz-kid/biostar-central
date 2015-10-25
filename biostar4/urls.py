from django.conf import settings
from django.conf.urls import include, url
from biostar4.forum import urls as forum_urls
from django.conf.urls.static import static

urlpatterns = [
    url(r'', include(forum_urls))

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

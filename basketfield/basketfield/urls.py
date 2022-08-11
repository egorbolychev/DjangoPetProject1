from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from basketfield import settings
from men.views import pageNotFound

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('captcha/', include('captcha.urls')),
    path('', include('men.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
handler404 = pageNotFound

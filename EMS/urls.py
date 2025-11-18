from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


URL_PREFIX = "api/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(URL_PREFIX + "user/", include("user.urls")),
    path(URL_PREFIX + "form/", include("form.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

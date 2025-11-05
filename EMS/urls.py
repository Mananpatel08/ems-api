from django.contrib import admin
from django.urls import path, include


URL_PREFIX = "api/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(URL_PREFIX + "user/", include("user.urls")),
    path(URL_PREFIX + "form/", include("form.urls")),
]

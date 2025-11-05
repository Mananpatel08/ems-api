from rest_framework.routers import DefaultRouter
from .views import (
    RootFormViewSet,
    PersonalDetailsViewSet,
    ServiceDetailsViewSet,
)

app_name = "form"
router = DefaultRouter()

router.register(r"", RootFormViewSet, basename="root-form")
router.register(r"personal-details", PersonalDetailsViewSet, basename="personal-details")
router.register(r"service-details", ServiceDetailsViewSet, basename="service-details")

urlpatterns = []
urlpatterns += router.urls
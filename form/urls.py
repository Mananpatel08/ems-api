from rest_framework.routers import DefaultRouter
from .views import (
    RootFormViewSet,
    PersonalDetailsViewSet,
    ServiceDetailsViewSet,
)

app_name = "form"
router = DefaultRouter()

router.register(r"personal-details", PersonalDetailsViewSet, basename="personal-details")
router.register(r"service-details", ServiceDetailsViewSet, basename="service-details")
router.register(r"", RootFormViewSet, basename="root-form")

urlpatterns = []
urlpatterns += router.urls
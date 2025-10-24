from rest_framework.routers import DefaultRouter

from .views import InsurancePolicyViewSet

router = DefaultRouter()
router.register(r"policies", InsurancePolicyViewSet)

urlpatterns = router.urls
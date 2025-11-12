from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RunViewSet, RunLocationViewSet, TerritoryViewSet, RegisterView, UserProfileView

router = DefaultRouter()
router.register('runs', RunViewSet, basename='runs')
router.register('locations', RunLocationViewSet, basename='locations')
router.register('territories', TerritoryViewSet, basename='territories')

schema_view = get_schema_view(
    openapi.Info(
        title="RunQuest API",
        default_version='v1',
        description="Kunlik energiyangizni va yugurishingizni nazorat qiling!",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]

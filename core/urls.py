from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from rest_framework import routers
from token_jwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.views import index, login, config, usuario, dashboard
from api.viewsets import ConfigViewSet, UserViewSet

ROUTER = routers.SimpleRouter()
ROUTER.register(r'config', ConfigViewSet, basename="Config")
ROUTER.register(r'user', UserViewSet, basename="User")

urlpatterns = [
    path('api/', include(ROUTER.urls)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', index),
    path('web/corpo', corpo),
    path('web/login', login, name='login'),   
    path('web/config', config, name='config'),
    path('web/menu', menu, name='menu'),    
    path('web/usuario', usuario, name='usuario'),    
    path('web/dashboard', dashboard, name='dashboard'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
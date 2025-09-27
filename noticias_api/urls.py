"""
URL configuration for noticias_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from noticias.views import MenuItemListAPIView
from usuarios.views.auth_view import LoginViewSet
from noticias.views import CategoriaViewSet, NoticiaViewSet


router = DefaultRouter()
router.register(r"categorias", CategoriaViewSet, basename="categoria")
router.register(r"noticias", NoticiaViewSet, basename="noticia")

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL DE OPEN API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # API DOCS
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API MENU dimanico
    path("api/menu/", MenuItemListAPIView.as_view(), name="menu-list"),

    # ENDPOINT PARA EL JWT DEL auth
    path('api/auth/login/', LoginViewSet.as_view(), name='login'),
    path('api/auth/refreh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token-refresh'),

    path("api/", include(router.urls)),
]

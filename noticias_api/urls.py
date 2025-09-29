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
from django.conf import settings
from noticias.views import MenuItemListAPIView
from noticias.views import CategoriaViewSet, NoticiaViewSet
from django.conf.urls.static import static

from usuarios.views import FacebookRegisterAPIView
from usuarios.views.admin_views import UsuariosAdminListAPIView, UsuarioToggleEstadoAPIView
from usuarios.views.auth_view import EmailLoginView, RegistroAPIView, ActivarCuentaAPIView, PasswordCheckAPIView

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
    path('api/auth/login/', EmailLoginView.as_view(), name='login'),
    path('api/auth/refreh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token-refresh'),
    path("api/auth/register/", RegistroAPIView.as_view(), name="register"),
    path("api/auth/activate/<uidb64>/<token>/", ActivarCuentaAPIView.as_view(), name="activate-account"),
    path("api/auth/password-check/", PasswordCheckAPIView.as_view(), name="password-check"),

    # USUARIOS
    path("api/admin/usuarios/", UsuariosAdminListAPIView.as_view(), name="admin-usuarios-list"),
    path("api/admin/usuarios/<int:pk>/estado/", UsuarioToggleEstadoAPIView.as_view(),
         name="admin-usuario-estado"),
    path("api/auth/facebook/register/", FacebookRegisterAPIView.as_view(), name="facebook-register"),

    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
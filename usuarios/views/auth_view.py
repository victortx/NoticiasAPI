from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets, throttling
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status

from usuarios.managers import enviar_email_activacion, enviar_email_reset_password
from usuarios.models import Usuario
from usuarios.serializers import RegistroUsuarioSerializer, validar_password_fuerte
from usuarios.utils import password_ya_usada, push_password_history

User = get_user_model()

class EmailLoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        self.fields.pop('username', None)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Debes enviar 'email' y 'password'.")

        # Busca por email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Email o contraseña inválidos.", code="no_active_account")
        except User.MultipleObjectsReturned:
            # En caso extremo de duplicados, toma el primero activo.
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if not user:
                raise exceptions.AuthenticationFailed("Email o contraseña inválidos.", code="no_active_account")

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Email o contraseña inválidos.", code="no_active_account")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("La cuenta está inactiva.", code="no_active_account")

        # Genera tokens
        refresh = self.get_token(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": getattr(user, "role", None),
            "name": (f"{user.first_name} {user.last_name}".strip() or user.username),
            "username": user.username,
            "user_id": user.id,
            "email": user.email,
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims extra dentro del JWT
        token["role"] = getattr(user, "role", None)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        token["name"] = full_name
        return token


class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailLoginSerializer


class RegistroAPIView(generics.CreateAPIView):
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        enviar_email_activacion(user, self.request)

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        # No devolvemos datos sensibles; solo mensaje
        return Response(
            {
                "detail": "Cuenta creada. Revisa tu correo para activar la cuenta.",
                "email": request.data.get("email")
            },
            status=status.HTTP_201_CREATED
        )

class ActivarCuentaAPIView(APIView):
    """
    GET /api/auth/activate/<uidb64>/<token>/
    Activa la cuenta si el token es válido.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Enlace inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({"detail": "Cuenta activada correctamente."})
        return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)

class PasswordCheckAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        pwd = request.data.get("password", "")
        errores = validar_password_fuerte(pwd)
        return Response({
            "valid": len(errores) == 0,
            "errors": errores
        })


class PasswordResetAnonThrottle(throttling.AnonRateThrottle):
    rate = "5/min"  # limita spam de solicitudes anónimas

class PasswordForgotAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetAnonThrottle]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if email:
            user = Usuario.objects.filter(email__iexact=email).first()
            if user:
                try:
                    enviar_email_reset_password(user)
                except Exception:
                    # No filtramos errores al cliente; mantenemos 200
                    pass
        return Response({"detail": "Si el correo existe, recibirás instrucciones para reiniciar tu contraseña."})


class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetAnonThrottle]

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password") or ""

        # Validación de presencia
        if not uidb64 or not token or not new_password:
            return Response({"detail": "Faltan parámetros."}, status=status.HTTP_400_BAD_REQUEST)

        # Valida fuerza de password
        errores = validar_password_fuerte(new_password)
        if errores:
            return Response({"valid": False, "errors": errores}, status=status.HTTP_400_BAD_REQUEST)

        # Decodifica el usuario
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Enlace inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Valida token de reset
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)

        # Cambia la contraseña
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Contraseña actualizada correctamente."})


class PasswordChangeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password") or ""
        new_password = request.data.get("new_password") or ""

        if not current_password or not new_password:
            return Response({"detail": "Faltan parámetros."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(current_password):
            return Response({"detail": "La contraseña actual no es correcta."}, status=status.HTTP_400_BAD_REQUEST)

        errores = validar_password_fuerte(new_password)
        if errores:
            return Response({"valid": False, "errors": errores}, status=status.HTTP_400_BAD_REQUEST)

        if password_ya_usada(user, new_password):
            return Response({"detail": "No puedes reutilizar una contraseña anterior."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        push_password_history(user)

        return Response({"detail": "Contraseña cambiada correctamente."}, status=200)
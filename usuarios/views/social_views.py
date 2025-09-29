import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.serializers import validar_password_fuerte, generar_username_desde_email
from usuarios.managers import enviar_email_activacion
from usuarios.utils import generar_password_fuerte

Usuario = get_user_model()

class FacebookRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Asegúrate de que el front te manda el token en LA MISMA CLAVE que lees aquí
        access_token = request.data.get("access_token") or request.data.get("fb_access_token")
        telefono = request.data.get("telefono", "")

        if not access_token:
            return Response({"detail": "access_token requerido"}, status=400)

        app_id = settings.FACEBOOK_APP_ID
        app_secret = settings.FACEBOOK_APP_SECRET
        if not app_id or not app_secret:
            return Response({"detail": "FACEBOOK_APP_ID/SECRET no configurados."}, status=500)

        # 1) Obtén un APP ACCESS TOKEN (más fiable que APP_ID|APP_SECRET)
        try:
            tok = requests.get(
                "https://graph.facebook.com/oauth/access_token",
                params={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "client_credentials",
                },
                timeout=10,
            )
            tok.raise_for_status()
            app_access_token = tok.json().get("access_token")
            if not app_access_token:
                return Response({"detail": "No se pudo obtener app_access_token de Facebook."}, status=502)
        except Exception as e:
            return Response(
                {"detail": "Error al obtener app_access_token de Facebook.", "error": str(e) if settings.DEBUG else "..."},
                status=502,
            )

        # 2) Inspecciona el token del usuario
        try:
            r = requests.get(
                "https://graph.facebook.com/v19.0/debug_token",
                params={"input_token": access_token, "access_token": app_access_token},
                timeout=10,
            )
            data = r.json()
            if not r.ok:
                return Response(
                    {"detail": "Facebook respondió error al validar token.", "fb": data if settings.DEBUG else "..."},
                    status=400,
                )
            d = data.get("data", {})
            if not d.get("is_valid"):
                return Response({"detail": "Token de Facebook inválido.", "fb": d if settings.DEBUG else "..."}, status=400)
            if str(d.get("app_id")) != str(app_id):
                return Response({"detail": "El token no pertenece a tu app de Facebook."}, status=400)
        except Exception as e:
            return Response(
                {"detail": "No se pudo verificar el token con Facebook.", "error": str(e) if settings.DEBUG else "..."},
                status=502,
            )

        # 3) Obtén perfil (requiere permiso 'email' en el login de FB)
        try:
            me = requests.get(
                "https://graph.facebook.com/v19.0/me",
                params={"fields": "id,email,first_name,last_name", "access_token": access_token},
                timeout=10,
            )
            me_data = me.json()
            if not me.ok:
                return Response({"detail": "Error al obtener perfil de Facebook.", "fb": me_data if settings.DEBUG else "..."}, status=400)
        except Exception as e:
            return Response({"detail": "No se pudo obtener el perfil de Facebook.", "error": str(e) if settings.DEBUG else "..."}, status=502)

        email = (me_data.get("email") or "").lower()
        if not email:
            return Response({"detail": "Facebook no retornó email. Solicita el scope 'email'."}, status=400)

        first_name = me_data.get("first_name") or ""
        last_name = me_data.get("last_name") or ""

        # 4) Alta/lookup usuario
        user = Usuario.objects.filter(email__iexact=email).first()
        created = False
        temp_password = None

        if not user:
            username = generar_username_desde_email(email)
            temp_password = generar_password_fuerte(12)
            if validar_password_fuerte(temp_password):
                return Response({"detail": "No se pudo generar una contraseña válida."}, status=500)

            user = Usuario(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False,  # activación por email
            )
            if hasattr(user, "phone_number"):
                user.phone_number = telefono
            user.set_password(temp_password)
            user.save()
            created = True
        else:
            # opcional: actualiza nombre/telefono
            changed = False
            if first_name and user.first_name != first_name:
                user.first_name = first_name; changed = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name; changed = True
            if hasattr(user, "phone_number") and telefono and user.phone_number != telefono:
                user.phone_number = telefono; changed = True
            if changed:
                user.save()

        # 5) Email de activación (con contraseña temporal si es nuevo)
        try:
            enviar_email_activacion(user, request, temp_password=temp_password)
        except Exception as e:
            # No tumbamos el flujo si falla el correo
            return Response(
                {"detail": "Usuario creado pero falló el envío de correo.", "email": email},
                status=201 if created else 200,
            )

        return Response(
            {
                "detail": "Cuenta creada. Revisa tu correo para activar la cuenta." if created else
                          "Usuario existente. Se envió enlace de activación.",
                "email": email,
                "created": created,
            },
            status=201 if created else 200,
        )

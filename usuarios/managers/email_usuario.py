from __future__ import annotations

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def enviar_email_activacion(user, request, temp_password: str | None = None):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("activate-account", kwargs={"uidb64": uidb64, "token": token})
    url = request.build_absolute_uri(path)

    subject = "Activa tu cuenta"
    text_extra = f"\n\nTu contraseña temporal: {temp_password}\n(Cámbiala después de activar)." if temp_password else ""
    text = (
        f"Hola {user.first_name or user.username},\n\n"
        f"Confirma tu cuenta con este enlace:\n{url}{text_extra}\n\n"
        "Si no creaste esta cuenta, ignora este correo."
    )
    html_pw = f"""
      <p style="margin-top:12px;">
        <strong>Contraseña temporal:</strong>
        <code style="padding:2px 6px;border:1px solid #ddd;border-radius:4px;display:inline-block;">{temp_password}</code><br>
        <small>Cámbiala después de activar.</small>
      </p>
    """ if temp_password else ""

    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;">
      <h2>¡Bienvenido(a)!</h2>
      <p>Hola <strong>{(user.first_name or user.username)}</strong>,</p>
      <p>Para activar tu cuenta, haz clic en el siguiente botón:</p>
      <p>
        <a href="{url}" style="background:#2563eb;color:#fff;padding:10px 16px;text-decoration:none;border-radius:6px;display:inline-block;">
          Activar cuenta
        </a>
      </p>
      {html_pw}
      <p>O copia y pega este enlace en tu navegador:<br><a href="{url}">{url}</a></p>
      <hr>
      <small>Si no solicitaste esta cuenta, ignora este mensaje.</small>
    </div>
    """

    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=getattr(settings, "EMAIL_USE_TLS", False),
        use_ssl=getattr(settings, "EMAIL_USE_SSL", False),
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        connection=connection,
    )
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)

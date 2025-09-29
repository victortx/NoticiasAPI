from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from usuarios.managers import UsuarioManager


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    direccion = models.CharField('Direccion', max_length=255, blank=True)

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        AUTOR = "autor", "Autor"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.AUTOR)

    objects = UsuarioManager()

    def save(self, *args, **kwargs):
        # SI ES ADMIN SE LE DA EL ACCESO AL ADMIN DE DJANGO
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class PasswordHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_history")
    encoded = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
from django.contrib.auth.models import AbstractUser
from django.db import models
from usuarios.managers import UsuarioManager


class Usuario(AbstractUser):
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
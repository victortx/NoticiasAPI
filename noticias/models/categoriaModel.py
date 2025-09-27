from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class Categoria(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    estado = models.CharField("Estado", max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
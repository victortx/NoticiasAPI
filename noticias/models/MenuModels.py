from django.db import models
from django.utils import timezone

class MenuItem(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    nombre = models.CharField("Nombre de la sección", max_length=80, unique=True)
    estado = models.CharField("Estado", max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
    ruta = models.CharField("Ruta", max_length=200, unique=True)
    icono = models.CharField("Icono", max_length=200, null=True, blank=True)
    fecha_creacion = models.DateTimeField("Fecha de creación", default=timezone.now, editable=False)

    class Meta:
        ordering = ["id"]
        verbose_name = "Ítem de menú"
        verbose_name_plural = "Ítems de menú"

    def __str__(self):
        return f"{self.nombre} ({self.estado})"

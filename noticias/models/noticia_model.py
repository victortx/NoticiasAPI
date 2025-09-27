from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

from noticias.models import Categoria


class Noticia(models.Model):
    # Básicos
    miniatura = models.ImageField(upload_to="noticias/miniaturas/", blank=True, null=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.CharField("Descripción de la noticia", max_length=400, blank=True)
    cuerpo = models.TextField()

    # Autor y categoría
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="noticias"
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="noticias"
    )

    # Fechas
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Extras
    hoja_estilo = models.TextField(blank=True)  # CSS opcional
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        ordering = ["-fecha_publicacion", "-fecha_creacion"]
        indexes = [
            models.Index(fields=["fecha_publicacion"]),
            models.Index(fields=["titulo"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        # Si no tiene fecha_publicacion y ya hay cuerpo/titulo, puedes auto-publicar:
        # if self.fecha_publicacion is None:
        #     self.fecha_publicacion = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
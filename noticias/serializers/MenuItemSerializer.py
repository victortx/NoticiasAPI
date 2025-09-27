from rest_framework import serializers
from noticias.models import MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "nombre", "icono", "estado", "ruta", "fecha_creacion"]

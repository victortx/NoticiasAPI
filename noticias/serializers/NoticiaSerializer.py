from rest_framework import serializers
from noticias.models import Categoria, Noticia

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug"]


class NoticiaSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.SerializerMethodField()
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source="categoria", queryset=Categoria.objects.all(), write_only=True
    )

    class Meta:
        model = Noticia
        fields = [
            "id", "slug",
            "miniatura",
            "titulo", "descripcion", "cuerpo",
            "autor", "autor_nombre",
            "categoria", "categoria_id",
            "fecha_publicacion", "fecha_creacion",
            "hoja_estilo",
        ]
        read_only_fields = ["slug", "fecha_creacion", "autor"]

    def get_autor_nombre(self, obj):
        if obj.autor:
            name = f"{obj.autor.first_name} {obj.autor.last_name}".strip()
            return name or obj.autor.username
        return None

    def create(self, validated_data):
        # Asignar autor automáticamente al usuario autenticado
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["autor"] = request.user
        return super().create(validated_data)

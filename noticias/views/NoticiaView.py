from rest_framework import viewsets, permissions, decorators, response
from django.db.models import Q
from noticias.models import Categoria, Noticia
from noticias.serializers import CategoriaSerializer, NoticiaSerializer
from noticias.permission import IsAuthorOrAdminCanWrite

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ["nombre", "slug"]


class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.select_related("autor", "categoria")
    serializer_class = NoticiaSerializer
    permission_classes = [IsAuthorOrAdminCanWrite]

    filterset_fields = ["categoria", "autor"]
    search_fields = ["titulo", "descripcion", "cuerpo", "slug"]
    ordering_fields = ["fecha_publicacion", "fecha_creacion", "titulo"]

    @decorators.action(detail=True, methods=["get"], url_path="recomendados")
    def recomendados(self, request, pk=None):

        base = Noticia.objects.select_related("autor", "categoria")
        actual = self.get_object()
        by = (request.query_params.get("by") or "categoria").lower()
        limit = int(request.query_params.get("limit", 5))

        qs = base.exclude(pk=actual.pk)

        if by == "autor" and actual.autor_id:
            qs = qs.filter(autor_id=actual.autor_id)
        elif by == "titulo":
            # Coincidencia simple por palabras del título (>3 chars)
            palabras = [w for w in actual.titulo.split() if len(w) > 3]
            q = Q()
            for w in palabras[:3]:
                q |= Q(titulo__icontains=w)
            qs = qs.filter(q)
            if not palabras:
                qs = qs.filter(categoria_id=actual.categoria_id)
        else:  # por categoría (default)
            qs = qs.filter(categoria_id=actual.categoria_id)

        qs = qs.order_by("-fecha_publicacion", "-fecha_creacion")[:limit]
        ser = self.get_serializer(qs, many=True)
        return response.Response(ser.data)

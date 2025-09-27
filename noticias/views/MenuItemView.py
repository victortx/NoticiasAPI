from rest_framework import generics, permissions
from noticias.models import MenuItem
from noticias.serializers import MenuItemSerializer

class MenuItemListAPIView(generics.ListAPIView):
    queryset = MenuItem.objects.filter(estado="activo").order_by("id")
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]

    filterset_fields = ["estado"]
    search_fields = ["nombre", "ruta"]
    ordering_fields = ["id", "nombre", "fecha_creacion"]

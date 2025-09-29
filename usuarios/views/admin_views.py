from rest_framework import generics, permissions, status
from rest_framework.response import Response

from usuarios.models import Usuario
from usuarios.serializers import UsuarioListSerializer, UsuarioEstadoSerializer
from usuarios.permissions import IsAdminRole

class UsuariosAdminListAPIView(generics.ListAPIView):
    queryset = Usuario.objects.all().order_by("id")
    serializer_class = UsuarioListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username"]


class UsuarioToggleEstadoAPIView(generics.UpdateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioEstadoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    http_method_names = ["patch", "put"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Evitar que el admin se desactive a sí mismo
        if instance.pk == request.user.pk and request.data.get("is_active") in [False, "false", "False", 0, "0"]:
            return Response(
                {"detail": "No puedes desactivar tu propia cuenta."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)
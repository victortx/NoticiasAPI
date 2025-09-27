from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorOrAdminCanWrite(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", None) in ("admin", "author"))

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if getattr(u, "role", None) == "admin" or u.is_superuser:
            return True
        return getattr(obj, "autor_id", None) == getattr(u, "id", None)

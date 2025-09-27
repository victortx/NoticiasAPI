from rest_framework import viewsets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = getattr(user, "role", None)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        token["name"] = full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["role"] = getattr(user, "role", None)
        data["name"] = (f"{user.first_name} {user.last_name}".strip() or user.username)
        data["username"] = user.username
        data["user_id"] = user.id
        return data

class LoginViewSet(TokenObtainPairView):
    serializer_class = LoginSerializer
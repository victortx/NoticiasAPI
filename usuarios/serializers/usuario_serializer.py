from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.text import slugify
import re
from usuarios.models import Usuario

Usuario = get_user_model()

class UsuarioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "telefono", "direccion", "role", "is_active"
        ]

class UsuarioEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "is_active"]
        read_only_fields = ["id"]


def validar_password_fuerte(pwd: str):
    errores = []
    if not (8 <= len(pwd) <= 16):
        errores.append("La contraseña debe tener entre 8 y 16 caracteres.")
    if not re.search(r"[a-z]", pwd):
        errores.append("Debe incluir al menos una letra minúscula.")
    if not re.search(r"[A-Z]", pwd):
        errores.append("Debe incluir al menos una letra mayúscula.")
    if not re.search(r"[0-9]", pwd):
        errores.append("Debe incluir al menos un dígito.")
    if not re.search(r"[^\w\s]", pwd):  # cualquier no alfanumérico
        errores.append("Debe incluir al menos un caracter especial.")
    return errores

def generar_username_desde_email(email: str) -> str:
    base = slugify(email.split("@")[0]) or "user"
    candidato = base
    n = 1
    while Usuario.objects.filter(username=candidato).exists():
        n += 1
        candidato = f"{base}-{n}"
    return candidato

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["email", "first_name", "last_name", "telefono", "password"]

    def validate_email(self, value):
        value = (value or "").strip().lower()
        if not value:
            raise serializers.ValidationError("El email es obligatorio.")
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_password(self, value):
        errores = validar_password_fuerte(value)
        if errores:
            raise serializers.ValidationError(errores)
        return value

    def create(self, validated_data):
        telefono = validated_data.pop("telefono", "")
        password = validated_data.pop("password")
        email = validated_data["email"].lower()

        username = generar_username_desde_email(email)

        user = Usuario(
            username=username,
            email=email,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_active=False,
            role=getattr(Usuario, "Role", None).AUTOR if hasattr(Usuario, "Role") else "Autor",
        )

        if hasattr(user, "phone_number"):
            user.phone_number = telefono

        user.set_password(password)
        user.save()
        return user
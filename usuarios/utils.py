import random, string
from django.contrib.auth.hashers import check_password
import re
from usuarios.models import PasswordHistory

def generar_password_fuerte(length=12):
    length = max(8, min(16, int(length)))
    lowers = string.ascii_lowercase
    uppers = string.ascii_uppercase
    digits = string.digits
    specials = "!@#$%^&*()-_=+[]{};:,.?/|"
    allchars = lowers + uppers + digits + specials

    pwd = [
        random.choice(lowers),
        random.choice(uppers),
        random.choice(digits),
        random.choice(specials),
    ]
    pwd += [random.choice(allchars) for _ in range(length - 4)]
    random.shuffle(pwd)
    return "".join(pwd)



PASSWORD_HISTORY_LIMIT = 5  # últimas N contraseñas prohibidas

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
    if not re.search(r"[^\w\s]", pwd):
        errores.append("Debe incluir al menos un caracter especial.")
    return errores

def password_ya_usada(user, raw_password, limit: int = PASSWORD_HISTORY_LIMIT) -> bool:
    # Compara contra la contraseña actual
    if user.password and check_password(raw_password, user.password):
        return True
    # Compara contra el historial (últimas N)
    for ph in PasswordHistory.objects.filter(user=user).order_by("-created_at")[:limit]:
        if check_password(raw_password, ph.encoded):
            return True
    return False

def push_password_history(user, limit: int = PASSWORD_HISTORY_LIMIT):
    # Guarda el hash actual en el historial y recorta a 'limit'
    if not user.password:
        return
    PasswordHistory.objects.create(user=user, encoded=user.password)
    ids = list(
        PasswordHistory.objects.filter(user=user)
        .order_by("-created_at")
        .values_list("id", flat=True)
    )
    if len(ids) > limit:
        PasswordHistory.objects.filter(user=user, id__in=ids[limit:]).delete()

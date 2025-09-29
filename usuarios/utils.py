import random, string

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

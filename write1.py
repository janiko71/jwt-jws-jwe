import jwt
import time

# JWT standard claims :
# iss = émetteur du token
# sub = sujet / utilisateur identitaire
# aud = audience / destinataire visé
# exp = date d'expiration
# nbf = date avant laquelle le token n'est pas valide
# iat = date d'émission du token
# role = rôle de l'utilisateur (claim personnalisé)
# email = adresse email
# name = nom complet

token_file = "token.txt"
secret = "ceci-est-mon-secret-mais-je-ne-le-dis-pas"
now = int(time.time())
five_minutes_later = now + 60

payload = {
    "iss": "https://geba.fr",
    "sub": "jeannot-lapin",
    "aud": "jwt-demo-app",
    "exp": five_minutes_later,
    "nbf": now,
    "iat": now,
    "role": "Super Admin",
    "email": "jeannot@geba.fr",
    "name": "Jeannot Lapin"
}

token = jwt.encode(payload, secret, algorithm="HS256")

with open(token_file, "w", encoding="utf-8") as f:
    f.write(token)

print('-'*72)
print(token)
print('-'*72)
audience_attendue = "jwt-demo-app"

try:
    decoded = jwt.decode(
        token,
        secret,
        audience=audience_attendue,
        algorithms=["HS256"]
    )
    print(decoded)
    print('-'*72)
except jwt.exceptions.PyJWTError as e:
    print(f"Erreur JWT : {type(e).__name__} - {e}")
    print('-'*72)


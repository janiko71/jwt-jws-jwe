import base64
import json

import jwt


token_file = "token.txt"
secret = "ceci-est-mon-secret-mais-je-ne-le-dis-pas"
audience_attendue = "jwt-demo-app"
issuer_attendu = "https://geba.fr"
utilisateur_attendu = "jeannot-lapin"

try:
    with open(token_file, "r", encoding="utf-8") as f:
        token = f.read().strip()

    parties = token.split(".")
    if len(parties) != 3:
        raise jwt.exceptions.InvalidTokenError("Le token n'est pas un JWT valide")

    payload_b64 = parties[1]
    padding_needed = (-len(payload_b64)) % 4
    payload_b64 = payload_b64 + "=" * padding_needed

    payload_json = base64.urlsafe_b64decode(payload_b64)
    payload = json.loads(payload_json.decode())

    decoded = jwt.decode(
        token,
        secret,
        issuer=issuer_attendu,
        audience=audience_attendue,
        algorithms=["HS256"],
        options={"require": ["exp", "iat", "nbf", "iss", "aud", "sub"]}
    )

    if decoded.get("sub") != utilisateur_attendu:
        raise PermissionError("Le sujet du token ne correspond pas à l'utilisateur attendu")

    if decoded.get("role") != "Super Admin":
        raise PermissionError("Le rôle du token ne permet pas cette action")

    print("-" * 72)
    print("Decoded : " + str(decoded))
    print("-" * 72)
    print("Payload : " + str(payload))
    print("-" * 72)

except jwt.exceptions.PyJWTError as e:
    print(f"Erreur JWT : {type(e).__name__} - {e}")
    print("-" * 72)
except (PermissionError, ValueError) as e:
    print(f"Erreur métier : {e}")
    print("-" * 72)
except FileNotFoundError:
    print(f"Fichier introuvable : {token_file}")
    print("-" * 72)

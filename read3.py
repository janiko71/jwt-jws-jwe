import json
import time
from pathlib import Path

from jwcrypto import jwk, jwe


token_file = "token_chiffre.txt"
private_key_file = "private.pem"
audience_attendue = "jwt-demo-app"
issuer_attendu = "https://geba.fr"
utilisateur_attendu = "jeannot-lapin"

try:
    token = Path(token_file).read_text(encoding="utf-8").strip()
    private_key = jwk.JWK.from_pem(
        Path(private_key_file).read_bytes()
    )

    encrypted_token = jwe.JWE()
    encrypted_token.deserialize(token, key=private_key)

    header = encrypted_token.jose_header
    if header.get("alg") != "RSA-OAEP-256":
        raise ValueError("Algorithme JWE inattendu")
    if header.get("enc") != "A256GCM":
        raise ValueError("Chiffrement JWE inattendu")

    payload = json.loads(encrypted_token.payload.decode("utf-8"))
    now = int(time.time())

    required_claims = ["exp", "iat", "nbf", "iss", "aud", "sub"]
    missing_claims = [claim for claim in required_claims if claim not in payload]
    if missing_claims:
        raise ValueError(
            "Claims obligatoires manquants : " + ", ".join(missing_claims)
        )

    if payload["iss"] != issuer_attendu:
        raise PermissionError("L'émetteur du token ne correspond pas à celui attendu")
    if payload["aud"] != audience_attendue:
        raise PermissionError("L'audience du token ne correspond pas à celle attendue")
    if payload["sub"] != utilisateur_attendu:
        raise PermissionError("Le sujet du token ne correspond pas à l'utilisateur attendu")
    if payload.get("role") != "Super Admin":
        raise PermissionError("Le rôle du token ne permet pas cette action")
    if payload["nbf"] > now:
        raise ValueError("Le token n'est pas encore valide")
    if payload["exp"] <= now:
        raise ValueError("Le token a expiré")

    print("-" * 72)
    print("Decoded : " + str(payload))
    print("-" * 72)

except (jwe.InvalidJWEData, ValueError, json.JSONDecodeError) as e:
    print(f"Erreur JWE : {type(e).__name__} - {e}")
    print("-" * 72)
except PermissionError as e:
    print(f"Erreur métier : {e}")
    print("-" * 72)
except FileNotFoundError:
    print(f"Fichier introuvable : {token_file} ou {private_key_file}")
    print("-" * 72)

import json
import time
from pathlib import Path

from jwcrypto import jwk, jwe


token_file = "token_chiffre.txt"
public_key_file = "public.pem"

now = int(time.time())
expiration = now + 300

payload = {
    "iss": "https://geba.fr",
    "sub": "jeannot-lapin",
    "aud": "jwt-demo-app",
    "exp": expiration,
    "nbf": now,
    "iat": now,
    "role": "Super Admin",
    "email": "jeannot@geba.fr",
    "name": "Jeannot Lapin"
}

public_key = jwk.JWK.from_pem(
    Path(public_key_file).read_bytes()
)

encrypted_token = jwe.JWE(
    plaintext=json.dumps(payload).encode("utf-8"),
    protected={
        "alg": "RSA-OAEP-256",
        "enc": "A256GCM"
    }
)
encrypted_token.add_recipient(public_key)
token = encrypted_token.serialize(compact=True)

Path(token_file).write_text(token, encoding="utf-8")

print("-" * 72)
print(token)
print("-" * 72)
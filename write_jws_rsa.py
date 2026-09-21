import time
from pathlib import Path

import jwt


token_file = "token.txt"
private_key_file = "private.pem"

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

private_key = Path(private_key_file).read_text(encoding="utf-8")
token = jwt.encode(payload, private_key, algorithm="RS256")
Path(token_file).write_text(token, encoding="utf-8")

print("-" * 72)
print(token)
print("-" * 72)

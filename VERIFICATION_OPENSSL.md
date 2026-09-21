# Vérification avec OpenSSL et Bash

> Contrôler les signatures JWS et déchiffrer un JWE depuis la ligne de commande.

[Accueil du projet](README.md) · [Ce guide](VERIFICATION_OPENSSL.md)

---

Les commandes suivantes permettent de contrôler les tokens sans utiliser directement
`jwt.decode()`. Elles vérifient la signature cryptographique. Les contrôles métier
(`iss`, `aud`, `sub`, `role`, etc.) doivent toujours être faits séparément.

## Avant de commencer

Depuis la racine du projet, installe les dépendances et génère la bi-clé RSA si
nécessaire :

```bash
pip install -r requirements.txt
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl pkey -in private.pem -pubout -out public.pem
```

| Vérification | Token | Clé ou secret | Résultat attendu |
| --- | --- | --- | --- |
| HMAC | `token.txt` | Secret partagé | `Signature HS256 valide` |
| RSA | `token.txt` | `public.pem` | `Verified OK` |
| JWE | `token_chiffre.txt` | `private.pem` | Payload déchiffré |

## Sommaire

- [Préparer les fonctions Bash](#préparer-quelques-fonctions-bash)
- [Vérifier un JWS HS256](#vérifier-un-jws-hs256-avec-un-secret-partagé)
- [Vérifier un JWS RS256](#vérifier-un-jws-rs256-avec-la-bi-clé-rsa)
- [Vérifier un JWE](#vérifier-un-jwe-avec-privatepem)

## Préparer quelques fonctions Bash

Depuis la racine du projet :

```bash
# Convertit une partie Base64URL JWT en Base64 classique puis la décode.
b64url_decode() {
    local value="$1"
    value=${value//-/+}
    value=${value//_//}
    case $((${#value} % 4)) in
        2) value+="==" ;;
        3) value+="=" ;;
    esac
    printf '%s' "$value" | openssl base64 -d -A
}

# Encode des octets en Base64URL sans retour à la ligne ni padding.
b64url_encode() {
    openssl base64 -A | tr '+/' '-_' | tr -d '='
}
```

## Vérifier un JWS HS256 avec un secret partagé

`write_jws_secret.py` produit un JWS HS256 dans `token.txt`. La signature est le
HMAC-SHA-256 de `header.payload` :

```bash
TOKEN=$(tr -d '\r\n' < token.txt)
HEADER=${TOKEN%%.*}
REST=${TOKEN#*.}
PAYLOAD=${REST%%.*}
SIGNATURE=${REST##*.}

printf '%s' "$HEADER.$PAYLOAD" > signing_input.bin
EXPECTED_SIGNATURE=$(
    openssl dgst -sha256 -mac HMAC \
        -macopt 'key:ceci-est-mon-secret-mais-je-ne-le-dis-pas' \
        -binary signing_input.bin | b64url_encode
)

if [ "$EXPECTED_SIGNATURE" = "$SIGNATURE" ]; then
    echo "Signature HS256 valide"
else
    echo "Signature HS256 invalide" >&2
    exit 1
fi

echo "Header :"
b64url_decode "$HEADER"
echo
echo "Payload :"
b64url_decode "$PAYLOAD"
echo
```

Le secret apparaît ici uniquement parce qu'il est volontairement pédagogique dans
`write_jws_secret.py`. En production, ne le mettez pas dans l'historique du shell.

## Vérifier un JWS RS256 avec la bi-clé RSA

`write_jws_rsa.py` signe `token.txt` avec `private.pem`. La vérification se fait
avec la clé publique et `openssl dgst` :

```bash
TOKEN=$(tr -d '\r\n' < token.txt)
HEADER=${TOKEN%%.*}
REST=${TOKEN#*.}
PAYLOAD=${REST%%.*}
SIGNATURE=${REST##*.}

printf '%s' "$HEADER.$PAYLOAD" > signing_input.bin
b64url_decode "$SIGNATURE" > signature.bin

openssl dgst -sha256 \
    -verify public.pem \
    -signature signature.bin \
    signing_input.bin
```

La sortie `Verified OK` signifie que `public.pem` correspond à la clé privée qui a
signé le token et que `header.payload` n'a pas été modifié. Une sortie `Verification
Failure` indique une signature incorrecte, un token altéré ou une mauvaise clé.

Pour inspecter les parties du JWT sans les considérer comme fiables :

```bash
echo "Header :"
b64url_decode "$HEADER"
echo
echo "Payload :"
b64url_decode "$PAYLOAD"
echo
```

## Vérifier un JWE avec `private.pem`

`write_jwe.py` produit `token_chiffre.txt`, composé de cinq parties :

```text
protected.encrypted_key.iv.ciphertext.tag
```

La clé privée RSA déchiffre d'abord la clé de contenu (CEK). Avec
`RSA-OAEP-256`, les paramètres OAEP et MGF1 utilisent SHA-256 :

```bash
TOKEN=$(tr -d '\r\n' < token_chiffre.txt)
IFS='.' read -r PROTECTED ENCRYPTED_KEY IV CIPHERTEXT TAG <<< "$TOKEN"

echo "En-tête JWE :"
b64url_decode "$PROTECTED"
echo

b64url_decode "$ENCRYPTED_KEY" > encrypted_key.bin
b64url_decode "$IV" > iv.bin
b64url_decode "$CIPHERTEXT" > ciphertext.bin
b64url_decode "$TAG" > tag.bin

openssl pkeyutl -decrypt \
    -inkey private.pem \
    -in encrypted_key.bin \
    -out cek.bin \
    -pkeyopt rsa_padding_mode:oaep \
    -pkeyopt rsa_oaep_md:sha256 \
    -pkeyopt rsa_mgf1_md:sha256
```

`openssl enc` ne permet pas de vérifier correctement le tag d'authentification
`A256GCM`. Il faut donc utiliser `AESGCM` pour l'étape finale. La bibliothèque
`cryptography` est déjà installée par `requirements.txt` :

```bash
python - "$PROTECTED" <<'PY'
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

protected = sys.argv[1].encode("ascii")
iv = Path("iv.bin").read_bytes()
ciphertext = Path("ciphertext.bin").read_bytes()
tag = Path("tag.bin").read_bytes()
cek = Path("cek.bin").read_bytes()

# En JWE compact, protected est l'Additional Authenticated Data (AAD).
plaintext = AESGCM(cek).decrypt(iv, ciphertext + tag, protected)
print(plaintext.decode("utf-8"))
PY
```

Cette dernière commande déchiffre le payload et vérifie simultanément le tag
GCM. Une modification du header protégé, de l'IV, du ciphertext ou du tag provoque
une erreur `InvalidTag`. La sortie doit ensuite être contrôlée comme dans
`read_jwe.py` : algorithmes attendus, expiration, audience, émetteur, sujet et
permissions métier.

---

[Retour en haut](#vérification-avec-openssl-et-bash) · [Accueil du projet](README.md)

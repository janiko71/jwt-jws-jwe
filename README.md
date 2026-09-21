# Mini tutoriel JWT / JWS / JWE

Ce projet montre comment générer, lire et vérifier des JWT en Python avec les bibliothèques `PyJWT` et `jwcrypto`.

## 1. Qu'est-ce qu'un JWT ?

Un JWT (JSON Web Token) est un token encodé en Base64 qui contient des données (claims) et peut être signé pour garantir son intégrité.

Un JWT a la forme suivante :

```text
<header>.<payload>.<signature>
```

- header : informations sur le type de token et l'algorithme de signature
- payload : les données métier (claims)
- signature : permet de vérifier que le token n'a pas été modifié

## 2. JWS : JSON Web Signature

Un JWS est un JWT signé.

Exemple :

```python
import jwt

secret = "mon-secret"
payload = {"sub": "jeannot-lapin", "role": "admin"}

token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```

Le token est signé avec la clé secrète, ce qui permet de vérifier son authenticité.

### Vérification

```python
decoded = jwt.decode(token, secret, algorithms=["HS256"])
print(decoded)
```

## 3. JWE : JSON Web Encryption

Un JWE est un JWT chiffré. Il protège le contenu du token contre la lecture par des tiers.

En JWE, le payload est chiffré et ne peut être lu qu'avec la bonne clé privée ou clé secrète selon le mécanisme utilisé.

Dans cet exemple, le payload est chiffré avec la clé publique RSA du destinataire. Le token utilise `RSA-OAEP-256` pour protéger la clé de chiffrement et `A256GCM` pour chiffrer les données :

```python
from jwcrypto import jwk, jwe

public_key = jwk.JWK.from_pem(open("public.pem", "rb").read())
encrypted_token = jwe.JWE(
    plaintext=b'{"sub": "jeannot-lapin"}',
    protected={"alg": "RSA-OAEP-256", "enc": "A256GCM"}
)
encrypted_token.add_recipient(public_key)
token = encrypted_token.serialize(compact=True)
```

Le payload n'est pas lisible sans la clé privée correspondante (`private.pem`). Un JWE compact contient cinq parties séparées par des points, contrairement à un JWS qui en contient trois.

## 4. Différence entre JWT, JWS et JWE

- JWT : concept général
- JWS : JWT signé
- JWE : JWT chiffré

### Résumé simple

- JWS = on vérifie l'identité et l'intégrité
- JWE = on protège aussi la confidentialité

## 5. Les claims standards importants

Voici les plus courants :

- `iss` : issuer, émetteur
- `sub` : subject, sujet / utilisateur
- `aud` : audience, destinataire prévu
- `exp` : expiration
- `nbf` : not before, valide à partir de
- `iat` : issued at, date d'émission

Exemple :

```python
payload = {
    "iss": "https://example.com",
    "sub": "jeannot-lapin",
    "aud": "jwt-demo-app",
    "exp": 1760000000,
    "nbf": 1720000000,
    "iat": 1720000000,
    "role": "Super Admin"
}
```

## 6. Vérification d'un token JWT

Une vérification cryptographique typique ressemble à ceci :

```python
try:
    decoded = jwt.decode(
        token,
        secret,
        issuer="https://example.com",
        audience="jwt-demo-app",
        algorithms=["HS256"],
        options={"require": ["exp", "iat", "nbf", "iss", "aud", "sub"]}
    )
    print(decoded)
except jwt.exceptions.PyJWTError as e:
    print(f"Erreur JWT : {type(e).__name__} - {e}")
```

### Vérification de l'audience (`aud`)

Le claim `aud` indique pour quel destinataire le token est destiné. C'est important pour empêcher qu'un token généré pour un service A soit utilisé par un service B.

Exemple :

```python
decoded = jwt.decode(
    token,
    secret,
    algorithms=["HS256"],
    audience="jwt-demo-app"
)
```

Si le token a un `aud` différent, la vérification échoue.

### Vérification métier hors `decode`

Il faut aussi vérifier des règles propres à l'application après le `decode`, par exemple :

- le sujet (`sub`) correspond à l'utilisateur attendu
- l'émetteur (`iss`) est bien celui que le service attend
- le rôle ou les permissions sont autorisés pour cette action

Exemple :

```python
if decoded.get("sub") != "jeannot-lapin":
    raise PermissionError("Utilisateur inattendu")

if decoded.get("role") != "Super Admin":
    raise PermissionError("Rôle insuffisant")
```

C'est important parce que `jwt.decode()` valide le token, mais pas forcément les règles métier de votre application.

## 7. Lecture d'un JWE

Le token chiffré est déchiffré avec la clé privée RSA. Après le déchiffrement, `read3.py` vérifie les claims standards et les règles métier :

```python
import json

from jwcrypto import jwk, jwe

private_key = jwk.JWK.from_pem(open("private.pem", "rb").read())
encrypted_token = jwe.JWE()
encrypted_token.deserialize(token, key=private_key)
payload = json.loads(encrypted_token.payload.decode("utf-8"))
```

Le déchiffrement protège la confidentialité et `A256GCM` garantit l'intégrité du contenu. Pour authentifier l'identité de l'émetteur, l'application peut également utiliser un JWS signé.

## 8. Bonnes pratiques

- Ne jamais stocker de secrets sensibles en clair dans le code
- Vérifier toujours la signature pour un JWS
- Déchiffrer un JWE uniquement avec la clé privée attendue
- Vérifier l'expiration (`exp`)
- Vérifier l'audience (`aud`) pour contrôler le destinataire attendu
- Vérifier le sujet (`sub`) et l'émetteur (`iss`) si nécessaire
- Vérifier les permissions métier après le `decode`
- Utiliser des algorithmes sécurisés
- Ne pas mettre d'informations sensibles dans le payload si elles ne doivent pas être visibles

## 9. Fichiers du projet

- `write1.py` : génère un JWT et l'écrit dans `token.txt`
- `read1.py` : lit le token, le vérifie et affiche le payload
- `write2.py` : génère un JWS signé avec RSA et l'écrit dans `token.txt`
- `read2.py` : vérifie le JWS avec `public.pem`
- `write3.py` : génère un JWE chiffré avec `public.pem` et l'écrit dans `token_chiffre.txt`
- `read3.py` : déchiffre le JWE avec `private.pem` et vérifie ses claims
- `private.pem` : clé privée RSA, à protéger et à ne jamais partager
- `public.pem` : clé publique RSA utilisée pour le chiffrement et la vérification
- `requirements.txt` : dépendances nécessaires pour le projet

## 10. Générer la bi-clé RSA

Si les fichiers `private.pem` et `public.pem` n'existent pas encore, générez-les avec OpenSSL :

```bash
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl pkey -in private.pem -pubout -out public.pem
```

La clé privée `private.pem` doit rester secrète. La clé publique `public.pem` peut être distribuée au service qui chiffre les tokens.

## 11. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 12. Lancer les exemples

```bash
python write1.py
python read1.py
python write2.py
python read2.py
python write3.py
python read3.py
```

## 13. En résumé

- JWT = format de token
- JWS = JWT signé
- JWE = JWT chiffré
- Les JWT sont très utilisés pour l'authentification et les autorisations dans les applications web et API.

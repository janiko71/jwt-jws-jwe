# Mini tutoriel JWT / JWS / JWE

Ce projet montre comment générer, lire et vérifier un JWT en Python avec la bibliothèque `PyJWT`.

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

Exemple conceptuel :

```python
# Exemple conceptuel : le payload est chiffré
# et non simplement signé comme dans un JWS.
```

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

## 7. Bonnes pratiques

- Ne jamais stocker de secrets sensibles en clair dans le code
- Vérifier toujours la signature
- Vérifier l'expiration (`exp`)
- Vérifier l'audience (`aud`) pour contrôler le destinataire attendu
- Vérifier le sujet (`sub`) et l'émetteur (`iss`) si nécessaire
- Vérifier les permissions métier après le `decode`
- Utiliser des algorithmes sécurisés
- Ne pas mettre d'informations sensibles dans le payload si elles ne doivent pas être visibles

## 8. Fichiers du projet

- `write1.py` : génère un JWT et l'écrit dans `token.txt`
- `read1.py` : lit le token, le vérifie et affiche le payload
- `requirements.txt` : dépendances nécessaires pour le projet

## 9. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 10. Lancer les exemples

```bash
python write1.py
python read1.py
```

## 11. En résumé

- JWT = format de token
- JWS = JWT signé
- JWE = JWT chiffré
- Les JWT sont très utilisés pour l'authentification et les autorisations dans les applications web et API.

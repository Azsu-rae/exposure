
# Docker Setup

Create an **image** \[T\]agged `user_service`:

```
docker build -f services/user_service/Dockerfile -t user_service .
```

*Create* and *start* a **container** from an image:

On linux:
```
docker run -p 8000:8000 --env-file services/user_service/.env --add-host=host.docker.internal:host-gateway user_service
```

On windows:
```
docker run -p 8000:8000 --env-file services/user_service/.env user_service
```

# Postgres Setup

```
sudo -i -u postgres
```

```
postgres=# ALTER ROLE asura WITH SUPERUSER;
ALTER ROLE
postgres=# \du
                             List of roles
 Role name |                         Attributes
-----------+------------------------------------------------------------
 asura     | Superuser
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS

postgres=#

```

# RS256

Generates a 2048-bit RSA private key and writes it to private.pem. The private key contains everything — both the private and public components.
```
openssl genrsa -out keys/private.pem 2048
```

Extracts just the public key from the private key file and writes it to public.pem. This is the file you distribute to other services.
```
  openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

The resulting files look like:
```
  -----BEGIN RSA PRIVATE KEY-----
  MIIEowIBAAKCAQEA...
  -----END RSA PRIVATE KEY-----
  -----BEGIN PUBLIC KEY-----
  MIIBIjANBgkqhkiG9w0B...
  -----END PUBLIC KEY-----
```

2048 bits is the standard minimum for RSA. 4096 is more secure but slower to verify — 2048 is fine for JWT signing since tokens are short-lived.


# Authentication

  2. Signature verification — the important part                                                                                              11:23:37 [25/1958]

  The full call chain in JWTAuthentication.authenticate() is:

  authenticate(request)
      → get_raw_token()        # extracts Bearer token from header
      → get_validated_token()  # validates signature, expiry, token type
      → get_user()             # our override — builds TokenUser from payload

  We only override get_user(). The signature verification happens in get_validated_token() which we don't touch — it runs exactly as normal.

  Inside get_validated_token(), SimpleJWT calls PyJWT's decode() which:
  3. Decodes the Base64 payload
  4. Recomputes the HMAC signature using your SECRET_KEY (or VERIFYING_KEY for RS256)
  5. Compares it against the signature in the token
  6. Checks expiry

  If any of those fail, it raises InvalidToken before get_user() is ever called.

  The catch for store_service: for this to work, store_service must use the same key that user_service signed with. Currently both services use SECRET_KEY by
  default. As long as both .env files have the same SECRET_KEY value, verification works.

  When you move to RS256 later, user_service signs with the private key and store_service only needs the public key in SIMPLE_JWT['VERIFYING_KEY'] — which is
  safer since the private key never leaves user_service.
● Yes, by default SimpleJWT uses Django's SECRET_KEY as an HMAC shared secret (HS256 algorithm). There's no key pair — it's a single secret that both signs and
  verifies. Whoever has it can do both.

  That's the problem with HS256 in a microservice setup: to verify tokens, store_service needs the same SECRET_KEY as user_service. But that means store_service
   could also forge tokens — it has everything needed to sign new ones.

  For microservices, RS256 is the right choice:
  - user_service has the private key → can sign tokens
  - store_service has the public key → can only verify, cannot forge

  To switch, in user_service's SIMPLE_JWT:
  SIMPLE_JWT = {
      'ALGORITHM': 'RS256',
      'SIGNING_KEY': env('JWT_PRIVATE_KEY'),
      'VERIFYING_KEY': env('JWT_PUBLIC_KEY'),
      ...
  }

  And in store_service's SIMPLE_JWT:
  SIMPLE_JWT = {
      'ALGORITHM': 'RS256',
      'SIGNING_KEY': None,
      'VERIFYING_KEY': env('JWT_PUBLIC_KEY'),
      ...
  }
  You generate the key pair once with:
  openssl genrsa -out private.pem 2048
  openssl rsa -in private.pem -pubout -out public.pem

  Then put the private key only in user_service's .env, and the public key in all other services' .env files.

  Want to make that switch now?


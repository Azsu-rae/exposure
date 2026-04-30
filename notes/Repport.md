
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

❯ authentication is working thanks to django's SERCRET_KEY. To fix the cross-service authentication problem, can I just use the access token passed by the user
   when an incoming request comes in, and, if need be for a subsequent request to another service you are bound by the parameters of the client request? (or
  maybe not because you can just do payload["user_id"] = <whatever you want>?) anyways what do you think? Should we move on to RSA? How to fix cross-service
  auth?

● Good thinking. Let me break it down:

  Passing the user's token to user_service — yes, this works and is a valid pattern for user-initiated requests. store_service forwards the Authorization:
  Bearer <token> header to user_service, which validates it with its own key. But it only covers requests triggered by a user. It doesn't cover background jobs
  or service-initiated calls, and doesn't solve the forging problem.

  The forging problem with HS256 — you're right to flag it. Since store_service has the same SECRET_KEY, it can craft {"user_id": 1, "role": "ADMIN", ...}, sign
   it with the shared secret, and user_service would accept it as legitimate. That's a real vulnerability.

  RS256 fixes this cleanly:
  - store_service gets the public key only → can verify, cannot sign
  - Forging is mathematically impossible without the private key
  - Token forwarding still works the same way

  For service-to-service calls specifically (store_service calling user_service's lookup endpoint):
  - If acting on behalf of a user → forward their token
  - For system/background calls → a separate API key header (X-Service-Key) is the simplest approach, checked independently of JWT

  The verdict: yes, move to RS256 now — it's straightforward and closes the biggest hole. Want to do it?
❯ but even with RS, can't the store service keep the signature parrt of the jwt and just do payload["user_id"] = ... and thus steal the identi15:14:22 [15/1895]
  user?

● No — changing the payload invalidates the signature. The signature is computed over both the header and payload together:

  signature = RSA_sign(base64(header) + "." + base64(payload), private_key)

  If you change even one character in the payload, the signature no longer matches that payload. When user_service verifies:

  RSA_verify(base64(header) + "." + base64(new_payload), signature, public_key) → FAIL

  The old signature was computed over the old payload. You'd need the private key to produce a valid signature for the modified payload — which store_service
  doesn't have with RS256.

  With HS256 (current setup) this attack is possible precisely because store_service has the same secret used to both sign and verify. That's exactly the hole

● Good questions — these are all examples of the same fundamental problem: cross-service state consistency. Let me explain how it's handled, then address your
  three specific cases.

  How coherence is handled in microservices

  Two patterns:

  Synchronous (HTTP calls between services)
  Service A calls service B directly after doing its work. Simple, but creates tight coupling — if B is down, A's operation fails or needs a rollback.

  Asynchronous (event-driven messaging — RabbitMQ, Kafka, Redis Streams)
  Service A publishes an event (order.created), service B subscribes and reacts when it's ready. Loosely coupled, resilient, but introduces eventual consistency
   — B's state lags briefly behind A's.

  The industry default for microservices is async events for anything non-critical-path, and sync calls only when you need an immediate answer to continue (e.g.
   payment authorization).

  ---
  Your three cases
  Your three cases


  1. order_id sync (store → delivery)
  When store_service creates an order, delivery_service needs to know. → store_service publishes order.created, delivery_service creates a pending delivery
  record.

  2. Order/delivery state alignment
  When delivery status changes to DELIVERED or CANCELLED → order status should follow. → delivery_service publishes delivery.status_changed, store_service
  updates the order.

  3. User role → SELLER when store created
  This one is actually backwards. The role should be set at registration, not derived from store creation — store_service shouldn't be driving user_service's
  data. The cleaner design is:
  - User registers with role: SELLER
  - store_service's IsSeller permission gates store creation
  - No cross-service call needed

  If your business logic requires users to start as BUYER and become SELLER by creating a store, then store_service publishes store.created → user_service
  updates the role. But that's a weaker design.

  ---
  What I'd recommend for your stack right now

  You have no message broker yet. Two options:

  1. Add Redis (or RabbitMQ) now — correct long-term, more setup
  2. Sync HTTP calls for now — using services.py pattern you already have in store_service, then migrate to events later

  Which direction do you want to go?

✻ Churned for 38s

● apps.py is where you configure your Django app's metadata and run startup code.

  Every Django app is represented by an AppConfig class. Django instantiates it once at startup and uses it for things like the app's label, verbose name, and
  default auto field type.

  The key method is ready() — Django calls it exactly once after all models have been loaded and the app registry is fully initialized. It's the safe place to
  run any code that depends on models being available, which is why signal connections go there. If you connected signals at module level (e.g. directly in
  models.py), you'd risk running code before the app registry is ready.

  Django auto-discovers AppConfig subclasses via the default_app_config variable in __init__.py, or in modern Django (3.2+), it just picks up the class
  automatically if it's the only one in apps.py.

  So in your case:

  class StoresConfig(AppConfig):
      name = "stores"          # must match the app name in INSTALLED_APPS

      def ready(self):
          import stores.signals  # registers all @receiver decorators

  The import stores.signals line has no side effects by itself — the side effect is the @receiver decorators running at import time, which register the signal
  handlers with Django's signal dispatcher. Without the import, the signal handlers are never registered even though the file exists.

✻ Crunched for 9s


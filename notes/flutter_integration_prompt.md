# Wire the existing Flutter app to the Exposure backend

## What you are doing

I have a working Flutter codebase for the **Exposure** marketplace app and a working Django microservices backend. Your job is **not to rewrite the app** — it is to **adapt the existing networking layer** so the app talks to the backend correctly through the new ingress, the right URL paths, the right auth flow, and the right eventual-consistency assumptions.

**Before you change anything**, read these existing parts of the Flutter project end-to-end:
- `lib/core/network/` (Dio setup, interceptors)
- `lib/core/config/` (base URLs, env)
- `lib/core/storage/` (token storage)
- `lib/features/auth/data/` (login / register / refresh)
- one or two feature data layers (e.g. `lib/features/feed/data/` or `lib/features/orders/data/`)
- `main.dart` and any provider/Dio bootstrap

Map *what already exists* before you decide *what to change*. If the codebase already has an interceptor that mostly works, edit it — don't replace it.

---

## The single most important change: one base URL

The backend is now fronted by **Traefik** on the dev host. There is **one ingress URL** for all services, not five.

- Default dev base URL: `http://localhost` (or `http://10.0.2.2` from the Android emulator → host loopback; `http://<host-ip>` from a physical device on the same LAN)
- Path routing is done by Traefik, transparent to the client.
- All services are reachable through this same host on port 80.

The existing codebase likely has **five** `--dart-define` keys (`USER_BASE_URL`, `STORE_BASE_URL`, `SOCIAL_BASE_URL`, `DELIVERY_BASE_URL`, `PAYMENT_BASE_URL`) pointing at ports `8000–8004`.

**Collapse them to a single `API_BASE_URL`.** Keep the per-feature data clients organised the same way, but they all share one Dio with one `baseUrl`. If you find five Dio instances, merge them into one — or keep one factory but have it return the same shared client for all callers.

If removing the per-service keys would be too invasive given how the codebase is wired, the safe alternative is: keep the keys, but set them all to the same value (the Traefik base URL). Don't keep them pointing at different ports — that bypasses Traefik and breaks the moment we move to staging.

---

## JWT — verify before you change

The backend uses **RS256** JWTs issued by user_service.

- Access token lifetime: **5 minutes**
- Refresh token lifetime: **1 day**
- Algorithm: RS256 (the app does not need to verify — the gateway and services do)
- Token payload includes: `user_id`, `username`, `email`, `role`, `is_active`

Required client behavior — confirm each is already done; if not, fix:

1. **Auth header**: `Authorization: Bearer <access>` on every request **except** the login/register/refresh calls.
2. **Refresh interceptor**: on `401`, single-flight refresh using the stored refresh token; retry the original request once; if refresh itself returns `401`, clear storage and route to Login.
3. **Token storage**:
   - **Refresh token** → `flutter_secure_storage` (encrypted, on-device).
   - **Access token** → in-memory only. **Never** persist it to disk.
4. **Logout**: must call the backend logout (which blacklists the refresh on the server) **and** clear local storage. Skipping the API call leaves the refresh valid until expiry.

If the existing app is missing any of these, add it. Do **not** replace the Dio config wholesale — patch in place.

---

## API surface — verified against the running services

The URL prefixes below are the **real** paths Django serves. The earlier scaffold prompt may have slightly different paths (e.g. `/api/auth/login/`); ignore those and use these.

### Auth & profile (user_service)

| Method | Path                              | Notes                                          |
|--------|-----------------------------------|------------------------------------------------|
| POST   | `/api/users/register/`            | `{username, email, phone, password, password2, role}`. Cannot register as `ADMIN` or `DELIVERY`. |
| POST   | `/api/users/login/`               | Returns `{user, tokens: {access, refresh}}`   |
| POST   | `/api/users/logout/`              | Body: `{refresh}`                              |
| POST   | `/api/users/refresh/`             | Body: `{refresh}` → `{access}`                 |
| POST   | `/api/users/change-password/`     | Body: `{old_password, new_password}`           |
| GET    | `/api/profile/`                   | Includes `seller_profile` if role is SELLER    |
| PUT    | `/api/profile/update/`            | Partial updates allowed                        |
| PUT    | `/api/profile/seller/`            | SELLER only                                    |
| DELETE | `/api/profile/delete/`            |                                                |
| GET    | `/api/lookup/?username=...`       | Auth required                                  |

### Stores, products, orders (store_service)

DRF DefaultRouter — standard list/retrieve/create/update/destroy on each resource.

- `/api/stores/` — POST/PUT/DELETE require role SELLER and ownership.
- `/api/products/` — listing filters out `is_blocked=true` for buyers; sellers see their own blocked items.
- `/api/orders/` — POST body shape:
  ```json
  {
    "shipping_address": "...",
    "payment_method": "CASH | CARD",
    "items": [{"product_id": 12, "quantity": 2}]
  }
  ```
  One Order = one Store implicitly (via the products in items). If the cart spans multiple stores, the client must split into N orders.

### Social — feed, search, pages, reviews (social_service)

| Method | Path                              | Notes                                          |
|--------|-----------------------------------|------------------------------------------------|
| GET    | `/api/posts/?offset=&limit=&category=` | Paginated feed; each item embeds `product` and `store` |
| GET    | `/api/posts/{id}/`                | Post + product + store + reviews + reviewer info |
| POST   | `/api/posts/create/`              | **Multipart** if including image; SELLER + must own the store of the product |
| DELETE | `/api/posts/{id}/delete/`         |                                                |
| GET    | `/api/search/?q=&category=`       |                                                |
| GET    | `/api/pages/{store_id}/`          | Store info + posts + aggregate rating          |
| POST   | `/api/reviews/create/`            | `{post_id, stars: 1..5, comment}`. One review per (post, user) — backend rejects duplicates with 400. |
| DELETE | `/api/reviews/{id}/delete/`       | Must be the review's author                    |

### Delivery & SSE tracking (delivery_service)

| Method | Path                                          | Notes                                          |
|--------|-----------------------------------------------|------------------------------------------------|
| GET    | `/api/deliveries/`                            | Filtered by role                               |
| GET    | `/api/deliveries/{id}/`                       |                                                |
| POST   | `/api/deliveries/{id}/simulate/start/`        | Dev/QA only — DELIVERY role                    |
| GET    | `/api/deliveries/{id}/stream/`                | **SSE** — `data: {...}\n\n` events; respect `done: true` |
| GET    | `/api/deliveries/{id}/status/`                | Polling fallback if SSE unavailable            |

**SSE specifics for Flutter:**
- Use `flutter_client_sse` (or equivalent). Pass the `Authorization` header — Traefik forwards it.
- Reconnect with exponential backoff on transient errors; stop on `done: true`.
- Polling fallback every 5 s if SSE has failed twice in a row.

### Payments (payment_service)

| Method | Path                                  | Notes                                          |
|--------|---------------------------------------|------------------------------------------------|
| GET    | `/api/payments/`                      | Auto-scoped by role                            |
| GET    | `/api/payments/{id}/`                 |                                                |
| POST   | `/api/payments/create/`               | `{order_id, seller_id, amount, method: CASH \| CARD}` → `{id, status, checkout_url?}` |

If `method=CARD`, open `checkout_url` in a WebView. The simulator marks it `HELD` immediately on success — treat that as "payment initiated", not "settled". Settlement happens via delivery state changes.

---

## Eventual-consistency gotchas the UI must handle

These are facts about the backend that affect what screens have to render gracefully. The existing app may already handle some of them; verify, don't assume.

1. **BUYER → SELLER promotion is async.**
   When a BUYER first creates a store, store_service publishes `store.created`. user_service consumes it, promotes the user to SELLER, and republishes `user.updated`. The role on the existing access token is now stale.
   - After a successful `POST /api/stores/`, **re-fetch `GET /api/profile/`** (or refresh the JWT) before you reveal merchant-only UI. Don't depend solely on the in-memory token claims.

2. **Order → Delivery is async.**
   `POST /api/orders/` succeeds immediately. delivery_service projects a `Delivery` row from a `order.created` event a moment later. The Tracking screen may receive a 404 from `/api/deliveries/{id}/` for a brief window.
   - Show "Awaiting delivery dispatch" / a loading state, then retry every 1–2 seconds for up to ~15 seconds before surfacing a real error.

3. **Payment status is not buyer-driven.**
   The buyer cannot move a payment from `HELD → RELEASED` themselves. That happens automatically when the delivery state machine reaches `Delivered`. Surface payment status as informational; never offer a "Release" button to the buyer.

4. **Social refs are eventually consistent.**
   social_service shows usernames and store names from a local read model rebuilt by RabbitMQ events. There is a small window where a renamed store / username still shows the old value. Don't add complex refetch loops — accept the staleness.

---

## What NOT to change

These are intentional in the existing app. Leave them alone unless explicitly broken.

- **Local-only features**: likes (per-post toggle in `shared_preferences`), follows, MockMode, theme. There is no backend API for these — keep the stubs.
- **Client-side AI moderation simulation**: keyword check before product/post submission. Pure local check; don't try to wire it to a real endpoint.
- **AI document processing screen**: pure UI mock; don't connect it.
- **Cart**: local state, persisted in `shared_preferences`. Group by store at checkout — backend has no multi-store cart.

---

## Checklist for the integration pass

Tick each off as you confirm it in the code:

- [ ] One `API_BASE_URL` config; all five service URLs collapsed.
- [ ] Single shared `Dio` instance (or one factory returning a single instance).
- [ ] `AuthInterceptor` attaches `Bearer <access>` to all requests except `/api/users/login/`, `/api/users/register/`, `/api/users/refresh/`.
- [ ] `RefreshInterceptor` does single-flight refresh on 401, retries the original request once.
- [ ] Refresh token stored only in `flutter_secure_storage`; access token in memory only.
- [ ] All endpoint paths in the data layer match the table above (especially `/api/users/login/` not `/api/auth/login/`).
- [ ] `POST /api/orders/` body shape matches: `{shipping_address, payment_method, items: [{product_id, quantity}]}`.
- [ ] `POST /api/posts/create/` is sent as **multipart** when an image is attached.
- [ ] Tracking screen handles the "no Delivery row yet" 404 with a retry loop.
- [ ] After a successful first `POST /api/stores/`, the app re-fetches `/api/profile/` before revealing merchant UI.
- [ ] SSE client passes the `Authorization` header and stops on `done: true`.
- [ ] Logout calls `POST /api/users/logout/` **and** clears storage.
- [ ] On Android emulator, base URL is `http://10.0.2.2`; document this in the README.
- [ ] On a physical device on the same LAN, base URL is `http://<host-ip>`; document this too. (Traefik listens on `:80`, so no port suffix needed.)
- [ ] `cleartextTrafficPermitted` is enabled for the dev host in `AndroidManifest.xml` / iOS `Info.plist` `NSAppTransportSecurity` while we're on plain HTTP — but only for dev domains. Plan the TLS switch as a follow-up.

---

## Reference: Bruno collections

Canonical request/response examples for every endpoint live under `exposure/api/`. If a response shape in the Flutter DTOs disagrees with the Bruno example, **the Bruno example is the source of truth** — update the DTO.

---

## Output expectations

Do **not** produce a green-field rewrite. Produce a focused diff of the existing project:

1. A summary of what you found in the current networking layer.
2. The list of files you changed and why (one sentence each).
3. The actual code changes — small, surgical, named-and-typed. No unrelated cleanup.
4. A short README/CHANGELOG note explaining the new single-base-URL config and how to launch against:
   - The local dev host (Traefik on `:80`)
   - The Android emulator (`10.0.2.2`)
   - A physical device on the LAN

If you discover a screen that would behave wrongly under the eventual-consistency gotchas above, fix it as part of the same pass and call it out in the summary.

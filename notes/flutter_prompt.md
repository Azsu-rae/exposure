# Build a Flutter mobile prototype for the **Exposure** social marketplace

## 🎯 PROJECT GOAL

A modern Android (Flutter) app frontend for the existing **Exposure** microservice backend. Combines a social feed with full e-commerce flows: product discovery, cart/checkout, real-time order tracking, merchant store management, and a client-side AI moderation simulation that complements the backend's own moderation.

The result should look and feel like a production-ready startup product.

---

## 🧱 BACKEND CONTEXT (read first — drives every screen)

The Flutter app talks to **5 Django microservices**, all sharing a single RS256 JWT issued by `user_service`. Bruno collections live in `exposure/api/` — every endpoint listed below has a `.yml` example you can copy from.

| Service     | Default port | Responsibilities                                          |
| ----------- | ------------ | --------------------------------------------------------- |
| user        | 8000         | Auth, profiles, JWT issuance                              |
| store       | 8001         | Stores, Products, Orders                                  |
| delivery    | 8002         | Deliveries, drivers, SSE stream for tracking              |
| payment     | 8003         | Simulated escrow payments (CASH / CARD)                   |
| social      | 8004         | Posts (product wrappers), Reviews, Feed, Search, Pages    |

### JWT mechanics
- `POST /api/auth/login/` returns `{ user, tokens: { access, refresh } }`.
- `access` lifetime: 5 min. `refresh`: 1 day. Algorithm: RS256.
- Token payload includes `user_id`, `username`, `email`, `role`, `is_active`.
- `POST /api/auth/refresh/` exchanges refresh → new access.
- `POST /api/auth/logout/` blacklists the refresh.
- All non-auth endpoints across all services expect `Authorization: Bearer <access>`.

### Role mapping
- **Backend roles**: `BUYER`, `SELLER`, `DELIVERY`, `ADMIN`.
- **App roles**: Customer = `BUYER`, Merchant = `SELLER`. SELLER also implies BUYER permissions on the store/cart side.
- DELIVERY and ADMIN are out of scope for this app — hide their flows.

### Eventual consistency the app needs to be aware of
- Creating a store on store_service publishes `store.created` → user_service promotes BUYER→SELLER → republishes `user.updated`. The new role only appears after the next `/api/profile/` fetch (or token refresh).
- Creating an Order publishes `order.created` → delivery_service projects a `Delivery` row asynchronously. The tracking screen may briefly show "no delivery yet" — handle this with a loading state.
- Payment status (HELD → RELEASED / REFUNDED) is driven by the delivery state machine, not the buyer.

---

## 👤 USER ROLES IN THE APP

1. **Customer (BUYER)** — default after registration
2. **Merchant (SELLER)** — granted automatically after creating a Store; can also register directly with `role=SELLER`

---

## 🧱 TECH REQUIREMENTS

- Flutter latest stable, Dart 3+
- State management: **Riverpod** (preferred) or Provider
- HTTP: **Dio** + interceptors (auth, refresh-on-401, error mapping)
- Secure storage: **flutter_secure_storage** for refresh token; access kept in-memory
- SSE: **flutter_client_sse** (or equivalent) for delivery tracking
- Routing: **go_router**
- Image: **cached_network_image**
- Forms: **reactive_forms** or built-in `Form` + `TextFormField`
- **Clean architecture** layered: `data/` (DTOs, API clients) → `domain/` (entities, repositories) → `presentation/` (screens, widgets, providers)
- Configuration via `--dart-define` (per-service base URLs) so the same APK can target dev/staging

### Required folder layout
```
lib/
  core/
    network/          # Dio, interceptors, AuthInterceptor
    storage/          # secure storage wrappers
    config/           # base URLs per service
    errors/           # exception mapping
  features/
    auth/
    feed/
    search/
    product/
    store/
    cart/
    checkout/
    orders/
    tracking/
    profile/
    merchant/
    moderation/       # client-side AI sim
    documents/        # AI document UI mock
  shared/
    widgets/          # PostCard, BlockedCard, PriceTag, RoleBadge…
    theme/
  main.dart
```

---

## 🌐 API SURFACE (use the Bruno files in `exposure/api/` as the canonical examples)

### user_service (8000)
- `POST /api/auth/register/` — body `{username, email, phone, password, password2, role}`
- `POST /api/auth/login/` — returns tokens
- `POST /api/auth/logout/` — body `{refresh}`
- `POST /api/auth/refresh/` — body `{refresh}`
- `POST /api/auth/change-password/`
- `GET  /api/profile/` — includes `seller_profile` if SELLER
- `PUT  /api/profile/update/`
- `PUT  /api/profile/seller/`
- `DELETE /api/profile/delete/`
- `GET  /api/lookup/?username=` — auth required

### store_service (8001)
- `GET/POST /api/stores/`, `GET/PUT/DELETE /api/stores/{id}/` — POST/PUT/DELETE require SELLER
- `GET/POST /api/products/`, `GET/PUT/DELETE /api/products/{id}/` — POST requires `store_id` + ownership; GET filters out `is_blocked=true`
- `GET/POST /api/orders/`, `GET /api/orders/{id}/` — body for POST: `{shipping_address, payment_method, items: [{product_id, quantity}]}`

### delivery_service (8002)
- `GET /api/deliveries/`, `GET /api/deliveries/{id}/`
- `POST /api/deliveries/{id}/simulate/start/` — DELIVERY role only (use only for QA/dev)
- `GET /api/deliveries/{id}/stream/` — **SSE** — emits `data: {…}\n\n` events with status, message, done flag
- `GET /api/deliveries/{id}/status/` — polling fallback

### payment_service (8003)
- `POST /api/payments/create/` — body `{order_id, seller_id, amount, method: CASH|CARD}` → returns `{id, status, checkout_url?}`
- `GET /api/payments/`, `GET /api/payments/{id}/` — auto-scoped by role

### social_service (8004)
- `GET /api/posts/?offset=&limit=&category=` — paginated feed; each item embeds `product` and `store`
- `GET /api/posts/{id}/` — post + product + store + reviews + reviewer usernames
- `POST /api/posts/create/` — multipart with optional image; SELLER, must own the store of the product
- `DELETE /api/posts/{id}/delete/`
- `GET /api/search/?q=&category=`
- `GET /api/pages/{store_id}/` — store info + posts + aggregate rating
- `POST /api/reviews/create/` — `{post_id, stars, comment}`, one per (post, user)
- `DELETE /api/reviews/{id}/delete/`

---

## 📱 SCREENS

### 1️⃣ Splash
- Logo, smooth fade/scale animation
- Reads stored refresh token; if valid, refresh access then route to Home; otherwise route to Login.

### 2️⃣ Auth
- **Login** — username + password → call user_service, persist tokens
- **Register** — fields: username, email, phone, password, password2, role (Customer / Merchant)
- Validation matches backend: passwords must match; cannot register as ADMIN/DELIVERY
- On error, surface server-side validation messages from the response body

### 3️⃣ Main shell — bottom nav
- Home / Search / Cart / Profile (+ Merchant tab when role is SELLER)

### 🏠 4️⃣ Home Feed (CORE)
- Vertical, infinite-scroll, paginated via `offset`/`limit` against `/api/posts/`
- Pull-to-refresh
- Category chips at top (filter by `category` query param)
- Each item is a **Post Card**:
  - Post image (cached)
  - Store name (tap → Store Profile)
  - Product name + price + category badge
  - Title + description (collapsible)
  - **Like ❤️** — local-only (persist with shared_prefs by post_id; backend has no concept of likes). Stub the API call site with `// TODO: when likes API exists, POST here`.
  - **Comment 💬** — opens Post Detail (which is where reviews live)
  - **Share 🔗** — system share intent with deep-link URL
  - Average rating + review count
- Empty state and skeleton loaders

### 🚫 Blocked Product Card (Merchant view only)
- The buyer feed never receives blocked products (server filters them).
- In the **Merchant > My Products** list, products with `is_blocked=true` render a red warning card:
  > ⚠️ This product is not available
  > Reason: Policy violation (illegal or restricted item)
  Optional "Learn More" button.

### 🔍 5️⃣ Search
- Search bar, debounced 300 ms, hits `/api/search/?q=`
- Optional category filter
- Grid of post cards
- Tap → Product/Post Detail

### 🛍 6️⃣ Product / Post Detail
- Hero image
- Product name, description, price, category
- Store row (tap → Store Profile)
- **Add to Cart** (local cart state)
- **Buy Now** → straight to Checkout with this single item
- **Reviews** section (real, from backend) — list + "Write a review" form (1–5 stars + comment); enforces backend rule: one review per post per user
- Pull-to-refresh re-fetches `/api/posts/{id}/`

### 🏬 7️⃣ Store Profile
- `GET /api/pages/{store_id}/`
- Store banner, name, wilaya/city, average rating, review count
- **Follow** button — local-only (mark as such, stub future API)
- Grid of the store's posts

### 🛒 8️⃣ Cart (local state, persisted)
- List of items: product, quantity, subtotal
- +/- quantity controls, remove item
- Total
- **Group items by store** — each store becomes its own Order at checkout (the backend has no multi-store cart concept, one Order = one store implicitly via products)
- Checkout button

### 💳 9️⃣ Checkout
- Address input (free text → `shipping_address`)
- Payment method: Cash (CASH) / Card (CARD)
- For each store-group:
  1. `POST /api/orders/` → returns `order_id`
  2. `POST /api/payments/create/` with `{order_id, seller_id (from product.store.seller), amount (cart total), method}`
  3. If CARD: open the returned `checkout_url` in a WebView; the simulator marks it HELD immediately, but treat success as "payment initiated"
  4. If CASH: payment stays PENDING until the courier confirms collection
- Show summary on success with links to Order Tracking

### 🚚 🔟 Order Tracking
- Stepper UI mirroring backend states: **Pending → Accepted → In Transit → Delivered** (or **Cancelled**)
- Connect to SSE `GET /api/deliveries/{id}/stream/` with `Authorization` header; render `message` field as toast/subtitle as events arrive
- Fallback to polling `/status/` every 5 s if SSE fails
- Show "Awaiting delivery dispatch" state when no Delivery row exists yet (eventual consistency window)
- Handle `done: true` to stop the stream gracefully

### 👤 1️⃣1️⃣ Profile
- `GET /api/profile/`
- User info (username, email, phone, role badge)
- **My Orders** → list `/api/orders/`, tap → Order Tracking
- **My Stores** (visible if SELLER) → list `/api/stores/` filtered to seller==me
- **Edit Profile** → `PUT /api/profile/update/`
- **Change Password** → `POST /api/auth/change-password/`
- **Logout** → `POST /api/auth/logout/` + clear secure storage
- **Delete Account** → confirmation dialog → `DELETE /api/profile/delete/`

### 🏪 1️⃣2️⃣ Merchant section (SELLER only)
**Stores tab**
- List my stores; "Create Store" CTA if none
- Create Store form: name, description, wilaya, city, ccp → `POST /api/stores/`
- After first store creation, profile may need re-fetch to reflect SELLER role (BUYER→SELLER promotion is async)

**Products tab (per store)**
- List my products (uses `/api/products/`)
- "Add Product" CTA → form
- Edit / Delete buttons per product
- Blocked products show the red warning card

**Add Product form**
- Product name, description, price, stock, category
- Image upload (mock — backend Product has no image field yet; show a TODO chip and store the local file for the future API)
- Submit triggers the **client-side AI moderation simulation** *before* the API call:
  - Loading dialog: "Analyzing product with AI…"
  - 1–2 s delay
  - Run keyword check below
  - If APPROVED → `POST /api/products/?store_id=<id>` and show success
  - If BLOCKED → show ❌ rejection with reason; **do not** call the API
- Even on client-approval, the server may still set `is_blocked=true` later — surface that on next list refresh

**Posts tab**
- Create a Post for an existing product (multipart `POST /api/posts/create/` with image)
- Delete posts

### 🤖 Client-side AI moderation (mock)
- Pure local check, runs before submitting product/post
- Trigger keywords (case-insensitive): `drug`, `weapon`, `illegal`, `gun`, `knife`, `narcotic`, `explosive`
- Reasons surfaced: "Illegal item detected" / "Restricted category" / "Prohibited keyword"
- Implement as `Future<ModerationResult> moderate({required String name, required String description})` so it can be swapped for a real `POST /api/moderate/` later (stub the call site with a comment)

### 🤖 1️⃣3️⃣ AI Document Processing (pure mock)
- Accessible from Profile > Tools or Merchant > Tools
- Upload document button (file picker, mock)
- Show preview placeholder
- "Processing…" animation, 1.5 s
- Show fake extracted JSON:
  ```json
  { "invoice_number": "12345", "date": "2026-05-02", "total": "5000 DA" }
  ```
- Wrap the upload call in a `DocumentAIService` stub that throws `UnimplementedError` so the future backend wiring is visible

---

## 🔧 CROSS-CUTTING REQUIREMENTS

### Networking
- One `Dio` per service (or a single Dio with per-call base URLs)
- `AuthInterceptor`: attach `Bearer <access>` to every request except `/auth/*`
- `RefreshInterceptor`: on 401, single-flight refresh using the refresh token; retry the original request once; on refresh failure, clear storage and route to Login
- All errors mapped to typed `AppException` (`NetworkException`, `UnauthorizedException`, `ValidationException(fieldErrors: Map)`, etc.)

### Storage
- Refresh token in `flutter_secure_storage`
- Cart, likes, follows, theme preference in `shared_preferences`
- Never store the access token to disk

### Theming
- Material 3, light + **dark mode** (toggle in Profile)
- Single seed color, generated `ColorScheme`
- Rounded cards (`12–16` radius), soft shadows
- Consistent spacing scale (4/8/12/16/24)
- Typography scale via `TextTheme`

### Localization & format
- Currency: **DZD** with `intl` `NumberFormat.currency(locale: 'fr_DZ', symbol: 'DA')`
- Dates: `intl` with `fr_DZ`
- Wilaya/city pickers seeded with Algerian wilayas (at least the 10 largest)
- App copy in English; structure for future Arabic/French i18n

### UX polish
- Skeleton loaders on every async list
- `SnackBar` feedback for cart actions, follows, likes, errors
- Hero animations on Post image → Detail
- Empty states with illustrations/icons
- Pull-to-refresh on every list
- Debounced search

### Configuration
- `--dart-define` keys: `USER_BASE_URL`, `STORE_BASE_URL`, `DELIVERY_BASE_URL`, `PAYMENT_BASE_URL`, `SOCIAL_BASE_URL`
- Defaults point at `http://10.0.2.2:<port>` (Android emulator → host loopback)
- Provide a `.env.example` and a README section explaining how to switch base URLs

---

## 📦 LOCAL MOCK DATA (for offline demos / when backend is down)

Provide a `MockMode` toggle (debug only) that swaps repositories for in-memory implementations seeded with:
- 4 users (2 buyers, 2 sellers — one of each is "you")
- 3 stores
- 12 products (2 with `is_blocked=true` for the merchant view)
- 5 posts in the feed
- 8 reviews across posts
- 2 orders in different stages (Pending, In Transit)

When `MockMode` is on, banner the app bar with "MOCK MODE" so it's obvious.

---

## 🧪 ACCEPTANCE CRITERIA

The reviewer should be able to:
1. Register a Customer → see the feed → like, search, view a post detail, write a review.
2. Add items to cart from multiple stores → checkout (CASH) → see one Order per store → open tracking.
3. Watch the tracking screen update live via SSE while a dev runs the delivery simulator from the backend.
4. Register a Merchant (or create a store as a Customer and observe the role upgrade after a profile refresh) → create a Store → add a Product → submit a name containing "weapon" and see the AI moderation reject it client-side.
5. Submit a clean product → see it published → wrap it in a Post with an image → confirm it appears in the feed.
6. Toggle dark mode and MockMode.
7. Trigger 401 by waiting >5 min on a screen → confirm the silent refresh keeps the user logged in.
8. Force a logout → land on Login; refresh token is wiped from secure storage.

---

## 🚫 EXPLICIT NON-GOALS

- No real payment integration. Card flow opens the simulated `checkout_url` in a WebView and treats it as success.
- No backend "likes" or "follows" — these are local-only with stubbed call sites.
- No DELIVERY or ADMIN UIs.
- No real document AI — the screen is a UI mock only.
- No push notifications (yet) — leave a TODO for FCM at the App shell level.

---

## 🎯 FINAL OUTPUT

A complete Flutter project that:
- Boots against the live Exposure backend with `--dart-define` URLs
- Demonstrates the full Customer + Merchant flow end-to-end
- Includes the AI moderation simulation (client-side) and the AI document UI (mock)
- Looks like a production-ready prototype: Material 3, dark mode, skeleton loaders, hero animations, snackbar feedback
- Has a `MockMode` toggle so it can be demoed without the backend running

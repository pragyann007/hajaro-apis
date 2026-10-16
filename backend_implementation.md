# Hajaro Backend API Implementation Specification

**Document status:** Production implementation contract v1.0  
**Product:** Hajaro — Nepal nationwide local-business discovery  
**Derived from:** `HAJARO BACKEND INFRASTRUCTURE.pdf`, frontend services/mocks (`src/services/*`, `src/mocks/transport.ts`), types (`src/types/api.ts`, `src/types/discovery.ts`), and product docs (`hajaro.md`, `BACKEND_HANDOFF.md`, `README.md`, `DEVELOPMENT_REPORT.md`)  
**Backend stack (PDF):** FastAPI · PostgreSQL 15 · PostGIS · SQLAlchemy 2.x · GeoAlchemy2 · asyncpg · Alembic · Pydantic v2  
**Schema:** `hajaro` (dedicated PostgreSQL schema)  
**Geographic scope:** All Nepal from day one (Damak is operational growth priority, never a registration/discovery allowlist)

---

## 1. Purpose of this document

This file is the complete API contract required to replace the frontend mock transport (`src/mocks/transport.ts` → `/api/mock/...`) with a real FastAPI backend so that `NEXT_PUBLIC_API_MODE=live` works end-to-end.

It covers:

1. **Phase 1 — Implement now (PDF):** public discovery, registration submissions, claims, verification data models, search, maps, offers, published reviews.
2. **Phase 2 — Design now / integrate after KhataIN IAM:** customer account, owner dashboard, staff admin, homepage CMS, lead analytics, uploads — fully specified here because the frontend already mocks every route.

Do **not** implement a separate Hajaro login/password/JWT/OTP system. Reuse KhataIN IAM (`/iam/*`). Do **not** expose unsecured administrative HTTP endpoints before IAM authorization is enforced.

---

## 2. Architecture alignment

### 2.1 Path prefix conventions

| Layer | Convention |
| --- | --- |
| Frontend live base | `NEXT_PUBLIC_API_URL` must include `/api/v1` (e.g. `https://host/api/v1`) |
| Frontend Hajaro paths | Relative paths start with `/hajaro/v1/...` (see `src/services/*.ts`) |
| Effective live URL | `{NEXT_PUBLIC_API_URL}/hajaro/v1/...` |
| Auth base | `NEXT_PUBLIC_AUTH_API_URL` (falls back to API URL) → `/iam/google`, `/iam/me`, `/iam/session/logout-current` |
| PDF / Nginx external | Proposed `/hajaro/api/v1/...` — configure Nginx to route this prefix to the same FastAPI routers (configurable `API_PREFIX`) |

**Canonical contract for frontend integration:** paths documented below as `/hajaro/v1/...` (relative to API base). Keep the prefix configurable so Hajaro can later mount inside KhataIN or run standalone.

### 2.2 Layering (PDF)

```
API routers  →  services  →  repositories  →  PostgreSQL/PostGIS (schema hajaro)
```

Suggested routers: `businesses`, `submissions`, `categories`, `locations`, `products`, `offers`, `search`, `maps`, `verification`, plus frontend-required: `account`, `owner`, `admin`, `home`, `uploads`, `leads`.

### 2.3 Shared response envelopes

**Pagination** (frontend `PageResult` + PDF):

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

PDF also allows:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 0,
    "total_pages": 0,
    "has_next": false
  }
}
```

**Frontend live mode expects the flat `PageResult` shape** (`items`, `total`, `page`, `page_size`). Implement that shape for all paginated public/owner list endpoints the frontend already calls. Optionally include `total_pages` / `has_next` as additional fields.

**Defaults:** `page=1`, `page_size=20` (search list UI uses `6`; map fetch may request up to `100`). Enforce a **maximum page_size** (recommend `100`). Deterministic ordering with stable ID/slug tie-breaker.

**Errors** (FastAPI-style, matching `src/services/api.ts`):

```json
{ "detail": "Human-readable message" }
```

| Status | When |
| --- | --- |
| `400` | Validation failure |
| `401` | Missing/invalid bearer session |
| `403` | Authenticated but wrong role/ownership |
| `404` | Resource not found / unknown route |
| `409` | Version conflict, synced catalog edit, duplicate |
| `422` | Pydantic validation (optional; frontend treats like 400) |
| `429` | Rate limit (submissions, claims, lead events, contact) |
| `500` | Unexpected server error |

### 2.4 Authentication & headers

| Header | Purpose |
| --- | --- |
| `Authorization: Bearer <token>` | KhataIN session (required on all non-`/public` Hajaro routes once IAM is live) |
| `X-Module` | Must match `NEXT_PUBLIC_API_MODULE` (default `HAJARO`) |
| `x-device-id` | Device correlation on auth calls |
| `X-Turnstile-Token` | Optional bot challenge on `/iam/google` |

**Roles used by frontend:**

| Role | Access |
| --- | --- |
| (anonymous) | Public discovery reads; public lead-events; public contact |
| `NORMAL_USER` | Customer account + merchant ownership (`owner_user_id`) |
| `HAJARO_ADMIN` | Staff admin queues (`/hajaro/v1/admin/*` except homepage) |
| `SUPER_ADMIN` / `SUPERADMIN` | Homepage CMS (`/hajaro/v1/admin/home`) |

Frontend route guards are **not** a security boundary. Every private endpoint must enforce authz server-side.

### 2.5 Publication vs verification (PDF §10)

| Concept | Question |
| --- | --- |
| Publication | Can this business appear in public search? |
| Verification | Which facts were independently confirmed? |

Publication statuses (`hajaro.businesses.publication_status`): `draft` · `pending_review` · `published` · `rejected` · `suspended` · `archived`.

**Only `published` businesses appear in public discovery.** A published business may still be unverified. Verification badges derive from `hajaro.business_verifications` grants — never a writable `is_verified` flag alone.

Frontend `Business.status` maps: `pending` ↔ `pending_review`; `published` ↔ `published`; etc.

### 2.6 Spatial rules (PDF §5, §15–16)

- Store points as `geography(Point,4326)` with GiST index.
- Construct with **longitude first, latitude second**.
- Nearby / radius filters require real coordinates; never invent distance.
- Map viewport: `bounds=south,west,north,east`; result limits + clustering at wide zoom.
- `city=nepal` (frontend) means nationwide published listings.
- Unknown municipality → empty page, never a “location unavailable” error.

---

## 3. Core database models (PDF §8) — implementation notes

| Table | Purpose | Indexes / notes |
| --- | --- | --- |
| `hajaro.locations` | Nepal admin + discovery geography | Unique slug per parent; type enum; optional point; active flag |
| `hajaro.categories` | Hierarchical categories | Parent FK; EN/NE names; not hardcoded in API |
| `hajaro.businesses` | Core listing | Unique `slug`; `location_id`; `geographic_point`; publication_status; GiST on point; FTS/trigram on name |
| `hajaro.business_categories` | M2M | Unique `(business_id, category_id)` |
| `hajaro.business_hours` | Weekly hours | Day + intervals; open-now in `Asia/Kathmandu` |
| `hajaro.business_media` | Photos | Object-storage URL refs; cover flag; display_order; max 12 public |
| `hajaro.catalog_items` | Products/services | `item_type`; `comparison_key`; brand; unit; is_published |
| `hajaro.public_prices` | NUMERIC amounts | `price_type`: fixed/from/estimated/on_request; availability; updated_at |
| `hajaro.offers` | Promotions | start/end UTC; publish rules; product associations |
| `hajaro.reviews` | Ratings | moderation_status; no anonymous create |
| `hajaro.business_submissions` | Registration inbox | submitted_data JSON; tracking token hash; rate-limit |
| `hajaro.business_claims` | Ownership claims | No auto-permission on approve until IAM ownership grant |
| `hajaro.verification_requests` | Verification workflow | Distinct verification_type |
| `hajaro.verification_events` | Append-only audit | Never overwrite history |
| `hajaro.business_verifications` | Active grants | Expiry + revocation |
| *(Phase 2)* `hajaro.saved_businesses`, `inquiries`, `lead_events`, `home_content`, `plan_requests`, `team_invites`, `holidays` | Account/merchant/CMS | Required by frontend mocks |

Frontend DTO field mapping highlights:

| Frontend `Business` field | DB / derivation |
| --- | --- |
| `slug`, `name`, `ne`, `description`, `descriptionNe` | businesses + localized columns or JSON |
| `phone`, `whatsapp`, `viber`, `lat`, `lng` | contacts + PostGIS |
| `category`, `area` | primary category slug + locality name |
| `city_slug`, `province_name`, `district_name`, `municipality_name`, `ward`, `address` | location join + address_line |
| `verified`, `pan_verified` | derived from verification grants |
| `rating`, `reviews`, `verified_reviews` | aggregates from published reviews |
| `products[]` | catalog_items + public_prices |
| `hours`, `photos` | business_hours / business_media |
| `open_now` | computed from hours + Asia/Kathmandu |
| `distance_km` | computed when `near` present |
| `owner_user_id`, `status`, `synced` | ownership + publication + KhataIN sync flag |

Price types frontend: `exact` | `from` | `on_request` ↔ PDF fixed / starting from / on request (map `estimated` if needed).

---

## 4. Frontend screen → API coverage matrix

| Frontend route / feature | Primary endpoints |
| --- | --- |
| `/`, home discovery | `GET /public/home`, `/public/categories`, `/public/locations`, `/public/location-tree`, `/public/businesses`, `/public/category-counts`, `/public/offers` |
| Location picker | `GET /public/location-tree` (+ Google Places client-side only) |
| `/search` list/grid/map | `GET /public/businesses` (+ filters); map may use `GET /map/businesses` |
| `/[city]`, `/[city]/[category]`, `/[city]/[category]/[area]` | search + category-counts + locations |
| `/categories` | categories + category-counts |
| `/offers` | `GET /public/offers` + search |
| `/compare` | `GET /public/product-comparison` |
| `/pricing` | `GET /public/plans` |
| `/contact` | `POST /public/contact` |
| `/b/[slug]` (+ products/reviews/photos/about/location) | business detail, products, reviews; `POST /public/lead-events` |
| Review / inquiry forms | `POST /businesses/{slug}/reviews`, `/inquiries` |
| Save shop | `POST/DELETE /account/saved/{slug}` |
| `/login`, `/logout` | `/iam/google`, `/iam/me`, `/iam/session/logout-current` |
| `/account/*` | account profile, saved, reviews, inquiries |
| `/business/add`, `/business/claim/[slug]` | `POST /businesses`, claim; uploads |
| `/dashboard/*` | owner businesses, profile, products, photos, hours, reviews reply, inquiries, leads, offers, team/plan/holidays |
| `/admin/*` | `admin/{listings,claims,reviews,reports,categories,locations,agents}` |
| `/admin/home` | admin home draft/publish |
| Sitemap / SEO | categories + published businesses |

---

## 5. Health & infrastructure

### 5.1 Health check

- **Route:** `GET /health` (or `{API_PREFIX}/health`)
- **Method:** `GET`
- **Access:** Public
- **Success `200`:**

```json
{
  "status": "ok",
  "database": "ok",
  "postgis": "3.x.x"
}
```

- **DB notes:** Verify PostgreSQL connectivity and `SELECT PostGIS_Version()`.

---

# Domain: Identity (KhataIN IAM — integrate, do not reimplement)

> Paths relative to `NEXT_PUBLIC_AUTH_API_URL`. Not part of Hajaro schema, but required for live frontend.

### IAM-1 — Google credential exchange

- **Route Path:** `POST /iam/google`
- **HTTP Method:** `POST`
- **Access Level:** Public (rate-limited; optional Turnstile)

**Request body:**

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `id_token` | string | yes | Google GIS ID token (`openid email profile`) |

**Success `200`:**

```json
{
  "status": "success",
  "user": {
    "id": "usr_01",
    "name": "Sita Sharma",
    "email": "sita@example.com",
    "avatar": "https://...",
    "roles": ["NORMAL_USER"],
    "phone": "9800000000",
    "language": "ne"
  },
  "access_token": "…",
  "session_token": "…",
  "session_id": 42
}
```

**Errors:** `400` invalid token · `403` when `status` is `2fa_required` / pending second factor (frontend must not create a session) · `429` rate limit.

**Business logic:** Existing KhataIN IAM only. Pending 2FA must not return a usable bearer session.

### IAM-2 — Current session user

- **Route Path:** `GET /iam/me`
- **HTTP Method:** `GET`
- **Access Level:** Protected (Bearer)
- **Success `200`:** `User` object as above.
- **Errors:** `401` expired/missing session.

### IAM-3 — Logout current session

- **Route Path:** `POST /iam/session/logout-current`
- **HTTP Method:** `POST`
- **Access Level:** Protected
- **Request body:** `{}`
- **Success `200`:** `{ "success": true }`

---

# Domain: Public Homepage CMS

### HOME-1 — Published homepage content

- **Route Path:** `GET /hajaro/v1/public/home`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Cache:** CDN/ISR friendly (`revalidate` 300s); invalidate on publish.

**Success `200`:** `HomeContent` (published only — never draft):

```json
{
  "version": 3,
  "brand_tagline": "Local Shops. Real Prices. Near You.",
  "banners": [{ "id": "b1", "title": { "en": "…", "ne": "…" }, "description": { "en": "…", "ne": "…" }, "href": "/ne/search", "tile": 1, "tone": "blue", "image_url": "https://…", "enabled": true }],
  "shortcuts": [{ "id": "s1", "label": { "en": "Hardware", "ne": "…" }, "icon": "Hammer", "category": "hardware", "color": "#e6eadd", "enabled": true }],
  "groups": [{ "id": "g1", "title": { "en": "Daily Needs", "ne": "…" }, "category": "grocery", "enabled": true, "cards": [{ "id": "c1", "label": { "en": "Cement", "ne": "…" }, "query": "cement", "tile": 2, "image_url": null }] }],
  "cities": [{ "id": "damak", "name": "Damak", "region": "Jhapa", "active": true, "tile": 1, "image_url": null }],
  "sections": [{ "id": "banners", "enabled": true, "title": { "en": "…", "ne": "…" }, "description": { "en": "…", "ne": "…" } }],
  "featured_businesses": ["damak-hardware"],
  "business_limit": 6,
  "product_limit": 8,
  "trust_items": [{ "id": "t1", "icon": "Shield", "title": { "en": "…", "ne": "…" }, "description": { "en": "…", "ne": "…" }, "color": "#0b3d2e" }],
  "ctas": {
    "app_title": { "en": "…", "ne": "…" },
    "app_description": { "en": "…", "ne": "…" },
    "owner_title": { "en": "…", "ne": "…" },
    "benefits": [{ "en": "…", "ne": "…" }],
    "button_label": { "en": "List your business", "ne": "…" }
  },
  "footer_description": { "en": "…", "ne": "…" },
  "updated_at": "2026-10-09T12:00:00Z"
}
```

**DB notes:** Persist draft + published JSON documents with optimistic `version`. Public endpoint returns published snapshot only.

### HOME-2 — Admin homepage draft (GET)

- **Route Path:** `GET /hajaro/v1/admin/home`
- **HTTP Method:** `GET`
- **Access Level:** Role-based — `SUPER_ADMIN` / `SUPERADMIN` only
- **Success `200`:**

```json
{
  "draft": { "...HomeContent": true },
  "published": { "...HomeContent": true },
  "published_at": "2026-10-09T12:00:00Z"
}
```

### HOME-3 — Save homepage draft

- **Route Path:** `PUT /hajaro/v1/admin/home`
- **HTTP Method:** `PUT`
- **Access Level:** Super-admin
- **Request body:** `{ "draft": HomeContent }` — client sends current `draft.version`
- **Success `200`:** Updated `HomeDraft` with `version` incremented and `updated_at` set.
- **Errors:** `400` validation · `403` · `409` if `draft.version` mismatch (“Another editor saved changes”).

### HOME-4 — Publish homepage

- **Route Path:** `POST /hajaro/v1/admin/home/publish`
- **HTTP Method:** `POST`
- **Access Level:** Super-admin
- **Request body:** `{ "version": 3 }`
- **Success `200`:** `HomeDraft` after copying draft → published.
- **Errors:** `409` version mismatch.

---

# Domain: Locations

### LOC-1 — Location tree (nationwide)

- **Route Path:** `GET /hajaro/v1/public/location-tree`
- **HTTP Method:** `GET`
- **Access Level:** Public

**Success `200`:** `LocationNode[]`

```json
[
  {
    "id": "np",
    "slug": "nepal",
    "type": "country",
    "parent_id": null,
    "name_en": "Nepal",
    "name_ne": "नेपाल",
    "status": "active",
    "lat": 28.3949,
    "lng": 84.1240,
    "business_count": 128
  },
  {
    "id": "koshi",
    "slug": "koshi",
    "type": "province",
    "parent_id": "np",
    "name_en": "Koshi",
    "name_ne": "कोशी",
    "status": "active",
    "business_count": 42
  }
]
```

**Types:** `country` | `province` | `district` | `municipality` | `city` | `ward` | `area`  
**Rules:** Zero-count nodes remain selectable. Counts = published businesses only. Official admin data from approved MoFAGA-aligned catalogue — do not invent official records. Support bilingual search.

**DB:** `hajaro.locations` hierarchy + aggregated counts (materialized view or cached count table recommended).

### LOC-2 — Areas / localities for a city scope

- **Route Path:** `GET /hajaro/v1/public/locations`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:**

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `city` | string | no | City/municipality slug; `nepal` = nationwide distinct areas |

**Success `200`:** `string[]` of locality/area names used by published businesses (frontend expects simple string array).

```json
["Damak Bazaar", "New Road", "Traffic Chowk"]
```

### LOC-3 — Admin locations CRUD

- **Route Path:** `GET|POST /hajaro/v1/admin/locations` · `PATCH|DELETE /hajaro/v1/admin/locations/{id}`
- **Access Level:** `HAJARO_ADMIN`
- **Request/response:** `Entry` rows (`id`, `name`, `status`, optional geo fields). Prefer writing into `hajaro.locations` rather than free-text area strings long-term.

---

# Domain: Categories

### CAT-1 — Category tree

- **Route Path:** `GET /hajaro/v1/public/categories`
- **HTTP Method:** `GET`
- **Access Level:** Public

**Success `200`:**

```json
[
  {
    "slug": "hardware",
    "en": "Hardware & Construction",
    "ne": "हार्डवेयर र निर्माण",
    "icon": "Hammer",
    "color": "#e6eadd",
    "parent_id": null
  },
  {
    "slug": "cement",
    "en": "Cement",
    "ne": "सिमेन्ट",
    "icon": "Package",
    "color": "#e6eadd",
    "parent_id": "hardware"
  }
]
```

**Seed (PDF §7):** Restaurants & Food, Hotels & Lodging, Hardware & Construction, Mobile & Electronics, Pharmacy & Health, Grocery & Wholesale, Auto & Bike, Clothing & Fashion, Furniture & Home, Electrical & Solar, Agriculture, Jewellery, Education, Beauty & Spa, Property & Real Estate, Repairs & Services, Wedding Services, Pet Supplies, Stationery & Printing — plus subcategories.

### CAT-2 — Category counts for a city scope

- **Route Path:** `GET /hajaro/v1/public/category-counts`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:** `city` (slug or `nepal`) — counts over **full** published dataset, not first page.

**Success `200`:**

```json
{ "hardware": 12, "pharmacy": 4, "grocery": 9, "cement": 3 }
```

### CAT-3 — Admin categories CRUD

- **Route Path:** `GET|POST /hajaro/v1/admin/categories` · `PATCH|DELETE /hajaro/v1/admin/categories/{id}`
- **Access Level:** `HAJARO_ADMIN`
- **POST body (Entry adapter):** `{ "name": "Hardware", "body": "हार्डवेयर", "category": "<parent_slug|null>", "status": "active" }`
- **DB:** Insert into `hajaro.categories`; slugify uniquely; prevent orphan deletes if businesses reference.

---

# Domain: Public Business Discovery & Search

### BIZ-1 — Search / list businesses

- **Route Path:** `GET /hajaro/v1/public/businesses`
- **HTTP Method:** `GET`
- **Access Level:** Public

**Query parameters (`SearchQuery`):**

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `q` | string | no | Keyword across business name (EN/NE), category labels, product/service names |
| `product_q` | string | no | Product facet text |
| `min_price` / `max_price` | number | no | Match quoted product price; **exclude** `on_request` |
| `category` | string | no | Category/subcategory slug |
| `city` | string | no | Municipality/city slug; `nepal` = nationwide |
| `province` | string | no | Province name/slug filter |
| `district` | string | no | District name/slug filter |
| `area` | string | no | Locality / bazaar / chowk |
| `near` | string | no | `lat,lng` |
| `radius_km` | number | no | Requires `near`; filter by PostGIS distance |
| `bounds` | string | no | `south,west,north,east` viewport |
| `place_id` / `place_name` | string | no | Google selection metadata only — **not** municipality IDs |
| `verified` | boolean | no | Has active verification grant |
| `open_now` | boolean | no | Computed Asia/Kathmandu |
| `has_prices` | boolean | no | Has non-on_request public price |
| `min_rating` | number | no | Minimum aggregate rating |
| `sort` | string | no | `relevance` (default) \| `rating` \| `distance` |
| `page` | int | no | Default 1 |
| `page_size` | int | no | Default 20; max 100 |

**Success `200`:**

```json
{
  "items": [
    {
      "slug": "damak-hardware",
      "name": "Damak Hardware",
      "ne": "दमक हार्डवेयर",
      "category": "hardware",
      "area": "Damak Bazaar",
      "description": "Cement, steel and tools.",
      "descriptionNe": "…",
      "image": "https://cdn.example/cover.jpg",
      "verified": true,
      "rating": 4.6,
      "reviews": 28,
      "verified_reviews": 12,
      "products": [],
      "phone": "9800000000",
      "whatsapp": "9800000000",
      "viber": null,
      "lat": 26.66,
      "lng": 87.693,
      "city_slug": "damak",
      "city_name_en": "Damak",
      "city_name_ne": "दमक",
      "province_name": "Koshi",
      "district_name": "Jhapa",
      "municipality_name": "Damak",
      "ward": 6,
      "address": "Near Traffic Chowk",
      "pan_verified": false,
      "open_now": true,
      "status": "published",
      "distance_km": 1.2
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 6
}
```

**Errors:** `400` invalid bounds/coords/page_size/radius.

**Business logic:** Apply all filters **before** totals/pagination. Published only. Full-text + trigram. GiST for geo. `city=nepal` = no city filter. Unknown city → empty page. Include `distance_km` only when `near` valid.

### BIZ-2 — Business detail

- **Route Path:** `GET /hajaro/v1/public/businesses/{slug}`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Path params:** `slug` (string, stable public slug)
- **Success `200`:** Full `Business` including `hours`, `photos`, `products` (or empty arrays).
- **Errors:** `404` if missing or not published.
- **DB:** Join categories, media, hours, aggregate rating; derive verification badges from grants.

### BIZ-3 — Public catalog (products)

- **Route Path:** `GET /hajaro/v1/public/businesses/{slug}/products`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:** `page`, `page_size`
- **Success `200`:** `PageResult<Product>`

```json
{
  "items": [
    {
      "id": "prd_01",
      "name": "OPC Cement 50kg",
      "ne": "OPC सिमेन्ट ५० केजी",
      "price": 1250,
      "unit": "bag",
      "stock": true,
      "price_type": "exact",
      "synced": false,
      "category": "cement",
      "comparison_key": "opc-cement-50kg",
      "updated_at": "2026-10-01T08:00:00Z"
    }
  ],
  "total": 18,
  "page": 1,
  "page_size": 20
}
```

**DB:** `catalog_items` + `public_prices` where `is_published` and business published. Currency NPR.

### BIZ-4 — Public reviews (read)

- **Route Path:** `GET /hajaro/v1/public/businesses/{slug}/reviews`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:**

| Param | Type | Description |
| --- | --- | --- |
| `page` / `page_size` | int | Pagination (UI often uses 6) |
| `verified` | boolean | `verification != none` when true |
| `rating` | int 1–5 | Exact star filter |
| `sort` | string | `newest` (default) \| `rating` |

**Success `200`:** `PageResult<Review>` — only `status=published`. Include `owner_reply` when present.

```json
{
  "items": [
    {
      "id": "rev_01",
      "business_slug": "damak-hardware",
      "user_id": "usr_c1",
      "author": "Ram B.",
      "rating": 5,
      "body": "Good cement stock and fair price.",
      "verification": "receipt",
      "status": "published",
      "owner_reply": "Thank you!",
      "receipt_url": null,
      "created_at": "2026-09-20T10:00:00Z"
    }
  ],
  "total": 28,
  "page": 1,
  "page_size": 6
}
```

### BIZ-5 — Public product search (PDF)

- **Route Path:** `GET /hajaro/v1/public/products`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:** Same geographic/keyword filters as search where applicable + `q`, pagination.
- **Success `200`:** Paginated catalog rows with embedded public business summary (for future product-first UX). Frontend currently uses comparison + business search; implement for PDF completeness.

### BIZ-6 — Product comparison

- **Route Path:** `GET /hajaro/v1/public/product-comparison`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:** `q` (required), `city`, `area`, `province`, `district`, `near`, `radius_km`, `available` (boolean)

**Success `200`:**

```json
{
  "query": "cement",
  "city_slug": "damak",
  "items": [
    {
      "business": { "slug": "damak-hardware", "name": "Damak Hardware", "lat": 26.66, "lng": 87.693, "distance_km": 0.8 },
      "product": { "id": "prd_01", "name": "OPC Cement 50kg", "price": 1250, "unit": "bag", "price_type": "exact", "stock": true, "comparison_key": "opc-cement-50kg" }
    }
  ]
}
```

**Rules:** Same geo scope as business search. Match `comparison_key` / brand / unit explicitly — never equate unlike units. Sort quoted prices ascending; `on_request` last. Bound results (frontend mock caps at 50); add pagination before large catalogs.

---

# Domain: Maps & Nearby (PDF §15–16)

### MAP-1 — Map viewport businesses

- **Route Path:** `GET /hajaro/v1/public/map/businesses`  
  *(PDF: `GET /map/businesses` under API prefix; expose as above for consistency)*
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:** Same filters as BIZ-1 plus required/strongly recommended `bounds=south,west,north,east`; `zoom` optional for clustering strategy; `limit` (default 100, max 200).

**Success `200`:**

```json
{
  "items": [
    {
      "id": "biz_uuid",
      "slug": "damak-hardware",
      "name": "Damak Hardware",
      "lat": 26.66,
      "lng": 87.693,
      "category": "hardware",
      "rating": 4.6,
      "verified": true,
      "image": "https://…"
    }
  ],
  "clusters": [
    { "lat": 26.67, "lng": 87.70, "count": 12, "bounds": [26.66, 87.69, 26.68, 87.71] }
  ],
  "mode": "markers"
}
```

**Rules:** Never return all Nepal businesses unbounded. At wide zoom return clusters. Respect published-only + search filters. Frontend today may call BIZ-1 with `page_size=100`; MAP-1 is the production-scale replacement.

### MAP-2 — Nearby search

- **Route Path:** Implemented via BIZ-1 query params `near` + `radius_km` (and/or dedicated alias `GET /hajaro/v1/public/businesses/nearby`).
- **Access:** Public
- **Logic:** `ST_DWithin` on `geography`; return `distance_km`; sort by distance when `sort=distance`.

---

# Domain: Offers

### OFF-1 — Public active offers

- **Route Path:** `GET /hajaro/v1/public/offers`
- **HTTP Method:** `GET`
- **Access Level:** Public
- **Query:** `business_slug?`, `city?`, `category?`

**Success `200`:** `Offer[]` — only offers where derived status is `active`, dates in range (UTC), parent business `published`, and not draft/paused.

```json
[
  {
    "id": "off_01",
    "business_slug": "damak-hardware",
    "title": "Monsoon cement deal",
    "title_ne": "…",
    "description": "…",
    "description_ne": "…",
    "category_slug": "cement",
    "product_ids": ["prd_01"],
    "regular_price": 1300,
    "offer_price": 1250,
    "starts_at": "2026-10-01T00:00:00+05:45",
    "ends_at": "2026-10-31T23:59:59+05:45",
    "terms": "While stocks last",
    "terms_ne": "…",
    "image_url": "https://…",
    "status": "active",
    "created_at": "2026-09-28T10:00:00Z",
    "updated_at": "2026-09-28T10:00:00Z",
    "views": 120,
    "contacts": 8
  }
]
```

**Status derivation:** `draft`/`paused` private; else `scheduled` before start, `expired` after end, `active` within window. Editor calendar dates in Asia/Kathmandu; store UTC.

### OFF-2 — Owner list offers

- **Route Path:** `GET /hajaro/v1/owner/businesses/{slug}/offers`
- **Access Level:** Protected — business owner (or staff with permission)
- **Success `200`:** All offers for business including draft/paused/expired.

### OFF-3 — Create offer

- **Route Path:** `POST /hajaro/v1/owner/businesses/{slug}/offers`
- **Access Level:** Owner
- **Request body (`OfferInput`):**

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| `title` / `title_ne` | string | yes | Length limits |
| `description` / `description_ne` | string | yes | Length limits |
| `category_slug` | string | yes | Must exist |
| `product_ids` | string[] | yes | Must belong to this business |
| `regular_price` | number | no | > 0 if set |
| `offer_price` | number | no | ≥ 0 and ≤ regular_price |
| `starts_at` / `ends_at` | ISO datetime | yes | `ends_at` > `starts_at` |
| `terms` / `terms_ne` | string | yes | |
| `image_url` | string | no | HTTPS object-storage URL only |
| `status` | enum | yes | `draft` \| `scheduled` \| `active` \| `paused` |

**Success `201`:** Full `Offer` with server `id`, timestamps, `views=0`, `contacts=0` (client cannot write metrics).

### OFF-4 — Update offer

- **Route Path:** `PUT /hajaro/v1/owner/businesses/{slug}/offers/{id}`
- **Access Level:** Owner of both business and offer
- **Success `200`:** Updated `Offer`
- **Errors:** `404` · `403` · `400` validation

### OFF-5 — Delete offer

- **Route Path:** `DELETE /hajaro/v1/owner/businesses/{slug}/offers/{id}`
- **Access Level:** Owner
- **Success `200`:** `{ "deleted": true }`

**DB:** `hajaro.offers` + offer↔product association table; attribute views/contacts via lead events where `source` references offer.

---

# Domain: Plans (marketing — public read)

### PLAN-1 — Public plans

- **Route Path:** `GET /hajaro/v1/public/plans`
- **HTTP Method:** `GET`
- **Access Level:** Public

**Success `200`:**

```json
[
  {
    "id": "free",
    "name": "Free listing",
    "price": 0,
    "features": ["Public storefront", "Products & prices", "Customer contacts"],
    "sponsored": false,
    "pricing_status": "approved",
    "category_slug": null
  },
  {
    "id": "featured",
    "name": "Featured visibility",
    "price": 0,
    "features": ["Sponsored placement (labelled)"],
    "sponsored": true,
    "pricing_status": "preview",
    "category_slug": null
  }
]
```

**Rules:** Unapproved prices display as “Pricing to be confirmed”. Sponsored independent of organic ranking/reviews. Payment not in Phase 1.

---

# Domain: Lead events & contact

### LEAD-1 — Track contact analytics

- **Route Path:** `POST /hajaro/v1/public/lead-events`
- **HTTP Method:** `POST`
- **Access Level:** Public (rate-limited; abuse controls)

**Request body:**

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `business_slug` | string | yes | Must exist & preferably published |
| `type` | enum | yes | `view` \| `call_click` \| `whatsapp_click` \| `viber_click` \| `direction_click` \| `inquiry` |
| `source` | string | yes | e.g. `web` |

**Success `202`:** `{ "accepted": true }`  
**Errors:** `400` unknown type · `404` business · `429` abuse

**Business logic:** Persist events for aggregation. Clicks ≠ completed calls/sales. Directions separate from inquiries. Deduplicate reasonably (IP/session windows). Feed owner `LeadSummary`.

### LEAD-2 — Site contact form

- **Route Path:** `POST /hajaro/v1/public/contact`
- **HTTP Method:** `POST`
- **Access Level:** Public (rate-limited)

**Request body:** `{ "name": string, "email": string, "message": string }` all required.  
**Success `202`:** `{ "accepted": true }`  
**Errors:** `400` incomplete fields.

---

# Domain: Business registration & claims (PDF §9, §12)

> PDF public paths: `POST /hajaro/api/v1/business-submissions` and `POST /businesses/{id}/claim-requests`.  
> Frontend currently calls authenticated `POST /hajaro/v1/businesses` and `POST /hajaro/v1/businesses/{slug}/claim`.  
> Implement **both** surfaces or alias them: public submission (tracking token, no owner grant) + authenticated create (sets `owner_user_id` pending publication).

### SUB-1 — Public business submission (PDF Phase 1)

- **Route Path:** `POST /hajaro/v1/public/business-submissions`  
  *(alias PDF: `/hajaro/api/v1/business-submissions`)*
- **HTTP Method:** `POST`
- **Access Level:** Public (rate-limited; spam/duplicate detection)

**Request body:**

| Field | Type | Required |
| --- | --- | --- |
| `name` | string | yes |
| `description` | string | no |
| `categories` | string[] | yes (≥1) |
| `phone` | string | yes |
| `whatsapp` | string | no |
| `email` | string | no |
| `address_line` / `address` | string | yes |
| `province_name` | string | yes |
| `district_name` | string | yes |
| `municipality_name` | string | yes |
| `ward` | int\|null | no |
| `locality` / `area` | string | yes |
| `lat` / `lng` | number | recommended |
| `contact_name` | string | yes |
| `pan` | string | no |
| `terms_accepted` | boolean | yes must be true |

**Success `201`:**

```json
{
  "id": "sub_01",
  "submission_status": "pending_review",
  "tracking_token": "unguessable-token",
  "created_at": "2026-10-16T04:00:00Z"
}
```

**Rules:** Enter `pending_review`. Do **not** create published business. Do not grant verified badge. Duplicate detection on phone+name+geo. Never expose private applicant data on public APIs.

**DB:** `hajaro.business_submissions`; store hashed tracking token.

### SUB-2 — Submission status by token

- **Route Path:** `GET /hajaro/v1/public/business-submissions/{token}/status`
- **HTTP Method:** `GET`
- **Access Level:** Public (token knowledge = authorization; unguessable tokens; no enumeration)

**Success `200`:**

```json
{
  "submission_status": "pending_review",
  "publication_status": null,
  "updated_at": "2026-10-16T04:00:00Z"
}
```

Never return reviewer notes or evidence files.

### SUB-3 — Authenticated listing create (frontend mock)

- **Route Path:** `POST /hajaro/v1/businesses`
- **HTTP Method:** `POST`
- **Access Level:** Protected (`NORMAL_USER`+)

**Request body (frontend):**

| Field | Required | Notes |
| --- | --- | --- |
| `name`, `category`, `area`, `phone` | yes | |
| `province_name`, `district_name`, `municipality_name` | yes | Nationwide — no city allowlist |
| `lat`, `lng` | yes | Finite; \|lat\|≤90, \|lng\|≤180 |
| `ne`, `description`, `ward`, `address`, `city_slug`, `city_name_en`, `photos[]` | no | |

**Success `201`:** `Business` with `status: "pending"` (`pending_review`), `owner_user_id` = current user, `verified: false`, empty products.  
**Errors:** `400` validation · `401`

### CLAIM-1 — Submit ownership claim

- **Route Path:** `POST /hajaro/v1/businesses/{slug}/claim`  
  *(PDF alias: `POST /hajaro/v1/businesses/{id}/claim-requests`)*
- **HTTP Method:** `POST`
- **Access Level:** Protected (or public with contact fields + tracking — prefer authenticated)

**Request body:** `{ "body": string (required evidence narrative), "phone"?: string, "url"?: string }`

**Success `201`:** `Entry` claim record `{ id, name, status: "pending", business_slug, user_id, body, phone, url, created_at }`

**Rules:** Does **not** grant editing access immediately. Approval later sets ownership only after identity verification (PDF). Store in `hajaro.business_claims`.

---

# Domain: Verification (PDF §10–11)

> Build models + services now. Applicant-facing status endpoints OK with tracking tokens. **Approvals are internal-only** until IAM staff roles are live — do not ship public approve endpoints.

### VER-1 — Request verification (design / post-IAM)

- **Route Path:** `POST /hajaro/v1/owner/businesses/{slug}/verification-requests`
- **Access Level:** Owner
- **Body:** `{ "verification_type": "contact"|"ownership"|"business"|"pan", "evidence_reference"?: string }`
- **Success `201`:** Request with status `pending`
- **DB:** `verification_requests` + append `verification_events`

### VER-2 — Track verification (token or owner)

- **Route Path:** `GET /hajaro/v1/public/verification-requests/{token}/status`  
  and/or `GET /hajaro/v1/owner/businesses/{slug}/verification-requests`
- **Access:** Token or owner
- **Success:** Status only — `not_requested` · `pending` · `under_review` · `additional_information_required` · `approved` · `rejected` · `expired` · `revoked`
- **Never expose** evidence binaries or reviewer notes publicly.

### VER-3 — Internal review operations

- **Route Path:** Internal service / staff-only admin tooling (not public until IAM)
- **Actions:** approve, reject, request more info, revoke, expire
- **On approve:** write `business_verifications` grant + event; public `verified` / type-specific badges derive from grants
- **On claim approve (admin):** may set `owner_user_id` **without** implying legal/PAN verification

---

# Domain: Reviews & inquiries (authenticated)

### REV-1 — Submit review

- **Route Path:** `POST /hajaro/v1/businesses/{slug}/reviews`
- **HTTP Method:** `POST`
- **Access Level:** Protected

**Request body:**

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `rating` | int | yes | 1–5 integer |
| `body` | string | yes | 10–2000 chars |
| `verification` | enum | yes | Phase 1 frontend sends `"none"` only |
| `receipt_url` | string | no | HTTPS upload; receipt alone ≠ verified badge |

**Success `201`:** Review with `status: "pending"`  
**Errors:** `400` · `401` · `404`

### REV-2 — Owner reply

- **Route Path:** `POST /hajaro/v1/owner/businesses/{slug}/reviews/{id}/reply`
- **Access Level:** Owner
- **Body:** `{ "body": string }` non-empty  
- **Success `200`:** Review with `owner_reply` set

### INQ-1 — Send inquiry

- **Route Path:** `POST /hajaro/v1/businesses/{slug}/inquiries`
- **Access Level:** Protected
- **Body:** `{ "message": string (10–2000), "phone_shared": boolean }`
- **Success `201`:** Inquiry `{ id, business_slug, user_id, message, phone_shared, status: "sent", created_at }`
- **Side effect:** Increment inquiry lead count

### INQ-2 — Owner list inquiries

- **Route Path:** `GET /hajaro/v1/owner/businesses/{slug}/inquiries`
- **Access Level:** Owner
- **Success `200`:** `Inquiry[]` (production should paginate)

### INQ-3 — Owner reply to inquiry

- **Route Path:** `POST /hajaro/v1/owner/businesses/{slug}/inquiries/{id}/reply`
- **Access Level:** Owner
- **Body:** `{ "reply": string }`
- **Success `200`:** Inquiry with `status: "replied"`

### RPT-1 — Report listing / content

- **Route Path:** `POST /hajaro/v1/reports`
- **Access Level:** Protected
- **Body:** `{ "body": string, "target_id"?: string }` (`target_id` = business slug)
- **Success `201`:** Report `Entry` with `status: "pending"`

---

# Domain: Customer account

### ACC-1 — Get / update profile

- **Route Path:** `GET /hajaro/v1/account/profile` · `PATCH /hajaro/v1/account/profile`
- **Access Level:** Protected
- **PATCH body:** `{ "name"?: string, "phone"?: string, "language"?: "en"|"ne" }`
- **Success `200`:** `User`
- **Errors:** `400` if name missing or language unsupported

### ACC-2 — Saved businesses

- **Route Path:**  
  - `GET /hajaro/v1/account/saved` → `Business[]`  
  - `POST /hajaro/v1/account/saved/{slug}` → `{ "saved": true }`  
  - `DELETE /hajaro/v1/account/saved/{slug}` → `{ "saved": false }`
- **Access Level:** Protected; isolation per user
- **Errors:** `404` unknown business

### ACC-3 — Own reviews

- **Route Path:**  
  - `GET /hajaro/v1/account/reviews` → `Review[]`  
  - `PATCH /hajaro/v1/account/reviews/{id}` body `{ body, rating }` → sets `status: "pending"` again  
  - `DELETE /hajaro/v1/account/reviews/{id}` → `{ "deleted": true }`
- **Access Level:** Protected — own reviews only

### ACC-4 — Own inquiries

- **Route Path:** `GET /hajaro/v1/account/inquiries`
- **Access Level:** Protected
- **Success `200`:** `Inquiry[]` for current user

---

# Domain: Owner / merchant dashboard

### OWN-1 — List owned businesses

- **Route Path:** `GET /hajaro/v1/owner/businesses`
- **Access Level:** Protected
- **Success `200`:** `Business[]` where `owner_user_id = current_user`
- **Frontend:** Multi-shop switcher (Damak owner, nationwide merchant)

### OWN-2 — Update profile

- **Route Path:** `PATCH /hajaro/v1/owner/businesses/{slug}`
- **Access Level:** Owner
- **Body (`ProfileUpdate`):** `name`, `area`, `description` required; optional `ne`, phones, `pan`, coords, Nepal address fields (`province_name`, `district_name`, `municipality_name`, `ward`, `address`, `city_slug`, `city_name_en`)
- **Success `200`:** Updated `Business`
- **Rules:** Validate coordinates; updating municipality may refresh `city_slug` / display names. No anonymous edit of published listings.

### OWN-3 — Lead summary

- **Route Path:** `GET /hajaro/v1/owner/businesses/{slug}/leads`
- **Access Level:** Owner
- **Success `200`:**

```json
{
  "views": 420,
  "calls": 38,
  "whatsapp": 51,
  "inquiries": 12,
  "directions": 22,
  "month": "2026-10",
  "daily": [{ "date": "2026-10-01", "views": 14 }],
  "recent": [{ "name": "Customer", "type": "call", "date": "2026-10-15" }]
}
```

Aggregate from `lead_events`. Label honestly — not unique customers or sales.

### OWN-4 — Hours

- **Route Path:** `GET /hajaro/v1/owner/businesses/{slug}/hours` · `PUT .../hours`
- **Access Level:** Owner
- **PUT body:** `Hour[7]` — `{ day: 0-6, open: "HH:MM", close: "HH:MM", closed: boolean }`
- **Errors:** `400` if not length 7
- **DB:** `business_hours`; open-now uses Asia/Kathmandu

### OWN-5 — Photos

- **Route Path:** `GET|PUT /hajaro/v1/owner/businesses/{slug}/photos`
- **Access Level:** Owner
- **PUT body:** `Photo[]` max 12 — `{ id, url, name }`
- **DB:** `business_media` ordered; HTTPS storage URLs only in production

### OWN-6 — Products CRUD

- **Route Path:**  
  - `POST /hajaro/v1/owner/businesses/{slug}/products`  
  - `PATCH .../products/{id}`  
  - `DELETE .../products/{id}`
- **Access Level:** Owner
- **Body:** `{ name, ne, price (≥0), unit, stock, price_type?, category?, comparison_key?, updated_at? }`
- **Success:** `201`/`200`/`{deleted:true}`
- **Errors:** `409` if `business.synced === true` (“Synced products must be edited in KhataIN.”)
- **DB:** `catalog_items` + `public_prices` (NUMERIC)

### OWN-7 — Team / plan / holidays entries

- **Route Path:** `GET|POST /hajaro/v1/owner/businesses/{slug}/{team|plan|holidays}` · `DELETE .../{id}`
- **Access Level:** Owner
- **POST body:** `{ "name": string, ...Entry fields }` → creates `status: "pending"` request (no payment/email send in Phase 1)
- **Success:** `Entry` / `{ deleted: true }`

---

# Domain: Uploads

### UP-1 — Authorize object-storage upload

- **Route Path:** `POST /hajaro/v1/uploads`
- **HTTP Method:** `POST`
- **Access Level:** Protected

**Request body:** `{ "name": string, "type": "image/jpeg"|"image/png"|"image/webp", "size": number }`  
**Validation:** type allowlist; `size ≤ 5_242_880` (5 MB)

**Success `200`:**

```json
{
  "upload_url": "https://storage.example/signed-put…",
  "public_url": "https://cdn.example/hajaro/…"
}
```

Client `PUT`s file bytes to `upload_url`. Never accept demo data-URLs as production assets. Scan/validate content server-side where possible. Receipt evidence needs retention/privacy controls.

---

# Domain: Staff administration

> Require `HAJARO_ADMIN`. Until KhataIN IAM is integrated, keep these behind internal tooling / tests — **do not** ship unsecured public admin HTTP. Contracts below match the frontend mock so live mode can connect when authz is ready.

All admin list endpoints currently return `Entry[]`. Production should add pagination (`page`, `page_size`, `total`) as datasets grow.

### ADM-1 — Listings

- **Route Path:** `GET|POST /hajaro/v1/admin/listings` · `PATCH|DELETE /hajaro/v1/admin/listings/{id}`
- **Access Level:** `HAJARO_ADMIN`
- **GET:** Map businesses → Entry (`id=slug`, status, category, area, phone, full Nepal address, lat/lng)
- **POST:** Field-agent create — requires name, category, area, province, district, municipality, valid lat/lng; `status: pending`; optional photo `url`
- **PATCH:** Update fields / `status` (`published`, `suspended`, …); if `target_id` set → **merge** listing into target (move reviews/inquiries/products, delete source)
- **DB:** Publication workflow on `businesses`; merge is transactional

### ADM-2 — Claims

- **Route Path:** `GET|POST|PATCH|DELETE /hajaro/v1/admin/claims[/{id}]`
- **Access Level:** Staff
- **On PATCH `status=approved`:** set `business.owner_user_id = claim.user_id` without auto-verification badge
- **DB:** `business_claims`

### ADM-3 — Reviews moderation

- **Route Path:** `GET|PATCH /hajaro/v1/admin/reviews[/{id}]`
- **Access Level:** Staff
- **PATCH body:** `{ "status": "published"|"hidden"|"flagged"|"pending" }`
- Only published reviews appear publicly

### ADM-4 — Reports

- **Route Path:** `GET|POST|PATCH|DELETE /hajaro/v1/admin/reports[/{id}]`
- **Access Level:** Staff
- Moderate customer reports queue

### ADM-5 — Categories / Locations / Agents

- **Route Path:** `/hajaro/v1/admin/{categories|locations|agents}` CRUD as in CAT-3 / LOC-3
- **Agents:** Field agent records (`Entry`: name, phone, email, status, area…)
- **Access Level:** Staff

---

# Domain: Standardized error catalog

| Code (HTTP) | Example `detail` | Typical cause |
| --- | --- | --- |
| 400 | `"Province, district and municipality are required."` | Registration validation |
| 400 | `"Choose 1–5 stars and write 10–2000 characters."` | Review validation |
| 400 | `"Set all seven days."` | Hours |
| 400 | `"Maximum 12 photos."` | Photos |
| 401 | `"Please sign in to continue."` | Missing bearer |
| 403 | `"You do not manage this business."` | Ownership |
| 403 | `"Staff access is required."` | Admin role |
| 403 | `"Only a super admin can manage homepage content."` | Homepage CMS |
| 404 | `"Business not found"` | Unknown/unpublished slug on public read |
| 409 | `"Synced products must be edited in KhataIN."` | Synced catalog |
| 409 | `"Another editor saved changes. Reload before saving."` | Home version |
| 429 | `"Too many requests. Try again later."` | Rate limit |
| 500 | `"Internal server error"` | Unhandled |

---

## 6. Security requirements (PDF §22) — checklist for implementers

- Public reads: published information only.
- Submissions/claims: rate-limit, validate, sanitize, duplicate detection, secure tracking tokens.
- No anonymous edit of published businesses.
- No public verification approvals or unprotected admin.
- No private applicant / evidence / reviewer notes on public APIs.
- Parameterized ORM queries; CORS allowlist; secrets in env.
- Do not expose local DB ports; do not touch production KhataIN without approval.
- Object storage: signed HTTPS URLs; validate MIME/size/bytes.

---

## 7. Implementation phases (mapped to PDF milestones)

| Milestone | Deliver endpoints |
| --- | --- |
| M1 Infrastructure | Health, DB/PostGIS, config, OpenAPI skeleton |
| M2 Core data | Locations seed, categories, business/hours/media/catalog/prices/offers models + seeds |
| M3 Public discovery | BIZ-1…6, CAT-*, LOC-*, OFF-1, MAP-*, PLAN-1, HOME-1, LEAD-1/2 |
| M4 Registration | SUB-*, CLAIM-1, publication workflow |
| M5 Verification | VER-* models/services + safe status tracking |
| M6 Integration/QA | Wire frontend live mode; tests; query optimization |
| Post-IAM | ACC-*, OWN-*, ADM-*, HOME-2…4, UP-1, REV/INQ writes already partially above |

---

## 8. Frontend live-mode cutover checklist

1. Implement all **Public** endpoints used by `directory.service.ts`, `discovery.service.ts`, `home.service.ts`, `businessService.plans/contact`.
2. Implement registration/claim/review/inquiry/report matching `workspace.service.ts` / `directory.service.ts`.
3. Confirm IAM Google/`me`/logout against real KhataIN.
4. Implement owner + admin surfaces with server-side role checks.
5. Configure `NEXT_PUBLIC_API_MODE=live`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_AUTH_API_URL`, module header agreement, CORS, storage CORS.
6. Rebuild Next.js (env embedded at build time).
7. Verify: home, search filters/map, business detail, comparison, offers, registration, claim, owner CRUD, staff queues, homepage publish.
8. Ensure production never serves mock businesses/reviews/metrics as real.

---

## 9. Endpoint index (complete)

### Public
| Method | Path |
| --- | --- |
| GET | `/hajaro/v1/public/home` |
| GET | `/hajaro/v1/public/categories` |
| GET | `/hajaro/v1/public/category-counts` |
| GET | `/hajaro/v1/public/locations` |
| GET | `/hajaro/v1/public/location-tree` |
| GET | `/hajaro/v1/public/plans` |
| GET | `/hajaro/v1/public/offers` |
| GET | `/hajaro/v1/public/product-comparison` |
| GET | `/hajaro/v1/public/products` |
| GET | `/hajaro/v1/public/businesses` |
| GET | `/hajaro/v1/public/businesses/{slug}` |
| GET | `/hajaro/v1/public/businesses/{slug}/products` |
| GET | `/hajaro/v1/public/businesses/{slug}/reviews` |
| GET | `/hajaro/v1/public/map/businesses` |
| POST | `/hajaro/v1/public/lead-events` |
| POST | `/hajaro/v1/public/contact` |
| POST | `/hajaro/v1/public/business-submissions` |
| GET | `/hajaro/v1/public/business-submissions/{token}/status` |
| GET | `/hajaro/v1/public/verification-requests/{token}/status` |

### Authenticated shared
| Method | Path |
| --- | --- |
| GET/PATCH | `/hajaro/v1/account/profile` |
| GET | `/hajaro/v1/account/saved` |
| POST/DELETE | `/hajaro/v1/account/saved/{slug}` |
| GET | `/hajaro/v1/account/reviews` |
| PATCH/DELETE | `/hajaro/v1/account/reviews/{id}` |
| GET | `/hajaro/v1/account/inquiries` |
| POST | `/hajaro/v1/businesses` |
| POST | `/hajaro/v1/businesses/{slug}/claim` |
| POST | `/hajaro/v1/businesses/{slug}/reviews` |
| POST | `/hajaro/v1/businesses/{slug}/inquiries` |
| POST | `/hajaro/v1/reports` |
| POST | `/hajaro/v1/uploads` |

### Owner
| Method | Path |
| --- | --- |
| GET | `/hajaro/v1/owner/businesses` |
| PATCH | `/hajaro/v1/owner/businesses/{slug}` |
| GET | `/hajaro/v1/owner/businesses/{slug}/leads` |
| GET/PUT | `/hajaro/v1/owner/businesses/{slug}/hours` |
| GET/PUT | `/hajaro/v1/owner/businesses/{slug}/photos` |
| POST/PATCH/DELETE | `/hajaro/v1/owner/businesses/{slug}/products[/{id}]` |
| POST | `/hajaro/v1/owner/businesses/{slug}/reviews/{id}/reply` |
| GET | `/hajaro/v1/owner/businesses/{slug}/inquiries` |
| POST | `/hajaro/v1/owner/businesses/{slug}/inquiries/{id}/reply` |
| GET/POST/DELETE | `/hajaro/v1/owner/businesses/{slug}/{team\|plan\|holidays}[/{id}]` |
| GET/POST | `/hajaro/v1/owner/businesses/{slug}/offers` |
| PUT/DELETE | `/hajaro/v1/owner/businesses/{slug}/offers/{id}` |
| POST/GET | `/hajaro/v1/owner/businesses/{slug}/verification-requests` |

### Admin
| Method | Path |
| --- | --- |
| GET/POST/PATCH/DELETE | `/hajaro/v1/admin/listings[/{id}]` |
| GET/POST/PATCH/DELETE | `/hajaro/v1/admin/claims[/{id}]` |
| GET/PATCH/DELETE | `/hajaro/v1/admin/reviews[/{id}]` |
| GET/POST/PATCH/DELETE | `/hajaro/v1/admin/reports[/{id}]` |
| GET/POST/PATCH/DELETE | `/hajaro/v1/admin/categories[/{id}]` |
| GET/POST/PATCH/DELETE | `/hajaro/v1/admin/locations[/{id}]` |
| GET/POST/PATCH/DELETE | `/hajaro/v1/admin/agents[/{id}]` |
| GET/PUT | `/hajaro/v1/admin/home` |
| POST | `/hajaro/v1/admin/home/publish` |

### IAM (external)
| Method | Path |
| --- | --- |
| POST | `/iam/google` |
| GET | `/iam/me` |
| POST | `/iam/session/logout-current` |

---

## 10. Final engineering principle

Build Hajaro as a clean, reusable PostgreSQL/PostGIS business-discovery backend for all Nepal. Reuse KhataIN authentication and production infrastructure later, but keep Hajaro domain logic, search, registration and verification independently maintainable. The first deliverable is a working, secure **public discovery** platform — not a second ERP.

**KhataIN runs the business. Hajaro brings the customers.**

---

*Generated for backend implementation from the Hajaro Next.js frontend mock surface and `HAJARO BACKEND INFRASTRUCTURE.pdf`. Payload field names match `src/types/api.ts` and `src/types/discovery.ts` unless noted as PDF-only extensions.*

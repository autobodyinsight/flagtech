# FlagTech / AutobodyOS

Shop-management app for a collision repair shop. It imports CCC and Mitchell estimates, then tracks the repair order through parts, technician hours, payments, a roadmap, and gross-profit reports.

The app is multi-shop. Each shop is a `domain`. An organization can own more than one shop. Requests only read and write rows for the signed-in shop.

## What was already here

- Email and password login with a session cookie. Passwords are bcrypt, and older SHA-256 hashes still verify and upgrade on the next login (the architect account is not rewritten).
- Shops, shop users, and roles Manager, Estimator, Tech, Receptionist, HR, and Support. Architect access comes from the `ARCHITECT_EMAIL` setting, not from a role stored on the user.
- CCC and Mitchell PDF import, review, and save into `saved_estimates`.
- Dashboard (current sales, average hours, average RO, total ROs, ROs per tech, repair-order table).
- Roadmap lanes: Arrived, Teardown, Auth, Parts, Body, Refinish, Reassy, Sublet, Wash/QC, Done.
- Parts ordering and receiving, technician roster, flag-out pay, and split insurance/customer payments.
- Closed-RO gross profit for parts and labor.
- Chat, setup, and an architect-only Manage screen.
- Red left sidebar and gray cards.

## What this change adds

- A new estimate page at `/ui/native-estimate`, opened from Estimates → + Estimate.
- VIN length, character, and check-digit checks. A bad check digit warns and still lets you continue.
- NHTSA vPIC decode for year, make, model, trim, body class, doors, drive, and engine. Every field stays editable. If the decoder is down, you type the vehicle in.
- Pencil-sketch front and rear views for 12 body styles, under `app/static/vehicles`. VIN decode picks the drawing. The body-style menu can override it, because a VIN cannot tell a swing-door SUV from a liftgate or a liftglass from a drop tailgate. The chosen variant is stored on the estimate. The older geometric SVG is used only if those images fail to load.
- Choosing a panel highlights that part in both views and opens a generic sub-part breakdown plus a line editor: operation, part name, part type, part number, quantity, price, body hours, refinish hours, mechanical hours, frame hours, and notes.
- Shop labor rates (body, refinish, mechanical, frame) and paint materials per refinish hour, stored in cents.
- Live totals. Money math for new estimates uses integer cents.
- Save, supplement/version, and convert to a repair order. Conversion writes the same `saved_estimates` shape an imported CCC estimate uses, so parts, hours, payments, the roadmap, and GP reports pick it up.
- Duplicate warning on import and on convert when the VIN matches, or the customer and vehicle match. Nothing is deleted. Confirm to save anyway.
- One-click assign of all unassigned body, paint, mechanical, or frame hours to a technician from the repair-order Tech tab.
- Organization row per shop, audit log, optional password reset, optional TOTP MFA, security headers, login rate limit, same-origin checks, health check, CSV report export, and text PDF printouts.
- Technician and Tech roles no longer see reports, payments, or dollar totals. Architect, Manager, Estimator, Receptionist, HR, Support, Owner, Admin, Accounting, and Front Office keep the access they already had. No migration updates `shop_users`.

## Licensed parts data

The parts list shipped here is a mock provider (`app/services/parts_catalog.py`). Part numbers that start with `MOCK-` are examples, not catalog prices.

Before you price real jobs from vehicle-specific data you need a license for:

- MOTOR / CCC estimating data, or the OEM parts and labor catalog you choose
- Any procedure, illustration, or part-number database from Mitchell, Audatex, or MOTOR

Plug a licensed provider in by implementing `PartsCatalogProvider.lookup` and returning it from `get_parts_catalog`. Do not copy those vendors' artwork into this repo.

NHTSA vPIC is free and only decodes the VIN. It is not a parts catalog.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
# edit DATABASE_URL and DATABASE_SSLMODE=disable for local Postgres
export $(grep -v '^#' .env | xargs)
python -m scripts.seed_demo          # optional, will not touch users
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 . The seed creates the Autobody Insight shop (`autobodyinsight.com`) only when that shop is missing, and a demo repair order only when that shop has no estimates.

Create users from Setup once a manager can sign in. On an empty database, `scripts/create_shop_user.py` inserts one user with the same columns Setup uses. It refuses to change an existing email and refuses the architect email. Put the password in `FLAGTECH_NEW_USER_PASSWORD`, not in git.

```bash
FLAGTECH_NEW_USER_EMAIL=person@autobodyinsight.com \
FLAGTECH_NEW_USER_ROLE=Manager \
FLAGTECH_NEW_USER_PASSWORD='set-a-long-password' \
python -m scripts.create_shop_user
```

## Tests

```bash
pytest -q
ruff check app/services/money.py app/services/vin.py app/services/estimate_math.py app/services/duplicates.py app/services/permissions.py tests
```

GitHub Actions runs that on push.

## Configuration

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Postgres connection string |
| `DATABASE_SSLMODE` | `require` on a host, `disable` for local Postgres without SSL |
| `ARCHITECT_EMAIL` | Account that keeps full architect access |
| `FLAGTECH_ENV` | `development` or `production` (production adds HSTS) |
| `FLAGTECH_RETURN_RESET_TOKEN` | Set to `1` only in local dev to see a reset token in the API |

Secrets stay in the environment. `.env.example` has placeholders only.

## Roles

| Role | Financials (GP, payments, sales dollars) |
| --- | --- |
| Architect | Yes. Not stored as a role and not edited by these changes. |
| Manager, Owner, Admin, HR, Support, Estimator, Receptionist, Accounting, Front Office | Yes. Same screens as before. |
| Tech, Technician | No. They still see the dashboard list, roadmap, parts, techs, and flag-out. |

## Backup and restore

```bash
pg_dump "$DATABASE_URL" --format=custom --file=flagtech.dump
# restore into an empty database you have already snapshotted
pg_restore --dbname "$DATABASE_URL" --clean --if-exists flagtech.dump
```

Take a dump before restore. Restore does not need to touch application code. The seed script will not overwrite users or existing repair orders.

## Deploy

`Dockerfile` runs gunicorn with uvicorn workers. `render.yaml` is the existing Render service. Set `DATABASE_URL`, `DATABASE_SSLMODE=require`, and `ARCHITECT_EMAIL` in the host's environment. Do not bake secrets into the image.

Health check: `GET /health`.

## API additions

- `POST /api/native-estimates/decode-vin`
- `GET /api/catalog/illustrations`, `/api/catalog/illustrations/{variant}`, `/api/catalog/areas`, `/api/catalog/diagram`, `/api/catalog/area-diagram`, `/api/catalog/parts`
- `GET` and `POST /api/shop/labor-rates`
- `GET` and `POST /api/native-estimates`, `POST /api/native-estimates/{id}/convert`, `POST /api/native-estimates/{id}/supplement`
- `POST /api/tech-assignment/quick`
- `GET /api/exports/reports.csv`, `/api/exports/native-estimates/{id}.pdf`, `/api/exports/ro/{ro}.pdf`
- `POST /api/auth/forgot-password`, `/api/auth/reset-password`
- `POST /api/auth/mfa/setup`, `/api/auth/mfa/enable`, `/api/auth/mfa/disable`

CCC import is still `POST /ui/grid` and `POST /ui/save-estimate`. A duplicate VIN or customer/vehicle returns HTTP 409 until the save is confirmed.

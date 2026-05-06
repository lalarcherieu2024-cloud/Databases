# Costuras de Paqui — Sewing Shop Management System

A Django + PostgreSQL management system for a sewing and tailoring shop, built
with the Django Unfold admin interface.

## Team & Module Ownership

| Member | Module | Models | Workflow |
|--------|--------|--------|----------|
| 1 | Customer | `Customer` | Workflow 1, Step 1 |
| 2 | Orders | `Order`, `OrderItem` | Workflow 1, Steps 2–6 + Workflow 3, Steps 1–3 |
| 3 | Garments & Materials | `Garment`, `Measurement`, `Material` | Workflow 1, Steps 3–5 |
| 4 | Production | `Employee`, `WorkTicket`, `ProductionLog` | Workflow 2 |
| 5 | Delivery & Docs | `Delivery` + ERD + Final Report | Workflow 3, Steps 4–6 |

## Setup (every member runs these once)

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd costuras_paqui
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
- For **PostgreSQL** (the project's main DB): fill in `DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.
- For **quick local testing without Postgres**: set `USE_SQLITE=True`.

### 3. Create the database (PostgreSQL only)

```bash
createdb costuras_paqui
# Or with psql:
# psql -U postgres -c "CREATE DATABASE costuras_paqui;"
```

### 4. Run migrations

```bash
python manage.py makemigrations shop
python manage.py migrate
```

### 5. Load demo data

```bash
python manage.py loaddata \
    shop/fixtures/01_customers.json \
    shop/fixtures/02_materials.json \
    shop/fixtures/03_employees.json \
    shop/fixtures/04_measurements.json \
    shop/fixtures/05_garments.json \
    shop/fixtures/06_orders.json \
    shop/fixtures/07_order_items.json \
    shop/fixtures/08_tickets.json \
    shop/fixtures/09_logs.json \
    shop/fixtures/10_deliveries.json
```

Expected output: `Installed 59 object(s) from 10 fixture(s)`.

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Run the server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ and log in.

## Critical rules to avoid breaking each other's work

These prevent the entire project from blowing up the day before submission:

1. **Only one person runs `makemigrations` after a merge to `develop`.** If two people push migration files numbered `0002_*`, you'll have a 30-minute conflict to fix. Coordinate in your group chat.

2. **Each member edits ONLY their assigned section** in `shop/models.py` and `shop/admin.py`. The sections are clearly marked with comment banners.

3. **Fixture loading order matters.** The numbered prefix (`01_`, `02_`, ...) reflects FK dependencies. Don't change the order. Don't reuse PKs across files.

4. **Branch per feature**: `feature/<member-name>-<task>` (e.g. `feature/ana-customer-admin`). Merge to `develop`, not `main`.

5. **Pull before you push.** `git pull --rebase origin develop` before every push.

## Day-by-day plan (3 days, 5 members)

### Day 1 — Whole team together
- All 5 clone and verify the baseline runs
- Run migrations and load fixtures together so everyone confirms it works on their machine
- Each member creates their feature branch
- Read the schema doc and confirm everyone understands their module

### Day 2 — Parallel module work
- Each member fills in their TODO sections in `admin.py`
- Each member can extend their fixtures (more demo data) if they want
- Member 5 starts the ERD (use [dbdiagram.io](https://dbdiagram.io)) and the final report

### Day 3 — Integration + submission
- Hours 0–2: full team integration test (run all 3 workflows in admin together)
- Hours 2–4: bug fixes and seed-data polish
- Hours 4–6: Member 5 finalizes the PDF report, demo rehearsal, submit

## Schema fixes vs original PDF

The original schema PDF contained three issues, fixed in `models.py`:

1. `WorkTicket.garment_type` was marked as Integer FK — corrected to a FK named `garment` pointing to `Garment`. The `garment_type` *string* lives on `Garment`, not the ticket.
2. `WorkTicket.instructions` was marked as TEXT FK — corrected to plain `TextField` (the FK marker was a typo).
3. The `GarmentMaterial` junction table was described in the relationships section but missing from the entities list. For v1, simplified to a plain `ManyToManyField` on `Garment.materials` (no through-table). Stretch goal: add a through-table with `meters_used` if time allows.

Member 5 updates the schema PDF with these corrections before submission.

## Project structure

```
costuras_paqui/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── costuras_paqui/             # project config
│   ├── settings.py             # Unfold pre-configured here
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── shop/                       # the single Django app
│   ├── models.py               # all 10 entities (sectioned by member)
│   ├── admin.py                # all admin (sectioned by member)
│   ├── apps.py
│   ├── migrations/
│   └── fixtures/               # demo data, numbered for load order
│       ├── 01_customers.json
│       ├── 02_materials.json
│       ├── 03_employees.json
│       ├── 04_measurements.json
│       ├── 05_garments.json
│       ├── 06_orders.json
│       ├── 07_order_items.json
│       ├── 08_tickets.json
│       ├── 09_logs.json
│       └── 10_deliveries.json
└── docs/                       # final report, ERD, workflow diagrams
```

## Useful commands cheatsheet

```bash
# Reset DB and reload everything (handy for testing)
rm db.sqlite3   # or drop+recreate the postgres DB
python manage.py migrate
python manage.py loaddata shop/fixtures/01_customers.json shop/fixtures/02_materials.json shop/fixtures/03_employees.json shop/fixtures/04_measurements.json shop/fixtures/05_garments.json shop/fixtures/06_orders.json shop/fixtures/07_order_items.json shop/fixtures/08_tickets.json shop/fixtures/09_logs.json shop/fixtures/10_deliveries.json

# Open Django shell to inspect data
python manage.py shell

# Check for issues without running the server
python manage.py check
```

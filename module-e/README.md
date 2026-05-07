# Costuras de Paqui — Taller de Costura

A Django-based management system for a sewing and tailoring shop. Built for the IE University Databases course.

## Overview

This application manages the full lifecycle of customer orders at Costuras de Paqui — from customer intake and measurements through production tracking and final delivery. It uses Django with PostgreSQL and Django Unfold for the admin interface.

## Team Members

| Module | Owner | Branch | Scope |
|--------|-------|--------|-------|
| A — Customer | — | `module-a-customers` | Customer model + admin |
| B — Orders | Luna | `feature/luna-orders` | Order, OrderItem models + admin |
| C — Garments & Materials | Sanad | `feature/sanad-garments` | Garment, Measurement, Material models |
| D — Production | Edard | `feature/edard-models` | Employee, WorkTicket, ProductionLog |
| E — Delivery + Docs | Owen | `feature/owen-delivery` | Delivery model, ERD, report, README |

## Tech Stack

- **Backend**: Django 5.x
- **Database**: PostgreSQL
- **Admin UI**: Django Unfold
- **ORM**: Django ORM
- **Python**: 3.11+

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/Databases.git
cd Databases
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create a database and user:

```sql
CREATE DATABASE costuras_paqui;
CREATE USER costuras_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE costuras_paqui TO costuras_user;
```

### 5. Configure environment

Copy `.env.example` to `.env` and fill in your database credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_NAME=costuras_paqui
DB_USER=costuras_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. (Optional) Load demo data

```bash
python manage.py seed_deliveries
```

### 9. Run the development server

```bash
python manage.py runserver
```

Then visit [http://localhost:8000/admin/](http://localhost:8000/admin/) and log in.

## Database Schema

The system consists of **11 entities** (10 main + 1 junction table) organized in Third Normal Form (3NF):

| Entity | Purpose |
|--------|---------|
| Customer | Client contact info and preferences |
| Order | Tracks orders with dates and status |
| OrderItem | Links an order to a garment with pricing |
| Garment | Describes each clothing item |
| Measurement | Body measurements for a garment (1:1 with Garment) |
| WorkTicket | Production task for a garment |
| Employee | Staff member info and role |
| ProductionLog | Records each production stage transition (audit trail) |
| Delivery | Tracks order delivery/pickup (1:1 with Order) |
| Material | Fabric and supply inventory |
| GarmentMaterial | Junction table for Garment ↔ Material (M:N) |

See `docs/erd.svg` and `docs/erd.mermaid` for the full Entity Relationship Diagram.

## Workflows

### Workflow 1: Customer Order Creation
1. Register or select a customer
2. Create a new order linked to the customer
3. Add garment items (OrderItem → Garment)
4. Record body measurements for each garment
5. Select materials from inventory
6. Confirm the order (status → 'confirmed')

### Workflow 2: Ticket Creation and Production Tracking
1. Generate work tickets for each garment
2. Assign tickets to employees by specialization
3. Move garments through stages: order_received → design_confirmed → cutting → sewing → finishing → quality_check
4. Log every stage transition in ProductionLog (immutable audit trail)
5. Handle rework if quality check fails
6. Mark as ready_for_delivery when passing QC

### Workflow 3: Order Completion and Delivery
1. Verify all tickets for the order are at ready_for_delivery
2. Final review of all garments against the original order
3. Mark order status as ready_for_delivery
4. **Create a Delivery record** — select method (pickup/courier/in_person), enter recipient name and any observations
5. **Confirm delivery** — when customer receives the order, set confirmed=True (via admin action or manual edit)
6. **Close the order** — order status changes to 'delivered', delivery date is recorded

## Project Structure

```
Databases/
├── costuras_paqui/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/                    # Main app
│   ├── models.py            # All models (Customer, Order, etc.)
│   ├── models_delivery.py   # Delivery model (Module E)
│   ├── admin.py             # Admin config for all models
│   ├── admin_delivery.py    # Delivery admin config (Module E)
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           └── seed_deliveries.py
├── docs/
│   ├── erd.svg              # Entity Relationship Diagram (image)
│   ├── erd.mermaid           # ERD source (Mermaid format)
│   └── report.md            # Final project report
├── requirements.txt
├── .env.example
├── manage.py
└── README.md
```

## Business Rules

1. Every order must belong to exactly one customer
2. An order can contain one or more garments (through OrderItem)
3. Each garment can generate one or more work tickets
4. Work tickets must always have a current production stage
5. Only active employees (is_active=True) can be assigned to new tickets
6. Completed orders should not remain in the active production queue
7. Delivered orders must have a delivery date and confirmation status recorded
8. Due dates are tracked so overdue orders can be flagged in the dashboard
9. Production log entries are immutable — they cannot be edited or deleted
10. An employee can work on multiple tickets, but each ticket has one assigned worker
11. Material stock levels should be updated when fabric is allocated to a garment
12. A garment's priority (normal, urgent, rush) determines its position in the production queue

## Status Values

| Entity | Possible Values |
|--------|----------------|
| Order status | received, confirmed, in_production, ready_for_delivery, delivered, cancelled |
| Garment status | pending, in_production, completed, on_hold |
| Ticket stage | order_received, design_confirmed, cutting, sewing, finishing, quality_check, ready_for_delivery, rework |
| Priority | normal, urgent, rush |
| Delivery method | pickup, courier, in_person |

## Git Workflow

We use a feature-branch workflow:

1. `main` — stable, production-ready code (do not push directly)
2. `develop` — integration branch where all feature branches merge
3. `feature/<name>` — individual module branches

To contribute:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature
# ... make changes ...
git add .
git commit -m "feat: description of changes"
git push origin feature/your-feature
# Then open a Pull Request to develop
```

## License

Academic project — IE University, Databases Course, 2026.

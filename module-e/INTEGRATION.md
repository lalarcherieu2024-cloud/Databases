# Module E — Integration Guide

This document explains how to integrate the Delivery model, ERD, documentation, and README into the existing project.

## Files in this module

```
shop/models_delivery.py      → Delivery Django model
shop/admin_delivery.py       → Delivery admin configuration (Django Unfold)
shop/migrations/XXXX_add_delivery_model.py  → Migration template (regenerate after integration)
management/commands/seed_deliveries.py      → Demo data seeder
docs/erd.svg                 → Entity Relationship Diagram (SVG image)
docs/erd.mermaid             → ERD source in Mermaid format
docs/report.md               → Final project report (all deliverables)
README.md                    → Project README (replaces existing or goes at root)
.env.example                 → Environment variable template
```

## Step-by-step integration

### Option A: Separate files (recommended for branch workflow)

1. **Copy `shop/models_delivery.py`** into your `shop/` directory.

2. **In `shop/models.py`**, add this import at the bottom:
   ```python
   from shop.models_delivery import Delivery  # Module E
   ```

3. **Copy `shop/admin_delivery.py`** into your `shop/` directory.

4. **In `shop/admin.py`**, add this import at the bottom:
   ```python
   import shop.admin_delivery  # Module E - registers Delivery admin
   ```

5. **Copy the `management/` directory** into `shop/`:
   ```
   shop/management/__init__.py
   shop/management/commands/__init__.py
   shop/management/commands/seed_deliveries.py
   ```

6. **Run migrations:**
   ```bash
   python manage.py makemigrations shop
   python manage.py migrate
   ```
   (Do NOT use the template migration file — let Django generate the real one.)

7. **Copy `docs/`** to the project root.

8. **Copy `README.md`** to the project root.

9. **Copy `.env.example`** to the project root.

### Option B: Merge directly into existing files

If you prefer to keep everything in single files:

1. Copy the `Delivery` class from `models_delivery.py` and paste it at the end of `shop/models.py`.

2. Copy the `DeliveryAdmin` class and `confirm_deliveries` action from `admin_delivery.py` and paste them at the end of `shop/admin.py`.

3. Run migrations as above.

## Adding to Django Unfold navigation

If the project uses a custom UNFOLD navigation in `settings.py`, add the Delivery link:

```python
{
    "title": "Delivery",
    "items": [
        {"title": "Deliveries", "link": "/admin/shop/delivery/", "icon": "local_shipping"},
    ],
},
```

## Testing

After integration:

```bash
# Check the model is registered
python manage.py shell -c "from shop.models_delivery import Delivery; print('Delivery model OK')"

# Check admin
python manage.py runserver
# Visit /admin/shop/delivery/

# Seed test data (requires existing orders with status 'ready_for_delivery')
python manage.py seed_deliveries
```

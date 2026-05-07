#!/bin/bash
# ============================================
# Module E — Branch Setup & Commit Script
# Run this from the root of your Databases repo
# ============================================

set -e

echo "=== Module E: Setting up branch ==="

# 1. Make sure we're on develop and up to date
git checkout develop
git pull origin develop

# 2. Create the feature branch
git checkout -b feature/owen-delivery

# 3. Copy Module E files into the project
# (Assumes you've extracted module-e/ next to this script)

# -- Delivery model
cp module-e/shop/models_delivery.py shop/models_delivery.py

# -- Delivery admin
cp module-e/shop/admin_delivery.py shop/admin_delivery.py

# -- Management command
mkdir -p shop/management/commands
touch shop/management/__init__.py
touch shop/management/commands/__init__.py
cp module-e/management/commands/seed_deliveries.py shop/management/commands/seed_deliveries.py

# -- Documentation
mkdir -p docs
cp module-e/docs/erd.svg docs/erd.svg
cp module-e/docs/erd.mermaid docs/erd.mermaid
cp module-e/docs/report.md docs/report.md

# -- Root files
cp module-e/README.md README.md
cp module-e/.env.example .env.example

# 4. Wire up imports in existing files
# Add Delivery import to models.py (if not already there)
if ! grep -q "models_delivery" shop/models.py 2>/dev/null; then
    echo "" >> shop/models.py
    echo "# Module E — Delivery" >> shop/models.py
    echo "from shop.models_delivery import Delivery" >> shop/models.py
    echo "Added Delivery import to shop/models.py"
fi

# Add Delivery admin import to admin.py (if not already there)
if ! grep -q "admin_delivery" shop/admin.py 2>/dev/null; then
    echo "" >> shop/admin.py
    echo "# Module E — Delivery admin" >> shop/admin.py
    echo "import shop.admin_delivery" >> shop/admin.py
    echo "Added Delivery admin import to shop/admin.py"
fi

# 5. Stage everything
git add -A

# 6. Commit
git commit -m "feat(module-e): add Delivery model, admin, ERD, docs, and README

Module E — Delivery + Documentation + ERD

- Added Delivery model (shop/models_delivery.py)
  - OneToOne with Order
  - Methods: confirm_delivery() for Workflow 3 Steps 5-6
  - Business rule validation (delivery_date required on confirm)

- Added Delivery admin (shop/admin_delivery.py)
  - Django Unfold integration
  - Bulk 'confirm deliveries' admin action
  - Search, filter, and list display configured

- Added management command: seed_deliveries

- Added ERD (docs/erd.svg + docs/erd.mermaid)
  - All 11 entities with attributes, keys, relationships

- Added project report (docs/report.md)
  - Problem description, requirements, normalized schema
  - All 3 workflows documented step by step
  - Business rules and status values

- Added README.md with setup instructions
- Added .env.example"

echo ""
echo "=== Done! ==="
echo "Now push to remote:"
echo "  git push -u origin feature/owen-delivery"
echo ""
echo "Then create a Pull Request to merge into develop (NOT main)."
echo ""
echo "After pushing, run migrations:"
echo "  python manage.py makemigrations shop"
echo "  python manage.py migrate"

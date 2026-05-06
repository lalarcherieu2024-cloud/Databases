# Day 2 — Per-Member Task Checklist

Each member has a set of **must-do** tasks (required for the rubric) and
**stretch goals** (nice if you have time). Focus on must-do first.

---

## Member 1 — Customer

**Files you own:** `shop/models.py` (Customer section), `shop/admin.py` (Customer section), `shop/fixtures/01_customers.json`

### Must-do
- [ ] Verify `Customer` model is complete in `models.py` (it already is)
- [ ] Enhance `CustomerAdmin` in `admin.py`:
  - Add a method `full_name(self, obj)` that returns `f"{obj.first_name} {obj.last_name}"` and put it in `list_display`
  - Make sure `search_fields` works (test by typing in the admin search box)
- [ ] Add 3–5 more customers to `01_customers.json` so the demo looks realistic
- [ ] Write 1 paragraph for the report describing **Workflow 1 Step 1**: registering / selecting a customer (give to Member 5)

### Stretch goals
- [ ] Add an inline on `CustomerAdmin` showing this customer's order history (read-only `TabularInline` of `Order`)
- [ ] Add a custom admin action: "Mark as VIP" (you'd need to add a `vip` BooleanField to Customer first)

---

## Member 2 — Orders

**Files you own:** `shop/models.py` (Order, OrderItem), `shop/admin.py` (Order section), `shop/fixtures/06_orders.json`, `shop/fixtures/07_order_items.json`

### Must-do
- [ ] Verify `Order` and `OrderItem` are complete in `models.py`
- [ ] Enhance `OrderAdmin`:
  - Confirm the `OrderItemInline` works (creating an order should let you add line items on the same page)
  - Add a custom admin action `mark_as_confirmed`: select orders, click action, sets `status='confirmed'` for all selected
  - Add a `total_items` method to `list_display` that returns `obj.items.count()`
- [ ] Add 2–3 more orders to the fixtures
- [ ] Write the report sections for **Workflow 1 Steps 2–6** and **Workflow 3 Steps 1–3** (give to Member 5)

### Stretch goals
- [ ] Override `Order.save()` to auto-calculate `total_price` from items (advanced — only if comfortable)
- [ ] Add a `is_overdue` property: `due_date < today and status != 'delivered'`. Show as a colored badge in `list_display`

---

## Member 3 — Garments & Materials

**Files you own:** `shop/models.py` (Garment, Measurement, Material sections), `shop/admin.py` (Garment section), fixtures 02, 04, 05

### Must-do
- [ ] Verify all three models are complete in `models.py`
- [ ] Enhance `GarmentAdmin`:
  - Confirm `filter_horizontal = ['materials']` works (M:N picker should be a dual-list widget)
  - Confirm `autocomplete_fields = ['measurement']` works
  - Add `list_filter` for `priority` and `garment_type`
- [ ] Enhance `MaterialAdmin`:
  - Add a method `low_stock(self, obj)` that returns `True` if `stock_meters < 5`, and add it to `list_display`
- [ ] Write the **normalization section (1NF/2NF/3NF)** of the report — you already have this content in the schema PDF; just polish it (give to Member 5)

### Stretch goals
- [ ] Build a `GarmentMaterial` through-table with a `meters_used` field. This means changing `Garment.materials` to use `through='GarmentMaterial'`. Coordinate with the team because it changes a migration. Only do this if Day 2 is ahead of schedule.

---

## Member 4 — Production

**Files you own:** `shop/models.py` (Employee, WorkTicket, ProductionLog), `shop/admin.py` (Production section), fixtures 03, 08, 09

### Must-do
- [ ] Verify all three models are complete in `models.py`
- [ ] Verify `WorkTicketAdmin.formfield_for_foreignkey` correctly limits `assigned_to` to active employees (test by creating a new ticket — the dropdown should only show 4 employees, not 5)
- [ ] Verify `ProductionLogAdmin` is read-only after creation (try editing a log — the fields should be greyed out)
- [ ] Add a custom admin action `advance_to_next_stage` on `WorkTicketAdmin`:
  - Define the stage order as a list
  - For each selected ticket, set `current_stage` to the next stage AND create a new `ProductionLog` row with `from_stage` = old, `to_stage` = new
- [ ] Write the report section for **Workflow 2** (full ticket lifecycle) (give to Member 5)

### Stretch goals
- [ ] Add validation: a ticket cannot move to `ready_for_delivery` without going through `quality_check` first
- [ ] Build a "rework" admin action that sets stage to `rework` and creates a log entry with a comment prompt

---

## Member 5 — Delivery + Documentation + ERD

**Files you own:** `shop/models.py` (Delivery), `shop/admin.py` (Delivery section), fixture 10, **all docs in `docs/`**, README

### Must-do
- [ ] Verify `Delivery` model and admin are complete
- [ ] **Draw the ERD** in [dbdiagram.io](https://dbdiagram.io) — all 10 entities with cardinalities, PKs, FKs. Export as PNG and save to `docs/erd.png`
- [ ] **Assemble the final report PDF** combining:
  - Problem description (write fresh, ~1 page)
  - Requirements description (~1 page)
  - Normalized database design (from Member 3's section + the schema PDF)
  - ERD image (your work)
  - Workflow 1, 2, 3 documentation (collected from Members 1, 2, 4)
  - Business rules (from the schema PDF)
- [ ] Update the README with the final setup instructions
- [ ] Test the full `loaddata` chain on a fresh database before submission

### Stretch goals
- [ ] Configure an Unfold dashboard widget showing pending/in-production/overdue order counts. Use `UNFOLD["DASHBOARD_CALLBACK"]` in `settings.py`. This is fiddly — only attempt if you have time.

---

## Daily standup format (15 min, end of each day)

Each person says:
1. What I finished today
2. What I'm blocked on (if anything)
3. What I'll do tomorrow

If anyone is blocked for >1 hour, post in the group chat immediately. Don't wait.

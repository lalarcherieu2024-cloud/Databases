# Costuras de Paqui — Final Project Report

**Course:** Databases  
**University:** IE University  
**Technologies:** Django, PostgreSQL, Django Unfold  

---

## 1. Problem Description

Costuras de Paqui is a sewing and tailoring shop (taller de costura) that needs a digital system to manage its daily operations. Currently, the shop handles customer orders, garment production, employee assignments, and deliveries using manual processes. This leads to missed deadlines, lost measurements, and difficulty tracking which garments are at which production stage.

**Scope:** The system covers the complete order lifecycle — from customer intake to final delivery — including customer management, order processing, garment specifications, material tracking, work ticket assignment, production stage tracking, and delivery confirmation.

**Intended users:** Paqui (shop owner) and her staff, who will interact with the system through the Django admin interface enhanced with Django Unfold.

---

## 2. Requirements Description

### Main Features

- **Customer Management:** Register customers, store contact details and preferences, access order history.
- **Order Management:** Create orders linked to customers, set due dates, add multiple garment items per order, track order status through its lifecycle.
- **Garment Details:** Record garment type, color, design notes, priority, and body measurements for each piece.
- **Material Tracking:** Maintain an inventory of fabrics and materials, allocate materials to garments with quantity tracking (M:N relationship).
- **Work Tickets:** Generate production tickets from confirmed orders, assign to employees by specialization, track through production stages.
- **Production Logging:** Immutable audit trail recording every stage transition with timestamps and employee attribution.
- **Delivery Management:** Record delivery method, recipient, and final observations. Confirm receipt and close orders.
- **Monitoring:** Filter and view pending, in-production, overdue, and completed orders through the admin dashboard.

### Business Rules

1. Every order must belong to exactly one customer.
2. An order can contain one or more garments (through OrderItem).
3. Each garment can generate one or more work tickets.
4. Work tickets must always have a current production stage.
5. Only active employees can be assigned to new tickets.
6. Completed orders should not remain in the active production queue.
7. Delivered orders must have a delivery date and confirmation status.
8. Due dates are tracked so overdue orders can be flagged.
9. Production log entries are immutable.
10. An employee can work on multiple tickets, but each ticket has one assigned worker.
11. Material stock levels should be updated when fabric is allocated.
12. A garment's priority (normal, urgent, rush) determines queue position.

---

## 3. Normalized Database Design

The database consists of 11 entities (10 main + 1 junction table) normalized to Third Normal Form (3NF).

### Normalization Decisions

**1NF:** All columns contain atomic values. When an order has multiple garments, each one is stored as a separate row in OrderItem rather than as a comma-separated list.

**2NF:** Every non-key attribute depends on the entire primary key. OrderItem acts as a junction between Order and Garment, so garment details are not duplicated inside the Order table.

**3NF:** There are no transitive dependencies. Measurement is its own table rather than being embedded in Garment. Employee data is referenced by foreign key in WorkTicket and ProductionLog instead of being duplicated.

**ProductionLog as audit trail:** Instead of updating a single status field on WorkTicket, we create a new row in ProductionLog for every transition, preserving the complete history.

**Garment–Material (M:N):** Since one garment can use multiple fabrics and one fabric can be used across many garments, we use a junction table (GarmentMaterial) with a meters_used column.

### Entity Definitions

#### Customer
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| phone | VARCHAR(20) | |
| email | VARCHAR(255) | |
| address | TEXT | |
| notes | TEXT | |
| created_at | DATETIME | |

#### Order
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| customer_id | INTEGER | FK → Customer |
| order_date | DATE | |
| due_date | DATE | |
| status | VARCHAR(30) | |
| total_price | DECIMAL(10,2) | |
| remarks | TEXT | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

#### OrderItem
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| order_id | INTEGER | FK → Order |
| garment_id | INTEGER | FK → Garment |
| quantity | INTEGER | |
| unit_price | DECIMAL(10,2) | |

#### Garment
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| garment_type | VARCHAR(50) | |
| color | VARCHAR(50) | |
| design_notes | TEXT | |
| priority | VARCHAR(20) | |
| status | VARCHAR(30) | |
| measurement_id | INTEGER | FK → Measurement |
| created_at | DATETIME | |

#### Measurement
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| bust | DECIMAL(6,2) | |
| waist | DECIMAL(6,2) | |
| hips | DECIMAL(6,2) | |
| shoulder_width | DECIMAL(6,2) | |
| sleeve_length | DECIMAL(6,2) | |
| inseam | DECIMAL(6,2) | |
| total_length | DECIMAL(6,2) | |
| extra_notes | TEXT | |

#### WorkTicket
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| garment_id | INTEGER | FK → Garment |
| assigned_to | INTEGER | FK → Employee |
| current_stage | VARCHAR(30) | |
| priority | VARCHAR(20) | |
| deadline | DATE | |
| instructions | TEXT | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

#### Employee
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| role | VARCHAR(50) | |
| phone | VARCHAR(20) | |
| specialization | VARCHAR(100) | |
| is_active | BOOLEAN | |

#### ProductionLog
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| ticket_id | INTEGER | FK → WorkTicket |
| performed_by | INTEGER | FK → Employee |
| from_stage | VARCHAR(30) | |
| to_stage | VARCHAR(30) | |
| comments | TEXT | |
| timestamp | DATETIME | |

#### Delivery
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| order_id | INTEGER | FK → Order |
| delivery_date | DATE | |
| method | VARCHAR(30) | |
| final_observations | TEXT | |
| recipient_name | VARCHAR(200) | |
| confirmed | BOOLEAN | |
| created_at | DATETIME | |

#### Material
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| name | VARCHAR(100) | |
| fabric_type | VARCHAR(50) | |
| color | VARCHAR(50) | |
| stock_meters | DECIMAL(8,2) | |
| price_per_meter | DECIMAL(8,2) | |

#### GarmentMaterial (Junction Table)
| Attribute | Type | Key |
|-----------|------|-----|
| id | INTEGER | PK |
| garment_id | INTEGER | FK → Garment |
| material_id | INTEGER | FK → Material |
| meters_used | DECIMAL(6,2) | |

### Relationships

| From | To | Cardinality | Description |
|------|----|-------------|-------------|
| Customer | Order | 1 : N | A customer can place many orders |
| Order | OrderItem | 1 : N | An order has one or more items |
| OrderItem | Garment | N : 1 | Each item references one garment |
| Garment | Measurement | 1 : 1 | Each garment has one set of measurements |
| Garment | WorkTicket | 1 : N | A garment can generate multiple tickets |
| WorkTicket | Employee | N : 1 | Each ticket is assigned to one worker |
| WorkTicket | ProductionLog | 1 : N | A ticket has many log entries |
| ProductionLog | Employee | N : 1 | Each log entry records who did it |
| Order | Delivery | 1 : 0..1 | An order may have one delivery record |
| Garment | Material | M : N | Garments can use multiple materials (via GarmentMaterial) |

---

## 4. ERD

See the file `docs/erd.svg` for the complete Entity Relationship Diagram showing all entities, relationships, cardinalities, primary keys, and foreign keys. A Mermaid source version is also available at `docs/erd.mermaid`.

---

## 5. Workflows

### Workflow 1: Customer Order Creation

**Step 1 — Register or select customer.** If the customer is new, the staff creates a new Customer record with their name, phone, email, and address. If returning, the staff searches and selects their existing record.

**Step 2 — Create a new order.** A new Order is created and linked to the selected customer. The staff enters the order date, due date, and any remarks. Status is automatically set to 'received'.

**Step 3 — Add garment items.** The staff adds one or more OrderItems to the order. Each item references a Garment record with garment type, color, priority, and design notes.

**Step 4 — Record measurements.** For each garment, a Measurement record is created with bust, waist, hips, shoulder width, sleeve length, inseam, and total length.

**Step 5 — Select materials.** The staff selects fabrics from the Material inventory. GarmentMaterial records track which materials are allocated and how many meters are needed.

**Step 6 — Confirm the order.** The order status changes from 'received' to 'confirmed', making it ready for production ticket generation.

### Workflow 2: Ticket Creation and Production Tracking

**Step 1 — Generate work tickets.** The system creates one WorkTicket per garment in the order, including garment reference, priority, deadline, and instructions.

**Step 2 — Assign to employee.** Each ticket is assigned to an employee based on role and specialization. Only active employees can receive assignments.

**Step 3 — Production stages.** The garment moves through: order_received → design_confirmed → cutting → sewing → finishing → quality_check.

**Step 4 — Log each transition.** Every stage change creates a new ProductionLog row recording old stage, new stage, who performed it, comments, and timestamp. These entries are immutable.

**Step 5 — Handle rework.** If quality check fails, the ticket can be sent back to a previous stage (marked 'rework') with a comment explaining the issue.

**Step 6 — Mark as ready.** When passing quality check, ticket status changes to 'ready_for_delivery' and the garment status to 'completed'.

### Workflow 3: Order Completion and Delivery

**Step 1 — Check all tickets.** Staff verifies every WorkTicket for the order has reached 'ready_for_delivery'. Incomplete tickets block order completion.

**Step 2 — Final review.** Staff checks all garments match the original order in type, color, quantity, and measurements.

**Step 3 — Mark order as completed.** Order status changes to 'ready_for_delivery'.

**Step 4 — Create delivery record.** A Delivery record is created with delivery method (pickup, courier, or in_person), recipient name, delivery date, and any final observations.

**Step 5 — Customer receives order.** When the customer picks up or receives their order, the Delivery.confirmed field is set to True. For pickups this happens at the shop; for courier deliveries the staff confirms by phone.

**Step 6 — Close the order.** Order status changes to 'delivered'. The delivery date is stored. The order now appears in the customer's order history.

---

## 6. Status Values Reference

| Entity | Possible Values |
|--------|----------------|
| Order status | received, confirmed, in_production, ready_for_delivery, delivered, cancelled |
| Garment status | pending, in_production, completed, on_hold |
| Ticket stage | order_received, design_confirmed, cutting, sewing, finishing, quality_check, ready_for_delivery, rework |
| Priority | normal, urgent, rush |
| Delivery method | pickup, courier, in_person |

# Module C - Normalization Notes (Garments & Materials)

This section explains how the `Garment`, `Measurement`, and `Material` design follows normalization principles and supports Workflow 1 (Steps 3-5).

## 1NF (First Normal Form)

- All fields store atomic values (single values per column).
- Multiple garments in one order are not stored in repeated columns; they are represented by separate rows in `OrderItem`.
- Material assignments are not stored as comma-separated text on garments; they are represented through a relational many-to-many association.

## 2NF (Second Normal Form)

- Attributes depend on the full key of their own table:
  - Garment-specific attributes (`garment_type`, `priority`, `status`, `design_notes`) live in `Garment`.
  - Measurement values (`bust`, `waist`, `hips`, etc.) live in `Measurement`.
  - Inventory attributes (`stock_meters`, `price_per_meter`, `fabric_type`) live in `Material`.
- No non-key attribute depends on only part of a composite key because entities use surrogate PKs and relationships are represented by FKs/M2M links.

## 3NF (Third Normal Form)

- No transitive dependencies are introduced across entities:
  - Measurement data is separated from garment descriptive data to avoid mixing body metrics with item metadata.
  - Material inventory data is centralized in `Material` and referenced by garments, which avoids duplicating stock and price values per garment.
- Shared reference data (priority/status choices) is standardized at the model level, reducing inconsistent values.

## Relationship Rationale

- `Garment` -> `Measurement` is modeled as one-to-one to represent one measurement profile per garment in this version.
- `Garment` <-> `Material` is many-to-many because one garment can use multiple materials and one material can be reused across many garments.
- This structure keeps the schema flexible for real sewing-shop scenarios while minimizing redundancy.

## Note for Future Iteration

If the team needs to track exact consumption per material, the many-to-many relation can be upgraded to an explicit through model (for example, `GarmentMaterial` with `meters_used`), without breaking the conceptual normalization approach.

# One-time migration: add blind-index columns and populate them for existing visitors.


from sqlalchemy import inspect, text

from app.database import SessionLocal, engine, Base
from app.models import User, Visitor, VisitRecord, AuditLog
from app.services.encryption import decrypt_field, blind_index

# Ensure base tables exist (won't ALTER existing tables, so columns are added below).
Base.metadata.create_all(bind=engine)

inspector = inspect(engine)
existing_cols = {c["name"] for c in inspector.get_columns("visitors")}

with engine.begin() as conn:
    if "phone_bidx" not in existing_cols:
        conn.execute(text("ALTER TABLE visitors ADD COLUMN phone_bidx VARCHAR(64)"))
        print("Added phone_bidx column.")
    if "id_number_bidx" not in existing_cols:
        conn.execute(text("ALTER TABLE visitors ADD COLUMN id_number_bidx VARCHAR(64)"))
        print("Added id_number_bidx column.")

db = SessionLocal()
visitors = db.query(Visitor).all()
updated = 0
for v in visitors:
    if v.phone:
        v.phone_bidx = blind_index(decrypt_field(v.phone))
    if v.id_number:
        v.id_number_bidx = blind_index(decrypt_field(v.id_number))
    updated += 1

db.commit()
db.close()
print(f"Backfilled blind index for {updated} visitor(s).")

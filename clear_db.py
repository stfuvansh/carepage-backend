from database import SessionLocal, Prescription

db = SessionLocal()

db.query(Prescription).delete()

db.commit()

db.close()

print("Database cleared successfully")
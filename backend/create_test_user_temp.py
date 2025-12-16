from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
try:
    user = User(
        email="test@cmeetrading.com",
        hashed_password=get_password_hash("Test@123456"),
        full_name="Test User",
        phone="0123456789",
        is_active=True,
        role="admin",
        is_verified=True,
        email_verified=True,
    )
    db.add(user)
    db.commit()
    print("✅ Test user created: test@cmeetrading.com / Test@123456")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()

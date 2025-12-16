#!/usr/bin/env python3
"""Script to create test user credentials"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserProfile
from app.models.user import Role
from app.core.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "test@cmeetrading.com").first()
        if existing:
            print("✅ Test user already exists")
            print(f"   Email: {existing.email}")
            role = db.query(Role).filter(Role.id == existing.role_id).first()
            print(f"   Role: {role.name if role else 'None'}")
            return True
        
        # Get admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            print("❌ Admin role not found. Please seed roles first.")
            return False
        
        # Create test user
        test_user = User(
            email="test@cmeetrading.com",
            password_hash=get_password_hash("Test@123456"),
            role_id=admin_role.id,
            status="active",
            email_verified=True,
            kyc_status="verified"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create user profile
        test_profile = UserProfile(
            user_id=test_user.id,
            full_name="Test User",
            display_name="Test User",
            phone="0123456789"
        )
        db.add(test_profile)
        db.commit()
        
        print("✅ Test user created")
        print("   Email: test@cmeetrading.com")
        print("   Password: Test@123456")
        print("   Role: admin")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("Creating Test User for CMEETRADING")
    print("="*60)
    create_test_user()

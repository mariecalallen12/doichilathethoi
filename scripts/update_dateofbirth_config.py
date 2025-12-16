#!/usr/bin/env python3
"""
Script để cập nhật dateOfBirth field trong registration config
Tắt field dateOfBirth (enabled = False)
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.system import SystemSetting
    
    # Database connection
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/digital_utopia'
    )
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        SETTING_KEY = "registration_fields"
        
        # Lấy config hiện tại
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == SETTING_KEY
        ).first()
        
        if not setting or not setting.value:
            print("❌ Không tìm thấy registration_fields config trong database")
            print("   Sử dụng default config...")
            sys.exit(1)
        
        config = setting.value
        fields = config.get('fields', [])
        
        print(f"📋 Tìm thấy {len(fields)} fields trong config")
        
        # Tìm và sửa dateOfBirth
        dateOfBirth_field = None
        for field in fields:
            if field.get('key') == 'dateOfBirth':
                dateOfBirth_field = field
                break
        
        if not dateOfBirth_field:
            print("❌ Không tìm thấy dateOfBirth field trong config")
            sys.exit(1)
        
        print(f"\n📝 dateOfBirth field trước khi sửa:")
        print(f"   - enabled: {dateOfBirth_field.get('enabled')}")
        print(f"   - required: {dateOfBirth_field.get('required')}")
        
        # Cập nhật
        dateOfBirth_field['enabled'] = False
        dateOfBirth_field['required'] = False
        
        print(f"\n✏️  dateOfBirth field sau khi sửa:")
        print(f"   - enabled: {dateOfBirth_field.get('enabled')}")
        print(f"   - required: {dateOfBirth_field.get('required')}")
        
        # Lưu lại vào database
        setting.value = config
        db.commit()
        db.refresh(setting)
        
        print("\n✅ Config đã được cập nhật trong database!")
        
        # Verify
        verify_setting = db.query(SystemSetting).filter(
            SystemSetting.key == SETTING_KEY
        ).first()
        verify_config = verify_setting.value
        verify_field = next((f for f in verify_config.get('fields', []) if f.get('key') == 'dateOfBirth'), None)
        
        if verify_field:
            print(f"\n🔍 Verified:")
            print(f"   - enabled: {verify_field.get('enabled')}")
            print(f"   - required: {verify_field.get('required')}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
        
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("   Cần chạy script này trong Docker container hoặc môi trường có cài đặt dependencies")
    print("\n   Cách 1: Chạy trong Docker container:")
    print("   docker exec -it digital_utopia_backend python3 /app/scripts/update_dateofbirth_config.py")
    print("\n   Cách 2: Sử dụng API endpoint để cập nhật")
    sys.exit(1)


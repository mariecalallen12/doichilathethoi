"""
Registration Fields Configuration Service
Lưu trữ và quản lý cấu hình các trường đăng ký
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Tuple
from ..models.system import SystemSetting

# Default registration fields configuration
DEFAULT_REGISTRATION_FIELDS = {
    "fields": [
        {
            "key": "fullName",
            "label": "Họ và Tên",
            "enabled": False,
            "required": False,
            "type": "text",
            "placeholder": "Nhập họ và tên đầy đủ"
        },
        {
            "key": "email",
            "label": "Email",
            "enabled": False,
            "required": False,
            "type": "email",
            "placeholder": "example@gmail.com"
        },
        {
            "key": "phone",
            "label": "Số Điện Thoại",
            "enabled": True,
            "required": True,
            "type": "tel",
            "placeholder": "+84 xxx xxx xxx"
        },
        {
            "key": "dateOfBirth",
            "label": "Ngày Sinh",
            "enabled": False,
            "required": False,
            "type": "date",
            "placeholder": ""
        },
        {
            "key": "password",
            "label": "Mật Khẩu",
            "enabled": True,
            "required": True,
            "type": "password",
            "placeholder": "Tối thiểu 8 ký tự"
        },
        {
            "key": "confirmPassword",
            "label": "Xác Nhận Mật Khẩu",
            "enabled": True,
            "required": True,
            "type": "password",
            "placeholder": "Nhập lại mật khẩu"
        },
        {
            "key": "country",
            "label": "Quốc Gia",
            "enabled": False,
            "required": False,
            "type": "select",
            "placeholder": "Chọn quốc gia",
            "default_value": "VN",
            "locked": True  # Không thể thay đổi từ admin
        },
        {
            "key": "tradingExperience",
            "label": "Kinh Nghiệm Giao Dịch",
            "enabled": False,
            "required": False,
            "type": "select",
            "placeholder": "Chọn mức độ kinh nghiệm",
            "default_value": "Chưa có kinh nghiệm",
            "locked": True  # Không thể thay đổi từ admin
        },
        {
            "key": "referralCode",
            "label": "Mã Giới Thiệu",
            "enabled": False,
            "required": False,
            "type": "text",
            "placeholder": "Nhập mã giới thiệu (nếu có)",
            "default_value": None,
            "locked": True  # Không thể thay đổi từ admin
        },
        {
            "key": "agreeTerms",
            "label": "Đồng ý điều khoản",
            "enabled": True,
            "required": True,
            "type": "checkbox",
            "placeholder": ""
        },
        {
            "key": "agreeMarketing",
            "label": "Đồng ý nhận marketing",
            "enabled": True,
            "required": False,
            "type": "checkbox",
            "placeholder": ""
        }
    ]
}

SETTING_KEY = "registration_fields"

# Default values for locked fields - không bao giờ thay đổi
LOCKED_FIELD_DEFAULTS = {
    "country": "VN",
    "tradingExperience": "Chưa có kinh nghiệm",
    "referralCode": None
}


def get_locked_field_default(field_key: str) -> Any:
    """
    Lấy giá trị mặc định cho các field bị khóa.
    Các giá trị này không bao giờ thay đổi và được set tự động ở backend.
    """
    return LOCKED_FIELD_DEFAULTS.get(field_key)


def _apply_field_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Force critical field visibility requirements regardless of stored config.
    Currently hides fullName/email so khách chỉ cần số điện thoại + mật khẩu.
    Also forces country, tradingExperience, referralCode to be disabled with default values.
    """
    fields = config.get("fields", [])
    for field in fields:
        if field.get("key") in ["fullName", "email"]:
            field["enabled"] = False
            field["required"] = False
        if field.get("key") in ["password", "phone"]:
            field["enabled"] = True
            field["required"] = True
        # Force disable và set default values cho các fields bị khóa
        if field.get("key") == "country":
            field["enabled"] = False
            field["required"] = False
            field["locked"] = True
            if "default_value" not in field:
                field["default_value"] = "VN"
        if field.get("key") == "tradingExperience":
            field["enabled"] = False
            field["required"] = False
            field["locked"] = True
            if "default_value" not in field:
                field["default_value"] = "Chưa có kinh nghiệm"
        if field.get("key") == "referralCode":
            field["enabled"] = False
            field["required"] = False
            field["locked"] = True
            if "default_value" not in field:
                field["default_value"] = None
    config["fields"] = fields
    return config


def get_registration_fields_config(db: Session = None) -> Dict[str, Any]:
    """
    Lấy cấu hình các trường đăng ký từ database
    Nếu không có trong DB, trả về default config
    Returns: Dict với 'fields', 'version', 'updated_at'
    """
    if db is None:
        from datetime import datetime
        return _apply_field_overrides({
            **DEFAULT_REGISTRATION_FIELDS,
            "version": 0,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    try:
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == SETTING_KEY
        ).first()
        
        if setting and setting.value:
            # Get version from updated_at timestamp
            version = int(setting.updated_at.timestamp() * 1000) if setting.updated_at else 0
            updated_at = setting.updated_at.isoformat() if setting.updated_at else None
            
            return _apply_field_overrides({
                **setting.value,
                "version": version,
                "updated_at": updated_at
            })
        
        # Return default with version
        from datetime import datetime
        return _apply_field_overrides({
            **DEFAULT_REGISTRATION_FIELDS,
            "version": 0,
            "updated_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Error getting registration fields config from DB: {e}")
        from datetime import datetime
        return {
            **DEFAULT_REGISTRATION_FIELDS,
            "version": 0,
            "updated_at": datetime.utcnow().isoformat()
        }


def save_registration_fields_config(config: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Lưu cấu hình các trường đăng ký vào database
    """
    try:
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == SETTING_KEY
        ).first()
        
        if setting:
            # Update existing setting
            setting.value = _apply_field_overrides(config)
            setting.is_public = True  # Allow client access
        else:
            # Create new setting
            setting = SystemSetting(
                key=SETTING_KEY,
                value=_apply_field_overrides(config),
                description="Cấu hình các trường đăng ký người dùng",
                is_public=True
            )
            db.add(setting)
        
        db.commit()
        db.refresh(setting)
        
        return setting.value
    except Exception as e:
        db.rollback()
        print(f"Error saving registration fields config to DB: {e}")
        raise


def validate_registration_fields_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate cấu hình các trường đăng ký
    Returns: (is_valid, error_message)
    """
    if "fields" not in config:
        return False, "Cấu hình phải có trường 'fields'"
    
    fields = config.get("fields", [])
    
    if not isinstance(fields, list):
        return False, "Trường 'fields' phải là một mảng"
    
    # Validate each field
    required_keys = ["key", "label", "enabled", "required", "type"]
    for field in fields:
        if not isinstance(field, dict):
            return False, "Mỗi field phải là một object"
        
        for key in required_keys:
            if key not in field:
                return False, f"Trường '{field.get('key', 'unknown')}' thiếu thuộc tính '{key}'"
        
        # Ensure core fields are not accidentally disabled
        if field["key"] in ["password", "phone"]:
            if not field.get("enabled", True):
                return False, f"Trường '{field['key']}' phải được bật"
            if not field.get("required", True):
                return False, f"Trường '{field['key']}' phải là bắt buộc"
            field["enabled"] = True
            field["required"] = True
        
        # Reject attempts to enable locked fields
        if field.get("locked", False) and field.get("enabled", False):
            return False, f"Trường '{field['key']}' đã bị khóa và không thể được bật"
    
    return True, ""


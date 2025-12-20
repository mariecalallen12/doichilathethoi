#!/usr/bin/env python3
"""
Payload Validator
Validate request payloads before sending to API
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class PayloadValidator:
    """Validate API request payloads"""
    
    def __init__(self, schemas_path: Optional[str] = None):
        """Initialize validator"""
        if schemas_path is None:
            schemas_path = Path(__file__).parent.parent / "test_data" / "payload_schemas.json"
        
        self.schemas_path = Path(schemas_path)
        self.schemas = {}
        
        if self.schemas_path.exists():
            with open(self.schemas_path, 'r') as f:
                self.schemas = json.load(f)
    
    def validate(self, endpoint: str, payload: Dict, method: str = "POST") -> Dict:
        """
        Validate payload for an endpoint
        
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "suggestions": List[str]
            }
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Try to find schema for this endpoint
        schema = self._find_schema(endpoint, method)
        
        if schema:
            # Validate against schema
            validation = self._validate_against_schema(payload, schema)
            result["errors"].extend(validation["errors"])
            result["warnings"].extend(validation["warnings"])
        else:
            # Generic validation
            result["warnings"].append(f"No schema found for {method} {endpoint}, performing generic validation")
            validation = self._generic_validation(payload, endpoint, method)
            result["errors"].extend(validation["errors"])
            result["warnings"].extend(validation["warnings"])
        
        result["valid"] = len(result["errors"]) == 0
        
        # Generate suggestions
        if result["errors"]:
            result["suggestions"].extend(self._generate_suggestions(result["errors"], endpoint))
        
        return result
    
    def _find_schema(self, endpoint: str, method: str) -> Optional[Dict]:
        """Find schema for endpoint"""
        # Try exact match
        key = f"{method.upper()}:{endpoint}"
        if key in self.schemas:
            return self.schemas[key]
        
        # Try pattern matching
        for schema_key, schema in self.schemas.items():
            if endpoint in schema_key or schema_key in endpoint:
                return schema
        
        return None
    
    def _validate_against_schema(self, payload: Dict, schema: Dict) -> Dict:
        """Validate payload against schema"""
        errors = []
        warnings = []
        
        required_fields = schema.get("required", [])
        fields = schema.get("fields", {})
        
        # Check required fields
        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types and formats
        for field, value in payload.items():
            if field in fields:
                field_spec = fields[field]
                field_type = field_spec.get("type")
                
                # Type validation
                if field_type == "string" and not isinstance(value, str):
                    errors.append(f"Field '{field}' should be string, got {type(value).__name__}")
                elif field_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' should be number, got {type(value).__name__}")
                elif field_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Field '{field}' should be boolean, got {type(value).__name__}")
                elif field_type == "object" and not isinstance(value, dict):
                    errors.append(f"Field '{field}' should be object, got {type(value).__name__}")
                elif field_type == "array" and not isinstance(value, list):
                    errors.append(f"Field '{field}' should be array, got {type(value).__name__}")
                
                # Format validation
                if "format" in field_spec:
                    format_type = field_spec["format"]
                    if format_type == "email" and "@" not in str(value):
                        errors.append(f"Field '{field}' should be a valid email")
                    elif format_type == "phone" and not str(value).startswith("+"):
                        warnings.append(f"Field '{field}' should start with '+' for phone number")
                
                # Min/Max validation
                if "min" in field_spec and isinstance(value, (int, float)):
                    if value < field_spec["min"]:
                        errors.append(f"Field '{field}' should be >= {field_spec['min']}")
                if "max" in field_spec and isinstance(value, (int, float)):
                    if value > field_spec["max"]:
                        errors.append(f"Field '{field}' should be <= {field_spec['max']}")
        
        return {"errors": errors, "warnings": warnings}
    
    def _generic_validation(self, payload: Dict, endpoint: str, method: str) -> Dict:
        """Generic validation when no schema is available"""
        errors = []
        warnings = []
        
        # Check for empty payload on POST/PUT
        if method in ["POST", "PUT", "PATCH"] and not payload:
            warnings.append("Empty payload for POST/PUT/PATCH request")
        
        # Check for common required fields based on endpoint
        if "/auth/register" in endpoint:
            if "email" not in payload and "phoneNumber" not in payload:
                errors.append("Registration requires email or phoneNumber")
            if "password" not in payload:
                errors.append("Registration requires password")
        elif "/auth/login" in endpoint:
            if "email" not in payload and "phone" not in payload:
                errors.append("Login requires email or phone")
            if "password" not in payload:
                errors.append("Login requires password")
        
        return {"errors": errors, "warnings": warnings}
    
    def _generate_suggestions(self, errors: List[str], endpoint: str) -> List[str]:
        """Generate suggestions based on errors"""
        suggestions = []
        
        for error in errors:
            if "Missing required field" in error:
                field = error.split(":")[-1].strip()
                suggestions.append(f"Add field '{field}' to payload")
            elif "should be" in error:
                suggestions.append(f"Check data type: {error}")
            elif "email" in error.lower():
                suggestions.append("Ensure email format is valid (e.g., user@example.com)")
            elif "password" in error.lower():
                suggestions.append("Ensure password meets requirements (min length, complexity)")
        
        return suggestions
    
    def validate_file(self, payload_file: str, endpoint: str, method: str = "POST") -> Dict:
        """Validate payload from file"""
        with open(payload_file, 'r') as f:
            payload = json.load(f)
        return self.validate(endpoint, payload, method)


if __name__ == "__main__":
    validator = PayloadValidator()
    
    # Test validation
    test_payload = {
        "email": "test@example.com",
        "password": "Test123!"
    }
    
    result = validator.validate("/api/auth/login", test_payload, "POST")
    print(json.dumps(result, indent=2))


#!/usr/bin/env python3
"""
API Validator
Validates API endpoints with schema validation, error handling, and performance checks
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIValidator:
    """Validate API endpoints with comprehensive checks"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.validation_results: List[Dict] = []
    
    def validate_response_schema(self, response_data: Any, expected_schema: Dict) -> Dict:
        """
        Validate response matches expected schema
        
        Args:
            response_data: Response data to validate
            expected_schema: Expected schema structure
            
        Returns:
            Validation result dictionary
        """
        errors = []
        
        if not isinstance(response_data, dict):
            return {
                "valid": False,
                "errors": ["Response is not a JSON object"]
            }
        
        # Check required fields
        required_fields = expected_schema.get("required", [])
        for field in required_fields:
            if field not in response_data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        field_types = expected_schema.get("properties", {})
        for field, expected_type in field_types.items():
            if field in response_data:
                actual_value = response_data[field]
                if not self._check_type(actual_value, expected_type):
                    errors.append(
                        f"Field '{field}' has wrong type. "
                        f"Expected {expected_type}, got {type(actual_value).__name__}"
                    )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if expected_python_type:
            if isinstance(expected_python_type, tuple):
                return isinstance(value, expected_python_type)
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, skip validation
    
    def validate_error_handling(self, endpoint: str, method: str = "GET",
                              invalid_data: Dict = None) -> Dict:
        """
        Test error handling for an endpoint
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            invalid_data: Invalid data to send (for POST/PUT)
            
        Returns:
            Validation result
        """
        url = f"{self.base_url}{endpoint}"
        method_func = getattr(requests, method.lower())
        
        start_time = time.time()
        try:
            if invalid_data and method.upper() in ["POST", "PUT", "PATCH"]:
                response = method_func(
                    url,
                    json=invalid_data,
                    timeout=self.timeout
                )
            else:
                response = method_func(url, timeout=self.timeout)
            
            response_time = time.time() - start_time
            
            # Check if error response is properly formatted
            is_error = response.status_code >= 400
            has_error_structure = False
            
            if is_error:
                try:
                    error_data = response.json()
                    # Check for common error response fields
                    has_error_structure = any(
                        key in error_data for key in ["error", "message", "detail"]
                    )
                except:
                    pass
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "is_error": is_error,
                "has_proper_error_structure": has_error_structure,
                "response_time": response_time,
                "valid": is_error and has_error_structure if is_error else True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.validation_results.append(result)
            return result
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": None,
                "error": str(e),
                "valid": False,
                "timestamp": datetime.now().isoformat()
            }
            self.validation_results.append(result)
            return result
    
    def check_performance(self, endpoint: str, method: str = "GET",
                         iterations: int = 5) -> Dict:
        """
        Check performance metrics for an endpoint
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            iterations: Number of requests to make
            
        Returns:
            Performance metrics
        """
        url = f"{self.base_url}{endpoint}"
        method_func = getattr(requests, method.lower())
        
        response_times = []
        success_count = 0
        
        for i in range(iterations):
            start_time = time.time()
            try:
                response = method_func(url, timeout=self.timeout)
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if 200 <= response.status_code < 300:
                    success_count += 1
            except Exception as e:
                logger.warning(f"Request {i+1} failed: {e}")
        
        if not response_times:
            return {
                "endpoint": endpoint,
                "method": method,
                "valid": False,
                "error": "All requests failed"
            }
        
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        # Performance thresholds (in seconds)
        excellent = avg_time < 0.5
        good = avg_time < 1.0
        acceptable = avg_time < 2.0
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "success_count": success_count,
            "success_rate": success_count / iterations,
            "average_response_time": avg_time,
            "min_response_time": min_time,
            "max_response_time": max_time,
            "performance_rating": (
                "excellent" if excellent else
                "good" if good else
                "acceptable" if acceptable else
                "poor"
            ),
            "valid": acceptable and success_count == iterations,
            "timestamp": datetime.now().isoformat()
        }
        
        self.validation_results.append(result)
        return result
    
    def validate_data_consistency(self, endpoint1: str, endpoint2: str,
                                 data_key: str) -> Dict:
        """
        Validate data consistency between two endpoints
        
        Args:
            endpoint1: First endpoint to compare
            endpoint2: Second endpoint to compare
            data_key: Key in response data to compare
            
        Returns:
            Consistency validation result
        """
        try:
            response1 = requests.get(f"{self.base_url}{endpoint1}", timeout=self.timeout)
            response2 = requests.get(f"{self.base_url}{endpoint2}", timeout=self.timeout)
            
            if response1.status_code != 200 or response2.status_code != 200:
                return {
                    "valid": False,
                    "error": "One or both endpoints returned error"
                }
            
            data1 = response1.json()
            data2 = response2.json()
            
            value1 = self._get_nested_value(data1, data_key)
            value2 = self._get_nested_value(data2, data_key)
            
            consistent = value1 == value2
            
            result = {
                "endpoint1": endpoint1,
                "endpoint2": endpoint2,
                "data_key": data_key,
                "value1": value1,
                "value2": value2,
                "consistent": consistent,
                "valid": consistent,
                "timestamp": datetime.now().isoformat()
            }
            
            self.validation_results.append(result)
            return result
            
        except Exception as e:
            result = {
                "endpoint1": endpoint1,
                "endpoint2": endpoint2,
                "valid": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.validation_results.append(result)
            return result
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
    
    def get_validation_summary(self) -> Dict:
        """Get summary of all validations"""
        total = len(self.validation_results)
        valid = sum(1 for r in self.validation_results if r.get("valid", False))
        invalid = total - valid
        
        return {
            "total_validations": total,
            "valid": valid,
            "invalid": invalid,
            "validity_rate": valid / total if total > 0 else 0
        }


if __name__ == "__main__":
    # Example usage
    validator = APIValidator("http://localhost:8000")
    
    # Test health endpoint performance
    validator.check_performance("/api/health", iterations=5)
    
    # Get summary
    summary = validator.get_validation_summary()
    print(f"Validations: {summary['total_validations']}")
    print(f"Valid: {summary['valid']}")
    print(f"Invalid: {summary['invalid']}")


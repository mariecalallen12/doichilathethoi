"""
Middleware Package
Authentication, rate limiting, and other middleware functions
"""

from .auth import (
    rate_limit,
    check_rate_limit,
    verify_token,
    get_current_user,
    get_current_user_optional,
    get_client_ip,
    extract_referral_token,
    revoke_refresh_token,
    send_email,
    authenticate_user,
    AuthenticationError,
    TokenValidationError,
    RateLimitError,
    get_error_message
)

__all__ = [
    # Middleware functions
    "rate_limit", "check_rate_limit", "verify_token",
    "get_current_user", "get_current_user_optional", "get_client_ip",
    "extract_referral_token", "revoke_refresh_token",
    "send_email", "get_error_message", "authenticate_user",
    # Exception classes
    "AuthenticationError", "TokenValidationError", "RateLimitError"
]

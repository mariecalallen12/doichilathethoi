"""
Two-Factor Authentication (TOTP) helper utilities.

Triển khai TOTP (RFC 6238) đơn giản để dùng chung cho 2FA.
"""

import base64
import hmac
import hashlib
import struct
import time
import secrets
from typing import Optional


def _normalize_base32(secret: str) -> bytes:
  """
  Chuẩn hóa và decode secret Base32 (không phân biệt hoa thường, bỏ padding).
  """
  s = secret.strip().replace(" ", "").upper()
  # Bù dấu '=' để chiều dài chia hết cho 8
  missing_padding = (-len(s)) % 8
  if missing_padding:
    s += "=" * missing_padding
  return base64.b32decode(s)


def generate_totp_secret(length: int = 20) -> str:
  """
  Tạo secret TOTP ở dạng Base32 (dùng cho Google Authenticator).
  """
  raw = secrets.token_bytes(length)
  return base64.b32encode(raw).decode("utf-8").rstrip("=")


def get_totp_token(
  secret: str,
  time_step: int = 30,
  digits: int = 6,
  for_time: Optional[float] = None,
) -> str:
  """
  Tính toán mã TOTP cho thời điểm cho trước.
  """
  if for_time is None:
    for_time = time.time()

  key = _normalize_base32(secret)
  counter = int(for_time // time_step)
  msg = struct.pack(">Q", counter)

  h = hmac.new(key, msg, hashlib.sha1).digest()
  offset = h[19] & 0x0F
  code_int = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF
  code = code_int % (10 ** digits)
  return f"{code:0{digits}d}"


def verify_totp(
  code: str,
  secret: str,
  window: int = 1,
  time_step: int = 30,
  digits: int = 6,
) -> bool:
  """
  Xác thực mã TOTP trong một khoảng thời gian cho phép (window ± 1 bước).
  """
  try:
    code = code.strip()
    if len(code) != digits or not code.isdigit():
      return False

    now = time.time()
    for offset in range(-window, window + 1):
      t = now + offset * time_step
      if get_totp_token(secret, time_step=time_step, digits=digits, for_time=t) == code:
        return True
  except Exception:
    return False

  return False


def build_otpauth_uri(secret: str, account_name: str, issuer: str = "CMEETRADING") -> str:
  """
  Tạo otpauth URI để dùng cho QR code với Google Authenticator.
  """
  label = f"{issuer}:{account_name}"
  return (
    f"otpauth://totp/{label}"
    f"?secret={secret}"
    f"&issuer={issuer}"
    f"&algorithm=SHA1&digits=6&period=30"
  )


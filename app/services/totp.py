"""Small TOTP helper (RFC 6238, SHA-1, 30 second step, 6 digits)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time


def generate_secret() -> str:
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def _normalize_secret(secret: str) -> bytes:
    padded = str(secret or "").strip().upper().replace(" ", "")
    padded += "=" * ((8 - len(padded) % 8) % 8)
    return base64.b32decode(padded, casefold=True)


def current_code(secret: str, for_time: int | None = None, step: int = 30) -> str:
    moment = int(for_time if for_time is not None else time.time())
    counter = int(moment // step)
    digest = hmac.new(_normalize_secret(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(binary % 1_000_000).zfill(6)


def verify_code(secret: str, code: str, for_time: int | None = None, window: int = 1) -> bool:
    candidate = "".join(ch for ch in str(code or "") if ch.isdigit())
    if len(candidate) != 6 or not secret:
        return False
    moment = int(for_time if for_time is not None else time.time())
    for offset in range(-window, window + 1):
        if hmac.compare_digest(current_code(secret, moment + offset * 30), candidate):
            return True
    return False


def provisioning_uri(secret: str, email: str, issuer: str = "FlagTech") -> str:
    label = f"{issuer}:{email}"
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer}&digits=6&period=30"

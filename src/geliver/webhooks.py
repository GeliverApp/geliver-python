from __future__ import annotations
from typing import Mapping, Optional


def verify_webhook(body: bytes, headers: Mapping[str, str], *, enable_verification: bool = False, secret: Optional[str] = None) -> bool:
    """Future-ready webhook verification.

    For now, verification is disabled by default and always returns True when disabled.
    When enabled in future versions, this will validate X-Signature and X-Timestamp headers.
    """
    if not enable_verification:
        return True
    signature = headers.get("x-signature") or headers.get("X-Signature")
    timestamp = headers.get("x-timestamp") or headers.get("X-Timestamp")
    if not signature or not timestamp or not secret:
        return False
    # Future: compute HMAC(secret, f"{timestamp}." + body) and compare
    return False


"""Dependency-free JWT decode/encode helpers (HMAC algorithms + 'none').

Implemented by hand with stdlib only (base64/json/hmac/hashlib) so this tool
has no extra dependency beyond what's already in requirements.txt.
"""
import base64
import hashlib
import hmac
import json

ALGORITHMS = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt(token: str):
    """Split & decode a JWT into (header, payload, signature_b64).
    Does NOT verify the signature — this is a decode-only inspection helper.
    """
    parts = token.strip().split(".")
    if len(parts) < 2:
        raise ValueError("Token must have at least a header and a payload segment")
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    signature = parts[2] if len(parts) > 2 else ""
    return header, payload, signature


def sign_jwt(header: dict, payload: dict, secret: str, algorithm: str = None) -> str:
    """Build and sign a new JWT from a header/payload dict pair."""
    header = dict(header)
    alg = (algorithm or header.get("alg") or "HS256").upper()
    header["alg"] = alg
    header.setdefault("typ", "JWT")

    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    if alg == "NONE":
        return f"{header_b64}.{payload_b64}."

    hash_fn = ALGORITHMS.get(alg)
    if hash_fn is None:
        raise ValueError(f"Unsupported algorithm: {alg} (supported: {', '.join(ALGORITHMS)}, none)")

    signature = hmac.new(secret.encode("utf-8"), signing_input, hash_fn).digest()
    return f"{header_b64}.{payload_b64}.{b64url_encode(signature)}"

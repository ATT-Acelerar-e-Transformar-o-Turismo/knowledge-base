import time
import httpx
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWKS_URL = "http://att-keycloak:7080/auth/realms/att/protocol/openid-connect/certs"
ALGORITHMS = ["RS256"]
JWKS_TTL = 300  # refresh JWKS every 5 minutes

_jwks_cache = None
_jwks_fetched_at = 0
security = HTTPBearer()


async def _get_jwks():
    global _jwks_cache, _jwks_fetched_at
    now = time.monotonic()
    if not _jwks_cache or (now - _jwks_fetched_at) > JWKS_TTL:
        async with httpx.AsyncClient() as client:
            resp = await client.get(JWKS_URL)
            resp.raise_for_status()
            _jwks_cache = resp.json()
            _jwks_fetched_at = now
    return _jwks_cache


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    try:
        jwks = await _get_jwks()
        payload = jwt.decode(
            token, jwks, algorithms=ALGORITHMS, options={"verify_aud": False}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    roles = payload.get("realm_access", {}).get("roles", [])
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return payload

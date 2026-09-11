#ID verification service
#waits for the verification API to be set via ID_VERIFICATION_API_URL
#if that var is empty the feature stays off, returns "not_configured" and never blocks registration or check-in

from datetime import datetime
from typing import Optional

from app.config import settings

#status values
STATUS_NOT_CONFIGURED = "not_configured"  # api var not set yet
STATUS_PENDING = "pending"                # api set but no final result yet
STATUS_VERIFIED = "verified"
STATUS_FAILED = "failed"
STATUS_ERROR = "error"                    # couldnt reach the provider


#only active once the api url is provided
def is_configured() -> bool:
    return bool(settings.ID_VERIFICATION_API_URL.strip())


#try to verify a visitor id, never raises, always returns a dict
def verify_id(
    id_type: Optional[str],
    id_number: Optional[str],
    full_name: Optional[str] = None,
) -> dict:
    now = datetime.utcnow().isoformat()

    #api not set yet so just skip and let the caller proceed
    if not is_configured():
        return {
            "status": STATUS_NOT_CONFIGURED,
            "provider": None,
            "detail": "ID verification API is not configured; skipping verification.",
            "checked_at": now,
        }

    #nothing to check against
    if not id_number:
        return {
            "status": STATUS_PENDING,
            "provider": settings.ID_VERIFICATION_API_URL,
            "detail": "No ID number supplied; verification pending.",
            "checked_at": now,
        }

    #api is set, call the provider
    #finish this bit once the real api contract is known, for now reach it and return pending instead of faking a verified state
    try:
        import httpx  # lazy import so the app runs without the dep until we actually need it

        headers = {}
        if settings.ID_VERIFICATION_API_KEY:
            headers["Authorization"] = f"Bearer {settings.ID_VERIFICATION_API_KEY}"

        payload = {
            "id_type": id_type,
            "id_number": id_number,
            "full_name": full_name,
        }

        with httpx.Client(timeout=settings.ID_VERIFICATION_TIMEOUT_SECONDS) as client:
            response = client.post(
                settings.ID_VERIFICATION_API_URL,
                json=payload,
                headers=headers,
            )

        if response.status_code >= 400:
            return {
                "status": STATUS_ERROR,
                "provider": settings.ID_VERIFICATION_API_URL,
                "detail": f"Verification provider returned HTTP {response.status_code}.",
                "checked_at": now,
            }

        #map the provider response
        #until the schema is final we treat a good call as pending so we never claim verified when we dont know
        data = {}
        try:
            data = response.json()
        except Exception:
            data = {}

        provider_status = str(data.get("status", "")).lower()
        if provider_status in (STATUS_VERIFIED, "approved", "match", "success"):
            resolved = STATUS_VERIFIED
        elif provider_status in (STATUS_FAILED, "rejected", "mismatch", "no_match"):
            resolved = STATUS_FAILED
        else:
            resolved = STATUS_PENDING

        return {
            "status": resolved,
            "provider": settings.ID_VERIFICATION_API_URL,
            "detail": data.get("detail", "Verification processed by provider."),
            "checked_at": now,
        }

    except Exception as exc:
        #dont let a verification hiccup break the caller
        return {
            "status": STATUS_ERROR,
            "provider": settings.ID_VERIFICATION_API_URL,
            "detail": f"Could not reach verification provider: {exc}",
            "checked_at": now,
        }

from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import json
import re
from datetime import datetime, timezone

initialize_app()

ALLOWED_ORIGINS = [
    "https://www.intonationlabs.com",
    "https://intonationlabs.com",
    "http://localhost:4321",
]

INQUIRY_TYPES = {"consulting", "workshop", "intonationai", "other"}


def _cors_headers(origin: str) -> dict[str, str]:
    allowed = origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]
    return {
        "Access-Control-Allow-Origin": allowed,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "86400",
    }


def _validate(data: dict) -> list[str]:
    errors = []
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()
    inquiry_type = (data.get("inquiry_type") or "").strip()

    if not name or len(name) < 2:
        errors.append("Name is required (min 2 characters).")
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("A valid email address is required.")
    if not message or len(message) < 10:
        errors.append("Message is required (min 10 characters).")
    if inquiry_type and inquiry_type not in INQUIRY_TYPES:
        errors.append(f"Invalid inquiry type. Must be one of: {', '.join(INQUIRY_TYPES)}")
    return errors


@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=ALLOWED_ORIGINS,
        cors_methods=["POST", "OPTIONS"],
    ),
    region="asia-southeast1",
    memory=options.MemoryOption.MB_256,
)
def contact_form(req: https_fn.Request) -> https_fn.Response:
    origin = req.headers.get("Origin", "")
    headers = _cors_headers(origin)

    if req.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    if req.method != "POST":
        return https_fn.Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            headers={**headers, "Content-Type": "application/json"},
        )

    try:
        data = req.get_json(silent=True) or {}
    except Exception:
        return https_fn.Response(
            json.dumps({"error": "Invalid JSON"}),
            status=400,
            headers={**headers, "Content-Type": "application/json"},
        )

    errors = _validate(data)
    if errors:
        return https_fn.Response(
            json.dumps({"error": "Validation failed", "details": errors}),
            status=422,
            headers={**headers, "Content-Type": "application/json"},
        )

    db = firestore.client()
    doc = {
        "name": data["name"].strip(),
        "email": data["email"].strip(),
        "company": (data.get("company") or "").strip(),
        "inquiry_type": (data.get("inquiry_type") or "other").strip(),
        "message": data["message"].strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "website_contact_form",
        "status": "new",
    }

    db.collection("leads").add(doc)

    return https_fn.Response(
        json.dumps({"success": True, "message": "Message received."}),
        status=200,
        headers={**headers, "Content-Type": "application/json"},
    )

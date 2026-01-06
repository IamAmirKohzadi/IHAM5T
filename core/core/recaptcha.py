import json
from urllib import parse, request

from django.conf import settings


def verify_recaptcha(token, remoteip=None):
    # Validate a reCAPTCHA token against Google's verify endpoint.
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not token:
        return False, "Please complete the CAPTCHA."
    if not secret:
        return False, "reCAPTCHA is not configured."

    payload = {"secret": secret, "response": token}
    if remoteip:
        payload["remoteip"] = remoteip

    try:
        data = parse.urlencode(payload).encode("utf-8")
        req = request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data,
            method="POST",
        )
        with request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
    except Exception:
        return False, "Could not verify CAPTCHA. Please try again."

    if result.get("success"):
        return True, ""
    return False, "Invalid CAPTCHA. Please try again."

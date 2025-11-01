import time
import hashlib
import hmac
import base64

SECRET_KEY = "scanno-secret"

def generate_token(username: str) -> str:
    timestamp = str(int(time.time()))
    raw = f"{username}:{timestamp}".encode()
    sig = hmac.new(SECRET_KEY.encode(), raw, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{username}:{timestamp}:{sig}".encode()).decode()

def verify_token(token: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        username, timestamp, sig = decoded.split(":")
        raw = f"{username}:{timestamp}".encode()
        valid_sig = hmac.new(SECRET_KEY.encode(), raw, hashlib.sha256).hexdigest()
        return hmac.compare_digest(valid_sig, sig)
    except Exception:
        return False

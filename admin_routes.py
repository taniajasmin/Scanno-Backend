from fastapi import APIRouter, HTTPException, Header
from utils.file_handler import read_admin_data, write_admin_data
from utils.auth import generate_token, verify_token
from openai import OpenAI

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login")
def admin_login(credentials: dict):
    data = read_admin_data()
    username = credentials.get("username")
    password = credentials.get("password")

    if username == data["admin_username"] and password == data["admin_password"]:
        token = generate_token(username)
        return {"message": "Login successful", "token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/key")
def get_current_key(authorization: str = Header(None)):
    if not authorization or not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = read_admin_data()
    key_preview = data["openai_api_key"][:8] + "..." if data["openai_api_key"] else "Not set"
    return {"current_key": key_preview}

@router.put("/key")
def update_api_key(update_data: dict, authorization: str = Header(None)):
    if not authorization or not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_key = update_data.get("new_key")
    if not new_key or not new_key.startswith("sk-"):
        raise HTTPException(status_code=400, detail="Invalid key format")

    data = read_admin_data()
    data["openai_api_key"] = new_key
    write_admin_data(data)

    try:
        client = OpenAI(api_key=new_key)
        client.models.list()  # simple validation
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or inactive API key")

    return {"message": "OpenAI key updated successfully"}


@router.get("/verify-token")
def verify_admin_token(authorization: str = Header(None)):
    if not authorization or not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Token is valid"}

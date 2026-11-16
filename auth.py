import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

USERNAME = os.environ.get("APP_USERNAME", "").strip()
PASSWORD = os.environ.get("APP_PASSWORD", "")

if not USERNAME or not PASSWORD or PASSWORD == "changeme":
    raise RuntimeError(
        "APP_USERNAME and APP_PASSWORD must be set to real values "
        "(the password cannot be empty or 'changeme'). Refusing to start."
    )


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    username = USERNAME
    password = PASSWORD
    ok_user = secrets.compare_digest(credentials.username.encode(), username.encode())
    ok_pass = secrets.compare_digest(credentials.password.encode(), password.encode())
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

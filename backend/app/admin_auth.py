from fastapi import Header, HTTPException
import os


def admin_auth(x_admin_token: str = Header(None)):
    admin_token = os.getenv("ADMIN_TOKEN")

    if not admin_token:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: ADMIN_TOKEN not set"
        )

    # Validate incoming token
    if x_admin_token != admin_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid admin token"
        )

    return True

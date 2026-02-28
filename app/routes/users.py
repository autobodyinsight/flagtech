from fastapi import APIRouter, HTTPException, Request

from app.services.auth import (
    ALLOWED_USER_ROLES,
    create_user,
    delete_user,
    list_users,
    normalize_email,
    update_user,
)

router = APIRouter()


@router.get("/users")
async def api_list_users(request: Request):
    return {"users": list_users(), "roles": list(ALLOWED_USER_ROLES)}


@router.post("/users")
async def api_create_user(request: Request):
    payload = await request.json()

    email = normalize_email(payload.get("email"))
    password = str(payload.get("password") or "")
    role = str(payload.get("role") or "user").strip().lower()

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    try:
        created = create_user(email=email, password=password, role=role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"ok": True, "user": created}


@router.patch("/users/{user_id}")
async def api_update_user(user_id: int, request: Request):
    payload = await request.json()

    email = payload.get("email")
    role = payload.get("role")
    password = payload.get("password")

    try:
        updated = update_user(
            user_id=user_id,
            email=normalize_email(email) if email else None,
            role=str(role).strip().lower() if role is not None else None,
            password=str(password) if password else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=404, detail="User not found or no changes applied")

    return {"ok": True, "user": updated}


@router.patch("/users/{user_id}/role")
async def api_assign_user_role(user_id: int, request: Request):
    payload = await request.json()

    role = str(payload.get("role") or "").strip().lower()
    if not role:
        raise HTTPException(status_code=400, detail="Role is required")

    try:
        updated = update_user(user_id=user_id, role=role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=404, detail="User not found or no changes applied")

    return {"ok": True, "user": updated}


@router.patch("/users/{user_id}/password")
async def api_reset_user_password(user_id: int, request: Request):
    payload = await request.json()

    password = str(payload.get("password") or "")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    try:
        updated = update_user(user_id=user_id, password=password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=404, detail="User not found or no changes applied")

    return {"ok": True, "user": updated}


@router.delete("/users/{user_id}")
async def api_delete_user(user_id: int, request: Request):
    deleted = delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "deleted": deleted}

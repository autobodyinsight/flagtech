"""Authentication routes for login and signup."""
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from app.services.auth import create_user, authenticate_user, store_session, get_session, delete_session

router = APIRouter()


@router.post("/signup")
async def signup(request: Request):
    """Create a new user account."""
    data = await request.json()
    
    email = data.get("email", "").strip()
    company_name = data.get("company_name", "").strip()
    password = data.get("password", "").strip()
    
    # Validate input
    if not email or not company_name or not password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "All fields are required"}
        )
    
    if len(password) < 6:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Password must be at least 6 characters"}
        )
    
    # Create user
    result = create_user(email, company_name, password)
    
    if not result["success"]:
        return JSONResponse(
            status_code=400,
            content=result
        )
    
    return JSONResponse(content=result)


@router.post("/login")
async def login(request: Request, response: Response):
    """Authenticate a user and create a session."""
    data = await request.json()
    
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    
    # Validate input
    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Email and password are required"}
        )
    
    # Authenticate user
    result = authenticate_user(email, password)
    
    if not result["success"]:
        return JSONResponse(
            status_code=401,
            content=result
        )
    
    # Store session with domain info
    store_session(result["token"], {
        "user_id": result["user"]["id"],
        "email": result["user"]["email"],
        "domain": result["user"]["domain"],
        "company_name": result["user"]["company_name"]
    })
    
    # Set session cookie on the response being returned
    json_response = JSONResponse(content=result)
    json_response.set_cookie(
        key="session_token",
        value=result["token"],
        httponly=True,
        max_age=86400 * 7,  # 7 days
        samesite="none",
        secure=True
    )
    
    return json_response


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Log out the current user."""
    token = request.cookies.get("session_token")
    if token:
        delete_session(token)
    response.delete_cookie("session_token")
    return JSONResponse(content={"success": True})


@router.get("/me")
async def get_current_user(request: Request):
    """Get the currently logged-in user."""
    token = request.cookies.get("session_token")
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Not authenticated"}
        )
    
    # Get user from session
    session_data = get_session(token)
    if not session_data:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Session expired"}
        )
    
    return JSONResponse(content={
        "success": True,
        "user": {
            "email": session_data["email"],
            "domain": session_data["domain"],
            "company_name": session_data["company_name"]
        }
    })

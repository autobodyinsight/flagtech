from fastapi import APIRouter

from .auth_routes import router as auth_router
from .parsing_routes import router as parsing_router
from .tech_routes import router as tech_router
from .vendor_routes import router as vendor_router
from .setup_manage_routes import router as setup_manage_router
from .chat_routes import router as chat_router
from .dashboard_routes import router as dashboard_router
from .payments_routes import router as payments_router
from .ro_routes import router as ro_router
from .misc_routes import router as misc_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(parsing_router)
router.include_router(tech_router)
router.include_router(vendor_router)
router.include_router(setup_manage_router)
router.include_router(chat_router)
router.include_router(dashboard_router)
router.include_router(payments_router)
router.include_router(ro_router)
router.include_router(misc_router)

from fastapi import APIRouter

from . import routes_all as impl


def build_partitioned_router(predicate):
    router = APIRouter()
    for route in impl.router.routes:
        path = str(getattr(route, "path", "") or "")
        if predicate(path):
            router.routes.append(route)
    return router

from __future__ import annotations

from typing import Iterable


ACCESS_ARCHITECT = "ARCHITECT"
ACCESS_MANAGER = "MANAGER"
ACCESS_HR = "HR"
ACCESS_USER = "USER"

ALL_ACCESS_LEVELS = (
    ACCESS_ARCHITECT,
    ACCESS_MANAGER,
    ACCESS_HR,
    ACCESS_USER,
)

ALL_WINDOW_FEATURES = (
    "main_ui",
    "dashboard",
    "upload",
    "phase",
    "parts",
    "tech",
    "flagout",
    "reports",
    "payments",
    "chat",
    "profile",
    "shop_context",
    "setup",
    "manage",
)

FEATURE_RULES: dict[str, tuple[str, ...]] = {
    "main_ui": ALL_ACCESS_LEVELS,
    "dashboard": ALL_ACCESS_LEVELS,
    "upload": ALL_ACCESS_LEVELS,
    "phase": ALL_ACCESS_LEVELS,
    "parts": ALL_ACCESS_LEVELS,
    "tech": ALL_ACCESS_LEVELS,
    "flagout": ALL_ACCESS_LEVELS,
    "reports": ALL_ACCESS_LEVELS,
    "payments": ALL_ACCESS_LEVELS,
    "chat": ALL_ACCESS_LEVELS,
    "profile": ALL_ACCESS_LEVELS,
    "shop_context": ALL_ACCESS_LEVELS,
    "setup": ALL_ACCESS_LEVELS,
    "manage": ALL_ACCESS_LEVELS,
}

ACTION_RULES: dict[str, tuple[str, ...]] = {
    "reset_profile_password": (ACCESS_ARCHITECT, ACCESS_MANAGER, ACCESS_HR),
}


def normalize_access_level(role: str | None, *, is_architect: bool = False) -> str:
    if is_architect:
        return ACCESS_ARCHITECT

    normalized_role = str(role or "").strip().lower()
    if normalized_role == "manager":
        return ACCESS_MANAGER
    if normalized_role == "hr":
        return ACCESS_HR
    return ACCESS_USER


def build_permission_snapshot(
    *,
    role: str | None,
    domain: str | None,
    shop_id: int | None,
    shop_uuid: str | None = None,
    user_uuid: str | None = None,
    is_architect: bool = False,
) -> dict:
    access_level = normalize_access_level(role, is_architect=is_architect)
    features = {
        feature: access_level in FEATURE_RULES.get(feature, ALL_ACCESS_LEVELS)
        for feature in ALL_WINDOW_FEATURES
    }
    actions = {
        action: access_level in ACTION_RULES.get(action, ALL_ACCESS_LEVELS)
        for action in ACTION_RULES
    }
    return {
        "access_level": access_level,
        "shop_domain": str(domain or "").strip().lower(),
        "shop_id": int(shop_id or 0) or None,
        "shop_uuid": str(shop_uuid or "").strip() or None,
        "user_uuid": str(user_uuid or "").strip() or None,
        "features": features,
        "actions": actions,
    }


def has_feature_access(snapshot: dict | None, feature: str | None) -> bool:
    if not feature:
        return True
    normalized_snapshot = snapshot or {}
    features = normalized_snapshot.get("features") or {}
    return bool(features.get(feature))


def has_action_access(snapshot: dict | None, action: str | None) -> bool:
    if not action:
        return True
    normalized_snapshot = snapshot or {}
    actions = normalized_snapshot.get("actions") or {}
    return bool(actions.get(action))


def allowed_access_levels_for_feature(feature: str) -> tuple[str, ...]:
    return FEATURE_RULES.get(feature, ALL_ACCESS_LEVELS)


def list_accessible_features(snapshot: dict | None) -> list[str]:
    normalized_snapshot = snapshot or {}
    features = normalized_snapshot.get("features") or {}
    return [feature for feature, allowed in features.items() if allowed]


def resolve_feature_for_path(path: str, method: str = "GET") -> str | None:
    normalized_path = str(path or "").strip().lower()
    normalized_method = str(method or "GET").strip().upper()

    if not normalized_path:
        return None

    if normalized_path == "/ui/manage" or normalized_path.startswith("/api/manage/"):
        return "manage"

    if normalized_path in {
        "/ui/legacy",
        "/ui/upload",
        "/ui/parse",
        "/ui/grid",
        "/ui/save-estimate",
        "/ui/auto-generate-ro",
        "/ui/aligned",
    }:
        return "upload"

    if normalized_path.startswith("/api/chat/"):
        return "chat"

    if normalized_path == "/api/dashboard-data":
        return "dashboard"

    if normalized_path.startswith("/api/phase/"):
        return "phase"

    if normalized_path.startswith("/api/parts/") or normalized_path.startswith("/api/vendors/"):
        return "parts"

    if (
        normalized_path.startswith("/api/techs/")
        or normalized_path.startswith("/api/ro-assignment")
        or normalized_path.startswith("/api/ro-assignments")
        or normalized_path.startswith("/api/tech-assignments")
        or normalized_path.startswith("/api/tech-assignment")
        or normalized_path.startswith("/api/ro-tech")
    ):
        return "tech"

    if (
        normalized_path.startswith("/api/flagout/")
        or normalized_path.startswith("/api/tech-flag-out")
    ):
        return "flagout"

    if normalized_path == "/api/reports_data" or normalized_path.startswith("/api/records/"):
        return "reports"

    if normalized_path.startswith("/api/payments/"):
        return "payments"

    if normalized_path == "/api/setup/shop":
        return "shop_context" if normalized_method == "GET" else "setup"

    if normalized_path == "/api/setup/context":
        return "shop_context"

    if (
        normalized_path.startswith("/api/setup/users")
        or (normalized_path == "/api/setup/shops" and normalized_method == "GET")
        or normalized_path.startswith("/api/setup/shops/")
        or normalized_path == "/api/setup/shops/delete"
    ):
        return "setup" if normalized_path.startswith("/api/setup/users") else "manage"

    if normalized_path.startswith("/ui/"):
        return "main_ui"

    return None


def can_access_any(snapshot: dict | None, features: Iterable[str]) -> bool:
    return any(has_feature_access(snapshot, feature) for feature in features)
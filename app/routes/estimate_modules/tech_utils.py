def _is_manager_or_hr_role(role: str | None) -> bool:
    normalized = str(role or "").strip().lower()
    return normalized in {"manager", "hr"}

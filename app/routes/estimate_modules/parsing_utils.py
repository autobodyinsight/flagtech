from datetime import date, datetime, timedelta, timezone
import math
import re


_TRAILING_PART_NUMBER_RE = re.compile(r"\b([A-Z0-9-]{6,})\s*$", re.IGNORECASE)


def _normalize_line_ids(values) -> set[int]:
    ids = set()
    if not isinstance(values, list):
        return ids
    for value in values:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        ids.add(parsed)
    return ids


def _alpha_only_description(value: str) -> str:
    tokens = re.split(r"\s+", str(value or "").strip())
    kept = []
    for token in tokens:
        cleaned = (token or "").strip().strip(",;:|()[]{}")
        if not cleaned:
            continue
        if any(ch.isdigit() for ch in cleaned):
            continue
        letters_only = re.sub(r"[^A-Za-z]", "", cleaned)
        if letters_only:
            kept.append(letters_only)
    return " ".join(kept)


def _serialize_datetime_for_client(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return value


def _extract_line_number(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return int(value)
        except Exception:
            return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    if not match:
        return None
    try:
        return int(match.group(0))
    except Exception:
        return None


def _coerce_number(value, default: float = 0.0) -> float:
    try:
        parsed = float(str(value).replace(",", "").strip())
        if math.isfinite(parsed):
            return parsed
    except Exception:
        pass
    return default


def _build_unified_estimate_lines(snapshot: dict | None) -> list[dict]:
    if not isinstance(snapshot, dict):
        return []

    sections = snapshot.get("sections")
    if not isinstance(sections, list):
        return []

    by_line: dict[int, dict] = {}
    order: list[int] = []

    def _get_or_create(line_number: int) -> dict:
        if line_number not in by_line:
            by_line[line_number] = {
                "lineNumber": line_number,
                "description": "",
                "labor": 0.0,
                "paint": 0.0,
                "qty": None,
                "partNumber": "",
                "extendedPrice": None,
            }
            order.append(line_number)
        return by_line[line_number]

    for section in sections:
        if not isinstance(section, dict):
            continue
        key = str(section.get("key") or "").strip().lower()
        items = section.get("items")
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            line_number = _extract_line_number(item.get("line") or item.get("lineNumber"))
            if line_number is None:
                continue

            record = _get_or_create(line_number)
            item_description = str(item.get("description") or "").strip()
            if item_description and not record.get("description"):
                record["description"] = item_description

            if key == "labor":
                record["labor"] = _coerce_number(item.get("value"), 0.0)
                continue

            if key == "paint":
                record["paint"] = _coerce_number(item.get("value"), 0.0)
                continue

            if key == "parts":
                qty_value = item.get("qty")
                if qty_value is not None and str(qty_value).strip() != "":
                    record["qty"] = _coerce_number(qty_value, 0.0)

                part_number = (
                    item.get("partNumber")
                    or item.get("part_number")
                    or item.get("part_no")
                    or item.get("part#")
                    or item.get("pn")
                    or ""
                )
                part_number = str(part_number or "").strip()
                if part_number:
                    record["partNumber"] = part_number

                price_value = item.get("extendedPrice")
                if price_value is None:
                    price_value = item.get("price")
                if price_value is not None and str(price_value).strip() != "":
                    record["extendedPrice"] = _coerce_number(price_value, 0.0)

    return [by_line[line_number] for line_number in sorted(order)]


def _parse_part_description_and_number(item: dict) -> tuple[str, str]:
    description = str(item.get("description") or "").strip()
    explicit_part_number = (
        item.get("part_number")
        or item.get("part_no")
        or item.get("part#")
        or item.get("pn")
        or ""
    )
    part_number = str(explicit_part_number or "").strip()

    def _clean_token(token: str) -> str:
        return (token or "").strip().strip(",;:|()[]{}")

    def _is_noise_token(token: str) -> bool:
        cleaned = _clean_token(token)
        if not cleaned:
            return True
        if re.fullmatch(r"\$?\d+(?:\.\d+)?", cleaned):
            return True
        if re.fullmatch(r"\d+(?:\.\d+)?(?:HRS?|HR)?", cleaned, re.IGNORECASE):
            return True
        if cleaned.lower() in {"qty", "incl", "incl.", "list", "price", "labor", "hrs", "hr", "ea", "each"}:
            return True
        return False

    def _is_part_number_token(token: str) -> bool:
        cleaned = _clean_token(token)
        if not re.fullmatch(r"[A-Z0-9-]{5,}", cleaned, re.IGNORECASE):
            return False
        has_alpha = any(ch.isalpha() for ch in cleaned)
        has_digit = any(ch.isdigit() for ch in cleaned)
        return has_alpha and has_digit

    tokens = description.split()
    kept_tokens = []
    for token in tokens:
        if _is_noise_token(token):
            continue
        if _is_part_number_token(token):
            if not part_number:
                part_number = _clean_token(token)
            continue
        kept_tokens.append(token)

    description = " ".join(kept_tokens).strip()

    if not part_number:
        trailing_match = _TRAILING_PART_NUMBER_RE.search(description)
        if trailing_match:
            candidate = _clean_token(trailing_match.group(1) or "")
            has_alpha = any(ch.isalpha() for ch in candidate)
            has_digit = any(ch.isdigit() for ch in candidate)
            if has_alpha and has_digit:
                part_number = candidate
                description = description[:trailing_match.start()].strip()

    description = re.sub(r"\s{2,}", " ", description).strip(" -|,;:")
    description = _alpha_only_description(description)
    return description, part_number


def _coerce_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return datetime.fromisoformat(cleaned).date()
        except Exception:
            return None
    return None


def _weekday_days_from_hours(hours: float) -> int:
    return max(0, math.ceil((hours / 4.0) + 3.0))


def _add_weekdays(start_date: date, weekday_days: int) -> date:
    if weekday_days <= 0:
        return start_date

    current = start_date
    added = 0
    while added < weekday_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def _calculate_ecd_date(in_date: date | None, hours: float) -> date | None:
    if in_date is None:
        return None
    return _add_weekdays(in_date, _weekday_days_from_hours(hours))


def _parse_owner_info(owner_info: str) -> tuple[str, str]:
    cleaned = (owner_info or "").strip()
    if not cleaned:
        return "", ""
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    if not lines:
        return "", ""
    name = lines[0]
    if re.fullmatch(r"\(?\d{3}\)?[\s\-]*\d{3}[\-\s]*\d{4}(?:\s*(?:cell|work|home|mobile))?", name, re.IGNORECASE):
        name = ""
    phone = lines[1] if len(lines) > 1 else ""
    if not phone and len(lines) > 0 and re.search(r"\(?\d{3}\)?[\s\-]*\d{3}[\-\s]*\d{4}", lines[0]):
        phone = lines[0]
    return name, phone


def _sum_hours(items) -> float:
    if not isinstance(items, list):
        return 0.0
    total = 0.0
    for item in items:
        if not isinstance(item, dict):
            continue
        total += _coerce_number(item.get("value"))
    return total


def _line_key(item: dict, index: int) -> str:
    line = item.get("line") if isinstance(item, dict) else None
    if line is None or line == "":
        return str(index + 1)
    return str(line)


def _normalize_repair_type(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized == "labor":
        return "body"
    if normalized in {"body", "paint", "mech", "frame"}:
        return normalized
    return "body"

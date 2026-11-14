"""Pick a pencil-sketch illustration pair from NHTSA vPIC fields.

Rules live in app/static/vehicles/mapping.json, the same file CJ approved
with the drawings. vPIC cannot tell a liftgate from a drop tailgate or from
swing-out rear doors, so those two variants are manual choices.
"""

from __future__ import annotations

import json
from functools import lru_cache
from html import escape
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parents[1] / "static" / "vehicles"
STATIC_URL = "/static/vehicles"


@lru_cache(maxsize=1)
def mapping() -> dict:
    return json.loads((ASSET_DIR / "mapping.json").read_text(encoding="utf-8"))


def _as_int(value) -> int | None:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def is_dually(record: dict) -> bool:
    signals = mapping()["dually_signals"]
    wheels = _as_int(record.get("Wheels"))
    if wheels is not None and wheels >= int(signals["Wheels_at_least"]):
        return True
    text = " ".join(str(record.get(field) or "") for field in signals["text_fields"]).upper()
    return any(token in text for token in signals["text_contains_any"])


def select_variant(record: dict | None) -> str:
    """First matching rule wins. Door-count fallback, then sedan."""
    source = record or {}
    rules = mapping()
    body = str(source.get("BodyClass") or "").lower()
    cab = str(source.get("BodyCabType") or "").lower()
    doors = _as_int(source.get("Doors"))
    for rule in rules["rules"]:
        when = rule["when"]
        if "BodyClass" in when and not any(token.lower() in body for token in when["BodyClass"]):
            continue
        if "BodyCabType" in when and not any(token.lower() in cab for token in when["BodyCabType"]):
            continue
        if "Doors" in when and doors not in when["Doors"]:
            continue
        if when.get("dually") and not is_dually(source):
            continue
        return rule["variant"]
    fallback = rules["fallback"]
    return fallback["by_doors"].get(str(doors), fallback["default"])


def known_variant(variant: str | None) -> str:
    key = str(variant or "").strip()
    if key in mapping()["variants"]:
        return key
    return mapping()["fallback"]["default"]


def list_variants() -> list[dict]:
    items = []
    for key, spec in mapping()["variants"].items():
        items.append(
            {
                "id": key,
                "label": spec["label"],
                "manual_only": bool(spec.get("manual_only")),
            }
        )
    return items


def variant_assets(variant: str | None) -> dict:
    key = known_variant(variant)
    spec = mapping()["variants"][key]
    views = {}
    for view, filename in spec["images"].items():
        stem = filename.rsplit(".", 1)[0]
        views[view] = {
            "jpg": f"{STATIC_URL}/{filename}",
            "webp": f"{STATIC_URL}/{stem}.webp",
            "overlay": f"{STATIC_URL}/{spec['overlays'][view]}",
        }
    return {
        "id": key,
        "label": spec["label"],
        "manual_only": bool(spec.get("manual_only")),
        "views": views,
    }


def profile_for_variant(variant: str | None) -> tuple[str, int]:
    """Map an illustration onto the area list used by the line editor."""
    key = known_variant(variant)
    if key == "coupe_2dr":
        return "coupe", 2
    if key.startswith("suv_2dr"):
        return "suv", 2
    if key.startswith("suv_"):
        return "suv", 4
    if key == "hatch_4dr":
        return "suv", 4
    if key == "minivan":
        return "van", 4
    if key.startswith("truck_regular"):
        return "pickup", 2
    if key.startswith("truck_"):
        return "pickup", 4
    return "sedan", 4


def render_views_html(variant: str | None) -> str:
    """Server-side markup for the two pencil views. The page uses the same structure."""
    assets = variant_assets(variant)
    blocks = []
    labels = {"front34": "Front", "rear34": "Rear"}
    for view, files in assets["views"].items():
        label = labels.get(view, view)
        blocks.append(
            f'<figure class="stage" data-view="{escape(view)}">'
            f'<picture>'
            f'<source srcset="{escape(files["webp"])}" type="image/webp">'
            f'<img src="{escape(files["jpg"])}" alt="{escape(assets["label"])} {escape(label)}">'
            f"</picture>"
            f'<div class="overlay" data-overlay="{escape(files["overlay"])}"></div>'
            f"</figure>"
        )
    return f'<div class="view-grid" data-variant="{escape(assets["id"])}">{"".join(blocks)}</div>'

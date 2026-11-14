"""Original collision-estimate diagrams.

These are simple geometric schematics drawn for FlagTech. They are not copies
of CCC, Mitchell, Audatex, or MOTOR artwork.
"""

from __future__ import annotations

from html import escape


AREA_LABELS = {
    "front_bumper": "Front bumper",
    "grille": "Grille",
    "hood": "Hood",
    "fender_l": "L fender",
    "fender_r": "R fender",
    "front_door_l": "L front door",
    "front_door_r": "R front door",
    "rear_door_l": "L rear door",
    "rear_door_r": "R rear door",
    "roof": "Roof",
    "trunk": "Trunk",
    "quarter_l": "L quarter panel",
    "quarter_r": "R quarter panel",
    "rear_body": "Rear body panel",
    "rear_bumper": "Rear bumper",
    "headlamps": "Headlamps",
    "tail_lamps": "Tail lamps",
    "glass": "Glass",
    "mirrors": "Mirrors",
    "wheels": "Wheels",
}


def normalize_body_style(value: str | None, doors: int | None = None) -> str:
    text = str(value or "").strip().lower()
    if text in {"sedan", "coupe", "suv", "pickup", "van"}:
        return text
    if any(token in text for token in ("pickup", "truck")):
        return "pickup"
    if "van" in text:
        return "van"
    if any(token in text for token in ("suv", "hatch", "crossover", "wagon")):
        return "suv"
    if "coupe" in text or (doors or 0) == 2:
        return "coupe"
    return "sedan"


def area_catalog(body_style: str, doors: int = 4) -> list[dict]:
    style = normalize_body_style(body_style, doors)
    door_count = 2 if style == "coupe" else 4 if int(doors or 4) >= 4 else 2
    if style == "pickup" and int(doors or 4) <= 2:
        door_count = 2
    quarter = "Bedside" if style == "pickup" else "Quarter panel"
    deck = {"pickup": "Tailgate", "suv": "Liftgate", "van": "Liftgate"}.get(style, "Trunk")
    areas = [
        ("front_bumper", "Front bumper"),
        ("grille", "Grille"),
        ("headlamps", "Headlamps"),
        ("hood", "Hood"),
        ("fender_l", "L fender"),
        ("fender_r", "R fender"),
        ("front_door_l", "L front door"),
        ("front_door_r", "R front door"),
    ]
    if door_count >= 4:
        areas.extend([("rear_door_l", "L rear door"), ("rear_door_r", "R rear door")])
    areas.extend(
        [
            ("roof", "Roof"),
            ("mirrors", "Mirrors"),
            ("glass", "Glass"),
            ("quarter_l", f"L {quarter.lower()}"),
            ("quarter_r", f"R {quarter.lower()}"),
            ("trunk", deck),
            ("rear_body", "Rear body panel"),
            ("tail_lamps", "Tail lamps"),
            ("rear_bumper", "Rear bumper"),
            ("wheels", "Wheels"),
        ]
    )
    return [{"id": key, "label": label} for key, label in areas]


def _zone(area: str, label: str, shape: str, selected: str) -> str:
    active = "active" if selected == area else ""
    return (
        f'<g class="zone {active}" data-area="{escape(area)}">'
        f"<title>{escape(label)}</title>{shape}</g>"
    )


def render_vehicle_svg(body_style: str = "sedan", doors: int = 4, side: str = "left", selected: str = "") -> str:
    style = normalize_body_style(body_style, doors)
    side = "right" if str(side).lower().startswith("r") else "left"
    suffix = "_l" if side == "left" else "_r"
    door_count = 2 if style == "coupe" or int(doors or 4) < 4 else 4
    if style == "pickup" and int(doors or 4) <= 2:
        door_count = 2
    deck_label = {"pickup": "Tailgate", "suv": "Liftgate", "van": "Liftgate"}.get(style, "Trunk")
    quarter_label = "Bedside" if style == "pickup" else "Quarter"
    roof_y = {"van": 48, "suv": 62, "pickup": 78, "sedan": 86, "coupe": 96}[style]
    rocker = 214
    door_top = roof_y + 46
    door_h = rocker - door_top
    if door_count >= 4:
        front_x, front_w, rear_x, rear_w = 300, 120, 422, 110
        cabin_end = 532
    else:
        front_x, front_w, rear_x, rear_w = 300, 150, 0, 0
        cabin_end = 450
    quarter_x = cabin_end
    quarter_w = 150 if style != "pickup" else 180
    deck_x = quarter_x + quarter_w - 8
    deck_w = 96 if style != "pickup" else 70
    rear_wheel_x = deck_x - 20 if style == "pickup" else 690
    zones = [
        _zone("front_bumper", "Front bumper", '<rect x="36" y="176" width="62" height="48" rx="8"/>', selected),
        _zone("grille", "Grille", '<rect x="48" y="150" width="40" height="24" rx="3"/>', selected),
        _zone("headlamps", "Headlamps", '<rect x="92" y="146" width="34" height="16" rx="4"/>', selected),
        _zone("hood", "Hood", '<path d="M108 168 L292 132 L300 176 L120 196 Z"/>', selected),
        _zone(f"fender{suffix}", f"{side.title()} fender", '<path d="M78 170 L150 162 L188 196 L96 208 Z"/>', selected),
        _zone("glass", "Glass", f'<path d="M250 {roof_y+6} L300 {door_top-4} L292 {door_top+28} L236 {roof_y+52} Z"/>', selected),
        _zone("mirrors", "Mirrors", f'<rect x="292" y="{door_top-16}" width="26" height="12" rx="3"/>', selected),
        _zone("roof", "Roof", f'<rect x="268" y="{roof_y}" width="{cabin_end-250}" height="34" rx="12"/>', selected),
        _zone(f"front_door{suffix}", f"{side.title()} front door", f'<rect x="{front_x}" y="{door_top}" width="{front_w}" height="{door_h}" rx="6"/>', selected),
    ]
    if door_count >= 4:
        zones.append(
            _zone(
                f"rear_door{suffix}",
                f"{side.title()} rear door",
                f'<rect x="{rear_x}" y="{door_top}" width="{rear_w}" height="{door_h}" rx="6"/>',
                selected,
            )
        )
    zones.extend(
        [
            _zone(
                f"quarter{suffix}",
                f"{side.title()} {quarter_label.lower()}",
                f'<path d="M{quarter_x} {roof_y+8} L{quarter_x+quarter_w} {roof_y+24} L{quarter_x+quarter_w} {rocker} L{quarter_x} {rocker} Z"/>',
                selected,
            ),
            _zone("trunk", deck_label, f'<rect x="{deck_x}" y="{roof_y+28}" width="{deck_w}" height="{rocker-(roof_y+28)}" rx="6"/>', selected),
            _zone("rear_body", "Rear body panel", f'<rect x="{deck_x+8}" y="{rocker-28}" width="{max(deck_w-16, 40)}" height="22" rx="3"/>', selected),
            _zone("tail_lamps", "Tail lamps", f'<rect x="{deck_x+deck_w-30}" y="{roof_y+36}" width="22" height="14" rx="3"/>', selected),
            _zone("rear_bumper", "Rear bumper", f'<rect x="{deck_x+deck_w-4}" y="176" width="54" height="48" rx="8"/>', selected),
            _zone("wheels", "Wheels", f'<circle cx="168" cy="236" r="30"/><circle cx="{rear_wheel_x}" cy="236" r="30"/>', selected),
        ]
    )
    body = "\n".join(zones)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 300" role="img" aria-label="Original {escape(style)} diagram, {escape(side)} side">
<style>
  .zone {{ cursor: pointer; }}
  .zone rect, .zone path, .zone circle {{ fill: #f7f4f2; stroke: #3c4142; stroke-width: 2; }}
  .zone:hover rect, .zone:hover path, .zone:hover circle {{ stroke: #971d1d; fill: #fff4f4; }}
  .zone.active rect, .zone.active path, .zone.active circle {{ stroke: #b22222; fill: #ffe8e8; stroke-width: 3; }}
  .caption {{ font: 600 14px "Segoe UI", sans-serif; fill: #3c4142; }}
</style>
<rect x="1" y="1" width="978" height="298" rx="16" fill="#f7f6f5" stroke="#d9d4d2"/>
<text class="caption" x="24" y="28">{escape(style.upper())} · {escape(side.upper())} SIDE · original schematic</text>
{body}
<line x1="30" y1="266" x2="950" y2="266" stroke="#d0cbc8" stroke-width="2"/>
<text class="caption" x="24" y="288">Click a panel. Two-door cars omit rear doors. Pickups use bedside and tailgate.</text>
</svg>'''


def render_area_svg(area: str) -> str:
    key = str(area or "front_bumper")
    label = AREA_LABELS.get(key, key.replace("_", " ").title())
    boxes = [
        (24, 36, "Outer"),
        (180, 36, "Reinforcement"),
        (336, 36, "Hardware"),
        (492, 36, "Seal / clip"),
    ]
    parts = []
    for x, y, name in boxes:
        parts.append(
            f'<g class="sub" data-subpart="{escape(name)}"><rect x="{x}" y="{y}" width="130" height="78" rx="10"/>'
            f'<text x="{x+65}" y="{y+44}" text-anchor="middle">{escape(name)}</text></g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 160" role="img" aria-label="Generic breakdown of {escape(label)}">
<style>
  .sub rect {{ fill: #fff; stroke: #971d1d; stroke-width: 2; }}
  text {{ font: 600 13px "Segoe UI", sans-serif; fill: #3c4142; }}
</style>
<text x="16" y="22">{escape(label)} — generic sub-part breakdown</text>
{''.join(parts)}
</svg>'''

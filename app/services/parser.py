import re
from app.models.estimate import LineItem

line_item_pattern = re.compile(
    r"^\|?\s*(\d+)\s*\|\s*(\w*)\s*\|\s*(.*?)\s*\|\s*([\w\d]*)\s*\|\s*(\d*)\s*\|\s*([\d.,]*)\s*\|\s*([\w\d.,]*)\s*\|\s*([\w\d.,]*)\s*\|?$"
)

def parse_estimate_text(text: str):
    items = []
    for line in text.splitlines():
        match = line_item_pattern.match(line)
        if match:
            items.append(LineItem(
                line=int(match.group(1)),
                operation=match.group(2) or None,
                description=match.group(3).strip(),
                part_number=match.group(4) or None,
                quantity=int(match.group(5)) if match.group(5) else None,
                price=float(match.group(6).replace(",", "")) if match.group(6) else None,
                labor=float(match.group(7)) if match.group(7) else None,
                paint=float(match.group(8)) if match.group(8) else None
            ))
    return items
import re
from app.models.estimate import LineItem
from app.utils import helpers


def parse_estimate_text(text: str):
    """Parse estimate text into a list of LineItem objects.

    This parser is permissive: it splits table-like lines by pipe (`|`),
    uses helper functions to clean numeric fields, and tolerates missing
    columns.
    """
    items = []
    for line in text.splitlines():
        if not helpers.is_estimate_line(line):
            continue

        stripped = helpers.strip_line_artifacts(line)
        parts = helpers.safe_split(stripped, "|")

        def get(idx: int) -> str:
            return parts[idx] if idx < len(parts) else ""

        # Line number: extract first integer
        m = re.search(r"\d+", get(0) or "")
        if not m:
            continue
        line_no = int(m.group())

        op_raw = get(1)
        operation = helpers.normalize_operation(op_raw) or (op_raw.strip() or None)

        description = get(2).strip()
        part_number = get(3).strip() or None

        quantity = helpers.clean_quantity(get(4))
        price = helpers.clean_price(get(5))
        labor = helpers.clean_float(get(6))
        paint = helpers.clean_float(get(7))

        items.append(LineItem(
            line=line_no,
            operation=operation,
            description=description,
            part_number=part_number,
            quantity=quantity,
            price=price,
            labor=labor,
            paint=paint,
        ))

    return items
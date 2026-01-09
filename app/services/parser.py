import re
from app.models.estimate import LineItem
from app.utils import helpers


def _parse_space_delimited_line(stripped: str):
    # returns (line_no:int, operation:str|None, description:str, labor:float|None, paint:float|None)
    tokens = stripped.split()
    # find leading line number
    m = re.match(r"^\s*(\d+)\b", stripped)
    if not m:
        return None
    line_no = int(m.group(1))

    # Guard: very large leading numbers are likely address/year/page numbers,
    # not table line numbers. Skip if clearly not a table line.
    if line_no > 999:
        return None

    # remove leading numeric token from tokens
    if re.match(r"^\d+$", tokens[0]):
        idx = 1
    else:
        # find first token that's numeric
        idx = 0
        for i, t in enumerate(tokens):
            if re.match(r"^\d+$", t):
                idx = i + 1
                break

    # detect operation token (if it's a known op)
    operation = None
    if idx < len(tokens):
        op_candidate = tokens[idx]
        normalized = helpers.normalize_operation(op_candidate)
        if normalized:
            operation = normalized
            idx += 1

    # Find numeric tokens and classify currency-like tokens so we don't
    # confuse extended price with labor/paint hours. Scan left-to-right so
    # we can assign small-number candidates in reading order.
    numeric_tokens = []  # (i, raw_token, float_value)
    for i in range(idx, len(tokens)):
        raw = tokens[i]
        raw_clean = raw.replace(",", "").replace("$", "")
        if re.match(r"^-?\d+(?:\.\d+)?$", raw_clean):
            try:
                val = float(raw_clean)
            except Exception:
                continue
            numeric_tokens.append((i, raw, val))

    def is_currency_like(tok, val):
        s = tok.replace(",", "")
        if "$" in tok:
            return True
        if abs(val) >= 100:
            return True
        m = re.match(r"^(\d+)(?:\.\d+)?$", s)
        if m and len(m.group(1)) >= 3:
            return True
        return False

    # collect small-number candidates (likely hours), skipping qty before currency
    small_candidates = []  # (i,val)
    for idx_num, raw, val in numeric_tokens:
        next_idx = idx_num + 1
        next_is_currency = False
        if next_idx < len(tokens):
            nxt = tokens[next_idx].replace(",", "").replace("$", "")
            if re.match(r"^-?\d+(?:\.\d+)?$", nxt):
                try:
                    nxt_val = float(nxt)
                    if is_currency_like(tokens[next_idx], nxt_val):
                        next_is_currency = True
                except Exception:
                    pass

        if is_currency_like(raw, val):
            continue
        if next_is_currency and float(val).is_integer():
            # probably a Qty value (e.g., '1' before extended price) -> skip
            continue
        if abs(val) <= 24:
            small_candidates.append((idx_num, val))

    labor = None
    paint = None
    if small_candidates:
        # assign left-to-right: first small -> labor, second -> paint
        labor = helpers.clean_float(str(small_candidates[0][1]))
        if len(small_candidates) >= 2:
            paint = helpers.clean_float(str(small_candidates[1][1]))

    numeric_indices = [i for i, _, _ in numeric_tokens]
    end_idx = numeric_indices[0] if numeric_indices else len(tokens)

    # Build description but strip part-number tokens (alphanumeric IDs)
    desc_tokens = []
    part_re = re.compile(r"(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9\-_/]{4,}")
    for t in tokens[idx:end_idx]:
        if part_re.search(t):
            continue
        if t.lower() in ("incl.", "incl", "m"):
            continue
        desc_tokens.append(t)
    description = " ".join(desc_tokens).strip()

    return (line_no, operation, description, labor, paint)


def parse_estimate_text(text: str):
    """Parse estimate text into a list of LineItem objects.

    Handles both pipe-delimited rows and space-delimited rows extracted from
    plain-text PDFs. Returns only the fields the UI needs: operation,
    description, labor, and paint.
    """
    items = []
    in_table = False
    for line in text.splitlines():
        # Start parsing when we see the explicit table header (avoid numeric headers elsewhere)
        if not in_table:
            if re.search(r"\bLine\b", line, re.IGNORECASE) and (re.search(r"\bOper\b|\bOperation\b", line, re.IGNORECASE) or re.search(r"\bDescription\b", line, re.IGNORECASE) or re.search(r"\bLabor\b", line, re.IGNORECASE)):
                in_table = True
            else:
                continue

        if not helpers.is_estimate_line(line):
            continue

        stripped = helpers.strip_line_artifacts(line)

        # If pipe-delimited, prefer the old column parsing
        if "|" in stripped:
            parts = helpers.safe_split(stripped, "|")

            def get(idx: int) -> str:
                return parts[idx] if idx < len(parts) else ""

            m = re.search(r"\d+", get(0) or "")
            if not m:
                continue
            line_no = int(m.group())

            op_raw = get(1)
            operation = helpers.normalize_operation(op_raw) or (op_raw.strip() or None)
            description = get(2).strip()
            labor = helpers.clean_float(get(6))
            paint = helpers.clean_float(get(7))

            items.append(LineItem(
                line=line_no,
                operation=operation,
                description=description,
                labor=labor,
                paint=paint,
            ))
            continue

        parsed = _parse_space_delimited_line(stripped)
        if not parsed:
            continue

        line_no, operation, description, labor, paint = parsed

        items.append(LineItem(
            line=line_no,
            operation=operation,
            description=description or "",
            labor=labor,
            paint=paint,
        ))

    return items
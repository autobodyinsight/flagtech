from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf, extract_words_from_pdf
from app.services.parser import parse_estimate_text
import math
import re


def _kmeans_1d(values, k, iters=20):
    if not values or k <= 0:
        return []
    # initialize centers as quantiles
    vals = sorted(values)
    centers = []
    n = len(vals)
    for i in range(k):
        idx = int((i + 0.5) * n / k)
        centers.append(vals[min(idx, n - 1)])

    for _ in range(iters):
        groups = {i: [] for i in range(k)}
        for v in vals:
            best = min(range(k), key=lambda c: abs(v - centers[c]))
            groups[best].append(v)
        changed = False
        for i in range(k):
            if groups[i]:
                newc = sum(groups[i]) / len(groups[i])
                if abs(newc - centers[i]) > 1e-6:
                    changed = True
                centers[i] = newc
        if not changed:
            break
    return centers


def _group_rows(words, y_thresh=8.0):
    # words: list of dicts with y0,y1; group by y-center proximity
    rows = []
    for w in sorted(words, key=lambda x: (x["y0"] + x["y1"]) / 2):
        ymid = (w["y0"] + w["y1"]) / 2
        placed = False
        for r in rows:
            if abs(r["ymid"] - ymid) <= y_thresh:
                r["words"].append(w)
                # update average ymid
                r["ymid"] = sum(( (ww["y0"]+ww["y1"]) / 2 for ww in r["words"] )) / len(r["words"])
                placed = True
                break
        if not placed:
            rows.append({"ymid": ymid, "words": [w]})
    return rows

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def upload_form():
    return """
<html>
<head>
    <title>FlagTech Estimate Parser</title>
    <style>body{font-family:Arial; padding:40px;}</style>
</head>
<body>
    <h2>Upload an Estimate PDF</h2>
    <form action="/ui/grid" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf" />
        <br><br>
        <button type="submit">View Estimate</button>
    </form>
</body>
</html>
"""

@router.post("/parse", response_class=HTMLResponse)
async def parse_ui(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    # Debug logging: show a truncated preview of extracted text
    try:
        print("===EXTRACTED TEXT PREVIEW (truncated)===")
        print(text[:4000])
        print("===END PREVIEW===")
    except Exception:
        print("[extractor] could not print text preview")

    items = parse_estimate_text(text)
    print(f"[parser] parsed {len(items)} items")

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item.line}</td>
            <td>{item.operation or ''}</td>
            <td>{item.description or ''}</td>
            <td>{item.labor if item.labor is not None else ''}</td>
            <td>{item.paint if item.paint is not None else ''}</td>
        </tr>
        """

    return f"""
<html>
<head>
    <title>Parsed Estimate</title>
</head>
<body style="font-family: Arial; padding: 40px;">
    <h2>Parsed Line Items</h2>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Line</th>
            <th>Op</th>
            <th>Description</th>
            <th>Labor</th>
            <th>Paint</th>
        </tr>
        {rows}
    </table>
    <br><br>
    <a href="/ui">Upload another file</a>
</body>
</html>
"""



@router.post("/grid", response_class=HTMLResponse)
async def grid_ui(file: UploadFile = File(...)):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # Prepare xmid/ymid and page index on words
    all_words = []
    for pi, page in enumerate(pages, start=1):
        for w in page.get("words", []):
            w["page_index"] = pi
            w["xmid"] = (w["x0"] + w["x1"]) / 2.0
            w["ymid"] = (w["y0"] + w["y1"]) / 2.0
            all_words.append(w)

    # detect first line-item row (anchor)
    anchor_page = None
    anchor_ymid = None
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            left = min(r["words"], key=lambda w: w["xmid"]) if r["words"] else None
            if not left:
                continue
            if re.search(r"\b\d+\b", left["text"]):
                anchor_page = pi
                anchor_ymid = r["ymid"]
                break
        if anchor_page:
            break

    # compute column centers
    if anchor_page:
        xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page) or (w["page_index"] == anchor_page and w["ymid"] >= (anchor_ymid - 3.0))]
    else:
        xvals = [w["xmid"] for w in all_words]

    centers = _kmeans_1d(xvals, 5, iters=40) if xvals else []
    centers_sorted = sorted(centers) if centers else []

    # Build table rows with editable fields
    table_rows = ""
    labor_total = 0.0
    paint_total = 0.0
    row_index = 0
    
    def esc(s):
        return (s or "").replace("<", "&lt;").replace(">", "&gt;")
    
    def parse_num(s):
        if not s:
            return 0.0
        s = str(s).replace("$", "").replace(",", "").strip()
        try:
            return float(s)
        except ValueError:
            return 0.0

    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            if anchor_page and pi == anchor_page and anchor_ymid is not None and r["ymid"] < (anchor_ymid - 3.0):
                continue
            wlist = sorted(r["words"], key=lambda ww: ww.get("xmid", 0))
            cols = {i: [] for i in range(len(centers_sorted) or 5)}
            for ww in wlist:
                if centers_sorted:
                    best = min(range(len(centers_sorted)), key=lambda c: abs(ww.get("xmid", 0) - centers_sorted[c]))
                else:
                    best = 2
                cols.setdefault(best, []).append(ww)

            vals = []
            for i in range(5):
                part = " ".join(w.get("text", "") for w in sorted(cols.get(i, []), key=lambda z: z.get("xmid", 0)))
                vals.append(part)

            # filter likely header rows
            left_col = vals[0].strip() if vals else ""
            combined_text = " ".join(vals).lower()
            if not re.search(r"\b\d+\b", left_col):
                if any(k in combined_text for k in ("customer", "address", "vin", "page", "estimate", "phone", "fax")):
                    continue
                if left_col.lower() in ("line", "line#", "no", "qty"):
                    continue

            labor_text = vals[3] if len(vals) > 3 else ""
            paint_text = vals[4] if len(vals) > 4 else ""
            
            labor_val = parse_num(labor_text)
            paint_val = parse_num(paint_text)
            labor_total += labor_val
            paint_total += paint_val

            table_rows += f"""
        <tr id="row-{row_index}">
            <td>{esc(vals[0])}</td>
            <td>{esc(vals[1])}</td>
            <td>{esc(vals[2])}</td>
            <td>
                <input type="checkbox" class="include-labor" checked data-index="{row_index}" style="margin-right:5px;">
                <input type="number" class="labor-input" data-index="{row_index}" value="{labor_val}" step="0.01" style="width:60px;">
            </td>
            <td>
                <input type="checkbox" class="include-paint" checked data-index="{row_index}" style="margin-right:5px;">
                <input type="number" class="paint-input" data-index="{row_index}" value="{paint_val}" step="0.01" style="width:60px;">
            </td>
        </tr>
        """
            row_index += 1
    
    # Add totals row
    table_rows += """
        <tr style="font-weight: bold; background-color: #f0f0f0;">
            <td colspan="3">TOTALS</td>
            <td><span id="labor-total">0.00</span></td>
            <td><span id="paint-total">0.00</span></td>
        </tr>
        """

    html = f"""
<html>
<head>
    <title>Estimate Editor</title>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        table {{ border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f9f9f9; }}
        input[type="number"] {{ padding: 4px; }}
        input[type="checkbox"] {{ cursor: pointer; }}
    </style>
</head>
<body>
    <h2>Estimate Editor</h2>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Line</th>
            <th>Op</th>
            <th>Description</th>
            <th>Labor Hours</th>
            <th>Paint Hours</th>
        </tr>
        {table_rows}
    </table>
    <br><a href='/ui'>Back</a>
    
    <script>
        function updateTotals() {{
            let laborTotal = 0;
            let paintTotal = 0;
            
            document.querySelectorAll('.labor-input').forEach(input => {{
                const index = input.getAttribute('data-index');
                const checkbox = document.querySelector(`.include-labor[data-index="${{index}}"]`);
                if (checkbox && checkbox.checked) {{
                    laborTotal += parseFloat(input.value) || 0;
                }}
            }});
            
            document.querySelectorAll('.paint-input').forEach(input => {{
                const index = input.getAttribute('data-index');
                const checkbox = document.querySelector(`.include-paint[data-index="${{index}}"]`);
                if (checkbox && checkbox.checked) {{
                    paintTotal += parseFloat(input.value) || 0;
                }}
            }});
            
            document.getElementById('labor-total').textContent = laborTotal.toFixed(2);
            document.getElementById('paint-total').textContent = paintTotal.toFixed(2);
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            // Initial calculation
            updateTotals();
            
            // Add listeners to all inputs and checkboxes
            document.querySelectorAll('.labor-input, .paint-input').forEach(input => {{
                input.addEventListener('change', updateTotals);
                input.addEventListener('input', updateTotals);
            }});
            
            document.querySelectorAll('.include-labor, .include-paint').forEach(checkbox => {{
                checkbox.addEventListener('change', updateTotals);
            }});
        }});
    </script>
</body>
</html>
"""

    return html


@router.post("/aligned", response_class=HTMLResponse)
async def aligned_ui(file: UploadFile = File(...)):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # compute xmid/ymid and page index for all words across all pages
    all_words = []
    for pi, page in enumerate(pages, start=1):
        for wdict in page.get("words", []):
            wdict["page_index"] = pi
            wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0
            all_words.append(wdict)

    if not all_words:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    # determine anchor (first detected line-item row)
    anchor_page = None
    anchor_ymid = None
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            left = min(r["words"], key=lambda w: w.get("xmid", 0)) if r["words"] else None
            if left and re.search(r"\b\d+\b", left.get("text", "")):
                anchor_page = pi
                anchor_ymid = r["ymid"]
                break
        if anchor_page:
            break

    # collect all xmid values to cluster into 5 columns (global across pages)
    # if anchor found, only use words at/after anchor to compute centers
    if anchor_page:
        xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page) or (w["page_index"] == anchor_page and w["ymid"] >= (anchor_ymid - 3.0))]
    else:
        xvals = [w["xmid"] for w in all_words]
    centers = _kmeans_1d(xvals, 5, iters=40)
    if not centers:
        return "<html><body><p>Could not compute columns.</p><a href='/ui'>Back</a></body></html>"

    centers_sorted = sorted(centers)
    col_names = ["Line", "Op", "Description", "Labor", "Paint"]

    table_rows = ""
    # process pages in order and append their rows
    for page_idx, page in enumerate(pages, start=1):
        # ensure per-page xmid/ymid are present
        for wdict in page.get("words", []):
            if "xmid" not in wdict:
                wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            if "ymid" not in wdict:
                wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0

        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            # sort words in row by x
            wlist = sorted(r["words"], key=lambda ww: ww["xmid"])
            cols = {i: [] for i in range(len(centers_sorted))}
            for ww in wlist:
                # assign to nearest center
                best = min(range(len(centers_sorted)), key=lambda c: abs(ww["xmid"] - centers_sorted[c]))
                cols[best].append(ww)

            # join texts per column
            vals = []
            for i in range(len(centers_sorted)):
                part = " ".join(w["text"] for w in sorted(cols[i], key=lambda z: z["xmid"]))
                vals.append(part)

            # Filter out header/customer rows: require a leading line number in first column
            left_col = vals[0].strip() if vals else ""
            combined_text = " ".join(vals).lower()
            if not re.search(r"\b\d+\b", left_col):
                if any(k in combined_text for k in ("customer", "address", "vin", "page", "estimate", "phone", "fax")):
                    continue
                if left_col.lower() in ("line", "line#", "no", "qty"):
                    continue

            # render only the five columns
            table_rows += "<tr>"
            for i in range(5):
                table_rows += f"<td>{(vals[i] if i < len(vals) else '')}</td>"
            table_rows += "</tr>"

    header_html = "".join(f"<th>{n}</th>" for n in col_names)

    return f"""
<html>
<head><title>Aligned Table</title></head>
<body style='font-family:Arial; padding:20px;'>
  <h2>Aligned Table (All Pages)</h2>
  <table border='1' cellpadding='6' cellspacing='0'>
    <tr>{header_html}</tr>
    {table_rows}
  </table>
  <br><a href='/ui'>Back</a>
</body>
</html>
"""
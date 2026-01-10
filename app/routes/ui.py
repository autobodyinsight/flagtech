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
</head>
<body style="font-family: Arial; padding: 40px;">
    <h2>Upload an Estimate PDF</h2>
    <form action="/ui/parse" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf" />
        <br><br>
        <button type="submit">Parse Estimate</button>
    </form>
    <br>
    <h3>Visual Layout / Aligned Table</h3>
    <form action="/ui/grid" method="post" enctype="multipart/form-data" style="display:inline-block; margin-right:12px;">
        <input type="file" name="file" accept="application/pdf" />
        <button type="submit">Show Visual Grid</button>
    </form>
    <form action="/ui/aligned" method="post" enctype="multipart/form-data" style="display:inline-block;">
        <input type="file" name="file" accept="application/pdf" />
        <button type="submit">Show Aligned Table</button>
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

    display_w = 800
    # Prepare xmid/ymid and page index on words
    for pi, page in enumerate(pages, start=1):
        for w in page.get("words", []):
            w["page_index"] = pi
            if "xmid" not in w:
                w["xmid"] = (w["x0"] + w["x1"]) / 2.0
            if "ymid" not in w:
                w["ymid"] = (w["y0"] + w["y1"]) / 2.0

    # detect second RO row (anchor) and ESTIMATE TOTALS row (end marker)
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()
            
            # Look for RO and use the second occurrence as anchor
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
            
            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]
            
            if anchor_page and subtotals_page:
                break
        
        if anchor_page and subtotals_page:
            break

    pages_html = ""
    for pi, page in enumerate(pages, start=1):
        # skip pages before anchor
        if anchor_page and pi < anchor_page:
            continue
        # skip pages after subtotals
        if subtotals_page and pi > subtotals_page:
            continue
        w = page.get("width", 1)
        h = page.get("height", 1)
        scale = display_w / w if w else 1.0

        boxes_html = ""
        for wd in page.get("words", []):
            # if this is the anchor page, skip words above the anchor_ymid
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            # if this is the subtotals page, skip words below the subtotals_ymid
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) > subtotals_ymid:
                    continue
            x = wd["x0"] * scale
            y = wd["y0"] * scale
            ww = (wd["x1"] - wd["x0"]) * scale
            hh = (wd["y1"] - wd["y0"]) * scale
            txt = wd["text"].replace("<", "&lt;").replace(">", "&gt;")
            boxes_html += f"<div style='position:absolute; left:{x}px; top:{y}px; width:{ww}px; height:{hh}px; border:1px solid rgba(0,120,215,0.6); font-size:10px; overflow:hidden;'>{txt}</div>"

        pages_html += f"<h3>Page {pi}</h3><div style='position:relative; width:{display_w}px; height:{int(h*scale)}px; border:1px solid #ccc; margin-bottom:20px;'>{boxes_html}</div>"

    html = f"""
<html>
<head><title>Visual Grid</title></head>
<body style='font-family:Arial; padding:20px;'>
  <h2>Document Visual Grid</h2>
  {pages_html}
  <br><a href='/ui'>Back</a>
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

    # determine anchor (second RO row) and end marker (ESTIMATE TOTALS row)
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()
            
            # Look for RO and use the second occurrence as anchor
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
            
            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]
            
            if anchor_page and subtotals_page:
                break
        
        if anchor_page and subtotals_page:
            break

    # collect all xmid values to cluster into 5 columns (global across pages)
    # if anchor found, only use words at/after anchor and before subtotals to compute centers
    if anchor_page:
        if subtotals_page:
            xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page and w["page_index"] < subtotals_page) or (w["page_index"] == anchor_page and w["ymid"] >= anchor_ymid) or (w["page_index"] == subtotals_page and w["ymid"] <= subtotals_ymid)]
        else:
            xvals = [w["xmid"] for w in all_words if (w["page_index"] > anchor_page) or (w["page_index"] == anchor_page and w["ymid"] >= anchor_ymid)]
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
        # skip pages after subtotals
        if subtotals_page and page_idx > subtotals_page:
            continue
        
        # ensure per-page xmid/ymid are present
        for wdict in page.get("words", []):
            if "xmid" not in wdict:
                wdict["xmid"] = (wdict["x0"] + wdict["x1"]) / 2.0
            if "ymid" not in wdict:
                wdict["ymid"] = (wdict["y0"] + wdict["y1"]) / 2.0

        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for r in rows:
            # skip rows above anchor (RO) or at/below subtotals
            if anchor_page and page_idx == anchor_page and anchor_ymid is not None:
                if r["ymid"] < anchor_ymid:
                    continue
            if subtotals_page and page_idx == subtotals_page and subtotals_ymid is not None:
                if r["ymid"] >= subtotals_ymid:
                    continue
            
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
                if any(k in combined_text for k in ("customer", "address", "vin", "page", "estimate", "phone", "fax", "ro")):
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
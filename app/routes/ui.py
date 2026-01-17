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
async def home_screen():
    return """
<html>
<head>
    <title>FlagTech</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
            background-color: #f5f5f5;
        }
        .sidebar {
            width: 150px;
            background-color: #0078d7;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }
        .nav-box {
            padding: 15px;
            background-color: #005a9e;
            color: white;
            text-align: center;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .nav-box:hover {
            background-color: #0078d7;
            border: 2px solid white;
        }
        .nav-box.active {
            background-color: #ffffff;
            color: #0078d7;
            border: 2px solid #0078d7;
        }
        .content-area {
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            margin-left: 150px;
            background-color: white;
            min-height: 100vh;
        }
        .screen {
            display: none;
        }
        .screen.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="nav-box active" onclick="switchScreen('upload')">UPLOAD</div>
        <div class="nav-box" onclick="switchScreen('tech')">TECH</div>
        <div class="nav-box" onclick="switchScreen('ros')">RO'S</div>
        <div class="nav-box" onclick="switchScreen('flagtech')">FLAG TECH</div>
    </div>
    
    <div class="content-area">
        <div id="upload" class="screen active">
            <h2>Upload an Estimate PDF</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="fileInput" name="file" accept="application/pdf" onchange="handleFileUpload()" />
            </form>
            <div id="uploadStatus"></div>
        </div>
        
        <div id="tech" class="screen">
            <h2>TECH</h2>
            <p>Tech management screen - coming soon</p>
        </div>
        
        <div id="ros" class="screen">
            <h2>RO'S</h2>
            <p>RO's management screen - coming soon</p>
        </div>
        
        <div id="flagtech" class="screen">
            <h2>FLAG TECH</h2>
            <p>Flag Tech screen - coming soon</p>
        </div>
    </div>
    
    <script>
        function switchScreen(screenName) {
            // Hide all screens
            const screens = document.querySelectorAll('.screen');
            screens.forEach(screen => screen.classList.remove('active'));
            
            // Remove active class from all nav boxes
            const navBoxes = document.querySelectorAll('.nav-box');
            navBoxes.forEach(box => box.classList.remove('active'));
            
            // Show selected screen
            document.getElementById(screenName).classList.add('active');
            
            // Add active class to clicked nav box
            event.target.classList.add('active');
        }
        
        function handleFileUpload() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.innerHTML = '<p>Processing...</p>';
            
            fetch('/ui/grid?ajax=true', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                statusDiv.innerHTML = html;
                fileInput.value = '';
                
                // Execute any scripts in the loaded content
                const scripts = statusDiv.querySelectorAll('script');
                scripts.forEach(oldScript => {
                    const newScript = document.createElement('script');
                    newScript.innerHTML = oldScript.innerHTML;
                    document.body.appendChild(newScript);
                });
            })
            .catch(error => {
                statusDiv.innerHTML = '<p>Error: ' + error.message + '</p>';
            });
        }
    </script>
</body>
</html>
"""

@router.get("/upload", response_class=HTMLResponse)
async def upload_form():
    return """
<html>
<head>
    <title>FlagTech Estimate Parser</title>
</head>
<body style="font-family: Arial; padding: 40px;">
    <h2>Upload an Estimate PDF</h2>
    <form id="uploadForm" action="/ui/grid" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf" onchange="this.form.submit()" />
    </form>
    <script>
        // Auto-submit form when file is selected
    </script>
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
async def grid_ui(file: UploadFile = File(...), ajax: str = None):
    pages = extract_words_from_pdf(file)
    if not pages:
        return "<html><body><p>No words found in PDF.</p><a href='/ui'>Back</a></body></html>"

    display_w = 1200
    # Prepare xmid/ymid and page index on words
    for pi, page in enumerate(pages, start=1):
        for w in page.get("words", []):
            w["page_index"] = pi
            if "xmid" not in w:
                w["xmid"] = (w["x0"] + w["x1"]) / 2.0
            if "ymid" not in w:
                w["ymid"] = (w["y0"] + w["y1"]) / 2.0

    # detect second RO row (anchor) and ESTIMATE TOTALS row (end marker)
    # also capture second RO line for vehicle info
    anchor_page = None
    anchor_ymid = None
    subtotals_page = None
    subtotals_ymid = None
    ro_count = 0
    second_ro_line = ""
    vehicle_info_line = ""
    
    for pi, page in enumerate(pages, start=1):
        rows = _group_rows(page.get("words", []), y_thresh=6.0)
        for idx, r in enumerate(rows):
            row_text = " ".join(w.get("text", "") for w in r["words"]).strip()
            
            # Look for RO and use the second occurrence as anchor
            if re.search(r"\bRO\b", row_text):
                ro_count += 1
                # Capture second RO line and search for vehicle info
                if ro_count == 2 and not anchor_page:
                    anchor_page = pi
                    anchor_ymid = r["ymid"]
                    second_ro_line = row_text
                    # Search for vehicle info line (contains 4-digit year)
                    for j in range(idx + 1, min(idx + 10, len(rows))):
                        next_line = " ".join(w.get("text", "") for w in rows[j]["words"]).strip()
                        # Look for a line with a 4-digit year (19xx or 20xx)
                        if re.search(r'\b(19\d{2}|20\d{2})\b', next_line):
                            vehicle_info_line = next_line
                            break
            
            # Look for ESTIMATE TOTALS as end marker
            if not subtotals_page and re.search(r"\bESTIMATE\s+TOTALS\b", row_text):
                subtotals_page = pi
                subtotals_ymid = r["ymid"]
            
            if anchor_page and subtotals_page:
                break
        
        if anchor_page and subtotals_page:
            break

    # Collect all words to find column positions
    all_words = []
    for pi, page in enumerate(pages, start=1):
        if anchor_page and pi < anchor_page:
            continue
        if subtotals_page and pi > subtotals_page:
            continue
        for wd in page.get("words", []):
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) > subtotals_ymid:
                    continue
            all_words.append(wd)
    
    # Use k-means to find 5 columns
    xvals = [w["xmid"] for w in all_words]
    centers = _kmeans_1d(xvals, 5, iters=40)
    centers_sorted = sorted(centers) if centers else []
    
    # Assume columns are: Line, Op, Description, Labor, Paint
    line_col_x = centers_sorted[0] if len(centers_sorted) > 0 else None
    paint_col_x = centers_sorted[4] if len(centers_sorted) > 4 else None

    pages_html = ""
    paint_items = []  # Store items with paint values for the modal
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
        
        # First, group words into rows and extract line/paint pairs
        page_words = []
        for wd in page.get("words", []):
            # if this is the anchor page, skip words above the anchor_ymid
            if anchor_page and pi == anchor_page and anchor_ymid is not None:
                if wd.get("ymid", 0) < (anchor_ymid - 3.0):
                    continue
            # if this is the subtotals page, skip words at or below the subtotals_ymid
            if subtotals_page and pi == subtotals_page and subtotals_ymid is not None:
                if wd.get("ymid", 0) >= (subtotals_ymid - 3.0):
                    continue
            page_words.append(wd)
        
        # Group into rows
        rows = _group_rows(page_words, y_thresh=6.0)
        
        # Extract line numbers and paint values from rows
        for row in rows:
            row_words = sorted(row["words"], key=lambda x: x["xmid"])
            line_num = None
            paint_val = None
            description = []
            
            for wd in row_words:
                word_xmid = wd.get("xmid", (wd["x0"] + wd["x1"]) / 2.0)
                
                # Check if this is a line number
                if line_col_x and abs(word_xmid - line_col_x) < 40:
                    if re.match(r'^\d+$', wd["text"].strip()):
                        line_num = wd["text"].strip()
                
                # Collect description text (everything in the middle)
                elif line_col_x and paint_col_x:
                    if line_col_x < word_xmid < paint_col_x:
                        description.append(wd["text"].strip())
                
                # Check if this is a paint value (only in paint column, not labor)
                if paint_col_x and abs(word_xmid - paint_col_x) < 30:
                    if re.match(r'^(\d+\.?\d*)$', wd["text"].strip()):
                        try:
                            paint_val = float(wd["text"].strip())
                        except:
                            pass
            
            # Add to paint_items ONLY if we found a line number AND a paint value in the paint column
            if line_num and paint_val is not None:
                paint_items.append({
                    "line": line_num,
                    "description": " ".join(description),
                    "value": paint_val
                })
        
        # Now display all words
        for wd in page_words:
            x = wd["x0"] * scale
            y = wd["y0"] * scale
            ww = (wd["x1"] - wd["x0"]) * scale
            hh = (wd["y1"] - wd["y0"]) * scale
            txt = wd["text"].replace("<", "&lt;").replace(">", "&gt;")
            boxes_html += f"<div style='position:absolute; left:{x}px; top:{y}px; width:{ww}px; height:{hh}px; border:1px solid rgba(0,120,215,0.6); font-size:15px; overflow:hidden;'>{txt}</div>"

        pages_html += f"<h3>Page {pi}</h3><div style='position:relative; width:{display_w}px; height:{int(h*scale)}px; border:1px solid #ccc; margin-bottom:20px;'>{boxes_html}</div>"

    # Calculate total paint value
    total_paint = sum(item["value"] for item in paint_items)
    paint_items_json = str(paint_items).replace("'", '"')

    # If AJAX request, return just the content without HTML wrapper
    if ajax:
        content = f"""
<h2>Document Visual Grid</h2>
<button onclick="openPaintModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#0078d7; color:white; border:none; border-radius:3px;'>Assign Labor</button>
<br><br>
{pages_html}
<br><a href='/ui'>Back</a>

<div id="paintModal" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closePaintModal()">&times;</span>
    <div style="margin-bottom: 15px;">
      <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{second_ro_line}</div>
      <div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>
    </div>
    <div style="margin-bottom: 15px;">
      <label style="font-weight: bold; font-size: 14px;">TECH:</label>
      <input type="text" id="techInput" style="padding: 8px; font-size: 14px; margin-left: 10px; width: 200px; border: 1px solid #ccc; border-radius: 3px;" placeholder="Enter technician name" />
    </div>
    <h2>Labor Assignment</h2>
    <div id="paintList"></div>
    <div class="paint-total">Total Labor: <span id="totalPaint">{total_paint}</span></div>
    <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
      <button onclick="printModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#50b350; color:white; border:none; border-radius:3px;'>Print</button>
      <button onclick="saveModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#0078d7; color:white; border:none; border-radius:3px;'>Save</button>
    </div>
  </div>
</div>

<style>
  .modal {{
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.4);
  }}
  .modal-content {{
    background-color: #fefefe;
    margin: 2% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 95%;
    max-width: 1400px;
    height: 80vh;
    overflow-y: auto;
    border-radius: 5px;
  }}
  .close {{
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
  }}
  .close:hover {{
    color: black;
  }}
  .paint-item {{
    padding: 12px;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
  }}
  .paint-item.deducted {{
    background-color: #f0f0f0;
    text-decoration: line-through;
    opacity: 0.6;
  }}
  .paint-item-checkbox {{
    cursor: pointer;
    width: 18px;
    height: 18px;
    margin-right: 10px;
  }}
  .paint-total {{
    padding: 12px 8px;
    font-weight: bold;
    background-color: #f0f0f0;
    margin-top: 10px;
    text-align: right;
  }}
</style>

<script>
  const paintItems = {paint_items_json};
  const initialTotal = {total_paint};
  
  function updateTotal() {{
    const checkboxes = document.querySelectorAll('.paint-item-checkbox');
    let deductedTotal = 0;
    
    checkboxes.forEach((checkbox, index) => {{
      if (checkbox.checked) {{
        deductedTotal += paintItems[index].value;
      }}
    }});
    
    const newTotal = (initialTotal - deductedTotal).toFixed(1);
    document.getElementById('totalPaint').innerText = newTotal;
  }}
  
  function toggleDeduction(index) {{
    const item = document.getElementById('item-' + index);
    item.classList.toggle('deducted');
    updateTotal();
  }}
  
  function openPaintModal() {{
    const modal = document.getElementById('paintModal');
    let html = '';
    
    if (paintItems.length === 0) {{
      html = '<p>No paint items found.</p>';
    }} else {{
      paintItems.forEach((item, index) => {{
        html += '<div class="paint-item" id="item-' + index + '">';
        html += '<input type="checkbox" class="paint-item-checkbox" onchange="toggleDeduction(' + index + ')" />';
        html += '<div style="flex: 1;"><strong>Line ' + item.line + '</strong> - ' + item.description + '</div>';
        html += '<div>' + item.value + ' hrs</div>';
        html += '</div>';
      }});
    }}
    
    document.getElementById('paintList').innerHTML = html;
    modal.style.display = 'block';
  }}
  
  function closePaintModal() {{
    document.getElementById('paintModal').style.display = 'none';
  }}
  
  function printModal() {{
    const printWindow = window.open('', '', 'height=600,width=800');
    const techValue = document.getElementById('techInput').value;
    
    const checkboxes = document.querySelectorAll('.paint-item-checkbox');
    let deductedTotal = 0;
    let printContent = '<html><head><title>Labor Assignment</title></head><body style="font-family: Arial; padding: 20px;">';
    
    printContent += '<div style="margin-bottom: 15px;">';
    printContent += '<div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{second_ro_line}</div>';
    printContent += '<div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>';
    printContent += '</div>';
    printContent += '<div style="margin-bottom: 15px;">';
    printContent += '<label style="font-weight: bold; font-size: 14px;">TECH:</label>';
    printContent += '<span style="font-size: 14px; margin-left: 10px;">' + techValue + '</span>';
    printContent += '</div>';
    
    printContent += '<h2>Labor Assignment</h2>';
    
    let totalLabor = 0;
    checkboxes.forEach((checkbox, index) => {{
      if (!checkbox.checked) {{
        printContent += '<div style="padding: 12px 8px; border-bottom: 1px solid #ddd;">';
        printContent += '<input type="checkbox" disabled style="margin-right: 10px;" />';
        printContent += '<strong>Line ' + paintItems[index].line + '</strong> - ' + paintItems[index].description;
        printContent += ' <div style="display: inline; float: right;">' + paintItems[index].value + ' hrs</div>';
        printContent += '</div>';
        totalLabor += paintItems[index].value;
      }} else {{
        deductedTotal += paintItems[index].value;
      }}
    }});
    
    printContent += '<div style="padding: 12px 8px; font-weight: bold; background-color: #f0f0f0; margin-top: 10px; text-align: right;">';
    printContent += 'Total Labor: ' + totalLabor.toFixed(1);
    printContent += '</div>';
    
    printContent += '</body></html>';
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  }}
  
  function saveModal() {{
    const checkboxes = document.querySelectorAll('.paint-item-checkbox');
    let selectedItems = [];
    let deductedTotal = 0;
    
    checkboxes.forEach((checkbox, index) => {{
      if (checkbox.checked) {{
        selectedItems.push(paintItems[index]);
        deductedTotal += paintItems[index].value;
      }}
    }});
    
    const newTotal = (initialTotal - deductedTotal).toFixed(1);
    
    const data = {{
      items: selectedItems,
      totalLabor: newTotal,
      timestamp: new Date().toISOString()
    }};
    
    // Create and download JSON file
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {{ type: 'application/json' }});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'labor-assignment-' + new Date().getTime() + '.json';
    link.click();
    URL.revokeObjectURL(url);
  }}
  
  window.onclick = function(event) {{  
    const modal = document.getElementById('paintModal');
    if (event.target == modal) {{
      modal.style.display = 'none';
    }}
  }}
</script>
"""
        return content


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
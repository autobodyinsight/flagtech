from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text

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
</body>
</html>
"""

@router.post("/parse", response_class=HTMLResponse)
async def parse_ui(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    items = parse_estimate_text(text)

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item.line}</td>
            <td>{item.operation or ''}</td>
            <td>{item.description or ''}</td>
            <td>{item.part_number or ''}</td>
            <td>{item.quantity if item.quantity is not None else ''}</td>
            <td>{item.price if item.price is not None else ''}</td>
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
            <th>Part #</th>
            <th>Qty</th>
            <th>Price</th>
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
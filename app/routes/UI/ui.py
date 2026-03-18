"""Main UI display for FlagTech."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .flagout import get_flagtech_screen_html
from .parts import get_parts_screen_html, get_parts_script
from .dashboard import get_dashboard_screen_html
from .techs import get_techs_screen_html
from .phase import get_phase_screen_html
from .reports import get_reports_screen_html
from .setup import get_setup_screen_html, get_setup_script

try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script, get_estimate_summary_html
except ImportError:
    import sys
    from pathlib import Path

    upload_dir = Path(__file__).parent / "upload_ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script, get_estimate_summary_html


router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home_screen():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>AutobodyOS</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; display: flex; height: 100vh; background-color: #d3d3d3; }}
        .sidebar {{
            width: 150px;
            background-color: #3c4142;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }}
        .nav-box {{
            padding: 15px;
            background-color: #3c4142;
            color: white;
            text-align: center;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            border: 2px solid transparent;
            transition: all 0.2s ease;
        }}
        .nav-box:hover {{ border: 2px solid white; }}
        .nav-box.active {{ background-color: #b22222; border: 2px solid #b22222; }}
        .content-area {{
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            margin-left: 150px;
            background-color: #d3d3d3;
            min-height: 100vh;
        }}
        .screen {{ display: none; }}
        .screen.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="nav-box active" data-screen="upload" onclick="switchScreen('upload', this)">UPLOAD</div>
        <div class="nav-box" data-screen="dashboard" onclick="switchScreen('dashboard', this)">DASHBOARD</div>
        <div class="nav-box" data-screen="parts" onclick="switchScreen('parts', this)">PARTS</div>
        <div class="nav-box" data-screen="tech" onclick="switchScreen('tech', this)">TECHS</div>
        <div class="nav-box" data-screen="phase" onclick="switchScreen('phase', this)">ROADMAP</div>
        <div class="nav-box" data-screen="flagtech" onclick="switchScreen('flagtech', this)">FLAGOUT</div>
        <div class="nav-box" data-screen="reports" onclick="switchScreen('reports', this)">REPORTS</div>
        <div class="nav-box" data-screen="setup" onclick="switchScreen('setup', this)">SETUP</div>
    </div>

    <div class="content-area">
        {get_upload_screen_html()}
        {get_estimate_summary_html()}
        {get_dashboard_screen_html()}
        {get_techs_screen_html()}
        {get_phase_screen_html()}
        {get_parts_screen_html()}
        {get_flagtech_screen_html()}
        {get_reports_screen_html()}
        {get_setup_screen_html()}
    </div>

    <script>
        function switchScreen(screenName, clickedEl) {{
            const screens = document.querySelectorAll('.screen');
            screens.forEach((screen) => screen.classList.remove('active'));

            const navBoxes = document.querySelectorAll('.nav-box');
            navBoxes.forEach((box) => box.classList.remove('active'));

            const target = document.getElementById(screenName);
            if (target) target.classList.add('active');
            if (clickedEl) clickedEl.classList.add('active');
        }}

        switchScreen('upload', document.querySelector('.nav-box[data-screen="upload"]'));
    </script>

    {get_upload_script()}
    {get_parts_script()}
    {get_setup_script()}
</body>
</html>
"""

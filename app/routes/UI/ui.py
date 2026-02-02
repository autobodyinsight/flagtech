"""Main UI display for FlagTech - simplified version with just the display screen."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .flagout import get_flagtech_screen_html
from .ros import get_ros_screen_html
from .techs import get_techs_screen_html
from .dashboard import get_dashboard_screen_html

try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload_ui"
    sys.path.insert(0, str(upload_dir))
    from upload import get_upload_screen_html, get_upload_script


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home_screen():
    """Main UI screen with sidebar navigation."""
    return f"""
<html>
<head>
    <title>FlagTech</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: #f5f5f5;
            margin: 0;
        }}
        .tab-bar {{
            background-color: #505050;
            display: flex;
            gap: 0;
            padding: 0;
            border-bottom: 3px solid #333;
        }}
        .nav-tab {{
            padding: 18px 35px;
            background-color: #666666;
            color: white;
            text-align: center;
            cursor: pointer;
            font-weight: bold;
            border-right: 1px solid #555;
            transition: all 0.3s ease;
            font-size: 14px;
            flex: 1;
            max-width: 200px;
        }}
        .nav-tab:hover {{
            background-color: #707070;
        }}
        .nav-tab.active {{
            background-color: #d32f2f;
            color: white;
            border-bottom: 3px solid #d32f2f;
            margin-bottom: -3px;
        }}
        .content-area {{
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            background-color: white;
        }}
        .screen {{
            display: none;
        }}
        .screen.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="tab-bar">
        <div class="nav-tab active" onclick="switchScreen('dashboard')">DASHBOARD</div>
        <div class="nav-tab" onclick="switchScreen('upload')">UPLOAD</div>
        <div class="nav-tab" onclick="switchScreen('tech')">TECH'S</div>
        <div class="nav-tab" onclick="switchScreen('ros')">RO'S</div>
        <div class="nav-tab" onclick="switchScreen('flagtech')">FLAG TECH</div>
    </div>
    
    <div class="content-area">
        {get_dashboard_screen_html()}
        {get_upload_screen_html()}
        {get_techs_screen_html()}
        {get_ros_screen_html()}
        {get_flagtech_screen_html()}
    </div>
    
    <script>
        function switchScreen(screenName) {{
            const screens = document.querySelectorAll('.screen');
            screens.forEach(screen => screen.classList.remove('active'));
            
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));
            
            document.getElementById(screenName).classList.add('active');
            event.target.classList.add('active');            
            // Load dashboard data if switching to dashboard
            if (screenName === 'dashboard' && typeof loadDashboardDataIfNeeded === 'function') {{
                loadDashboardDataIfNeeded();
            }}        }}
        
        {get_upload_script()}
    </script>
</body>
</html>
"""


# ---------------------------------------------------------
# Individual Screen Endpoints
# ---------------------------------------------------------

@router.get("/tech-screen", response_class=HTMLResponse)
async def tech_screen():
    """Return just the techs screen HTML content."""
    return get_techs_screen_html()


# Note: save-labor and save-refinish endpoints are now in upload_ui/routes.py
"""Main UI display for FlagTech - simplified to just show the main screen."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .flagout import get_flagtech_screen_html
from .ros import get_ros_screen_html
from .techs import get_techs_screen_html
try:
    from .upload_ui.upload import get_upload_screen_html, get_upload_script
except ImportError:
    # Fallback if directory name has space
    import sys
    from pathlib import Path
    upload_dir = Path(__file__).parent / "upload ui"
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
            height: 100vh;
            background-color: #f5f5f5;
        }}
        .sidebar {{
            width: 150px;
            background-color: #505050;
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
            background-color: #666666;
            color: white;
            text-align: center;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        .nav-box:hover {{
            background-color: #707070;
            border: 2px solid white;
        }}
        .nav-box.active {{
            background-color: #d32f2f;
            color: white;
            border: 2px solid #d32f2f;
        }}
        .content-area {{
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            margin-left: 150px;
            background-color: white;
            min-height: 100vh;
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
    <div class="sidebar">
        <div class="nav-box active" onclick="switchScreen('upload')">UPLOAD</div>
        <div class="nav-box" onclick="switchScreen('tech')">TECH'S</div>
        <div class="nav-box" onclick="switchScreen('ros')">RO'S</div>
        <div class="nav-box" onclick="switchScreen('flagtech')">FLAG TECH</div>
    </div>
    
    <div class="content-area">
        {get_upload_screen_html()}
        {get_techs_screen_html()}
        {get_ros_screen_html()}
        {get_flagtech_screen_html()}
    </div>
    
    <script>
        function switchScreen(screenName) {{
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
        }}
        
        {get_upload_script()}
    </script>
</body>
</html>
"""

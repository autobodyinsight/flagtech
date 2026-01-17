# Wix Code Embed Setup Guide

This guide will help you embed the FlagTech UI into your Wix website while keeping the backend on Render.

## Overview

- **Frontend**: Standalone HTML file embedded in Wix
- **Backend**: FastAPI application hosted on Render
- **Communication**: Frontend makes API calls to your Render backend via CORS-enabled endpoints

## Step 1: Deploy Backend to Render

1. Make sure your backend is deployed on Render with these files:
   - `app/main.py` (already configured with CORS)
   - `app/routes/ui.py`
   - `app/services/extractor.py`
   - `app/services/parser.py`
   - `requirements.txt`
   - `render.yaml`

2. Note your Render URL (e.g., `https://your-app.onrender.com`)

## Step 2: Configure the HTML File

1. Open `wix_embed.html`
2. Find line 141: `const API_BASE_URL = 'https://your-app.onrender.com';`
3. Replace `'https://your-app.onrender.com'` with your actual Render URL
4. Save the file

## Step 3: Upload to Wix

### Option A: Using Wix Custom Element (Recommended)

1. Go to your Wix Editor
2. Click **Add** (+) on the left sidebar
3. Select **Embed** → **Custom Element**
4. Choose **HTML iframe**
5. Click **Choose Source** → **Upload File**
6. Upload your modified `wix_embed.html` file
7. Adjust the iframe size to fit your layout (recommended: full width, ~800px height minimum)
8. Click **Apply**

### Option B: Using HTML Embed Code

1. Go to your Wix Editor
2. Click **Add** (+) on the left sidebar
3. Select **Embed** → **HTML iframe**
4. Click **Enter Code**
5. Copy and paste the entire content of `wix_embed.html`
6. Adjust the iframe settings as needed
7. Click **Apply**

### Option C: Using Wix Code (for developers)

1. Enable Wix Developer Mode in your site
2. Go to **Site Structure** → **Code Files**
3. Create a new page (e.g., `FlagTech Page`)
4. In the page code, add an HTML Component:
   ```javascript
   $w.onReady(function () {
       $w("#html1").postMessage({
           type: 'init'
       });
   });
   ```
5. Add an HTML element to your page and paste the `wix_embed.html` content

## Step 4: Test the Integration

1. **Publish** your Wix site
2. Navigate to the page with the embedded FlagTech UI
3. Test uploading a PDF file
4. Verify that:
   - File uploads successfully
   - Visual grid displays
   - "Assign Labor" button opens the modal
   - Print and Save functions work

## Step 5: Production Configuration

### Security Improvements

For production, update [main.py](main.py#L10-L15) CORS settings to restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.wixsite.com",
        "https://www.yourdomain.com"  # Your custom domain
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### Environment Variables on Render

Set these environment variables in your Render dashboard:
- `ALLOWED_ORIGINS`: Your Wix domain (comma-separated if multiple)

Update [main.py](main.py) to use environment variables:

```python
import os

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Issue: "CORS Error" in browser console

**Solution**: 
1. Verify CORS is enabled in [main.py](main.py)
2. Check that your Render backend is running
3. Ensure the API_BASE_URL in `wix_embed.html` is correct

### Issue: File upload fails

**Solution**:
1. Check browser console for errors
2. Verify Render backend is accessible: `https://your-app.onrender.com/docs`
3. Test API endpoint directly: `curl -X POST https://your-app.onrender.com/ui/grid?ajax=true`

### Issue: Modal doesn't display data

**Solution**:
1. Check that the PDF contains recognizable line items
2. Verify the parser is working by testing at `/ui/grid` directly
3. Check browser console for JavaScript errors

### Issue: Wix iframe is too small

**Solution**:
1. In Wix Editor, click on the embedded element
2. Adjust height to at least 800px
3. Set width to "Stretch to fit"
4. Consider making the page full-width for better experience

## File Structure

```
/workspaces/flagtech/
├── wix_embed.html           # Standalone HTML for Wix embed (CONFIGURE THIS)
├── WIX_SETUP.md            # This guide
├── app/
│   ├── main.py             # FastAPI app with CORS enabled
│   ├── routes/
│   │   ├── ui.py           # UI endpoints
│   │   └── estimate.py     # API endpoints
│   └── services/
│       ├── extractor.py    # PDF extraction
│       └── parser.py       # Text parsing
└── requirements.txt
```

## Support

If you encounter issues:
1. Check the browser console for errors (F12)
2. Verify your Render backend is running: visit `/docs` endpoint
3. Test the API endpoints directly using the Swagger UI
4. Check Render logs for backend errors

## Next Steps

After successful setup:
1. Customize the UI colors/styling in `wix_embed.html` to match your brand
2. Add authentication if needed
3. Implement the TECH'S, RO'S, and FLAG TECH screens
4. Set up a database for storing labor assignments
5. Add user management features

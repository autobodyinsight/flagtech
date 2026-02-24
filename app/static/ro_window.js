// RO Window HTML generator for new window popup
function getRoWindowHtml(ro) {
    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>RO Window</title>
            <style>
                body { margin:0; font-family: Arial, sans-serif; background:#f7f7f7; }
                .ro-banner {
                    position:fixed;
                    top:0; left:0; right:0;
                    background:#1E90FF;
                    color:#fff;
                    padding:18px 32px;
                    z-index:1000;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08);
                    display:flex;
                    flex-wrap:wrap;
                    gap:32px 48px;
                    align-items:center;
                    font-size:18px;
                }
                .ro-banner-label { font-weight:bold; margin-right:6px; }
                .ro-banner-row { display:flex; gap:24px; flex-wrap:wrap; }
                .ro-content {
                    margin-top:90px;
                    padding:32px;
                    min-height:400px;
                }
            </style>
        </head>
        <body>
            <div class="ro-banner">
                <div class="ro-banner-row">
                    <span class="ro-banner-label">RO#:</span> <span>${ro.ro}</span>
                    <span class="ro-banner-label">Customer:</span> <span>${ro.customer || '-'}</span>
                    <span class="ro-banner-label">Phone:</span> <span>${ro.phone || '-'}</span>
                    <span class="ro-banner-label">Insurance:</span> <span>${ro.insurance || '-'}</span>
                    <span class="ro-banner-label">Claim#:</span> <span>${ro.claim_number || '-'}</span>
                    <span class="ro-banner-label">Vehicle:</span> <span>${ro.vehicle || '-'}</span>
                    <span class="ro-banner-label">IN Date:</span> <span>${ro.in_date || '-'}</span>
                    <span class="ro-banner-label">ECD Date:</span> <span>${ro.ecd_date || '-'}</span>
                </div>
            </div>
            <div class="ro-content">
                <!-- Empty content area for future tabs/sections -->
            </div>
        </body>
        </html>
    `;
}

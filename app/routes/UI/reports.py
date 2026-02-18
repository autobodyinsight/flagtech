from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.services.auth import get_current_user
from app.services.db import get_closed_ros_and_summary

router = APIRouter()

# API endpoint for JS fetch
@router.get("/api/reports_data", response_class=JSONResponse)
async def reports_data(user=Depends(get_current_user)):
    closed_ros, summary = get_closed_ros_and_summary()
    summary_data = [
        {"category": k, "sales": v["sales"], "gp_percent": v["gp_percent"], "gp_dollar": v["gp_dollar"]}
        for k, v in summary.items()
    ]
    # Convert closed_ros rows to dicts if needed
    ros = []
    for row in closed_ros:
        if isinstance(row, dict):
            ros.append(row)
        elif hasattr(row, '_asdict'):
            ros.append(row._asdict())
        elif hasattr(row, '__dict__'):
            ros.append(dict(row.__dict__))
        else:
            # fallback: assume tuple with known columns
            ros.append({
                "ro_number": row[0], "vehicle": row[1], "tech": row[2], "parts": row[3], "insurance": row[4], "customer": row[5], "in_date": row[6], "picked_up": row[7], "hours": row[8], "total": row[9], "status": row[10], "gp_percent": row[11], "gp_dollar": row[12], "type": row[13]
            })
    return {"summary": summary_data, "closed_ros": ros}
"""REPORTS window for summary metrics and closed RO list."""

def get_reports_screen_html():
    """Return the HTML content for the REPORTS window."""
    return r'''
    <div id="reports" class="screen" style="padding:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
            <h1 style="text-align:center; margin:0; flex:1;">REPORTS</h1>
            <button style="padding:10px 16px; background:var(--brand-red, #d32f2f); color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Print</button>
        </div>
        <!-- Summary Metrics Section -->
        <div style="margin-bottom:32px;">
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#f5f5f5;">
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">CATEGORY</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">TOTAL SALES</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">TOTAL GP %</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">TOTAL GP $</th>
                    </tr>
                </thead>
                <tbody id="reportsSummaryBody">
                    <tr><td colspan="4" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        <!-- Closed RO List Section -->
        <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 18px 0; color:#333;">Closed Repair Orders</h3>
            <div style="overflow-x:auto;">
                <table id="reportsRoListTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr class="dashboard-header-row">
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">RO#</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">Vehicle</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">Customer</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">Insurance</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">In</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">Picked Up</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">HRS</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">Total</th>
                        </tr>
                    </thead>
                    <tbody id="reportsRoListBody">
                        <tr>
                            <td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <style>
        .dashboard-header-row th, .dashboard-header-cell {
            font-family: inherit;
            font-size: 16px;
            font-weight: bold;
            background: #23272a;
            color: #fff;
        }
        .reports-green-bold {
            color: #2e7d32;
            font-weight: bold;
        }
    </style>
    <script>
    async function loadReportsData() {
        try {
            const resp = await fetch('/api/reports_data');
            const data = await resp.json();
            // Render summary
            const summaryBody = document.getElementById('reportsSummaryBody');
            summaryBody.innerHTML = '';
            for (const row of data.summary) {
                summaryBody.innerHTML += `<tr>
                    <td style='padding:12px;'>${row.category}</td>
                    <td style='padding:12px;'>$${row.sales.toLocaleString()}</td>
                    <td style='padding:12px;'>${row.gp_percent}%</td>
                    <td style='padding:12px;'>$${row.gp_dollar.toLocaleString()}</td>
                </tr>`;
            }
            // Render closed RO list
            const roBody = document.getElementById('reportsRoListBody');
            roBody.innerHTML = '';
            if (data.closed_ros.length === 0) {
                roBody.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#999;'>No closed repair orders found.</td></tr>`;
            } else {
                for (const ro of data.closed_ros) {
                    roBody.innerHTML += `<tr>
                        <td style='padding:12px;'>${ro.ro_number || ''}</td>
                        <td style='padding:12px;'>${ro.vehicle || ''}</td>
                        <td style='padding:12px;'>${ro.customer || ''}</td>
                        <td style='padding:12px;'>${ro.insurance || ''}</td>
                        <td style='padding:12px;'>${ro.in_date || ''}</td>
                        <td style='padding:12px;'>${ro.picked_up || ''}</td>
                        <td style='padding:12px; text-align:right;'>${ro.hours || ''}</td>
                        <td style='padding:12px; text-align:right;'>$${ro.total ? ro.total.toLocaleString() : ''}</td>
                    </tr>`;
                }
            }
        } catch (e) {
            document.getElementById('reportsSummaryBody').innerHTML = `<tr><td colspan='4' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            document.getElementById('reportsRoListBody').innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
        }
    }
    // Load data when REPORTS screen is shown
    document.addEventListener('DOMContentLoaded', function() {
        const reportsTab = document.querySelector('.nav-tab[onclick*="reports"]');
        if (reportsTab) {
            reportsTab.addEventListener('click', loadReportsData);
        }
    });
    </script>
    '''
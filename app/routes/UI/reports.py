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
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">TOTAL SALES</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">TOTAL GP %</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left;">TOTAL GP $</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="color:#2e7d32; font-weight:bold;">
                        <td style="padding:12px;">RO'S</td>
                        <td style="padding:12px;">$10354</td>
                        <td style="padding:12px;">40%</td>
                        <td style="padding:12px;">$4141.60</td>
                    </tr>
                    <tr>
                        <td style="padding:12px;">PARTS</td>
                        <td style="padding:12px;">$5412.32</td>
                        <td style="padding:12px;">20%</td>
                        <td style="padding:12px;">$1080.46</td>
                    </tr>
                    <tr>
                        <td style="padding:12px;">LABOR</td>
                        <td style="padding:12px;">$1200</td>
                        <td style="padding:12px;">20%</td>
                        <td style="padding:12px;">$240</td>
                    </tr>
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
    '''
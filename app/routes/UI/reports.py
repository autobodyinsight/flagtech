from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.db import get_closed_ros_and_summary

router = APIRouter()

@router.get("/api/reports_data", response_class=JSONResponse)
async def reports_data():
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
            <div style="display:flex; flex-direction:column; align-items:flex-start; gap:10px; min-width:260px;">
                <label style="display:flex; align-items:center; gap:10px; cursor:pointer; user-select:none;">
                    <span style="font-weight:700; color:#333;">Status</span>
                    <span class="reports-toggle-wrap">
                        <input id="reportsStatusToggle" type="checkbox" class="reports-toggle-input" />
                        <span class="reports-toggle-slider"></span>
                    </span>
                    <span id="reportsStatusLabel" style="font-weight:700; color:#333; min-width:68px;">CLOSED</span>
                </label>
                <div style="display:flex; gap:10px; align-items:flex-end; flex-wrap:wrap;">
                    <label style="display:flex; flex-direction:column; gap:4px; font-size:12px; color:#555; font-weight:600;">
                        <span>Start Date</span>
                        <input id="reportsStartDate" type="date" style="padding:7px 8px; border:1px solid #ccc; border-radius:4px; min-width:130px;" />
                    </label>
                    <label style="display:flex; flex-direction:column; gap:4px; font-size:12px; color:#555; font-weight:600;">
                        <span>End Date</span>
                        <input id="reportsEndDate" type="date" style="padding:7px 8px; border:1px solid #ccc; border-radius:4px; min-width:130px;" />
                    </label>
                </div>
            </div>
            <h1 style="text-align:center; margin:0; flex:1;">REPORTS</h1>
            <div style="position:relative;">
                <button id="reportsPrintTrigger" class="mini-popup-trigger" onclick="reportsOpenPrintOptionsModal()" style="padding:10px 16px; background:var(--brand-red, #d32f2f); color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Print</button>
                <div id="reportsPrintOptionsModal" class="mini-popup-panel" style="display:none; right:0; left:auto;">
                    <h2 style="margin:0 0 14px 0; color:#333; font-size:18px;">Print Closed RO List</h2>
                    <p style="margin:0 0 12px 0; font-weight:bold; color:#555;">Print by:</p>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <button onclick="reportsPrintClosedRos('ro')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">RO</button>
                        <button onclick="reportsPrintClosedRos('insurance')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">INSURANCE</button>
                        <button onclick="reportsPrintClosedRos('tech')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">TECH</button>
                        <button onclick="reportsPrintClosedRos('estimator')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">ESTIMATOR</button>
                    </div>
                </div>
            </div>
        </div>
        <!-- Summary Metrics Section -->
        <div style="margin-bottom:32px;">
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#3c4142;">
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">CATEGORY</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">TOTAL SALES</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">TOTAL GP %</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">TOTAL GP $</th>
                    </tr>
                </thead>
                <tbody id="reportsSummaryBody">
                    <tr><td colspan="4" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        <!-- Closed RO List Section -->
        <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 id="reportsRoSectionHeader" style="margin:0 0 18px 0; color:#333;">Closed Repair Orders</h3>
            <div style="overflow-x:auto;">
                <table id="reportsRoListTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr class="dashboard-header-row">
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">RO#</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">Vehicle</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; cursor:pointer; user-select:none;">Insurance</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">HRS</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">PARTS-S</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">PARTS-C</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">LABOR-S</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">LABOR-C</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">TOTAL-S</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right; cursor:pointer; user-select:none;">TOTAL-C</th>
                        </tr>
                    </thead>
                    <tbody id="reportsRoListBody">
                        <tr>
                            <td colspan="10" style="padding:20px; text-align:center; color:#999;">Loading...</td>
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
        .mini-popup-panel {
            position: absolute;
            top: 100%;
            left: 0;
            z-index: 1000;
            background: #fff;
            border: 2px solid #b22222;
            border-radius: 6px;
            padding: 12px;
            min-width: 300px;
            max-width: 500px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            margin-top: 4px;
            opacity: 0;
            transform: translateY(-6px);
            transition: opacity 0.18s ease, transform 0.18s ease;
            pointer-events: none;
        }
        .mini-popup-panel.open {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }
        .reports-toggle-wrap {
            position: relative;
            display: inline-block;
            width: 46px;
            height: 24px;
        }
        .reports-toggle-input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .reports-toggle-slider {
            position: absolute;
            cursor: pointer;
            inset: 0;
            background-color: #777;
            border-radius: 999px;
            transition: background-color 0.2s ease;
        }
        .reports-toggle-slider:before {
            content: "";
            position: absolute;
            height: 18px;
            width: 18px;
            left: 3px;
            top: 3px;
            background-color: #fff;
            border-radius: 50%;
            transition: transform 0.2s ease;
        }
        .reports-toggle-input:checked + .reports-toggle-slider {
            background-color: #2e7d32;
        }
        .reports-toggle-input:checked + .reports-toggle-slider:before {
            transform: translateX(22px);
        }
    </style>
    <script>
    let reportsDataCache = { summary: [], closed_ros: [], open_ros: [] };
    let reportsUiState = { status: 'closed', startDate: '', endDate: '' };
    let reportsRoLookup = {};

    function formatReportsPercent(value) {
        const amount = Number(value || 0);
        return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function formatReportsMoney(value) {
        const amount = Number(value || 0);
        return '$' + amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function computeGpValues(sales, cost) {
        const safeSales = Number(sales || 0);
        const safeCost = Number(cost || 0);
        const gpDollar = safeSales - safeCost;
        const gpPercent = safeSales > 0 ? (gpDollar / safeSales) * 100 : 0;
        return { gpDollar, gpPercent };
    }

    function formatReportsHours(value) {
        const amount = Number(value || 0);
        if (!Number.isFinite(amount)) {
            return '0.0';
        }
        return amount.toFixed(1);
    }

    function reportsResolveGroupName(row, groupKey) {
        const source = row || {};
        if (groupKey === 'insurance') {
            return String(source.insurance || source.insurance_company || '').trim();
        }
        if (groupKey === 'tech') {
            return String(source.tech || source.tech_name || source.technician || '').trim();
        }
        if (groupKey === 'estimator') {
            return String(source.estimator || source.written_by || source.estimate_by || '').trim();
        }
        return String(source[groupKey] || '').trim();
    }

    function reportsNormalizeStatus(row, fallbackStatus) {
        const explicit = String((row || {}).status || '').trim().toLowerCase();
        if (explicit === 'open' || explicit === 'closed') return explicit;

        const phase = String((row || {}).phase || '').trim().toLowerCase();
        if (phase === 'complete' || phase === 'complete/finish' || phase === 'closed') return 'closed';
        if (phase) return 'open';

        return String(fallbackStatus || 'closed').trim().toLowerCase() === 'open' ? 'open' : 'closed';
    }

    function reportsResolveRowDateIso(row) {
        const candidates = [row?.in_date, row?.picked_up, row?.closed_at, row?.saved_at, row?.date];
        for (const value of candidates) {
            const text = String(value || '').trim();
            if (!text) continue;
            if (/^\d{4}-\d{2}-\d{2}$/.test(text)) return text;
            const parsed = new Date(text);
            if (!Number.isNaN(parsed.getTime())) {
                const y = parsed.getFullYear();
                const m = String(parsed.getMonth() + 1).padStart(2, '0');
                const d = String(parsed.getDate()).padStart(2, '0');
                return `${y}-${m}-${d}`;
            }
        }
        return '';
    }

    function reportsBuildOpenRowsFromDashboardRows(rows) {
        const list = Array.isArray(rows) ? rows : [];
        return list.map((row) => {
            const status = reportsNormalizeStatus(row, 'open');
            return {
                ro_number: row.ro || row.ro_number || '',
                vehicle: row.vehicle || '',
                insurance: row.insurance || row.insurance_company || '',
                hours: Number(row.hours || 0),
                total_sales: Number((row.total_sales ?? row.total) || 0),
                total_cost: Number(row.total_cost || 0),
                parts_sales: Number(row.parts_sales || 0),
                parts_cost: Number(row.parts_cost || 0),
                labor_sales: Number(row.labor_sales || 0),
                labor_cost: Number(row.labor_cost || 0),
                in_date: row.in_date || '',
                picked_up: row.picked_up || '',
                closed_at: row.closed_at || '',
                saved_at: row.saved_at || '',
                phase: row.phase || '',
                status,
            };
        });
    }

    function reportsGetFilteredRows() {
        const targetStatus = reportsUiState.status === 'open' ? 'open' : 'closed';
        const sourceRows = targetStatus === 'open'
            ? (Array.isArray(reportsDataCache.open_ros) ? reportsDataCache.open_ros : [])
            : (Array.isArray(reportsDataCache.closed_ros) ? reportsDataCache.closed_ros : []);

        const startDate = String(reportsUiState.startDate || '').trim();
        const endDate = String(reportsUiState.endDate || '').trim();

        return sourceRows.filter((row) => {
            const normalizedStatus = reportsNormalizeStatus(row, targetStatus);
            if (normalizedStatus !== targetStatus) return false;

            if (!startDate && !endDate) return true;
            const rowDate = reportsResolveRowDateIso(row);
            if (!rowDate) return false;
            if (startDate && rowDate < startDate) return false;
            if (endDate && rowDate > endDate) return false;
            return true;
        });
    }

    function reportsRenderRoList() {
        const roBody = document.getElementById('reportsRoListBody');
        const sectionHeader = document.getElementById('reportsRoSectionHeader');
        if (!roBody) return;

        const isOpenView = reportsUiState.status === 'open';
        const rows = reportsGetFilteredRows();
        reportsRoLookup = {};
        rows.forEach((row) => {
            const key = String(row?.ro_number || row?.ro || '').trim();
            if (key) reportsRoLookup[key] = row;
        });
        if (sectionHeader) {
            sectionHeader.textContent = isOpenView ? 'Open Repair Orders' : 'Closed Repair Orders';
        }

        roBody.innerHTML = '';
        if (!rows.length) {
            const noneLabel = isOpenView ? 'No open repair orders found.' : 'No closed repair orders found.';
            roBody.innerHTML = `<tr><td colspan='10' style='padding:20px; text-align:center; color:#999;'>${noneLabel}</td></tr>`;
            return;
        }
        roBody.innerHTML = reportsBuildRoRowsHtml(rows);
    }

    function reportsApplyFiltersFromControls() {
        const toggleEl = document.getElementById('reportsStatusToggle');
        const statusLabelEl = document.getElementById('reportsStatusLabel');
        const startDateEl = document.getElementById('reportsStartDate');
        const endDateEl = document.getElementById('reportsEndDate');

        reportsUiState.status = toggleEl && toggleEl.checked ? 'open' : 'closed';
        reportsUiState.startDate = String(startDateEl?.value || '').trim();
        reportsUiState.endDate = String(endDateEl?.value || '').trim();

        if (statusLabelEl) {
            statusLabelEl.textContent = reportsUiState.status === 'open' ? 'OPENED' : 'CLOSED';
        }

        reportsRenderRoList();
    }

    function reportsNormalizeIsoDateForInput(value) {
        if (!value) return '';
        const text = String(value);
        if (text.includes('T')) return text.split('T')[0];
        const match = text.match(/^(\d{4}-\d{2}-\d{2})/);
        return match ? match[1] : '';
    }

    function reportsFormatDateMmDdYyyy(value) {
        const iso = reportsNormalizeIsoDateForInput(value);
        if (!iso) return '-';
        const [yyyy, mm, dd] = iso.split('-');
        if (!yyyy || !mm || !dd) return '-';
        return `${mm}/${dd}/${yyyy}`;
    }

    function reportsOpenClosedRoWindow(event, roNumber) {
        if (event) event.stopPropagation();
        const roKey = String(roNumber || '').trim();
        const ro = reportsRoLookup[roKey];
        if (!ro) {
            alert('RO not found.');
            return;
        }

        const closedDateText = reportsFormatDateMmDdYyyy(ro.closed_at || ro.closed_date || ro.updated_at || ro.picked_up || '');
        const inDateText = reportsFormatDateMmDdYyyy(ro.in_date);
        const ecdDateText = reportsFormatDateMmDdYyyy(ro.ecd_date);
        const pickedUpDateText = reportsFormatDateMmDdYyyy(ro.picked_up);

        const icons = {
            notepad: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="6" width="18" height="16" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="10" x2="19" y2="10" stroke="white" stroke-width="2"/><line x1="9" y1="14" x2="19" y2="14" stroke="white" stroke-width="2"/><line x1="9" y1="18" x2="15" y2="18" stroke="white" stroke-width="2"/></svg>`,
            estimate: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="3" width="16" height="22" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="8" x2="19" y2="8" stroke="white" stroke-width="2"/><rect x="9" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="9" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><line x1="9" y1="22" x2="19" y2="22" stroke="white" stroke-width="2"/></svg>`,
            tech: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="9" r="4" stroke="white" stroke-width="2"/><rect x="7" y="17" width="14" height="6" rx="3" stroke="white" stroke-width="2"/><path d="M21 21l2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/><path d="M7 21l-2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>`,
            cart: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="14" r="9" stroke="white" stroke-width="2"/><circle cx="14" cy="14" r="5.2" stroke="white" stroke-width="2"/><circle cx="14" cy="14" r="1.7" fill="white"/><path d="M14 5.8v3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M14 19v3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M5.8 14h3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M19 14h3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/></svg>`,
            credit: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="7" width="20" height="14" rx="3" stroke="white" stroke-width="2"/><rect x="7" y="17" width="6" height="3" rx="1.5" stroke="white" stroke-width="2"/><line x1="4" y1="12" x2="24" y2="12" stroke="white" stroke-width="2"/></svg>`
        };

        const sidebarHtml = `
            <div id="roSidebar" style="position:fixed; left:0; top:var(--ro-header-height, 170px); height:calc(100vh - var(--ro-header-height, 170px)); width:64px; background:#23272a; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:38px; z-index:100; box-shadow:2px 0 8px rgba(0,0,0,0.08);">
                <button class="ro-sidebar-btn active" data-view="notes" style="background:none; border:none; padding:0; cursor:pointer;">${icons.notepad}</button>
                <button class="ro-sidebar-btn" data-view="estimate" style="background:none; border:none; padding:0; cursor:pointer;">${icons.estimate}</button>
                <button class="ro-sidebar-btn" data-view="tech" style="background:none; border:none; padding:0; cursor:pointer;">${icons.tech}</button>
                <button class="ro-sidebar-btn" data-view="parts" style="background:none; border:none; padding:0; cursor:pointer;">${icons.cart}</button>
                <button class="ro-sidebar-btn" data-view="payments" style="background:none; border:none; padding:0; cursor:pointer;">${icons.credit}</button>
            </div>
        `;

        const bannerHtml = `
            <div id="roHeaderBar" style="background:#23272a; color:#fff; padding:16px 24px 18px 24px; border-bottom:3px solid #d32f2f; position:relative; min-height:132px; z-index:120;">
                <div style="font-size:20px; font-weight:bold; margin-bottom:10px;">RO Window</div>
                <div style="position:absolute; top:14px; left:50%; transform:translateX(-50%); font-weight:900; letter-spacing:1.5px; font-size:20px; color:#fff;">CLOSED</div>
                <div style="position:absolute; top:58px; right:24px; display:flex; flex-direction:column; align-items:flex-start; gap:6px; z-index:10;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="ro-header-label" style="margin-right:0;">Picked Up:</span>
                        <span class="ro-header-date-text">${pickedUpDateText}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="ro-header-label" style="margin-right:0;">Closed:</span>
                        <span class="ro-header-date-text">${closedDateText}</span>
                    </div>
                    <div style="position:relative; margin-top:4px;">
                        <button type="button" id="roPopupPrintButton" class="mini-popup-trigger" style="padding:7px 18px; background:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold; font-size:15px; cursor:pointer;">Print</button>
                        <div id="roPrintOptionsModal" class="mini-popup-panel" style="display:none; right:0; left:auto; top:100%;">
                            <h2 style="margin:0 0 14px 0; color:#333; font-size:18px;">Print RO</h2>
                            <p style="margin:0 0 12px 0; font-weight:bold; color:#555;">Print by:</p>
                            <div style="display:flex; flex-direction:column; gap:8px;">
                                <button id="roPrintOptionBill" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Bill</button>
                                <button id="roPrintOptionServiceOrder" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Service Order</button>
                                <button id="roPrintOptionParts" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Parts</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:20px 28px; margin-right:260px; align-items:start;">
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <div><span class="ro-header-label">RO#:</span> <span class="ro-header-value">${reportsEscapeHtml(ro.ro_number || ro.ro || '')}</span></div>
                        <div><span class="ro-header-label">Customer:</span> <span class="ro-header-value">${reportsEscapeHtml(ro.customer || '-')}</span></div>
                        <div><span class="ro-header-label">Phone:</span> <span class="ro-header-value">${reportsEscapeHtml(ro.phone || '-')}</span></div>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <div><span class="ro-header-label">Insurance:</span> <span class="ro-header-value">${reportsEscapeHtml(ro.insurance || '-')}</span></div>
                        <div><span class="ro-header-label">Claim#:</span> <span class="ro-header-value">${reportsEscapeHtml(ro.claim_number || '-')}</span></div>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <div><span class="ro-header-label">Vehicle:</span> <span class="ro-header-value">${reportsEscapeHtml(ro.vehicle || '-')}</span></div>
                        <div><span class="ro-header-label">IN Date:</span> <span class="ro-header-date-text">${inDateText}</span></div>
                        <div><span class="ro-header-label">ECD Date:</span> <span class="ro-header-date-text">${ecdDateText}</span></div>
                    </div>
                </div>
            </div>
            <div id="roWindowContent" style="padding:32px 32px 32px 88px; min-height:180px; background:#fff; color:#23272a; font-size:18px;"></div>
        `;

        const win = window.open('', `Reports_Closed_RO_${roKey}`, 'width=900,height=640,scrollbars=yes,resizable=yes');
        if (!win) {
            alert('Popup blocked. Please allow popups for this site.');
            return;
        }

        win.document.title = `Closed RO Window - ${roKey}`;
        win.document.body.innerHTML = `<div style='display:flex; flex-direction:row; height:100vh; width:100vw; background:#f2f2f2;'>${sidebarHtml}<div style='flex:1; display:flex; flex-direction:column; min-width:0;'>${bannerHtml}</div></div>`;

        const style = win.document.createElement('style');
        style.textContent = `
            body { margin:0; font-family:Segoe UI,Arial,sans-serif; background:#f2f2f2; }
            #roSidebar svg { display:block; margin:0 auto; }
            .ro-sidebar-btn { opacity:0.72; transition:opacity 0.15s ease, transform 0.15s ease; }
            .ro-sidebar-btn:hover { opacity:1; transform:translateY(-1px); }
            .ro-sidebar-btn.active { opacity:1; }
            .ro-header-label { color:#d32f2f; font-weight:700; margin-right:6px; white-space:nowrap; }
            .ro-header-value { color:#fff; font-weight:600; }
            .ro-header-date-text { color:#fff; font-weight:600; min-width:110px; }
            .ro-window-card { background:#fafafa; border:1px solid #ddd; border-radius:8px; padding:14px; }
            .mini-popup-panel {
                position: absolute;
                top: 100%;
                left: 0;
                z-index: 1000;
                background: #fff;
                border: 2px solid #b22222;
                border-radius: 6px;
                padding: 12px;
                min-width: 300px;
                max-width: 500px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                margin-top: 4px;
                opacity: 0;
                transform: translateY(-6px);
                transition: opacity 0.18s ease, transform 0.18s ease;
                pointer-events: none;
            }
            .mini-popup-panel.open {
                opacity: 1;
                transform: translateY(0);
                pointer-events: auto;
            }
        `;
        win.document.head.appendChild(style);

        const roDoc = win.document;
        const contentEl = roDoc.getElementById('roWindowContent');
        const printBtn = roDoc.getElementById('roPopupPrintButton');
        const printPanel = roDoc.getElementById('roPrintOptionsModal');
        const headerEl = roDoc.getElementById('roHeaderBar');
        if (headerEl) {
            const h = Math.ceil(headerEl.getBoundingClientRect().height);
            roDoc.documentElement.style.setProperty('--ro-header-height', `${h}px`);
        }

        function popupEsc(v) {
            return String(v === null || v === undefined ? '' : v)
                .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        }

        function popupMoney(v) {
            const n = Number(v || 0);
            return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function popupToNumber(value, fallback = 0) {
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : fallback;
        }

        function popupNormalizeDisplayNumber(value) {
            const numeric = popupToNumber(value, 0);
            return Number.isInteger(numeric)
                ? String(numeric)
                : numeric.toFixed(2).replace(/\.00$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
        }

        function popupFormatDate(value) {
            return reportsFormatDateMmDdYyyy(value);
        }

        function popupExtractLineNumber(value) {
            if (value === null || value === undefined) return null;
            const match = String(value).match(/\d+/);
            if (!match) return null;
            const parsed = Number(match[0]);
            return Number.isFinite(parsed) ? parsed : null;
        }

        function popupSameRo(a, b) {
            const left = String(a || '').trim();
            const right = String(b || '').trim();
            if (!left || !right) return false;
            if (left === right) return true;
            if (/^\d+$/.test(left) && /^\d+$/.test(right)) {
                return Number(left) === Number(right);
            }
            return left.toLowerCase() === right.toLowerCase();
        }

        function popupFormatDateTime(value) {
            const source = String(value || '').trim();
            if (!source) return '-';
            const dt = new Date(source);
            if (Number.isNaN(dt.getTime())) return source;
            const mm = String(dt.getMonth() + 1).padStart(2, '0');
            const dd = String(dt.getDate()).padStart(2, '0');
            const yyyy = String(dt.getFullYear());
            const hh = String(dt.getHours()).padStart(2, '0');
            const min = String(dt.getMinutes()).padStart(2, '0');
            return `${mm}/${dd}/${yyyy} ${hh}:${min}`;
        }

        function popupBuildUnifiedLinesFromSections(sections) {
            const byLine = new Map();

            function getLineRecord(lineNumber) {
                if (!byLine.has(lineNumber)) {
                    byLine.set(lineNumber, {
                        lineNumber,
                        description: '',
                        labor: 0,
                        paint: 0,
                        qty: null,
                        partNumber: '',
                        extendedPrice: null,
                    });
                }
                return byLine.get(lineNumber);
            }

            (Array.isArray(sections) ? sections : []).forEach((section) => {
                const sectionKey = String(section?.key || '').toLowerCase();
                const items = Array.isArray(section?.items) ? section.items : [];
                items.forEach((item) => {
                    const lineNumber = popupExtractLineNumber(item?.line ?? item?.lineNumber);
                    if (lineNumber === null) return;
                    const record = getLineRecord(lineNumber);
                    const desc = String(item?.description || '').trim();
                    if (desc && !record.description) record.description = desc;

                    if (sectionKey === 'labor') {
                        record.labor = popupToNumber(item?.value, 0);
                        return;
                    }
                    if (sectionKey === 'paint') {
                        record.paint = popupToNumber(item?.value, 0);
                        return;
                    }
                    if (sectionKey === 'parts') {
                        const qtyRaw = item?.qty;
                        if (qtyRaw !== null && qtyRaw !== undefined && String(qtyRaw).trim() !== '') {
                            record.qty = popupToNumber(qtyRaw, 0);
                        }
                        const partNumber = String(item?.partNumber || item?.part_number || item?.part_no || item?.['part#'] || item?.pn || '').trim();
                        if (partNumber) record.partNumber = partNumber;
                        const extPriceRaw = item?.extendedPrice ?? item?.price;
                        if (extPriceRaw !== null && extPriceRaw !== undefined && String(extPriceRaw).trim() !== '') {
                            record.extendedPrice = popupToNumber(extPriceRaw, 0);
                        }
                    }
                });
            });

            return Array.from(byLine.values()).sort((a, b) => a.lineNumber - b.lineNumber);
        }

        function popupGetUnifiedEstimateLines(estimate) {
            return Array.isArray(estimate?.unified_lines)
                ? [...estimate.unified_lines].sort((a, b) => popupToNumber(a?.lineNumber, 0) - popupToNumber(b?.lineNumber, 0))
                : popupBuildUnifiedLinesFromSections(Array.isArray(estimate?.sections) ? estimate.sections : []);
        }

        function roTogglePrintPopup(panel) {
            if (!panel) return;
            const isOpen = panel.classList.contains('open');
            roDoc.querySelectorAll('.mini-popup-panel.open').forEach((openPanel) => {
                openPanel.classList.remove('open');
                openPanel.style.display = 'none';
            });
            if (!isOpen) {
                panel.style.display = 'block';
                panel.classList.add('open');
            }
        }

        function roClosePrintOptionsModal() {
            if (!printPanel) return;
            printPanel.classList.remove('open');
            printPanel.style.display = 'none';
        }

        function roOpenPrintWindow(title, bodyHtml, options = {}) {
            const printWindow = window.open('', '_blank');
            if (!printWindow) {
                alert('Unable to open print preview. Please allow pop-ups for this site.');
                return;
            }
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>${popupEsc(title)}</title>
                        <style>
                            @media print { @page { margin: 0.5in; } body { margin: 0; } }
                            body { font-family: Arial, sans-serif; color:#222; padding:20px; }
                            .header { text-align:center; margin-bottom:16px; border-bottom:2px solid #b22222; padding-bottom:8px; }
                            table { width:100%; border-collapse:collapse; margin-top:10px; }
                            thead th { background:#3c4142; color:#fff; text-align:left; padding:8px; font-size:12px; }
                            tbody td { padding:8px; border-bottom:1px solid #eee; font-size:12px; }
                            .num { text-align:right; }
                        </style>
                    </head>
                    <body>${bodyHtml}</body>
                </html>
            `);
            printWindow.document.close();
            printWindow.focus();
            if (options.immediatePrint) {
                printWindow.print();
                return;
            }
            setTimeout(() => printWindow.print(), 250);
        }

        async function roPrintBill() {
            roClosePrintOptionsModal();
            try {
                const [res, paymentsRes] = await Promise.all([
                    popupFetchJson(`/api/ro-estimate?ro=${encodeURIComponent(roKey)}`),
                    popupFetchJson(`/api/payments/ro?ro=${encodeURIComponent(roKey)}`),
                ]);
                const estimate = res.estimate || {};
                const lines = popupGetUnifiedEstimateLines(estimate);
                const paymentRow = paymentsRes?.row || {};
                const insuranceTotal = popupToNumber(paymentRow.insurance_total ?? ro.insurance_pay ?? 0, 0);
                const customerTotal = popupToNumber(paymentRow.customer_total ?? ro.customer_pay ?? 0, 0);
                const grandTotal = insuranceTotal + customerTotal;
                const linesHtml = lines.map((line) => {
                    const qty = line?.qty;
                    const qtyDisplay = qty === null || qty === undefined || String(qty).trim() === '' ? '-' : popupNormalizeDisplayNumber(qty);
                    const priceDisplay = (line?.extendedPrice === null || line?.extendedPrice === undefined || String(line?.extendedPrice).trim() === '')
                        ? '-'
                        : popupNormalizeDisplayNumber(line?.extendedPrice);
                    return `
                        <tr>
                            <td>${popupEsc(line?.lineNumber || '-')}</td>
                            <td>${popupEsc(String(line?.description || '').trim() || '-')}</td>
                            <td>${popupEsc(String(line?.partNumber || '').trim() || '-')}</td>
                            <td class="num">${popupEsc(qtyDisplay)}</td>
                            <td class="num">${popupEsc(popupNormalizeDisplayNumber(line?.labor || 0))}</td>
                            <td class="num">${popupEsc(popupNormalizeDisplayNumber(line?.paint || 0))}</td>
                            <td class="num">${popupEsc(priceDisplay)}</td>
                        </tr>
                    `;
                }).join('');

                roOpenPrintWindow(
                    `RO ${roKey} Bill`,
                    `
                        <div class="header" style="text-align:left;">
                            <div style="font-size:56px; font-weight:800; line-height:1; margin-bottom:8px;">RO #${popupEsc(roKey || '-')}</div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:6px;">
                                <div style="font-size:20px; font-weight:600;">Vehicle: ${popupEsc(ro.vehicle || '-')}</div>
                                <div style="font-size:30px; font-weight:800; letter-spacing:1px;">INVOICE</div>
                            </div>
                            <div style="font-size:18px; font-weight:600;">Customer: ${popupEsc(ro.customer || '-')} | Insurance: ${popupEsc(ro.insurance || '-')}</div>
                            <div style="font-size:16px; font-weight:600; margin-top:4px;">In ${popupEsc(inDateText)} | ECD ${popupEsc(ecdDateText)} | Picked Up ${popupEsc(pickedUpDateText)} | Closed ${popupEsc(closedDateText)}</div>
                        </div>
                        <table>
                            <thead>
                                <tr><th>Line #</th><th>Description</th><th>Part #</th><th class="num">Qty</th><th class="num">Labor</th><th class="num">Paint</th><th class="num">Price</th></tr>
                            </thead>
                            <tbody>${linesHtml || '<tr><td colspan="7" style="text-align:center; color:#777;">No repair lines found.</td></tr>'}</tbody>
                        </table>
                        <div style="display:flex; justify-content:flex-end; margin-top:14px;">
                            <div style="min-width:320px; font-size:13px;">
                                <div style="display:flex; justify-content:space-between; padding:3px 0;"><span>Insurance Total</span><span>${popupMoney(insuranceTotal)}</span></div>
                                <div style="display:flex; justify-content:space-between; padding:3px 0;"><span>Customer Total</span><span>${popupMoney(customerTotal)}</span></div>
                                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid #ccc; margin-top:4px; font-weight:700;"><span>Grand Total</span><span>${popupMoney(grandTotal)}</span></div>
                            </div>
                        </div>
                    `
                );
            } catch (error) {
                alert('Unable to generate Bill print.');
            }
        }

        async function roPrintServiceOrder() {
            roClosePrintOptionsModal();
            try {
                const data = await popupFetchJson(`/api/ro-tech-lines?ro=${encodeURIComponent(roKey)}`);
                const techTargets = (Array.isArray(data.tech_lines) ? data.tech_lines : [])
                    .filter((item) => String(item.mode || '').toLowerCase() === 'tech' && String(item.tech_name || item.tech || '').trim());

                if (!techTargets.length) {
                    alert('No tech lines available for Service Order.');
                    return;
                }

                const sectionsByTech = new Map();
                for (const target of techTargets) {
                    const techName = String(target.tech_name || target.tech || '').trim();
                    const repairType = String(target.repair_type || target.type || 'body').trim();
                    const query = new URLSearchParams({ ro: roKey, mode: 'tech', repair_type: repairType, tech_name: techName });
                    const details = await popupFetchJson(`/api/ro-assignment-lines?${query.toString()}`);
                    const lines = Array.isArray(details.lines) ? details.lines : [];
                    if (!sectionsByTech.has(techName)) sectionsByTech.set(techName, []);
                    const targetLines = sectionsByTech.get(techName);
                    lines.forEach((line) => {
                        targetLines.push({
                            line_number: line.line_number || line.line_key || '-',
                            description: line.description || '-',
                            repair_type: line.repair_type || repairType,
                            hours: popupToNumber(line.hours || 0),
                        });
                    });
                }

                const sections = Array.from(sectionsByTech.entries()).map(([techName, techLines]) => {
                    const techTotalHours = techLines.reduce((sum, line) => sum + popupToNumber(line.hours || 0), 0);
                    const rowsHtml = techLines
                        .sort((a, b) => (popupExtractLineNumber(a.line_number) ?? 999999) - (popupExtractLineNumber(b.line_number) ?? 999999))
                        .map((line) => `
                            <tr>
                                <td>${popupEsc(line.line_number || '-')}</td>
                                <td>${popupEsc(line.description || '-')}</td>
                                <td>${popupEsc(line.repair_type || '-')}</td>
                                <td class="num">${popupToNumber(line.hours || 0).toFixed(1)}</td>
                            </tr>
                        `).join('');
                    return `
                        <div style="margin-top:18px;">
                            <div style="font-size:16px; font-weight:700; margin-bottom:6px;">${popupEsc(techName)}</div>
                            <table>
                                <thead><tr><th>Line</th><th>Description</th><th>Type</th><th class="num">HRS</th></tr></thead>
                                <tbody>${rowsHtml || '<tr><td colspan="4" style="text-align:center; color:#777;">No lines assigned.</td></tr>'}</tbody>
                            </table>
                            <div style="display:flex; justify-content:flex-end; margin-top:6px; font-size:13px; font-weight:700;">TOTAL HRS: ${techTotalHours.toFixed(1)}</div>
                        </div>
                    `;
                });

                roOpenPrintWindow(
                    `RO ${roKey} Service Order`,
                    `
                        <div class="header" style="text-align:left;">
                            <div style="font-size:56px; font-weight:800; line-height:1; margin-bottom:8px;">RO #${popupEsc(roKey || '-')}</div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:6px;">
                                <div style="font-size:20px; font-weight:600;">Vehicle: ${popupEsc(ro.vehicle || '-')}</div>
                                <div style="font-size:30px; font-weight:800; letter-spacing:1px;">SERVICE ORDER</div>
                            </div>
                        </div>
                        ${sections.join('')}
                    `
                );
            } catch (error) {
                alert('Unable to generate Service Order print.');
            }
        }

        async function roPrintParts() {
            roClosePrintOptionsModal();
            try {
                const linesRes = await popupFetchJson(`/api/parts/ro-lines?ro=${encodeURIComponent(roKey)}`);
                const lines = Array.isArray(linesRes.lines) ? linesRes.lines : [];
                const totalPrice = lines.reduce((sum, line) => {
                    const qty = popupToNumber(line.qty || 0, 0);
                    const price = popupToNumber(line.price || line.extended_price || 0, 0);
                    return sum + (qty > 0 ? (price * qty) : price);
                }, 0);
                const rowsHtml = lines.map((line) => `
                    <tr>
                        <td>${popupEsc(line.line || '-')}</td>
                        <td>${popupEsc(line.description || '-')}</td>
                        <td class="num">${popupEsc(line.qty || 0)}</td>
                        <td class="num">${popupMoney(line.price || 0)}</td>
                    </tr>
                `).join('');

                roOpenPrintWindow(
                    `RO ${roKey} Parts`,
                    `
                        <div class="header" style="text-align:left;">
                            <div style="font-size:56px; font-weight:800; line-height:1; margin-bottom:8px;">RO #${popupEsc(roKey || '-')}</div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:6px;">
                                <div style="font-size:20px; font-weight:600;">Vehicle: ${popupEsc(ro.vehicle || '-')}</div>
                                <div style="font-size:30px; font-weight:800; letter-spacing:1px;">PARTS</div>
                            </div>
                        </div>
                        <table>
                            <thead><tr><th>Line</th><th>Description</th><th class="num">QTY</th><th class="num">Price</th></tr></thead>
                            <tbody>${rowsHtml || '<tr><td colspan="4" style="text-align:center; color:#777;">No parts lines found.</td></tr>'}</tbody>
                        </table>
                        <div style="display:flex; justify-content:flex-end; margin-top:10px; font-size:14px; font-weight:700;">TOTAL PRICE: ${popupMoney(totalPrice)}</div>
                    `,
                    { immediatePrint: true }
                );
            } catch (error) {
                alert('Unable to generate Parts print.');
            }
        }

        if (printBtn && printPanel) {
            printBtn.addEventListener('click', (event) => {
                event.stopPropagation();
                roTogglePrintPopup(printPanel);
            });
        }

        const printBillBtn = roDoc.getElementById('roPrintOptionBill');
        const printServiceOrderBtn = roDoc.getElementById('roPrintOptionServiceOrder');
        const printPartsBtn = roDoc.getElementById('roPrintOptionParts');
        if (printBillBtn) printBillBtn.addEventListener('click', () => { roPrintBill(); });
        if (printServiceOrderBtn) printServiceOrderBtn.addEventListener('click', () => { roPrintServiceOrder(); });
        if (printPartsBtn) printPartsBtn.addEventListener('click', () => { roPrintParts(); });

        roDoc.addEventListener('click', (event) => {
            if (!printPanel || !printPanel.classList.contains('open')) return;
            const target = event.target;
            if ((printBtn && printBtn.contains(target)) || printPanel.contains(target)) return;
            roClosePrintOptionsModal();
        });

        async function popupFetchJson(url, options = {}) {
            const resp = await fetch(url, { credentials: 'include', cache: 'no-store', ...options });
            const data = await resp.json();
            if (!resp.ok || data.error) throw new Error(data.error || 'Request failed');
            return data;
        }

        async function renderNotesView() {
            if (!contentEl) return;
            contentEl.innerHTML = `
                <div class="ro-window-card">
                    <div style="font-weight:700; font-size:18px; margin-bottom:10px; color:#333;">Notes Log</div>
                    <div style="display:flex; gap:10px; margin-bottom:12px; align-items:flex-start;">
                        <textarea id="roPopupNoteInput" rows="3" style="flex:1; padding:10px; border:1px solid #ccc; border-radius:6px; resize:vertical;" placeholder="Add note..."></textarea>
                        <button id="roPopupNoteSave" type="button" style="padding:10px 14px; background:#505050; color:#fff; border:none; border-radius:6px; cursor:pointer;">Save</button>
                    </div>
                    <div id="roPopupNotesList" style="max-height:420px; overflow-y:auto;"></div>
                </div>
            `;

            const listEl = roDoc.getElementById('roPopupNotesList');
            const inputEl = roDoc.getElementById('roPopupNoteInput');
            const saveBtn = roDoc.getElementById('roPopupNoteSave');

            async function loadNotes() {
                listEl.innerHTML = '<div style="color:#777;">Loading...</div>';
                try {
                    const res = await popupFetchJson(`/api/ro-notes?ro=${encodeURIComponent(roKey)}`);
                    const notes = Array.isArray(res.notes) ? res.notes : [];
                    if (!notes.length) {
                        listEl.innerHTML = '<div style="color:#999;">No notes yet.</div>';
                        return;
                    }
                    listEl.innerHTML = notes.map((note) => `
                        <div style="padding:10px 0; border-bottom:1px solid #eee;">
                            <div style="font-size:12px; color:#666; margin-bottom:4px;">${popupEsc(popupFormatDateTime(note.created_at))} • ${popupEsc(note.created_by || 'Unknown')}</div>
                            <div style="white-space:pre-wrap; color:#222;">${popupEsc(note.note || '')}</div>
                        </div>
                    `).join('');
                } catch (error) {
                    listEl.innerHTML = '<div style="color:#c62828;">Error loading notes.</div>';
                }
            }

            saveBtn.addEventListener('click', async () => {
                const text = String(inputEl.value || '').trim();
                if (!text) return;
                saveBtn.disabled = true;
                try {
                    await popupFetchJson('/api/ro-notes', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ro: roKey, note: text }),
                    });
                    inputEl.value = '';
                    await loadNotes();
                } catch (error) {
                    alert('Error saving note.');
                } finally {
                    saveBtn.disabled = false;
                }
            });

            await loadNotes();
        }

        async function renderEstimateView() {
            if (!contentEl) return;
            contentEl.innerHTML = `<div class="ro-window-card"><div style="font-weight:700; font-size:18px; margin-bottom:10px; color:#333;">Estimate</div><div id="roPopupEstimateContent" style="color:#444;"><div style="color:#777;">Loading...</div></div></div>`;
            const content = roDoc.getElementById('roPopupEstimateContent');
            try {
                const res = await popupFetchJson(`/api/ro-estimate?ro=${encodeURIComponent(roKey)}`);
                const estimate = res.estimate || {};
                const lines = Array.isArray(estimate.unified_lines) ? estimate.unified_lines : [];
                const rowsHtml = lines.map((line) => `
                    <tr>
                        <td style="padding:8px; border-bottom:1px solid #eee;">${popupEsc(line.lineNumber || '-')}</td>
                        <td style="padding:8px; border-bottom:1px solid #eee;">${popupEsc(line.description || '-')}</td>
                        <td style="padding:8px; border-bottom:1px solid #eee; text-align:right;">${popupEsc(line.labor ?? 0)}</td>
                        <td style="padding:8px; border-bottom:1px solid #eee; text-align:right;">${popupEsc(line.paint ?? 0)}</td>
                    </tr>
                `).join('');
                content.innerHTML = `<table style="width:100%; border-collapse:collapse;"><thead><tr><th style="text-align:left; padding:8px;">Line</th><th style="text-align:left; padding:8px;">Description</th><th style="text-align:right; padding:8px;">Labor</th><th style="text-align:right; padding:8px;">Paint</th></tr></thead><tbody>${rowsHtml || '<tr><td colspan="4" style="padding:12px; color:#777;">No estimate lines.</td></tr>'}</tbody></table>`;
            } catch (err) {
                content.innerHTML = '<div style="color:#c62828;">Error loading estimate.</div>';
            }
        }

        async function renderTechView() {
            if (!contentEl) return;
            contentEl.innerHTML = `<div class="ro-window-card"><div style="font-weight:700; font-size:18px; margin-bottom:10px; color:#333;">Tech</div><div id="roPopupTechContent" style="color:#444;"><div style="color:#777;">Loading...</div></div></div>`;
            const content = roDoc.getElementById('roPopupTechContent');
            try {
                const res = await popupFetchJson(`/api/ro-tech-lines?ro=${encodeURIComponent(roKey)}`);
                const items = Array.isArray(res.tech_lines) ? res.tech_lines : [];
                content.innerHTML = items.map((item) => `<div style="padding:8px 0; border-bottom:1px solid #eee;"><strong>${popupEsc(item.tech || item.tech_name || 'Unassigned')}</strong> - ${popupEsc(item.repair_type || item.type || '')} (${popupEsc(item.hours || 0)} hrs)</div>`).join('') || '<div style="color:#777;">No tech assignments.</div>';
            } catch (err) {
                content.innerHTML = '<div style="color:#c62828;">Error loading tech data.</div>';
            }
        }

        async function renderPartsView() {
            if (!contentEl) return;
            contentEl.innerHTML = `<div class="ro-window-card"><div style="font-weight:700; font-size:18px; margin-bottom:10px; color:#333;">Parts</div><div id="roPopupPartsContent" style="color:#444;"><div style="color:#777;">Loading...</div></div></div>`;
            const content = roDoc.getElementById('roPopupPartsContent');
            try {
                const res = await popupFetchJson(`/api/parts/ro-lines?ro=${encodeURIComponent(roKey)}`);
                const lines = Array.isArray(res.lines) ? res.lines : [];
                content.innerHTML = lines.map((line) => `<div style="padding:8px 0; border-bottom:1px solid #eee;">Line ${popupEsc(line.line || '-')}: ${popupEsc(line.description || '-')} (${popupEsc(line.qty || 0)} qty)</div>`).join('') || '<div style="color:#777;">No parts lines.</div>';
            } catch (err) {
                content.innerHTML = '<div style="color:#c62828;">Error loading parts data.</div>';
            }
        }

        async function renderPaymentsView() {
            if (!contentEl) return;
            contentEl.innerHTML = `
                <div class="ro-window-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div id="roPopupPaymentsTitle" style="font-weight:700; font-size:18px; color:#333;">Payments - GRAND TOTAL: -</div>
                        <button id="roPopupPaymentsSave" type="button" style="padding:9px 14px; background:#d32f2f; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:700;">SAVE</button>
                    </div>
                    <div id="roPopupPaymentsLog"><div style="color:#777;">Loading...</div></div>
                </div>
            `;

            const logEl = roDoc.getElementById('roPopupPaymentsLog');
            const saveBtn = roDoc.getElementById('roPopupPaymentsSave');
            const titleEl = roDoc.getElementById('roPopupPaymentsTitle');

            function formatShortPaymentDate(value) {
                const source = String(value || '').trim();
                if (!source) return '--/--/--';
                let dt;
                if (/^\d{4}-\d{2}-\d{2}$/.test(source)) {
                    dt = new Date(`${source}T00:00:00`);
                } else {
                    dt = new Date(source);
                }
                if (Number.isNaN(dt.getTime())) return '--/--/--';
                const mm = String(dt.getMonth() + 1).padStart(2, '0');
                const dd = String(dt.getDate()).padStart(2, '0');
                const yy = String(dt.getFullYear()).slice(-2);
                return `${mm}/${dd}/${yy}`;
            }

            function renderPaymentLog(entries) {
                const sorted = [...(Array.isArray(entries) ? entries : [])].sort((a, b) => {
                    const aDate = new Date(a.business_date || a.paid_at || a.date || '').getTime() || 0;
                    const bDate = new Date(b.business_date || b.paid_at || b.date || '').getTime() || 0;
                    return bDate - aDate;
                });
                if (!sorted.length) return '<div style="color:#777;">No payments yet.</div>';
                return sorted.map((entry) => {
                    const dt = popupEsc(formatShortPaymentDate(entry.business_date || entry.paid_at || entry.date));
                    const typeText = String(entry.payment_type || 'CARD').toUpperCase();
                    const checkNo = String(entry.check_number || '').trim();
                    const typ = popupEsc(typeText === 'CHECK' && checkNo ? `CHECK #${checkNo}` : typeText);
                    const who = popupEsc(String(entry.created_by || 'Unknown'));
                    return `<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #f0f0f0;"><div>${dt} - ${typ} - ${who}</div><div style="font-weight:600;">${popupMoney(entry.amount || 0)}</div></div>`;
                }).join('');
            }

            const data = await popupFetchJson(`/api/payments/ro?ro=${encodeURIComponent(roKey)}`);
            const row = data?.row || null;
            if (!row) {
                logEl.innerHTML = '<div style="color:#777;">No payments found for this RO.</div>';
                return;
            }

            const insuranceEntries = Array.isArray(row.insurance_payment_entries) ? row.insurance_payment_entries : [];
            const customerEntries = Array.isArray(row.customer_payment_entries) ? row.customer_payment_entries : [];
            const insuranceTotal = Number(row.insurance_total || 0);
            const customerTotal = Number(row.customer_total || 0);
            const roGrandTotal = insuranceTotal + customerTotal;
            titleEl.textContent = `Payments - GRAND TOTAL: ${popupMoney(roGrandTotal)}`;

            logEl.innerHTML = `
                <div style="border:1px solid #e2e2e2; border-radius:6px; padding:12px; margin-bottom:14px; background:#fff;">
                    <div style="font-weight:700; margin-bottom:8px;">INSURANCE: ${popupEsc(row.insurance_name || ro.insurance || '-')}</div>
                    <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px;">
                        <input id="roPopupInsurancePaymentInput" type="number" step="0.01" min="0" placeholder="0.00" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:180px;" />
                        <select id="roPopupInsurancePaymentType" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:120px;">
                            <option value="CARD">CARD</option><option value="CASH">CASH</option><option value="CHECK">CHECK</option>
                        </select>
                        <input id="roPopupInsuranceCheckNumber" type="text" placeholder="Check #" style="display:none; padding:8px; border:1px solid #ccc; border-radius:4px; width:150px;" />
                    </div>
                    <div id="roPopupInsuranceLog">${renderPaymentLog(insuranceEntries)}</div>
                </div>
                <div style="border:1px solid #e2e2e2; border-radius:6px; padding:12px; background:#fff;">
                    <div style="font-weight:700; margin-bottom:8px;">CUSTOMER: ${popupEsc(row.customer || ro.customer || '-')}</div>
                    <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px;">
                        <input id="roPopupCustomerPaymentInput" type="number" step="0.01" min="0" placeholder="0.00" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:180px;" />
                        <select id="roPopupCustomerPaymentType" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:120px;">
                            <option value="CARD">CARD</option><option value="CASH">CASH</option><option value="CHECK">CHECK</option>
                        </select>
                        <input id="roPopupCustomerCheckNumber" type="text" placeholder="Check #" style="display:none; padding:8px; border:1px solid #ccc; border-radius:4px; width:150px;" />
                    </div>
                    <div id="roPopupCustomerLog">${renderPaymentLog(customerEntries)}</div>
                </div>
            `;

            function syncCheck(selectId, inputId) {
                const s = roDoc.getElementById(selectId);
                const i = roDoc.getElementById(inputId);
                if (!s || !i) return;
                const isCheck = String(s.value || '').toUpperCase() === 'CHECK';
                i.style.display = isCheck ? 'inline-block' : 'none';
                if (!isCheck) i.value = '';
            }
            ['roPopupInsurancePaymentType', 'roPopupCustomerPaymentType'].forEach((id, idx) => {
                const inputId = idx === 0 ? 'roPopupInsuranceCheckNumber' : 'roPopupCustomerCheckNumber';
                const sel = roDoc.getElementById(id);
                if (sel) sel.addEventListener('change', () => syncCheck(id, inputId));
                syncCheck(id, inputId);
            });

            saveBtn.onclick = async () => {
                const insuranceInput = roDoc.getElementById('roPopupInsurancePaymentInput');
                const customerInput = roDoc.getElementById('roPopupCustomerPaymentInput');
                const insuranceType = roDoc.getElementById('roPopupInsurancePaymentType');
                const customerType = roDoc.getElementById('roPopupCustomerPaymentType');
                const insuranceCheck = roDoc.getElementById('roPopupInsuranceCheckNumber');
                const customerCheck = roDoc.getElementById('roPopupCustomerCheckNumber');

                const insuranceAmount = parseFloat((insuranceInput?.value || '').trim());
                const customerAmount = parseFloat((customerInput?.value || '').trim());
                const hasInsurance = Number.isFinite(insuranceAmount) && insuranceAmount > 0;
                const hasCustomer = Number.isFinite(customerAmount) && customerAmount > 0;
                if (!hasInsurance && !hasCustomer) {
                    alert('Enter an insurance or customer payment amount.');
                    return;
                }

                saveBtn.disabled = true;
                try {
                    await popupFetchJson('/api/payments/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ro: roKey,
                            insurance_payment: hasInsurance ? insuranceAmount : undefined,
                            customer_payment: hasCustomer ? customerAmount : undefined,
                            insurance_payment_type: String(insuranceType?.value || 'CARD').toUpperCase(),
                            customer_payment_type: String(customerType?.value || 'CARD').toUpperCase(),
                            insurance_check_number: hasInsurance ? String(insuranceCheck?.value || '').trim() : '',
                            customer_check_number: hasCustomer ? String(customerCheck?.value || '').trim() : '',
                            business_date: new Date().toISOString().slice(0, 10),
                        }),
                    });
                    await renderPaymentsView();
                } catch (err) {
                    alert('Error saving payment.');
                } finally {
                    saveBtn.disabled = false;
                }
            };
        }

        async function showView(view) {
            roDoc.querySelectorAll('.ro-sidebar-btn').forEach((b) => {
                b.classList.toggle('active', b.getAttribute('data-view') === view);
            });
            if (view === 'notes') return renderNotesView();
            if (view === 'estimate') return renderEstimateView();
            if (view === 'tech') return renderTechView();
            if (view === 'parts') return renderPartsView();
            if (view === 'payments') return renderPaymentsView();
        }

        roDoc.querySelectorAll('.ro-sidebar-btn').forEach((btn) => {
            btn.addEventListener('click', () => showView(btn.getAttribute('data-view') || 'notes'));
        });

        showView('notes');
    }

    function reportsBuildRoRowsHtml(rows, options = {}) {
        const boldGpDollar = !!options.boldGpDollar;
        const normalizedRows = Array.isArray(rows) ? rows : [];
        return normalizedRows.map((ro, index) => {
            const partsSales = Number(ro.parts_sales || 0);
            const partsCost = Number(ro.parts_cost || 0);
            const laborSales = Number(ro.labor_sales || 0);
            const laborCost = Number(ro.labor_cost || 0);
            const totalSales = Number((ro.total_sales ?? ro.total) || 0);
            const totalCost = Number(ro.total_cost || 0);

            const partsGp = computeGpValues(partsSales, partsCost);
            const laborGp = computeGpValues(laborSales, laborCost);
            const totalGp = computeGpValues(totalSales, totalCost);

            const rowBg = index % 2 === 0 ? '#f2f0ef' : '#ffffff';
            const gpBg = index % 2 === 0 ? '#ececec' : '#f7f7f7';

            const partsGpDollarHtml = boldGpDollar
                ? `<strong>${formatReportsMoney(partsGp.gpDollar)}</strong>`
                : `${formatReportsMoney(partsGp.gpDollar)}`;
            const laborGpDollarHtml = boldGpDollar
                ? `<strong>${formatReportsMoney(laborGp.gpDollar)}</strong>`
                : `${formatReportsMoney(laborGp.gpDollar)}`;
            const totalGpDollarHtml = boldGpDollar
                ? `<strong>${formatReportsMoney(totalGp.gpDollar)}</strong>`
                : `${formatReportsMoney(totalGp.gpDollar)}`;

            return `
                <tr style="background:${rowBg};">
                    <td style='padding:12px;'>
                        <button type="button" data-ro="${reportsEscapeHtml(ro.ro_number || '')}" onclick="reportsOpenClosedRoWindow(event, this.dataset.ro)" style="background:none; border:none; padding:0; color:#1b4f9c; font-weight:700; text-decoration:underline; cursor:pointer;">${reportsEscapeHtml(ro.ro_number || '')}</button>
                    </td>
                    <td style='padding:12px;'>${reportsEscapeHtml(ro.vehicle || '')}</td>
                    <td style='padding:12px;'>${reportsEscapeHtml(ro.insurance || '')}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsHours(ro.hours)}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsMoney(partsSales)}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsMoney(partsCost)}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsMoney(laborSales)}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsMoney(laborCost)}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsMoney(totalSales)}</td>
                    <td style='padding:12px; text-align:right;'>${formatReportsMoney(totalCost)}</td>
                </tr>
                <tr style="background:${gpBg};">
                    <td colspan='4' style='padding:8px 12px;'></td>
                    <td colspan='2' style='padding:8px 12px; text-align:right; font-size:12px;'>Parts GP: ${formatReportsPercent(partsGp.gpPercent)}% | ${partsGpDollarHtml}</td>
                    <td colspan='2' style='padding:8px 12px; text-align:right; font-size:12px;'>Labor GP: ${formatReportsPercent(laborGp.gpPercent)}% | ${laborGpDollarHtml}</td>
                    <td colspan='2' style='padding:8px 12px; text-align:right; font-size:12px;'>Total GP: ${formatReportsPercent(totalGp.gpPercent)}% | ${totalGpDollarHtml}</td>
                </tr>
            `;
        }).join('');
    }

    function reportsEscapeHtml(value) {
        return String(value === null || value === undefined ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function reportsToggleMiniPopup(panel) {
        if (!panel) return;
        const isOpen = panel.classList.contains('open');
        document.querySelectorAll('#reports .mini-popup-panel.open').forEach((openPanel) => {
            openPanel.classList.remove('open');
            openPanel.style.display = 'none';
        });
        if (!isOpen) {
            panel.style.display = 'block';
            panel.classList.add('open');
        }
    }

    function reportsClosePrintOptionsModal() {
        const panel = document.getElementById('reportsPrintOptionsModal');
        if (!panel) return;
        panel.classList.remove('open');
        panel.style.display = 'none';
    }

    function reportsOpenPrintOptionsModal() {
        reportsToggleMiniPopup(document.getElementById('reportsPrintOptionsModal'));
    }

    function reportsClosedRoTableHtml(rows) {
        const normalizedRows = Array.isArray(rows) ? rows : [];
        const rowsHtml = reportsBuildRoRowsHtml(normalizedRows, { boldGpDollar: true });

        return `
            <table style="width:100%; border-collapse:collapse; margin-top:12px;">
                <thead>
                    <tr class="dashboard-header-row">
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff;">RO#</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff;">Vehicle</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff;">Insurance</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">HRS</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">PARTS-S</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">PARTS-C</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">LABOR-S</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">LABOR-C</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">TOTAL-S</th>
                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; background:#23272a; color:#fff; text-align:right;">TOTAL-C</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml || `<tr><td colspan="10" style="padding:20px; text-align:center; color:#999;">No closed repair orders found.</td></tr>`}
                </tbody>
            </table>
        `;
    }

    function reportsSummaryTableHtml(summaryRows) {
        const rows = Array.isArray(summaryRows) ? summaryRows : [];
        const rowColors = ['#d3d3d3', '#f2f0ef'];
        const bodyHtml = rows.map((row, index) => {
            const bg = rowColors[index % 2];
            const gpDollarText = formatReportsMoney(row.gp_dollar);
            return `<tr style="background:${bg};">
                <td style='padding:12px;'>${reportsEscapeHtml(row.category)}</td>
                <td style='padding:12px;'>${formatReportsMoney(row.sales)}</td>
                <td style='padding:12px;'>${formatReportsPercent(row.gp_percent)}%</td>
                <td style='padding:12px;'><strong>${gpDollarText}</strong></td>
            </tr>`;
        }).join('');

        return `
            <table style="width:100%; border-collapse:collapse; margin-bottom:16px;">
                <thead>
                    <tr style="background:#3c4142;">
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">CATEGORY</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">TOTAL SALES</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">TOTAL GP %</th>
                        <th style="padding:12px; font-size:18px; font-weight:bold; text-align:left; color:#fff;">TOTAL GP $</th>
                    </tr>
                </thead>
                <tbody>${bodyHtml}</tbody>
            </table>
        `;
    }

    function reportsComputeMetrics(rows) {
        const normalizedRows = Array.isArray(rows) ? rows : [];
        let partsSales = 0;
        let partsCost = 0;
        let laborSales = 0;
        let laborCost = 0;
        let totalSales = 0;
        let totalCost = 0;

        normalizedRows.forEach((ro) => {
            partsSales += Number(ro.parts_sales || 0);
            partsCost += Number(ro.parts_cost || 0);
            laborSales += Number(ro.labor_sales || 0);
            laborCost += Number(ro.labor_cost || 0);
            totalSales += Number((ro.total_sales ?? ro.total) || 0);
            totalCost += Number(ro.total_cost || 0);
        });

        return {
            roCount: normalizedRows.length,
            totalSales,
            total: computeGpValues(totalSales, totalCost),
            parts: computeGpValues(partsSales, partsCost),
            labor: computeGpValues(laborSales, laborCost),
        };
    }

    function reportsOpenPrintWindow(title, bodyHtml) {
        const win = window.open('', '_blank');
        if (!win) {
            alert('Unable to open print preview. Please allow pop-ups for this site.');
            return;
        }
        win.document.write(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>${reportsEscapeHtml(title)}</title>
                    <style>
                        @media print {
                            @page { margin: 0.5in; }
                            body { margin: 0; }
                        }
                        body { font-family: Arial, sans-serif; color:#222; padding:20px; }
                        .header { text-align:center; margin-bottom:16px; border-bottom:2px solid #b22222; padding-bottom:8px; }
                        .header h1 { margin:0 0 6px 0; color:#b22222; font-size:24px; }
                        .header p { margin:0; color:#666; }
                        .group-title { font-size:18px; font-weight:bold; color:#333; margin-bottom:4px; }
                        .group-header-line { font-size:12px; line-height:1.4; color:#444; margin-bottom:8px; border-bottom:1px solid #ddd; padding-bottom:6px; }
                        table { width:100%; border-collapse:collapse; margin-top:10px; }
                        thead th { background:#3c4142; color:#fff; text-align:left; padding:8px; font-size:12px; }
                        tbody td { padding:8px; border-bottom:1px solid #eee; font-size:12px; }
                        .num { text-align:right; }
                    </style>
                </head>
                <body>${bodyHtml}</body>
            </html>
        `);
        win.document.close();
        win.focus();
        setTimeout(() => win.print(), 250);
    }

    function reportsPrintClosedRos(sortBy) {
        reportsClosePrintOptionsModal();

        const rows = reportsGetFilteredRows();
        if (!rows.length) {
            alert('No repair orders to print.');
            return;
        }

        const sortMap = {
            ro: 'ro_number',
            insurance: 'insurance',
            tech: 'tech',
            estimator: 'estimator',
        };
        const sortKey = sortMap[sortBy] || 'ro_number';
        const printLabelMap = {
            ro: 'RO',
            insurance: 'INSURANCE',
            tech: 'TECH',
            estimator: 'ESTIMATOR',
        };
        const printLabel = printLabelMap[sortBy] || 'RO';

        const sortedRows = [...rows].sort((a, b) => {
            const av = String(a?.[sortKey] || '').toLowerCase();
            const bv = String(b?.[sortKey] || '').toLowerCase();
            return av.localeCompare(bv, undefined, { numeric: true, sensitivity: 'base' });
        });

        const groups = new Map();
        sortedRows.forEach((row) => {
            const raw = String(row?.[sortKey] || '').trim();
            const key = raw || 'Unassigned';
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key).push(row);
        });

        const sectionTitle = reportsUiState.status === 'open' ? 'Open Repair Orders' : 'Closed Repair Orders';
        const summaryHtml = reportsSummaryTableHtml(reportsDataCache.summary || []);

        const sectionsHtml = Array.from(groups.entries()).map(([groupName, groupRows]) => {
            const metrics = reportsComputeMetrics(groupRows);
            const rowsHtml = reportsBuildRoRowsHtml(groupRows, { boldGpDollar: true });
            return `
                <div style="margin-top:16px;">
                    <div class="group-title">${reportsEscapeHtml(groupName)}</div>
                    <div class="group-header-line">
                        ROs: ${groupRows.length} |
                        Sales: ${formatReportsMoney(metrics.totalSales)} |
                        GP%: ${formatReportsPercent(metrics.total.gpPercent)}% |
                        GP$: ${formatReportsMoney(metrics.total.gpDollar)}
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>RO#</th><th>Vehicle</th><th>Insurance</th>
                                <th class="num">HRS</th><th class="num">PARTS-S</th><th class="num">PARTS-C</th>
                                <th class="num">LABOR-S</th><th class="num">LABOR-C</th>
                                <th class="num">TOTAL-S</th><th class="num">TOTAL-C</th>
                            </tr>
                        </thead>
                        <tbody>${rowsHtml}</tbody>
                    </table>
                </div>
            `;
        }).join('');

        reportsOpenPrintWindow(
            `${sectionTitle} - ${printLabel}`,
            `<div class="header"><h1>${sectionTitle}</h1><p>Print by: ${printLabel}</p></div>${summaryHtml}${sectionsHtml}`
        );
    }

    async function loadReportsData() {
        try {
            const [reportsResp, dashboardResp] = await Promise.all([
                fetch('/api/reports_data'),
                fetch('/api/dashboard-data', { credentials: 'include' }),
            ]);

            const data = await reportsResp.json();
            const dashboardData = await dashboardResp.json();
            reportsDataCache = {
                summary: Array.isArray(data.summary) ? data.summary : [],
                closed_ros: Array.isArray(data.closed_ros) ? data.closed_ros : [],
                open_ros: reportsBuildOpenRowsFromDashboardRows(dashboardData?.roList || []),
            };

            const summaryBody = document.getElementById('reportsSummaryBody');
            if (summaryBody) {
                summaryBody.innerHTML = '';
                const rowColors = ['#d3d3d3', '#f2f0ef'];
                for (let i = 0; i < reportsDataCache.summary.length; i += 1) {
                    const row = reportsDataCache.summary[i];
                    const rowBg = rowColors[i % 2];
                    summaryBody.innerHTML += `<tr style='background:${rowBg};'>
                        <td style='padding:12px;'>${reportsEscapeHtml(row.category)}</td>
                        <td style='padding:12px;'>${formatReportsMoney(row.sales)}</td>
                        <td style='padding:12px;'>${formatReportsPercent(row.gp_percent)}%</td>
                        <td style='padding:12px;'>${formatReportsMoney(row.gp_dollar)}</td>
                    </tr>`;
                }
            }

            reportsRenderRoList();
        } catch (e) {
            const summaryBody = document.getElementById('reportsSummaryBody');
            const roBody = document.getElementById('reportsRoListBody');
            if (summaryBody) {
                summaryBody.innerHTML = `<tr><td colspan='4' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            }
            if (roBody) {
                roBody.innerHTML = `<tr><td colspan='10' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            }
        }
    }
    // Load data when REPORTS screen is shown
    document.addEventListener('DOMContentLoaded', function() {
        const reportsTab = document.querySelector('.nav-tab[onclick*="reports"]');
        if (reportsTab) {
            reportsTab.addEventListener('click', loadReportsData);
        }

        const toggleEl = document.getElementById('reportsStatusToggle');
        const startDateEl = document.getElementById('reportsStartDate');
        const endDateEl = document.getElementById('reportsEndDate');

        if (toggleEl) {
            toggleEl.checked = false;
            toggleEl.addEventListener('change', reportsApplyFiltersFromControls);
        }
        if (startDateEl) {
            startDateEl.addEventListener('change', reportsApplyFiltersFromControls);
        }
        if (endDateEl) {
            endDateEl.addEventListener('change', reportsApplyFiltersFromControls);
        }
        reportsApplyFiltersFromControls();

        window.addEventListener('click', function(event) {
            const panel = document.getElementById('reportsPrintOptionsModal');
            if (!panel || !panel.classList.contains('open')) return;
            if (event.target.closest('#reportsPrintTrigger') || event.target.closest('#reportsPrintOptionsModal')) return;
            reportsClosePrintOptionsModal();
        });
    });
    </script>
    <style></style>
    '''
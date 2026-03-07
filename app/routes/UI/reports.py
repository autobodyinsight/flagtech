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
            <h3 style="margin:0 0 18px 0; color:#333;">Closed Repair Orders</h3>
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
    </style>
    <script>
    let reportsDataCache = { summary: [], closed_ros: [] };

    function formatReportsPercent(value) {
        const amount = Number(value || 0);
        return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function formatReportsMoney(value) {
        const amount = Number(value || 0);
        return '$' + amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function reportsSchedulePrintDialog(win) {
        if (!win) return;
        let didPrint = false;

        const runPrint = () => {
            if (didPrint) return;
            didPrint = true;
            try {
                win.focus();
                win.print();
            } catch (err) {
                console.error('Unable to open print dialog:', err);
            }
        };

        const scheduleAfterRender = () => {
            if (didPrint) return;
            if (typeof win.requestAnimationFrame === 'function') {
                win.requestAnimationFrame(() => win.requestAnimationFrame(runPrint));
            } else {
                setTimeout(runPrint, 0);
            }
        };

        if (win.document?.readyState === 'complete') {
            scheduleAfterRender();
        } else {
            win.addEventListener('load', scheduleAfterRender, { once: true });
        }
        setTimeout(scheduleAfterRender, 120);
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

    function reportsBuildRoRowsHtml(rows, options = {}) {
        const boldGpDollar = !!options.boldGpDollar;
        const normalizedRows = Array.isArray(rows) ? rows : [];
        return normalizedRows.map((ro, index) => {
            const partsSales = Number(ro.parts_sales || 0);
        reportsSchedulePrintDialog(win);
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
                    <td style='padding:12px;'>${reportsEscapeHtml(ro.ro_number || '')}</td>
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
                        body { font-family: Arial, sans-serif; padding: 20px; color: #333; }
                        .header { text-align:center; margin-bottom:20px; border-bottom:2px solid #b22222; padding-bottom:10px; }
                        .header h1 { margin:0 0 6px 0; color:#b22222; font-size:26px; }
                        .header p { margin:0; color:#666; }
                        .group-wrap { margin-top:24px; margin-bottom:8px; }
                        .group-title { font-size:18px; font-weight:bold; color:#333; margin-bottom:4px; }
                        .group-header-line { font-size:12px; line-height:1.4; color:#444; margin-bottom:8px; border-bottom:1px solid #ddd; padding-bottom:6px; }
                        table { width:100%; border-collapse:collapse; }
                        thead th { font-size:12px; }
                        tbody td { font-size:12px; }
                    </style>
                </head>
                <body>
                    ${bodyHtml}
                </body>
            </html>
        `);
        win.document.close();
        reportsSchedulePrintDialog(win);
    }

    function reportsPrintClosedRos(printBy) {
        reportsClosePrintOptionsModal();
        const rows = Array.isArray(reportsDataCache.closed_ros) ? reportsDataCache.closed_ros : [];
        if (!rows.length) {
            alert('No closed repair orders to print.');
            return;
        }

        const summaryRows = Array.isArray(reportsDataCache.summary) ? reportsDataCache.summary : [];
        const labelMap = { ro: 'RO', insurance: 'INSURANCE', tech: 'TECH', estimator: 'ESTIMATOR' };
        const printLabel = labelMap[printBy] || 'RO';
        const summaryHtml = reportsSummaryTableHtml(summaryRows);

        if (printBy === 'ro') {
            const roCountHtml = `<div style="margin:6px 0 14px 0; font-weight:bold;">RO Count: ${rows.length}</div>`;
            const tableHtml = reportsClosedRoTableHtml(rows);
            reportsOpenPrintWindow(
                `Closed Repair Orders - ${printLabel}`,
                `<div class="header"><h1>Closed Repair Orders</h1><p>Print by: ${printLabel}</p></div>${summaryHtml}${roCountHtml}${tableHtml}`
            );
            return;
        }

        const key = printBy;
        const grouped = new Map();
        rows.forEach((row) => {
            const groupName = reportsResolveGroupName(row, key) || 'Unspecified';
            if (!grouped.has(groupName)) grouped.set(groupName, []);
            grouped.get(groupName).push(row);
        });

        const sectionsHtml = Array.from(grouped.entries())
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([groupName, groupRows]) => {
                const metrics = reportsComputeMetrics(groupRows);
                const groupHeaderHtml = `
                    <div class="group-wrap">
                        <div class="group-title">${reportsEscapeHtml(groupName)}</div>
                        <div class="group-header-line">RO Count: ${metrics.roCount} &nbsp;&nbsp;&nbsp;&nbsp; Grand Total Sales: ${formatReportsMoney(metrics.totalSales)} &nbsp;&nbsp;&nbsp;&nbsp; Total GP: ${formatReportsPercent(metrics.total.gpPercent)}% | ${formatReportsMoney(metrics.total.gpDollar)} &nbsp;&nbsp;&nbsp;&nbsp; Parts GP: ${formatReportsPercent(metrics.parts.gpPercent)}% | ${formatReportsMoney(metrics.parts.gpDollar)} &nbsp;&nbsp;&nbsp;&nbsp; Labor GP: ${formatReportsPercent(metrics.labor.gpPercent)}% | ${formatReportsMoney(metrics.labor.gpDollar)}</div>
                    </div>
                `;
                return `${groupHeaderHtml}${reportsClosedRoTableHtml(groupRows)}`;
            })
            .join('');

        reportsOpenPrintWindow(
            `Closed Repair Orders - ${printLabel}`,
            `<div class="header"><h1>Closed Repair Orders</h1><p>Print by: ${printLabel}</p></div>${summaryHtml}${sectionsHtml}`
        );
    }

    async function loadReportsData() {
        try {
            const resp = await fetch('/api/reports_data');
            const data = await resp.json();
            reportsDataCache = {
                summary: Array.isArray(data.summary) ? data.summary : [],
                closed_ros: Array.isArray(data.closed_ros) ? data.closed_ros : [],
            };
            // Render summary
            const summaryBody = document.getElementById('reportsSummaryBody');
            summaryBody.innerHTML = '';
            const rowColors = ['#d3d3d3', '#f2f0ef'];
            for (let i = 0; i < reportsDataCache.summary.length; i += 1) {
                const row = reportsDataCache.summary[i];
                const rowBg = rowColors[i % 2];
                summaryBody.innerHTML += `<tr style='background:${rowBg};'>
                    <td style='padding:12px;'>${row.category}</td>
                    <td style='padding:12px;'>${formatReportsMoney(row.sales)}</td>
                    <td style='padding:12px;'>${formatReportsPercent(row.gp_percent)}%</td>
                    <td style='padding:12px;'>${formatReportsMoney(row.gp_dollar)}</td>
                </tr>`;
            }
            // Render closed RO list
            const roBody = document.getElementById('reportsRoListBody');
            roBody.innerHTML = '';
            if (reportsDataCache.closed_ros.length === 0) {
                roBody.innerHTML = `<tr><td colspan='10' style='padding:20px; text-align:center; color:#999;'>No closed repair orders found.</td></tr>`;
            } else {
                roBody.innerHTML = reportsBuildRoRowsHtml(reportsDataCache.closed_ros);
            }
        } catch (e) {
            document.getElementById('reportsSummaryBody').innerHTML = `<tr><td colspan='4' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            document.getElementById('reportsRoListBody').innerHTML = `<tr><td colspan='10' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
        }
    }
    // Load data when REPORTS screen is shown
    document.addEventListener('DOMContentLoaded', function() {
        const reportsTab = document.querySelector('.nav-tab[onclick*="reports"]');
        if (reportsTab) {
            reportsTab.addEventListener('click', loadReportsData);
        }
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
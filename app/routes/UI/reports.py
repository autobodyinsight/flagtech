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

    function computeGpValues(sales, cost) {
        const safeSales = Number(sales || 0);
        const safeCost = Number(cost || 0);
        const gpDollar = safeSales - safeCost;
        const gpPercent = safeSales > 0 ? (gpDollar / safeSales) * 100 : 0;
        return { gpDollar, gpPercent };
    }

    function renderGpEnclosure(salesLabel, costLabel, sales, cost) {
        const gp = computeGpValues(sales, cost);
        const salesText = formatReportsMoney(sales);
        const costText = formatReportsMoney(cost);
        const gpDollarText = Number(gp.gpDollar || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        return `<div class='reports-gp-enclosure'>
            <div class='reports-gp-enclosure-top'>
                <span>${salesLabel} : ${salesText}</span>
                <span>|</span>
                <span>${costLabel} : ${costText}</span>
            </div>
            <div class='reports-gp-enclosure-bottom'>
                <span>GP ${formatReportsPercent(gp.gpPercent)}%</span>
                <span>-</span>
                <span>GP $${gpDollarText}</span>
            </div>
        </div>`;
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
        const rowsHtml = normalizedRows.map((ro) => {
            const partsSales = Number(ro.parts_sales || 0);
            const partsCost = Number(ro.parts_cost || 0);
            const laborSales = Number(ro.labor_sales || 0);
            const laborCost = Number(ro.labor_cost || 0);
            const totalSales = Number((ro.total_sales ?? ro.total) || 0);
            const totalCost = Number(ro.total_cost || 0);
            const hoursValue = Number(ro.hours || 0);
            const hoursText = Number.isFinite(hoursValue) ? hoursValue.toFixed(1) : reportsEscapeHtml(ro.hours || '');

            return `<tr>
                <td style='padding:12px;'>${reportsEscapeHtml(ro.ro_number || '')}</td>
                <td style='padding:12px;'>${reportsEscapeHtml(ro.vehicle || '')}</td>
                <td style='padding:12px;'>${reportsEscapeHtml(ro.insurance || '')}</td>
                <td style='padding:12px; text-align:right;'>${hoursText}</td>
                <td colspan='2' style='padding:8px 12px;'>${renderGpEnclosure('PARTS-S', 'PARTS-C', partsSales, partsCost)}</td>
                <td colspan='2' style='padding:8px 12px;'>${renderGpEnclosure('LABOR-S', 'LABOR-C', laborSales, laborCost)}</td>
                <td colspan='2' style='padding:8px 12px;'>${renderGpEnclosure('TOTAL-S', 'TOTAL-C', totalSales, totalCost)}</td>
            </tr>`;
        }).join('');

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
            return `<tr style="background:${bg};">
                <td style='padding:12px;'>${reportsEscapeHtml(row.category)}</td>
                <td style='padding:12px;'>${formatReportsMoney(row.sales)}</td>
                <td style='padding:12px;'>${formatReportsPercent(row.gp_percent)}%</td>
                <td style='padding:12px;'>${formatReportsMoney(row.gp_dollar)}</td>
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
                        .group-header { display:flex; justify-content:space-between; align-items:flex-start; gap:20px; margin-top:26px; margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid #ddd; }
                        .group-title { font-size:20px; font-weight:bold; color:#333; }
                        .group-metrics { text-align:right; font-size:13px; line-height:1.5; color:#444; }
                        table { width:100%; border-collapse:collapse; }
                        .reports-gp-enclosure { border: 1px solid #9e9e9e; background: #fff; width: fit-content; min-width: 260px; margin: 0 auto; font-size: 12px; color: inherit; }
                        .reports-gp-enclosure-top { display:flex; justify-content:center; align-items:center; gap:8px; padding:4px 8px; border-bottom:1px solid #9e9e9e; }
                        .reports-gp-enclosure-bottom { display:flex; justify-content:center; align-items:center; gap:14px; padding:4px 8px; }
                    </style>
                </head>
                <body>
                    ${bodyHtml}
                </body>
            </html>
        `);
        win.document.close();
        win.focus();
        setTimeout(() => win.print(), 250);
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
            const groupName = String(row?.[key] || '').trim() || 'Unspecified';
            if (!grouped.has(groupName)) grouped.set(groupName, []);
            grouped.get(groupName).push(row);
        });

        const sectionsHtml = Array.from(grouped.entries())
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([groupName, groupRows]) => {
                const metrics = reportsComputeMetrics(groupRows);
                const groupHeaderHtml = `
                    <div class="group-header">
                        <div class="group-title">${reportsEscapeHtml(groupName)}</div>
                        <div class="group-metrics">
                            <div><strong>Grand Total Sales:</strong> ${formatReportsMoney(metrics.totalSales)}</div>
                            <div><strong>RO Count:</strong> ${metrics.roCount}</div>
                            <div><strong>Total GP:</strong> ${formatReportsPercent(metrics.total.gpPercent)}% | ${formatReportsMoney(metrics.total.gpDollar)}</div>
                            <div><strong>Parts GP:</strong> ${formatReportsPercent(metrics.parts.gpPercent)}% | ${formatReportsMoney(metrics.parts.gpDollar)}</div>
                            <div><strong>Labor GP:</strong> ${formatReportsPercent(metrics.labor.gpPercent)}% | ${formatReportsMoney(metrics.labor.gpDollar)}</div>
                        </div>
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
                for (const ro of reportsDataCache.closed_ros) {
                    const partsSales = Number(ro.parts_sales || 0);
                    const partsCost = Number(ro.parts_cost || 0);
                    const laborSales = Number(ro.labor_sales || 0);
                    const laborCost = Number(ro.labor_cost || 0);
                    const totalSales = Number((ro.total_sales ?? ro.total) || 0);
                    const totalCost = Number(ro.total_cost || 0);

                    roBody.innerHTML += `<tr>
                        <td style='padding:12px;'>${ro.ro_number || ''}</td>
                        <td style='padding:12px;'>${ro.vehicle || ''}</td>
                        <td style='padding:12px;'>${ro.insurance || ''}</td>
                        <td style='padding:12px; text-align:right;'>${ro.hours || ''}</td>
                        <td colspan='2' style='padding:8px 12px;'>${renderGpEnclosure('PARTS-S', 'PARTS-C', partsSales, partsCost)}</td>
                        <td colspan='2' style='padding:8px 12px;'>${renderGpEnclosure('LABOR-S', 'LABOR-C', laborSales, laborCost)}</td>
                        <td colspan='2' style='padding:8px 12px;'>${renderGpEnclosure('TOTAL-S', 'TOTAL-C', totalSales, totalCost)}</td>
                    </tr>`;
                }
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
    <style>
        .reports-gp-enclosure {
            border: 1px solid #9e9e9e;
            background: #fff;
            width: fit-content;
            min-width: 320px;
            margin: 0 auto;
            font-size: inherit;
            font-weight: normal;
            color: inherit;
        }
        .reports-gp-enclosure-top {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            padding: 6px 10px;
            border-bottom: 1px solid #9e9e9e;
            font-size: inherit;
            font-weight: normal;
        }
        .reports-gp-enclosure-bottom {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 18px;
            padding: 6px 10px;
            font-size: inherit;
            font-weight: normal;
        }
    </style>
    '''
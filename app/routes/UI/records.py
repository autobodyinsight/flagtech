"""RECORDS window for closed repair orders."""


def get_records_screen_html():
    """Return the HTML content for the RECORDS window."""
    return r'''
    <div id="records" class="screen" style="padding:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
            <h1 style="text-align:center; margin:0; flex:1;">RECORDS</h1>
        </div>
        <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 18px 0; color:#333;">Closed Repair Orders</h3>
            <div style="overflow-x:auto;">
                <table id="recordsRoListTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr class="dashboard-header-row">
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">RO#</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">VEHICLE</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">CUSTOMER</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">INSURANCE</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">IN</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">OUT</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">CLOSED</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">TOTAL</th>
                        </tr>
                    </thead>
                    <tbody id="recordsRoListBody">
                        <tr><td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>
                    </tbody>
                </table>
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
            .records-gp-box {
                display: inline-block;
                padding: 6px 10px;
                border: 1px solid #b7b7b7;
                border-radius: 6px;
                background: #ffffff;
                font-size: 12px;
                font-weight: 700;
                color: #222;
                white-space: nowrap;
            }
        </style>
        <script>
        function formatRecordsDate(value) {
            const source = String(value || '').trim();
            if (!source) return '';
            let dt;
            if (/^\d{4}-\d{2}-\d{2}$/.test(source)) {
                dt = new Date(`${source}T00:00:00`);
            } else {
                dt = new Date(source);
            }
            if (Number.isNaN(dt.getTime())) return source;
            const mm = String(dt.getMonth() + 1).padStart(2, '0');
            const dd = String(dt.getDate()).padStart(2, '0');
            const yy = String(dt.getFullYear()).slice(-2);
            return `${mm}/${dd}/${yy}`;
        }

        function formatRecordsMoney(value) {
            const amount = Number(value || 0);
            return '$' + amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function formatRecordsPercent(value) {
            const amount = Number(value || 0);
            return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function computeGp(sales, cost) {
            const safeSales = Number(sales || 0);
            const safeCost = Number(cost || 0);
            const gpDollar = safeSales - safeCost;
            const gpPercent = safeSales > 0 ? (gpDollar / safeSales) * 100 : 0;
            return { gpDollar, gpPercent };
        }

        function renderGpBox(label, sales, cost) {
            const gp = computeGp(sales, cost);
            const gpDollarAbs = Math.abs(Number(gp.gpDollar || 0)).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            const gpDollarText = gp.gpDollar < 0 ? `-${gpDollarAbs}` : gpDollarAbs;
            return `<div class='records-gp-box' title='${label}'>[GP ${formatRecordsPercent(gp.gpPercent)}% – GP$${gpDollarText}]</div>`;
        }

        async function loadRecordsData() {
            const body = document.getElementById('recordsRoListBody');
            if (!body) return;
            try {
                const [recordsResp, reportsResp] = await Promise.all([
                    fetch('/api/records/closed-ros', { credentials: 'include' }),
                    fetch('/api/reports_data', { credentials: 'include' })
                ]);
                const data = await recordsResp.json();
                const reportsData = await reportsResp.json();
                const rows = Array.isArray(data.rows) ? data.rows : [];
                const reportsRows = Array.isArray(reportsData.closed_ros) ? reportsData.closed_ros : [];
                const reportsByRo = {};
                reportsRows.forEach((reportRow) => {
                    const key = String(reportRow.ro_number || '').trim();
                    if (key) reportsByRo[key] = reportRow;
                });
                body.innerHTML = '';
                if (!rows.length) {
                    body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#999;'>No closed repair orders found.</td></tr>`;
                    return;
                }

                rows.forEach((row, index) => {
                    const rowBg = (index % 2 === 0) ? '#d3d3d3' : '#f2f0ef';
                    const reportRow = reportsByRo[String(row.ro || '').trim()] || {};
                    const partsSales = Number(reportRow.parts_sales || 0);
                    const partsCost = Number(reportRow.parts_cost || 0);
                    const laborSales = Number(reportRow.labor_sales || 0);
                    const laborCost = Number(reportRow.labor_cost || 0);
                    const totalSales = Number((reportRow.total_sales !== undefined ? reportRow.total_sales : row.total) || 0);
                    const totalCost = Number((reportRow.total_cost !== undefined ? reportRow.total_cost : (partsCost + laborCost)) || 0);

                    body.innerHTML += `<tr>
                        <td style='padding:12px; background:${rowBg};'>${row.ro || ''}</td>
                        <td style='padding:12px; background:${rowBg};'>${row.vehicle || ''}</td>
                        <td style='padding:12px; background:${rowBg};'>${row.customer || ''}</td>
                        <td style='padding:12px; background:${rowBg};'>${row.insurance || ''}</td>
                        <td style='padding:12px; background:${rowBg};'>${formatRecordsDate(row.in_date)}</td>
                        <td style='padding:12px; background:${rowBg};'>${formatRecordsDate(row.out_date)}</td>
                        <td style='padding:12px; background:${rowBg};'>${formatRecordsDate(row.closed_date)}</td>
                        <td style='padding:12px; text-align:right; background:${rowBg};'>${formatRecordsMoney(row.total)}</td>
                    </tr>`;

                    body.innerHTML += `<tr>
                        <td colspan='8' style='padding:6px 12px 12px 12px; background:${rowBg}; border-top:0;'>
                            <div style='display:grid; grid-template-columns:repeat(8, minmax(0, 1fr)); gap:8px; align-items:center;'>
                                <div style='grid-column:6;'>${renderGpBox('PARTS GP', partsSales, partsCost)}</div>
                                <div style='grid-column:7;'>${renderGpBox('LABOR GP', laborSales, laborCost)}</div>
                                <div style='grid-column:8; justify-self:end;'>${renderGpBox('TOTAL GP', totalSales, totalCost)}</div>
                            </div>
                        </td>
                    </tr>`;
                });
            } catch (error) {
                body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            }
        }
        </script>
    </div>
    '''

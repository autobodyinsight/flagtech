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

        function formatRecordsDateTime(value) {
            const source = String(value || '').trim();
            if (!source) return '';
            const dt = new Date(source);
            if (Number.isNaN(dt.getTime())) return source;
            const mm = String(dt.getMonth() + 1).padStart(2, '0');
            const dd = String(dt.getDate()).padStart(2, '0');
            const yy = String(dt.getFullYear()).slice(-2);
            let hours = dt.getHours();
            const minutes = String(dt.getMinutes()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12 || 12;
            return `${mm}/${dd}/${yy} ${hours}:${minutes} ${ampm}`;
        }

        function formatRecordsMoney(value) {
            const amount = Number(value || 0);
            return '$' + amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        async function loadRecordsData() {
            const body = document.getElementById('recordsRoListBody');
            if (!body) return;
            try {
                const resp = await fetch('/api/records/closed-ros', { credentials: 'include' });
                const data = await resp.json();
                const rows = Array.isArray(data.rows) ? data.rows : [];
                body.innerHTML = '';
                if (!rows.length) {
                    body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#999;'>No closed repair orders found.</td></tr>`;
                    return;
                }

                rows.forEach((row) => {
                    body.innerHTML += `<tr>
                        <td style='padding:12px;'>${row.ro || ''}</td>
                        <td style='padding:12px;'>${row.vehicle || ''}</td>
                        <td style='padding:12px;'>${row.customer || ''}</td>
                        <td style='padding:12px;'>${row.insurance || ''}</td>
                        <td style='padding:12px;'>${formatRecordsDate(row.in_date)}</td>
                        <td style='padding:12px;'>${formatRecordsDate(row.out_date)}</td>
                        <td style='padding:12px;'>${formatRecordsDateTime(row.closed_date)}</td>
                        <td style='padding:12px; text-align:right;'>${formatRecordsMoney(row.total)}</td>
                    </tr>`;
                });
            } catch (error) {
                body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            }
        }
        </script>
    </div>
    '''

"""RECORDS window for closed repair orders."""


def get_records_screen_html():
    """Return the HTML content for the RECORDS window."""
    return r'''
    <div id="records" class="screen" style="padding:20px; position:relative;">
        <div id="recordsSidebar" style="position:fixed; left:0; top:76px; height:calc(100vh - 76px); width:64px; background:#23272a; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:38px; z-index:100; box-shadow:2px 0 8px rgba(0,0,0,0.08);">
            <div style="display:flex; flex-direction:column; align-items:center; gap:38px; width:100%;">
                <button id="recordsSidebarBtn-ros" class="records-sidebar-btn active" data-view="ros" title="RO's" onclick="recordsSwitchView('ros')" style="background:none; border:none; padding:0; cursor:pointer;">
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="3" width="16" height="22" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="8" x2="19" y2="8" stroke="white" stroke-width="2"/><rect x="9" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="9" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><line x1="9" y1="22" x2="19" y2="22" stroke="white" stroke-width="2"/></svg>
                </button>
                <button id="recordsSidebarBtn-tech" class="records-sidebar-btn" data-view="tech" title="Tech" onclick="recordsSwitchView('tech')" style="background:none; border:none; padding:0; cursor:pointer;">
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="9" r="4" stroke="white" stroke-width="2"/><rect x="7" y="17" width="14" height="6" rx="3" stroke="white" stroke-width="2"/><path d="M21 21l2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/><path d="M7 21l-2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
                </button>
                <button id="recordsSidebarBtn-parts" class="records-sidebar-btn" data-view="parts" title="Parts" onclick="recordsSwitchView('parts')" style="background:none; border:none; padding:0; cursor:pointer;">
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="23" r="2" stroke="white" stroke-width="2"/><circle cx="20" cy="23" r="2" stroke="white" stroke-width="2"/><rect x="5" y="7" width="18" height="10" rx="2" stroke="white" stroke-width="2"/><path d="M7 7V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v2" stroke="white" stroke-width="2"/></svg>
                </button>
                <button id="recordsSidebarBtn-vendors" class="records-sidebar-btn" data-view="vendors" title="Vendors" onclick="recordsSwitchView('vendors')" style="background:none; border:none; padding:0; cursor:pointer;">
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="10" width="18" height="13" rx="1.8" stroke="white" stroke-width="2"/><path d="M4 10h20" stroke="white" stroke-width="2"/><path d="M8 10V6h12v4" stroke="white" stroke-width="2"/><path d="M10 14v9" stroke="white" stroke-width="2"/><path d="M14 14v9" stroke="white" stroke-width="2"/><path d="M18 14v9" stroke="white" stroke-width="2"/></svg>
                </button>
            </div>
        </div>

        <div id="recordsMainPanel" style="margin-left:84px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
            <h1 style="text-align:center; margin:0; flex:1;">RECORDS</h1>
        </div>

        <div id="recordsPanel-ros" class="records-content-panel" style="display:block; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
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

        <div id="recordsPanel-tech" class="records-content-panel" style="display:none; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 18px 0; color:#333;">Tech</h3>
            <div style="overflow-x:auto;">
                <table id="recordsTechListTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr class="dashboard-header-row">
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">TECH</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">PAY RATE</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">TOTAL HRS</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:center;">TOTAL RO'S</th>
                        </tr>
                    </thead>
                    <tbody id="recordsTechListBody">
                        <tr><td colspan="4" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div id="recordsPanel-parts" class="records-content-panel" style="display:none; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 18px 0; color:#333;">Parts</h3>
            <div style="color:#666;">Parts screen</div>
        </div>

        <div id="recordsPanel-vendors" class="records-content-panel" style="display:none; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 18px 0; color:#333;">Vendors</h3>
            <div style="color:#666;">Vendors screen</div>
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
            #recordsSidebar svg { display:block; margin:0 auto; }
            #recordsSidebar .records-sidebar-btn { opacity:0.72; transition:opacity 0.15s ease, transform 0.15s ease; }
            #recordsSidebar .records-sidebar-btn:hover { opacity:1; transform:translateY(-1px); }
            #recordsSidebar .records-sidebar-btn.active { opacity:1; }
            #recordsSidebar { box-shadow:2px 0 8px rgba(0,0,0,0.08); }
            @media (max-width: 700px) {
                #recordsSidebar { width:44px; }
                #recordsSidebar svg { width:22px; height:22px; }
                #recordsMainPanel { margin-left:64px !important; }
            }
        </style>
        <script>
        function recordsSetActiveSidebar(view) {
            document.querySelectorAll('#recordsSidebar .records-sidebar-btn').forEach((button) => {
                const btnView = String(button.getAttribute('data-view') || '').toLowerCase();
                button.classList.toggle('active', btnView === String(view || '').toLowerCase());
            });
        }

        function recordsSwitchView(view) {
            const normalizedView = String(view || 'ros').toLowerCase();
            document.querySelectorAll('#records .records-content-panel').forEach((panel) => {
                panel.style.display = 'none';
            });

            const targetPanel = document.getElementById(`recordsPanel-${normalizedView}`);
            if (targetPanel) {
                targetPanel.style.display = 'block';
            } else {
                const defaultPanel = document.getElementById('recordsPanel-ros');
                if (defaultPanel) defaultPanel.style.display = 'block';
            }

            recordsSetActiveSidebar(normalizedView);
            if (normalizedView === 'ros') {
                loadRecordsData();
            } else if (normalizedView === 'tech') {
                loadRecordsTechPayouts();
            }
        }

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

        function escapeRecordsHtml(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function formatRecordsShortDate(value) {
            const source = String(value || '').trim();
            if (!source) return '-';
            const dt = new Date(source);
            if (Number.isNaN(dt.getTime())) return source;
            const mm = String(dt.getMonth() + 1).padStart(2, '0');
            const dd = String(dt.getDate()).padStart(2, '0');
            const yy = String(dt.getFullYear()).slice(-2);
            return `${mm}/${dd}/${yy}`;
        }

        function recordsDaysSinceIn(value) {
            const source = String(value || '').trim();
            if (!source) return '-';
            const dt = new Date(source);
            if (Number.isNaN(dt.getTime())) return '-';
            const today = new Date();
            const start = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate());
            const now = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            const diffMs = now.getTime() - start.getTime();
            const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            return Number.isFinite(days) ? Math.max(0, days) : '-';
        }

        async function openRecordsTechDetailWindow(techId, techName) {
            const win = window.open('', `Records_Tech_${techId}`, 'width=1220,height=760,scrollbars=yes,resizable=yes');
            if (!win) {
                alert('Popup blocked. Please allow popups for this site.');
                return;
            }

            const safeTechName = escapeRecordsHtml(techName || `Tech #${techId}`);
            win.document.title = `Tech Detail - ${safeTechName}`;
            win.document.body.innerHTML = `
                <div style="padding:20px; background:#d3d3d3; min-height:100vh; font-family:Arial,sans-serif;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;">
                        <h2 style="margin:0; color:#333;">Paid RO's - ${safeTechName}</h2>
                        <button onclick="window.close()" style="padding:8px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Close</button>
                    </div>
                    <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <div style="overflow-x:auto;">
                            <table id="recordsTechDetailTable" style="width:100%; border-collapse:collapse;">
                                <thead>
                                    <tr class="dashboard-header-row">
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">RO#</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Vehicle</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Insurance</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">In</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:center;" title="Days Since In Date">⏳</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">ECD</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">HRS</th>
                                        <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">Total</th>
                                    </tr>
                                </thead>
                                <tbody id="recordsTechDetailBody">
                                    <tr><td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            const style = win.document.createElement('style');
            style.textContent = `
                body { margin:0; }
                .dashboard-header-row th, .dashboard-header-cell {
                    font-family: inherit;
                    font-size: 16px;
                    font-weight: bold;
                    background: #23272a;
                    color: #fff;
                }
                button.ro-link {
                    background:none;
                    border:none;
                    color:#0066cc;
                    text-decoration:underline;
                    cursor:pointer;
                    padding:0;
                    font:inherit;
                }
            `;
            win.document.head.appendChild(style);

            try {
                const resp = await fetch(`/api/records/tech-paid-ros?tech_id=${encodeURIComponent(String(techId))}`, { credentials: 'include' });
                const data = await resp.json();
                const rows = Array.isArray(data.rows) ? data.rows : [];
                const body = win.document.getElementById('recordsTechDetailBody');
                if (!body) return;

                if (!rows.length) {
                    body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#999;'>No paid RO records found for this tech.</td></tr>`;
                    return;
                }

                body.innerHTML = '';
                rows.forEach((row, index) => {
                    const rowBg = index % 2 === 0 ? '#f2f0ef' : '#ffffff';
                    const roValue = String(row.ro || '').trim();
                    const roEscaped = escapeRecordsHtml(roValue);
                    const vehicle = escapeRecordsHtml(row.vehicle || 'N/A');
                    const insurance = escapeRecordsHtml(row.insurance || '-');
                    const inDate = formatRecordsShortDate(row.in_date);
                    const ecdDate = formatRecordsShortDate(row.ecd_date);
                    const daysSinceIn = recordsDaysSinceIn(row.in_date);
                    const hours = Number(row.hours || 0).toFixed(1);
                    const total = formatRecordsMoney(row.total || 0);

                    body.innerHTML += `
                        <tr>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg};'>
                                <button type='button' class='ro-link' data-ro='${roEscaped}'>${roEscaped}</button>
                            </td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; color:#333;'>${vehicle}</td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; color:#333;'>${insurance}</td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; color:#333;'>${inDate}</td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; text-align:center; color:#333;'>${daysSinceIn}</td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; color:#333;'>${ecdDate}</td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; text-align:right; color:#333;'>${hours}</td>
                            <td style='padding:12px; border-bottom:1px solid #eee; background:${rowBg}; text-align:right; color:#333;'>${total}</td>
                        </tr>
                    `;
                });

                Array.from(win.document.querySelectorAll('button.ro-link')).forEach((button) => {
                    button.addEventListener('click', async () => {
                        const roNumber = String(button.getAttribute('data-ro') || '').trim();
                        if (!roNumber) return;

                        const openerWindow = win.opener;
                        if (!openerWindow || openerWindow.closed) {
                            alert('Main window is not available.');
                            return;
                        }

                        if (typeof openerWindow.openRoWindowFromDashboard !== 'function') {
                            alert('RO window function is unavailable.');
                            return;
                        }

                        const hasRoInMemory = Array.isArray(openerWindow.dashboardData?.roList)
                            && openerWindow.dashboardData.roList.some((item) => String(item?.ro || '') === roNumber);

                        if (!hasRoInMemory) {
                            try {
                                const dashResp = await openerWindow.fetch('/api/dashboard-data', { credentials: 'include' });
                                const dashData = await dashResp.json();
                                if (dashData && Array.isArray(dashData.roList)) {
                                    openerWindow.dashboardData = dashData;
                                }
                            } catch (err) {
                                console.error('Unable to refresh dashboard data for RO window open:', err);
                            }
                        }

                        openerWindow.openRoWindowFromDashboard(null, roNumber);
                        openerWindow.focus();
                    });
                });
            } catch (error) {
                const body = win.document.getElementById('recordsTechDetailBody');
                if (body) {
                    body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#c00;'>Error loading paid RO records</td></tr>`;
                }
            }
        }

        async function loadRecordsData() {
            recordsSetActiveSidebar('ros');
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

                rows.forEach((row, index) => {
                    const rowBg = (index % 2 === 0) ? '#d3d3d3' : '#f2f0ef';
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
                });
            } catch (error) {
                body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            }
        }

        async function loadRecordsTechPayouts() {
            const body = document.getElementById('recordsTechListBody');
            if (!body) return;

            body.innerHTML = `<tr><td colspan='4' style='padding:20px; text-align:center; color:#999;'>Loading...</td></tr>`;
            try {
                const resp = await fetch('/api/records/tech-payouts', { credentials: 'include' });
                const data = await resp.json();
                const rows = Array.isArray(data.rows) ? data.rows : [];

                body.innerHTML = '';
                if (!rows.length) {
                    body.innerHTML = `<tr><td colspan='4' style='padding:20px; text-align:center; color:#999;'>No paid tech payouts found.</td></tr>`;
                    return;
                }

                rows.forEach((row, index) => {
                    const rowBg = (index % 2 === 0) ? '#d3d3d3' : '#f2f0ef';
                    const techName = String(row.tech_name || '').trim() || `Tech #${row.tech_id || ''}`;
                    const totalRos = Number(row.total_ros || 0);

                    body.innerHTML += `<tr>
                        <td style='padding:12px; background:${rowBg};'><button type='button' class='tech-link' data-tech-id='${Number(row.tech_id || 0)}' data-tech-name='${escapeRecordsHtml(techName)}' style='background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;'>${escapeRecordsHtml(techName)}</button></td>
                        <td style='padding:12px; text-align:right; background:${rowBg};'>${formatRecordsMoney(row.pay_rate || 0)}</td>
                        <td style='padding:12px; text-align:right; background:${rowBg};'>${Number(row.total_hours || 0).toFixed(1)}</td>
                        <td style='padding:12px; text-align:center; background:${rowBg};'>${totalRos}</td>
                    </tr>`;
                });

                body.querySelectorAll('button.tech-link').forEach((button) => {
                    button.addEventListener('click', () => {
                        const techId = Number(button.getAttribute('data-tech-id') || 0);
                        const techName = String(button.getAttribute('data-tech-name') || '').trim();
                        if (!techId) return;
                        openRecordsTechDetailWindow(techId, techName);
                    });
                });
            } catch (error) {
                body.innerHTML = `<tr><td colspan='4' style='padding:20px; text-align:center; color:#c00;'>Error loading tech payouts</td></tr>`;
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            recordsSwitchView('ros');
        });
        </script>
    </div>
    '''

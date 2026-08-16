"""Estimates screen content for the FlagTech UI."""


def get_estimates_screen_html():
    """Return the HTML content for the Estimates screen."""
    return """
        <div id="estimate" class="screen" style="padding:20px;">
            <style>
                #estimate .dashboard-ro-title-tab {
                    display: inline-flex;
                    align-items: center;
                    background: rgba(0,0,0,0.03);
                    color: #000000;
                    font-weight: 700;
                    padding: 10px 14px;
                    border-radius: 8px 8px 0 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    margin-bottom: -1px;
                }
                #estimate .dashboard-ro-table-wrap {
                    background: #ffffff;
                    border-radius: 4px;
                    overflow: hidden;
                }
                #estimate .dashboard-header-row th,
                #estimate .dashboard-header-cell {
                    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                    font-size: 15px;
                    font-weight: 600;
                    background: rgba(0,0,0,0.03) !important;
                    color: #000000;
                    text-align: left;
                    border: none !important;
                    border-bottom: 1px solid #b22222 !important;
                    padding-top: 14px !important;
                    padding-bottom: 14px !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }
                #estimateListBody tr.estimate-row td {
                    background: #ffffff;
                    border: none;
                    border-bottom: 1px solid rgba(0,0,0,0.06) !important;
                    min-height: 48px;
                    height: 48px;
                    vertical-align: middle;
                    color: #333;
                }
                #estimateListBody tr.estimate-row:hover td {
                    background: rgba(0,0,0,0.04) !important;
                }
                #estimateListBody .estimate-number {
                    font-weight: 700;
                    color: #111;
                }
            </style>

            <div style="display:flex; align-items:center; justify-content:center; margin-bottom:20px;">
                <h1 style="text-align:center; margin:0;">ESTIMATES</h1>
            </div>

            <div style="margin-top:8px;">
                <div style="display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:0; position:relative;">
                    <h3 class="dashboard-ro-title-tab" style="margin:0; color:#333;">Estimate List</h3>
                </div>
                <div class="dashboard-ro-table-wrap" style="overflow-x:auto;">
                    <table id="estimateListTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="dashboard-header-row">
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Estimate #</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Vehicle</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Customer</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Insurance</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">In</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">Total</th>
                            </tr>
                        </thead>
                        <tbody id="estimateListBody">
                            <tr>
                                <td colspan="6" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            async function loadEstimateList() {
                const body = document.getElementById('estimateListBody');
                if (!body) return;
                body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>';

                try {
                    const response = await fetch('/api/estimate-list', { credentials: 'include' });
                    const data = await response.json();
                    if (!response.ok || data.error) throw new Error(data.error || 'Unable to load estimates');

                    const rows = Array.isArray(data.estimateList) ? data.estimateList : [];
                    if (!rows.length) {
                        body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#666;">No estimates found.</td></tr>';
                        return;
                    }

                    body.innerHTML = rows.map((row) => {
                        const estimateNumber = row.estimate_number ?? '';
                        const vehicle = row.vehicle || '-';
                        const customer = row.customer || '-';
                        const insurance = row.insurance || '-';
                        const inDate = row.in_date || '-';
                        const total = Number(row.total || 0);

                        return `
                            <tr class="estimate-row">
                                <td class="estimate-number">${{estimateNumber}}</td>
                                <td>${{vehicle}}</td>
                                <td>${{customer}}</td>
                                <td>${{insurance}}</td>
                                <td>${{inDate}}</td>
                                <td style="text-align:right; font-weight:600; color:#111;">${{formatCurrency(total)}}</td>
                            </tr>
                        `;
                    }).join('');
                } catch (error) {
                    console.error('Error loading estimate list:', error);
                    body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#b22222;">Unable to load estimates.</td></tr>';
                }
            }

            function formatCurrency(value) {
                const numeric = Number(value || 0);
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                }).format(numeric);
            }
        </script>
    """

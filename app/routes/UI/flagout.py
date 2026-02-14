"""Flagout screen content for the FlagTech UI."""


def get_flagtech_screen_html():
    """Return the HTML content for the Flagout screen."""
    return """
    <div id="flagtech" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">FLAGOUT</h1>
        <div style="text-align:center; margin-bottom:16px;">
            <button id="flagoutInitializeBtn" onclick="toggleFlagoutInitialize()" style="padding:10px 20px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
                INITIALIZE
            </button>
        </div>

        <div style="margin-top:20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px;">
                <h2 style="margin:0;">Tech List</h2>
                <button id="flagoutPayoutBtn" onclick="openFlagoutPayoutConfirm()" style="display:none; padding:10px 20px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
                    payout
                </button>
            </div>
            <div id="flagoutTechTable" style="width:100%; border:1px solid #ddd; border-radius:4px; overflow:hidden; background:#fff;">
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:2px solid #ddd; font-weight:bold;">
                    <div style="flex:1.8; text-align:left;">Tech Name</div>
                    <div style="flex:1; text-align:center;">Role</div>
                    <div style="flex:1; text-align:center;">Pay Rate</div>
                    <div style="flex:1; text-align:right;">Total HRS</div>
                </div>
                <div id="flagoutTechRows">
                    <div style="padding:14px; color:#777; text-align:center;">Loading...</div>
                </div>
            </div>
        </div>

        <div id="flagoutPayoutModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; background:#f2f2f2;">
                <span class="close" onclick="closeFlagoutPayoutModal()">&times;</span>
                <h3 style="margin-bottom:14px;">Payout Summary</h3>
                <div id="flagoutPayoutSummaryBody"></div>
                <div style="text-align:right; margin-top:14px;">
                    <button onclick="printFlagoutPayoutSummary()" style="padding:10px 20px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
                        Print
                    </button>
                </div>
            </div>
        </div>

        <div id="flagoutPayoutConfirmModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:460px; background:#f2f2f2;">
                <h3 style="margin:0 0 16px 0; text-align:center;">YOU’RE ABOUT TO PAYOUT, CONFIRM</h3>
                <div style="display:flex; justify-content:center; gap:10px;">
                    <button onclick="closeFlagoutPayoutConfirm()" style="padding:10px 20px; background:#777; color:#fff; border:none; border-radius:4px; cursor:pointer;">Cancel</button>
                    <button onclick="confirmFlagoutPayout()" style="padding:10px 20px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Confirm</button>
                </div>
            </div>
        </div>

        <style>
            .flagout-tech-row {
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:12px;
                border-bottom:1px solid #eee;
            }
            .flagout-tech-row:hover {
                background:#fafafa;
            }
            .flagout-tech-toggle {
                background:none;
                border:none;
                color:#0066cc;
                text-decoration:underline;
                cursor:pointer;
                font:inherit;
                padding:0;
                font-weight:bold;
            }
            .flagout-ros-wrap {
                display:none;
                padding:12px 16px;
                border-bottom:1px solid #eee;
                background:#fafafa;
            }
            .flagout-ros-panel {
                border:1px solid #ddd;
                border-radius:6px;
                background:#fff;
                overflow:hidden;
            }
            .flagout-ros-table {
                width:100%;
                border-collapse:collapse;
            }
            .flagout-ros-table thead tr {
                background:#d9d9d9;
                border-bottom:2px solid #999;
            }
            .flagout-ros-table th,
            .flagout-ros-table td {
                padding:8px 12px;
                border-bottom:1px solid #eee;
                text-align:left;
            }
            .flagout-ros-table th:nth-child(2),
            .flagout-ros-table td:nth-child(2) {
                text-align:left;
            }
            .flagout-ros-table th:nth-child(3),
            .flagout-ros-table td:nth-child(3),
            .flagout-ros-table th:nth-child(4),
            .flagout-ros-table td:nth-child(4),
            .flagout-ros-table th:nth-child(5),
            .flagout-ros-table td:nth-child(5) {
                text-align:right;
            }
        </style>

        <script>
            let flagoutInitializeMode = false;
            let currentFlagoutTechs = [];
            let selectedFlagoutRosByTech = {};
            let lastFlagoutPayoutSummaries = [];
            let openFlagoutTechIds = new Set();

            function formatCurrency(amount) {
                const value = Number(amount || 0);
                return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }

            function toggleFlagoutInitialize() {
                flagoutInitializeMode = !flagoutInitializeMode;
                selectedFlagoutRosByTech = {};

                const initBtn = document.getElementById('flagoutInitializeBtn');
                const payoutBtn = document.getElementById('flagoutPayoutBtn');
                if (initBtn) {
                    initBtn.textContent = flagoutInitializeMode ? 'DONE' : 'INITIALIZE';
                }
                if (payoutBtn) {
                    payoutBtn.style.display = flagoutInitializeMode ? 'inline-flex' : 'none';
                    payoutBtn.disabled = true;
                }

                renderFlagoutTechRows(currentFlagoutTechs || []);
            }

            function getSelectedRosForTech(techId) {
                const key = String(techId);
                if (!selectedFlagoutRosByTech[key]) {
                    selectedFlagoutRosByTech[key] = new Set();
                }
                return selectedFlagoutRosByTech[key];
            }

            function updatePayoutButtonState() {
                const payoutBtn = document.getElementById('flagoutPayoutBtn');
                if (!payoutBtn) return;
                const hasSelections = Object.values(selectedFlagoutRosByTech).some(setVal => setVal && setVal.size > 0);
                payoutBtn.disabled = !hasSelections;
            }

            function toggleTechSelection(techId, checked) {
                const selectedSet = getSelectedRosForTech(techId);
                selectedSet.clear();
                if (checked) {
                    const tech = (currentFlagoutTechs || []).find(item => Number(item.tech_id || 0) === Number(techId));
                    (tech?.ros || []).forEach(roItem => {
                        const ro = String(roItem.ro || '').trim();
                        if (ro) selectedSet.add(ro);
                    });
                }
                updatePayoutButtonState();
                renderFlagoutTechRows(currentFlagoutTechs || []);
            }

            function toggleRoSelection(techId, ro, checked) {
                const selectedSet = getSelectedRosForTech(techId);
                if (checked) {
                    selectedSet.add(String(ro));
                } else {
                    selectedSet.delete(String(ro));
                }
                updatePayoutButtonState();
                renderFlagoutTechRows(currentFlagoutTechs || []);
            }

            function closeFlagoutPayoutModal() {
                const modal = document.getElementById('flagoutPayoutModal');
                if (modal) {
                    modal.style.display = 'none';
                }
            }

            function openFlagoutPayoutConfirm() {
                const modal = document.getElementById('flagoutPayoutConfirmModal');
                if (!modal) return;
                modal.style.display = 'block';
            }

            function closeFlagoutPayoutConfirm() {
                const modal = document.getElementById('flagoutPayoutConfirmModal');
                if (!modal) return;
                modal.style.display = 'none';
            }

            function confirmFlagoutPayout() {
                closeFlagoutPayoutConfirm();
                submitFlagoutPayout();
            }

            function showFlagoutPayoutSummary(summaries) {
                lastFlagoutPayoutSummaries = Array.isArray(summaries) ? summaries : [];
                const modal = document.getElementById('flagoutPayoutModal');
                const body = document.getElementById('flagoutPayoutSummaryBody');
                if (!modal || !body) return;

                if (!lastFlagoutPayoutSummaries.length) {
                    body.innerHTML = '<div style="color:#777;">No payouts were processed.</div>';
                } else {
                    body.innerHTML = lastFlagoutPayoutSummaries.map(item => `
                        <div style="border:1px solid #ddd; border-radius:6px; background:#fff; padding:12px; margin-bottom:10px;">
                            <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">${item.tech_name || '-'}</div>
                            <div style="display:flex; gap:20px; flex-wrap:wrap; color:#444; font-size:14px;">
                                <div><strong>Total ROs Paid:</strong> ${Number(item.total_ros_paid || 0)}</div>
                                <div><strong>Pay Rate:</strong> ${formatCurrency(item.pay_rate || 0)}/hr</div>
                                <div><strong>Total Paid:</strong> ${formatCurrency(item.total_paid || 0)}</div>
                            </div>
                        </div>
                    `).join('');
                }

                modal.style.display = 'block';
            }

            function printFlagoutPayoutSummary() {
                const summaries = lastFlagoutPayoutSummaries || [];
                if (!summaries.length) {
                    alert('No payout summary to print.');
                    return;
                }

                const printWindow = window.open('', '_blank', 'width=1100,height=800');
                if (!printWindow) return;

                const pages = summaries.map((summary) => {
                    const rows = (summary.ros || []).map((ro) => `
                        <tr>
                            <td>${ro.ro || '-'}</td>
                            <td>${ro.vehicle_info || '-'}</td>
                            <td style="text-align:right;">${Number(ro.total_hours || 0).toFixed(1)}</td>
                            <td style="text-align:right;">${formatCurrency(ro.pay_rate || 0)}/hr</td>
                            <td style="text-align:right; font-weight:bold;">${formatCurrency(ro.total || 0)}</td>
                        </tr>
                    `).join('');

                    return `
                        <section class="page">
                            <h2>${summary.tech_name || '-'}</h2>
                            <table>
                                <thead>
                                    <tr>
                                        <th>RO #</th>
                                        <th>Vehicle Info</th>
                                        <th style="text-align:right;">Total Hours</th>
                                        <th style="text-align:right;">Pay Rate</th>
                                        <th style="text-align:right;">Total</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                            <div class="sum">SUM: ${formatCurrency(summary.total_paid || 0)}</div>
                            <div class="pending">PENDING TAXES</div>
                        </section>
                    `;
                }).join('');

                printWindow.document.write(`
                    <html>
                    <head>
                        <title>Flagout Payout Summary</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 0; padding: 0; color: #222; }
                            .page { padding: 28px; page-break-after: always; }
                            .page:last-child { page-break-after: auto; }
                            h2 { margin: 0 0 14px 0; color: #d32f2f; }
                            table { width: 100%; border-collapse: collapse; margin-top: 8px; }
                            th, td { border-bottom: 1px solid #e5e5e5; padding: 10px; font-size: 14px; }
                            thead th { background: #f4f4f4; text-align: left; }
                            .sum { margin-top: 14px; text-align: right; font-size: 18px; font-weight: bold; }
                            .pending { margin-top: 8px; text-align: right; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
                        </style>
                    </head>
                    <body>
                        ${pages}
                    </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                printWindow.print();
            }

            function submitFlagoutPayout() {
                const selections = Object.entries(selectedFlagoutRosByTech)
                    .map(([techId, roSet]) => ({
                        tech_id: Number(techId),
                        ros: Array.from(roSet || [])
                    }))
                    .filter(item => Number.isFinite(item.tech_id) && item.ros.length > 0);

                if (!selections.length) {
                    alert('Select at least one RO to payout.');
                    return;
                }

                fetch('/api/flagout/payout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ selections })
                })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        showFlagoutPayoutSummary(res.summaries || []);
                        selectedFlagoutRosByTech = {};
                        loadFlagoutTechs();
                    })
                    .catch(err => {
                        console.error('Error saving payout:', err);
                        alert('Error saving payout.');
                    });
            }

            function renderFlagoutTechRows(techs) {
                const container = document.getElementById('flagoutTechRows');
                if (!container) return;

                currentFlagoutTechs = Array.isArray(techs) ? techs : [];

                const visibleTechIds = new Set((currentFlagoutTechs || []).map(item => String(Number(item.tech_id || 0))));
                openFlagoutTechIds = new Set(Array.from(openFlagoutTechIds).filter(id => visibleTechIds.has(String(id))));

                if (!techs || techs.length === 0) {
                    container.innerHTML = "<div style='padding:14px; color:#777; text-align:center;'>No flagged-out RO lines yet.</div>";
                    return;
                }

                const html = techs.map((tech) => {
                    const techId = Number(tech.tech_id || 0);
                    const name = tech.tech_name || `Tech #${techId}`;
                    const role = (tech.role || '').trim() || '-';
                    const payRate = Number(tech.pay_rate || 0);
                    const totalHours = Number(tech.total_hours || 0);
                    const selectedSet = getSelectedRosForTech(techId);
                    const roCount = (tech.ros || []).length;
                    const selectedCount = selectedSet.size;
                    const techChecked = roCount > 0 && selectedCount === roCount;
                    const techPartial = selectedCount > 0 && selectedCount < roCount;
                    const isOpen = openFlagoutTechIds.has(String(techId));
                    const roRows = (tech.ros || []).map((roItem) => {
                        const ro = roItem.ro || '—';
                        const vehicleInfo = roItem.vehicle_info || '—';
                        const roPayRate = Number(roItem.pay_rate || payRate || 0);
                        const roHours = Number(roItem.total_hours || 0);
                        const roPay = roPayRate * roHours;
                        const roChecked = selectedSet.has(String(ro));
                        const roCheckbox = flagoutInitializeMode
                            ? `<td style="text-align:center;"><input type="checkbox" ${roChecked ? 'checked' : ''} onclick="event.stopPropagation();" onchange="toggleRoSelection(${techId}, '${String(ro).replace(/'/g, "\\'")}', this.checked)" /></td>`
                            : '';
                        return `
                            <tr>
                                ${roCheckbox}
                                <td><strong>RO# ${ro}</strong></td>
                                <td>${vehicleInfo}</td>
                                <td>${formatCurrency(roPayRate)}/hr</td>
                                <td>${roHours.toFixed(1)}</td>
                                <td>${formatCurrency(roPay)}</td>
                            </tr>
                        `;
                    }).join('');

                    const roTable = roRows
                        ? `
                            <div class="flagout-ros-panel">
                                <table class="flagout-ros-table">
                                    <thead>
                                        <tr>
                                            ${flagoutInitializeMode ? '<th style="text-align:center; width:40px;">✓</th>' : ''}
                                            <th>RO#</th>
                                            <th>Vehicle Info</th>
                                            <th>Pay Rate</th>
                                            <th>Total HRS</th>
                                            <th>Total Pay</th>
                                        </tr>
                                    </thead>
                                    <tbody>${roRows}</tbody>
                                </table>
                            </div>
                        `
                        : "<div style='padding:10px; color:#777;'>No ROs found.</div>";

                    return `
                        <div class="flagout-tech-row">
                            <div style="flex:1.8;">
                                ${flagoutInitializeMode ? `<input type="checkbox" ${techChecked ? 'checked' : ''} ${techPartial ? 'data-partial="1"' : ''} onclick="event.stopPropagation();" onchange="toggleTechSelection(${techId}, this.checked)" style="margin-right:8px;" />` : ''}
                                <button type="button" class="flagout-tech-toggle" onclick="toggleFlagoutTechRos(${techId})">${name}</button>
                            </div>
                            <div style="flex:1; text-align:center;">${role}</div>
                            <div style="flex:1; text-align:center;">${formatCurrency(payRate)}/hr</div>
                            <div style="flex:1; text-align:right; font-weight:bold;">${totalHours.toFixed(1)}</div>
                        </div>
                        <div id="flagout-ros-${techId}" class="flagout-ros-wrap" style="display:${isOpen ? 'block' : 'none'};">${roTable}</div>
                    `;
                }).join('');

                container.innerHTML = html;
                if (flagoutInitializeMode) {
                    container.querySelectorAll('input[data-partial="1"]').forEach((input) => {
                        input.indeterminate = true;
                    });
                }
                updatePayoutButtonState();
            }

            function toggleFlagoutTechRos(techId) {
                const row = document.getElementById(`flagout-ros-${techId}`);
                if (!row) return;
                const key = String(techId);
                const willOpen = row.style.display !== 'block';
                row.style.display = willOpen ? 'block' : 'none';
                if (willOpen) {
                    openFlagoutTechIds.add(key);
                } else {
                    openFlagoutTechIds.delete(key);
                }
            }

            function loadFlagoutTechs() {
                const container = document.getElementById('flagoutTechRows');
                if (container) {
                    container.innerHTML = "<div style='padding:14px; color:#777; text-align:center;'>Loading...</div>";
                }

                fetch('/api/flagout/techs', { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        renderFlagoutTechRows(res.techs || []);
                    })
                    .catch(err => {
                        console.error('Error loading flagout techs:', err);
                        if (container) {
                            container.innerHTML = "<div style='padding:14px; color:red; text-align:center;'>Error loading flagout list.</div>";
                        }
                    });
            }

            document.addEventListener('DOMContentLoaded', loadFlagoutTechs);
        </script>
    </div>
    """

"""Flagout screen content for the FlagTech UI."""


def get_flagtech_screen_html():
    """Return the HTML content for the Flagout screen."""
    return """
    <div id="flagtech" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">FLAGOUT</h1>

        <div style="margin-top:20px;">
            <h2 style="margin-bottom:16px;">Tech List</h2>
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
            function formatCurrency(amount) {
                const value = Number(amount || 0);
                return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }

            function renderFlagoutTechRows(techs) {
                const container = document.getElementById('flagoutTechRows');
                if (!container) return;

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
                    const roRows = (tech.ros || []).map((roItem) => {
                        const ro = roItem.ro || '—';
                        const vehicleInfo = roItem.vehicle_info || '—';
                        const roPayRate = Number(roItem.pay_rate || payRate || 0);
                        const roHours = Number(roItem.total_hours || 0);
                        const roPay = roPayRate * roHours;
                        return `
                            <tr>
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
                                <button type="button" class="flagout-tech-toggle" onclick="toggleFlagoutTechRos(${techId})">${name}</button>
                            </div>
                            <div style="flex:1; text-align:center;">${role}</div>
                            <div style="flex:1; text-align:center;">${formatCurrency(payRate)}/hr</div>
                            <div style="flex:1; text-align:right; font-weight:bold;">${totalHours.toFixed(1)}</div>
                        </div>
                        <div id="flagout-ros-${techId}" class="flagout-ros-wrap">${roTable}</div>
                    `;
                }).join('');

                container.innerHTML = html;
            }

            function toggleFlagoutTechRos(techId) {
                const row = document.getElementById(`flagout-ros-${techId}`);
                if (!row) return;
                row.style.display = row.style.display === 'block' ? 'none' : 'block';
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

"""Dashboard screen content for the FlagTech UI."""


def get_dashboard_screen_html():
    """Return the HTML content for the Dashboard screen."""
    return """
        <div id="dashboard" class="screen active" style="padding:20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
                <h1 style="text-align:center; margin:0; flex:1;">DASHBOARD</h1>
                <button onclick="flashAllData()" style="padding:10px 16px; background:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">FLASH</button>
            </div>
            
            <div style="display:flex; gap:20px;">
                <!-- Left Side: Vertical Bars -->
                <div style="flex:0 0 300px; display:flex; flex-direction:column; gap:20px;">
                    <!-- Total Sales Bar -->
                    <div style="background:#f9f9f9; padding:20px; border-radius:8px; border:1px solid #ddd; flex:1; display:flex; flex-direction:column; height:calc((100% - 20px) / 2);">
                        <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Total Sales</h3>
                        <div style="position:relative; flex:1; background:#e0e0e0; border-radius:4px; overflow:hidden;">
                            <div id="totalSalesBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #4caf50, #81c784); transition:height 0.5s ease;">
                            </div>
                        </div>
                        <div id="totalSalesValue" style="text-align:center; font-size:20px; font-weight:bold; color:#4caf50; margin-top:10px;">
                            $0
                        </div>
                    </div>
                    
                    <!-- Pending Payments Bar -->
                    <div style="background:#f9f9f9; padding:20px; border-radius:8px; border:1px solid #ddd; flex:1; display:flex; flex-direction:column; height:calc((100% - 20px) / 2);">
                        <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Pending Payments</h3>
                        <div style="position:relative; flex:1; background:#e0e0e0; border-radius:4px; overflow:hidden;">
                            <div id="pendingPaymentsBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #ff9800, #ffb74d); transition:height 0.5s ease;">
                            </div>
                        </div>
                        <div id="pendingPaymentsValue" style="text-align:center; font-size:20px; font-weight:bold; color:#ff9800; margin-top:10px;">
                            $0
                        </div>
                    </div>
                </div>
                
                <!-- Right Side: 6 Display Cards in 2 Columns -->
                <div style="flex:1; display:grid; grid-template-columns:1fr 1fr; gap:20px; align-content:start;">
                    <!-- Current GP Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #2196f3; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Current GP</h4>
                        <div id="currentGP" style="font-size:32px; font-weight:bold; color:#2196f3;">
                            0%
                        </div>
                    </div>
                    
                    <!-- Parts Cost Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #e91e63; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Parts Cost</h4>
                        <div id="partsCost" style="font-size:32px; font-weight:bold; color:#e91e63;">
                            $0
                        </div>
                    </div>
                    
                    <!-- Average Hours Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #9c27b0; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Average Hrs</h4>
                        <div id="averageHrs" style="font-size:32px; font-weight:bold; color:#9c27b0;">
                            0.0
                        </div>
                    </div>
                    
                    <!-- Average RO Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #ff5722; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Average RO</h4>
                        <div id="averageRO" style="font-size:32px; font-weight:bold; color:#ff5722;">
                            $0
                        </div>
                    </div>
                    
                    <!-- Total Hrs per Tech - Pie Chart -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #00bcd4; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Total Hrs per Tech</h4>
                        <canvas id="hoursPerTechChart" style="max-height:150px;"></canvas>
                    </div>
                    
                    <!-- Total ROs per Tech - List View -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #795548; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Total ROs per Tech</h4>
                        <div id="rosPerTechList" style="max-height:150px; overflow-y:auto; font-size:14px;">
                            <div style="color:#999; text-align:center;">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- RO List Table -->
            <div style="margin-top:30px; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin:0 0 20px 0; color:#333;">Repair Orders</h3>
                <div style="overflow-x:auto;">
                    <table id="roListTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f5f5f5; text-align:left;">
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">RO#</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Vehicle</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Customer</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Phone</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Tech</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Painter</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right;">HRS</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right;">Total</th>
                            </tr>
                        </thead>
                        <tbody id="roListBody">
                            <tr>
                                <td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="repairLinesModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; max-height:80vh; overflow-y:auto;">
                <span class="close" onclick="closeRepairLinesModal()">&times;</span>
                <h2 id="repairLinesTitle" style="margin-bottom:16px;">Repair Lines</h2>
                <div style="margin-bottom:12px;">
                    <label for="repairLinesTech" style="font-weight:bold; font-size:12px; color:#666;">TECH</label>
                    <select id="repairLinesTech" style="width:100%; padding:8px; margin-top:6px;"></select>
                </div>
                <div id="repairLinesBody"></div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                    <div id="repairLinesTotal" style="font-weight:bold;">Total Assigned: 0.0 hrs</div>
                    <button id="repairLinesSave" onclick="saveRepairAssignment()" style="padding:8px 16px; background:#4CAF50; color:#fff; border:none; border-radius:4px; cursor:pointer;">Save</button>
                </div>
            </div>
        </div>

        <style>
            .modal {
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.4);
            }
            .modal-content {
                background-color: #f2f2f2;
                margin: 3% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 95%;
                border-radius: 6px;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: #000;
            }
        </style>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Global variables for dashboard
            let dashboardData = null;
            let hoursPerTechChartInstance = null;
            
            // Check if BACKEND_BASE is already defined, if not, define it
            if (typeof BACKEND_BASE === 'undefined') {
                var BACKEND_BASE = "https://flagtech1.onrender.com";
            }
            
            // Load dashboard data
            async function loadDashboardData() {
                try {
                    const response = await fetch(BACKEND_BASE + '/api/dashboard-data', { credentials: 'include' });
                    const data = await response.json();
                    if (data && !data.error) {
                        dashboardData = data;
                        updateDashboard(data);
                        return;
                    }
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }

                const fallback = {
                    totalSales: 0,
                    pendingPayments: 0,
                    currentGP: 0,
                    partsCost: 0,
                    averageHrs: 0,
                    averageRO: 0,
                    hoursPerTech: [],
                    rosPerTech: [],
                    roList: []
                };
                dashboardData = fallback;
                updateDashboard(fallback);
            }

            async function flashAllData() {
                const confirmed = confirm('This will delete all uploaded estimate data. Continue?');
                if (!confirmed) return;

                try {
                    const response = await fetch(BACKEND_BASE + '/api/flash', { method: 'POST' });
                    const result = await response.json();
                    if (result.status === 'success') {
                        await loadDashboardData();
                        alert('All uploaded estimate data cleared.');
                    } else {
                        alert('Flash failed: ' + (result.message || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Flash failed: ' + error.message);
                }
            }
            
            // Update all dashboard elements
            function updateDashboard(data) {
                // Update Total Sales bar and value
                const maxSales = Math.max(data.totalSales, data.pendingPayments, 10000); // minimum scale
                const salesPercent = (data.totalSales / maxSales) * 100;
                document.getElementById('totalSalesBar').style.height = salesPercent + '%';
                document.getElementById('totalSalesValue').innerText = '$' + data.totalSales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Pending Payments bar and value
                const pendingPercent = (data.pendingPayments / maxSales) * 100;
                document.getElementById('pendingPaymentsBar').style.height = pendingPercent + '%';
                document.getElementById('pendingPaymentsValue').innerText = '$' + data.pendingPayments.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Current GP
                document.getElementById('currentGP').innerText = data.currentGP.toFixed(1) + '%';
                
                // Update Parts Cost
                document.getElementById('partsCost').innerText = '$' + data.partsCost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Average Hours
                document.getElementById('averageHrs').innerText = data.averageHrs.toFixed(1);
                
                // Update Average RO
                document.getElementById('averageRO').innerText = '$' + data.averageRO.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Total Hrs per Tech - Pie Chart
                updateHoursPerTechChart(data.hoursPerTech);
                
                // Update Total ROs per Tech - List
                updateRosPerTechList(data.rosPerTech);
                
                // Update RO List Table
                updateRoListTable(data.roList);
            }
            
            // Update pie chart for hours per tech
            function updateHoursPerTechChart(hoursPerTech) {
                const ctx = document.getElementById('hoursPerTechChart');
                
                if (!ctx) return;
                
                const labels = hoursPerTech.map(item => item.tech);
                const dataValues = hoursPerTech.map(item => item.hours);
                
                // Generate colors for each tech
                const colors = [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ];
                
                // Destroy existing chart if it exists
                if (hoursPerTechChartInstance) {
                    hoursPerTechChartInstance.destroy();
                }
                
                hoursPerTechChartInstance = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: dataValues,
                            backgroundColor: colors.slice(0, labels.length),
                            borderWidth: 2,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    font: {
                                        size: 10
                                    },
                                    padding: 8
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.label + ': ' + context.parsed.toFixed(1) + ' hrs';
                                    }
                                }
                            }
                        }
                    }
                });
            }
            
            // Update list for ROs per tech
            function updateRosPerTechList(rosPerTech) {
                const container = document.getElementById('rosPerTechList');
                
                if (rosPerTech.length === 0) {
                    container.innerHTML = '<div style="color:#999; text-align:center;">No data</div>';
                    return;
                }
                
                let html = '';
                rosPerTech.forEach(item => {
                    html += `
                        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #eee;">
                            <span style="color:#333;">${item.tech}</span>
                            <span style="font-weight:bold; color:#795548;">${item.ros}</span>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            function safeId(value) {
                return String(value || '')
                    .replace(/[^a-zA-Z0-9_-]/g, '-')
                    .replace(/-+/g, '-')
                    .toLowerCase();
            }

            function toggleRoNotes(roNumber) {
                const notesRow = document.getElementById(`notes-row-${safeId(roNumber)}`);
                if (!notesRow) return;
                const isHidden = notesRow.style.display === 'none' || notesRow.style.display === '';
                notesRow.style.display = isHidden ? 'table-row' : 'none';
                if (isHidden) {
                    loadRoNotes(roNumber);
                }
            }

            function loadRoNotes(roNumber) {
                const listEl = document.getElementById(`notes-list-${safeId(roNumber)}`);
                if (!listEl) return;
                listEl.innerHTML = '<div style="color:#777;">Loading...</div>';

                fetch(`/api/ro-notes?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (!res.notes || res.notes.length === 0) {
                            listEl.innerHTML = '<div style="color:#999;">No notes yet.</div>';
                            return;
                        }
                        listEl.innerHTML = res.notes.map(note => {
                            const when = note.created_at ? new Date(note.created_at).toLocaleString() : '';
                            return `
                                <div style="padding:6px 0; border-bottom:1px solid #eee;">
                                    <div style="font-size:12px; color:#777;">${when}</div>
                                    <div style="white-space:pre-wrap;">${note.note || ''}</div>
                                </div>
                            `;
                        }).join('');
                    })
                    .catch(err => {
                        console.error('Error loading notes:', err);
                        listEl.innerHTML = '<div style="color:red;">Error loading notes.</div>';
                    });
            }

            function saveRoNote(roNumber) {
                const input = document.getElementById(`notes-input-${safeId(roNumber)}`);
                if (!input) return;
                const text = (input.value || '').trim();
                if (!text) return;

                fetch('/api/ro-notes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ ro: roNumber, note: text })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    input.value = '';
                    loadRoNotes(roNumber);
                })
                .catch(err => {
                    console.error('Error saving note:', err);
                    alert('Error saving note.');
                });
            }

            // Update RO list table
            function updateRoListTable(roList) {
                const tbody = document.getElementById('roListBody');
                
                if (!roList || roList.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="padding:20px; text-align:center; color:#999;">No repair orders found</td></tr>';
                    return;
                }
                
                let html = '';
                roList.forEach((ro, index) => {
                    const rowBg = index % 2 === 0 ? '#fff' : '#f9f9f9';
                    const rowId = safeId(ro.ro);
                    const techLabel = ro.tech || 'Unassigned';
                    const painterLabel = ro.painter || 'Unassigned';
                    const customerDisplay = ro.customer || '-';
                    const phoneDisplay = ro.phone || '-';
                    html += `
                        <tr style="background:${rowBg}; cursor:pointer;" onclick="toggleRoNotes('${ro.ro}')">
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#0066cc; text-decoration:underline;">${ro.ro}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.vehicle || 'N/A'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${customerDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${phoneDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button type="button" onclick="openRepairLinesModal(event, '${ro.ro}', 'labor')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${techLabel}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button type="button" onclick="openRepairLinesModal(event, '${ro.ro}', 'paint')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${painterLabel}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333; text-align:right;">${ro.hours.toFixed(1)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333; text-align:right; font-weight:bold;">$${ro.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                        <tr id="notes-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="8" style="padding:12px 16px; border-bottom:1px solid #eee;">
                                <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;">
                                    <div style="font-weight:bold; margin-bottom:8px;">Notes</div>
                                    <div id="notes-list-${rowId}" style="max-height:180px; overflow-y:auto; margin-bottom:10px;"></div>
                                    <div style="display:flex; gap:10px;">
                                        <textarea id="notes-input-${rowId}" rows="2" style="flex:1; padding:8px; resize:vertical;" placeholder="Add note..."></textarea>
                                        <button onclick="saveRoNote('${ro.ro}')" style="padding:8px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Save</button>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `;
                });
                
                tbody.innerHTML = html;
            }

            function closeRepairLinesModal() {
                const modal = document.getElementById('repairLinesModal');
                if (modal) modal.style.display = 'none';
            }

            let currentRepairMode = 'labor';
            let currentRepairRo = '';
            let currentRepairLines = [];

            function normalizeLineKey(item, index) {
                return item.line !== null && item.line !== undefined ? String(item.line) : String(index + 1);
            }

            function updateAssignedTotal() {
                const totalEl = document.getElementById('repairLinesTotal');
                if (!totalEl) return;
                let total = 0.0;
                currentRepairLines.forEach((item, index) => {
                    const key = normalizeLineKey(item, index);
                    const checkbox = document.querySelector(`.repair-line-omit[data-line="${key}"]`);
                    if (checkbox && checkbox.checked) {
                        return;
                    }
                    const val = parseFloat(item.value);
                    if (Number.isFinite(val)) {
                        total += val;
                    }
                });
                totalEl.textContent = `Total Assigned: ${total.toFixed(1)} hrs`;
            }

            function renderRepairLines(lines, mode, assignment, techs) {
                const container = document.getElementById('repairLinesBody');
                if (!container) return;

                const techSelect = document.getElementById('repairLinesTech');
                if (techSelect) {
                    const options = ['<option value="">Select tech...</option>'];
                    (techs || []).forEach(tech => {
                        const label = `${tech.first_name || ''} ${tech.last_name || ''}`.trim() || `Tech #${tech.id}`;
                        options.push(`<option value="${tech.id}" data-name="${label}">${label}</option>`);
                    });
                    techSelect.innerHTML = options.join('');
                    if (assignment && assignment.tech_id) {
                        techSelect.value = String(assignment.tech_id);
                    }
                }

                const excluded = Array.isArray(assignment?.excluded_lines) ? assignment.excluded_lines.map(String) : [];

                if (!lines || lines.length === 0) {
                    container.innerHTML = '<div style="color:#777;">No repair lines found.</div>';
                    updateAssignedTotal();
                    return;
                }

                container.innerHTML = lines.map((item, index) => {
                    const lineKey = normalizeLineKey(item, index);
                    const line = item.line || lineKey || '—';
                    const desc = item.description || '';
                    const value = Number.isFinite(parseFloat(item.value)) ? parseFloat(item.value).toFixed(1) : '0.0';
                    const isOmitted = excluded.includes(lineKey);
                    return `
                        <div style="display:flex; align-items:center; gap:10px; padding:10px 8px; border-bottom:1px solid #eee;">
                            <div style="width:24px;"><input type="checkbox" class="repair-line-omit" data-line="${lineKey}" ${isOmitted ? 'checked' : ''} /></div>
                            <div style="flex:1;"><strong>Line ${line}</strong> - ${desc}</div>
                            <div style="min-width:80px; text-align:right; font-weight:bold;">${value} hrs</div>
                        </div>
                    `;
                }).join('');

                container.querySelectorAll('.repair-line-omit').forEach(checkbox => {
                    checkbox.addEventListener('change', updateAssignedTotal);
                });
                updateAssignedTotal();
            }

            function openRepairLinesModal(event, roNumber, mode) {
                if (event) {
                    event.stopPropagation();
                }
                const modal = document.getElementById('repairLinesModal');
                const title = document.getElementById('repairLinesTitle');
                const container = document.getElementById('repairLinesBody');
                if (!modal || !title || !container) return;

                currentRepairMode = mode === 'paint' ? 'paint' : 'labor';
                currentRepairRo = roNumber;
                currentRepairLines = [];

                const label = currentRepairMode === 'paint' ? 'Paint' : 'Labor';
                title.textContent = `${label} Repair Lines - RO# ${roNumber}`;
                container.innerHTML = '<div style="color:#777;">Loading...</div>';
                modal.style.display = 'block';

                Promise.all([
                    fetch(`/api/ro-repairs?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' }).then(r => r.json()),
                    fetch('/api/techs/list', { credentials: 'include' }).then(r => r.json())
                ])
                    .then(([repairsRes, techsRes]) => {
                        if (repairsRes.error) {
                            throw new Error(repairsRes.error);
                        }
                        const lines = currentRepairMode === 'paint' ? repairsRes.paint : repairsRes.labor;
                        const assignment = repairsRes.assignments ? repairsRes.assignments[currentRepairMode] : null;
                        const techs = techsRes.techs || [];
                        currentRepairLines = Array.isArray(lines) ? lines : [];
                        renderRepairLines(currentRepairLines, currentRepairMode, assignment, techs);
                    })
                    .catch(err => {
                        console.error('Error loading repair lines:', err);
                        container.innerHTML = '<div style="color:red;">Error loading repair lines.</div>';
                    });
            }

            function saveRepairAssignment() {
                if (!currentRepairRo) {
                    return;
                }

                const techSelect = document.getElementById('repairLinesTech');
                if (!techSelect || !techSelect.value) {
                    alert('Please select a tech.');
                    return;
                }
                const techId = parseInt(techSelect.value, 10);
                const techName = techSelect.options[techSelect.selectedIndex]?.dataset?.name || '';

                const excludedLines = [];
                currentRepairLines.forEach((item, index) => {
                    const key = normalizeLineKey(item, index);
                    const checkbox = document.querySelector(`.repair-line-omit[data-line="${key}"]`);
                    if (checkbox && checkbox.checked) {
                        excludedLines.push(key);
                    }
                });

                fetch('/api/ro-assignments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        ro: currentRepairRo,
                        role: currentRepairMode,
                        tech_id: techId,
                        tech_name: techName,
                        excluded_lines: excludedLines
                    })
                })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        closeRepairLinesModal();
                        loadDashboardData();
                    })
                    .catch(err => {
                        console.error('Error saving assignment:', err);
                        alert('Error saving assignment.');
                    });
            }
            
            // Load dashboard data when dashboard screen is shown
            // We'll call this from the switchScreen function
            window.loadDashboardDataIfNeeded = function() {
                // Check if dashboard screen is active
                const dashboardScreen = document.getElementById('dashboard');
                if (dashboardScreen && dashboardScreen.classList.contains('active')) {
                    loadDashboardData();
                }
            };
            
            // Load initially if dashboard is the first screen (unlikely but handle it)
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', loadDashboardDataIfNeeded);
            } else {
                loadDashboardDataIfNeeded();
            }
        </script>
    """

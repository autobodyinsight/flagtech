"""Dashboard screen content for the FlagTech UI."""


def get_dashboard_screen_html():
    """Return the HTML content for the Dashboard screen."""
    return r"""
        <div id="dashboard" class="screen active" style="padding:20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
                <h1 style="text-align:center; margin:0; flex:1;">DASHBOARD</h1>
                <button onclick="flashAllData()" style="padding:10px 16px; background:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">FLASH</button>
            </div>
            
            <div style="display:flex; gap:20px; align-items:stretch; --dash-chart-h: 520px; --dash-card-h: calc((var(--dash-chart-h) - 40px) / 3);">
                <style>
                    .dash-stack { display:flex; flex-direction:column; gap:20px; }
                    .dash-card { height: var(--dash-card-h); }
                    .dash-card-fill { flex:1; }
                    .dash-chart { height: var(--dash-chart-h); }
                </style>
                <!-- Column 1: Current Sales + Total ROs -->
                <div style="flex:0 0 300px;" class="dash-stack">
                    <div style="background:#f9f9f9; padding:20px; border-radius:8px; border:1px solid #ddd; display:flex; flex-direction:column;" class="dash-card">
                        <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Current Sales</h3>
                        <div style="position:relative; background:#e0e0e0; border-radius:4px; overflow:hidden;" class="dash-card-fill">
                            <div id="totalSalesBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #4caf50, #81c784); transition:height 0.5s ease;">
                            </div>
                        </div>
                        <div id="totalSalesValue" style="text-align:center; font-size:20px; font-weight:bold; color:#4caf50; margin-top:10px;">
                            $0
                        </div>
                    </div>

                    <div style="background:#f9f9f9; padding:20px; border-radius:8px; border:1px solid #ddd; display:flex; flex-direction:column;" class="dash-card">
                        <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Total RO's</h3>
                        <div style="position:relative; background:#e0e0e0; border-radius:4px; overflow:hidden;" class="dash-card-fill">
                            <div id="totalRosBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #42a5f5, #90caf9); transition:height 0.5s ease;">
                            </div>
                        </div>
                        <div id="totalRosValue" style="text-align:center; font-size:20px; font-weight:bold; color:#42a5f5; margin-top:10px;">
                            0
                        </div>
                    </div>
                </div>

                <!-- Column 2: Average Hrs + Average RO + Total ROs per Tech -->
                <div style="flex:0 0 320px;" class="dash-stack">
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #9c27b0; box-shadow:0 2px 4px rgba(0,0,0,0.1);" class="dash-card">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Average Hrs</h4>
                        <div id="averageHrs" style="font-size:32px; font-weight:bold; color:#9c27b0;">
                            0.0
                        </div>
                    </div>

                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #ff5722; box-shadow:0 2px 4px rgba(0,0,0,0.1);" class="dash-card">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Average RO</h4>
                        <div id="averageRO" style="font-size:32px; font-weight:bold; color:#ff5722;">
                            $0
                        </div>
                    </div>

                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #795548; box-shadow:0 2px 4px rgba(0,0,0,0.1);" class="dash-card">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Total ROs per Tech</h4>
                        <div id="rosPerTechList" style="height:100%; overflow-y:auto; font-size:14px;">
                            <div style="color:#999; text-align:center;">Loading...</div>
                        </div>
                    </div>
                </div>

                <!-- Column 3: Total Hrs per Tech -->
                <div style="flex:1; display:flex; flex-direction:column;">
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #00bcd4; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; flex-direction:column;" class="dash-chart">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Total Hrs per Tech</h4>
                        <div style="display:flex; gap:16px; align-items:center; width:100%; flex:1;">
                            <div style="flex:0 0 55%; max-width:55%; height:100%;">
                                <canvas id="hoursPerTechChart" style="height:100%; width:100%;"></canvas>
                            </div>
                            <div id="hoursPerTechLegend" style="flex:1; font-size:12px; color:#333; max-height:100%; overflow:auto;"></div>
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
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Insurance</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Claim #</th>
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

        <div id="assignmentModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; max-height:85vh; overflow-y:auto;">
                <span class="close" onclick="closeAssignmentModal()">&times;</span>
                <h2 id="assignmentModalTitle" style="margin-bottom:16px;">Assign Tech</h2>
                <div style="margin-bottom:12px;">
                    <label for="assignmentTechSelect" style="font-weight:bold; font-size:12px; color:#666;">TECH</label>
                    <select id="assignmentTechSelect" style="width:100%; padding:8px; margin-top:6px;"></select>
                </div>
                <div id="assignmentTypeWrap" style="margin-bottom:12px; display:none;">
                    <label for="assignmentTypeSelect" style="font-weight:bold; font-size:12px; color:#666;">TYPE</label>
                    <select id="assignmentTypeSelect" style="width:100%; padding:8px; margin-top:6px;">
                        <option value="body">body</option>
                        <option value="mech">mech</option>
                        <option value="other">other</option>
                        <option value="paint">paint</option>
                    </select>
                </div>
                <div style="margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                    <input type="checkbox" id="assignmentSelectAll" onchange="toggleAssignmentSelectAll()" />
                    <label for="assignmentSelectAll" style="font-weight:bold; font-size:12px;">Select all</label>
                </div>
                <div id="assignmentModalBody"></div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                    <div id="assignmentModalTotal" style="font-weight:bold;">Total: 0.0 hrs</div>
                    <div style="display:flex; gap:8px;">
                        <button type="button" onclick="printAssignmentModal()" style="padding:8px 16px; background:#9c27b0; color:#fff; border:none; border-radius:4px; cursor:pointer;">Print</button>
                        <button id="assignmentModalSave" onclick="saveAssignmentModal()" style="padding:8px 16px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Save</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="techDetailModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:800px; max-height:80vh; overflow-y:auto;">
                <span class="close" onclick="closeTechDetailModal()" style="color:#d32f2f; font-size:32px;">&times;</span>
                <h2 id="techDetailTitle" style="margin-bottom:16px;">Tech Repair Lines</h2>
                <div id="techDetailBody" style="margin-bottom:16px;"></div>
                <div style="display:flex; justify-content:space-between; align-items:center; padding-top:12px; border-top:2px solid #ddd;">
                    <div id="techDetailTotal" style="font-weight:bold; font-size:18px;">Total: 0.0 hrs</div>
                    <button onclick="printTechDetail()" style="padding:10px 20px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">PRINT</button>
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
                color: #000;
            }
            .modal-content * {
                color: #000;
            }
            .modal-content button {
                color: #fff !important;
            }
            .modal-content .close {
                color: #000 !important;
            }
            button:not(.link-button) {
                background: #b22222 !important;
                color: #fff !important;
                border: none !important;
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
            
            // Load dashboard data
            async function loadDashboardData() {
                try {
                    const response = await fetch('/api/dashboard-data', { credentials: 'include' });
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
                    totalROs: 0,
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
                    const response = await fetch('/api/flash', { method: 'POST', credentials: 'include' });
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
                const maxSales = Math.max(data.totalSales, 10000); // minimum scale
                const salesPercent = (data.totalSales / maxSales) * 100;
                document.getElementById('totalSalesBar').style.height = salesPercent + '%';
                document.getElementById('totalSalesValue').innerText = '$' + data.totalSales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

                const maxRos = Math.max(data.totalROs, 1);
                const rosPercent = (data.totalROs / maxRos) * 100;
                document.getElementById('totalRosBar').style.height = rosPercent + '%';
                document.getElementById('totalRosValue').innerText = data.totalROs.toLocaleString('en-US');
                
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
                const legendEl = document.getElementById('hoursPerTechLegend');
                
                if (!ctx) return;
                if (!legendEl) return;

                if (!hoursPerTech || hoursPerTech.length === 0) {
                    if (hoursPerTechChartInstance) {
                        hoursPerTechChartInstance.destroy();
                        hoursPerTechChartInstance = null;
                    }
                    legendEl.innerHTML = '<div style="color:#999; text-align:center;">No data</div>';
                    return;
                }
                
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
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
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

                legendEl.innerHTML = labels.map((label, idx) => {
                    const color = colors[idx % colors.length];
                    const value = dataValues[idx];
                    return `
                        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; padding:4px 0; border-bottom:1px solid #eee;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span style="width:10px; height:10px; background:${color}; display:inline-block; border-radius:2px;"></span>
                                <span>${label}</span>
                            </div>
                            <span style="font-weight:bold;">${value.toFixed(1)} hrs</span>
                        </div>
                    `;
                }).join('');
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
                        if (!listEl) return;
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
                        if (listEl) {
                            listEl.innerHTML = '<div style="color:red;">Error loading notes.</div>';
                        }
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

            function toggleRoNotesFromLink(event, roNumber) {
                if (event) event.stopPropagation();
                toggleRoNotes(roNumber);
            }

            function toggleOldPhone(event, rowId) {
                if (event) event.stopPropagation();
                const oldEl = document.getElementById(`phone-old-${rowId}`);
                if (!oldEl) return;
                oldEl.style.display = oldEl.style.display === 'none' ? 'inline-block' : 'none';
            }

            function startPhoneEdit(event, rowId) {
                if (event) event.stopPropagation();
                const displayEl = document.getElementById(`phone-display-${rowId}`);
                const editEl = document.getElementById(`phone-edit-${rowId}`);
                if (!displayEl || !editEl) return;
                displayEl.style.display = 'none';
                editEl.style.display = 'inline-flex';
                const input = document.getElementById(`phone-input-${rowId}`);
                if (input) {
                    input.focus();
                    input.select();
                }
            }

            function cancelPhoneEdit(event, rowId) {
                if (event) event.stopPropagation();
                const displayEl = document.getElementById(`phone-display-${rowId}`);
                const editEl = document.getElementById(`phone-edit-${rowId}`);
                if (!displayEl || !editEl) return;
                editEl.style.display = 'none';
                displayEl.style.display = 'inline-flex';
            }

            function confirmPhoneEdit(event, rowId, roNumber) {
                if (event) event.stopPropagation();
                const input = document.getElementById(`phone-input-${rowId}`);
                const displayValue = document.getElementById(`phone-current-${rowId}`);
                const oldValue = document.getElementById(`phone-old-value-${rowId}`);
                if (!input || !displayValue || !oldValue) return;

                const newPhone = (input.value || '').trim();
                if (!newPhone) {
                    alert('Please enter a phone number.');
                    return;
                }

                fetch('/api/ro-phone', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ ro: roNumber, phone: newPhone })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    displayValue.textContent = res.phone || newPhone;
                    oldValue.textContent = res.phone_original || oldValue.textContent;
                    cancelPhoneEdit(event, rowId);
                })
                .catch(err => {
                    console.error('Error updating phone:', err);
                    alert('Error updating phone.');
                });
            }

            // Clean phone number to display only digits
            function cleanPhoneNumber(phone) {
                if (!phone || phone === '-') return '-';
                // Extract only numeric characters
                const digits = phone.replace(/\D/g, '');
                if (!digits) return '-';
                // Format as (XXX) XXX-XXXX if 10 digits, otherwise just return digits
                if (digits.length === 10) {
                    return `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}`;
                }
                return digits;
            }

            let keepOpenRo = '';

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
                    const customerDisplay = ro.customer || '-';
                    const phoneDisplay = cleanPhoneNumber(ro.phone);
                    const insuranceDisplay = (ro.insurance || '-').split(/\s+/).slice(0, 2).join(' ');
                    const claimDisplay = ro.claim_number || '-';
                    const phoneOriginal = cleanPhoneNumber(ro.phone_original) || phoneDisplay || '-';
                    html += `
                        <tr style="background:${rowBg};">
                            <td style="padding:12px; border-bottom:1px solid #eee;">
                                <button type="button" class="link-button" onclick="toggleRoNotesFromLink(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${ro.ro}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.vehicle || 'N/A'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${customerDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <span id="phone-display-${rowId}" style="display:inline-flex; align-items:center; gap:6px;">
                                    <button type="button" class="link-button" onclick="startPhoneEdit(event, '${rowId}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                        <span id="phone-current-${rowId}">${phoneDisplay}</span>
                                    </button>
                                    <button type="button" onclick="toggleOldPhone(event, '${rowId}')" style="background:#eee; border:1px solid #ccc; border-radius:3px; padding:0 6px; font-size:12px; cursor:pointer;">+</button>
                                    <span id="phone-old-${rowId}" style="display:none; font-size:12px; color:#777;">Old: <span id="phone-old-value-${rowId}">${phoneOriginal}</span></span>
                                </span>
                                <span id="phone-edit-${rowId}" style="display:none; align-items:center; gap:6px;">
                                    <input id="phone-input-${rowId}" value="${phoneDisplay === '-' ? '' : phoneDisplay}" style="padding:4px 6px; width:140px;" />
                                    <button type="button" onclick="confirmPhoneEdit(event, '${rowId}', '${ro.ro}')" style="padding:4px 8px; font-size:12px; background:#4CAF50; color:#fff; border:none; border-radius:4px; cursor:pointer;">Confirm</button>
                                    <button type="button" onclick="cancelPhoneEdit(event, '${rowId}')" style="padding:4px 8px; font-size:12px; background:#999; color:#fff; border:none; border-radius:4px; cursor:pointer;">Cancel</button>
                                </span>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${insuranceDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${claimDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right;">
                                <button type="button" class="link-button" onclick="toggleTechAssignment(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${ro.hours.toFixed(1)}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333; text-align:right; font-weight:bold;">$${ro.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                        <tr id="tech-assignment-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="8" style="padding:16px; border-bottom:1px solid #eee;">
                                <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:16px;">
                                    <div id="tech-assignment-list-${rowId}" style="margin-top:12px;">
                                        <div style="color:#777;">Loading...</div>
                                    </div>
                                </div>
                            </td>
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

                if (keepOpenRo) {
                    const openRow = document.getElementById(`tech-assignment-row-${safeId(keepOpenRo)}`);
                    if (openRow) {
                        openRow.style.display = 'table-row';
                        loadRoAssignmentsSummary(keepOpenRo);
                    }
                }
            }

            function closeRepairLinesModal() {
                const modal = document.getElementById('repairLinesModal');
                if (modal) modal.style.display = 'none';
            }

            function toggleTechAssignment(event, roNumber) {
                if (event) event.stopPropagation();
                const assignmentRow = document.getElementById(`tech-assignment-row-${safeId(roNumber)}`);
                if (!assignmentRow) return;
                const isHidden = assignmentRow.style.display === 'none' || assignmentRow.style.display === '';
                assignmentRow.style.display = isHidden ? 'table-row' : 'none';
                if (isHidden) {
                    keepOpenRo = roNumber;
                    loadRoAssignmentsSummary(roNumber);
                } else if (keepOpenRo === roNumber) {
                    keepOpenRo = '';
                }
            }

            function getLineHours(line) {
                const raw = line && (line.hours !== undefined ? line.hours : line.value);
                const val = parseFloat(raw);
                return Number.isFinite(val) ? val : 0;
            }

            function calculateTotalHours(lines) {
                let total = 0.0;
                (lines || []).forEach(line => {
                    total += getLineHours(line);
                });
                return total;
            }

            function calculateAssignedHours(lines, excludedLines) {
                const excluded = new Set((excludedLines || []).map(String));
                let total = 0.0;
                (lines || []).forEach((line, index) => {
                    const key = normalizeLineKey(line, index);
                    if (excluded.has(String(key))) {
                        return;
                    }
                    total += getLineHours(line);
                });
                return total;
            }

            function sumPendingHours(pendingLines, labor, paint) {
                const laborMap = {};
                const paintMap = {};

                (labor || []).forEach((item, index) => {
                    laborMap[normalizeLineKey(item, index)] = item;
                });
                (paint || []).forEach((item, index) => {
                    paintMap[normalizeLineKey(item, index)] = item;
                });

                let total = 0.0;
                (pendingLines || []).forEach(entry => {
                    if (!entry || typeof entry !== 'object') return;
                    const role = String(entry.role || '').toLowerCase();
                    const lineKey = String(entry.line || '');
                    if (!lineKey) return;
                    const source = role === 'paint' ? paintMap : laborMap;
                    const item = source[lineKey];
                    if (!item) return;
                    total += getLineHours(item);
                });
                return total;
            }

            function buildPendingLines(pendingLines, labor, paint) {
                const laborMap = {};
                const paintMap = {};

                (labor || []).forEach((item, index) => {
                    laborMap[normalizeLineKey(item, index)] = item;
                });
                (paint || []).forEach((item, index) => {
                    paintMap[normalizeLineKey(item, index)] = item;
                });

                const results = [];
                (pendingLines || []).forEach(entry => {
                    if (!entry || typeof entry !== 'object') return;
                    const role = String(entry.role || '').toLowerCase();
                    const lineKey = String(entry.line || '');
                    if (!lineKey) return;
                    const source = role === 'paint' ? paintMap : laborMap;
                    const item = source[lineKey];
                    if (!item) return;
                    results.push({
                        pending_role: role,
                        pending_line_key: lineKey,
                        line: item.line || lineKey,
                        description: item.description || '',
                        value: item.value || item.hours || 0
                    });
                });
                return results;
            }

            function loadRoAssignmentsSummary(roNumber) {
                const listEl = document.getElementById(`tech-assignment-list-${safeId(roNumber)}`);
                if (!listEl) {
                    console.error('Could not find element:', `tech-assignment-list-${safeId(roNumber)}`);
                    return;
                }

                // Fetch repair data with assignments
                fetch(`/api/ro-repairs?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(data => {
                        console.log('Loaded repair data:', data);
                        
                        const labor = data.labor || [];
                        const paint = data.paint || [];
                        const assignments = data.assignments || {};
                        const assignmentRows = data.assignment_rows || [];

                        const laborExcluded = assignments.labor?.excluded_lines || [];
                        const paintExcluded = assignments.paint?.excluded_lines || [];
                        const pendingLines = assignments.pending?.excluded_lines || [];
                        const pendingType = assignments.pending?.pending_type || 'body';

                        const laborTotalAll = calculateTotalHours(labor);
                        const paintTotalAll = calculateTotalHours(paint);
                        const laborAssigned = calculateAssignedHours(labor, laborExcluded);
                        const paintAssigned = calculateAssignedHours(paint, paintExcluded);
                        const pendingLaborHours = sumPendingHours(
                            (pendingLines || []).filter(entry => String(entry?.role || '').toLowerCase() === 'labor'),
                            labor,
                            []
                        );
                        const pendingPaintHours = sumPendingHours(
                            (pendingLines || []).filter(entry => String(entry?.role || '').toLowerCase() === 'paint'),
                            [],
                            paint
                        );
                        const laborUnassigned = Math.max(
                            0,
                            laborTotalAll - pendingLaborHours - assignedTotals.labor
                        );
                        const paintUnassigned = Math.max(
                            0,
                            paintTotalAll - pendingPaintHours - assignedTotals.paint
                        );

                        const displayList = [];
                        const assignedTotals = { labor: 0.0, paint: 0.0 };

                        assignmentRows.forEach(row => {
                            const role = String(row.role || '').toLowerCase();
                            if (role !== 'labor' && role !== 'paint') return;
                            if (!row.tech_name) return;
                            const typeLabel = row.pending_type || (role === 'paint' ? 'paint' : 'body');
                            const hours = Number.isFinite(parseFloat(row.assigned_hours))
                                ? parseFloat(row.assigned_hours)
                                : 0.0;
                            assignedTotals[role] += hours;
                            displayList.push({
                                role: role,
                                tech_name: row.tech_name,
                                type_label: typeLabel,
                                hours: hours.toFixed(1),
                                is_assigned: true,
                                tech_id: row.tech_id
                            });
                        });

                        if (labor.length > 0 && laborUnassigned > 0) {
                            displayList.push({
                                role: 'labor',
                                tech_name: 'unassigned',
                                type_label: 'body',
                                hours: laborUnassigned.toFixed(1),
                                is_assigned: false,
                                tech_id: null
                            });
                        }

                        if (paint.length > 0 && paintUnassigned > 0) {
                            displayList.push({
                                role: 'paint',
                                tech_name: 'unassigned',
                                type_label: 'paint',
                                hours: paintUnassigned.toFixed(1),
                                is_assigned: false,
                                tech_id: null
                            });
                        }

                        const pendingTotal = sumPendingHours(pendingLines, labor, paint);
                        if (pendingTotal > 0) {
                            displayList.push({
                                role: 'pending',
                                tech_name: 'Pending',
                                type_label: pendingType,
                                hours: pendingTotal.toFixed(1),
                                is_assigned: false,
                                tech_id: null
                            });
                        }

                        let html = '';

                        if (displayList.length === 0) {
                            html = '<div style="color:#999; padding:12px;">No repair data found.</div>';
                        } else {
                            html = '<table style="width:100%; border-collapse:collapse; margin-top:8px;">';
                            html += '<thead><tr style="background:#d9d9d9; border-bottom:2px solid #999;">';
                            html += '<th style="padding:8px 12px; text-align:left; font-weight:bold; color:#333;">TECH</th>';
                            html += '<th style="padding:8px 12px; text-align:left; font-weight:bold; color:#333;">TYPE</th>';
                            html += '<th style="padding:8px 12px; text-align:right; font-weight:bold; color:#333;">TOTAL</th>';
                            html += '</tr></thead><tbody>';

                            displayList.forEach((item) => {
                                const textColor = item.is_assigned ? '#333' : '#d32f2f';
                                const fontWeight = item.is_assigned ? 'normal' : 'bold';

                                html += `<tr style="background:#fff; border-bottom:1px solid #ddd;">`;
                                html += `<td style="padding:8px 12px; color:${textColor}; font-weight:${fontWeight};">`;
                                html += `<button type="button" class="link-button" onclick="openAssignmentModal(event, '${roNumber}', '${item.role}')" style="background:none; border:none; color:${textColor}; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:${fontWeight};">${item.tech_name}</button>`;
                                html += `</td>`;
                                html += `<td style="padding:8px 12px; color:#333; text-transform:capitalize;">${item.type_label}</td>`;
                                html += `<td style="padding:8px 12px; text-align:right; color:#333; font-weight:bold;">${item.hours}</td>`;
                                html += '</tr>';
                            });

                            html += '</tbody></table>';
                        }
                        
                        if (listEl) {
                            listEl.innerHTML = html;
                        }
                    })
                    .catch(err => {
                        console.error('Error loading repair data:', err);
                        if (listEl) {
                            listEl.innerHTML = '<div style="color:red; padding:12px;">Error loading data. Check console.</div>';
                        }
                    });
            }

            let currentAssignmentModal = {
                ro: '',
                role: '',
                lines: [],
                assignment: null,
                pendingLines: [],
                pendingType: 'body',
                assignmentsByRole: {}
            };

            function closeAssignmentModal() {
                const modal = document.getElementById('assignmentModal');
                if (modal) modal.style.display = 'none';
            }

            function openAssignmentModal(event, roNumber, role) {
                if (event) event.stopPropagation();
                const modal = document.getElementById('assignmentModal');
                const title = document.getElementById('assignmentModalTitle');
                const body = document.getElementById('assignmentModalBody');
                const typeWrap = document.getElementById('assignmentTypeWrap');
                const typeSelect = document.getElementById('assignmentTypeSelect');

                if (!modal || !title || !body) return;

                const roleLabel = role === 'paint' ? 'Paint' : 'Body';
                title.textContent = role === 'pending'
                    ? `Pending Assignments - RO# ${roNumber}`
                    : `${roleLabel} Assignments - RO# ${roNumber}`;
                body.innerHTML = '<div style="color:#777;">Loading repair lines...</div>';
                modal.style.display = 'block';

                Promise.all([
                    fetch(`/api/ro-repairs?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' }).then(r => r.json()),
                    fetch('/api/techs/list', { credentials: 'include' }).then(r => r.json())
                ])
                    .then(([repairsRes, techsRes]) => {
                        if (repairsRes.error) {
                            throw new Error(repairsRes.error);
                        }
                        const lines = role === 'paint' ? (repairsRes.paint || []) : (repairsRes.labor || []);
                        const assignmentsByRole = repairsRes.assignments || {};
                        const assignment = assignmentsByRole ? assignmentsByRole[role] : null;
                        const techs = techsRes.techs || [];
                        const pendingAssignment = assignmentsByRole.pending || {};
                        const pendingLines = pendingAssignment.excluded_lines || [];
                        const pendingType = pendingAssignment.pending_type || 'body';

                        let modalLines = lines;
                        if (role === 'pending') {
                            modalLines = buildPendingLines(pendingLines, repairsRes.labor || [], repairsRes.paint || []);
                        }

                        currentAssignmentModal = {
                            ro: roNumber,
                            role: role,
                            lines: Array.isArray(modalLines) ? modalLines : [],
                            assignment: assignment,
                            pendingLines: Array.isArray(pendingLines) ? pendingLines : [],
                            pendingType: pendingType,
                            assignmentsByRole: assignmentsByRole
                        };

                        populateAssignmentTechSelect(techs, assignment);
                        if (typeWrap && typeSelect) {
                            if (role === 'pending') {
                                typeWrap.style.display = 'block';
                                typeSelect.value = pendingType || 'body';
                            } else {
                                typeWrap.style.display = 'none';
                            }
                        }
                        renderAssignmentModalBody(currentAssignmentModal.lines, assignment);
                    })
                    .catch(err => {
                        console.error('Error loading assignment modal:', err);
                        body.innerHTML = '<div style="color:red;">Error loading repair lines.</div>';
                    });
            }

            function populateAssignmentTechSelect(techs, assignment) {
                const select = document.getElementById('assignmentTechSelect');
                if (!select) return;

                const options = ['<option value="">unassigned</option>'];
                (techs || []).forEach(tech => {
                    const label = `${tech.first_name || ''} ${tech.last_name || ''}`.trim() || `Tech #${tech.id}`;
                    options.push(`<option value="${tech.id}" data-name="${label}">${label}</option>`);
                });
                select.innerHTML = options.join('');

                if (assignment && assignment.tech_id) {
                    select.value = String(assignment.tech_id);
                } else {
                    select.value = '';
                }
            }

            function renderAssignmentModalBody(lines, assignment) {
                const body = document.getElementById('assignmentModalBody');
                if (!body) return;
                const selectAll = document.getElementById('assignmentSelectAll');

                const excluded = Array.isArray(assignment?.excluded_lines) ? assignment.excluded_lines.map(String) : [];

                if (!lines || lines.length === 0) {
                    body.innerHTML = '<div style="color:#777;">No repair lines found.</div>';
                    if (selectAll) {
                        selectAll.checked = false;
                        selectAll.disabled = true;
                    }
                    updateAssignmentModalTotal();
                    return;
                }

                const rows = lines.map((item, index) => {
                    const lineKey = item.pending_role
                        ? `${item.pending_role}:${item.pending_line_key}`
                        : normalizeLineKey(item, index);
                    const line = item.line || lineKey || '—';
                    const desc = item.description || '';
                    const hours = getLineHours(item);
                    const value = hours.toFixed(1);
                    const isOmitted = currentAssignmentModal.role === 'pending'
                        ? false
                        : excluded.includes(String(lineKey));

                    return `
                        <div style="display:flex; align-items:center; gap:12px; padding:10px 12px; border-bottom:1px solid #eee; background:#fff;">
                            <div style="width:24px;">
                                <input type="checkbox" class="assignment-omit" data-line="${lineKey}" data-hrs="${value}" ${isOmitted ? 'checked' : ''} onchange="updateAssignmentModalTotal()" />
                            </div>
                            <div style="flex:1; font-size:13px; color:#333;">
                                <strong>Line ${line}</strong> - ${desc}
                            </div>
                            <div style="min-width:70px; text-align:right; font-weight:bold; font-size:13px;">${value} hrs</div>
                        </div>
                    `;
                }).join('');

                body.innerHTML = `
                    <div style="border:1px solid #ddd; border-radius:4px; background:#fff; max-height:220px; overflow-y:auto;">
                        ${rows}
                    </div>
                `;

                if (selectAll) {
                    selectAll.disabled = false;
                    const totalBoxes = body.querySelectorAll('input.assignment-omit').length;
                    const checkedBoxes = body.querySelectorAll('input.assignment-omit:checked').length;
                    selectAll.checked = totalBoxes > 0 && totalBoxes === checkedBoxes;
                }

                updateAssignmentModalTotal();
            }

            function toggleAssignmentSelectAll() {
                const body = document.getElementById('assignmentModalBody');
                const selectAll = document.getElementById('assignmentSelectAll');
                if (!body || !selectAll) return;
                body.querySelectorAll('input.assignment-omit').forEach(checkbox => {
                    checkbox.checked = selectAll.checked;
                });
                updateAssignmentModalTotal();
            }

            function updateAssignmentModalTotal() {
                const totalEl = document.getElementById('assignmentModalTotal');
                const body = document.getElementById('assignmentModalBody');
                if (!totalEl || !body) return;

                let total = 0.0;
                body.querySelectorAll('input.assignment-omit').forEach(checkbox => {
                    if (!checkbox.checked) {
                        const hrs = parseFloat(checkbox.getAttribute('data-hrs'));
                        if (Number.isFinite(hrs)) {
                            total += hrs;
                        }
                    }
                });

                totalEl.textContent = `Total: ${total.toFixed(1)} hrs`;

                const selectAll = document.getElementById('assignmentSelectAll');
                if (selectAll && !selectAll.disabled) {
                    const totalBoxes = body.querySelectorAll('input.assignment-omit').length;
                    const checkedBoxes = body.querySelectorAll('input.assignment-omit:checked').length;
                    selectAll.checked = totalBoxes > 0 && totalBoxes === checkedBoxes;
                }
            }

            function saveAssignmentModal() {
                if (!currentAssignmentModal.ro || !currentAssignmentModal.role) return;

                const body = document.getElementById('assignmentModalBody');
                const select = document.getElementById('assignmentTechSelect');
                const typeSelect = document.getElementById('assignmentTypeSelect');
                if (!body || !select) return;

                const excludedLines = [];
                body.querySelectorAll('input.assignment-omit:checked').forEach(checkbox => {
                    excludedLines.push(checkbox.getAttribute('data-line'));
                });

                const techIdRaw = select.value;
                const techId = techIdRaw ? parseInt(techIdRaw, 10) : null;
                const techName = techIdRaw
                    ? (select.options[select.selectedIndex]?.dataset?.name || '')
                    : '';

                const pendingType = typeSelect && currentAssignmentModal.role === 'pending'
                    ? (typeSelect.value || 'body')
                    : (currentAssignmentModal.pendingType || 'body');

                if (currentAssignmentModal.role === 'pending') {
                    const pendingKeep = excludedLines.map(entry => {
                        const parts = String(entry).split(':');
                        return { role: parts[0], line: parts[1] };
                    });

                    const uncheckedLines = currentAssignmentModal.lines
                        .map((item, index) => {
                            const lineKey = item.pending_role
                                ? `${item.pending_role}:${item.pending_line_key}`
                                : normalizeLineKey(item, index);
                            return {
                                key: lineKey,
                                role: item.pending_role,
                                line: item.pending_line_key || normalizeLineKey(item, index)
                            };
                        })
                        .filter(item => !excludedLines.includes(item.key));

                    if (uncheckedLines.length > 0 && !techIdRaw) {
                        alert('Please select a tech to assign pending lines.');
                        return;
                    }

                    const byRole = {
                        labor: new Set(),
                        paint: new Set()
                    };
                    uncheckedLines.forEach(item => {
                        if (item.role === 'labor' || item.role === 'paint') {
                            byRole[item.role].add(String(item.line));
                        }
                    });

                    const updates = [];
                    ['labor', 'paint'].forEach(role => {
                        if (byRole[role].size === 0) return;
                        const payload = {
                            ro: currentAssignmentModal.ro,
                            role: role,
                            tech_id: Number.isFinite(techId) ? techId : null,
                            tech_name: techIdRaw ? techName : '',
                            included_lines: Array.from(byRole[role]),
                            pending_type: pendingType
                        };
                        updates.push(fetch('/api/ro-assignments', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            credentials: 'include',
                            body: JSON.stringify(payload)
                        }).then(r => r.json()));
                    });

                    updates.push(fetch('/api/ro-assignments', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({
                            ro: currentAssignmentModal.ro,
                            role: 'pending',
                            tech_id: null,
                            tech_name: '',
                            excluded_lines: pendingKeep,
                            pending_type: pendingType
                        })
                    }).then(r => r.json()));

                    Promise.all(updates)
                        .then(results => {
                            if (results.some(res => res.error)) {
                                throw new Error('One or more assignments failed');
                            }
                            closeAssignmentModal();
                            keepOpenRo = currentAssignmentModal.ro;
                            loadRoAssignmentsSummary(currentAssignmentModal.ro);
                            loadDashboardData();
                        })
                        .catch(err => {
                            console.error('Error saving assignment modal:', err);
                            alert('Error saving assignment.');
                        });
                    return;
                }

                const pendingFiltered = (currentAssignmentModal.pendingLines || []).filter(entry => {
                    return entry && entry.role && entry.role !== currentAssignmentModal.role;
                });
                const pendingMerged = pendingFiltered.concat(
                    excludedLines.map(lineKey => ({ role: currentAssignmentModal.role, line: lineKey }))
                );

                const requests = [
                    fetch('/api/ro-assignments', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({
                            ro: currentAssignmentModal.ro,
                            role: currentAssignmentModal.role,
                            tech_id: Number.isFinite(techId) ? techId : null,
                            tech_name: techName,
                            excluded_lines: excludedLines
                        })
                    }).then(r => r.json()),
                    fetch('/api/ro-assignments', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({
                            ro: currentAssignmentModal.ro,
                            role: 'pending',
                            tech_id: null,
                            tech_name: '',
                            excluded_lines: pendingMerged,
                            pending_type: pendingType
                        })
                    }).then(r => r.json())
                ];

                Promise.all(requests)
                    .then(results => {
                        if (results.some(res => res.error)) {
                            throw new Error('One or more assignments failed');
                        }
                        closeAssignmentModal();
                        keepOpenRo = currentAssignmentModal.ro;
                        loadRoAssignmentsSummary(currentAssignmentModal.ro);
                        loadDashboardData();
                    })
                    .catch(err => {
                        console.error('Error saving assignment modal:', err);
                        alert('Error saving assignment.');
                    });
            }

            function printAssignmentModal() {
                if (!currentAssignmentModal.ro || !currentAssignmentModal.role) return;

                const body = document.getElementById('assignmentModalBody');
                const totalEl = document.getElementById('assignmentModalTotal');
                const techSelect = document.getElementById('assignmentTechSelect');
                if (!body || !totalEl) return;

                const roleLabel = currentAssignmentModal.role === 'paint' ? 'Paint' : 'Body';
                const titleText = `${roleLabel} Assignments - RO# ${currentAssignmentModal.ro}`;
                const techName = techSelect && techSelect.value
                    ? (techSelect.options[techSelect.selectedIndex]?.dataset?.name || '')
                    : 'unassigned';

                const rows = currentAssignmentModal.lines.map((item, index) => {
                    const lineKey = item.pending_role
                        ? `${item.pending_role}:${item.pending_line_key}`
                        : normalizeLineKey(item, index);
                    const line = item.line || lineKey || '—';
                    const desc = item.description || '';
                    const hours = getLineHours(item).toFixed(1);
                    const checkbox = body.querySelector(`input.assignment-omit[data-line="${lineKey}"]`);
                    const omitted = checkbox && checkbox.checked;
                    return {
                        line,
                        desc,
                        hours,
                        omitted
                    };
                }).filter(row => !row.omitted);

                const printWindow = window.open('', '_blank');
                const rowsHtml = rows.map(row => {
                    return `
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:8px;">Line ${row.line}</td>
                            <td style="padding:8px;">${row.desc}</td>
                            <td style="padding:8px; text-align:right; font-weight:bold;">${row.hours} hrs</td>
                        </tr>
                    `;
                }).join('');

                printWindow.document.write(`
                    <html>
                        <head>
                            <title>${titleText}</title>
                            <style>
                                @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap');
                                * { box-sizing: border-box; }
                                body {
                                    font-family: 'DM Sans', 'Segoe UI', Tahoma, Arial, sans-serif;
                                    padding: 28px;
                                    color: #1f2933;
                                    background: #f6f7f9;
                                }
                                .sheet {
                                    background: #ffffff;
                                    border: 1px solid #e3e7ee;
                                    border-radius: 12px;
                                    padding: 24px;
                                    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
                                }
                                .header {
                                    display: flex;
                                    align-items: flex-end;
                                    justify-content: space-between;
                                    gap: 16px;
                                    border-bottom: 1px solid #e3e7ee;
                                    padding-bottom: 14px;
                                    margin-bottom: 18px;
                                }
                                .title {
                                    margin: 0;
                                    font-size: 22px;
                                    font-weight: 700;
                                    color: #0f172a;
                                }
                                .subtitle {
                                    margin: 6px 0 0;
                                    font-size: 13px;
                                    color: #64748b;
                                }
                                .total-card {
                                    background: #111827;
                                    color: #ffffff;
                                    padding: 10px 14px;
                                    border-radius: 10px;
                                    font-weight: 700;
                                    font-size: 14px;
                                    white-space: nowrap;
                                }
                                table {
                                    width: 100%;
                                    border-collapse: collapse;
                                    font-size: 13px;
                                }
                                thead th {
                                    text-align: left;
                                    font-weight: 700;
                                    color: #334155;
                                    background: #f1f5f9;
                                    padding: 10px 12px;
                                    border-bottom: 1px solid #e2e8f0;
                                }
                                tbody td {
                                    padding: 10px 12px;
                                    border-bottom: 1px solid #eef2f7;
                                }
                                tbody tr:nth-child(even) td {
                                    background: #fafbfc;
                                }
                                .hrs {
                                    text-align: right;
                                    font-weight: 700;
                                    color: #0f172a;
                                }
                                .empty {
                                    color: #64748b;
                                    text-align: center;
                                    padding: 14px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="sheet">
                                <div class="header">
                                    <div>
                                        <h1 class="title">${titleText}</h1>
                                        <div class="subtitle">Tech: ${techName}</div>
                                    </div>
                                    <div class="total-card">${totalEl.textContent}</div>
                                </div>
                                <table>
                                    <thead>
                                        <tr>
                                            <th style="width:110px;">Line</th>
                                            <th>Description</th>
                                            <th class="hrs" style="width:110px;">Hours</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${rowsHtml || '<tr><td colspan="3" class="empty">No assigned lines.</td></tr>'}
                                    </tbody>
                                </table>
                            </div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.print();
            }

            let currentTechDetailData = null;

            function openTechDetailModal(roNumber, techId, techName, role) {
                const modal = document.getElementById('techDetailModal');
                const title = document.getElementById('techDetailTitle');
                const body = document.getElementById('techDetailBody');
                
                if (!modal || !title || !body) return;
                
                title.textContent = `${techName} - RO# ${roNumber}`;
                body.innerHTML = '<div style="color:#777;">Loading...</div>';
                modal.style.display = 'block';
                
                currentTechDetailData = { roNumber, techId, techName, role };
                
                fetch(`/api/ro-tech-detail?ro=${encodeURIComponent(roNumber)}&tech_id=${techId}&role=${role}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        
                        const lines = res.repair_lines || [];
                        let totalHrs = 0;
                        
                        if (body) {
                            if (lines.length === 0) {
                                body.innerHTML = '<div style="color:#999;">No repair lines assigned.</div>';
                            } else {
                                let html = '<table style="width:100%; border-collapse:collapse;">';
                                html += '<thead><tr style="background:#f5f5f5; text-align:left;">';
                                html += '<th style="padding:8px; font-weight:bold; color:#555;">Line</th>';
                                html += '<th style="padding:8px; font-weight:bold; color:#555;">Description</th>';
                                html += '<th style="padding:8px; font-weight:bold; color:#555; text-align:right;">Hours</th>';
                                html += '</tr></thead><tbody>';
                                
                                lines.forEach(line => {
                                    const lineNum = line.line || '—';
                                    const desc = line.description || '';
                                    const hours = line.value ? parseFloat(line.value).toFixed(1) : '0.0';
                                    totalHrs += parseFloat(hours);
                                    
                                    html += `
                                        <tr style="border-bottom:1px solid #eee;">
                                            <td style="padding:10px;">${lineNum}</td>
                                            <td style="padding:10px;">${desc}</td>
                                            <td style="padding:10px; text-align:right; font-weight:bold;">${hours}</td>
                                        </tr>
                                    `;
                                });
                                
                                html += '</tbody></table>';
                                body.innerHTML = html;
                            }
                            
                            const totalEl = document.getElementById('techDetailTotal');
                            if (totalEl) {
                                totalEl.textContent = `Total: ${totalHrs.toFixed(1)} hrs`;
                            }
                        }
                    })
                    .catch(err => {
                        console.error('Error loading tech detail:', err);
                        if (body) {
                            body.innerHTML = '<div style="color:red;">Error loading repair lines.</div>';
                        }
                    });
            }

            function closeTechDetailModal() {
                const modal = document.getElementById('techDetailModal');
                if (modal) modal.style.display = 'none';
            }

            function printTechDetail() {
                if (!currentTechDetailData) return;
                
                const body = document.getElementById('techDetailBody');
                const total = document.getElementById('techDetailTotal');
                
                if (!body || !total) return;
                
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <html>
                        <head>
                            <title>Tech Detail - ${currentTechDetailData.techName}</title>
                            <style>
                                body { font-family: Arial, sans-serif; padding: 20px; }
                                h1 { color: #d32f2f; }
                                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                                th { background: #f5f5f5; font-weight: bold; }
                                .total { margin-top: 20px; font-size: 18px; font-weight: bold; }
                            </style>
                        </head>
                        <body>
                            <h1>${currentTechDetailData.techName} - RO# ${currentTechDetailData.roNumber}</h1>
                            ${body.innerHTML}
                            <div class="total">${total.textContent}</div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.print();
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
                        if (!container) return;
                        const lines = currentRepairMode === 'paint' ? repairsRes.paint : repairsRes.labor;
                        const assignment = repairsRes.assignments ? repairsRes.assignments[currentRepairMode] : null;
                        const techs = techsRes.techs || [];
                        currentRepairLines = Array.isArray(lines) ? lines : [];
                        renderRepairLines(currentRepairLines, currentRepairMode, assignment, techs);
                    })
                    .catch(err => {
                        console.error('Error loading repair lines:', err);
                        if (container) {
                            container.innerHTML = '<div style="color:red;">Error loading repair lines.</div>';
                        }
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

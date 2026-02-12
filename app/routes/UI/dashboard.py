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

        <div id="techAssignModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:980px; max-height:85vh; overflow-y:auto;">
                <span class="close" onclick="closeTechAssignModal()">&times;</span>
                <h2 id="techAssignTitle" style="margin-bottom:18px;">Assign Repair Lines</h2>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
                    <div>
                        <label for="techAssignTech" style="font-weight:bold; font-size:12px; color:#666;">TECH</label>
                        <select id="techAssignTech" style="width:100%; padding:8px; margin-top:6px;"></select>
                    </div>
                    <div>
                        <label for="techAssignType" style="font-weight:bold; font-size:12px; color:#666;">TYPE</label>
                        <select id="techAssignType" style="width:100%; padding:8px; margin-top:6px;">
                            <option value="body">body</option>
                            <option value="paint">paint</option>
                            <option value="mech">mech</option>
                            <option value="frame">frame</option>
                        </select>
                    </div>
                </div>
                <div style="border:1px solid #ddd; border-radius:6px; overflow:hidden; background:#fff;">
                    <div style="padding:10px 12px; border-bottom:1px solid #eee; background:#fafafa; display:flex; align-items:center; gap:8px;">
                        <input id="techAssignMaster" type="checkbox" onchange="toggleAllAssignmentLines()" style="width:16px; height:16px; cursor:pointer;" />
                        <label for="techAssignMaster" style="font-weight:bold; cursor:pointer;">Select / Deselect All</label>
                    </div>
                    <div id="techAssignLines" style="max-height:380px; overflow-y:auto;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                    <div id="techAssignTotal" style="font-weight:bold;">Selected Total: 0.0 hrs</div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="printTechAssignModal()" style="padding:9px 18px; background:#333; color:#fff; border:none; border-radius:4px; cursor:pointer;">Print</button>
                        <button onclick="saveTechAssignModal()" style="padding:9px 18px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save</button>
                    </div>
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
                                <button type="button" onclick="toggleRoNotesFromLink(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${ro.ro}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.vehicle || 'N/A'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${customerDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <span id="phone-display-${rowId}" style="display:inline-flex; align-items:center; gap:6px;">
                                    <button type="button" onclick="startPhoneEdit(event, '${rowId}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
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
                                <button type="button" onclick="toggleTechAssignment(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${ro.hours.toFixed(1)}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333; text-align:right; font-weight:bold;">$${ro.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                        <tr id="tech-assignment-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="8" style="padding:16px; border-bottom:1px solid #eee;">
                                <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:16px;">
                                    <div style="font-weight:bold; color:#333; margin-bottom:10px;">Tech List</div>
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
            }

            function toggleTechAssignment(event, roNumber) {
                if (event) event.stopPropagation();
                const assignmentRow = document.getElementById(`tech-assignment-row-${safeId(roNumber)}`);
                if (!assignmentRow) return;
                const isHidden = assignmentRow.style.display === 'none' || assignmentRow.style.display === '';
                assignmentRow.style.display = isHidden ? 'table-row' : 'none';
                if (isHidden) {
                    loadTechAssignments(roNumber);
                }
            }

            let currentTechAssignContext = null;
            let currentTechAssignLines = [];

            function normalizeTypeLabel(typeValue) {
                const value = String(typeValue || '').toLowerCase();
                if (value === 'labor') return 'body';
                if (value === 'body' || value === 'paint' || value === 'mech' || value === 'frame') return value;
                return value || '?';
            }

            function closeTechAssignModal() {
                const modal = document.getElementById('techAssignModal');
                if (modal) modal.style.display = 'none';
                currentTechAssignContext = null;
                currentTechAssignLines = [];
            }

            function loadTechAssignments(roNumber) {
                const listEl = document.getElementById(`tech-assignment-list-${safeId(roNumber)}`);
                if (!listEl) {
                    console.error('Could not find element:', `tech-assignment-list-${safeId(roNumber)}`);
                    return;
                }

                fetch(`/api/ro-tech-lines?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(data => {
                        const displayList = data.tech_lines || [];
                        let html = '';

                        if (displayList.length === 0) {
                            html = '<div style="color:#999; padding:12px;">No repair data found.</div>';
                        } else {
                            html = '<table style="width:100%; border-collapse:collapse; margin-top:8px;">';
                            html += '<thead><tr style="background:#d9d9d9; border-bottom:2px solid #999;">';
                            html += '<th style="padding:8px 12px; text-align:left; font-weight:bold; color:#333;">TECH</th>';
                            html += '<th style="padding:8px 12px; text-align:left; font-weight:bold; color:#333;">TYPE</th>';
                            html += '<th style="padding:8px 12px; text-align:right; font-weight:bold; color:#333;">HRS</th>';
                            html += '</tr></thead><tbody>';

                            displayList.forEach((item) => {
                                const techLabel = item.tech || 'unassigned';
                                const typeLabel = normalizeTypeLabel(item.type || '?');
                                const textColor = techLabel.toUpperCase() === 'PENDING' ? '#d32f2f' : '#333';
                                html += `<tr style="background:#fff; border-bottom:1px solid #ddd;">`;
                                html += `<td style="padding:8px 12px; color:${textColor}; font-weight:bold;">`;
                                html += `<button type="button" onclick='openTechAssignModal("${roNumber}", ${JSON.stringify(item).replace(/'/g, "&#39;")})' style="background:none; border:none; color:${textColor}; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">${techLabel}</button>`;
                                html += `</td>`;
                                html += `<td style="padding:8px 12px; color:#333;">${typeLabel}</td>`;
                                html += `<td style="padding:8px 12px; text-align:right; color:#333; font-weight:bold;">${Number(item.hours || 0).toFixed(1)}</td>`;
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

            function updateTechAssignMasterState() {
                const master = document.getElementById('techAssignMaster');
                const checks = document.querySelectorAll('.tech-assign-line-checkbox');
                if (!master) return;
                if (checks.length === 0) {
                    master.checked = false;
                    master.indeterminate = false;
                    return;
                }
                const checkedCount = Array.from(checks).filter(chk => chk.checked).length;
                master.checked = checkedCount === checks.length;
                master.indeterminate = checkedCount > 0 && checkedCount < checks.length;
            }

            function updateTechAssignTotal() {
                const totalEl = document.getElementById('techAssignTotal');
                if (!totalEl) return;
                const checks = document.querySelectorAll('.tech-assign-line-checkbox:checked');
                let total = 0;
                checks.forEach((checkbox) => {
                    const hours = parseFloat(checkbox.getAttribute('data-hours') || '0');
                    if (Number.isFinite(hours)) {
                        total += hours;
                    }
                });
                totalEl.textContent = `Selected Total: ${total.toFixed(1)} hrs`;
                updateTechAssignMasterState();
            }

            function toggleAllAssignmentLines() {
                const master = document.getElementById('techAssignMaster');
                const checks = document.querySelectorAll('.tech-assign-line-checkbox');
                checks.forEach(chk => {
                    chk.checked = !!master?.checked;
                });
                updateTechAssignTotal();
            }

            function populateTechAssignTechs(techs, currentTechName) {
                const select = document.getElementById('techAssignTech');
                if (!select) return;
                const options = ['<option value="">Select tech...</option>'];
                (techs || []).forEach((tech) => {
                    const label = tech.name || `Tech #${tech.id}`;
                    options.push(`<option value="${tech.id}" data-name="${label}">${label}</option>`);
                });
                select.innerHTML = options.join('');

                if (currentTechName) {
                    const match = Array.from(select.options).find(opt => (opt.dataset?.name || '') === currentTechName);
                    if (match) {
                        select.value = match.value;
                    }
                }
            }

            function renderTechAssignLines(lines) {
                const container = document.getElementById('techAssignLines');
                if (!container) return;

                if (!lines || lines.length === 0) {
                    container.innerHTML = '<div style="padding:12px; color:#777;">No repair lines found.</div>';
                    updateTechAssignTotal();
                    return;
                }

                container.innerHTML = lines.map((line, index) => {
                    const lineNumber = line.line_number || line.line_key || String(index + 1);
                    const description = line.description || '';
                    const hours = Number(line.hours || 0).toFixed(1);
                    const lineType = normalizeTypeLabel(line.repair_type);
                    return `
                        <div style="display:flex; align-items:flex-start; gap:10px; padding:10px 12px; border-bottom:1px solid #eee;">
                            <input type="checkbox" class="tech-assign-line-checkbox" checked data-repair-type="${lineType}" data-line-key="${line.line_key}" data-hours="${hours}" onchange="updateTechAssignTotal()" style="margin-top:2px; width:16px; height:16px; cursor:pointer;" />
                            <div style="flex:1;">
                                <div style="font-weight:bold; color:#333;">${lineType.toUpperCase()} · Line ${lineNumber}</div>
                                <div style="font-size:12px; color:#666;">${description}</div>
                            </div>
                            <div style="min-width:80px; text-align:right; font-weight:bold;">${hours} hrs</div>
                        </div>
                    `;
                }).join('');

                updateTechAssignTotal();
            }

            function openTechAssignModal(roNumber, lineItem) {
                const modal = document.getElementById('techAssignModal');
                const title = document.getElementById('techAssignTitle');
                const linesContainer = document.getElementById('techAssignLines');
                const typeSelect = document.getElementById('techAssignType');
                if (!modal || !title || !linesContainer || !typeSelect) return;

                const mode = (lineItem?.mode || '').toLowerCase();
                const sourceType = normalizeTypeLabel(lineItem?.repair_type || lineItem?.type || 'body');
                const sourceTech = lineItem?.tech_name || lineItem?.tech || '';

                currentTechAssignContext = {
                    ro: roNumber,
                    source: {
                        mode: mode,
                        repair_type: sourceType,
                        tech_name: sourceTech
                    }
                };

                title.textContent = `Assign Repair Lines - RO# ${roNumber}`;
                linesContainer.innerHTML = '<div style="padding:12px; color:#777;">Loading...</div>';
                modal.style.display = 'block';

                const query = new URLSearchParams({
                    ro: roNumber,
                    mode: mode,
                    repair_type: sourceType,
                    tech_name: sourceTech
                });

                fetch(`/api/ro-assignment-lines?${query.toString()}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }

                        currentTechAssignLines = res.lines || [];
                        populateTechAssignTechs(res.techs || [], mode === 'tech' ? sourceTech : '');
                        typeSelect.value = mode === 'pending' ? 'body' : sourceType;
                        renderTechAssignLines(currentTechAssignLines);
                    })
                    .catch(err => {
                        console.error('Error loading assignment lines:', err);
                        linesContainer.innerHTML = '<div style="padding:12px; color:red;">Error loading repair lines.</div>';
                    });
            }

            function saveTechAssignModal() {
                if (!currentTechAssignContext?.ro || !currentTechAssignContext?.source) {
                    return;
                }

                const techSelect = document.getElementById('techAssignTech');
                const typeSelect = document.getElementById('techAssignType');
                if (!techSelect || !typeSelect || !techSelect.value) {
                    alert('Please select a tech.');
                    return;
                }

                const selected = Array.from(document.querySelectorAll('.tech-assign-line-checkbox:checked')).map((checkbox) => ({
                    repair_type: checkbox.getAttribute('data-repair-type'),
                    line_key: checkbox.getAttribute('data-line-key')
                }));

                if (selected.length === 0) {
                    alert('Select at least one repair line.');
                    return;
                }

                const targetTechName = techSelect.options[techSelect.selectedIndex]?.dataset?.name || '';
                const targetTechId = parseInt(techSelect.value, 10);

                fetch('/api/ro-assignment-save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        ro: currentTechAssignContext.ro,
                        source: currentTechAssignContext.source,
                        target: {
                            tech_id: Number.isFinite(targetTechId) ? targetTechId : null,
                            tech_name: targetTechName,
                            repair_type: typeSelect.value
                        },
                        selected_lines: selected
                    })
                })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        const roNumber = currentTechAssignContext.ro;
                        closeTechAssignModal();
                        loadTechAssignments(roNumber);
                        loadDashboardData();
                    })
                    .catch(err => {
                        console.error('Error saving assignment:', err);
                        alert('Error saving assignments.');
                    });
            }

            function printTechAssignModal() {
                if (!currentTechAssignContext?.ro) {
                    return;
                }

                const techSelect = document.getElementById('techAssignTech');
                const typeSelect = document.getElementById('techAssignType');
                const selectedRows = Array.from(document.querySelectorAll('.tech-assign-line-checkbox:checked'));
                if (!selectedRows.length) {
                    alert('Select at least one repair line to print.');
                    return;
                }
                const techName = techSelect?.options?.[techSelect.selectedIndex]?.dataset?.name || 'Unassigned';
                const typeName = typeSelect?.value || '?';
                const roNumber = currentTechAssignContext.ro;

                let total = 0;
                const linesHtml = selectedRows.map((checkbox) => {
                    const row = checkbox.closest('div');
                    const meta = row?.querySelector('div > div')?.textContent || '';
                    const desc = row?.querySelector('div > div:nth-child(2)')?.textContent || '';
                    const hours = parseFloat(checkbox.getAttribute('data-hours') || '0');
                    total += Number.isFinite(hours) ? hours : 0;
                    return `
                        <tr>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${meta}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${desc}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right; font-weight:bold;">${hours.toFixed(1)}</td>
                        </tr>
                    `;
                }).join('');

                const printWindow = window.open('', '_blank', 'width=980,height=760');
                if (!printWindow) return;

                printWindow.document.write(`
                    <html>
                        <head>
                            <title>Tech Assignment Print</title>
                            <style>
                                body { font-family: Arial, sans-serif; padding: 28px; color:#222; }
                                .header { display:flex; justify-content:space-between; margin-bottom:20px; }
                                .title { font-size:24px; font-weight:bold; color:#d32f2f; }
                                .meta { font-size:14px; line-height:1.7; }
                                table { width:100%; border-collapse:collapse; margin-top:16px; }
                                thead th { text-align:left; background:#f5f5f5; padding:10px; border-bottom:2px solid #ddd; }
                                .total { margin-top:18px; font-size:18px; font-weight:bold; text-align:right; }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <div class="title">Assigned Repair Lines</div>
                                <div class="meta">RO: ${roNumber}<br/>Tech: ${techName}<br/>Type: ${typeName}</div>
                            </div>
                            <table>
                                <thead>
                                    <tr><th>Repair Line</th><th>Description</th><th style="text-align:right;">HRS</th></tr>
                                </thead>
                                <tbody>${linesHtml}</tbody>
                            </table>
                            <div class="total">Total Hours: ${total.toFixed(1)}</div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                printWindow.print();
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

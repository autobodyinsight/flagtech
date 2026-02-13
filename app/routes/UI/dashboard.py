"""Dashboard screen content for the FlagTech UI."""


def get_dashboard_screen_html():
    """Return the HTML content for the Dashboard screen."""
    return r"""
        <div id="dashboard" class="screen active" style="padding:20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
                <h1 style="text-align:center; margin:0; flex:1;">DASHBOARD</h1>
                <button onclick="flashAllData()" style="padding:10px 16px; background:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">FLASH</button>
            </div>
            
            <div style="--dash-chart-h: 520px;">
                <style>
                    .dash-center-card {
                        background:#fff;
                        padding:20px;
                        border-radius:8px;
                        border:2px solid #00bcd4;
                        box-shadow:0 2px 4px rgba(0,0,0,0.08);
                        height: var(--dash-chart-h);
                        display:flex;
                        flex-direction:column;
                    }
                    .dash-matrix {
                        display:grid;
                        gap:16px;
                        grid-template-columns: 1fr minmax(320px, 1.2fr) 1fr;
                        grid-template-rows: 170px 1fr 190px;
                        align-items:stretch;
                        height:100%;
                    }
                    .dash-cell {
                        background:#f9f9f9;
                        border:1px solid #ddd;
                        border-radius:8px;
                        padding:14px;
                        display:flex;
                        flex-direction:column;
                    }
                    .dash-card-fill { flex:1; }
                    .dash-avg-row {
                        display:flex;
                        gap:12px;
                        height:100%;
                    }
                    .dash-mini-card {
                        flex:1;
                        border-radius:8px;
                        padding:12px;
                        border:2px solid transparent;
                        display:flex;
                        flex-direction:column;
                        justify-content:center;
                        background:#fff;
                        box-shadow:0 2px 4px rgba(0,0,0,0.08);
                    }
                    .dash-pie-wrap {
                        flex:1;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                    }
                    .dash-pie-inner {
                        width:80%;
                        height:80%;
                        min-width:220px;
                        min-height:220px;
                    }
                </style>

                <div class="dash-center-card">
                    <h4 style="margin:0 0 12px 0; color:#666; font-size:14px; text-align:center;">Total Hrs per Tech</h4>
                    <div class="dash-matrix">
                        <!-- Top Left: Current Sales -->
                        <div class="dash-cell">
                            <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Current Sales</h3>
                            <div style="position:relative; background:#e0e0e0; border-radius:4px; overflow:hidden;" class="dash-card-fill">
                                <div id="totalSalesBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #4caf50, #81c784); transition:height 0.5s ease;"></div>
                            </div>
                            <div id="totalSalesValue" style="text-align:center; font-size:20px; font-weight:bold; color:#4caf50; margin-top:10px;">$0</div>
                        </div>

                        <!-- Top Center: Average Hrs + Average RO -->
                        <div class="dash-cell" style="background:#fff;">
                            <div class="dash-avg-row">
                                <div class="dash-mini-card" style="border-color:#9c27b0;">
                                    <h4 style="margin:0 0 8px 0; color:#666; font-size:13px;">Average Hrs</h4>
                                    <div id="averageHrs" style="font-size:24px; font-weight:bold; color:#9c27b0;">0.0</div>
                                </div>
                                <div class="dash-mini-card" style="border-color:#ff5722;">
                                    <h4 style="margin:0 0 8px 0; color:#666; font-size:13px;">Average RO</h4>
                                    <div id="averageRO" style="font-size:24px; font-weight:bold; color:#ff5722;">$0</div>
                                </div>
                            </div>
                        </div>

                        <!-- Top Right: Total ROs -->
                        <div class="dash-cell">
                            <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Total RO's</h3>
                            <div style="position:relative; background:#e0e0e0; border-radius:4px; overflow:hidden;" class="dash-card-fill">
                                <div id="totalRosBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #42a5f5, #90caf9); transition:height 0.5s ease;"></div>
                            </div>
                            <div id="totalRosValue" style="text-align:center; font-size:20px; font-weight:bold; color:#42a5f5; margin-top:10px;">0</div>
                        </div>

                        <!-- Middle Left: Spacer -->
                        <div></div>

                        <!-- Center: Pie Chart -->
                        <div class="dash-cell" style="background:#fff; border:1px solid #eee;">
                            <div class="dash-pie-wrap">
                                <div class="dash-pie-inner">
                                    <canvas id="hoursPerTechChart" style="height:100%; width:100%;"></canvas>
                                </div>
                            </div>
                        </div>

                        <!-- Middle Right: Spacer -->
                        <div></div>

                        <!-- Bottom Left: Total ROs per Tech -->
                        <div class="dash-cell" style="border:2px solid #795548;">
                            <h4 style="margin:0 0 12px 0; color:#666; font-size:13px;">Total ROs per Tech</h4>
                            <div id="rosPerTechList" style="height:100%; overflow-y:auto; font-size:14px;">
                                <div style="color:#999; text-align:center;">Loading...</div>
                            </div>
                        </div>

                        <!-- Bottom Center: Spacer -->
                        <div></div>

                        <!-- Bottom Right: Tech List with Total Hrs -->
                        <div class="dash-cell" style="border:2px solid #00bcd4;">
                            <h4 style="margin:0 0 12px 0; color:#666; font-size:13px;">Tech List (Total Hrs)</h4>
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
                                <th data-sort-key="ro" onclick="sortRoListByHeader('ro')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">RO# <span data-sort-indicator="ro" style="font-size:12px;"></span></th>
                                <th data-sort-key="vehicle" onclick="sortRoListByHeader('vehicle')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">Vehicle <span data-sort-indicator="vehicle" style="font-size:12px;"></span></th>
                                <th data-sort-key="customer" onclick="sortRoListByHeader('customer')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">Customer <span data-sort-indicator="customer" style="font-size:12px;"></span></th>
                                <th data-sort-key="phone" onclick="sortRoListByHeader('phone')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">Phone <span data-sort-indicator="phone" style="font-size:12px;"></span></th>
                                <th data-sort-key="insurance" onclick="sortRoListByHeader('insurance')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">Insurance <span data-sort-indicator="insurance" style="font-size:12px;"></span></th>
                                <th data-sort-key="claim_number" onclick="sortRoListByHeader('claim_number')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">Claim # <span data-sort-indicator="claim_number" style="font-size:12px;"></span></th>
                                <th data-sort-key="in_date" onclick="sortRoListByHeader('in_date')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">In <span data-sort-indicator="in_date" style="font-size:12px;"></span></th>
                                <th data-sort-key="ecd_date" onclick="sortRoListByHeader('ecd_date')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; cursor:pointer; user-select:none;">ECD <span data-sort-indicator="ecd_date" style="font-size:12px;"></span></th>
                                <th data-sort-key="hours" onclick="sortRoListByHeader('hours')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right; cursor:pointer; user-select:none;">HRS <span data-sort-indicator="hours" style="font-size:12px;"></span></th>
                                <th data-sort-key="total" onclick="sortRoListByHeader('total')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right; cursor:pointer; user-select:none;">Total <span data-sort-indicator="total" style="font-size:12px;"></span></th>
                            </tr>
                        </thead>
                        <tbody id="roListBody">
                            <tr>
                                <td colspan="10" style="padding:20px; text-align:center; color:#999;">Loading...</td>
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

        <div id="roDatePickerPopup" style="display:none; position:fixed; z-index:2001; background:#fff; border:1px solid #ccc; border-radius:6px; padding:8px; box-shadow:0 3px 8px rgba(0,0,0,0.18);">
            <input id="roDatePickerInput" type="date" style="padding:4px 6px;" />
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
            let roSortState = {
                key: null,
                direction: 'asc'
            };
            
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

            function formatShortDate(value) {
                if (!value) return '-';
                const source = String(value).trim();
                if (!source) return '-';
                const datePart = source.includes('T') ? source.split('T')[0] : source;
                const parts = datePart.split('-');
                if (parts.length !== 3) return '-';
                const [year, month, day] = parts;
                if (!year || !month || !day) return '-';
                return `${month.padStart(2, '0')}/${day.padStart(2, '0')}/${year.slice(-2)}`;
            }

            function addWeekdaysIso(startIso, weekdayDays) {
                if (!startIso) return '';
                const [yearStr, monthStr, dayStr] = startIso.split('-');
                let current = new Date(Number(yearStr), Number(monthStr) - 1, Number(dayStr));
                if (Number.isNaN(current.getTime())) return '';
                let added = 0;
                while (added < weekdayDays) {
                    current.setDate(current.getDate() + 1);
                    const day = current.getDay();
                    if (day !== 0 && day !== 6) added += 1;
                }
                const y = current.getFullYear();
                const m = String(current.getMonth() + 1).padStart(2, '0');
                const d = String(current.getDate()).padStart(2, '0');
                return `${y}-${m}-${d}`;
            }

            function computeEcdIso(inIso, hours) {
                if (!inIso) return '';
                const weekdayDays = Math.max(0, Math.ceil((Number(hours || 0) / 4) + 3));
                return addWeekdaysIso(inIso, weekdayDays);
            }

            function closeRoDatePicker() {
                const popup = document.getElementById('roDatePickerPopup');
                const input = document.getElementById('roDatePickerInput');
                if (!popup || !input) return;
                popup.style.display = 'none';
                input.onchange = null;
                delete popup.dataset.rowId;
                delete popup.dataset.ro;
                delete popup.dataset.field;
                delete popup.dataset.hours;
            }

            function updateRoDateCell(rowId, field, isoValue) {
                const btn = document.getElementById(`ro-date-${field}-${rowId}`);
                if (!btn) return;
                btn.dataset.iso = isoValue || '';
                btn.textContent = formatShortDate(isoValue);
            }

            async function patchRoDate(roNumber, field, isoValue) {
                const response = await fetch('/api/ro-dates', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ ro: roNumber, field, value: isoValue })
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    throw new Error(result.error || 'Failed to update date');
                }
                return result;
            }

            async function openRoDatePicker(event, rowId, roNumber, field, hours) {
                if (event) event.stopPropagation();
                const btn = document.getElementById(`ro-date-${field}-${rowId}`);
                const popup = document.getElementById('roDatePickerPopup');
                const input = document.getElementById('roDatePickerInput');
                if (!btn || !popup || !input) return;

                popup.dataset.rowId = rowId;
                popup.dataset.ro = roNumber;
                popup.dataset.field = field;
                popup.dataset.hours = String(hours || 0);

                const currentIso = btn.dataset.iso || '';
                input.value = currentIso;

                const rect = btn.getBoundingClientRect();
                const popupWidth = 210;
                const left = Math.min(window.innerWidth - popupWidth - 8, Math.max(8, rect.right + 8));
                const top = Math.min(window.innerHeight - 60, Math.max(8, rect.top));
                popup.style.left = `${left}px`;
                popup.style.top = `${top}px`;
                popup.style.display = 'block';

                input.onchange = async () => {
                    const selectedIso = input.value;
                    if (!selectedIso) {
                        closeRoDatePicker();
                        return;
                    }

                    const oldIso = btn.dataset.iso || '';
                    if (oldIso === selectedIso) {
                        closeRoDatePicker();
                        return;
                    }

                    try {
                        await patchRoDate(roNumber, field, selectedIso);
                        updateRoDateCell(rowId, field, selectedIso);

                        if (field === 'in_date') {
                            const autoEcdIso = computeEcdIso(selectedIso, Number(hours || 0));
                            if (autoEcdIso) {
                                await patchRoDate(roNumber, 'ecd_date', autoEcdIso);
                                updateRoDateCell(rowId, 'ecd_date', autoEcdIso);
                            }
                        }
                    } catch (error) {
                        console.error('Error updating RO date:', error);
                        alert('Error updating date.');
                    } finally {
                        closeRoDatePicker();
                    }
                };

                input.focus();
                if (typeof input.showPicker === 'function') {
                    input.showPicker();
                }
            }

            document.addEventListener('click', function(event) {
                const popup = document.getElementById('roDatePickerPopup');
                if (!popup || popup.style.display === 'none') return;
                if (popup.contains(event.target)) return;
                if (event.target && event.target.closest && event.target.closest('.ro-date-btn')) return;
                closeRoDatePicker();
            });

            function sortRoListByHeader(sortKey) {
                if (roSortState.key === sortKey) {
                    roSortState.direction = roSortState.direction === 'asc' ? 'desc' : 'asc';
                } else {
                    roSortState.key = sortKey;
                    roSortState.direction = 'asc';
                }

                if (dashboardData && Array.isArray(dashboardData.roList)) {
                    updateRoListTable(dashboardData.roList);
                }
            }

            function normalizeSortValue(ro, sortKey) {
                if (!ro) return '';

                if (sortKey === 'hours' || sortKey === 'total') {
                    return Number(ro[sortKey] || 0);
                }

                if (sortKey === 'in_date' || sortKey === 'ecd_date') {
                    const parsedDate = Date.parse(ro[sortKey] || '');
                    return Number.isNaN(parsedDate) ? 0 : parsedDate;
                }

                return String(ro[sortKey] || '').toLowerCase();
            }

            function updateRoSortIndicators() {
                const indicators = document.querySelectorAll('[data-sort-indicator]');
                indicators.forEach((element) => {
                    const key = element.getAttribute('data-sort-indicator');
                    if (key && roSortState.key === key) {
                        element.textContent = roSortState.direction === 'asc' ? '▲' : '▼';
                    } else {
                        element.textContent = '';
                    }
                });
            }

            // Update RO list table
            function updateRoListTable(roList) {
                const tbody = document.getElementById('roListBody');
                const sourceList = Array.isArray(roList) ? roList : [];
                const sortedList = [...sourceList];

                if (roSortState.key) {
                    sortedList.sort((a, b) => {
                        const valueA = normalizeSortValue(a, roSortState.key);
                        const valueB = normalizeSortValue(b, roSortState.key);

                        if (typeof valueA === 'number' && typeof valueB === 'number') {
                            if (valueA === valueB) return 0;
                            return valueA < valueB ? -1 : 1;
                        }

                        return String(valueA).localeCompare(String(valueB), undefined, { numeric: true, sensitivity: 'base' });
                    });

                    if (roSortState.direction === 'desc') {
                        sortedList.reverse();
                    }
                }

                updateRoSortIndicators();
                
                if (sortedList.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="10" style="padding:20px; text-align:center; color:#999;">No repair orders found</td></tr>';
                    return;
                }
                
                let html = '';
                sortedList.forEach((ro, index) => {
                    const rowBg = index % 2 === 0 ? '#fff' : '#f9f9f9';
                    const rowId = safeId(ro.ro);
                    const customerDisplay = ro.customer || '-';
                    const phoneDisplay = cleanPhoneNumber(ro.phone);
                    const insuranceDisplay = (ro.insurance || '-').split(/\s+/).slice(0, 2).join(' ');
                    const claimDisplay = ro.claim_number || '-';
                    const phoneOriginal = cleanPhoneNumber(ro.phone_original) || phoneDisplay || '-';
                    const inIso = ro.in_date || '';
                    const ecdIso = ro.ecd_date || computeEcdIso(inIso, Number(ro.hours || 0));
                    const inDisplay = formatShortDate(inIso);
                    const ecdDisplay = formatShortDate(ecdIso);
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
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button id="ro-date-in_date-${rowId}" class="ro-date-btn" data-iso="${inIso}" type="button" onclick="openRoDatePicker(event, '${rowId}', '${ro.ro}', 'in_date', ${Number(ro.hours || 0)})" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${inDisplay}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button id="ro-date-ecd_date-${rowId}" class="ro-date-btn" data-iso="${ecdIso}" type="button" onclick="openRoDatePicker(event, '${rowId}', '${ro.ro}', 'ecd_date', ${Number(ro.hours || 0)})" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${ecdDisplay}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right;">
                                <button type="button" onclick="toggleTechAssignment(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${ro.hours.toFixed(1)}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333; text-align:right; font-weight:bold;">$${ro.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                        <tr id="tech-assignment-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:16px; border-bottom:1px solid #eee;">
                                <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:16px;">
                                    <div style="font-weight:bold; color:#333; margin-bottom:10px;">Tech List</div>
                                    <div id="tech-assignment-list-${rowId}" style="margin-top:12px;">
                                        <div style="color:#777;">Loading...</div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr id="notes-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:12px 16px; border-bottom:1px solid #eee;">
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

                const parseLineSortValue = (value, fallback) => {
                    const text = value === null || value === undefined ? String(fallback) : String(value);
                    const match = text.match(/\d+/);
                    return match ? parseInt(match[0], 10) : Number.MAX_SAFE_INTEGER;
                };

                const sortedLines = [...lines].sort((a, b) => {
                    const aLine = parseLineSortValue(a.line_number || a.line_key, 0);
                    const bLine = parseLineSortValue(b.line_number || b.line_key, 0);
                    if (aLine !== bLine) return aLine - bLine;
                    const aDesc = String(a.description || '').toLowerCase();
                    const bDesc = String(b.description || '').toLowerCase();
                    return aDesc.localeCompare(bDesc);
                });

                container.innerHTML = sortedLines.map((line, index) => {
                    const lineNumber = line.line_number || line.line_key || String(index + 1);
                    const description = String(line.description || '').trim().toLowerCase();
                    const hours = Number(line.hours || 0).toFixed(1);
                    const lineType = normalizeTypeLabel(line.repair_type);
                    return `
                        <div style="display:flex; align-items:center; gap:10px; padding:10px 12px; border-bottom:1px solid #eee;">
                            <input type="checkbox" class="tech-assign-line-checkbox" checked data-repair-type="${lineType}" data-line-key="${line.line_key}" data-line-number="${lineNumber}" data-description="${description}" data-hours="${hours}" onchange="updateTechAssignTotal()" style="width:16px; height:16px; cursor:pointer;" />
                            <div style="flex:1; color:#333;">Line ${lineNumber} ${description}</div>
                            <div style="min-width:70px; text-align:right; color:#555; text-transform:lowercase;">${lineType.toLowerCase()}</div>
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
                const sortedRows = [...selectedRows].sort((a, b) => {
                    const aLine = parseInt((a.getAttribute('data-line-number') || '').match(/\d+/)?.[0] || '0', 10);
                    const bLine = parseInt((b.getAttribute('data-line-number') || '').match(/\d+/)?.[0] || '0', 10);
                    if (aLine !== bLine) return aLine - bLine;
                    const aDesc = (a.getAttribute('data-description') || '').toLowerCase();
                    const bDesc = (b.getAttribute('data-description') || '').toLowerCase();
                    return aDesc.localeCompare(bDesc);
                });

                const linesHtml = sortedRows.map((checkbox) => {
                    const lineNumber = checkbox.getAttribute('data-line-number') || '—';
                    const desc = checkbox.getAttribute('data-description') || '';
                    const type = (checkbox.getAttribute('data-repair-type') || '').toLowerCase();
                    const hours = parseFloat(checkbox.getAttribute('data-hours') || '0');
                    total += Number.isFinite(hours) ? hours : 0;
                    return `
                        <tr>
                            <td style="padding:10px; border-bottom:1px solid #eee;">Line ${lineNumber} ${desc}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-transform:lowercase;">${type}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right; font-weight:bold;">${hours.toFixed(1)} hrs</td>
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
                                    <tr><th>Repair Line</th><th>Type</th><th style="text-align:right;">HRS</th></tr>
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

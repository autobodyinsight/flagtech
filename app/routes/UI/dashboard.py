"""Dashboard screen content for the FlagTech UI."""


def get_dashboard_screen_html():
    """Return the HTML content for the Dashboard screen."""
    return r"""
        <div id="dashboard" class="screen active" style="padding:20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
                <h1 style="text-align:center; margin:0; flex:1;">DASHBOARD</h1>
                <button onclick="flashAllData()" style="padding:10px 16px; background:var(--brand-red, #d32f2f); color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">FLASH</button>
            </div>
            
            <div style="--dash-chart-h: 520px;">
                <style>
                    .dash-center-card {
                        background:#fff;
                        padding:20px;
                        border-radius:8px;
                        border:2px solid #00bcd4;
                        box-shadow:0 2px 4px rgba(0,0,0,0.08);
                        height: auto;
                        display:flex;
                        flex-direction:column;
                    }
                    .dash-matrix {
                        display:flex;
                        flex-direction:column;
                        gap:16px;
                        align-items:stretch;
                    }
                    .dash-list-wrap {
                        width:100%;
                        max-width:320px;
                        margin:0 auto;
                    }
                    .dash-cell {
                        padding:6px;
                        display:flex;
                        flex-direction:column;
                    }
                    .dash-card-fill { flex:1; }
                    .dash-avg-row {
                        display:flex;
                        gap:12px;
                        height:100%;
                    }
                    .dash-middle-row {
                        display:flex;
                        gap:16px;
                        align-items:center;
                        justify-content:center;
                        flex-wrap:wrap;
                    }
                    .dash-side-list {
                        flex:0 1 320px;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                    }
                    .dash-pie-cell {
                        flex:0 1 420px;
                        display:flex;
                        justify-content:center;
                        align-items:center;
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

                <div class="dash-center-card" style="font-size:18px;">
                    <div class="dash-matrix">
                        <div style="display:flex; gap:16px; flex-wrap:wrap; justify-content:center; align-items:stretch;">
                            <!-- Current Sales -->
                            <div class="dash-cell" style="flex:1 1 220px; max-width:320px;">
                                <h3 style="margin:0 0 10px 0; text-align:center; color:#333; font-weight:bold;">Current Sales</h3>
                                <div style="position:relative; background:#e0e0e0; border-radius:4px; overflow:hidden;" class="dash-card-fill">
                                    <div id="totalSalesBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #1E90FF, #1E90FF); transition:height 0.5s ease;"></div>
                                </div>
                                <div id="totalSalesValue" style="text-align:center; font-size:20px; font-weight:bold; color:#1E90FF; margin-top:10px;">$0</div>
                            </div>

                            <!-- Average Hrs + Average RO -->
                            <div class="dash-cell" style="flex:1 1 260px; max-width:360px;">
                                <div class="dash-avg-row">
                                    <div class="dash-mini-card" style="border-color:#FF8C00; box-shadow:none;">
                                        <h4 style="margin:0 0 8px 0; color:#666; font-size:18px; font-weight:bold;">Average Hrs</h4>
                                        <div id="averageHrs" style="font-size:24px; font-weight:bold; color:#FF8C00;">0.0</div>
                                    </div>
                                    <div class="dash-mini-card" style="border-color:#FF8C00; box-shadow:none;">
                                        <h4 style="margin:0 0 8px 0; color:#666; font-size:18px; font-weight:bold;">Average RO</h4>
                                        <div id="averageRO" style="font-size:24px; font-weight:bold; color:#FF8C00;">$0</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Total ROs -->
                            <div class="dash-cell" style="flex:1 1 220px; max-width:320px;">
                                <h3 style="margin:0 0 10px 0; text-align:center; color:#333; font-weight:bold;">Total RO's</h3>
                                <div style="position:relative; background:#e0e0e0; border-radius:4px; overflow:hidden;" class="dash-card-fill">
                                    <div id="totalRosBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #1E90FF, #1E90FF); transition:height 0.5s ease;"></div>
                                </div>
                                <div id="totalRosValue" style="text-align:center; font-size:20px; font-weight:bold; color:#1E90FF; margin-top:10px;">0</div>
                            </div>
                        </div>

                        <div class="dash-middle-row">
                            <div class="dash-side-list">
                                <div class="dash-cell" style="width:100%;">
                                    <div class="dash-list-wrap">
                                        <h4 style="margin:0 0 12px 0; color:#666; font-size:18px; text-align:center; font-weight:bold;">Total ROs per Tech</h4>
                                        <div id="rosPerTechList" style="font-size:14px;">
                                            <div style="color:#999; text-align:center;">Loading...</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="dash-pie-cell">
                                <div class="dash-cell" style="width:100%;">
                                    <div class="dash-pie-wrap">
                                        <div class="dash-pie-inner">
                                            <canvas id="hoursPerTechChart" style="height:100%; width:100%;"></canvas>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="dash-side-list">
                                <div class="dash-cell" style="width:100%;">
                                    <div class="dash-list-wrap">
                                        <h4 style="margin:0 0 12px 0; color:#666; font-size:18px; text-align:center; font-weight:bold;">Tech List (Total Hrs)</h4>
                                        <div id="hoursPerTechLegend" style="font-size:12px; color:#333;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- RO List Table -->
            <div style="margin-top:30px; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; position:relative;">
                    <h3 style="margin:0; color:#333;">Repair Orders</h3>
                    <button id="dashboardPrintTrigger" class="mini-popup-trigger" onclick="openPrintOptionsModal()" style="padding:8px 16px; background:var(--brand-red, #d32f2f); color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold; font-size:14px;">Print</button>
                    <div id="printOptionsModal" class="mini-popup-panel" style="display:none; right:0; left:auto;">
                        <h2 style="margin:0 0 14px 0; color:#333; font-size:18px;">Print RO List</h2>
                        <p style="margin:0 0 12px 0; font-weight:bold; color:#555;">Print by:</p>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <button onclick="printRoList('ro')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">RO #</button>
                            <button onclick="printRoList('insurance')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Insurance</button>
                            <button onclick="printRoList('in_date')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">In date</button>
                            <button onclick="printRoList('ecd_date')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">ECD</button>
                        </div>
                    </div>
                </div>
                <div style="overflow-x:auto;">
                    <table id="roListTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="dashboard-header-row">
                                <th class="dashboard-header-cell" data-sort-key="ro" onclick="sortRoListByHeader('ro')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">RO# <span data-sort-indicator="ro" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="vehicle" onclick="sortRoListByHeader('vehicle')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Vehicle <span data-sort-indicator="vehicle" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="customer" onclick="sortRoListByHeader('customer')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Customer <span data-sort-indicator="customer" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="insurance" onclick="sortRoListByHeader('insurance')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Insurance <span data-sort-indicator="insurance" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="phase" onclick="sortRoListByHeader('phase')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Phase <span data-sort-indicator="phase" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="in_date" onclick="sortRoListByHeader('in_date')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">In <span data-sort-indicator="in_date" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="days_since_in" onclick="sortRoListByHeader('days_since_in')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:center; cursor:pointer; user-select:none;" title="Days Since In Date">⏳ <span data-sort-indicator="days_since_in" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="ecd_date" onclick="sortRoListByHeader('ecd_date')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">ECD <span data-sort-indicator="ecd_date" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="hours" onclick="sortRoListByHeader('hours')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right; cursor:pointer; user-select:none;">HRS <span data-sort-indicator="hours" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="total" onclick="sortRoListByHeader('total')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right; cursor:pointer; user-select:none;">Total <span data-sort-indicator="total" style="font-size:12px;"></span></th>
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
            .dashboard-header-row {
                background:#3c4142;
                text-align:left;
            }
            .dashboard-header-cell {
                color:#fff;
            }
            .mini-popup-panel {
                position: absolute;
                top: 100%;
                left: 0;
                z-index: 1000;
                background: #fff;
                border: 2px solid #b22222;
                border-radius: 6px;
                padding: 12px;
                min-width: 300px;
                max-width: 500px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                margin-top: 4px;
                opacity: 0;
                transform: translateY(-6px);
                transition: opacity 0.18s ease, transform 0.18s ease;
                pointer-events: none;
            }
            .mini-popup-panel.open {
                opacity: 1;
                transform: translateY(0);
                pointer-events: auto;
            }
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
                    '#00BFFF',
                    '#FF8C00',
                    '#32CD32',
                    '#FFD700',
                    '#40E0D0',
                    '#8A2BE2',
                    '#708090'
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
                            backgroundColor: labels.map((_, idx) => colors[idx % colors.length]),
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

            const openRoSlideDownState = new Map();

            function normalizeRoKey(roNumber) {
                return String(roNumber || '');
            }

            function rememberRoSlideDownOpen(roNumber, type) {
                openRoSlideDownState.set(normalizeRoKey(roNumber), type);
            }

            function forgetRoSlideDownOpen(roNumber, type) {
                const roKey = normalizeRoKey(roNumber);
                if (openRoSlideDownState.get(roKey) === type) {
                    openRoSlideDownState.delete(roKey);
                }
            }

            function closeOtherRoSlideDownsForSameRo(roNumber, keepType) {
                const roKey = normalizeRoKey(roNumber);
                const openType = openRoSlideDownState.get(roKey);
                if (!openType || openType === keepType) return;
                const roId = safeId(roNumber);
                const otherRowEl = document.getElementById(`${openType}-row-${roId}`);
                closeRoSlideDownRow(otherRowEl);
                openRoSlideDownState.delete(roKey);
            }

            function loadRoSlideDownContent(roNumber, type) {
                if (type === 'notes') {
                    loadRoNotes(roNumber);
                } else if (type === 'tech-assignment') {
                    loadTechAssignments(roNumber);
                } else if (type === 'activity') {
                    loadRoActivityLog(roNumber);
                }
            }

            function restoreOpenRoSlideDowns() {
                const openEntries = Array.from(openRoSlideDownState.entries());
                openEntries.forEach(([roNumber, type]) => {
                    const roId = safeId(roNumber);
                    const rowEl = document.getElementById(`${type}-row-${roId}`);
                    if (!rowEl) {
                        forgetRoSlideDownOpen(roNumber, type);
                        return;
                    }
                    openRoSlideDownRow(rowEl);
                    loadRoSlideDownContent(roNumber, type);
                });
            }

            function refreshRoSlideDownHeight(roNumber, type) {
                const rowEl = document.getElementById(`${type}-row-${safeId(roNumber)}`);
                if (!rowEl || rowEl.style.display === 'none' || rowEl.style.display === '') return;
                const panel = rowEl.querySelector('.ro-slide-panel');
                if (!panel) return;
                panel.style.overflow = 'visible';
                panel.style.maxHeight = `${panel.scrollHeight}px`;
                panel.style.opacity = '1';
                setTimeout(() => {
                    if (rowEl.style.display === 'table-row') {
                        panel.style.maxHeight = 'none';
                    }
                }, 230);
            }

            function openRoSlideDownRow(rowEl) {
                if (!rowEl) return;
                rowEl.style.display = 'table-row';
                const panel = rowEl.querySelector('.ro-slide-panel');
                if (!panel) return;
                panel.style.overflow = 'visible';
                panel.style.maxHeight = '0px';
                panel.style.opacity = '0';
                requestAnimationFrame(() => {
                    panel.style.maxHeight = `${panel.scrollHeight}px`;
                    panel.style.opacity = '1';
                    setTimeout(() => {
                        if (rowEl.style.display === 'table-row') {
                            panel.style.maxHeight = 'none';
                        }
                    }, 230);
                });
            }

            function closeRoSlideDownRow(rowEl) {
                if (!rowEl) return;
                const panel = rowEl.querySelector('.ro-slide-panel');
                if (!panel) {
                    rowEl.style.display = 'none';
                    return;
                }
                if (panel.style.maxHeight === 'none') {
                    panel.style.maxHeight = `${panel.scrollHeight}px`;
                    void panel.offsetHeight;
                }
                panel.style.maxHeight = '0px';
                panel.style.opacity = '0';
                setTimeout(() => {
                    if (panel.style.maxHeight === '0px') {
                        rowEl.style.display = 'none';
                    }
                }, 220);
            }

            function toggleRoSlideDown(roNumber, type) {
                const roId = safeId(roNumber);
                const rowEl = document.getElementById(`${type}-row-${roId}`);
                if (!rowEl) return false;

                const isHidden = rowEl.style.display === 'none' || rowEl.style.display === '';
                if (isHidden) {
                    closeOtherRoSlideDownsForSameRo(roNumber, type);
                    openRoSlideDownRow(rowEl);
                    rememberRoSlideDownOpen(roNumber, type);
                    return true;
                }

                closeRoSlideDownRow(rowEl);
                forgetRoSlideDownOpen(roNumber, type);
                return false;
            }

            function toggleRoNotes(roNumber) {
                const opened = toggleRoSlideDown(roNumber, 'notes');
                if (opened) {
                    loadRoNotes(roNumber);
                }
            }

            function toggleCustomerContact(event, roNumber) {
                if (event) event.stopPropagation();
                toggleRoSlideDown(roNumber, 'customer-contact');
            }

            function toggleInsuranceClaim(event, roNumber) {
                if (event) event.stopPropagation();
                toggleRoSlideDown(roNumber, 'insurance-claim');
            }

            function toggleVehicleVin(event, roNumber) {
                if (event) event.stopPropagation();
                toggleRoSlideDown(roNumber, 'vehicle-vin');
            }

            function toggleRoActivityLogFromRow(event, roNumber) {
                if (!event) return;
                if (event.target && event.target.closest && event.target.closest('button, select, input, textarea, label, .mini-popup-panel, .ro-slide-panel')) {
                    return;
                }
                const opened = toggleRoSlideDown(roNumber, 'activity');
                if (opened) {
                    loadRoActivityLog(roNumber);
                }
            }

            function loadRoActivityLog(roNumber) {
                const listEl = document.getElementById(`activity-list-${safeId(roNumber)}`);
                if (!listEl) return;
                listEl.innerHTML = '<div style="color:#777;">Loading...</div>';

                fetch(`/api/ro-activity?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (!listEl) return;
                        const entries = Array.isArray(res.entries) ? res.entries : [];
                        if (entries.length === 0) {
                            listEl.innerHTML = '<div style="color:#999;">No activity found.</div>';
                            refreshRoSlideDownHeight(roNumber, 'activity');
                            return;
                        }
                        listEl.innerHTML = entries.map((entry) => {
                            const dateText = entry.date || '-';
                            const message = entry.message || '';
                            return `
                                <div style="padding:8px 0; border-bottom:1px solid #eee;">
                                    <div style="font-size:12px; color:#777; margin-bottom:2px;">${dateText}</div>
                                    <div style="color:#333;">${message}</div>
                                </div>
                            `;
                        }).join('');
                        refreshRoSlideDownHeight(roNumber, 'activity');
                    })
                    .catch(err => {
                        console.error('Error loading RO activity:', err);
                        if (listEl) {
                            listEl.innerHTML = '<div style="color:red;">Error loading activity.</div>';
                            refreshRoSlideDownHeight(roNumber, 'activity');
                        }
                    });
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
                            refreshRoSlideDownHeight(roNumber, 'notes');
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
                        refreshRoSlideDownHeight(roNumber, 'notes');
                    })
                    .catch(err => {
                        console.error('Error loading notes:', err);
                        if (listEl) {
                            listEl.innerHTML = '<div style="color:red;">Error loading notes.</div>';
                            refreshRoSlideDownHeight(roNumber, 'notes');
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

            function formatPhaseDisplay(phase) {
                const key = String(phase || 'teardown').trim().toLowerCase();
                const labelMap = {
                    teardown: 'Teardown',
                    auth: 'Auth',
                    parts: 'Parts',
                    body: 'Body',
                    refinish: 'Refinish',
                    reassy: 'Reassy',
                    sublet: 'Sublet',
                    washqc: 'Wash/QC',
                    'wash/qc': 'Wash/QC',
                    complete: 'Complete/Finish',
                    'complete/finish': 'Complete/Finish'
                };
                return labelMap[key] || phase || 'Teardown';
            }

            function normalizePhaseValue(phase) {
                const key = String(phase || 'teardown').trim().toLowerCase();
                if (key === 'wash/qc') return 'washqc';
                if (key === 'complete/finish') return 'complete';
                return key || 'teardown';
            }

            function getPhaseDropdownOptions(selectedPhase) {
                const selected = normalizePhaseValue(selectedPhase);
                const options = [
                    { value: 'teardown', label: 'Teardown' },
                    { value: 'auth', label: 'Auth' },
                    { value: 'parts', label: 'Parts' },
                    { value: 'body', label: 'Body' },
                    { value: 'refinish', label: 'Refinish' },
                    { value: 'reassy', label: 'Reassy' },
                    { value: 'sublet', label: 'Sublet' },
                    { value: 'washqc', label: 'Wash/QC' },
                    { value: 'complete', label: 'Complete/Finish' }
                ];
                return options
                    .map((option) => `<option value="${option.value}" ${selected === option.value ? 'selected' : ''}>${option.label}</option>`)
                    .join('');
            }

            async function changeRoPhase(event, roNumber, phaseValue) {
                if (event) event.stopPropagation();
                const normalizedPhase = normalizePhaseValue(phaseValue);

                try {
                    const response = await fetch('/api/phase/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ ro: roNumber, phase: normalizedPhase })
                    });
                    const result = await response.json();
                    if (!response.ok || result.error) {
                        throw new Error(result.error || 'Failed to save phase');
                    }

                    if (dashboardData && Array.isArray(dashboardData.roList)) {
                        dashboardData.roList = dashboardData.roList.map((row) => (
                            row && row.ro === roNumber
                                ? { ...row, phase: normalizedPhase }
                                : row
                        ));
                        updateRoListTable(dashboardData.roList);
                    }

                    if (typeof loadPhaseData === 'function') {
                        loadPhaseData();
                    }
                } catch (error) {
                    console.error('Error updating phase from dashboard:', error);
                    alert('Error updating phase.');
                    if (typeof loadDashboardData === 'function') {
                        loadDashboardData();
                    }
                }
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

            function calculateDaysSince(isoDate) {
                if (!isoDate) return null;
                try {
                    const [yearStr, monthStr, dayStr] = isoDate.split('-');
                    const inDate = new Date(Number(yearStr), Number(monthStr) - 1, Number(dayStr));
                    if (isNaN(inDate.getTime())) return null;
                    
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    inDate.setHours(0, 0, 0, 0);
                    
                    const diffTime = today - inDate;
                    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                    
                    return diffDays;
                } catch (error) {
                    return null;
                }
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

                if (sortKey === 'days_since_in') {
                    const days = calculateDaysSince(ro.in_date || '');
                    return days === null ? -1 : Number(days);
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

            // Sublet detection functions
            function getPendingSubletItems(ro) {
                if (!ro) return [];
                
                const subletItems = [];
                // Only check parts repairs (not labor/paint repairs)
                const partsItems = ro.parts_repairs || [];
                
                // Keywords that should trigger warning
                const directKeywords = [
                    'wheel',
                    'alignment',
                    'thrust angle',
                    'windshield',
                    'w/shield',
                    'qtr glass',
                    'backglass',
                    'stripe',
                    'stripes',
                    'edge guard',
                    'edge guards'
                ];
                
                partsItems.forEach(item => {
                    if (!item || !item.description) return;
                    
                    const desc = String(item.description).toLowerCase();
                    
                    // Check for direct keywords
                    for (const keyword of directKeywords) {
                        if (desc.includes(keyword)) {
                            // Exclusions for "wheel"
                            if (keyword === 'wheel' && (
                                desc.includes('steering wheel') ||
                                desc.includes('fender wheel') ||
                                desc.includes('wheel pick up') ||
                                desc.includes('wheelhouse') ||
                                desc.includes('wheel opng mldg') ||
                                desc.includes('wheel opening mldg')
                            )) {
                                continue;
                            }
                            
                            // Exclusions for "windshield" and "w/shield"
                            if ((keyword === 'windshield' || keyword === 'w/shield') && (
                                desc.includes('w/shield washer') ||
                                desc.includes('w/shield wipper') ||
                                desc.includes('windshield washer') ||
                                desc.includes('windshield wipper')
                            )) {
                                continue;
                            }
                            
                            subletItems.push({
                                description: item.description,
                                line: item.line,
                                type: 'Parts'
                            });
                            return; // Don't check other keywords for this item
                        }
                    }
                });
                
                return subletItems;
            }
            
            function hasSubletWarning(ro) {
                const subletItems = getPendingSubletItems(ro);
                return subletItems.length > 0;
            }
            
            // Track currently open mini popup panel
            let currentOpenMiniPopup = null;

            function openMiniPopup(panel) {
                if (!panel) return;
                if (currentOpenMiniPopup && currentOpenMiniPopup !== panel) {
                    closeMiniPopup(currentOpenMiniPopup);
                }
                panel.style.display = 'block';
                requestAnimationFrame(() => {
                    panel.classList.add('open');
                });
                currentOpenMiniPopup = panel;
            }

            function closeMiniPopup(panel) {
                if (!panel) return;
                panel.classList.remove('open');
                setTimeout(() => {
                    if (!panel.classList.contains('open')) {
                        panel.style.display = 'none';
                    }
                }, 200);
                if (currentOpenMiniPopup === panel) {
                    currentOpenMiniPopup = null;
                }
            }

            function toggleMiniPopup(panel) {
                if (!panel) return;
                const shouldOpen = panel.style.display === 'none' || panel.style.display === '';
                if (shouldOpen) {
                    openMiniPopup(panel);
                } else {
                    closeMiniPopup(panel);
                }
            }
            
            function toggleSubletPanel(event, roNumber) {
                event.stopPropagation();
                event.preventDefault();
                
                const panelId = `sublet-panel-${safeId(roNumber)}`;
                const panel = document.getElementById(panelId);
                
                if (!panel) return;

                toggleMiniPopup(panel);
            }
            
            // Close panel when clicking outside
            document.addEventListener('click', function(event) {
                if (currentOpenMiniPopup &&
                    !event.target.closest('.mini-popup-trigger') &&
                    !event.target.closest('.mini-popup-panel')) {
                    closeMiniPopup(currentOpenMiniPopup);
                }
            });

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
                    const rowBg = index % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                    const rowId = safeId(ro.ro);
                    const estimatorDisplay = getRoEstimatorDisplay(ro);
                    const customerDisplay = ro.customer || '-';
                    const phoneDisplay = cleanPhoneNumber(ro.phone);
                    const insuranceDisplay = (ro.insurance || '-').split(/\s+/).slice(0, 2).join(' ');
                    const claimDisplay = ro.claim_number || '-';
                    const phaseDisplay = formatPhaseDisplay(ro.phase);
                    const phaseSelectOptions = getPhaseDropdownOptions(ro.phase);
                    const vinDisplay = ro.vin || '-';
                    const phoneOriginal = cleanPhoneNumber(ro.phone_original) || phoneDisplay || '-';
                    const inIso = ro.in_date || '';
                    const ecdIso = ro.ecd_date || computeEcdIso(inIso, Number(ro.hours || 0));
                    const inDisplay = formatShortDate(inIso);
                    const ecdDisplay = formatShortDate(ecdIso);
                    
                    // Calculate days since in date
                    const daysSinceIn = calculateDaysSince(inIso);
                    const daysDisplay = daysSinceIn !== null ? daysSinceIn : '-';
                    
                    // Check for sublet warning
                    const showSubletWarning = hasSubletWarning(ro);
                    const subletItems = showSubletWarning ? getPendingSubletItems(ro) : [];
                    
                    html += `
                        <tr style="background:${rowBg};" onclick="toggleRoActivityLogFromRow(event, '${ro.ro}')">
                            <td style="padding:12px; border-bottom:1px solid #eee; position:relative;">
                                <div style="display:inline-flex; align-items:center; gap:6px;">
                                    <button type="button" class="mini-popup-trigger" onclick="openRoPrintModal(event, '${ro.ro}')" style="background:none; border:none; color:#333; cursor:pointer; padding:0; font-size:16px; line-height:1;" title="Print Reports">🖨️</button>
                                    <button type="button" onclick="toggleRoNotesFromLink(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                        ${ro.ro}
                                    </button>
                                    ${showSubletWarning ? `
                                        <span class="sublet-warning-icon mini-popup-trigger" onclick="toggleSubletPanel(event, '${ro.ro}')" style="cursor:pointer; color:#ff9800; font-size:18px; line-height:1;" title="Pending Sublets">⚠️</span>
                                        <div id="sublet-panel-${rowId}" class="sublet-panel mini-popup-panel" style="display:none;">
                                            <div style="font-weight:bold; color:#e65100; margin-bottom:8px; font-size:14px;">Pending Sublet Items:</div>
                                            <ul style="margin:0; padding-left:20px; font-size:13px;">
                                                ${subletItems.map(item => `
                                                    <li style="margin-bottom:6px; color:#333;">
                                                        ${item.line ? `<strong>Line ${item.line}:</strong> ` : ''}${item.description}
                                                        <span style="color:#666; font-size:11px;"> (${item.type})</span>
                                                    </li>
                                                `).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}
                                    <div id="ro-print-panel-${rowId}" class="mini-popup-panel" style="display:none;">
                                        <h2 id="roPrintTitle-${rowId}" style="margin:0 0 12px 0; color:#333; font-size:16px;">Print Reports - RO# ${ro.ro}</h2>
                                        <p style="margin:0 0 10px 0; font-weight:bold; color:#555;">Select reports to print:</p>
                                        <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:12px;">
                                            <label style="display:flex; align-items:center; gap:8px; padding:8px; background:#f9f9f9; border-radius:4px; cursor:pointer;">
                                                <input type="checkbox" id="printFileCover-${rowId}" style="width:16px; height:16px; cursor:pointer;" />
                                                <span style="font-size:14px;">File Cover Page</span>
                                            </label>
                                            <label style="display:flex; align-items:center; gap:8px; padding:8px; background:#f9f9f9; border-radius:4px; cursor:pointer;">
                                                <input type="checkbox" id="printVehicleTag-${rowId}" style="width:16px; height:16px; cursor:pointer;" />
                                                <span style="font-size:14px;">Vehicle Tag</span>
                                            </label>
                                            <label style="display:flex; align-items:center; gap:8px; padding:8px; background:#f9f9f9; border-radius:4px; cursor:pointer;">
                                                <input type="checkbox" id="printTechBody-${rowId}" style="width:16px; height:16px; cursor:pointer;" />
                                                <span style="font-size:14px;">Tech Body</span>
                                            </label>
                                            <label style="display:flex; align-items:center; gap:8px; padding:8px; background:#f9f9f9; border-radius:4px; cursor:pointer;">
                                                <input type="checkbox" id="printTechPaint-${rowId}" style="width:16px; height:16px; cursor:pointer;" />
                                                <span style="font-size:14px;">Tech Paint</span>
                                            </label>
                                            <label style="display:flex; align-items:center; gap:8px; padding:8px; background:#f9f9f9; border-radius:4px; cursor:pointer;">
                                                <input type="checkbox" id="printTechMech-${rowId}" style="width:16px; height:16px; cursor:pointer;" />
                                                <span style="font-size:14px;">Tech Mech</span>
                                            </label>
                                        </div>
                                        <div style="display:flex; justify-content:flex-end; gap:8px;">
                                            <button onclick="closeRoPrintModal()" style="padding:8px 14px; background:#999; color:#fff; border:none; border-radius:4px; cursor:pointer;">Cancel</button>
                                            <button onclick="generateSelectedPrints()" style="padding:8px 14px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Print</button>
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button type="button" onclick="toggleVehicleVin(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; text-align:left;">
                                    ${ro.vehicle || 'N/A'}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button type="button" onclick="toggleCustomerContact(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; text-align:left;">
                                    ${customerDisplay}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button type="button" onclick="toggleInsuranceClaim(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; text-align:left;">
                                    ${insuranceDisplay}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <select onchange="changeRoPhase(event, '${ro.ro}', this.value)" style="padding:4px 6px; border:1px solid #ccc; border-radius:4px; background:#fff; color:#333; font-size:13px; max-width:160px;">
                                    ${phaseSelectOptions}
                                </select>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button id="ro-date-in_date-${rowId}" class="ro-date-btn" data-iso="${inIso}" type="button" onclick="openRoDatePicker(event, '${rowId}', '${ro.ro}', 'in_date', ${Number(ro.hours || 0)})" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${inDisplay}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#555; text-align:center; font-weight:bold;">${daysDisplay}</td>
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
                        <tr id="vehicle-vin-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:0 16px 10px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px 12px;">
                                        <span style="font-weight:bold; color:#555;">VIN:</span>
                                        <span style="margin-left:8px; color:#333;">${vinDisplay}</span>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr id="activity-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:0 16px 10px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px 12px;">
                                        <div style="font-weight:bold; margin-bottom:8px; color:#333;">RO Activity Log</div>
                                        <div id="activity-list-${rowId}" style="width:100%;"></div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr id="customer-contact-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:0 16px 10px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px 12px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                                        <span style="font-weight:bold; color:#555;">Phone:</span>
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
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr id="insurance-claim-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:0 16px 10px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px 12px;">
                                        <span style="font-weight:bold; color:#555;">Claim Number:</span>
                                        <span style="margin-left:8px; color:#333;">${claimDisplay}</span>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr id="tech-assignment-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:16px; border-bottom:1px solid #eee;">
                                <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:16px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                        <div style="font-weight:bold; color:#333;">Tech List</div>
                                        <div style="font-weight:bold; color:#333; font-style:italic;">*${escapeHtml(estimatorDisplay)}*</div>
                                    </div>
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
                restoreOpenRoSlideDowns();
            }

            function toggleTechAssignment(event, roNumber) {
                if (event) event.stopPropagation();
                const opened = toggleRoSlideDown(roNumber, 'tech-assignment');
                if (opened) {
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

            function getRoEstimatorDisplay(ro) {
                const preferred = String(ro?.written_by || '').trim() || String(ro?.estimator || '').trim();
                if (preferred) {
                    return preferred.toUpperCase();
                }

                const ownerInfo = String(ro?.owner_info || '').trim();
                if (ownerInfo) {
                    const writtenByMatch = ownerInfo.match(/written\s*by\s*:\s*([^\n,]+)/i);
                    if (writtenByMatch && writtenByMatch[1]) {
                        return String(writtenByMatch[1]).trim().toUpperCase();
                    }
                    const estimatorMatch = ownerInfo.match(/estimator\s*:\s*([^\n,]+)/i);
                    if (estimatorMatch && estimatorMatch[1]) {
                        return String(estimatorMatch[1]).trim().toUpperCase();
                    }
                }

                return '-';
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
                            refreshRoSlideDownHeight(roNumber, 'tech-assignment');
                        }
                    })
                    .catch(err => {
                        console.error('Error loading repair data:', err);
                        if (listEl) {
                            listEl.innerHTML = '<div style="color:red; padding:12px;">Error loading data. Check console.</div>';
                            refreshRoSlideDownHeight(roNumber, 'tech-assignment');
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
                    <!DOCTYPE html>
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
            
            // Print Options Modal Functions
            function openPrintOptionsModal() {
                toggleMiniPopup(document.getElementById('printOptionsModal'));
            }
            
            function closePrintOptionsModal() {
                closeMiniPopup(document.getElementById('printOptionsModal'));
            }
            
            function printRoList(sortBy) {
                closePrintOptionsModal();
                
                if (!dashboardData || !dashboardData.roList || dashboardData.roList.length === 0) {
                    alert('No repair orders to print');
                    return;
                }
                
                // Sort the data
                const sortedList = [...dashboardData.roList].sort((a, b) => {
                    let valA = a[sortBy];
                    let valB = b[sortBy];
                    
                    if (sortBy === 'ro' || sortBy === 'insurance') {
                        valA = String(valA || '').toLowerCase();
                        valB = String(valB || '').toLowerCase();
                        return valA.localeCompare(valB);
                    }
                    
                    if (sortBy === 'in_date' || sortBy === 'ecd_date') {
                        valA = valA || '';
                        valB = valB || '';
                        return valA.localeCompare(valB);
                    }
                    
                    return 0;
                });
                
                // Get sort label
                const sortLabels = {
                    'ro': 'RO #',
                    'insurance': 'Insurance',
                    'in_date': 'In date',
                    'ecd_date': 'ECD'
                };
                const sortLabel = sortLabels[sortBy] || sortBy;
                
                // Build table rows
                let rowsHtml = '';
                sortedList.forEach((ro, index) => {
                    const rowBg = index % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                    const inDisplay = ro.in_date ? formatShortDate(ro.in_date) : '-';
                    const ecdDisplay = ro.ecd_date ? formatShortDate(ro.ecd_date) : '-';
                    const daysSinceIn = calculateDaysSince(ro.in_date || '');
                    const daysDisplay = daysSinceIn !== null ? daysSinceIn : '-';
                    
                    rowsHtml += `
                        <tr style="background:${rowBg};">
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ro.ro}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ro.vehicle || 'N/A'}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ro.customer || '-'}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ro.phone || '-'}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ro.insurance || '-'}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ro.claim_number || '-'}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${inDisplay}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:center; font-weight:bold;">${daysDisplay}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${ecdDisplay}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${ro.hours.toFixed(1)}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">$${ro.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                    `;
                });
                
                // Calculate totals
                const totalHours = sortedList.reduce((sum, ro) => sum + ro.hours, 0);
                const totalAmount = sortedList.reduce((sum, ro) => sum + ro.total, 0);
                
                // Open print window
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>RO List - Print by ${sortLabel}</title>
                            <style>
                                @media print {
                                    @page { margin: 0.5in; }
                                    body { margin: 0; }
                                }
                                body {
                                    font-family: Arial, sans-serif;
                                    padding: 20px;
                                    color: #333;
                                }
                                .header {
                                    text-align: center;
                                    margin-bottom: 30px;
                                    border-bottom: 2px solid #b22222;
                                    padding-bottom: 15px;
                                }
                                .header h1 {
                                    margin: 0 0 8px 0;
                                    color: #b22222;
                                    font-size: 28px;
                                }
                                .header .subtitle {
                                    margin: 0;
                                    color: #666;
                                    font-size: 16px;
                                }
                                table {
                                    width: 100%;
                                    border-collapse: collapse;
                                    margin-top: 20px;
                                }
                                thead th {
                                    text-align: left;
                                    background: #f5f5f5;
                                    padding: 12px 10px;
                                    border-bottom: 2px solid #ddd;
                                    font-weight: bold;
                                    color: #555;
                                    font-size: 13px;
                                }
                                tbody td {
                                    font-size: 12px;
                                }
                                .totals {
                                    margin-top: 20px;
                                    padding-top: 15px;
                                    border-top: 2px solid #333;
                                    display: flex;
                                    justify-content: flex-end;
                                    gap: 40px;
                                    font-weight: bold;
                                    font-size: 15px;
                                }
                                .footer {
                                    margin-top: 40px;
                                    text-align: center;
                                    color: #999;
                                    font-size: 11px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>Repair Orders</h1>
                                <p class="subtitle">Print by: ${sortLabel}</p>
                            </div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>RO #</th>
                                        <th>Vehicle</th>
                                        <th>Customer</th>
                                        <th>Phone</th>
                                        <th>Insurance</th>
                                        <th>Claim #</th>
                                        <th>In</th>
                                        <th style="text-align:center;">⏳</th>
                                        <th>ECD</th>
                                        <th style="text-align:right;">HRS</th>
                                        <th style="text-align:right;">Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${rowsHtml}
                                </tbody>
                            </table>
                            <div class="totals">
                                <div>Total ROs: ${sortedList.length}</div>
                                <div>Total Hours: ${totalHours.toFixed(1)}</div>
                                <div>Total Amount: $${totalAmount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                            </div>
                            <div class="footer">
                                <p>Generated on ${new Date().toLocaleString()}</p>
                            </div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => {
                    printWindow.print();
                }, 250);
            }
            
            // RO Print Modal Functions
            let currentRoPrintData = null;
            
            function openRoPrintModal(event, roNumber) {
                if (event) event.stopPropagation();
                const rowId = safeId(roNumber);
                const panel = document.getElementById(`ro-print-panel-${rowId}`);
                if (!panel) return;
                
                // Reset checkboxes
                const fileCoverEl = document.getElementById(`printFileCover-${rowId}`);
                const vehicleTagEl = document.getElementById(`printVehicleTag-${rowId}`);
                const techBodyEl = document.getElementById(`printTechBody-${rowId}`);
                const techPaintEl = document.getElementById(`printTechPaint-${rowId}`);
                const techMechEl = document.getElementById(`printTechMech-${rowId}`);
                if (fileCoverEl) fileCoverEl.checked = false;
                if (vehicleTagEl) vehicleTagEl.checked = false;
                if (techBodyEl) techBodyEl.checked = false;
                if (techPaintEl) techPaintEl.checked = false;
                if (techMechEl) techMechEl.checked = false;
                
                // Update title
                const titleEl = document.getElementById(`roPrintTitle-${rowId}`);
                if (titleEl) titleEl.textContent = `Print Reports - RO# ${roNumber}`;
                
                // Store RO number for later use
                currentRoPrintData = { ro: roNumber, rowId };
                
                // Show popup
                toggleMiniPopup(panel);
            }
            
            function closeRoPrintModal() {
                const rowId = currentRoPrintData?.rowId;
                if (rowId) {
                    closeMiniPopup(document.getElementById(`ro-print-panel-${rowId}`));
                }
                currentRoPrintData = null;
            }
            
            async function generateSelectedPrints() {
                if (!currentRoPrintData || !currentRoPrintData.ro) {
                    return;
                }
                
                const rowId = currentRoPrintData.rowId;
                const fileCover = !!document.getElementById(`printFileCover-${rowId}`)?.checked;
                const vehicleTag = !!document.getElementById(`printVehicleTag-${rowId}`)?.checked;
                const techBody = !!document.getElementById(`printTechBody-${rowId}`)?.checked;
                const techPaint = !!document.getElementById(`printTechPaint-${rowId}`)?.checked;
                const techMech = !!document.getElementById(`printTechMech-${rowId}`)?.checked;
                
                if (!fileCover && !vehicleTag && !techBody && !techPaint && !techMech) {
                    alert('Please select at least one report to print.');
                    return;
                }
                
                try {
                    // Fetch print data
                    const response = await fetch(`/api/ro-print-data?ro=${encodeURIComponent(currentRoPrintData.ro)}`, {
                        credentials: 'include'
                    });
                    
                    if (!response.ok) {
                        throw new Error('Failed to load print data');
                    }
                    
                    const data = await response.json();
                    
                    // Close modal
                    closeRoPrintModal();
                    
                    // Generate selected prints
                    if (fileCover) printFileCover(data);
                    if (vehicleTag) printVehicleTag(data);
                    if (techBody) printTechBody(data);
                    if (techPaint) printTechPaint(data);
                    if (techMech) printTechMech(data);
                    
                } catch (err) {
                    console.error('Error generating prints:', err);
                    alert('Error loading print data. Please try again.');
                }
            }
            
            function printFileCover(data) {
                // Generate handwritten note lines to fill the page (single column, full width)
                // Reduced to every other line for easier writing
                const numLines = 11;
                let noteLinesHtml = '';
                for (let i = 0; i < numLines; i++) {
                    noteLinesHtml += '<div class="note-line">______/______/_________:_______________________________________________________________________________________________________________________________________________</div>';
                }
                
                const techDisplay = data.techs.body || '';
                
                const printWindow = window.open('', '_blank', 'width=1100,height=850');
                if (!printWindow) return;
                
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>File Cover Page - ${data.ro}</title>
                            <style>
                                @media print {
                                    @page { 
                                        size: landscape;
                                        margin: 0.5in;
                                    }
                                    body { margin: 0; }
                                }
                                body {
                                    font-family: Arial, sans-serif;
                                    padding: 30px;
                                    color: #222;
                                }
                                .header {
                                    text-align: center;
                                    margin-bottom: 45px;
                                    border-bottom: 3px solid #d32f2f;
                                    padding-bottom: 22px;
                                }
                                .header h1 {
                                    margin: 0;
                                    font-size: 48px;
                                    color: #d32f2f;
                                }
                                .info-grid {
                                    display: grid;
                                    grid-template-columns: 1fr 1fr;
                                    gap: 30px 60px;
                                    margin-bottom: 45px;
                                }
                                .info-item {
                                    display: flex;
                                    gap: 15px;
                                }
                                .info-label {
                                    font-weight: bold;
                                    color: #555;
                                    min-width: 150px;
                                    font-size: 24px;
                                }
                                .info-value {
                                    color: #222;
                                    font-size: 24px;
                                }
                                .info-value.ro-number {
                                    font-size: 96px;
                                    font-weight: bold;
                                    color: #d32f2f;
                                }
                                .totals-section {
                                    display: flex;
                                    gap: 45px;
                                    margin-top: 45px;
                                    padding: 30px;
                                    background: #f5f5f5;
                                    border-radius: 8px;
                                }
                                .total-item {
                                    flex: 1;
                                }
                                .total-label {
                                    font-size: 21px;
                                    color: #666;
                                    margin-bottom: 8px;
                                }
                                .total-value {
                                    font-size: 36px;
                                    font-weight: bold;
                                    color: #d32f2f;
                                }
                                .notes-section {
                                    margin-top: 45px;
                                    padding: 30px;
                                    border: 2px solid #ddd;
                                    border-radius: 8px;
                                }
                                .notes-title {
                                    font-weight: bold;
                                    font-size: 27px;
                                    margin-bottom: 22px;
                                    color: #333;
                                }
                                .note-line {
                                    font-family: 'Courier New', monospace;
                                    font-size: 16px;
                                    color: #333;
                                    letter-spacing: 0.5px;
                                    margin-bottom: 28px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>FILE COVER PAGE</h1>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <div class="info-label">RO#:</div>
                                    <div class="info-value ro-number">${escapeHtml(data.ro)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Vehicle:</div>
                                    <div class="info-value">${escapeHtml(data.vehicle)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">VIN:</div>
                                    <div class="info-value">${escapeHtml(data.vin)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Insurance:</div>
                                    <div class="info-value">${escapeHtml(data.insurance)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Claim#:</div>
                                    <div class="info-value">${escapeHtml(data.claim_number)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Tech:</div>
                                    <div class="info-value">${escapeHtml(techDisplay)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">In Date:</div>
                                    <div class="info-value">${formatShortDate(data.in_date)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">ECD:</div>
                                    <div class="info-value">${formatShortDate(data.ecd_date)}</div>
                                </div>
                            </div>
                            <div class="totals-section">
                                <div class="total-item">
                                    <div class="total-label">Total</div>
                                    <div class="total-value">$${data.totals.grand_total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                                </div>
                                <div class="total-item">
                                    <div class="total-label">Insurance Total</div>
                                    <div class="total-value">$${data.totals.insurance_total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                                </div>
                                <div class="total-item">
                                    <div class="total-label">Customer Total</div>
                                    <div class="total-value">$${data.totals.customer_total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                                </div>
                            </div>
                            <div class="notes-section">
                                <div class="notes-title">Notes</div>
                                ${noteLinesHtml}
                            </div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => printWindow.print(), 250);
            }
            
            function printVehicleTag(data) {
                const printWindow = window.open('', '_blank', 'width=800,height=1000');
                if (!printWindow) return;
                
                const techDisplay = data.techs.body || '';
                
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>Vehicle Tag - ${data.ro}</title>
                            <style>
                                @media print {
                                    @page { margin: 0.5in; }
                                    body { margin: 0; }
                                }
                                body {
                                    font-family: Arial, sans-serif;
                                    padding: 40px;
                                    color: #222;
                                }
                                .line {
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: baseline;
                                    margin-bottom: 15px;
                                }
                                .vehicle-info {
                                    font-size: 38px;
                                    font-weight: bold;
                                }
                                .ro-section {
                                    font-size: 156px;
                                    font-weight: bold;
                                    color: #d32f2f;
                                    text-align: right;
                                }
                                .vin-info {
                                    font-size: 32px;
                                    color: #333;
                                }
                                .tech-section {
                                    font-size: 32px;
                                    color: #333;
                                    text-align: right;
                                }
                                .separator {
                                    border-top: 2px solid #333;
                                    margin: 25px 0;
                                }
                                .two-col {
                                    display: grid;
                                    grid-template-columns: 1fr 1fr;
                                    gap: 40px;
                                    margin-bottom: 30px;
                                }
                                .section-label {
                                    font-size: 36px;
                                    font-weight: bold;
                                    color: #555;
                                    margin-bottom: 10px;
                                    text-transform: uppercase;
                                }
                                .section-content {
                                    font-size: 28px;
                                    color: #222;
                                    line-height: 1.6;
                                }
                                .date-section {
                                    display: grid;
                                    grid-template-columns: 1fr 1fr;
                                    gap: 40px;
                                    margin: 30px 0;
                                }
                                .date-item {
                                    display: flex;
                                    flex-direction: column;
                                }
                                .date-label {
                                    font-size: 32px;
                                    font-weight: bold;
                                    color: #555;
                                    text-transform: uppercase;
                                    margin-bottom: 8px;
                                }
                                .date-value {
                                    font-size: 36px;
                                    color: #222;
                                }
                                .checklist-container {
                                    margin-top: 40px;
                                }
                                .checklist-row {
                                    display: grid;
                                    grid-template-columns: repeat(4, 1fr);
                                    gap: 20px;
                                    margin-bottom: 120px;
                                }
                                .checklist-row-centered {
                                    display: flex;
                                    justify-content: space-around;
                                    gap: 60px;
                                    max-width: 80%;
                                    margin: 0 auto;
                                }
                                .checklist-item {
                                    display: flex;
                                    align-items: flex-start;
                                    gap: 10px;
                                }
                                .checkbox {
                                    width: 35px;
                                    height: 35px;
                                    border: 4px solid #333;
                                    border-radius: 4px;
                                    flex-shrink: 0;
                                    margin-top: 3px;
                                }
                                .checklist-content {
                                    display: flex;
                                    flex-direction: column;
                                    gap: 5px;
                                }
                                .checklist-label {
                                    font-size: 28px;
                                    font-weight: bold;
                                    color: #333;
                                    text-transform: uppercase;
                                }
                                .checklist-line {
                                    font-size: 36px;
                                    color: #666;
                                    font-family: 'Courier New', monospace;
                                    letter-spacing: 1px;
                                }
                                .signature-line {
                                    font-size: 14px;
                                    color: #888;
                                    margin-top: 9px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="line">
                                <div class="vehicle-info">${escapeHtml(data.vehicle)}</div>
                                <div class="ro-section">RO# ${escapeHtml(data.ro)}</div>
                            </div>
                            <div class="line">
                                <div class="vin-info">VIN: ${escapeHtml(data.vin)}</div>
                                <div class="tech-section">Tech: ${escapeHtml(techDisplay)}</div>
                            </div>
                            
                            <div class="separator"></div>
                            
                            <div class="two-col">
                                <div>
                                    <div class="section-label">Customer</div>
                                    <div class="section-content">
                                        ${escapeHtml(data.customer)}<br/>
                                        ${escapeHtml(data.phone)}
                                    </div>
                                </div>
                                <div>
                                    <div class="section-label">Insurance</div>
                                    <div class="section-content">
                                        ${escapeHtml(data.insurance)}<br/>
                                        Claim# ${escapeHtml(data.claim_number)}
                                    </div>
                                </div>
                            </div>
                            
                            <div class="date-section">
                                <div class="date-item">
                                    <div class="date-label">In Date</div>
                                    <div class="date-value">${formatShortDate(data.in_date)}</div>
                                </div>
                                <div class="date-item">
                                    <div class="date-label">ECD</div>
                                    <div class="date-value">${formatShortDate(data.ecd_date)}</div>
                                </div>
                            </div>
                            
                            <div class="separator"></div>
                            
                            <div class="checklist-container">
                                <div class="checklist-row">
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">Teardown</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">Body</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">Parts</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">Paint</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="checklist-row-centered">
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">Reassy</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">Wash</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                    <div class="checklist-item">
                                        <div class="checkbox"></div>
                                        <div class="checklist-content">
                                            <div class="checklist-label">QC</div>
                                            <div class="checklist-line">___/___/____</div>
                                            <div class="signature-line">Inspected by: ________________</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => printWindow.print(), 250);
            }
            
            function printTechBody(data) {
                printTechLines(data, 'Body', data.body_lines, data.techs.body);
            }
            
            function printTechPaint(data) {
                printTechLines(data, 'Paint', data.paint_lines, data.techs.paint);
            }
            
            function printTechMech(data) {
                printTechLines(data, 'Mech', data.mech_lines, data.techs.mech);
            }
            
            function printTechLines(data, typeName, lines, techName) {
                if (!lines || lines.length === 0) {
                    alert(`No ${typeName} lines found for this RO.`);
                    return;
                }
                
                const totalHours = lines.reduce((sum, line) => sum + line.hours, 0);
                const techDisplayValue = techName || '_______________________';
                
                const linesHtml = lines.map((line, idx) => {
                    const rowBg = idx % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                    return `
                        <tr style="background:${rowBg};">
                            <td style="padding:10px; border-bottom:1px solid #eee;">${escapeHtml(line.line || '-')}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${escapeHtml(line.description)}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right; font-weight:bold;">${line.hours.toFixed(1)}</td>
                        </tr>
                    `;
                }).join('');
                
                const printWindow = window.open('', '_blank', 'width=980,height=760');
                if (!printWindow) return;
                
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>Tech ${typeName} - ${data.ro}</title>
                            <style>
                                @media print {
                                    @page { margin: 0.5in; }
                                    body { margin: 0; }
                                }
                                body {
                                    font-family: Arial, sans-serif;
                                    padding: 28px;
                                    color: #222;
                                }
                                .header {
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    margin-bottom: 25px;
                                    padding-bottom: 15px;
                                    border-bottom: 2px solid #d32f2f;
                                }
                                .title {
                                    font-size: 28px;
                                    font-weight: bold;
                                    color: #d32f2f;
                                }
                                .meta {
                                    text-align: right;
                                    font-size: 14px;
                                    line-height: 1.7;
                                }
                                table {
                                    width: 100%;
                                    border-collapse: collapse;
                                    margin-top: 16px;
                                }
                                thead th {
                                    text-align: left;
                                    background: #f5f5f5;
                                    padding: 12px 10px;
                                    border-bottom: 2px solid #ddd;
                                    font-weight: bold;
                                }
                                thead th:last-child {
                                    text-align: right;
                                }
                                .total {
                                    margin-top: 20px;
                                    font-size: 20px;
                                    font-weight: bold;
                                    text-align: right;
                                    color: #d32f2f;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <div class="title">Tech ${typeName} Lines</div>
                                <div class="meta">
                                    <div><strong>RO#:</strong> ${escapeHtml(data.ro)}</div>
                                    <div><strong>Tech:</strong> ${escapeHtml(techDisplayValue)}</div>
                                    <div><strong>Vehicle:</strong> ${escapeHtml(data.vehicle)}</div>
                                </div>
                            </div>
                            <table>
                                <thead>
                                    <tr>
                                        <th style="width:15%;">Line</th>
                                        <th style="width:65%;">Description</th>
                                        <th style="width:20%;">Hours</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${linesHtml}
                                </tbody>
                            </table>
                            <div class="total">
                                Total Hours: ${totalHours.toFixed(1)}
                            </div>
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => printWindow.print(), 250);
            }
            
            function escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
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

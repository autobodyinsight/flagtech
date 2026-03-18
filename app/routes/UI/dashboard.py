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
                        border:none;
                        box-shadow:0 8px 20px rgba(0,0,0,0.08);
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
            <div style="margin-top:30px;">
                <div style="display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:0; position:relative;">
                    <h3 class="dashboard-ro-title-tab" style="margin:0; color:#333;">Repair Orders</h3>
                    <button id="dashboardPrintTrigger" class="mini-popup-trigger" onclick="openPrintOptionsModal()" style="padding:8px 10px; background:none; border:none; color:#b22222; cursor:pointer; display:inline-flex; align-items:center; justify-content:center;" aria-label="Print">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                            <path d="M7 8V4H17V8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                            <rect x="5" y="14" width="14" height="6" rx="1" stroke="currentColor" stroke-width="1.8"/>
                            <rect x="4" y="8" width="16" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/>
                            <circle cx="17" cy="11" r="1" fill="currentColor"/>
                        </svg>
                    </button>
                    <div id="printOptionsModal" class="mini-popup-panel" style="display:none; right:0; left:auto;">
                        <h2 style="margin:0 0 14px 0; color:#333; font-size:18px;">Print RO List</h2>
                        <p style="margin:0 0 12px 0; font-weight:bold; color:#555;">Print by:</p>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <button onclick="printRoList('ro')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">RO #</button>
                            <button onclick="printRoList('insurance')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Insurance</button>
                            <button onclick="printRoList('in_date')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">In date</button>
                            <button onclick="printRoList('ecd_date')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">ECD</button>
                            <button onclick="printRoList('tech')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Techs</button>
                            <button onclick="printRoList('phase')" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Roadmap</button>
                        </div>
                    </div>
                </div>
                <div class="dashboard-ro-table-wrap" style="overflow-x:auto;">
                    <table id="roListTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="dashboard-header-row">
                                <th class="dashboard-header-cell" data-sort-key="ro" onclick="sortRoListByHeader('ro')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">RO# <span data-sort-indicator="ro" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="vehicle" onclick="sortRoListByHeader('vehicle')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Vehicle <span data-sort-indicator="vehicle" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="customer" onclick="sortRoListByHeader('customer')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Customer <span data-sort-indicator="customer" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="insurance" onclick="sortRoListByHeader('insurance')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Insurance <span data-sort-indicator="insurance" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="phase" onclick="sortRoListByHeader('phase')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">Roadmap <span data-sort-indicator="phase" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="in_date" onclick="sortRoListByHeader('in_date')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">In <span data-sort-indicator="in_date" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="days_since_in" onclick="sortRoListByHeader('days_since_in')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:center; cursor:pointer; user-select:none;" title="Days Since In Date">⏳ <span data-sort-indicator="days_since_in" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" data-sort-key="ecd_date" onclick="sortRoListByHeader('ecd_date')" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">ECD <span data-sort-indicator="ecd_date" style="font-size:12px;"></span></th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right; user-select:none;">HRS</th>
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
            .dashboard-ro-title-tab {
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
            .dashboard-ro-table-wrap {
                background: #ffffff;
                border-radius: 4px;
                overflow: hidden;
            }
            #roListTable {
                width: 100%;
                background: #ffffff;
                border-collapse: collapse;
                border: none;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
                box-shadow: none;
            }
            .dashboard-header-row th,
            .dashboard-header-cell {
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 15px;
                font-weight: 600;
                background: rgba(0,0,0,0.03) !important;
                color: #000000;
                text-align: left !important;
                border: none !important;
                border-bottom: 1px solid #b22222 !important;
                position: sticky;
                top: 0;
                z-index: 2;
                padding-top: 14px !important;
                padding-bottom: 14px !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            #roListTable thead th,
            #roListTable thead th span,
            #roListTable thead th * {
                color: #000000 !important;
            }
            #roListBody tr.dashboard-ro-main-row td {
                background: #ffffff;
                border: none;
                border-bottom: 1px solid rgba(0,0,0,0.06) !important;
                min-height: 48px;
                height: 48px;
                text-align: left;
                vertical-align: middle;
                box-shadow: none !important;
            }
            #roListBody tr.dashboard-ro-main-row + tr.dashboard-ro-main-row td {
                border-top: 6px solid transparent;
                background-clip: padding-box;
            }
            #roListBody tr.dashboard-ro-main-row:hover td {
                background: rgba(0,0,0,0.04) !important;
                box-shadow: none !important;
            }
            #roListTable th:nth-child(6),
            #roListTable td:nth-child(6),
            #roListTable th:nth-child(7),
            #roListTable td:nth-child(7),
            #roListTable th:nth-child(8),
            #roListTable td:nth-child(8) {
                text-align: center !important;
            }
            #roListTable th:nth-child(9),
            #roListTable td:nth-child(9),
            #roListTable th:nth-child(10),
            #roListTable td:nth-child(10) {
                text-align: right !important;
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
        // Opens a new window with RO details banner
        function openRoWindowFromDashboard(event, roNumber) {
            if (event) event.stopPropagation();
            // Find the RO data from dashboardData.roList
            if (!dashboardData || !dashboardData.roList) {
                alert('RO data not loaded.');
                return;
            }
            const ro = dashboardData.roList.find(r => String(r.ro) === String(roNumber));
            if (!ro) {
                alert('RO not found.');
                return;
            }

            const normalizeIsoDateForInput = (value) => {
                if (!value) return '';
                const text = String(value);
                if (text.includes('T')) return text.split('T')[0];
                const dateMatch = text.match(/^(\d{4}-\d{2}-\d{2})/);
                return dateMatch ? dateMatch[1] : '';
            };

            const formatIsoDateForHeader = (isoDate) => {
                const value = String(isoDate || '').trim();
                if (!value) return '-';
                const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
                if (!match) return value;
                return `${match[2]}/${match[3]}/${match[1]}`;
            };

            const inDateValue = normalizeIsoDateForInput(ro.in_date);
            const ecdDateValue = normalizeIsoDateForInput(ro.ecd_date);
            const pickedUpDateValue = normalizeIsoDateForInput(ro.picked_up);
            const inDateDisplay = formatIsoDateForHeader(inDateValue);
            const ecdDateDisplay = formatIsoDateForHeader(ecdDateValue);
            const pickedUpDateDisplay = formatIsoDateForHeader(pickedUpDateValue);
            const insuranceHeaderValue = (() => {
                const text = String(ro.insurance || '').trim();
                if (!text) return '-';
                return text.split(/\s+/).slice(0, 3).join(' ');
            })();
            // SVG line icons (white, flat, no fill)
            const icons = {
                notepad: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="6" width="18" height="16" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="10" x2="19" y2="10" stroke="white" stroke-width="2"/><line x1="9" y1="14" x2="19" y2="14" stroke="white" stroke-width="2"/><line x1="9" y1="18" x2="15" y2="18" stroke="white" stroke-width="2"/></svg>`,
                estimate: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="3" width="16" height="22" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="8" x2="19" y2="8" stroke="white" stroke-width="2"/><rect x="9" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="9" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><line x1="9" y1="22" x2="19" y2="22" stroke="white" stroke-width="2"/></svg>`,
                tech: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="9" r="4" stroke="white" stroke-width="2"/><rect x="7" y="17" width="14" height="6" rx="3" stroke="white" stroke-width="2"/><path d="M21 21l2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/><path d="M7 21l-2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>`,
                cart: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="14" r="9" stroke="white" stroke-width="2"/><circle cx="14" cy="14" r="5.2" stroke="white" stroke-width="2"/><circle cx="14" cy="14" r="1.7" fill="white"/><path d="M14 5.8v3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M14 19v3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M5.8 14h3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M19 14h3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M8.3 8.3l2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/><path d="M17.4 17.4l2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/><path d="M19.7 8.3l-2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/><path d="M10.6 17.4l-2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/></svg>`,
                credit: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="7" width="20" height="14" rx="3" stroke="white" stroke-width="2"/><rect x="7" y="17" width="6" height="3" rx="1.5" stroke="white" stroke-width="2"/><line x1="4" y1="12" x2="24" y2="12" stroke="white" stroke-width="2"/></svg>`,
                print: `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7 9V4h10v5" stroke="white" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><rect x="4" y="9" width="16" height="8" rx="2" stroke="white" stroke-width="1.9"/><path d="M7 17h10v3H7z" stroke="white" stroke-width="1.9" stroke-linejoin="round"/><circle cx="17" cy="12.5" r="0.9" fill="white"/></svg>`,
                close: `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="8.5" stroke="white" stroke-width="1.9"/><path d="M9 9l6 6" stroke="white" stroke-width="1.9" stroke-linecap="round"/><path d="M15 9l-6 6" stroke="white" stroke-width="1.9" stroke-linecap="round"/></svg>`
            };

            // Sidebar HTML
            const sidebarHtml = `
                <div id="roSidebar" style="position:relative; flex:0 0 64px; height:100%; background:linear-gradient(180deg, #000 0%, #b22222 100%); display:flex; flex-direction:column; align-items:center; justify-content:center; box-shadow:2px 0 8px rgba(0,0,0,0.08);">
                    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; flex:1 1 auto; height:100%; width:100%; padding:10px 0; transform:translateY(-30%);">
                        <button id="roSidebarBtn-notes" class="ro-sidebar-btn" data-view="notes" title="Notes" style="background:none; border:none; padding:0; cursor:pointer;">${icons.notepad}</button>
                        <button id="roSidebarBtn-estimate" class="ro-sidebar-btn" data-view="estimate" title="Estimate" style="background:none; border:none; padding:0; cursor:pointer;">${icons.estimate}</button>
                        <button id="roSidebarBtn-tech" class="ro-sidebar-btn" data-view="tech" title="Tech" style="background:none; border:none; padding:0; cursor:pointer;">${icons.tech}</button>
                        <button id="roSidebarBtn-parts" class="ro-sidebar-btn" data-view="parts" title="Parts" style="background:none; border:none; padding:0; cursor:pointer;">${icons.cart}</button>
                        <button id="roSidebarBtn-payments" class="ro-sidebar-btn" data-view="payments" title="Payments" style="background:none; border:none; padding:0; cursor:pointer;">${icons.credit}</button>
                        <div style="position:relative; display:flex; justify-content:center; width:100%;">
                            <button id="roPrintTrigger" class="ro-sidebar-btn ro-sidebar-action mini-popup-trigger" type="button" aria-label="Print" title="Print" style="background:none; border:none; padding:0; cursor:pointer;">${icons.print}</button>
                            <div id="roPrintOptionsModal" class="mini-popup-panel" style="display:none; left:calc(100% + 10px); right:auto; top:0;">
                                <h2 style="margin:0 0 14px 0; color:#333; font-size:18px;">Print RO</h2>
                                <p style="margin:0 0 12px 0; font-weight:bold; color:#555;">Print by:</p>
                                <div style="display:flex; flex-direction:column; gap:8px;">
                                    <button id="roPrintOptionBill" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Bill</button>
                                    <button id="roPrintOptionServiceOrder" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Service Order</button>
                                    <button id="roPrintOptionParts" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Parts</button>
                                    <button id="roPrintOptionServiceTag" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Service Tag</button>
                                    <button id="roPrintOptionServiceCover" type="button" style="padding:10px 12px; background:#f5f5f5; color:#333; border:1px solid #ddd; border-radius:4px; cursor:pointer; text-align:left; font-size:14px;">Service Cover</button>
                                </div>
                                <div id="roPrintServiceOrderWrap" style="display:none; margin-top:10px; padding-top:10px; border-top:1px solid #eee;">
                                    <label for="roPrintTechSelect" style="display:block; margin-bottom:6px; color:#555; font-weight:600;">Tech</label>
                                    <select id="roPrintTechSelect" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; margin-bottom:8px;">
                                        <option value="">Loading...</option>
                                    </select>
                                    <button id="roPrintServiceOrderGo" type="button" style="padding:10px 12px; width:100%; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:14px; font-weight:700;">Print Service Order</button>
                                </div>
                            </div>
                        </div>
                        <button id="roCloseButton" class="ro-sidebar-btn ro-sidebar-action" type="button" aria-label="Close RO" title="Close RO" style="background:none; border:none; padding:0; cursor:pointer;">${icons.close}</button>
                    </div>
                </div>
            `;

            // Banner fields
            const bannerHtml = `
                <div id="roHeaderBar" style="background:linear-gradient(90deg, #111 0%, #23272a 48%, #d32f2f 100%); color:#fff; padding:12px 24px; border-bottom:none; position:relative; z-index:120;">
                    <div id="roClosedStatusLabel" style="position:absolute; top:14px; left:50%; transform:translateX(-50%); font-weight:900; letter-spacing:1.5px; font-size:20px; color:#fff; display:${String((ro.phase || '')).toLowerCase().includes('complete') ? 'block' : 'none'};">CLOSED</div>
                    <div id="roSummaryHeaderGrid" style="display:flex; flex-direction:column; gap:10px; align-items:stretch; margin-right:8px;">
                        <div style="display:grid; grid-template-columns:repeat(5, minmax(0, 1fr)); gap:16px; align-items:center;">
                            <div class="ro-header-item"><span class="ro-header-label">RO#:</span> <span class="ro-header-value">${ro.ro || '-'}</span></div>
                            <div class="ro-header-item"><span class="ro-header-label">Customer:</span> <span class="ro-header-value">${ro.customer || '-'}</span></div>
                            <div class="ro-header-item"><span class="ro-header-label">Phone:</span> <span class="ro-header-value">${ro.phone || '-'}</span></div>
                            <div class="ro-header-item"><span class="ro-header-label">Vehicle:</span> <span class="ro-header-value">${ro.vehicle || '-'}</span></div>
                            <div class="ro-header-item"><span class="ro-header-label">VIN:</span> <span class="ro-header-value">${ro.vin || '-'}</span></div>
                        </div>
                        <div style="display:grid; grid-template-columns:repeat(5, minmax(0, 1fr)); gap:16px; align-items:center;">
                            <div class="ro-header-item"><span class="ro-header-label">Insurance:</span> <span class="ro-header-value">${insuranceHeaderValue}</span></div>
                            <div class="ro-header-item"><span class="ro-header-label">Claim#:</span> <span class="ro-header-value">${ro.claim_number || '-'}</span></div>
                            <div class="ro-header-item ro-header-date-row">
                                <span class="ro-header-label">In Date:</span>
                                <span id="roHeaderInDateDisplay" class="ro-header-date-display">${inDateDisplay}</span>
                                <input type="date" id="roHeaderInDate" class="ro-header-date-input" value="${inDateValue}" data-field="in_date" data-ro="${ro.ro || ''}" />
                            </div>
                            <div class="ro-header-item ro-header-date-row">
                                <span class="ro-header-label">ECD Date:</span>
                                <span id="roHeaderEcdDateDisplay" class="ro-header-date-display">${ecdDateDisplay}</span>
                                <input type="date" id="roHeaderEcdDate" class="ro-header-date-input" value="${ecdDateValue}" data-field="ecd_date" data-ro="${ro.ro || ''}" />
                            </div>
                            <div class="ro-header-item ro-header-date-row">
                                <span class="ro-header-label">Pick Up Date:</span>
                                <span id="roHeaderPickedUpDateDisplay" class="ro-header-date-display">${pickedUpDateDisplay}</span>
                                <input type="date" id="roHeaderPickedUpDate" class="ro-header-date-input" value="${pickedUpDateValue}" data-field="picked_up" data-ro="${ro.ro || ''}" />
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const contentHtml = `
                <div id="roWindowContent" style="padding:32px; min-height:180px; background:#fff; color:#23272a; font-size:18px; flex:1 1 auto; overflow:auto;">(Content area)</div>
            `;

            // Open new window
            const win = window.open('', `RO_Window_${ro.ro}`, 'width=900,height=600,scrollbars=yes,resizable=yes');
            if (!win) {
                alert('Popup blocked. Please allow popups for this site.');
                return;
            }
            win.document.title = `RO Window - ${ro.ro}`;
            win.document.body.innerHTML = `<div id='roPopupRoot' style='display:flex; flex-direction:column; height:100vh; width:100vw; background:#f2f2f2; overflow:hidden;'>${bannerHtml}<div id='roPopupLowerLayout' style='display:flex; flex:1 1 auto; min-height:0;'>${sidebarHtml}<div style='flex:1 1 auto; min-width:0; display:flex; flex-direction:column; min-height:0;'>${contentHtml}</div></div></div>`;
            // Add styles for sidebar and icons
            const style = win.document.createElement('style');
            style.textContent = `
                body { margin:0; font-family:Segoe UI,Arial,sans-serif; background:#f2f2f2; }
                #roSidebar svg { display:block; margin:0 auto; }
                #roSidebar .ro-sidebar-btn { opacity:0.72; transition:opacity 0.15s ease, transform 0.15s ease; width:100%; display:flex; align-items:center; justify-content:center; }
                #roSidebar .ro-sidebar-btn:hover { opacity:1; transform:translateY(-1px); }
                #roSidebar .ro-sidebar-btn.active { opacity:1; }
                #roSidebar { box-shadow:2px 0 8px rgba(0,0,0,0.08); min-height:0; flex-shrink:0; }
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
                .ro-header-item { font-size:15px; line-height:1.25; min-width:0; }
                .ro-header-label { color:#d32f2f; font-weight:700; margin-right:6px; white-space:nowrap; }
                .ro-header-value { color:#fff; font-weight:600; word-break:break-word; }
                .ro-header-date-row { display:flex; align-items:center; gap:8px; }
                .ro-header-date-display {
                    color:#fff;
                    font-weight:600;
                    cursor:pointer;
                    text-decoration:underline;
                    text-underline-offset:2px;
                    white-space:nowrap;
                }
                .ro-header-date-input {
                    display:none;
                    height:30px;
                    min-width:146px;
                    width:146px;
                    border:1px solid #d0d0d0;
                    border-radius:4px;
                    background:#fff;
                    color:#111;
                    padding:2px 6px;
                    font-size:14px;
                    cursor:pointer;
                }
                .ro-header-date-input.editing { display:inline-block; }
                .ro-header-date-input:focus {
                    outline:2px solid rgba(178,34,34,0.35);
                    box-shadow:none;
                }
                .ro-sidebar-action {
                    opacity: 0.9;
                }
                .ro-sidebar-action:hover {
                    opacity: 1;
                    transform: translateY(-1px);
                }
                                @keyframes roCloseWarnBlink {
                                        0%, 49% { opacity: 1; }
                                        50%, 100% { opacity: 0.25; }
                                }
                                .ro-window-card { background:#fafafa; border:1px solid #ddd; border-radius:8px; padding:14px; }
                .dashboard-ro-table-wrap {
                    background:#ffffff;
                    border-radius:4px;
                    overflow:hidden;
                }
                .dashboard-header-row th,
                .dashboard-header-cell {
                    font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;
                    font-size:15px;
                    font-weight:600;
                    background:rgba(0,0,0,0.03) !important;
                    color:#000000;
                    border:none !important;
                    border-bottom:1px solid #b22222 !important;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08);
                }
                @media (max-width: 700px) {
                                    #roSidebar { flex-basis:44px; }
                  #roSidebar svg { width:22px; height:22px; }
                }
            `;
            win.document.head.appendChild(style);

            const roWindowDoc = win.document;
            const roWindowContentEl = roWindowDoc.getElementById('roWindowContent');
            const popupState = {
                activeView: '',
                techLineItems: [],
                techSelectedIndices: [],
                techAssignContext: null,
                techAssignLines: [],
                techAssignManualLines: [],
                techAssignNextManualId: 1,
                roPrintTechOptions: []
            };

            function escapePopupHtml(value) {
                return String(value === null || value === undefined ? '' : value)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }

            function popupFormatMoney(value) {
                const amount = Number(value || 0);
                return '$' + amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }

            function popupFormatDateTime(value) {
                if (!value) return '-';
                const parsed = new Date(value);
                if (Number.isNaN(parsed.getTime())) return String(value);
                return parsed.toLocaleString();
            }

            function popupFormatDate(value) {
                if (!value) return '-';
                if (/^\d{4}-\d{2}-\d{2}$/.test(String(value))) {
                    const parts = String(value).split('-');
                    return `${parts[1]}/${parts[2]}/${parts[0]}`;
                }
                return popupFormatDateTime(value);
            }

            function buildPrintHeaderHtml() {
                return '';
            }

            function extractPartNumberAndDescription(rawDescription, explicitPartNumber) {
                const source = String(rawDescription || '').trim();
                const explicit = String(explicitPartNumber || '').trim();
                if (!source) return { description: '', partNumber: explicit };

                const tokens = source.split(/\s+/);
                const kept = [];
                let extractedPartNumber = explicit;

                function cleanToken(token) {
                    return String(token || '').trim().replace(/^[\[\](){},;:]+|[\[\](){},;:]+$/g, '');
                }

                function looksLikePartNumber(token) {
                    const cleaned = cleanToken(token);
                    if (!cleaned) return false;
                    if (!/^[A-Za-z0-9-]{5,}$/.test(cleaned)) return false;
                    const hasLetter = /[A-Za-z]/.test(cleaned);
                    const hasDigit = /\d/.test(cleaned);
                    return hasLetter && hasDigit;
                }

                tokens.forEach((token) => {
                    if (looksLikePartNumber(token)) {
                        if (!extractedPartNumber) {
                            extractedPartNumber = cleanToken(token).toUpperCase();
                        }
                        return;
                    }
                    kept.push(cleanToken(token));
                });

                const alphaOnlyDescription = kept
                    .filter((token) => token && !/\d/.test(token))
                    .map((token) => token.replace(/[^A-Za-z]/g, ''))
                    .filter((token) => token)
                    .join(' ')
                    .replace(/\s+/g, ' ')
                    .trim();

                return {
                    description: alphaOnlyDescription,
                    partNumber: extractedPartNumber,
                };
            }

            function normalizeTypeLabelLocal(typeValue) {
                const value = String(typeValue || '').toLowerCase();
                if (value === 'labor') return 'body';
                if (value === 'body' || value === 'paint' || value === 'mech' || value === 'frame') return value;
                return value || '?';
            }

            async function popupFetchJson(url, options = {}) {
                const response = await fetch(url, {
                    credentials: 'include',
                    cache: 'no-store',
                    ...options,
                });
                const payload = await response.json();
                if (!response.ok || payload.error) {
                    throw new Error(payload.error || 'Request failed');
                }
                return payload;
            }

            function popupToNumber(value, fallback = 0) {
                const parsed = Number(value);
                return Number.isFinite(parsed) ? parsed : fallback;
            }

            function popupExtractLineNumber(value) {
                if (value === null || value === undefined) return null;
                const text = String(value);
                const match = text.match(/\d+/);
                if (!match) return null;
                const parsed = Number(match[0]);
                return Number.isFinite(parsed) ? parsed : null;
            }

            function popupNormalizeDisplayNumber(value) {
                const numeric = popupToNumber(value, 0);
                return Number.isInteger(numeric)
                    ? String(numeric)
                    : numeric.toFixed(2).replace(/\.00$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
            }

            function popupBuildUnifiedLinesFromSections(sectionList) {
                const byLine = new Map();

                function getLineRecord(lineNumber) {
                    if (!byLine.has(lineNumber)) {
                        byLine.set(lineNumber, {
                            lineNumber,
                            description: '',
                            labor: 0,
                            paint: 0,
                            qty: null,
                            partNumber: '',
                            extendedPrice: null,
                        });
                    }
                    return byLine.get(lineNumber);
                }

                (Array.isArray(sectionList) ? sectionList : []).forEach((section) => {
                    const sectionKey = String(section?.key || '').toLowerCase();
                    const items = Array.isArray(section?.items) ? section.items : [];
                    items.forEach((item) => {
                        const lineNumber = popupExtractLineNumber(item?.line ?? item?.lineNumber);
                        if (lineNumber === null) return;

                        const record = getLineRecord(lineNumber);
                        const desc = String(item?.description || '').trim();
                        if (desc && !record.description) {
                            record.description = desc;
                        }

                        if (sectionKey === 'labor') {
                            record.labor = popupToNumber(item?.value, 0);
                            return;
                        }
                        if (sectionKey === 'paint') {
                            record.paint = popupToNumber(item?.value, 0);
                            return;
                        }
                        if (sectionKey === 'parts') {
                            const qtyRaw = item?.qty;
                            if (qtyRaw !== null && qtyRaw !== undefined && String(qtyRaw).trim() !== '') {
                                record.qty = popupToNumber(qtyRaw, 0);
                            }
                            const partNumber = String(
                                item?.partNumber || item?.part_number || item?.part_no || item?.['part#'] || item?.pn || ''
                            ).trim();
                            if (partNumber) {
                                record.partNumber = partNumber;
                            }
                            const extPriceRaw = item?.extendedPrice ?? item?.price;
                            if (extPriceRaw !== null && extPriceRaw !== undefined && String(extPriceRaw).trim() !== '') {
                                record.extendedPrice = popupToNumber(extPriceRaw, 0);
                            }
                        }
                    });
                });

                return Array.from(byLine.values()).sort((a, b) => a.lineNumber - b.lineNumber);
            }

            function popupGetUnifiedEstimateLines(estimate) {
                const unified = Array.isArray(estimate?.unified_lines)
                    ? [...estimate.unified_lines].sort((a, b) => popupToNumber(a?.lineNumber, 0) - popupToNumber(b?.lineNumber, 0))
                    : popupBuildUnifiedLinesFromSections(Array.isArray(estimate?.sections) ? estimate.sections : []);
                return unified;
            }

            function roTogglePrintPopup(panel) {
                if (!panel) return;
                const isOpen = panel.classList.contains('open');
                roWindowDoc.querySelectorAll('.mini-popup-panel.open').forEach((openPanel) => {
                    openPanel.classList.remove('open');
                    openPanel.style.display = 'none';
                });
                if (!isOpen) {
                    panel.style.display = 'block';
                    panel.classList.add('open');
                }
            }

            function roClosePrintOptionsModal() {
                const panel = roWindowDoc.getElementById('roPrintOptionsModal');
                if (!panel) return;
                panel.classList.remove('open');
                panel.style.display = 'none';
                const wrap = roWindowDoc.getElementById('roPrintServiceOrderWrap');
                if (wrap) wrap.style.display = 'none';
            }

            function roOpenPrintWindow(title, bodyHtml, options = {}) {
                const printWindow = window.open('', '_blank');
                if (!printWindow) {
                    alert('Unable to open print preview. Please allow pop-ups for this site.');
                    return;
                }
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>${escapePopupHtml(title)}</title>
                            <style>
                                @media print { @page { margin: 0.5in; } body { margin: 0; } }
                                body { font-family: Arial, sans-serif; color:#222; padding:20px; }
                                .header { text-align:center; margin-bottom:16px; border-bottom:2px solid #b22222; padding-bottom:8px; }
                                .header h1 { margin:0 0 6px 0; color:#b22222; font-size:24px; }
                                .header p { margin:0; color:#666; }
                                table { width:100%; border-collapse:collapse; margin-top:10px; }
                                thead th { background:#3c4142; color:#fff; text-align:left; padding:8px; font-size:12px; }
                                tbody td { padding:8px; border-bottom:1px solid #eee; font-size:12px; }
                                .num { text-align:right; }
                                .line-break { height:1px; background:#444; margin:14px 0; }
                            </style>
                        </head>
                        <body>${bodyHtml}</body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                if (options && options.immediatePrint) {
                    printWindow.print();
                    return;
                }
                setTimeout(() => printWindow.print(), 250);
            }

            async function roPrintBill() {
                roClosePrintOptionsModal();
                try {
                    const printHeaderHtml = buildPrintHeaderHtml();
                    const res = await popupFetchJson(`/api/ro-estimate?ro=${encodeURIComponent(ro.ro)}`);
                    const estimate = res.estimate || {};
                    const lines = popupGetUnifiedEstimateLines(estimate);

                    const linesHtml = lines.map((line) => {
                        const lineNumber = popupToNumber(line?.lineNumber, 0);
                        const description = escapePopupHtml(String(line?.description || '').trim() || '-');
                        const partNumber = escapePopupHtml(String(line?.partNumber || '').trim() || '-');
                        const qty = line?.qty;
                        const qtyDisplay = qty === null || qty === undefined || String(qty).trim() === '' ? '-' : popupNormalizeDisplayNumber(qty);
                        const labor = popupNormalizeDisplayNumber(line?.labor || 0);
                        const paint = popupNormalizeDisplayNumber(line?.paint || 0);
                        const price = (line?.extendedPrice === null || line?.extendedPrice === undefined || String(line?.extendedPrice).trim() === '')
                            ? '-'
                            : popupNormalizeDisplayNumber(line?.extendedPrice);
                        return `
                            <tr>
                                <td>${escapePopupHtml(lineNumber)}</td>
                                <td>${description}</td>
                                <td>${partNumber}</td>
                                <td class="num">${escapePopupHtml(qtyDisplay)}</td>
                                <td class="num">${escapePopupHtml(labor)}</td>
                                <td class="num">${escapePopupHtml(paint)}</td>
                                <td class="num">${escapePopupHtml(price)}</td>
                            </tr>
                        `;
                    }).join('');

                    const grandTotal = popupToNumber(ro.total || ro.grand_total || 0);
                    const insuranceDueRaw = popupToNumber(ro.insurance_pay || 0);
                    const customerDueRaw = popupToNumber(ro.customer_pay || 0);
                    const insuranceDue = insuranceDueRaw > 0 ? insuranceDueRaw : 0;
                    const customerDue = customerDueRaw > 0 ? customerDueRaw : Math.max(0, grandTotal - insuranceDue);

                    roOpenPrintWindow(
                        `RO ${ro.ro} Bill`,
                        `
                            <div class="header" style="text-align:left; position:relative; min-height:170px;">
                                ${printHeaderHtml}
                                <div style="font-size:72px; font-weight:800; line-height:1; margin-bottom:8px;">RO #${escapePopupHtml(ro.ro || '-')}</div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:6px;">
                                    <div style="font-size:24px; font-weight:600;">Vehicle: ${escapePopupHtml(ro.vehicle || '-')}</div>
                                    <div style="font-size:32px; font-weight:800; letter-spacing:1px;">INVOICE</div>
                                </div>
                                <div style="font-size:24px; font-weight:600;">VIN: ${escapePopupHtml(ro.vin || '-')}</div>
                            </div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; font-size:13px;">
                                <div>
                                    <div style="font-size:26px;"><strong>Customer:</strong> ${escapePopupHtml(ro.customer || '-')}</div>
                                    <div style="font-size:26px;"><strong>Phone:</strong> ${escapePopupHtml(ro.phone || '-')}</div>
                                </div>
                                <div>
                                    <div style="font-size:26px;"><strong>Insurance:</strong> ${escapePopupHtml(ro.insurance || '-')}</div>
                                    <div style="font-size:26px;"><strong>RO Info:</strong> In ${escapePopupHtml(popupFormatDate(ro.in_date))} | ECD ${escapePopupHtml(popupFormatDate(ro.ecd_date))} | Picked Up ${escapePopupHtml(popupFormatDate(ro.picked_up))}</div>
                                </div>
                            </div>
                            <div class="line-break"></div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Line #</th>
                                        <th>Description</th>
                                        <th>Part #</th>
                                        <th class="num">Qty</th>
                                        <th class="num">Labor</th>
                                        <th class="num">Paint</th>
                                        <th class="num">Price</th>
                                    </tr>
                                </thead>
                                <tbody>${linesHtml || '<tr><td colspan="7" style="text-align:center; color:#777;">No repair lines found.</td></tr>'}</tbody>
                            </table>
                            <div style="margin-top:16px; display:flex; justify-content:flex-end;">
                                <div style="min-width:360px; font-size:13px;">
                                    <div style="display:flex; justify-content:space-between; padding:4px 0;"><span><strong>Grand Total Due</strong></span><span><strong>${popupFormatMoney(grandTotal)}</strong></span></div>
                                    <div style="display:flex; justify-content:space-between; padding:4px 0;"><span>Total Due from Insurance</span><span>${popupFormatMoney(insuranceDue)}</span></div>
                                    <div style="display:flex; justify-content:space-between; padding:4px 0;"><span>Total Due from Customer</span><span>${popupFormatMoney(customerDue)}</span></div>
                                </div>
                            </div>
                        `
                    );
                } catch (error) {
                    console.error('Error printing bill:', error);
                    alert('Unable to generate Bill print.');
                }
            }

            async function roOpenServiceOrderSelector() {
                const wrap = roWindowDoc.getElementById('roPrintServiceOrderWrap');
                const selectEl = roWindowDoc.getElementById('roPrintTechSelect');
                if (!wrap || !selectEl) return;
                wrap.style.display = 'block';
                try {
                    const data = await popupFetchJson(`/api/ro-tech-lines?ro=${encodeURIComponent(ro.ro)}`);
                    const options = (Array.isArray(data.tech_lines) ? data.tech_lines : [])
                        .filter((item) => String(item.mode || '').toLowerCase() === 'tech' && item.tech_id);

                    popupState.roPrintTechOptions = options;
                    selectEl.innerHTML = '<option value="all">All Techs</option>';
                    options.forEach((item) => {
                        const option = roWindowDoc.createElement('option');
                        option.value = String(item.tech_id);
                        option.textContent = `${item.tech || `Tech #${item.tech_id}`}`;
                        selectEl.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading tech selector:', error);
                    selectEl.innerHTML = '<option value="all">All Techs</option>';
                    popupState.roPrintTechOptions = [];
                }
            }

            async function roPrintServiceOrderSelected() {
                const selectEl = roWindowDoc.getElementById('roPrintTechSelect');
                if (!selectEl) return;
                const selectedValue = String(selectEl.value || 'all');
                roClosePrintOptionsModal();

                try {
                    const printHeaderHtml = buildPrintHeaderHtml();
                    let targets = popupState.roPrintTechOptions || [];
                    if (selectedValue !== 'all') {
                        targets = targets.filter((item) => String(item.tech_id) === selectedValue);
                    }

                    if (!targets.length) {
                        alert('No tech lines available for Service Order.');
                        return;
                    }

                    const sectionsByTech = new Map();
                    for (const target of targets) {
                        const techName = String(target.tech_name || target.tech || '').trim();
                        const repairType = normalizeTypeLabelLocal(target.repair_type || target.type || 'body');
                        if (!techName) continue;

                        const query = new URLSearchParams({
                            ro: ro.ro,
                            mode: 'tech',
                            repair_type: repairType,
                            tech_name: techName,
                        });
                        const details = await popupFetchJson(`/api/ro-assignment-lines?${query.toString()}`);
                        const lines = Array.isArray(details.lines) ? details.lines : [];

                        if (!sectionsByTech.has(techName)) {
                            sectionsByTech.set(techName, []);
                        }
                        const targetLines = sectionsByTech.get(techName);
                        lines.forEach((line) => {
                            targetLines.push({
                                line_number: line.line_number || line.line_key || '-',
                                description: line.description || '-',
                                repair_type: normalizeTypeLabelLocal(line.repair_type || repairType),
                                hours: popupToNumber(line.hours || 0),
                            });
                        });
                    }

                    const sections = Array.from(sectionsByTech.entries()).map(([techName, techLines]) => {
                        const sortedLines = [...techLines].sort((a, b) => {
                            const aNum = popupExtractLineNumber(a.line_number);
                            const bNum = popupExtractLineNumber(b.line_number);
                            if (aNum === null && bNum === null) return 0;
                            if (aNum === null) return 1;
                            if (bNum === null) return -1;
                            return aNum - bNum;
                        });

                        const rowsHtml = sortedLines.map((line) => `
                            <tr>
                                <td>${escapePopupHtml(line.line_number || '-')}</td>
                                <td>${escapePopupHtml(line.description || '-')}</td>
                                <td>${escapePopupHtml(normalizeTypeLabelLocal(line.repair_type || ''))}</td>
                                <td class="num">${popupToNumber(line.hours || 0).toFixed(1)}</td>
                            </tr>
                        `).join('');

                        return `
                            <div style="margin-top:18px;">
                                <div style="font-size:16px; font-weight:700; margin-bottom:6px;">${escapePopupHtml(techName)}</div>
                                <table>
                                    <thead>
                                        <tr><th>Line</th><th>Description</th><th>Type</th><th class="num">HRS</th></tr>
                                    </thead>
                                    <tbody>${rowsHtml || '<tr><td colspan="4" style="text-align:center; color:#777;">No lines assigned.</td></tr>'}</tbody>
                                </table>
                            </div>
                        `;
                    });

                    const totalAllHours = Array.from(sectionsByTech.values())
                        .reduce((sum, lines) => sum + lines.reduce((lineSum, line) => lineSum + popupToNumber(line.hours, 0), 0), 0);
                    const totalFooterHtml = `
                        <div style="margin-top:16px; display:flex; justify-content:flex-end; font-size:14px; font-weight:700;">
                            <div>Total Repair Line Hours: ${totalAllHours.toFixed(1)}</div>
                        </div>
                    `;

                    const estimatorRaw = String(getRoEstimatorDisplay(ro) || '-').trim();
                    const estimatorClean = estimatorRaw.replace(/\s*\(estimator\s*\/\s*written by\)\s*$/i, '').trim() || estimatorRaw;
                    const estimatorText = escapePopupHtml(estimatorClean || '-');
                    const insuranceText = escapePopupHtml(ro.insurance || '-');
                    const vehicleText = escapePopupHtml(ro.vehicle || '-');
                    const vinText = escapePopupHtml(ro.vin || '-');

                    roOpenPrintWindow(
                        `RO ${ro.ro} Service Order`,
                        `
                            <div class="header" style="text-align:left; position:relative; min-height:170px;">
                                ${printHeaderHtml}
                                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:18px; margin-bottom:6px;">
                                    <div style="font-size:72px; font-weight:800; line-height:1; margin-bottom:8px;">RO #${escapePopupHtml(ro.ro || '-')}</div>
                                    <div style="text-align:right;">
                                        <div style="font-size:32px; font-weight:800; letter-spacing:1px;">SERVICE ORDER</div>
                                        <div style="font-size:22px; font-weight:600; margin-top:4px;">Estimator: ${estimatorText}</div>
                                        <div style="font-size:22px; font-weight:600; margin-top:4px;">Insurance: ${insuranceText}</div>
                                    </div>
                                </div>
                                <div style="font-size:24px; font-weight:600; margin-bottom:4px;">Vehicle: ${vehicleText}</div>
                                <div style="font-size:24px; font-weight:600;">VIN: ${vinText}</div>
                            </div>
                            ${sections.join('')}
                            ${totalFooterHtml}
                        `
                    );
                } catch (error) {
                    console.error('Error printing service order:', error);
                    alert('Unable to generate Service Order print.');
                }
            }

            async function roPrintParts() {
                roClosePrintOptionsModal();
                try {
                    const printHeaderHtml = buildPrintHeaderHtml();
                    const [linesRes, onOrderRes, arrivedRes, returnedRes, receivedRes] = await Promise.all([
                        popupFetchJson(`/api/parts/ro-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/on-order-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/arrived-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/returned-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/received?ro=${encodeURIComponent(ro.ro)}`),
                    ]);

                    const lines = Array.isArray(linesRes.lines) ? linesRes.lines : [];
                    const onOrder = Array.isArray(onOrderRes.items) ? onOrderRes.items : [];
                    const arrived = Array.isArray(arrivedRes.items) ? arrivedRes.items : [];
                    const returned = Array.isArray(returnedRes.items) ? returnedRes.items : [];
                    const received = Array.isArray(receivedRes.items) ? receivedRes.items : [];

                    const arrivedSet = new Set(arrived.map((item) => Number(item.line_id)));
                    const returnedSet = new Set(returned.map((item) => Number(item.line_id)));
                    const onOrderSet = new Set(onOrder.map((item) => Number(item.line_id)));

                    const partNumberByLine = new Map();
                    const vendorByLine = new Map();
                    const etaByLine = new Map();
                    const listByLine = new Map();
                    const costByLine = new Map();

                    [...onOrder, ...arrived, ...returned, ...received].forEach((entry) => {
                        const lineId = Number(entry.line_id);
                        if (!Number.isFinite(lineId) || lineId <= 0) return;
                        const partNumber = String(entry.part_number || '').trim();
                        const vendor = String(entry.vendor || '').trim();
                        const eta = String(entry.eta || entry.arrival_date || '').trim();
                        const listVal = Number(entry.list);
                        const costVal = Number(entry.cost);

                        if (partNumber && !partNumberByLine.has(lineId)) partNumberByLine.set(lineId, partNumber);
                        if (vendor && !vendorByLine.has(lineId)) vendorByLine.set(lineId, vendor);
                        if (eta && !etaByLine.has(lineId)) etaByLine.set(lineId, eta);
                        if (Number.isFinite(listVal) && !listByLine.has(lineId)) listByLine.set(lineId, listVal);
                        if (Number.isFinite(costVal) && !costByLine.has(lineId)) costByLine.set(lineId, costVal);
                    });

                    const rowsHtml = lines.map((line) => {
                        const idNum = Number(line.id);
                        const extracted = extractPartNumberAndDescription(
                            line.description || '',
                            line.part_number || partNumberByLine.get(idNum) || ''
                        );
                        const cleanDescription = extracted.description || '—';
                        const linePartNumber = String(extracted.partNumber || '').trim();
                        const lineList = Number.isFinite(Number(listByLine.get(idNum)))
                            ? Number(listByLine.get(idNum))
                            : Number(line.price || 0);
                        const lineCost = Number.isFinite(Number(costByLine.get(idNum))) ? Number(costByLine.get(idNum)) : null;
                        const lineVendor = String(vendorByLine.get(idNum) || '').trim();
                        const lineEtaRaw = String(etaByLine.get(idNum) || '').trim();
                        const lineEta = lineEtaRaw ? popupFormatDate(lineEtaRaw) : '—';
                        const isOnOrder = onOrderSet.has(idNum) || !!line.is_ordered;
                        const isArrived = arrivedSet.has(idNum);
                        const isReturned = returnedSet.has(idNum);

                        return `
                            <tr>
                                <td>${escapePopupHtml(line.line || '-')}</td>
                                <td>${escapePopupHtml(cleanDescription)}</td>
                                <td>${escapePopupHtml(linePartNumber || '-')}</td>
                                <td class="num">${popupFormatMoney(lineList)}</td>
                                <td class="num">${lineCost === null ? '—' : popupFormatMoney(lineCost)}</td>
                                <td class="num">${escapePopupHtml(line.qty || 0)}</td>
                                <td>${escapePopupHtml(lineVendor || '-')}</td>
                                <td>${escapePopupHtml(lineEta)}</td>
                                <td style="text-align:center;">${isOnOrder ? 'Yes' : '—'}</td>
                                <td style="text-align:center;">${isArrived ? 'Yes' : '—'}</td>
                                <td style="text-align:center;">${isReturned ? 'Yes' : '—'}</td>
                            </tr>
                        `;
                    }).join('');

                    const vehicleText = escapePopupHtml(ro.vehicle || '-');
                    const vinText = escapePopupHtml(ro.vin || '-');
                    const techAssignedText = escapePopupHtml(ro.tech || '-');

                    roOpenPrintWindow(
                        `RO ${ro.ro} Parts`,
                        `
                            <div class="header" style="text-align:left; position:relative; min-height:170px;">
                                ${printHeaderHtml}
                                <div style="font-size:72px; font-weight:800; line-height:1; margin-bottom:8px;">RO #${escapePopupHtml(ro.ro || '-')}</div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:6px;">
                                    <div style="font-size:24px; font-weight:600;">Vehicle: ${vehicleText}</div>
                                    <div style="text-align:right;">
                                        <div style="font-size:32px; font-weight:800; letter-spacing:1px;">PARTS</div>
                                        <div style="font-size:24px; font-weight:600; margin-top:4px;">TECH ASSIGNED: ${techAssignedText}</div>
                                    </div>
                                </div>
                                <div style="font-size:24px; font-weight:600;">VIN: ${vinText}</div>
                            </div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Line</th><th>Description</th><th>Part #</th><th class="num">List</th><th class="num">Cost</th><th class="num">QTY</th><th>Vendor</th><th>ETA</th><th style="text-align:center;">On Order</th><th style="text-align:center;">Arrived</th><th style="text-align:center;">Returned</th>
                                    </tr>
                                </thead>
                                <tbody>${rowsHtml || '<tr><td colspan="11" style="text-align:center; color:#777;">No parts lines found.</td></tr>'}</tbody>
                            </table>
                        `,
                        { immediatePrint: true }
                    );
                } catch (error) {
                    console.error('Error printing parts:', error);
                    alert('Unable to generate Parts print.');
                }
            }

            function roPrintServiceTag() {
                roClosePrintOptionsModal();
                const checkpoints = [
                    'Parts Verified',
                    'Bodywork Passed',
                    'Primer / Prep Passed',
                    'Paint Passed',
                    'Re-Assembly Passed',
                    'QC Fit / Finish / Functions OK',
                ];
                const checksHtml = checkpoints.map((item) => `
                    <div style="display:grid; grid-template-columns:1.4fr 1fr 1fr; gap:20px; align-items:end; margin-bottom:16px; font-size:15px;">
                        <div>${escapePopupHtml(item)}</div>
                        <div style="border-bottom:1px solid #333; min-height:24px;"><span style="font-size:11px; color:#666;">Date</span></div>
                        <div style="border-bottom:1px solid #333; min-height:24px;"><span style="font-size:11px; color:#666;">Signature</span></div>
                    </div>
                `).join('');

                const inDateText = escapePopupHtml(popupFormatDate(ro.in_date));
                const outDateText = escapePopupHtml(popupFormatDate(ro.picked_up));
                const customerText = escapePopupHtml(ro.customer || '-');
                const insuranceText = escapePopupHtml(ro.insurance || '-');
                const vehicleText = escapePopupHtml(ro.vehicle || '-');
                const vinText = escapePopupHtml(ro.vin || '-');

                roOpenPrintWindow(
                    `RO ${ro.ro} Service Tag`,
                    `
                        <div style="height:50vh; display:flex; flex-direction:column; justify-content:center; gap:14px;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                                <div style="font-size:108px; font-weight:800; line-height:1;">RO ${escapePopupHtml(ro.ro || '-')}</div>
                                <div style="font-size:32px; font-weight:700;">IN DATE: ${inDateText}</div>
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-end; font-size:36px; font-weight:600; line-height:1.1;">
                                <div>${customerText}</div>
                                <div>OUT DATE: ${outDateText}</div>
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-end; font-size:34px; font-weight:600; line-height:1.1;">
                                <div>${vehicleText}</div>
                                <div>${insuranceText}</div>
                            </div>
                            <div style="font-size:32px; font-weight:600; line-height:1.1;">${vinText}</div>
                        </div>
                        <div class="line-break"></div>
                        <div style="height:45vh; display:flex; flex-direction:column; justify-content:center; margin-top:12px;">${checksHtml}</div>
                    `
                );
            }

            async function roPrintServiceCover() {
                roClosePrintOptionsModal();
                try {
                    const printData = await popupFetchJson(`/api/ro-print-data?ro=${encodeURIComponent(ro.ro)}`);
                    const inDateText = escapePopupHtml(popupFormatDate(printData?.in_date || ro.in_date));
                    const outDateText = escapePopupHtml(popupFormatDate(ro.picked_up));
                    const customerText = escapePopupHtml(printData?.customer || ro.customer || '-');
                    const insuranceText = escapePopupHtml(printData?.insurance || ro.insurance || '-');
                    const vehicleText = escapePopupHtml(printData?.vehicle || ro.vehicle || '-');
                    const vinText = escapePopupHtml(printData?.vin || ro.vin || '-');
                    const insuranceTotal = popupToNumber(printData?.totals?.insurance_total, popupToNumber(ro.insurance_pay || 0));
                    const customerTotal = popupToNumber(printData?.totals?.customer_total, popupToNumber(ro.customer_pay || 0));

                    const noteLinesHtml = Array.from({ length: 6 }).map(() => `
                        <div style="font-size:18px; margin-bottom:18px; letter-spacing:0.2px;">
                            _____/_____/_______&nbsp;&nbsp;&nbsp;&nbsp;______________________________________________________
                        </div>
                    `).join('');

                    roOpenPrintWindow(
                        `RO ${ro.ro} Service Cover`,
                        `
                            <div style="height:50vh; display:flex; flex-direction:column; justify-content:center; gap:14px;">
                                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                                    <div style="font-size:108px; font-weight:800; line-height:1;">RO ${escapePopupHtml(ro.ro || '-')}</div>
                                    <div style="font-size:32px; font-weight:700;">IN DATE: ${inDateText}</div>
                                </div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-end; font-size:36px; font-weight:600; line-height:1.1;">
                                    <div>${customerText}</div>
                                    <div>OUT DATE: ${outDateText}</div>
                                </div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-end; font-size:34px; font-weight:600; line-height:1.1;">
                                    <div>${vehicleText}</div>
                                    <div>${insuranceText}</div>
                                </div>
                                <div style="font-size:32px; font-weight:600; line-height:1.1;">${vinText}</div>
                            </div>
                            <div class="line-break"></div>
                            <div style="height:45vh; display:flex; flex-direction:column; justify-content:flex-start; margin-top:8px;">
                                <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:16px; margin-bottom:18px; font-size:18px;">
                                    <div><strong>Insurance Total:</strong> ${popupFormatMoney(insuranceTotal)}</div>
                                    <div><strong>Customer Total:</strong> ${popupFormatMoney(customerTotal)}</div>
                                    <div><strong>In Date:</strong> ${inDateText}</div>
                                    <div><strong>Out Date:</strong> ${outDateText}</div>
                                </div>
                                ${noteLinesHtml}
                            </div>
                        `
                    );
                } catch (error) {
                    console.error('Error printing service cover:', error);
                    alert('Unable to generate Service Cover print.');
                }
            }

            function bindRoPrintActions() {
                const trigger = roWindowDoc.getElementById('roPrintTrigger');
                const panel = roWindowDoc.getElementById('roPrintOptionsModal');
                const billBtn = roWindowDoc.getElementById('roPrintOptionBill');
                const serviceOrderBtn = roWindowDoc.getElementById('roPrintOptionServiceOrder');
                const partsBtn = roWindowDoc.getElementById('roPrintOptionParts');
                const serviceTagBtn = roWindowDoc.getElementById('roPrintOptionServiceTag');
                const serviceCoverBtn = roWindowDoc.getElementById('roPrintOptionServiceCover');
                const serviceOrderGoBtn = roWindowDoc.getElementById('roPrintServiceOrderGo');

                if (trigger && panel) {
                    trigger.addEventListener('click', (event) => {
                        event.stopPropagation();
                        roTogglePrintPopup(panel);
                    });
                }
                if (billBtn) billBtn.addEventListener('click', () => { roPrintBill(); });
                if (serviceOrderBtn) serviceOrderBtn.addEventListener('click', async () => { await roOpenServiceOrderSelector(); });
                if (serviceOrderGoBtn) serviceOrderGoBtn.addEventListener('click', async () => { await roPrintServiceOrderSelected(); });
                if (partsBtn) partsBtn.addEventListener('click', () => { roPrintParts(); });
                if (serviceTagBtn) serviceTagBtn.addEventListener('click', () => { roPrintServiceTag(); });
                if (serviceCoverBtn) serviceCoverBtn.addEventListener('click', () => { roPrintServiceCover(); });

                roWindowDoc.addEventListener('click', (event) => {
                    if (!panel || !panel.classList.contains('open')) return;
                    const target = event.target;
                    if ((trigger && trigger.contains(target)) || panel.contains(target)) return;
                    roClosePrintOptionsModal();
                });
            }

            async function patchRoDate(roNumber, field, isoValue) {
                await popupFetchJson('/api/ro-dates', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ro: roNumber, field, value: isoValue }),
                });
            }

            async function saveRoHeaderDateInput(input, errorLabel = 'date') {
                if (!input) return;
                const roNumber = input.dataset.ro || '';
                const field = input.dataset.field || '';
                const nextValue = input.value || '';
                const prevValue = input.dataset.lastValue || '';
                if (!roNumber || !field || !nextValue || nextValue === prevValue) return;
                if (input.dataset.saving === '1') return;

                input.dataset.saving = '1';
                input.disabled = true;
                try {
                    await patchRoDate(roNumber, field, nextValue);
                    input.dataset.lastValue = nextValue;
                    ro[field] = nextValue;
                } catch (error) {
                    console.error('Error updating RO date:', error);
                    input.value = prevValue;
                    alert(`Unable to save ${errorLabel}.`);
                } finally {
                    input.disabled = false;
                    input.dataset.saving = '0';
                }
            }

            function bindDateAutosave(inputId, options = {}) {
                const input = roWindowDoc.getElementById(inputId);
                if (!input) return;
                const errorLabel = options.errorLabel || 'date';
                const display = options.displayId ? roWindowDoc.getElementById(options.displayId) : null;
                input.dataset.lastValue = input.value || '';

                const formatDisplayDate = (value) => {
                    const text = String(value || '').trim();
                    if (!text) return '-';
                    const match = text.match(/^(\d{4})-(\d{2})-(\d{2})$/);
                    if (!match) return text;
                    return `${match[2]}/${match[3]}/${match[1]}`;
                };

                const syncDisplayText = () => {
                    if (!display) return;
                    display.textContent = formatDisplayDate(input.value || input.dataset.lastValue || '');
                };

                const exitEditMode = () => {
                    input.classList.remove('editing');
                    if (display) display.style.display = 'inline';
                    syncDisplayText();
                };

                const enterEditMode = () => {
                    input.classList.add('editing');
                    if (display) display.style.display = 'none';
                    try {
                        input.focus();
                        if (typeof input.showPicker === 'function') {
                            input.showPicker();
                        }
                    } catch (_) {
                    }
                };

                if (display) {
                    display.addEventListener('click', () => {
                        enterEditMode();
                    });
                }

                input.addEventListener('change', async function() {
                    await saveRoHeaderDateInput(this, errorLabel);
                    exitEditMode();
                });

                // Date picker selections fire input as the value changes; save immediately.
                input.addEventListener('input', async function() {
                    await saveRoHeaderDateInput(this, errorLabel);
                });

                input.addEventListener('keydown', async function(event) {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        await saveRoHeaderDateInput(this, errorLabel);
                        exitEditMode();
                        return;
                    }
                    if (event.key === 'Escape') {
                        event.preventDefault();
                        input.value = input.dataset.lastValue || '';
                        exitEditMode();
                    }
                });

                input.addEventListener('blur', async function() {
                    await saveRoHeaderDateInput(this, errorLabel);
                    exitEditMode();
                });

                syncDisplayText();
            }

            function setActiveSidebar(view) {
                roWindowDoc.querySelectorAll('#roSidebar .ro-sidebar-btn').forEach((button) => {
                    if (button.getAttribute('data-view') === view) {
                        button.classList.add('active');
                    } else {
                        button.classList.remove('active');
                    }
                });
            }

            function renderLoading(message) {
                if (!roWindowContentEl) return;
                roWindowContentEl.innerHTML = `<div class="ro-window-card" style="color:#777;">${escapePopupHtml(message || 'Loading...')}</div>`;
            }

            function bindSidebarButtons() {
                roWindowDoc.querySelectorAll('#roSidebar .ro-sidebar-btn').forEach((button) => {
                    button.addEventListener('click', () => {
                        const view = button.getAttribute('data-view') || '';
                        if (view) {
                            showSidebarView(view);
                        }
                    });
                });
            }

            function closeRoConfirmPopover() {
                const panel = roWindowDoc.getElementById('roCloseConfirmPopover');
                if (panel) {
                    panel.remove();
                }
            }

            async function flushHeaderDateInputs() {
                const dateFields = [
                    roWindowDoc.getElementById('roHeaderInDate'),
                    roWindowDoc.getElementById('roHeaderEcdDate'),
                    roWindowDoc.getElementById('roHeaderPickedUpDate'),
                ].filter(Boolean);

                for (const input of dateFields) {
                    const roNumber = input.dataset.ro || '';
                    const field = input.dataset.field || '';
                    const currentValue = input.value || '';
                    const lastValue = input.dataset.lastValue || '';
                    if (!roNumber || !field || !currentValue || currentValue === lastValue) {
                        continue;
                    }
                    await patchRoDate(roNumber, field, currentValue);
                    input.dataset.lastValue = currentValue;
                }
            }

            function openRoConfirmPopover() {
                closeRoConfirmPopover();

                const closeButton = roWindowDoc.getElementById('roCloseButton');
                if (!closeButton) return;

                const panel = roWindowDoc.createElement('div');
                panel.id = 'roCloseConfirmPopover';
                panel.style.position = 'fixed';
                panel.style.width = '300px';
                panel.style.background = '#fff';
                panel.style.border = '1px solid #ccc';
                panel.style.borderRadius = '8px';
                panel.style.boxShadow = '0 8px 22px rgba(0,0,0,0.2)';
                panel.style.padding = '12px';
                panel.style.zIndex = '9000';

                const rect = closeButton.getBoundingClientRect();
                const left = Math.max(10, Math.min(window.innerWidth - 320, rect.right + 10));
                const top = Math.max(10, rect.top - 2);
                panel.style.left = `${left}px`;
                panel.style.top = `${top}px`;

                panel.innerHTML = `
                    <div style="font-size:14px; color:#222; margin-bottom:10px;">You're about to close the RO. Confirm?</div>
                    <div id="roCloseMissingPickupWarning" style="display:none; margin:0 0 10px 0; color:#d32f2f; font-weight:800; animation: roCloseWarnBlink 0.9s linear infinite;">ENTER PICK UP DATE FIRST</div>
                    <div style="display:flex; justify-content:flex-end; gap:8px;">
                        <button id="roCloseConfirmCancel" type="button" style="padding:7px 12px; background:#999; color:#fff; border:none; border-radius:5px; cursor:pointer;">Cancel</button>
                        <button id="roCloseConfirmYes" type="button" style="padding:7px 12px; background:#d32f2f; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:700;">Yes</button>
                    </div>
                `;

                roWindowDoc.body.appendChild(panel);

                const cancelBtn = roWindowDoc.getElementById('roCloseConfirmCancel');
                const yesBtn = roWindowDoc.getElementById('roCloseConfirmYes');
                const warningEl = roWindowDoc.getElementById('roCloseMissingPickupWarning');
                const pickedUpInput = roWindowDoc.getElementById('roHeaderPickedUpDate');

                function syncPickedUpWarning() {
                    const hasPickedUp = !!String(pickedUpInput?.value || '').trim();
                    if (warningEl) {
                        warningEl.style.display = hasPickedUp ? 'none' : 'block';
                    }
                    return hasPickedUp;
                }

                syncPickedUpWarning();
                if (pickedUpInput) {
                    pickedUpInput.addEventListener('input', syncPickedUpWarning);
                    pickedUpInput.addEventListener('change', syncPickedUpWarning);
                }

                if (cancelBtn) {
                    cancelBtn.addEventListener('click', () => {
                        closeRoConfirmPopover();
                    });
                }

                if (yesBtn) {
                    yesBtn.addEventListener('click', async () => {
                        if (!syncPickedUpWarning()) {
                            return;
                        }
                        yesBtn.disabled = true;
                        try {
                            await flushHeaderDateInputs();
                            await popupFetchJson('/api/payments/close-ro', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ ro: ro.ro }),
                            });

                            const closedLabel = roWindowDoc.getElementById('roClosedStatusLabel');
                            if (closedLabel) {
                                closedLabel.style.display = 'block';
                            }

                            closeRoConfirmPopover();

                            if (window.opener && !window.opener.closed) {
                                if (typeof window.opener.loadDashboardData === 'function') {
                                    window.opener.loadDashboardData();
                                }
                            }
                        } catch (error) {
                            console.error('Error closing RO:', error);
                            alert(error.message || 'Unable to close RO.');
                        } finally {
                            yesBtn.disabled = false;
                        }
                    });
                }
            }

            function bindCloseRoButton() {
                const closeButton = roWindowDoc.getElementById('roCloseButton');
                if (!closeButton) return;
                closeButton.addEventListener('click', (event) => {
                    event.stopPropagation();
                    openRoConfirmPopover();
                });

                roWindowDoc.addEventListener('click', (event) => {
                    const panel = roWindowDoc.getElementById('roCloseConfirmPopover');
                    if (!panel) return;
                    const target = event.target;
                    if (panel.contains(target) || target === closeButton) return;
                    closeRoConfirmPopover();
                });
            }

            async function renderNotesView() {
                if (!roWindowContentEl) return;
                roWindowContentEl.innerHTML = `
                    <div class="ro-window-card">
                        <div style="font-weight:700; font-size:18px; margin-bottom:10px; color:#333;">Notes Log</div>
                        <div style="display:flex; gap:10px; margin-bottom:12px; align-items:flex-start;">
                            <textarea id="roPopupNoteInput" rows="3" style="flex:1; padding:10px; border:1px solid #ccc; border-radius:6px; resize:vertical;" placeholder="Add note..."></textarea>
                            <span id="roPopupNoteSave" role="button" aria-label="Save" title="Save" style="display:inline-flex; align-items:center; justify-content:center; width:68px; height:68px; color:#b22222; cursor:pointer;"><svg width="44" height="44" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M5 3h11l3 3v15H5V3z" fill="currentColor"/><rect x="8" y="4" width="8" height="5" fill="#ffffff"/><rect x="8" y="14" width="8" height="6" fill="#ffffff"/></svg></span>
                        </div>
                        <div id="roPopupNotesList" style="max-height:420px; overflow-y:auto;"></div>
                    </div>
                `;

                const listEl = roWindowDoc.getElementById('roPopupNotesList');
                const inputEl = roWindowDoc.getElementById('roPopupNoteInput');
                const saveBtn = roWindowDoc.getElementById('roPopupNoteSave');

                async function loadNotes() {
                    if (!listEl) return;
                    listEl.innerHTML = '<div style="color:#777;">Loading...</div>';
                    try {
                        const res = await popupFetchJson(`/api/ro-notes?ro=${encodeURIComponent(ro.ro)}`);
                        const notes = Array.isArray(res.notes) ? res.notes : [];
                        if (!notes.length) {
                            listEl.innerHTML = '<div style="color:#999;">No notes yet.</div>';
                            return;
                        }
                        listEl.innerHTML = notes.map((note) => {
                            const when = popupFormatDateTime(note.created_at);
                            const who = escapePopupHtml(note.created_by || 'Unknown');
                            const text = escapePopupHtml(note.note || '');
                            return `
                                <div style="padding:10px 0; border-bottom:1px solid #eee;">
                                    <div style="font-size:12px; color:#666; margin-bottom:4px;">${escapePopupHtml(when)} • ${who}</div>
                                    <div style="white-space:pre-wrap; color:#222;">${text}</div>
                                </div>
                            `;
                        }).join('');
                    } catch (error) {
                        console.error('Error loading notes:', error);
                        listEl.innerHTML = '<div style="color:#c62828;">Error loading notes.</div>';
                    }
                }

                if (saveBtn && inputEl) {
                    saveBtn.addEventListener('click', async () => {
                        const noteText = String(inputEl.value || '').trim();
                        if (!noteText) return;
                        saveBtn.disabled = true;
                        try {
                            await popupFetchJson('/api/ro-notes', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ ro: ro.ro, note: noteText }),
                            });
                            inputEl.value = '';
                            await loadNotes();
                        } catch (error) {
                            console.error('Error saving note:', error);
                            alert('Error saving note.');
                        } finally {
                            saveBtn.disabled = false;
                        }
                    });
                }

                await loadNotes();
            }

            async function renderEstimateView() {
                if (!roWindowContentEl) return;
                roWindowContentEl.innerHTML = '<div id="roPopupEstimateContent" style="color:#444;"><div style="color:#777;">Loading...</div></div>';

                const contentEl = roWindowDoc.getElementById('roPopupEstimateContent');
                if (!contentEl) return;

                try {
                    const res = await popupFetchJson(`/api/ro-estimate?ro=${encodeURIComponent(ro.ro)}`);
                    const estimate = res.estimate || {};
                    const header = estimate.header || {};
                    const vehicle = header.vehicle || {};
                    const totals = Array.isArray(estimate.totals) ? estimate.totals : [];
                    const sections = Array.isArray(estimate.sections) ? estimate.sections : [];

                    function toNumber(value, fallback = 0) {
                        const parsed = Number(value);
                        return Number.isFinite(parsed) ? parsed : fallback;
                    }

                    function extractLineNumber(value) {
                        if (value === null || value === undefined) return null;
                        const text = String(value);
                        const match = text.match(/\d+/);
                        if (!match) return null;
                        const parsed = Number(match[0]);
                        return Number.isFinite(parsed) ? parsed : null;
                    }

                    function normalizeDisplayNumber(value) {
                        const numeric = toNumber(value, 0);
                        return Number.isInteger(numeric)
                            ? String(numeric)
                            : numeric.toFixed(2).replace(/\.00$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
                    }

                    function buildUnifiedLinesFromSections(sectionList) {
                        const byLine = new Map();

                        function getLineRecord(lineNumber) {
                            if (!byLine.has(lineNumber)) {
                                byLine.set(lineNumber, {
                                    lineNumber,
                                    description: '',
                                    labor: 0,
                                    paint: 0,
                                    qty: null,
                                    partNumber: '',
                                    extendedPrice: null,
                                });
                            }
                            return byLine.get(lineNumber);
                        }

                        sectionList.forEach((section) => {
                            const sectionKey = String(section?.key || '').toLowerCase();
                            const items = Array.isArray(section?.items) ? section.items : [];
                            items.forEach((item) => {
                                const lineNumber = extractLineNumber(item?.line ?? item?.lineNumber);
                                if (lineNumber === null) return;

                                const record = getLineRecord(lineNumber);
                                const desc = String(item?.description || '').trim();
                                if (desc && !record.description) {
                                    record.description = desc;
                                }

                                if (sectionKey === 'labor') {
                                    record.labor = toNumber(item?.value, 0);
                                    return;
                                }
                                if (sectionKey === 'paint') {
                                    record.paint = toNumber(item?.value, 0);
                                    return;
                                }
                                if (sectionKey === 'parts') {
                                    const qtyRaw = item?.qty;
                                    if (qtyRaw !== null && qtyRaw !== undefined && String(qtyRaw).trim() !== '') {
                                        record.qty = toNumber(qtyRaw, 0);
                                    }
                                    const partNumber = String(
                                        item?.partNumber || item?.part_number || item?.part_no || item?.['part#'] || item?.pn || ''
                                    ).trim();
                                    if (partNumber) {
                                        record.partNumber = partNumber;
                                    }
                                    const extPriceRaw = item?.extendedPrice ?? item?.price;
                                    if (extPriceRaw !== null && extPriceRaw !== undefined && String(extPriceRaw).trim() !== '') {
                                        record.extendedPrice = toNumber(extPriceRaw, 0);
                                    }
                                }
                            });
                        });

                        return Array.from(byLine.values()).sort((a, b) => a.lineNumber - b.lineNumber);
                    }

                    const unifiedLines = Array.isArray(estimate.unified_lines)
                        ? [...estimate.unified_lines].sort((a, b) => toNumber(a?.lineNumber, 0) - toNumber(b?.lineNumber, 0))
                        : buildUnifiedLinesFromSections(sections);

                    const ownerInfo = String(header.owner_info || '').trim();

                    const unifiedHtml = unifiedLines.length
                        ? `
                            <div class="dashboard-ro-table-wrap" style="overflow:hidden;">
                                <div style="overflow-x:auto;">
                                    <table style="width:100%; border-collapse:collapse; table-layout:fixed;">
                                        <colgroup>
                                            <col style="width:8%;" />
                                            <col style="width:48%;" />
                                            <col style="width:10%;" />
                                            <col style="width:8%;" />
                                            <col style="width:9%;" />
                                            <col style="width:9%;" />
                                            <col style="width:8%;" />
                                        </colgroup>
                                        <thead>
                                            <tr class="dashboard-header-row">
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:left; white-space:nowrap;">Line #</th>
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:left; white-space:nowrap;">Description</th>
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:left; white-space:nowrap;">Part #</th>
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:right; white-space:nowrap;">Qty</th>
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:right; white-space:nowrap;">Labor</th>
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:right; white-space:nowrap;">Paint</th>
                                                <th class="dashboard-header-cell" style="padding:12px; text-align:right; white-space:nowrap;">Price</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${unifiedLines.map((line) => {
                                                const lineNumber = toNumber(line?.lineNumber, 0);
                                                const description = String(line?.description || '').trim() || '-';
                                                const labor = toNumber(line?.labor, 0);
                                                const paint = toNumber(line?.paint, 0);
                                                const qty = line?.qty;
                                                const partNumber = String(line?.partNumber || '').trim();
                                                const extendedPrice = line?.extendedPrice;

                                                const qtyDisplay = qty === null || qty === undefined || String(qty).trim() === ''
                                                    ? '-'
                                                    : normalizeDisplayNumber(qty);
                                                const partNumberDisplay = partNumber || '-';
                                                const priceDisplay = extendedPrice === null || extendedPrice === undefined || String(extendedPrice).trim() === ''
                                                    ? '-'
                                                    : normalizeDisplayNumber(extendedPrice);

                                                return `
                                                    <tr style="border-bottom:1px solid rgba(0,0,0,0.06); background:#fff;">
                                                        <td style="padding:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapePopupHtml(lineNumber)}</td>
                                                        <td style="padding:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapePopupHtml(description)}</td>
                                                        <td style="padding:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapePopupHtml(partNumberDisplay)}</td>
                                                        <td style="padding:8px; text-align:right; white-space:nowrap;">${escapePopupHtml(qtyDisplay)}</td>
                                                        <td style="padding:8px; text-align:right; white-space:nowrap;">${escapePopupHtml(normalizeDisplayNumber(labor))}</td>
                                                        <td style="padding:8px; text-align:right; white-space:nowrap;">${escapePopupHtml(normalizeDisplayNumber(paint))}</td>
                                                        <td style="padding:8px; text-align:right; white-space:nowrap;">${escapePopupHtml(priceDisplay)}</td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `
                        : '<div style="color:#777;">No estimate lines available.</div>';

                    const totalEntry = totals.find((total) => {
                        const key = String(total?.key || '').trim().toLowerCase();
                        const label = String(total?.label || '').trim().toLowerCase();
                        return (
                            key === 'grand_total' ||
                            key === 'grandtotal' ||
                            label === 'grand total' ||
                            key === 'total' ||
                            label === 'total'
                        );
                    });
                    let estimateTotalDisplay = '-';
                    if (totalEntry?.display) {
                        estimateTotalDisplay = String(totalEntry.display).trim() || '-';
                    } else if (totalEntry && totalEntry.value !== null && totalEntry.value !== undefined && String(totalEntry.value).trim() !== '') {
                        estimateTotalDisplay = `$${normalizeDisplayNumber(totalEntry.value)}`;
                    }

                    contentEl.innerHTML = `
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <div style="font-weight:700; color:#333;">Repair Lines</div>
                            <div style="font-weight:700; color:#333;">Estimate Total: ${escapePopupHtml(estimateTotalDisplay)}</div>
                        </div>
                        ${unifiedHtml}
                    `;
                } catch (error) {
                    console.error('Error loading estimate snapshot:', error);
                    contentEl.innerHTML = '<div style="color:#c62828;">Unable to load estimate snapshot.</div>';
                }
            }

            function renderTechAssignLinesModal(lines) {
                const container = roWindowDoc.getElementById('roPopupTechModalLines');
                if (!container) return;
                const manualLines = Array.isArray(popupState.techAssignManualLines) ? popupState.techAssignManualLines : [];
                if ((!lines || !lines.length) && manualLines.length === 0) {
                    container.innerHTML = '<div style="padding:10px; color:#777;">No repair lines found.</div>';
                    return;
                }
                const sorted = [...lines].sort((a, b) => {
                    const av = parseInt(String(a.line_number || a.line_key || '').match(/\d+/)?.[0] || '0', 10);
                    const bv = parseInt(String(b.line_number || b.line_key || '').match(/\d+/)?.[0] || '0', 10);
                    return av - bv;
                });
                const standardRows = sorted.map((line) => {
                    const lineNumber = escapePopupHtml(line.line_number || line.line_key || '-');
                    const description = escapePopupHtml(String(line.description || '').trim());
                    const lineType = normalizeTypeLabelLocal(line.repair_type);
                    const hours = Number(line.hours || 0).toFixed(1);
                    return `
                        <div style="display:flex; align-items:center; gap:10px; padding:8px 10px; border-bottom:1px solid #eee;">
                            <input type="checkbox" class="roPopupTechLineCheckbox" checked data-line-key="${escapePopupHtml(line.line_key)}" data-repair-type="${escapePopupHtml(lineType)}" data-hours="${escapePopupHtml(hours)}" style="width:16px; height:16px;" />
                            <div style="flex:1; color:#333;">Line ${lineNumber} ${description}</div>
                            <div style="min-width:70px; text-align:right; font-weight:bold;">${hours} hrs</div>
                        </div>
                    `;
                }).join('');

                const manualRows = manualLines.map((line) => {
                    const lineKey = escapePopupHtml(line.line_key || '');
                    const lineType = escapePopupHtml(normalizeTypeLabelLocal(line.repair_type || 'body'));
                    const description = escapePopupHtml(String(line.description || ''));
                    const hours = Number(line.hours || 0);
                    return `
                        <div class="ro-popup-tech-manual-row" data-line-key="${lineKey}" style="display:flex; align-items:center; gap:10px; padding:8px 10px; border-bottom:1px solid #eee; background:#fafafa; font-style:italic;">
                            <input type="checkbox" class="roPopupTechLineCheckbox" checked data-is-manual="1" data-line-key="${lineKey}" data-repair-type="${lineType}" data-hours="${escapePopupHtml(hours.toFixed(1))}" style="width:16px; height:16px;" />
                            <select class="roPopupTechManualPreset" data-line-key="${lineKey}" style="min-width:140px; padding:6px; border:1px solid #ccc; border-radius:4px; font-style:normal;">
                                <option value="">Preset...</option>
                                <option value="LKQ repair" ${description.toLowerCase() === 'lkq repair' ? 'selected' : ''}>LKQ repair</option>
                                <option value="Shop damage" ${description.toLowerCase() === 'shop damage' ? 'selected' : ''}>Shop damage</option>
                                <option value="Reassignment" ${description.toLowerCase() === 'reassignment' ? 'selected' : ''}>Reassignment</option>
                                <option value="Tech change" ${description.toLowerCase() === 'tech change' ? 'selected' : ''}>Tech change</option>
                            </select>
                            <input type="text" class="roPopupTechManualDescription" data-line-key="${lineKey}" value="${description}" placeholder="Description" style="flex:1; padding:6px; border:1px solid #ccc; border-radius:4px; font-style:normal;" />
                            <input type="number" class="roPopupTechManualHours" data-line-key="${lineKey}" min="0" step="0.1" value="${escapePopupHtml(hours.toFixed(1))}" style="width:90px; padding:6px; border:1px solid #ccc; border-radius:4px; text-align:right; font-style:normal;" />
                            <div style="min-width:70px; text-align:right; font-weight:bold;">hrs</div>
                        </div>
                    `;
                }).join('');

                container.innerHTML = `${standardRows}${manualRows}`;

                container.querySelectorAll('.roPopupTechManualPreset').forEach((selectEl) => {
                    selectEl.addEventListener('change', (event) => {
                        const selectTarget = event.currentTarget;
                        const lineKey = selectTarget?.getAttribute('data-line-key') || '';
                        const value = String(selectTarget?.value || '').trim();
                        const descInput = container.querySelector(`.roPopupTechManualDescription[data-line-key="${lineKey}"]`);
                        if (descInput && value) {
                            descInput.value = value;
                        }
                    });
                });
            }

            function addTechAssignManualLinePopup() {
                const lineId = popupState.techAssignNextManualId || 1;
                popupState.techAssignNextManualId = lineId + 1;
                const typeSelect = roWindowDoc.getElementById('roPopupTechType');
                const currentType = normalizeTypeLabelLocal(typeSelect?.value || 'body');
                popupState.techAssignManualLines = Array.isArray(popupState.techAssignManualLines)
                    ? popupState.techAssignManualLines
                    : [];
                popupState.techAssignManualLines.push({
                    line_key: `manual-${lineId}`,
                    repair_type: currentType,
                    description: '',
                    hours: 0,
                });
                renderTechAssignLinesModal(popupState.techAssignLines || []);
            }

            async function openTechAssignModalPopup(item) {
                const modal = roWindowDoc.getElementById('roPopupTechModal');
                const title = roWindowDoc.getElementById('roPopupTechModalTitle');
                const techSelect = roWindowDoc.getElementById('roPopupTechSelect');
                const typeSelect = roWindowDoc.getElementById('roPopupTechType');
                if (!modal || !title || !techSelect || !typeSelect) return;

                const mode = String(item?.mode || '').toLowerCase();
                const sourceType = normalizeTypeLabelLocal(item?.repair_type || item?.type || 'body');
                const sourceTech = String(item?.tech_name || item?.tech || '');

                popupState.techAssignContext = {
                    ro: ro.ro,
                    source: {
                        mode,
                        repair_type: sourceType,
                        tech_name: sourceTech,
                    },
                };
                popupState.techAssignManualLines = [];
                popupState.techAssignNextManualId = 1;

                title.textContent = `Assign Repair Lines - RO# ${ro.ro}`;
                modal.style.display = 'flex';
                renderTechAssignLinesModal([]);

                try {
                    const query = new URLSearchParams({
                        ro: ro.ro,
                        mode,
                        repair_type: sourceType,
                        tech_name: sourceTech,
                    });
                    const res = await popupFetchJson(`/api/ro-assignment-lines?${query.toString()}`);
                    popupState.techAssignLines = Array.isArray(res.lines) ? res.lines : [];

                    const options = ['<option value="">Select tech...</option>'];
                    (res.techs || []).forEach((tech) => {
                        const label = escapePopupHtml(tech.name || `Tech #${tech.id}`);
                        options.push(`<option value="${escapePopupHtml(tech.id)}" data-name="${label}">${label}</option>`);
                    });
                    techSelect.innerHTML = options.join('');
                    if (mode === 'tech' && sourceTech) {
                        const matched = Array.from(techSelect.options).find((opt) => (opt.dataset?.name || '') === sourceTech);
                        if (matched) techSelect.value = matched.value;
                    }
                    typeSelect.value = mode === 'pending' ? 'body' : sourceType;

                    renderTechAssignLinesModal(popupState.techAssignLines);
                } catch (error) {
                    console.error('Error loading assignment lines:', error);
                    renderTechAssignLinesModal([]);
                }
            }

            async function saveTechAssignModalPopup() {
                const context = popupState.techAssignContext;
                if (!context?.ro || !context?.source) return;

                const techSelect = roWindowDoc.getElementById('roPopupTechSelect');
                const typeSelect = roWindowDoc.getElementById('roPopupTechType');
                if (!techSelect || !typeSelect || !techSelect.value) {
                    alert('Please select a tech.');
                    return;
                }

                const selectedLines = Array.from(roWindowDoc.querySelectorAll('.roPopupTechLineCheckbox:checked')).map((checkbox) => {
                    const lineKey = checkbox.getAttribute('data-line-key') || '';
                    const repairType = checkbox.getAttribute('data-repair-type') || 'body';
                    const isManual = checkbox.getAttribute('data-is-manual') === '1';
                    const payload = {
                        repair_type: repairType,
                        line_key: lineKey,
                    };

                    if (isManual) {
                        const descInput = roWindowDoc.querySelector(`.roPopupTechManualDescription[data-line-key="${lineKey}"]`);
                        const hoursInput = roWindowDoc.querySelector(`.roPopupTechManualHours[data-line-key="${lineKey}"]`);
                        payload.is_manual = true;
                        payload.description = String(descInput?.value || '').trim();
                        payload.hours = Number(hoursInput?.value || 0);
                    }

                    return payload;
                }).filter((item) => {
                    if (!item.is_manual) return true;
                    return !!item.description && Number.isFinite(item.hours) && item.hours >= 0;
                });

                if (!selectedLines.length) {
                    alert('Select at least one repair line.');
                    return;
                }

                const techId = parseInt(techSelect.value, 10);
                const techName = techSelect.options[techSelect.selectedIndex]?.dataset?.name || '';

                await popupFetchJson('/api/ro-assignment-save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ro: context.ro,
                        source: context.source,
                        target: {
                            tech_id: Number.isFinite(techId) ? techId : null,
                            tech_name: techName,
                            repair_type: typeSelect.value,
                        },
                        selected_lines: selectedLines,
                    }),
                });

                const modal = roWindowDoc.getElementById('roPopupTechModal');
                if (modal) modal.style.display = 'none';
                await renderTechView();
                loadDashboardData();
            }

            function bindTechModalActions() {
                const closeBtn = roWindowDoc.getElementById('roPopupTechModalClose');
                const saveBtn = roWindowDoc.getElementById('roPopupTechModalSave');
                const addLineBtn = roWindowDoc.getElementById('roPopupTechModalAddLine');
                const modal = roWindowDoc.getElementById('roPopupTechModal');
                if (closeBtn && modal) closeBtn.onclick = () => { modal.style.display = 'none'; };
                if (addLineBtn) {
                    addLineBtn.onclick = () => {
                        addTechAssignManualLinePopup();
                    };
                }
                if (saveBtn) {
                    saveBtn.onclick = async () => {
                        try {
                            await saveTechAssignModalPopup();
                        } catch (error) {
                            console.error('Error saving assignment:', error);
                            alert('Error saving assignments.');
                        }
                    };
                }
            }

            async function renderTechView() {
                if (!roWindowContentEl) return;
                popupState.techSelectedIndices = [];
                roWindowContentEl.innerHTML = `
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:10px;">
                            <div style="font-weight:700; font-size:18px; color:#333;">Tech Hours Assignment</div>
                            <button id="roPopupTechUnassignBtn" type="button" style="padding:8px 12px; background:#d32f2f; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:700;" disabled>Unassign</button>
                        </div>
                        <div id="roPopupTechList"><div style="color:#777;">Loading...</div></div>
                    </div>
                    <div id="roPopupTechModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.45); z-index:6000; align-items:center; justify-content:center;">
                        <div style="background:#fff; width:min(860px, 92vw); max-height:90vh; overflow:auto; border-radius:8px; padding:14px 16px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <div id="roPopupTechModalTitle" style="font-weight:700; color:#333;"></div>
                                <button id="roPopupTechModalClose" type="button" style="background:none; border:none; font-size:20px; cursor:pointer;">×</button>
                            </div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
                                <div>
                                    <label style="font-weight:600; color:#555;">Tech</label>
                                    <select id="roPopupTechSelect" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></select>
                                </div>
                                <div>
                                    <label style="font-weight:600; color:#555;">Type</label>
                                    <select id="roPopupTechType" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                                        <option value="body">body</option>
                                        <option value="paint">paint</option>
                                        <option value="mech">mech</option>
                                        <option value="frame">frame</option>
                                    </select>
                                </div>
                            </div>
                            <div id="roPopupTechModalLines" style="border:1px solid #e2e2e2; border-radius:6px; max-height:52vh; overflow:auto;"></div>
                            <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
                                <button id="roPopupTechModalAddLine" type="button" style="padding:9px 14px; background:#f5f5f5; color:#333; border:1px solid #ccc; border-radius:6px; cursor:pointer;">+ Add Line</button>
                                <button id="roPopupTechModalSave" type="button" style="padding:9px 14px; background:#d32f2f; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:700;">Save</button>
                            </div>
                        </div>
                    </div>
                `;

                bindTechModalActions();
                const listEl = roWindowDoc.getElementById('roPopupTechList');
                const unassignBtn = roWindowDoc.getElementById('roPopupTechUnassignBtn');

                function syncTechSelectionState() {
                    const selected = popupState.techSelectedIndices || [];
                    if (unassignBtn) {
                        unassignBtn.disabled = selected.length === 0;
                        unassignBtn.style.opacity = selected.length === 0 ? '0.6' : '1';
                        unassignBtn.style.cursor = selected.length === 0 ? 'not-allowed' : 'pointer';
                    }
                }

                function bindTechRowSelection() {
                    roWindowDoc.querySelectorAll('.roPopupTechRowCheckbox').forEach((checkbox) => {
                        checkbox.addEventListener('change', () => {
                            const idx = parseInt(checkbox.getAttribute('data-tech-index') || '-1', 10);
                            if (!Number.isFinite(idx) || idx < 0) return;
                            const selected = Array.isArray(popupState.techSelectedIndices) ? popupState.techSelectedIndices.slice() : [];
                            const existingIndex = selected.indexOf(idx);
                            if (checkbox.checked && existingIndex === -1) selected.push(idx);
                            if (!checkbox.checked && existingIndex >= 0) selected.splice(existingIndex, 1);
                            popupState.techSelectedIndices = selected;
                            syncTechSelectionState();
                        });
                    });
                }

                async function unassignSelectedTechRows() {
                    const selectedIndices = Array.isArray(popupState.techSelectedIndices) ? popupState.techSelectedIndices.slice() : [];
                    if (!selectedIndices.length) {
                        alert('Select at least one row to unassign.');
                        return;
                    }

                    const selectedSources = selectedIndices
                        .map((idx) => popupState.techLineItems[idx])
                        .filter((item) => !!item)
                        .map((item) => ({
                            mode: item.mode,
                            repair_type: item.repair_type || item.type,
                            tech_name: item.tech_name || item.tech || '',
                        }));

                    if (!selectedSources.length) {
                        alert('No valid rows selected.');
                        return;
                    }

                    await popupFetchJson('/api/ro-assignment-unassign', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ro: ro.ro,
                            selected_sources: selectedSources,
                        }),
                    });

                    await renderTechView();
                    loadDashboardData();
                }

                if (unassignBtn) {
                    unassignBtn.onclick = async () => {
                        try {
                            await unassignSelectedTechRows();
                        } catch (error) {
                            console.error('Error unassigning selected tech rows:', error);
                            alert('Error unassigning selected rows.');
                        }
                    };
                }

                syncTechSelectionState();
                try {
                    const data = await popupFetchJson(`/api/ro-tech-lines?ro=${encodeURIComponent(ro.ro)}`);
                    const displayList = Array.isArray(data.tech_lines) ? data.tech_lines : [];
                    popupState.techLineItems = displayList;
                    popupState.techSelectedIndices = [];

                    if (!displayList.length) {
                        listEl.innerHTML = '<div style="color:#999; padding:8px;">No repair data found.</div>';
                        syncTechSelectionState();
                        return;
                    }

                    listEl.innerHTML = `
                        <div class="dashboard-ro-table-wrap" style="overflow:hidden;">
                        <table style="width:100%; border-collapse:collapse;">
                            <thead>
                                <tr class="dashboard-header-row">
                                    <th class="dashboard-header-cell" style="padding:12px 10px; text-align:center; width:44px;">Sel</th>
                                    <th class="dashboard-header-cell" style="padding:12px; text-align:left;">TECH</th>
                                    <th class="dashboard-header-cell" style="padding:12px; text-align:left;">TYPE</th>
                                    <th class="dashboard-header-cell" style="padding:12px; text-align:right;">HRS</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${displayList.map((item, index) => {
                                    const techLabel = escapePopupHtml(item.tech || 'unassigned');
                                    const typeLabel = escapePopupHtml(normalizeTypeLabelLocal(item.type || '?'));
                                    const textColor = techLabel.toUpperCase() === 'PENDING' ? '#d32f2f' : '#333';
                                    const hrs = Number(item.hours || 0).toFixed(1);
                                    return `
                                        <tr style="background:#fff; border-bottom:1px solid rgba(0,0,0,0.06);">
                                            <td style="padding:8px 10px; text-align:center;"><input type="checkbox" class="roPopupTechRowCheckbox" data-tech-index="${index}" style="width:16px; height:16px; cursor:pointer;" /></td>
                                            <td style="padding:8px 12px; color:${textColor}; font-weight:700;"><button type="button" data-tech-index="${index}" class="roPopupTechAssignBtn" style="background:none; border:none; color:${textColor}; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:700;">${techLabel}</button></td>
                                            <td style="padding:8px 12px; color:#333;">${typeLabel}</td>
                                            <td style="padding:8px 12px; text-align:right; color:#333; font-weight:700;">${hrs}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                        </div>
                    `;

                    roWindowDoc.querySelectorAll('.roPopupTechAssignBtn').forEach((button) => {
                        button.addEventListener('click', async () => {
                            const idx = parseInt(button.getAttribute('data-tech-index') || '-1', 10);
                            const item = popupState.techLineItems[idx];
                            if (!item) return;
                            await openTechAssignModalPopup(item);
                        });
                    });
                    bindTechRowSelection();
                    syncTechSelectionState();
                } catch (error) {
                    console.error('Error loading repair data:', error);
                    listEl.innerHTML = '<div style="color:#c62828;">Error loading data.</div>';
                    syncTechSelectionState();
                }
            }

            async function renderPartsView() {
                if (!roWindowContentEl) return;
                roWindowContentEl.innerHTML = `
                    <div>
                        <div style="font-weight:700; color:#333; margin-bottom:6px;">Parts List</div>
                        <div id="roPopupPartsStatus" style="margin-bottom:12px;"></div>
                        <div id="roPopupPartsLines" style="margin-bottom:14px;"></div>
                        <div style="font-weight:700; color:#333; margin-bottom:6px;">Invoices</div>
                        <div id="roPopupPartsInvoices"></div>
                    </div>
                `;

                const statusEl = roWindowDoc.getElementById('roPopupPartsStatus');
                const linesEl = roWindowDoc.getElementById('roPopupPartsLines');
                const invoicesEl = roWindowDoc.getElementById('roPopupPartsInvoices');

                try {
                    const [rosRes, linesRes, onOrderRes, arrivedRes, returnedRes, receivedRes] = await Promise.all([
                        popupFetchJson('/api/parts/ros'),
                        popupFetchJson(`/api/parts/ro-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/on-order-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/arrived-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/returned-lines?ro=${encodeURIComponent(ro.ro)}`),
                        popupFetchJson(`/api/parts/received?ro=${encodeURIComponent(ro.ro)}`),
                    ]);

                    const roRow = (Array.isArray(rosRes.ros) ? rosRes.ros : []).find((item) => String(item.ro || '') === String(ro.ro)) || {};
                    const lines = Array.isArray(linesRes.lines) ? linesRes.lines : [];
                    const onOrder = Array.isArray(onOrderRes.items) ? onOrderRes.items : [];
                    const arrived = Array.isArray(arrivedRes.items) ? arrivedRes.items : [];
                    const returned = Array.isArray(returnedRes.items) ? returnedRes.items : [];
                    const received = Array.isArray(receivedRes.items) ? receivedRes.items : [];

                    const arrivedSet = new Set(arrived.map((item) => Number(item.line_id)));
                    const returnedSet = new Set(returned.map((item) => Number(item.line_id)));
                    const onOrderSet = new Set(onOrder.map((item) => Number(item.line_id)));
                    const partNumberByLine = new Map();
                    const vendorByLine = new Map();
                    const etaByLine = new Map();
                    const listByLine = new Map();
                    const costByLine = new Map();

                    function registerVendorEta(entry) {
                        const lineId = Number(entry.line_id);
                        if (Number.isNaN(lineId) || lineId <= 0) return;

                        const vendor = String(entry.vendor || '').trim();
                        const eta = String(entry.eta || entry.arrival_date || '').trim();

                        if (vendor && !vendorByLine.has(lineId)) {
                            vendorByLine.set(lineId, vendor);
                        }
                        if (eta && !etaByLine.has(lineId)) {
                            etaByLine.set(lineId, eta);
                        }
                    }

                    function registerListAndCost(entry) {
                        const lineId = Number(entry.line_id);
                        if (Number.isNaN(lineId) || lineId <= 0) return;

                        const listValue = Number(entry.list);
                        if (Number.isFinite(listValue) && !listByLine.has(lineId)) {
                            listByLine.set(lineId, listValue);
                        }

                        const costValue = Number(entry.cost);
                        if (Number.isFinite(costValue) && !costByLine.has(lineId)) {
                            costByLine.set(lineId, costValue);
                        }
                    }

                    [...onOrder, ...arrived, ...returned, ...received].forEach((entry) => {
                        const lineId = Number(entry.line_id);
                        const partNumber = String(entry.part_number || '').trim();
                        if (!Number.isNaN(lineId) && lineId > 0 && partNumber && !partNumberByLine.has(lineId)) {
                            partNumberByLine.set(lineId, partNumber);
                        }
                        registerVendorEta(entry);
                        registerListAndCost(entry);
                    });

                    statusEl.innerHTML = `
                        <div style="display:flex; flex-wrap:wrap; gap:8px;">
                            <span style="padding:6px 10px; background:#f1f1f1; border-radius:999px; font-size:13px;">On Order: <strong>${Number(roRow.on_order || 0)}</strong></span>
                            <span style="padding:6px 10px; background:#f1f1f1; border-radius:999px; font-size:13px;">Arrived: <strong>${Number(roRow.arrived || 0)}</strong></span>
                            <span style="padding:6px 10px; background:#f1f1f1; border-radius:999px; font-size:13px;">Returned: <strong>${Number(roRow.returned || 0)}</strong></span>
                            ${(Number(roRow.on_order_warning_count || 0) > 0) ? `<span style="padding:6px 10px; background:#fff3e0; border-radius:999px; font-size:13px; color:#e65100;">⚠ Overdue: <strong>${Number(roRow.on_order_warning_count || 0)}</strong></span>` : ''}
                        </div>
                    `;

                    if (!lines.length) {
                        linesEl.innerHTML = '<div style="color:#777;">No parts lines found.</div>';
                    } else {
                        linesEl.innerHTML = `
                            <div class="dashboard-ro-table-wrap" style="overflow:auto;">
                                <table style="width:100%; border-collapse:collapse;">
                                    <thead>
                                        <tr class="dashboard-header-row">
                                            <th class="dashboard-header-cell" style="padding:12px;">Line</th>
                                            <th class="dashboard-header-cell" style="padding:12px;">Description</th>
                                            <th class="dashboard-header-cell" style="padding:12px;">Part #</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:right;">List</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:right;">Cost</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:right;">QTY</th>
                                            <th class="dashboard-header-cell" style="padding:12px;">Vendor</th>
                                            <th class="dashboard-header-cell" style="padding:12px;">ETA</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:center;">On Order</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:center;">Arrived</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:center;">Returned</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${lines.map((line, idx) => {
                                            const idNum = Number(line.id);
                                            const extracted = extractPartNumberAndDescription(
                                                line.description || '',
                                                line.part_number || partNumberByLine.get(idNum) || ''
                                            );
                                            const cleanDescription = extracted.description || '—';
                                            const linePartNumber = String(extracted.partNumber || '').trim();
                                            const lineList = Number.isFinite(Number(listByLine.get(idNum)))
                                                ? Number(listByLine.get(idNum))
                                                : Number(line.price || 0);
                                            const lineCost = Number.isFinite(Number(costByLine.get(idNum)))
                                                ? Number(costByLine.get(idNum))
                                                : null;
                                            const lineVendor = String(vendorByLine.get(idNum) || '').trim();
                                            const lineEtaRaw = String(etaByLine.get(idNum) || '').trim();
                                            const lineEta = lineEtaRaw ? popupFormatDate(lineEtaRaw) : '—';
                                            const isOnOrder = onOrderSet.has(idNum) || !!line.is_ordered;
                                            const isArrived = arrivedSet.has(idNum);
                                            const isReturned = returnedSet.has(idNum);
                                            return `
                                                <tr style="background:#fff; border-bottom:1px solid rgba(0,0,0,0.06);">
                                                    <td style="padding:8px;">${escapePopupHtml(line.line || '-')}</td>
                                                    <td style="padding:8px;">${escapePopupHtml(cleanDescription)}</td>
                                                    <td style="padding:8px;">${escapePopupHtml(linePartNumber || '-')}</td>
                                                    <td style="padding:8px; text-align:right;">${popupFormatMoney(lineList)}</td>
                                                    <td style="padding:8px; text-align:right;">${lineCost === null ? '—' : popupFormatMoney(lineCost)}</td>
                                                    <td style="padding:8px; text-align:right;">${escapePopupHtml(line.qty || 0)}</td>
                                                    <td style="padding:8px;">${escapePopupHtml(lineVendor || '-')}</td>
                                                    <td style="padding:8px;">${escapePopupHtml(lineEta)}</td>
                                                    <td style="padding:8px; text-align:center; font-weight:600; color:${isOnOrder ? '#2e7d32' : '#777'};">${isOnOrder ? 'Yes' : '—'}</td>
                                                    <td style="padding:8px; text-align:center; font-weight:600; color:${isArrived ? '#2e7d32' : '#777'};">${isArrived ? 'Yes' : '—'}</td>
                                                    <td style="padding:8px; text-align:center; font-weight:600; color:${isReturned ? '#2e7d32' : '#777'};">${isReturned ? 'Yes' : '—'}</td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        `;
                    }

                    const receivedByInvoice = {};
                    received.forEach((entry) => {
                        const invoice = String(entry.invoice_number || '').trim();
                        if (!invoice) return;
                        if (!receivedByInvoice[invoice]) receivedByInvoice[invoice] = [];
                        receivedByInvoice[invoice].push(entry);
                    });
                    const invoiceNumbers = Object.keys(receivedByInvoice);

                    if (!invoiceNumbers.length) {
                        invoicesEl.innerHTML = '<div style="color:#777;">No invoice records.</div>';
                    } else {
                        invoicesEl.innerHTML = `
                            <div class="dashboard-ro-table-wrap" style="overflow:auto;">
                                <table style="width:100%; border-collapse:collapse;">
                                    <thead>
                                        <tr class="dashboard-header-row">
                                            <th class="dashboard-header-cell" style="padding:12px;">Invoice #</th>
                                            <th class="dashboard-header-cell" style="padding:12px;">Vendor</th>
                                            <th class="dashboard-header-cell" style="padding:12px;">Received</th>
                                            <th class="dashboard-header-cell" style="padding:12px; text-align:right;">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${invoiceNumbers.map((invoice, idx) => {
                                            const group = receivedByInvoice[invoice] || [];
                                            // Total should reflect received part costs, not invoice header totals.
                                            const total = group.reduce((sum, item) => sum + Number(item.cost || 0), 0);
                                            const vendorNames = Array.from(new Set(group
                                                .map((item) => String(item.vendor || '').trim())
                                                .filter(Boolean)));
                                            const receivedDates = group
                                                .map((item) => String(item.received_date || item.received_at || '').trim())
                                                .filter(Boolean);
                                            const latestReceivedRaw = receivedDates.length ? receivedDates.sort().slice(-1)[0] : '';
                                            const receivedDisplay = latestReceivedRaw ? popupFormatDate(latestReceivedRaw) : '—';
                                            const vendorDisplay = escapePopupHtml(vendorNames.join(', ') || '—');
                                            const key = escapePopupHtml(invoice);
                                            return `
                                                <tr style="background:#fff; border-bottom:1px solid rgba(0,0,0,0.06); pointer-events:none;">
                                                    <td style="padding:8px;">
                                                        <button type="button" class="roPopupInvoiceToggle" data-invoice-key="${key}" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; pointer-events:auto;">
                                                            ${key}
                                                        </button>
                                                    </td>
                                                    <td style="padding:8px;">${vendorDisplay}</td>
                                                    <td style="padding:8px;">${escapePopupHtml(receivedDisplay)}</td>
                                                    <td style="padding:8px; text-align:right;">${popupFormatMoney(total)}</td>
                                                </tr>
                                                <tr id="roPopupInvoiceDetail-${key}" style="display:none; background:#fff;">
                                                    <td colspan="4" style="padding:8px 10px; border-bottom:1px solid #eee;"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        `;

                        roWindowDoc.querySelectorAll('.roPopupInvoiceToggle').forEach((toggleEl) => {
                            toggleEl.addEventListener('click', () => {
                                const key = toggleEl.getAttribute('data-invoice-key') || '';
                                const detailRow = roWindowDoc.getElementById(`roPopupInvoiceDetail-${key}`);
                                if (!detailRow) return;
                                const isOpen = detailRow.style.display === 'table-row';
                                roWindowDoc.querySelectorAll('[id^="roPopupInvoiceDetail-"]').forEach((el) => {
                                    el.style.display = 'none';
                                });
                                if (isOpen) return;

                                const detailCell = detailRow.querySelector('td');
                                const group = receivedByInvoice[key] || [];
                                const groupRows = group.map((item) => {
                                    const lineId = Number(item.line_id || 0);
                                    const lineInfo = lines.find((line) => Number(line.id || 0) === lineId) || {};
                                    return `
                                        <tr>
                                            <td style="padding:6px 8px; border-bottom:1px solid #f0f0f0; width:80px;">${escapePopupHtml(lineInfo.line || lineId || '-')}</td>
                                            <td style="padding:6px 8px; border-bottom:1px solid #f0f0f0;">${escapePopupHtml(lineInfo.description || '')}</td>
                                            <td style="padding:6px 8px; border-bottom:1px solid #f0f0f0; text-align:right; width:120px;">${popupFormatMoney(item.cost || 0)}</td>
                                        </tr>
                                    `;
                                }).join('');
                                if (detailCell) {
                                    detailCell.innerHTML = `
                                        <div style="font-weight:700; margin-bottom:6px; color:#333;">Invoice Details</div>
                                        <table style="width:100%; border-collapse:collapse;">
                                            <thead>
                                                <tr class="dashboard-header-row" style="text-align:left;">
                                                    <th style="padding:6px 8px; width:80px;">Line</th>
                                                    <th style="padding:6px 8px;">Description</th>
                                                    <th style="padding:6px 8px; width:120px; text-align:right;">Cost</th>
                                                </tr>
                                            </thead>
                                            <tbody>${groupRows}</tbody>
                                        </table>
                                    `;
                                }
                                detailRow.style.display = 'table-row';
                            });
                        });
                    }
                } catch (error) {
                    console.error('Error loading parts view:', error);
                    statusEl.innerHTML = '<div style="color:#c62828;">Error loading parts data.</div>';
                    linesEl.innerHTML = '';
                    invoicesEl.innerHTML = '';
                }
            }

            async function renderPaymentsView() {
                if (!roWindowContentEl) return;
                roWindowContentEl.innerHTML = `
                    <div class="ro-window-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <div id="roPopupPaymentsTitle" style="font-weight:700; font-size:18px; color:#333;">Payments - GRAND TOTAL: -</div>
                            <span id="roPopupPaymentsSave" role="button" aria-label="Save" title="Save" style="display:inline-flex; align-items:center; justify-content:center; width:68px; height:68px; color:#d32f2f; cursor:pointer;"><svg width="44" height="44" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M5 3h11l3 3v15H5V3z" fill="currentColor"/><rect x="8" y="4" width="8" height="5" fill="#ffffff"/><rect x="8" y="14" width="8" height="6" fill="#ffffff"/></svg></span>
                        </div>
                        <div id="roPopupPaymentsLog"><div style="color:#777;">Loading...</div></div>
                    </div>
                `;

                const logEl = roWindowDoc.getElementById('roPopupPaymentsLog');
                const saveBtn = roWindowDoc.getElementById('roPopupPaymentsSave');
                const titleEl = roWindowDoc.getElementById('roPopupPaymentsTitle');

                function formatShortPaymentDate(value) {
                    const source = String(value || '').trim();
                    if (!source) return '--/--/--';
                    let dt;
                    if (/^\d{4}-\d{2}-\d{2}$/.test(source)) {
                        dt = new Date(`${source}T00:00:00`);
                    } else {
                        dt = new Date(source);
                    }
                    if (Number.isNaN(dt.getTime())) return '--/--/--';
                    const mm = String(dt.getMonth() + 1).padStart(2, '0');
                    const dd = String(dt.getDate()).padStart(2, '0');
                    const yy = String(dt.getFullYear()).slice(-2);
                    return `${mm}/${dd}/${yy}`;
                }

                function formatBalance(value) {
                    const numeric = Number(value || 0);
                    if (!Number.isFinite(numeric) || numeric <= 0) return '$0';
                    return popupFormatMoney(numeric);
                }

                function formatGrandTotal(value) {
                    const numeric = Number(value || 0);
                    if (!Number.isFinite(numeric)) return '-';
                    return popupFormatMoney(Math.max(0, numeric));
                }

                function renderPaymentLog(entries) {
                    const sorted = [...entries].sort((a, b) => {
                        const aDate = new Date(a.business_date || a.paid_at || a.date || '').getTime() || 0;
                        const bDate = new Date(b.business_date || b.paid_at || b.date || '').getTime() || 0;
                        return bDate - aDate;
                    });
                    if (!sorted.length) {
                        return '<div style="color:#777; padding:6px 0;">No payments yet.</div>';
                    }
                    return sorted.map((entry) => {
                        const dateText = formatShortPaymentDate(entry.business_date || entry.paid_at || entry.date);
                        const typeText = String(entry.payment_type || 'CARD').trim().toUpperCase() || 'CARD';
                        const checkNumberText = String(entry.check_number || '').trim();
                        const userText = String(entry.created_by || 'Unknown').trim() || 'Unknown';
                        const typeWithCheck = typeText === 'CHECK' && checkNumberText
                            ? `CHECK #${checkNumberText}`
                            : typeText;
                        return `
                            <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #f0f0f0;">
                                <div style="color:#333;">${escapePopupHtml(dateText)} - ${escapePopupHtml(typeWithCheck)} - ${escapePopupHtml(userText)}</div>
                                <div style="font-weight:600; color:#333;">${popupFormatMoney(entry.amount || 0)}</div>
                            </div>
                        `;
                    }).join('');
                }

                function syncCheckNumberVisibility(typeSelectEl, checkInputEl) {
                    if (!typeSelectEl || !checkInputEl) return;
                    const paymentType = String(typeSelectEl.value || '').toUpperCase();
                    const isCheck = paymentType === 'CHECK';
                    checkInputEl.style.display = isCheck ? 'inline-block' : 'none';
                    if (!isCheck) {
                        checkInputEl.value = '';
                    }
                }

                function renderPaymentsScreenForRow(row) {
                    const insuranceEntries = Array.isArray(row.insurance_payment_entries) ? row.insurance_payment_entries : [];
                    const customerEntries = Array.isArray(row.customer_payment_entries) ? row.customer_payment_entries : [];

                    const insuranceTotal = Number(row.insurance_total || 0);
                    const customerTotal = Number(row.customer_total || 0);
                    const insurancePaid = Number(row.insurance_paid || 0);
                    const customerPaid = Number(row.customer_paid || 0);
                    const roGrandTotal = insuranceTotal + customerTotal;
                    const insuranceDue = Math.max(0, insuranceTotal - insurancePaid);
                    const customerDue = Math.max(0, customerTotal - customerPaid);
                    const roDue = Math.max(0, roGrandTotal - (insurancePaid + customerPaid));

                    const pendingGrandTotalColor = '#fbc02d';
                    const paidGrandTotalColor = '#2e7d32';
                    const insuranceGrandTotalColor = insuranceDue <= 0.009 ? paidGrandTotalColor : pendingGrandTotalColor;
                    const customerGrandTotalColor = customerDue <= 0.009 ? paidGrandTotalColor : pendingGrandTotalColor;
                    const roGrandTotalColor = roDue <= 0.009 ? paidGrandTotalColor : pendingGrandTotalColor;

                    const insuranceBalance = formatBalance(insuranceDue);
                    const customerBalance = formatBalance(customerDue);
                    const insuranceGrandTotal = formatGrandTotal(insuranceTotal);
                    const customerGrandTotal = formatGrandTotal(customerTotal);
                    const roGrandTotalText = formatGrandTotal(roGrandTotal);

                    const insuranceName = String(row.insurance_name || '').trim() || '-';
                    const customerName = String(row.customer || '').trim() || '-';

                    if (titleEl) {
                        titleEl.innerHTML = `Payments - GRAND TOTAL: <span style="color:${roGrandTotalColor}; font-weight:800;">${escapePopupHtml(roGrandTotalText)}</span>`;
                    }

                    logEl.innerHTML = `
                        <div style="border:1px solid #e2e2e2; border-radius:6px; padding:12px; margin-bottom:14px; background:#fff;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; color:#333; font-weight:700;">
                                <div>INSURANCE: ${escapePopupHtml(insuranceName)}</div>
                                <div style="text-align:right; line-height:1.35;">
                                    <div>GRAND TOTAL: <span style="color:${insuranceGrandTotalColor}; font-weight:800;">${escapePopupHtml(insuranceGrandTotal)}</span></div>
                                    <div>BALANCE: ${escapePopupHtml(insuranceBalance)}</div>
                                </div>
                            </div>
                            <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px;">
                                <input id="roPopupInsurancePaymentInput" type="number" step="0.01" min="0" placeholder="0.00" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:180px;" />
                                <select id="roPopupInsurancePaymentType" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:120px;">
                                    <option value="CARD">CARD</option>
                                    <option value="CASH">CASH</option>
                                    <option value="CHECK">CHECK</option>
                                </select>
                                <input id="roPopupInsuranceCheckNumber" type="text" placeholder="Check #" style="display:none; padding:8px; border:1px solid #ccc; border-radius:4px; width:150px;" />
                            </div>
                            <div style="height:1px; background:#ddd; margin:8px 0 10px 0;"></div>
                            <div id="roPopupInsuranceLog">${renderPaymentLog(insuranceEntries)}</div>
                        </div>

                        <div style="border:1px solid #e2e2e2; border-radius:6px; padding:12px; background:#fff;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; color:#333; font-weight:700;">
                                <div>CUSTOMER: ${escapePopupHtml(customerName)}</div>
                                <div style="text-align:right; line-height:1.35;">
                                    <div>GRAND TOTAL: <span style="color:${customerGrandTotalColor}; font-weight:800;">${escapePopupHtml(customerGrandTotal)}</span></div>
                                    <div>BALANCE: ${escapePopupHtml(customerBalance)}</div>
                                </div>
                            </div>
                            <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px;">
                                <input id="roPopupCustomerPaymentInput" type="number" step="0.01" min="0" placeholder="0.00" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:180px;" />
                                <select id="roPopupCustomerPaymentType" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:120px;">
                                    <option value="CARD">CARD</option>
                                    <option value="CASH">CASH</option>
                                    <option value="CHECK">CHECK</option>
                                </select>
                                <input id="roPopupCustomerCheckNumber" type="text" placeholder="Check #" style="display:none; padding:8px; border:1px solid #ccc; border-radius:4px; width:150px;" />
                            </div>
                            <div style="height:1px; background:#ddd; margin:8px 0 10px 0;"></div>
                            <div id="roPopupCustomerLog">${renderPaymentLog(customerEntries)}</div>
                        </div>
                    `;
                }

                try {
                    const data = await popupFetchJson('/api/payments/open-ros');
                    const rows = Array.isArray(data.rows) ? data.rows : [];
                    const row = rows.find((item) => String(item.ro || '') === String(ro.ro));
                    if (!row) {
                        logEl.innerHTML = '<div style="color:#777;">No payments found for this RO.</div>';
                        return;
                    }

                    renderPaymentsScreenForRow(row);

                    const insuranceTypeSelect = roWindowDoc.getElementById('roPopupInsurancePaymentType');
                    const customerTypeSelect = roWindowDoc.getElementById('roPopupCustomerPaymentType');
                    const insuranceCheckInput = roWindowDoc.getElementById('roPopupInsuranceCheckNumber');
                    const customerCheckInput = roWindowDoc.getElementById('roPopupCustomerCheckNumber');

                    syncCheckNumberVisibility(insuranceTypeSelect, insuranceCheckInput);
                    syncCheckNumberVisibility(customerTypeSelect, customerCheckInput);

                    if (insuranceTypeSelect && insuranceCheckInput) {
                        insuranceTypeSelect.addEventListener('change', () => syncCheckNumberVisibility(insuranceTypeSelect, insuranceCheckInput));
                    }
                    if (customerTypeSelect && customerCheckInput) {
                        customerTypeSelect.addEventListener('change', () => syncCheckNumberVisibility(customerTypeSelect, customerCheckInput));
                    }

                    if (saveBtn) {
                        saveBtn.onclick = async () => {
                            const insuranceInput = roWindowDoc.getElementById('roPopupInsurancePaymentInput');
                            const customerInput = roWindowDoc.getElementById('roPopupCustomerPaymentInput');
                            const insuranceTypeSelect = roWindowDoc.getElementById('roPopupInsurancePaymentType');
                            const customerTypeSelect = roWindowDoc.getElementById('roPopupCustomerPaymentType');
                            const insuranceCheckInput = roWindowDoc.getElementById('roPopupInsuranceCheckNumber');
                            const customerCheckInput = roWindowDoc.getElementById('roPopupCustomerCheckNumber');

                            const insuranceAmount = parseFloat((insuranceInput?.value || '').trim());
                            const customerAmount = parseFloat((customerInput?.value || '').trim());

                            const hasInsurance = Number.isFinite(insuranceAmount) && insuranceAmount > 0;
                            const hasCustomer = Number.isFinite(customerAmount) && customerAmount > 0;

                            if (!hasInsurance && !hasCustomer) {
                                alert('Enter an insurance or customer payment amount.');
                                return;
                            }

                            const payload = {
                                ro: ro.ro,
                                insurance_payment: hasInsurance ? insuranceAmount : undefined,
                                customer_payment: hasCustomer ? customerAmount : undefined,
                                insurance_payment_type: String(insuranceTypeSelect?.value || 'CARD').toUpperCase(),
                                customer_payment_type: String(customerTypeSelect?.value || 'CARD').toUpperCase(),
                                insurance_check_number: hasInsurance ? String(insuranceCheckInput?.value || '').trim() : '',
                                customer_check_number: hasCustomer ? String(customerCheckInput?.value || '').trim() : '',
                                business_date: new Date().toISOString().slice(0, 10),
                            };

                            saveBtn.disabled = true;
                            try {
                                const saveRes = await popupFetchJson('/api/payments/save', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify(payload),
                                });
                                if (saveRes?.error) {
                                    throw new Error(saveRes.error);
                                }

                                if (insuranceInput) insuranceInput.value = '';
                                if (customerInput) customerInput.value = '';
                                if (insuranceCheckInput) insuranceCheckInput.value = '';
                                if (customerCheckInput) customerCheckInput.value = '';
                                await renderPaymentsView();
                            } catch (saveError) {
                                console.error('Error saving payment:', saveError);
                                alert('Error saving payment.');
                            } finally {
                                if (saveBtn) saveBtn.disabled = false;
                            }
                        };
                    }
                } catch (error) {
                    console.error('Error loading payments log:', error);
                    logEl.innerHTML = '<div style="color:#c62828;">Error loading payments log.</div>';
                }
            }

            async function showSidebarView(view) {
                popupState.activeView = view;
                setActiveSidebar(view);
                renderLoading('Loading...');
                if (view === 'notes') {
                    await renderNotesView();
                    return;
                }
                if (view === 'estimate') {
                    await renderEstimateView();
                    return;
                }
                if (view === 'tech') {
                    await renderTechView();
                    return;
                }
                if (view === 'parts') {
                    await renderPartsView();
                    return;
                }
                if (view === 'payments') {
                    await renderPaymentsView();
                    return;
                }
                roWindowContentEl.innerHTML = '<div class="ro-window-card" style="color:#777;">Select a sidebar item.</div>';
            }

            bindDateAutosave('roHeaderInDate', { errorLabel: 'In Date', displayId: 'roHeaderInDateDisplay' });
            bindDateAutosave('roHeaderEcdDate', { errorLabel: 'ECD Date', displayId: 'roHeaderEcdDateDisplay' });
            bindDateAutosave('roHeaderPickedUpDate', { errorLabel: 'Pick Up Date', displayId: 'roHeaderPickedUpDateDisplay' });
            bindRoPrintActions();
            bindSidebarButtons();
            bindCloseRoButton();
            showSidebarView('notes');
        }
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

            function isOpenDashboardRo(ro) {
                const phase = String(ro?.phase || '').trim().toLowerCase();
                return phase !== 'complete' && phase !== 'complete/finish';
            }

            function toNumeric(value) {
                const parsed = Number(value);
                return Number.isFinite(parsed) ? parsed : 0;
            }

            function sumRepairHours(items) {
                if (!Array.isArray(items)) return 0;
                return items.reduce((sum, item) => sum + toNumeric(item?.value), 0);
            }

            function computeOpenOnlyDashboardMetrics(roList) {
                const openRos = (Array.isArray(roList) ? roList : []).filter(isOpenDashboardRo);
                const totalROs = openRos.length;

                let totalSales = 0;
                let totalHours = 0;

                const hoursByTech = {};
                const rosByTechSets = {};

                openRos.forEach((ro) => {
                    const roKey = String(ro?.ro || '');
                    const roTotal = toNumeric(ro?.total);
                    const roHours = toNumeric(ro?.hours);

                    totalSales += roTotal;
                    totalHours += roHours;

                    const laborTech = String(ro?.tech || '').trim() || 'Unassigned';
                    const paintTech = String(ro?.painter || '').trim() || 'Unassigned';
                    const laborHours = sumRepairHours(ro?.labor_repairs);
                    const paintHours = sumRepairHours(ro?.paint_repairs);

                    hoursByTech[laborTech] = (hoursByTech[laborTech] || 0) + laborHours;
                    hoursByTech[paintTech] = (hoursByTech[paintTech] || 0) + paintHours;

                    if (!rosByTechSets[laborTech]) rosByTechSets[laborTech] = new Set();
                    if (!rosByTechSets[paintTech]) rosByTechSets[paintTech] = new Set();
                    if (roKey) {
                        rosByTechSets[laborTech].add(roKey);
                        rosByTechSets[paintTech].add(roKey);
                    }
                });

                const averageHrs = totalROs ? totalHours / totalROs : 0;
                const averageRO = totalROs ? totalSales / totalROs : 0;

                const hoursPerTech = Object.entries(hoursByTech)
                    .map(([tech, hours]) => ({ tech, hours: toNumeric(hours) }))
                    .sort((a, b) => b.hours - a.hours);

                const rosPerTech = Object.entries(rosByTechSets)
                    .map(([tech, roSet]) => ({ tech, ros: roSet.size }))
                    .sort((a, b) => b.ros - a.ros);

                return {
                    totalSales,
                    totalROs,
                    averageHrs,
                    averageRO,
                    hoursPerTech,
                    rosPerTech,
                };
            }
            
            // Update all dashboard elements
            function updateDashboard(data) {
                const openMetrics = computeOpenOnlyDashboardMetrics(data?.roList || []);

                // Update Total Sales bar and value
                const maxSales = Math.max(openMetrics.totalSales, 10000); // minimum scale
                const salesPercent = (openMetrics.totalSales / maxSales) * 100;
                document.getElementById('totalSalesBar').style.height = salesPercent + '%';
                document.getElementById('totalSalesValue').innerText = '$' + openMetrics.totalSales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

                const maxRos = Math.max(openMetrics.totalROs, 1);
                const rosPercent = (openMetrics.totalROs / maxRos) * 100;
                document.getElementById('totalRosBar').style.height = rosPercent + '%';
                document.getElementById('totalRosValue').innerText = openMetrics.totalROs.toLocaleString('en-US');
                
                // Update Average Hours
                document.getElementById('averageHrs').innerText = openMetrics.averageHrs.toFixed(1);
                
                // Update Average RO
                document.getElementById('averageRO').innerText = '$' + openMetrics.averageRO.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Total Hrs per Tech - Pie Chart
                updateHoursPerTechChart(openMetrics.hoursPerTech);
                
                // Update Total ROs per Tech - List
                updateRosPerTechList(openMetrics.rosPerTech);
                
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
                } else if (type === 'hrs-assignment') {
                    loadRoHrsAssignments(roNumber);
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
                            const who = escapeHtml(note.created_by || 'Unknown');
                            const text = escapeHtml(note.note || '');
                            return `
                                <div style="padding:6px 0; border-bottom:1px solid #eee;">
                                    <div style="font-size:12px; color:#777;">${escapeHtml(when)} • ${who}</div>
                                    <div style="white-space:pre-wrap;">${text}</div>
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

            async function saveRoContactPayload(roNumber, payload) {
                const response = await fetch('/api/ro-phone', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ ro: roNumber, ...payload })
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    throw new Error(result.error || 'Error saving contact details');
                }
                return result;
            }

            function normalizePhoneList(phoneValues) {
                const values = Array.isArray(phoneValues) ? phoneValues : [];
                const seen = new Set();
                const normalized = [];
                values.forEach((value) => {
                    const cleaned = cleanPhoneNumber(value);
                    if (!cleaned || cleaned === '-' || seen.has(cleaned)) {
                        return;
                    }
                    seen.add(cleaned);
                    normalized.push(cleaned);
                });
                return normalized;
            }

            function renderAdditionalPhones(rowId, phoneValues, roNumber) {
                const container = document.getElementById(`phone-additional-${rowId}`);
                if (!container) return;
                const values = normalizePhoneList(phoneValues).slice(1);
                const resolvedRo = String(roNumber || container.dataset.ro || '').trim();
                if (values.length === 0) {
                    container.innerHTML = '';
                    return;
                }
                container.innerHTML = values
                    .map((phone, idx) => {
                        const phoneIndex = idx + 1;
                        return `
                            <span style="display:inline-flex; align-items:center; gap:6px;">
                                <span id="phone-secondary-display-wrap-${rowId}-${phoneIndex}" style="display:inline-flex;">
                                    <button
                                        type="button"
                                        onclick='startSecondaryPhoneEdit(event, ${JSON.stringify(rowId)}, ${phoneIndex})'
                                        style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;"
                                    >
                                        <span id="phone-secondary-display-text-${rowId}-${phoneIndex}">${escapeHtml(phone)}</span>
                                    </button>
                                </span>
                                <span id="phone-secondary-edit-wrap-${rowId}-${phoneIndex}" style="display:none; align-items:center;">
                                    <input
                                        id="phone-secondary-input-${rowId}-${phoneIndex}"
                                        value="${escapeHtml(phone)}"
                                        onkeydown='handleSecondaryPhoneEnter(event, ${JSON.stringify(rowId)}, ${JSON.stringify(resolvedRo)}, ${phoneIndex})'
                                        style="padding:4px 6px; width:150px;"
                                    />
                                </span>
                                <button
                                    type="button"
                                    onclick='deletePhoneAtIndex(event, ${JSON.stringify(rowId)}, ${JSON.stringify(resolvedRo)}, ${phoneIndex})'
                                    style="background:#d32f2f; border:1px solid #b71c1c; color:#fff; border-radius:3px; padding:0 8px; font-size:13px; cursor:pointer;"
                                >-</button>
                            </span>
                        `;
                    })
                    .join('');
            }

            function setPhonePrimaryEditMode(rowId, editing) {
                const displayWrap = document.getElementById(`phone-primary-display-wrap-${rowId}`);
                const editWrap = document.getElementById(`phone-primary-edit-wrap-${rowId}`);
                const input = document.getElementById(`phone-primary-input-${rowId}`);
                if (!displayWrap || !editWrap) return;
                displayWrap.style.display = editing ? 'none' : 'inline-flex';
                editWrap.style.display = editing ? 'inline-flex' : 'none';
                if (editing && input) {
                    input.focus();
                    input.select();
                }
            }

            function startPrimaryPhoneEdit(event, rowId) {
                if (event) {
                    event.stopPropagation();
                    event.preventDefault();
                }
                setPhonePrimaryEditMode(rowId, true);
            }

            function startPrimaryPhoneEditWithValue(event, rowId, phoneValue) {
                startPrimaryPhoneEdit(event, rowId);
                const input = document.getElementById(`phone-primary-input-${rowId}`);
                if (!input) return;
                const nextValue = String(phoneValue || '').trim();
                input.value = nextValue;
                input.focus();
                input.select();
            }

            function setSecondaryPhoneEditMode(rowId, phoneIndex, editing) {
                const displayWrap = document.getElementById(`phone-secondary-display-wrap-${rowId}-${phoneIndex}`);
                const editWrap = document.getElementById(`phone-secondary-edit-wrap-${rowId}-${phoneIndex}`);
                const input = document.getElementById(`phone-secondary-input-${rowId}-${phoneIndex}`);
                if (!displayWrap || !editWrap) return;
                displayWrap.style.display = editing ? 'none' : 'inline-flex';
                editWrap.style.display = editing ? 'inline-flex' : 'none';
                if (editing && input) {
                    input.focus();
                    input.select();
                }
            }

            function startSecondaryPhoneEdit(event, rowId, phoneIndex) {
                if (event) {
                    event.stopPropagation();
                    event.preventDefault();
                }
                setSecondaryPhoneEditMode(rowId, phoneIndex, true);
            }

            function setAddPhoneToggleState(rowId, enabled) {
                const button = document.getElementById(`phone-add-toggle-${rowId}`);
                const wrapper = document.getElementById(`phone-add-input-wrap-${rowId}`);
                if (button) {
                    button.dataset.enabled = enabled ? '1' : '0';
                    button.style.background = enabled ? '#b71c1c' : '#d32f2f';
                    button.style.borderColor = enabled ? '#7f0000' : '#b71c1c';
                }
                if (wrapper) {
                    wrapper.style.display = enabled ? 'block' : 'none';
                }
            }

            function toggleAddPhoneInput(event, rowId) {
                if (event) {
                    event.stopPropagation();
                    event.preventDefault();
                }
                const button = document.getElementById(`phone-add-toggle-${rowId}`);
                const input = document.getElementById(`phone-add-input-${rowId}`);
                if (!button || !input) return;

                const isEnabled = button.dataset.enabled === '1';
                if (isEnabled) {
                    if ((input.value || '').trim()) {
                        input.focus();
                        return;
                    }
                    setAddPhoneToggleState(rowId, false);
                    return;
                }

                setAddPhoneToggleState(rowId, true);
                input.value = '';
                input.focus();
                input.select();
            }

            function setEmailDisplayState(rowId, emailValue) {
                const normalized = String(emailValue || '').trim();
                const displayWrap = document.getElementById(`email-display-wrap-${rowId}`);
                const displayText = document.getElementById(`email-display-text-${rowId}`);
                const editWrap = document.getElementById(`email-edit-wrap-${rowId}`);
                const input = document.getElementById(`email-input-${rowId}`);
                if (!displayWrap || !displayText || !editWrap || !input) return;

                if (normalized) {
                    displayText.textContent = normalized;
                    displayWrap.style.display = 'inline-flex';
                    editWrap.style.display = 'none';
                    input.value = normalized;
                    return;
                }

                displayText.textContent = '';
                displayWrap.style.display = 'none';
                editWrap.style.display = 'inline-flex';
                input.value = '';
            }

            function startEmailEdit(event, rowId) {
                if (event) {
                    event.stopPropagation();
                    event.preventDefault();
                }
                const displayWrap = document.getElementById(`email-display-wrap-${rowId}`);
                const editWrap = document.getElementById(`email-edit-wrap-${rowId}`);
                const input = document.getElementById(`email-input-${rowId}`);
                if (!displayWrap || !editWrap || !input) return;
                displayWrap.style.display = 'none';
                editWrap.style.display = 'inline-flex';
                input.focus();
                input.select();
            }

            function updateRoContactInMemory(roNumber, phoneValues, emailValue) {
                if (!dashboardData || !Array.isArray(dashboardData.roList)) return;
                const normalizedPhones = normalizePhoneList(phoneValues);
                dashboardData.roList = dashboardData.roList.map((row) => {
                    if (!row || String(row.ro) !== String(roNumber)) {
                        return row;
                    }
                    const nextRow = { ...row };
                    nextRow.phone_numbers = normalizedPhones;
                    nextRow.phone = normalizedPhones[0] || '';
                    nextRow.phone_original = normalizedPhones[0] || '';
                    if (typeof emailValue === 'string') {
                        nextRow.email = emailValue;
                    }
                    return nextRow;
                });
            }

            function applyUpdatedPhoneState(rowId, roNumber, result) {
                const updatedPhones = normalizePhoneList(result.phone_numbers);
                const primaryPhone = updatedPhones[0] || '-';
                const primaryInput = document.getElementById(`phone-primary-input-${rowId}`);
                const primaryDisplayText = document.getElementById(`phone-primary-display-text-${rowId}`);
                if (primaryInput) {
                    primaryInput.value = primaryPhone === '-' ? '' : primaryPhone;
                }
                if (primaryDisplayText) {
                    primaryDisplayText.textContent = primaryPhone;
                }
                renderAdditionalPhones(rowId, updatedPhones, roNumber);
                updateRoContactInMemory(roNumber, updatedPhones, result.email);
                refreshRoSlideDownHeight(roNumber, 'customer-contact');
            }

            async function handlePrimaryPhoneEnter(event, rowId, roNumber) {
                if (!event || event.key !== 'Enter') return;
                event.preventDefault();
                event.stopPropagation();

                const input = document.getElementById(`phone-primary-input-${rowId}`);
                if (!input) return;

                const enteredPhone = (input.value || '').trim();
                if (!enteredPhone) {
                    return;
                }

                input.disabled = true;
                try {
                    const result = await saveRoContactPayload(roNumber, {
                        action: 'update_phone_at_index',
                        index: 0,
                        phone: enteredPhone,
                    });
                    applyUpdatedPhoneState(rowId, roNumber, result);
                    setPhonePrimaryEditMode(rowId, false);
                } catch (error) {
                    console.error('Error updating phone:', error);
                    alert('Error updating phone.');
                } finally {
                    input.disabled = false;
                }
            }

            async function handleAdditionalPhoneEnter(event, rowId, roNumber) {
                if (!event || event.key !== 'Enter') return;
                event.preventDefault();
                event.stopPropagation();

                const input = document.getElementById(`phone-add-input-${rowId}`);
                const wrapper = document.getElementById(`phone-add-input-wrap-${rowId}`);
                if (!input || !wrapper) return;

                const enteredPhone = (input.value || '').trim();
                if (!enteredPhone) {
                    return;
                }

                input.disabled = true;
                try {
                    const result = await saveRoContactPayload(roNumber, {
                        action: 'add_phone',
                        phone: enteredPhone,
                    });
                    applyUpdatedPhoneState(rowId, roNumber, result);
                    input.value = '';
                } catch (error) {
                    console.error('Error adding phone:', error);
                    alert('Error saving additional phone.');
                } finally {
                    input.disabled = false;
                }
            }

            async function handleSecondaryPhoneEnter(event, rowId, roNumber, phoneIndex) {
                if (!event || event.key !== 'Enter') return;
                event.preventDefault();
                event.stopPropagation();

                const input = document.getElementById(`phone-secondary-input-${rowId}-${phoneIndex}`);
                if (!input) return;

                const enteredPhone = (input.value || '').trim();
                if (!enteredPhone) {
                    return;
                }

                input.disabled = true;
                try {
                    const result = await saveRoContactPayload(roNumber, {
                        action: 'update_phone_at_index',
                        index: phoneIndex,
                        phone: enteredPhone,
                    });
                    applyUpdatedPhoneState(rowId, roNumber, result);
                } catch (error) {
                    console.error('Error updating phone:', error);
                    alert('Error updating phone.');
                } finally {
                    input.disabled = false;
                }
            }

            async function deletePhoneAtIndex(event, rowId, roNumber, phoneIndex) {
                if (event) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                try {
                    const result = await saveRoContactPayload(roNumber, {
                        action: 'delete_phone_at_index',
                        index: phoneIndex,
                    });
                    applyUpdatedPhoneState(rowId, roNumber, result);
                    setPhonePrimaryEditMode(rowId, false);
                } catch (error) {
                    console.error('Error deleting phone:', error);
                    alert('Error deleting phone.');
                }
            }

            function deletePrimaryPhone(event, rowId, roNumber) {
                deletePhoneAtIndex(event, rowId, roNumber, 0);
            }

            async function handleEmailEnter(event, rowId, roNumber) {
                if (!event || event.key !== 'Enter') return;
                event.preventDefault();
                event.stopPropagation();

                const input = document.getElementById(`email-input-${rowId}`);
                if (!input) return;

                const enteredEmail = (input.value || '').trim();
                input.disabled = true;
                try {
                    const result = await saveRoContactPayload(roNumber, {
                        action: 'set_email',
                        email: enteredEmail,
                    });
                    const updatedEmail = result.email || '';
                    input.value = updatedEmail;
                    setEmailDisplayState(rowId, updatedEmail);
                    updateRoContactInMemory(roNumber, result.phone_numbers, updatedEmail);
                    refreshRoSlideDownHeight(roNumber, 'customer-contact');
                } catch (error) {
                    console.error('Error updating email:', error);
                    alert('Error updating email.');
                } finally {
                    input.disabled = false;
                }
            }

            function normalizeHrsAssignmentType(typeValue) {
                const value = String(typeValue || '').trim().toLowerCase();
                if (value === 'mech') return 'mechanical';
                if (value === 'mechanical') return 'mechanical';
                if (value === 'body' || value === 'paint' || value === 'frame' || value === 'glass') return value;
                return '';
            }

            async function loadRoHrsAssignments(roNumber) {
                const rowId = safeId(roNumber);
                const contentEl = document.getElementById(`hrs-assignment-content-${rowId}`);
                if (!contentEl) return;

                contentEl.innerHTML = '<div style="color:#777;">Loading assignments...</div>';
                refreshRoSlideDownHeight(roNumber, 'hrs-assignment');

                try {
                    const response = await fetch(`/api/ro-tech-lines?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' });
                    const data = await response.json();
                    const techLines = Array.isArray(data?.tech_lines) ? data.tech_lines : [];
                    const assignments = {
                        body: '',
                        paint: '',
                        frame: '',
                        mechanical: '',
                        glass: '',
                    };

                    techLines.forEach((line) => {
                        const typeKey = normalizeHrsAssignmentType(line?.type || line?.repair_type || '');
                        if (!typeKey) return;
                        const techName = String(line?.tech || '').trim();
                        if (!techName || techName.toLowerCase() === 'unassigned' || techName.toUpperCase() === 'PENDING') {
                            return;
                        }
                        if (!assignments[typeKey]) {
                            assignments[typeKey] = techName;
                        }
                    });

                    let html = '<table style="width:100%; border-collapse:collapse;">';
                    html += '<thead><tr style="background:#d9d9d9; border-bottom:2px solid #999;">';
                    html += '<th style="padding:8px 10px; text-align:left; color:#333;">Body</th>';
                    html += '<th style="padding:8px 10px; text-align:left; color:#333;">Paint</th>';
                    html += '<th style="padding:8px 10px; text-align:left; color:#333;">Frame</th>';
                    html += '<th style="padding:8px 10px; text-align:left; color:#333;">Mechanical</th>';
                    html += '<th style="padding:8px 10px; text-align:left; color:#333;">Glass</th>';
                    html += '</tr></thead><tbody>';
                    html += '<tr style="border-bottom:1px solid #ddd; background:#fff;">';
                    html += `<td style="padding:8px 10px; color:#333;">${escapeHtml(assignments.body || '')}</td>`;
                    html += `<td style="padding:8px 10px; color:#333;">${escapeHtml(assignments.paint || '')}</td>`;
                    html += `<td style="padding:8px 10px; color:#333;">${escapeHtml(assignments.frame || '')}</td>`;
                    html += `<td style="padding:8px 10px; color:#333;">${escapeHtml(assignments.mechanical || '')}</td>`;
                    html += `<td style="padding:8px 10px; color:#333;">${escapeHtml(assignments.glass || '')}</td>`;
                    html += '</tr></tbody></table>';

                    contentEl.innerHTML = html;
                    refreshRoSlideDownHeight(roNumber, 'hrs-assignment');
                } catch (error) {
                    console.error('Error loading HRS assignments:', error);
                    contentEl.innerHTML = '<div style="color:red;">Error loading assignments.</div>';
                    refreshRoSlideDownHeight(roNumber, 'hrs-assignment');
                }
            }

            function toggleRoHrsAssignments(event, roNumber) {
                if (event) {
                    event.stopPropagation();
                    event.preventDefault();
                }
                const opened = toggleRoSlideDown(roNumber, 'hrs-assignment');
                if (opened) {
                    loadRoHrsAssignments(roNumber);
                }
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
                    complete: 'Done',
                    'complete/finish': 'Done'
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
                    { value: 'complete', label: 'Done' }
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

            function openPrintOptionsModal() {
                const panel = document.getElementById('printOptionsModal');
                if (!panel) return;
                toggleMiniPopup(panel);
            }

            function getDashboardPrintGroupMeta(sortKey) {
                const normalized = String(sortKey || 'ro').toLowerCase();
                const meta = {
                    ro: { heading: 'RO #', grouped: false },
                    insurance: { heading: 'Insurance', grouped: true },
                    in_date: { heading: 'In Date', grouped: true },
                    ecd_date: { heading: 'ECD', grouped: true },
                    tech: { heading: 'Techs', grouped: true },
                    phase: { heading: 'Roadmap', grouped: true },
                };
                return meta[normalized] || meta.ro;
            }

            function getDashboardPrintGroupValue(ro, sortKey) {
                const item = ro || {};
                if (sortKey === 'in_date' || sortKey === 'ecd_date') {
                    return String(item[sortKey] || '').trim();
                }
                if (sortKey === 'phase') {
                    return String(formatPhaseDisplay(item.phase || '') || '').trim();
                }
                if (sortKey === 'tech') {
                    return String(item.tech || '').trim();
                }
                if (sortKey === 'insurance') {
                    return String(item.insurance || '').trim();
                }
                return String(item[sortKey] || '').trim();
            }

            function getDashboardPrintGroupLabel(ro, sortKey) {
                const rawValue = getDashboardPrintGroupValue(ro, sortKey);
                if (sortKey === 'in_date') {
                    return rawValue ? formatShortDate(rawValue) : 'No In Date';
                }
                if (sortKey === 'ecd_date') {
                    return rawValue ? formatShortDate(rawValue) : 'No ECD';
                }
                if (sortKey === 'tech') {
                    return rawValue || 'Unassigned';
                }
                if (sortKey === 'phase') {
                    return rawValue || 'No Roadmap';
                }
                if (sortKey === 'insurance') {
                    return rawValue || 'No Insurance';
                }
                return rawValue || '-';
            }

            function compareDashboardPrintGroupKeys(leftKey, rightKey, sortKey) {
                if (sortKey === 'in_date' || sortKey === 'ecd_date') {
                    const leftDate = Date.parse(leftKey || '') || 0;
                    const rightDate = Date.parse(rightKey || '') || 0;
                    return leftDate - rightDate;
                }
                return String(leftKey || '').localeCompare(String(rightKey || ''), undefined, { numeric: true, sensitivity: 'base' });
            }

            function compareDashboardPrintRows(left, right) {
                const leftRo = String(left?.ro || '');
                const rightRo = String(right?.ro || '');
                return leftRo.localeCompare(rightRo, undefined, { numeric: true, sensitivity: 'base' });
            }

            function buildDashboardPrintRows(rows) {
                return rows.map((ro) => {
                    const roNumber = escapeHtml(String(ro?.ro || '-'));
                    const vehicle = escapeHtml(String(ro?.vehicle || '-'));
                    const customer = escapeHtml(String(ro?.customer || '-'));
                    const insurance = escapeHtml(String(ro?.insurance || '-'));
                    const roadmap = escapeHtml(formatPhaseDisplay(ro?.phase || ''));
                    const inDate = escapeHtml(formatShortDate(ro?.in_date || ''));
                    const ecdDate = escapeHtml(formatShortDate(ro?.ecd_date || ''));
                    const tech = escapeHtml(String(ro?.tech || 'Unassigned'));
                    const hoursValue = Number(ro?.hours || 0);
                    const totalValue = Number(ro?.total || 0);

                    return `
                        <tr class="dashboard-print-row">
                            <td>${roNumber}</td>
                            <td>${vehicle}</td>
                            <td>${customer}</td>
                            <td>${insurance}</td>
                            <td>${roadmap}</td>
                            <td>${tech}</td>
                            <td class="center-cell">${inDate}</td>
                            <td class="center-cell">${ecdDate}</td>
                            <td class="num-cell">${hoursValue.toFixed(1)}</td>
                            <td class="num-cell">$${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                        </tr>
                    `;
                }).join('');
            }

            function buildDashboardPrintTable(rows) {
                const rowsHtml = buildDashboardPrintRows(rows);
                return `
                    <div class="dashboard-print-table-wrap">
                        <table class="dashboard-print-table">
                            <thead>
                                <tr class="dashboard-print-header-row">
                                    <th>RO#</th>
                                    <th>Vehicle</th>
                                    <th>Customer</th>
                                    <th>Insurance</th>
                                    <th>Roadmap</th>
                                    <th>Tech</th>
                                    <th class="center-cell">In</th>
                                    <th class="center-cell">ECD</th>
                                    <th class="num-cell">HRS</th>
                                    <th class="num-cell">Total</th>
                                </tr>
                            </thead>
                            <tbody>${rowsHtml}</tbody>
                        </table>
                    </div>
                `;
            }

            function buildDashboardPrintSection(title, rows) {
                const label = escapeHtml(String(title || '-'));
                const count = Array.isArray(rows) ? rows.length : 0;
                return `
                    <section class="dashboard-print-section">
                        <div class="dashboard-print-section-header">
                            <div class="dashboard-print-section-title">${label}</div>
                            <div class="dashboard-print-section-count">${count} RO${count === 1 ? '' : 's'}</div>
                        </div>
                        ${buildDashboardPrintTable(rows)}
                    </section>
                `;
            }

            function printRoList(sortBy) {
                const panel = document.getElementById('printOptionsModal');
                if (panel) {
                    closeMiniPopup(panel);
                }

                const source = (dashboardData && Array.isArray(dashboardData.roList)) ? [...dashboardData.roList] : [];
                if (!source.length) {
                    alert('No repair orders to print.');
                    return;
                }

                const sortKey = String(sortBy || 'ro').toLowerCase();
                const meta = getDashboardPrintGroupMeta(sortKey);
                let bodyHtml = '';

                if (meta.grouped) {
                    const grouped = new Map();
                    source.forEach((item) => {
                        const key = getDashboardPrintGroupValue(item, sortKey);
                        if (!grouped.has(key)) grouped.set(key, []);
                        grouped.get(key).push(item);
                    });

                    const orderedKeys = Array.from(grouped.keys()).sort((leftKey, rightKey) => {
                        return compareDashboardPrintGroupKeys(leftKey, rightKey, sortKey);
                    });

                    bodyHtml = orderedKeys.map((groupKey) => {
                        const groupRows = [...(grouped.get(groupKey) || [])].sort(compareDashboardPrintRows);
                        const label = getDashboardPrintGroupLabel(groupRows[0] || {}, sortKey);
                        return buildDashboardPrintSection(label, groupRows);
                    }).join('');
                } else {
                    const sorted = [...source].sort(compareDashboardPrintRows);
                    bodyHtml = buildDashboardPrintSection(meta.heading, sorted);
                }

                const printWindow = window.open('', '_blank');
                if (!printWindow) return;

                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Repair Orders</title>
                        <style>
                            @media print {
                                @page { margin: 0.45in; }
                                body { margin: 0; }
                                .dashboard-print-section { break-inside: avoid; }
                            }
                            body {
                                font-family: "Segoe UI", Arial, sans-serif;
                                margin: 20px;
                                color: #111;
                                background: #ffffff;
                            }
                            .dashboard-print-page-title {
                                margin: 0;
                                font-size: 28px;
                                font-weight: 800;
                                color: #111;
                            }
                            .dashboard-print-subtitle {
                                margin: 8px 0 18px 0;
                                color: #666;
                                font-size: 13px;
                            }
                            .dashboard-print-section {
                                margin: 0 0 20px 0;
                            }
                            .dashboard-print-section-header {
                                display: flex;
                                align-items: center;
                                justify-content: space-between;
                                gap: 12px;
                                padding: 10px 14px;
                                background: #f7f3ed;
                                border-bottom: 3px solid #b22222;
                                border-radius: 8px 8px 0 0;
                            }
                            .dashboard-print-section-title {
                                font-size: 18px;
                                font-weight: 800;
                                color: #222;
                            }
                            .dashboard-print-section-count {
                                font-size: 13px;
                                font-weight: 700;
                                color: #b22222;
                                white-space: nowrap;
                            }
                            .dashboard-print-table-wrap {
                                border: 1px solid #ddd;
                                border-top: none;
                                border-radius: 0 0 8px 8px;
                                overflow: hidden;
                            }
                            .dashboard-print-table {
                                width: 100%;
                                border-collapse: collapse;
                            }
                            .dashboard-print-header-row th {
                                background: #3b4041;
                                color: #fff;
                                text-align: left;
                                padding: 11px 12px;
                                font-size: 12px;
                                font-weight: 800;
                            }
                            .dashboard-print-row td {
                                padding: 11px 12px;
                                font-size: 12px;
                                border-top: 1px solid #ececec;
                                background: #fff;
                            }
                            .dashboard-print-row:first-child td {
                                border-top: none;
                            }
                            .center-cell {
                                text-align: center;
                            }
                            .num-cell {
                                text-align: right;
                            }
                        </style>
                    </head>
                    <body>
                        <h1 class="dashboard-print-page-title">Repair Orders</h1>
                        <p class="dashboard-print-subtitle">Printed by ${escapeHtml(meta.heading)}</p>
                        ${bodyHtml}
                    </body>
                    </html>
                `);
                printWindow.document.close();
                setTimeout(() => printWindow.print(), 150);
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
                    const vinRaw = String(ro.vin || '-');
                    const vinDisplay = (() => {
                        const safeVin = escapeHtml(vinRaw);
                        if (!safeVin || safeVin === '-') return safeVin || '-';
                        if (safeVin.length <= 8) {
                            return `<span style="text-decoration:underline;">${safeVin}</span>`;
                        }
                        const head = safeVin.slice(0, safeVin.length - 8);
                        const tail = safeVin.slice(-8);
                        return `${head}<span style="text-decoration:underline;">${tail}</span>`;
                    })();
                    const phoneNumbers = normalizePhoneList(ro.phone_numbers);
                    if (phoneNumbers.length === 0 && phoneDisplay && phoneDisplay !== '-') {
                        phoneNumbers.push(phoneDisplay);
                    }
                    const primaryPhoneDisplay = phoneNumbers[0] || '-';
                    const additionalPhoneDisplays = phoneNumbers.slice(1);
                    const emailDisplay = (ro.email || '').trim();
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
                        <tr class="dashboard-ro-main-row" style="background:${rowBg};">
                            <td style="padding:12px; border-bottom:1px solid #eee; position:relative;">
                                <div style="display:inline-flex; align-items:center; gap:6px;">
                                    <button type="button" onclick="openRoWindowFromDashboard(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
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
                                <select onchange="changeRoPhase(event, '${ro.ro}', this.value)" style="padding:6px 12px; border:none; border-radius:999px; background:#f3f4f6; color:#1f2937; font-size:13px; max-width:160px; outline:none; appearance:none; -webkit-appearance:none; -moz-appearance:none;">
                                    ${phaseSelectOptions}
                                </select>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${inDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#555; text-align:center; font-weight:bold;">${daysDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ecdDisplay}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#333;">
                                <button type="button" onclick="toggleRoHrsAssignments(event, '${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${ro.hours.toFixed(1)}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333; text-align:right; font-weight:bold;">$${ro.total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                        <tr id="hrs-assignment-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="10" style="padding:0 16px 10px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px 12px;">
                                        <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:8px; color:#333;">
                                            <div style="font-weight:bold;">HRS Assignments</div>
                                            <div style="font-weight:bold; color:#333;">${escapeHtml(estimatorDisplay)}</div>
                                        </div>
                                        <div id="hrs-assignment-content-${rowId}" style="width:100%;"></div>
                                    </div>
                                </div>
                            </td>
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
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px 12px; display:flex; align-items:flex-start; gap:16px; flex-wrap:wrap;">
                                        <div style="display:flex; flex-direction:column; gap:6px;">
                                            <div style="display:flex; align-items:center; gap:8px;">
                                                <span style="font-weight:bold; color:#555;">Phone:</span>
                                                <span id="phone-primary-display-wrap-${rowId}" style="display:inline-flex;">
                                                    <button type="button" onclick="startPrimaryPhoneEdit(event, '${rowId}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                                        <span id="phone-primary-display-text-${rowId}">${primaryPhoneDisplay}</span>
                                                    </button>
                                                </span>
                                                <span id="phone-primary-edit-wrap-${rowId}" style="display:none; align-items:center;">
                                                    <input id="phone-primary-input-${rowId}" value="${primaryPhoneDisplay === '-' ? '' : primaryPhoneDisplay}" onkeydown="handlePrimaryPhoneEnter(event, '${rowId}', '${ro.ro}')" style="padding:4px 6px; width:150px;" />
                                                </span>
                                                <button id="phone-add-toggle-${rowId}" data-enabled="0" type="button" onclick="toggleAddPhoneInput(event, '${rowId}')" style="background:#d32f2f; border:1px solid #b71c1c; color:#fff; border-radius:3px; padding:0 8px; font-size:13px; cursor:pointer;">+</button>
                                                <button type="button" onclick="deletePrimaryPhone(event, '${rowId}', '${ro.ro}')" style="background:#d32f2f; border:1px solid #b71c1c; color:#fff; border-radius:3px; padding:0 8px; font-size:13px; cursor:pointer;">-</button>
                                            </div>
                                            <div id="phone-additional-${rowId}" data-ro="${escapeHtml(ro.ro)}" style="display:flex; align-items:center; gap:12px; margin-left:56px; flex-wrap:wrap;">
                                                ${additionalPhoneDisplays.map((phone, idx) => `<span style="display:inline-flex; align-items:center; gap:6px;"><span id="phone-secondary-display-wrap-${rowId}-${idx + 1}" style="display:inline-flex;"><button type="button" onclick='startSecondaryPhoneEdit(event, ${JSON.stringify(rowId)}, ${idx + 1})' style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;"><span id="phone-secondary-display-text-${rowId}-${idx + 1}">${escapeHtml(phone)}</span></button></span><span id="phone-secondary-edit-wrap-${rowId}-${idx + 1}" style="display:none; align-items:center;"><input id="phone-secondary-input-${rowId}-${idx + 1}" value="${escapeHtml(phone)}" onkeydown='handleSecondaryPhoneEnter(event, ${JSON.stringify(rowId)}, ${JSON.stringify(ro.ro)}, ${idx + 1})' style="padding:4px 6px; width:150px;" /></span><button type="button" onclick='deletePhoneAtIndex(event, ${JSON.stringify(rowId)}, ${JSON.stringify(ro.ro)}, ${idx + 1})' style="background:#d32f2f; border:1px solid #b71c1c; color:#fff; border-radius:3px; padding:0 8px; font-size:13px; cursor:pointer;">-</button></span>`).join('')}
                                            </div>
                                            <div id="phone-add-input-wrap-${rowId}" style="display:none; margin-left:56px;">
                                                <input id="phone-add-input-${rowId}" placeholder="Add phone and press Enter" onkeydown="handleAdditionalPhoneEnter(event, '${rowId}', '${ro.ro}')" style="padding:4px 6px; width:190px;" />
                                            </div>
                                        </div>
                                        <div style="display:flex; align-items:center; gap:8px; margin-left:auto;">
                                            <span style="font-weight:bold; color:#555;">Email:</span>
                                            <span id="email-display-wrap-${rowId}" style="${emailDisplay ? 'display:inline-flex;' : 'display:none;'}">
                                                <button type="button" onclick="startEmailEdit(event, '${rowId}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; text-align:left;">
                                                    <span id="email-display-text-${rowId}">${escapeHtml(emailDisplay)}</span>
                                                </button>
                                            </span>
                                            <span id="email-edit-wrap-${rowId}" style="${emailDisplay ? 'display:none;' : 'display:inline-flex;'}">
                                                <input id="email-input-${rowId}" value="${escapeHtml(emailDisplay)}" placeholder="Enter email and press Enter" onkeydown="handleEmailEnter(event, '${rowId}', '${ro.ro}')" style="padding:4px 6px; width:220px;" />
                                            </span>
                                        </div>
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
                                        <div style="font-weight:bold; color:#333;">${escapeHtml(estimatorDisplay)}</div>
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
                                        <button onclick="saveRoNote('${ro.ro}')" style="padding:8px 14px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:700;">Save</button>
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
                const toTitleCaseName = (value) => String(value || '')
                    .trim()
                    .toLowerCase()
                    .split(/\s+/)
                    .filter(Boolean)
                    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
                    .join(' ');

                const estimatorName = toTitleCaseName(ro?.estimator || '');
                const writtenByName = toTitleCaseName(ro?.written_by || '');

                if (estimatorName && writtenByName) {
                    if (estimatorName.toLowerCase() === writtenByName.toLowerCase()) {
                        return `${estimatorName} (Estimator / Written by)`;
                    }
                    return `${estimatorName} / ${writtenByName}`;
                }

                if (estimatorName) return `${estimatorName} (Estimator)`;
                if (writtenByName) return `${writtenByName} (Written by)`;
                return '-';
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

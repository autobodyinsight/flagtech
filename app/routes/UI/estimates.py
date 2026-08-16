"""Estimates screen content for the FlagTech UI."""


def get_estimates_screen_html():
    """Return the HTML content for the Estimates screen."""
    return r"""
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
                    gap: 10px;
                }
                #estimate .estimate-tab-add {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 7px 12px;
                    border-radius: 8px;
                    background: #2e9d53;
                    color: #fff;
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 0.2px;
                    box-shadow: none;
                    border: none;
                    line-height: 1;
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
                    <div style="display:flex; align-items:center; gap:10px;">
                        <h3 class="dashboard-ro-title-tab" style="margin:0; color:#333;">Estimate List</h3>
                        <button type="button" class="estimate-tab-add" aria-label="Add Estimate" onclick="openEstimateWindowFromEstimateList(event)">+ Estimate</button>
                    </div>
                </div>
                <div class="dashboard-ro-table-wrap" style="overflow-x:auto;">
                    <table id="estimateListTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="dashboard-header-row">
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Estimate #</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Vehicle</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Customer</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Insurance</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Claim Number</th>
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
            window.currentEstimateRows = [];

            function formatCurrency(value) {
                const numeric = Number(value || 0);
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                }).format(numeric);
            }

            function getNextEstimateNumber(startingAt = 702) {
                const numbers = (window.currentEstimateRows || [])
                    .map((row) => Number(row.estimate_number))
                    .filter((value) => Number.isFinite(value) && value > 0);
                if (!numbers.length) return startingAt;
                return Math.max(...numbers) + 1;
            }

            function openEstimateWindowFromEstimateList(event) {
                if (event) event.stopPropagation();

                const nextEstimateNumber = getNextEstimateNumber();
                const win = window.open('', `Estimate_Window_${nextEstimateNumber}`, 'width=900,height=600,scrollbars=yes,resizable=yes');
                if (!win) {
                    alert('Popup blocked. Please allow popups for this site.');
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

                const estimateData = {
                    estimate_number: nextEstimateNumber,
                    customer: '',
                    phone: '',
                    vehicle: '',
                    vin: '',
                    insurance: '',
                    claim_number: '',
                    in_date: '',
                    ecd_date: '',
                    picked_up: ''
                };

                const inDateValue = normalizeIsoDateForInput(estimateData.in_date);
                const ecdDateValue = normalizeIsoDateForInput(estimateData.ecd_date);
                const pickedUpDateValue = normalizeIsoDateForInput(estimateData.picked_up);
                const inDateDisplay = formatIsoDateForHeader(inDateValue);
                const ecdDateDisplay = formatIsoDateForHeader(ecdDateValue);
                const pickedUpDateDisplay = formatIsoDateForHeader(pickedUpDateValue);
                const insuranceHeaderValue = (() => {
                    const text = String(estimateData.insurance || '').trim();
                    if (!text) return '-';
                    return text.split(/\s+/).slice(0, 3).join(' ');
                })();

                const icons = {
                    notepad: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="6" width="18" height="16" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="10" x2="19" y2="10" stroke="white" stroke-width="2"/><line x1="9" y1="14" x2="19" y2="14" stroke="white" stroke-width="2"/><line x1="9" y1="18" x2="15" y2="18" stroke="white" stroke-width="2"/></svg>`,
                    estimate: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="3" width="16" height="22" rx="2" stroke="white" stroke-width="2"/><line x1="9" y1="8" x2="19" y2="8" stroke="white" stroke-width="2"/><rect x="9" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="11" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="9" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><rect x="15" y="16" width="4" height="3" rx="0.8" stroke="white" stroke-width="1.8"/><line x1="9" y1="22" x2="19" y2="22" stroke="white" stroke-width="2"/></svg>`,
                    tech: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="9" r="4" stroke="white" stroke-width="2"/><rect x="7" y="17" width="14" height="6" rx="3" stroke="white" stroke-width="2"/><path d="M21 21l2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/><path d="M7 21l-2.5 2.5" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>`,
                    cart: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="14" r="9" stroke="white" stroke-width="2"/><circle cx="14" cy="14" r="5.2" stroke="white" stroke-width="2"/><circle cx="14" cy="14" r="1.7" fill="white"/><path d="M14 5.8v3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M14 19v3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M5.8 14h3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M19 14h3.2" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M8.3 8.3l2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/><path d="M17.4 17.4l2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/><path d="M19.7 8.3l-2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/><path d="M10.6 17.4l-2.3 2.3" stroke="white" stroke-width="1.6" stroke-linecap="round"/></svg>`,
                    credit: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="7" width="20" height="14" rx="3" stroke="white" stroke-width="2"/><rect x="7" y="17" width="6" height="3" rx="1.5" stroke="white" stroke-width="2"/><line x1="4" y1="12" x2="24" y2="12" stroke="white" stroke-width="2"/></svg>`,
                    print: `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7 9V4h10v5" stroke="white" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><rect x="4" y="9" width="16" height="8" rx="2" stroke="white" stroke-width="1.9"/><path d="M7 17h10v3H7z" stroke="white" stroke-width="1.9" stroke-linejoin="round"/><circle cx="17" cy="12.5" r="0.9" fill="white"/></svg>`,
                    close: `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="8.5" stroke="white" stroke-width="1.9"/><path d="M9 9l6 6" stroke="white" stroke-width="1.9" stroke-linecap="round"/><path d="M15 9l-6 6" stroke="white" stroke-width="1.9" stroke-linecap="round"/></svg>`
                };

                const sidebarHtml = `
                    <div id="estimateSidebar" style="position:relative; flex:0 0 64px; height:100%; background:linear-gradient(180deg, #000 0%, #b22222 100%); display:flex; flex-direction:column; align-items:center; justify-content:center; box-shadow:2px 0 8px rgba(0,0,0,0.08);">
                        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; flex:1 1 auto; height:100%; width:100%; padding:10px 0; transform:translateY(-30%);">
                            <button id="estimateSidebarBtn-notes" class="estimate-sidebar-btn" data-view="notes" title="Notes" style="background:none; border:none; padding:0; cursor:pointer;">${icons.notepad}</button>
                            <button id="estimateSidebarBtn-estimate" class="estimate-sidebar-btn" data-view="estimate" title="Estimate" style="background:none; border:none; padding:0; cursor:pointer;">${icons.estimate}</button>
                            <button id="estimateSidebarBtn-tech" class="estimate-sidebar-btn" data-view="tech" title="Tech" style="background:none; border:none; padding:0; cursor:pointer;">${icons.tech}</button>
                            <button id="estimateSidebarBtn-parts" class="estimate-sidebar-btn" data-view="parts" title="Parts" style="background:none; border:none; padding:0; cursor:pointer;">${icons.cart}</button>
                            <button id="estimateSidebarBtn-payments" class="estimate-sidebar-btn" data-view="payments" title="Payments" style="background:none; border:none; padding:0; cursor:pointer;">${icons.credit}</button>
                            <div style="position:relative; display:flex; justify-content:center; width:100%;">
                                <button id="estimatePrintTrigger" class="estimate-sidebar-btn estimate-sidebar-action mini-popup-trigger" type="button" aria-label="Print" title="Print" style="background:none; border:none; padding:0; cursor:pointer;">${icons.print}</button>
                            </div>
                            <button id="estimateCloseButton" class="estimate-sidebar-btn estimate-sidebar-action" type="button" aria-label="Close Estimate" title="Close Estimate" style="background:none; border:none; padding:0; cursor:pointer;">${icons.close}</button>
                        </div>
                    </div>
                `;

                const bannerHtml = `
                    <div id="estimateHeaderBar" style="background:linear-gradient(90deg, #111 0%, #23272a 48%, #d32f2f 100%); color:#fff; padding:12px 24px; position:relative; z-index:120;">
                        <div id="estimateSummaryHeaderGrid" style="display:flex; flex-direction:column; gap:10px; align-items:stretch; margin-right:8px;">
                            <div style="display:grid; grid-template-columns:repeat(5, minmax(0, 1fr)); gap:16px; align-items:center;">
                                <div class="estimate-header-item"><span class="estimate-header-label">Estimate #:</span> <span class="estimate-header-value">${nextEstimateNumber}</span></div>
                                <div class="estimate-header-item"><span class="estimate-header-label">Customer:</span> <span class="estimate-header-value">${estimateData.customer || '-'}</span></div>
                                <div class="estimate-header-item"><span class="estimate-header-label">Phone:</span> <span class="estimate-header-value">${estimateData.phone || '-'}</span></div>
                                <div class="estimate-header-item"><span class="estimate-header-label">Vehicle:</span> <span class="estimate-header-value">${estimateData.vehicle || '-'}</span></div>
                                <div class="estimate-header-item"><span class="estimate-header-label">VIN:</span> <span class="estimate-header-value">${estimateData.vin || '-'}</span></div>
                            </div>
                            <div style="display:grid; grid-template-columns:repeat(5, minmax(0, 1fr)); gap:16px; align-items:center;">
                                <div class="estimate-header-item"><span class="estimate-header-label">Insurance:</span> <span class="estimate-header-value">${insuranceHeaderValue}</span></div>
                                <div class="estimate-header-item"><span class="estimate-header-label">Claim#:</span> <span class="estimate-header-value">${estimateData.claim_number || '-'}</span></div>
                                <div class="estimate-header-item estimate-header-date-row">
                                    <span class="estimate-header-label">In Date:</span>
                                    <span id="estimateHeaderInDateDisplay" class="estimate-header-date-display">${inDateDisplay}</span>
                                    <input type="date" id="estimateHeaderInDate" class="estimate-header-date-input" value="${inDateValue}" data-field="in_date" data-estimate="${nextEstimateNumber}" />
                                </div>
                                <div class="estimate-header-item estimate-header-date-row">
                                    <span class="estimate-header-label">ECD Date:</span>
                                    <span id="estimateHeaderEcdDateDisplay" class="estimate-header-date-display">${ecdDateDisplay}</span>
                                    <input type="date" id="estimateHeaderEcdDate" class="estimate-header-date-input" value="${ecdDateValue}" data-field="ecd_date" data-estimate="${nextEstimateNumber}" />
                                </div>
                                <div class="estimate-header-item estimate-header-date-row">
                                    <span class="estimate-header-label">Pick Up Date:</span>
                                    <span id="estimateHeaderPickedUpDateDisplay" class="estimate-header-date-display">${pickedUpDateDisplay}</span>
                                    <input type="date" id="estimateHeaderPickedUpDate" class="estimate-header-date-input" value="${pickedUpDateValue}" data-field="picked_up" data-estimate="${nextEstimateNumber}" />
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                const contentHtml = `
                    <div id="estimateWindowContent" style="padding:32px; min-height:180px; background:#fff; color:#23272a; font-size:18px; flex:1 1 auto; overflow:auto;">Estimate details will load here.</div>
                `;

                win.document.title = `Estimate Window - ${nextEstimateNumber}`;
                win.document.body.innerHTML = `<div id='estimatePopupRoot' style='display:flex; flex-direction:column; height:100vh; width:100vw; background:#f2f2f2; overflow:hidden;'>${bannerHtml}<div id='estimatePopupLowerLayout' style='display:flex; flex:1 1 auto; min-height:0;'>${sidebarHtml}<div style='flex:1 1 auto; min-width:0; display:flex; flex-direction:column; min-height:0;'>${contentHtml}</div></div></div>`;

                const style = win.document.createElement('style');
                style.textContent = `
                    body { margin:0; font-family:Segoe UI,Arial,sans-serif; background:#f2f2f2; }
                    #estimateSidebar svg { display:block; margin:0 auto; }
                    #estimateSidebar .estimate-sidebar-btn { opacity:0.72; transition:opacity 0.15s ease, transform 0.15s ease; width:100%; display:flex; align-items:center; justify-content:center; }
                    #estimateSidebar .estimate-sidebar-btn:hover { opacity:1; transform:translateY(-1px); }
                    #estimateSidebar .estimate-sidebar-btn.active { opacity:1; }
                    #estimateSidebar { box-shadow:2px 0 8px rgba(0,0,0,0.08); min-height:0; flex-shrink:0; }
                    .estimate-header-item { font-size:15px; line-height:1.25; min-width:0; }
                    .estimate-header-label { color:#d32f2f; font-weight:700; margin-right:6px; white-space:nowrap; }
                    .estimate-header-value { color:#fff; font-weight:600; word-break:break-word; }
                    .estimate-header-date-row { display:flex; align-items:center; gap:8px; }
                    .estimate-header-date-display {
                        color:#fff;
                        font-weight:600;
                        cursor:pointer;
                        text-decoration:underline;
                        text-underline-offset:2px;
                        white-space:nowrap;
                    }
                    .estimate-header-date-input {
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
                    .estimate-header-date-input.editing { display:inline-block; }
                    .estimate-header-date-input:focus {
                        outline:2px solid rgba(178,34,34,0.35);
                        box-shadow:none;
                    }
                    .estimate-sidebar-action { opacity:0.9; }
                    .estimate-sidebar-action:hover { opacity:1; transform:translateY(-1px); }
                `;
                win.document.head.appendChild(style);
            }

            async function loadEstimateList() {
                const body = document.getElementById('estimateListBody');
                if (!body) return;
                body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>';

                try {
                    const response = await fetch('/api/estimate-list', { credentials: 'include' });
                    const data = await response.json();
                    if (!response.ok || data.error) throw new Error(data.error || 'Unable to load estimates');

                    const rows = Array.isArray(data.estimateList) ? data.estimateList : [];
                    window.currentEstimateRows = rows;

                    if (!rows.length) {
                        body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#666;">NO CURRENT ESTIMATES</td></tr>';
                        return;
                    }

                    body.innerHTML = rows.map((row) => {
                        const estimateNumber = row.estimate_number ?? '';
                        const vehicle = row.vehicle || '-';
                        const customer = row.customer || '-';
                        const insurance = row.insurance || '-';
                        const claimNumber = row.claim_number || '-';
                        const total = Number(row.total || 0);

                        return `
                            <tr class="estimate-row">
                                <td class="estimate-number">${estimateNumber}</td>
                                <td>${vehicle}</td>
                                <td>${customer}</td>
                                <td>${insurance}</td>
                                <td>${claimNumber}</td>
                                <td style="text-align:right; font-weight:600; color:#111;">${formatCurrency(total)}</td>
                            </tr>
                        `;
                    }).join('');
                } catch (error) {
                    console.error('Error loading estimate list:', error);
                    body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#b22222;">Unable to load estimates.</td></tr>';
                }
            }
        </script>
    """

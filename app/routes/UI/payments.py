"""Payments screen content for the FlagTech UI."""


def get_payments_screen_html():
    """Return the HTML content for the Payments screen."""
    return r"""
        <div id="payments" class="screen" style="padding:20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; gap:12px;">
                <h1 style="text-align:center; margin:0; flex:1;">PAYMENTS</h1>
                <div style="display:flex; align-items:center; gap:10px;">
                    <div id="paymentsCloseStatus" style="font-size:12px; color:#666; min-height:16px;"></div>
                    <button id="paymentsCloseRoBtn" type="button" onclick="handlePaymentsCloseRoClick(event)" style="padding:10px 16px; background:var(--brand-red, #d32f2f); color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer; font-size:14px;">
                        Close RO
                    </button>
                </div>
            </div>

            <style>
                .payments-header-row {
                    background:#3c4142;
                    text-align:left;
                }
                .payments-header-cell {
                    color:#fff;
                }
            </style>

            <div style="background:#fff; border-radius:8px; padding:18px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <div style="overflow-x:auto;">
                    <table id="paymentsRoTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="payments-header-row">
                                <th id="paymentsCloseHeader" class="payments-header-cell payments-close-col" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; width:36px; display:none;"></th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">RO#</th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Customer</th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Vehicle</th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">Insurance (Total)</th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">Customer (Total)</th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">Grand Total</th>
                                <th class="payments-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">BALANCE</th>
                            </tr>
                        </thead>
                        <tbody id="paymentsRoTableBody">
                            <tr>
                                <td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            let paymentsRows = [];
            let paymentsTechPaymentsByRo = {};
            let openPaymentsRoDetailId = null;
            let paymentsCloseMode = false;
            let paymentsSelectedCloseRo = '';

            function paymentsSafeId(value) {
                return String(value || '').replace(/[^a-zA-Z0-9_-]/g, '_');
            }

            function paymentsFormatMoney(value) {
                const numeric = Number(value || 0);
                return '$' + numeric.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }

            function paymentsToNumber(value) {
                if (typeof value === 'number') return value;
                const cleaned = String(value || '').replace(/[$,\s]/g, '');
                if (!cleaned) return 0;
                const parsed = Number(cleaned);
                return Number.isFinite(parsed) ? parsed : NaN;
            }

            function paymentsFormatCurrencyInputValue(value) {
                const cleaned = String(value || '')
                    .replace(/[^0-9.]/g, '')
                    .replace(/(\..*)\./g, '$1');
                if (!cleaned) return '';
                const parsed = Number(cleaned);
                if (!Number.isFinite(parsed)) return '';
                return '$' + parsed.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }

            function paymentsHandleCurrencyInput(event) {
                if (!event || !event.target) return;
                event.target.value = paymentsFormatCurrencyInputValue(event.target.value);
            }

            function paymentsGetLocalBusinessDateISO() {
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }

            function paymentsFormatBusinessDate(value) {
                const raw = String(value || '').trim().slice(0, 10);
                const parts = raw.split('-');
                if (parts.length !== 3) return '-';

                const [year, month, day] = parts;
                if (!year || !month || !day) return '-';
                return `${month}/${day}/${year.slice(-2)}`;
            }

            function buildPaymentsEntryRows(entries, includeInputColumn) {
                if (!Array.isArray(entries) || entries.length === 0) return '';
                return entries.map((entry) => {
                    const amount = Number(entry.amount || 0);
                    const dateDisplay = paymentsFormatBusinessDate(entry.business_date);
                    if (includeInputColumn) {
                        return `
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${dateDisplay}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:#333;">${paymentsFormatMoney(amount)}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec;"></td>
                            </tr>
                        `;
                    }
                    return `
                        <tr>
                            <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${dateDisplay}</td>
                            <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:#333;">${paymentsFormatMoney(amount)}</td>
                            <td style="padding:8px; border-bottom:1px solid #ececec;"></td>
                        </tr>
                    `;
                }).join('');
            }

            function paymentsEscapedRoValue(value) {
                return String(value || '').replace(/'/g, "\\'");
            }

            function paymentsEscapeHtml(value) {
                return String(value || '')
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }

            function setPaymentsCloseStatus(message, color) {
                const statusEl = document.getElementById('paymentsCloseStatus');
                if (!statusEl) return;
                statusEl.textContent = message || '';
                statusEl.style.color = color || '#666';
            }

            function syncPaymentsCloseSelectionUI() {
                const checkboxes = document.querySelectorAll('.payments-close-checkbox');
                checkboxes.forEach((checkbox) => {
                    const roValue = String(checkbox.getAttribute('data-ro') || '');
                    checkbox.checked = !!paymentsSelectedCloseRo && roValue === paymentsSelectedCloseRo;
                });
            }

            function applyPaymentsCloseModeToTable() {
                const closeCells = document.querySelectorAll('.payments-close-col');
                closeCells.forEach((cell) => {
                    cell.style.display = paymentsCloseMode ? '' : 'none';
                });

                const button = document.getElementById('paymentsCloseRoBtn');
                if (button) {
                    button.textContent = 'Close RO';
                }

                syncPaymentsCloseSelectionUI();
            }

            function onPaymentsCloseRoSelect(event, roNumber) {
                if (event) event.stopPropagation();
                const roValue = String(roNumber || '');
                if (!roValue) return;

                paymentsSelectedCloseRo = paymentsSelectedCloseRo === roValue ? '' : roValue;
                syncPaymentsCloseSelectionUI();
            }

            async function handlePaymentsCloseRoClick(event) {
                if (event) event.stopPropagation();
                const button = document.getElementById('paymentsCloseRoBtn');
                if (!button) return;

                if (!paymentsCloseMode) {
                    paymentsCloseMode = true;
                    paymentsSelectedCloseRo = '';
                    applyPaymentsCloseModeToTable();
                    setPaymentsCloseStatus('Select one RO, then click Close RO again.', '#666');
                    return;
                }

                if (!paymentsSelectedCloseRo) {
                    paymentsCloseMode = false;
                    paymentsSelectedCloseRo = '';
                    applyPaymentsCloseModeToTable();
                    setPaymentsCloseStatus('', '#666');
                    return;
                }

                const roToClose = paymentsSelectedCloseRo;
                button.disabled = true;
                setPaymentsCloseStatus(`Closing RO ${roToClose}...`, '#555');

                try {
                    const response = await fetch('/api/payments/close-ro', {
                        method: 'POST',
                        credentials: 'include',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ro: roToClose }),
                    });
                    const payload = await response.json();
                    if (!response.ok) {
                        throw new Error(payload.error || 'Unable to close RO');
                    }

                    paymentsCloseMode = false;
                    paymentsSelectedCloseRo = '';
                    await loadPaymentsData();

                    if (typeof loadDashboardData === 'function') {
                        loadDashboardData();
                    }

                    setPaymentsCloseStatus(`RO ${roToClose} closed.`, '#2e7d32');
                } catch (err) {
                    console.error('Error closing RO:', err);
                    setPaymentsCloseStatus(err.message || 'Unable to close RO', '#c62828');
                } finally {
                    button.disabled = false;
                    applyPaymentsCloseModeToTable();
                }
            }

            function buildPaymentsBalancePanel(options) {
                const {
                    rowId,
                    roEscaped,
                    insuranceName,
                    customerName,
                    insuranceTotal,
                    customerTotal,
                    insurancePaid,
                    customerPaid,
                    insuranceBalance,
                    customerBalance,
                    insurancePaymentEntries,
                    customerPaymentEntries,
                    editable,
                } = options;

                const insuranceTotalColor = insuranceBalance === 0 ? '#2e7d32' : '#333';
                const customerTotalColor = customerBalance === 0 ? '#2e7d32' : '#333';

                const saveControlsHtml = editable
                    ? `
                        <div style="display:flex; justify-content:flex-end; align-items:center; gap:12px; margin-bottom:10px;">
                            <div id="payments-save-msg-${rowId}" style="font-size:12px; color:#666;"></div>
                            <button id="payments-save-btn-${rowId}" type="button" onclick="saveGrandTotalPaymentsForRo(event, '${roEscaped}')" style="padding:8px 16px; background:var(--brand-red, #d32f2f); color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold; font-size:14px;">
                                SAVE
                            </button>
                        </div>
                    `
                    : '';

                const insuranceInputHtml = editable
                    ? `
                        <input id="payments-ins-paid-${rowId}" type="text" inputmode="decimal" pattern="^\\d{0,6}(\\.\\d{0,2})?$" maxlength="9" value="${paymentsFormatMoney(0)}" oninput="paymentsHandleCurrencyInput(event)" placeholder="$0.00" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:170px; text-align:right;" />
                    `
                    : '';

                const customerInputHtml = editable
                    ? `
                        <input id="payments-cust-paid-${rowId}" type="text" inputmode="decimal" pattern="^\\d{0,6}(\\.\\d{0,2})?$" maxlength="9" value="${paymentsFormatMoney(0)}" oninput="paymentsHandleCurrencyInput(event)" placeholder="$0.00" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:170px; text-align:right;" />
                    `
                    : '';

                const buildSectionRows = (entries, totalAmount, paidTotal) => {
                    let runningBalance = Math.max(0, Number(totalAmount || 0) - Number(paidTotal || 0));
                    const rows = [];

                    const normalizedEntries = Array.isArray(entries) ? entries : [];
                    normalizedEntries.forEach((entry, index) => {
                        const amount = Number(entry.amount || 0);
                        const dateDisplay = paymentsFormatBusinessDate(entry.business_date || entry.paid_at || entry.date);
                        const rowBalance = runningBalance;
                        const balanceColor = index === 0
                            ? (rowBalance === 0 ? '#2e7d32' : '#c62828')
                            : '#333';

                        rows.push(`
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${dateDisplay}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:#333;">${paymentsFormatMoney(amount)}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:${balanceColor}; font-weight:${index === 0 ? 'bold' : 'normal'};">${paymentsFormatMoney(rowBalance)}</td>
                            </tr>
                        `);

                        runningBalance = Math.max(0, rowBalance + amount);
                    });

                    if (rows.length === 0 && Number(paidTotal || 0) > 0) {
                        const newestBalance = Math.max(0, Number(totalAmount || 0) - Number(paidTotal || 0));
                        const newestColor = newestBalance === 0 ? '#2e7d32' : '#c62828';
                        rows.push(`
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${paymentsFormatBusinessDate(paymentsGetLocalBusinessDateISO())}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:#333;">${paymentsFormatMoney(paidTotal)}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:${newestColor}; font-weight:bold;">${paymentsFormatMoney(newestBalance)}</td>
                            </tr>
                        `);
                    }

                    return rows.join('');
                };

                const insuranceRowsHtml = buildSectionRows(insurancePaymentEntries, insuranceTotal, insurancePaid);
                const customerRowsHtml = buildSectionRows(customerPaymentEntries, customerTotal, customerPaid);

                const insuranceTableHtml = editable
                    ? `
                        <table style="width:100%; border-collapse:collapse; table-layout:fixed; margin-bottom:10px;">
                            <colgroup>
                                <col style="width:34%;" />
                                <col style="width:33%;" />
                                <col style="width:33%;" />
                            </colgroup>
                            <thead>
                                <tr style="background:#f7f7f7; text-align:left;">
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000;">${insuranceInputHtml}</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">PAYMENTS</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">BALANCE</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${insuranceRowsHtml}
                            </tbody>
                        </table>
                    `
                    : `
                        <table style="width:100%; border-collapse:collapse; table-layout:fixed; margin-bottom:10px;">
                            <colgroup>
                                <col style="width:34%;" />
                                <col style="width:33%;" />
                                <col style="width:33%;" />
                            </colgroup>
                            <thead>
                                <tr style="background:#f7f7f7; text-align:left;">
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000;"></th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">PAYMENTS</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">BALANCE</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${insuranceRowsHtml}
                            </tbody>
                        </table>
                    `;

                const customerTableHtml = editable
                    ? `
                        <table style="width:100%; border-collapse:collapse; table-layout:fixed;">
                            <colgroup>
                                <col style="width:34%;" />
                                <col style="width:33%;" />
                                <col style="width:33%;" />
                            </colgroup>
                            <thead>
                                <tr style="background:#f7f7f7; text-align:left;">
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000;">${customerInputHtml}</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">PAYMENTS</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">BALANCE</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${customerRowsHtml}
                            </tbody>
                        </table>
                    `
                    : `
                        <table style="width:100%; border-collapse:collapse; table-layout:fixed;">
                            <colgroup>
                                <col style="width:34%;" />
                                <col style="width:33%;" />
                                <col style="width:33%;" />
                            </colgroup>
                            <thead>
                                <tr style="background:#f7f7f7; text-align:left;">
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000;"></th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">PAYMENTS</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">BALANCE</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${customerRowsHtml}
                            </tbody>
                        </table>
                    `;

                return `
                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;">
                        ${saveControlsHtml}
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px;">
                            <div style="font-weight:bold; color:#000;">INSURANCE</div>
                            <div style="font-weight:bold; color:#000;">TOTAL:</div>
                            <div style="font-weight:bold; color:${insuranceTotalColor};">${paymentsFormatMoney(insuranceTotal)}</div>
                        </div>
                        <div style="color:#333; margin-bottom:6px;">${insuranceName || '-'}</div>
                        ${insuranceTableHtml}

                        <div style="border-top:2px dotted #bbb; margin:12px 0 10px 0;"></div>

                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px;">
                            <div style="font-weight:bold; color:#000;">CUSTOMER</div>
                            <div style="font-weight:bold; color:#000;">TOTAL:</div>
                            <div style="font-weight:bold; color:${customerTotalColor};">${paymentsFormatMoney(customerTotal)}</div>
                        </div>
                        <div style="color:#333; margin-bottom:6px;">${customerName || '-'}</div>
                        ${customerTableHtml}
                    </div>
                `;
            }

            function paymentsOpenRow(rowEl) {
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

            function paymentsCloseRow(rowEl) {
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

            function togglePaymentsEditor(event, roNumber) {
                if (event) event.stopPropagation();
                const rowId = paymentsSafeId(roNumber);
                const detailRow = document.getElementById(`payments-editor-row-${rowId}`);
                if (!detailRow) return;

                const isHidden = detailRow.style.display === 'none' || detailRow.style.display === '';
                if (isHidden) {
                    paymentsOpenRow(detailRow);
                    return;
                }

                paymentsCloseRow(detailRow);
            }

            function findPaymentsRow(roNumber) {
                const roValue = String(roNumber || '');
                return paymentsRows.find((row) => String(row.ro || '') === roValue) || null;
            }

            async function loadPaymentsTechLog(roNumber) {
                const roKey = String(roNumber || '');
                if (!roKey) return [];
                if (Array.isArray(paymentsTechPaymentsByRo[roKey])) {
                    return paymentsTechPaymentsByRo[roKey];
                }

                const response = await fetch(`/api/payments/log?ro=${encodeURIComponent(roKey)}`, { credentials: 'include' });
                const payload = await response.json();
                if (!response.ok) {
                    throw new Error(payload.error || 'Unable to load tech payment log');
                }

                const entries = Array.isArray(payload.entries) ? payload.entries : [];
                paymentsTechPaymentsByRo[roKey] = entries;
                return entries;
            }

            function renderPaymentsRoDetailContent(roNumber, rowData, techEntries, errorMessage) {
                const rowId = paymentsSafeId(roNumber);
                const contentEl = document.getElementById(`payments-ro-details-content-${rowId}`);
                if (!contentEl) return;

                if (!rowData) {
                    contentEl.innerHTML = '<div style="color:#c62828;">Unable to load RO payment details.</div>';
                    return;
                }

                const insurancePaid = Number(rowData.insurance_paid || 0);
                const customerPaid = Number(rowData.customer_paid || 0);
                const invoiceReceivedTotal = insurancePaid + customerPaid;
                const invoicePayments = Array.isArray(rowData.invoice_payments) ? rowData.invoice_payments : [];
                const invoicePaymentsTotal = invoicePayments.reduce((sum, entry) => sum + Number(entry.amount_paid || 0), 0);

                const rows = Array.isArray(techEntries) ? techEntries : [];
                const isLoadingTech = techEntries === null;
                const techPaymentsTotal = rows.reduce((sum, entry) => sum + Number(entry.amount || 0), 0);
                const combinedGrandTotal = invoiceReceivedTotal + techPaymentsTotal;

                const techRowsHtml = isLoadingTech
                    ? '<tr><td colspan="3" style="padding:8px; border-bottom:1px solid #ececec; text-align:center; color:#777;">Loading tech payments...</td></tr>'
                    : rows.length > 0
                    ? rows.map((entry) => {
                        const paidAt = String(entry.paid_at || '-');
                        const techName = String(entry.tech_name || 'Unassigned');
                        const amount = Number(entry.amount || 0);
                        return `
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${paidAt}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${techName}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:#333;">${paymentsFormatMoney(amount)}</td>
                            </tr>
                        `;
                    }).join('')
                    : '<tr><td colspan="3" style="padding:8px; border-bottom:1px solid #ececec; text-align:center; color:#777;">No tech payments recorded</td></tr>';

                const errorHtml = errorMessage
                    ? `<div style="margin-top:8px; color:#c62828; font-size:12px;">${String(errorMessage)}</div>`
                    : '';

                const invoiceRowsHtml = invoicePayments.length > 0
                    ? invoicePayments.map((entry) => {
                        const invoiceNumber = paymentsEscapeHtml(String(entry.invoice_number || '-'));
                        const amountPaid = Number(entry.amount_paid || 0);
                        return `
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${invoiceNumber}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; color:#333;">${paymentsFormatMoney(amountPaid)}</td>
                            </tr>
                        `;
                    }).join('')
                    : '<tr><td colspan="2" style="padding:8px; border-bottom:1px solid #ececec; text-align:center; color:#777;">No invoice payments saved in Parts</td></tr>';

                contentEl.innerHTML = `
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:30px; align-items:start;">
                        <div>
                            <div style="font-weight:bold; color:#000; margin-bottom:6px;">Payments Made for Invoices</div>
                            <table style="width:100%; border-collapse:collapse;">
                                <thead>
                                    <tr style="background:#f7f7f7; text-align:left;">
                                        <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#666;">Invoice #</th>
                                        <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${invoiceRowsHtml}
                                    <tr>
                                        <td style="padding:8px; border-bottom:1px solid #ececec; font-weight:bold; color:#333;">Invoices Paid Total</td>
                                        <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; font-weight:bold; color:#333;">${paymentsFormatMoney(invoicePaymentsTotal)}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div>
                            <div style="font-weight:bold; color:#000; margin-bottom:6px;">Payments Made for Techs</div>
                            <table style="width:100%; border-collapse:collapse;">
                                <thead>
                                    <tr style="background:#f7f7f7; text-align:left;">
                                        <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#666;">Paid At</th>
                                        <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#666;">Tech</th>
                                        <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#000; text-align:right;">Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${techRowsHtml}
                                    <tr>
                                        <td colspan="2" style="padding:8px; border-bottom:1px solid #ececec; font-weight:bold; color:#333;">Tech Payments Total</td>
                                        <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; font-weight:bold; color:#333;">${paymentsFormatMoney(techPaymentsTotal)}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div style="margin-top:12px; padding-top:10px; border-top:1px solid #ddd; display:flex; justify-content:flex-end; gap:10px; align-items:center;">
                        <div style="font-weight:bold; color:#555;">Grand Total (Received Invoices + Tech Payments):</div>
                        <div style="font-weight:bold; color:#333; font-size:15px;">${paymentsFormatMoney(combinedGrandTotal)}</div>
                    </div>
                    ${errorHtml}
                `;
            }

            async function togglePaymentsRoDetails(event, roNumber) {
                if (event) event.stopPropagation();

                const rowId = paymentsSafeId(roNumber);
                const detailRow = document.getElementById(`payments-ro-details-row-${rowId}`);
                if (!detailRow) return;

                const isOpen = detailRow.style.display === 'table-row';
                if (isOpen) {
                    paymentsCloseRow(detailRow);
                    if (openPaymentsRoDetailId === rowId) {
                        openPaymentsRoDetailId = null;
                    }
                    return;
                }

                if (openPaymentsRoDetailId && openPaymentsRoDetailId !== rowId) {
                    const previousRow = document.getElementById(`payments-ro-details-row-${openPaymentsRoDetailId}`);
                    paymentsCloseRow(previousRow);
                }

                openPaymentsRoDetailId = rowId;
                const rowData = findPaymentsRow(roNumber);
                renderPaymentsRoDetailContent(roNumber, rowData, null, null);
                paymentsOpenRow(detailRow);

                try {
                    const techEntries = await loadPaymentsTechLog(roNumber);
                    if (openPaymentsRoDetailId !== rowId) return;
                    renderPaymentsRoDetailContent(roNumber, rowData, techEntries, null);
                } catch (err) {
                    console.error('Error loading RO payment details:', err);
                    if (openPaymentsRoDetailId !== rowId) return;
                    renderPaymentsRoDetailContent(roNumber, rowData, [], err.message || 'Unable to load tech payments');
                }
            }

            async function saveGrandTotalPaymentsForRo(event, roNumber) {
                if (event) event.stopPropagation();

                const rowId = paymentsSafeId(roNumber);
                const insuranceInput = document.getElementById(`payments-ins-paid-${rowId}`);
                const customerInput = document.getElementById(`payments-cust-paid-${rowId}`);
                const messageEl = document.getElementById(`payments-save-msg-${rowId}`);
                const saveBtn = document.getElementById(`payments-save-btn-${rowId}`);

                if (!insuranceInput || !customerInput || !messageEl || !saveBtn) return;

                const insurancePayment = paymentsToNumber(insuranceInput.value);
                const customerPayment = paymentsToNumber(customerInput.value);

                if (!Number.isFinite(insurancePayment) || !Number.isFinite(customerPayment) || insurancePayment < 0 || customerPayment < 0) {
                    messageEl.style.color = '#c62828';
                    messageEl.textContent = 'Enter valid non-negative currency amounts.';
                    return;
                }

                if (insurancePayment === 0 && customerPayment === 0) {
                    messageEl.style.color = '#c62828';
                    messageEl.textContent = 'Enter a payment amount greater than 0.00.';
                    return;
                }

                saveBtn.disabled = true;
                messageEl.style.color = '#555';
                messageEl.textContent = 'Saving...';

                try {
                    const response = await fetch('/api/payments/save', {
                        method: 'POST',
                        credentials: 'include',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ro: roNumber,
                            insurance_payment: insurancePayment,
                            customer_payment: customerPayment,
                            business_date: paymentsGetLocalBusinessDateISO(),
                        }),
                    });

                    const payload = await response.json();
                    if (!response.ok) {
                        throw new Error(payload.error || 'Unable to save payments');
                    }

                    messageEl.style.color = '#2e7d32';
                    messageEl.textContent = 'Saved';
                    insuranceInput.value = paymentsFormatMoney(0);
                    customerInput.value = paymentsFormatMoney(0);
                    await loadPaymentsData({ reopenEditorRo: roNumber });

                    const refreshedRowId = paymentsSafeId(roNumber);
                    const refreshedMessageEl = document.getElementById(`payments-save-msg-${refreshedRowId}`);
                    if (refreshedMessageEl) {
                        refreshedMessageEl.style.color = '#2e7d32';
                        refreshedMessageEl.textContent = 'Saved';
                    }
                } catch (err) {
                    console.error('Error saving grand total payments:', err);
                    messageEl.style.color = '#c62828';
                    messageEl.textContent = err.message || 'Unable to save payments';
                } finally {
                    saveBtn.disabled = false;
                }
            }

            function renderPaymentsTable(rows) {
                const tbody = document.getElementById('paymentsRoTableBody');
                if (!tbody) return;
                openPaymentsRoDetailId = null;

                if (!Array.isArray(rows) || rows.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="padding:20px; text-align:center; color:#999;">No open repair orders found</td></tr>';
                    applyPaymentsCloseModeToTable();
                    return;
                }

                let html = '';
                rows.forEach((row, index) => {
                    const rowBg = index % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                    const ro = row.ro || '';
                    const rowId = paymentsSafeId(ro);
                    const insuranceTotal = Number(row.insurance_total || 0);
                    const customerTotal = Number(row.customer_total || 0);
                    const insurancePaid = Number(row.insurance_paid || 0);
                    const customerPaid = Number(row.customer_paid || 0);
                    const grandTotal = Number(row.grand_total || 0);
                    const balance = Number(row.balance || 0);
                    const insuranceBalance = Math.max(0, insuranceTotal - insurancePaid);
                    const customerBalance = Math.max(0, customerTotal - customerPaid);
                    const insuranceName = String(row.insurance_name || row.insurance || '').trim();
                    const customerName = String(row.customer || '').trim();
                    const insurancePaymentEntries = Array.isArray(row.insurance_payment_entries) ? row.insurance_payment_entries : [];
                    const customerPaymentEntries = Array.isArray(row.customer_payment_entries) ? row.customer_payment_entries : [];
                    const roEscaped = paymentsEscapedRoValue(ro);

                    html += `
                        <tr style="background:${rowBg};">
                            <td class="payments-close-col" style="padding:12px 8px; border-bottom:1px solid #eee; text-align:center; width:36px; display:${paymentsCloseMode ? '' : 'none'};">
                                <input
                                    type="checkbox"
                                    class="payments-close-checkbox"
                                    data-ro="${paymentsEscapeHtml(ro)}"
                                    onchange="onPaymentsCloseRoSelect(event, '${roEscaped}')"
                                    onclick="event.stopPropagation();"
                                    style="width:16px; height:16px; cursor:pointer;"
                                />
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                <button type="button" onclick="togglePaymentsRoDetails(event, '${roEscaped}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${ro || '-'}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${row.customer || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${row.vehicle || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; color:#333;">${paymentsFormatMoney(insuranceTotal)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; color:#333;">${paymentsFormatMoney(customerTotal)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#333;">
                                <button type="button" onclick="togglePaymentsEditor(event, '${roEscaped}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${paymentsFormatMoney(grandTotal)}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#333;">
                                ${paymentsFormatMoney(balance)}
                            </td>
                        </tr>
                        <tr id="payments-ro-details-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="8" style="padding:0 16px 12px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;">
                                        <div id="payments-ro-details-content-${rowId}" style="color:#777;">Loading payment details...</div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr id="payments-editor-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="8" style="padding:0 16px 12px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    ${buildPaymentsBalancePanel({
                                        rowId,
                                        roEscaped,
                                        insuranceName,
                                        customerName,
                                        insuranceTotal,
                                        customerTotal,
                                        insurancePaid,
                                        customerPaid,
                                        insuranceBalance,
                                        customerBalance,
                                        insurancePaymentEntries,
                                        customerPaymentEntries,
                                        editable: true,
                                    })}
                                </div>
                            </td>
                        </tr>
                    `;
                });

                tbody.innerHTML = html;
                applyPaymentsCloseModeToTable();
            }

            async function loadPaymentsData(options) {
                try {
                    const response = await fetch('/api/payments/open-ros', { credentials: 'include' });
                    const payload = await response.json();
                    paymentsRows = Array.isArray(payload.rows) ? payload.rows : [];
                    paymentsTechPaymentsByRo = {};
                    openPaymentsRoDetailId = null;
                    renderPaymentsTable(paymentsRows);
                    if (!paymentsCloseMode) {
                        paymentsSelectedCloseRo = '';
                    }

                    const reopenEditorRo = options && options.reopenEditorRo ? String(options.reopenEditorRo) : '';
                    if (reopenEditorRo) {
                        const rowId = paymentsSafeId(reopenEditorRo);
                        const editorRow = document.getElementById(`payments-editor-row-${rowId}`);
                        if (editorRow) {
                            paymentsOpenRow(editorRow);
                        }
                    }
                } catch (err) {
                    console.error('Error loading payments data:', err);
                    const tbody = document.getElementById('paymentsRoTableBody');
                    if (tbody) {
                        tbody.innerHTML = '<tr><td colspan="8" style="padding:20px; text-align:center; color:#c62828;">Unable to load payments data</td></tr>';
                    }
                }
            }
        </script>
    """

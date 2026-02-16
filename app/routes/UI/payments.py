"""Payments screen content for the FlagTech UI."""


def get_payments_screen_html():
    """Return the HTML content for the Payments screen."""
    return r"""
        <div id="payments" class="screen" style="padding:20px;">
            <h1 style="text-align:center; margin-bottom:20px;">PAYMENTS</h1>

            <div style="background:#fff; border-radius:8px; padding:18px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <div style="overflow-x:auto;">
                    <table id="paymentsRoTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f5f5f5; text-align:left;">
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">RO#</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Customer</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Vehicle</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right;">Insurance (Total)</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right;">Customer (Total)</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right;">Grand Total</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555; text-align:right;">BALANCE</th>
                            </tr>
                        </thead>
                        <tbody id="paymentsRoTableBody">
                            <tr>
                                <td colspan="7" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            let paymentsRows = [];

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

            function paymentsEscapedRoValue(value) {
                return String(value || '').replace(/'/g, "\\'");
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

            async function savePaymentsForRo(event, roNumber) {
                if (event) event.stopPropagation();

                const rowId = paymentsSafeId(roNumber);
                const insuranceInput = document.getElementById(`payments-ins-paid-${rowId}`);
                const customerInput = document.getElementById(`payments-cust-paid-${rowId}`);
                const messageEl = document.getElementById(`payments-save-msg-${rowId}`);
                const saveBtn = document.getElementById(`payments-save-btn-${rowId}`);

                if (!insuranceInput || !customerInput || !messageEl || !saveBtn) return;

                const insurancePaid = paymentsToNumber(insuranceInput.value);
                const customerPaid = paymentsToNumber(customerInput.value);

                if (!Number.isFinite(insurancePaid) || !Number.isFinite(customerPaid) || insurancePaid < 0 || customerPaid < 0) {
                    messageEl.style.color = '#c62828';
                    messageEl.textContent = 'Enter valid non-negative currency amounts.';
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
                            insurance_paid: insurancePaid,
                            customer_paid: customerPaid,
                        }),
                    });

                    const payload = await response.json();
                    if (!response.ok) {
                        throw new Error(payload.error || 'Unable to save payments');
                    }

                    messageEl.style.color = '#2e7d32';
                    messageEl.textContent = 'Saved';
                    await loadPaymentsData();
                } catch (err) {
                    console.error('Error saving payments:', err);
                    messageEl.style.color = '#c62828';
                    messageEl.textContent = err.message || 'Unable to save payments';
                } finally {
                    saveBtn.disabled = false;
                }
            }

            function renderPaymentsTable(rows) {
                const tbody = document.getElementById('paymentsRoTableBody');
                if (!tbody) return;

                if (!Array.isArray(rows) || rows.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="padding:20px; text-align:center; color:#999;">No open repair orders found</td></tr>';
                    return;
                }

                let html = '';
                rows.forEach((row, index) => {
                    const rowBg = index % 2 === 0 ? '#fff' : '#f9f9f9';
                    const ro = row.ro || '';
                    const rowId = paymentsSafeId(ro);
                    const insuranceTotal = Number(row.insurance_total || 0);
                    const customerTotal = Number(row.customer_total || 0);
                    const insurancePaid = Number(row.insurance_paid || 0);
                    const customerPaid = Number(row.customer_paid || 0);
                    const grandTotal = Number(row.grand_total || 0);
                    const balance = Number(row.balance || 0);
                    const roEscaped = paymentsEscapedRoValue(ro);

                    html += `
                        <tr style="background:${rowBg};">
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${row.customer || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${row.vehicle || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; color:#333;">${paymentsFormatMoney(insuranceTotal)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; color:#333;">${paymentsFormatMoney(customerTotal)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#333;">
                                <button type="button" onclick="togglePaymentsEditor(event, '${roEscaped}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                    ${paymentsFormatMoney(grandTotal)}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#333;">${paymentsFormatMoney(balance)}</td>
                        </tr>
                        <tr id="payments-editor-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="7" style="padding:0 16px 12px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;">
                                        <div style="display:grid; grid-template-columns:auto auto auto; gap:10px 14px; align-items:center;">
                                            <div style="font-weight:bold; color:#333;">INSURANCE: ${paymentsFormatMoney(insuranceTotal)}</div>
                                            <label style="color:#555; font-weight:bold;">PAID:</label>
                                            <input id="payments-ins-paid-${rowId}" type="number" min="0" step="0.01" value="${insurancePaid.toFixed(2)}" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:170px; text-align:right;" />

                                            <div style="font-weight:bold; color:#333;">CUSTOMER: ${paymentsFormatMoney(customerTotal)}</div>
                                            <label style="color:#555; font-weight:bold;">PAID:</label>
                                            <input id="payments-cust-paid-${rowId}" type="number" min="0" step="0.01" value="${customerPaid.toFixed(2)}" style="padding:8px; border:1px solid #ccc; border-radius:4px; width:170px; text-align:right;" />
                                        </div>
                                        <div style="display:flex; align-items:center; gap:12px; margin-top:12px;">
                                            <button id="payments-save-btn-${rowId}" type="button" onclick="savePaymentsForRo(event, '${roEscaped}')" style="padding:8px 14px; background:#4caf50; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
                                                SAVE
                                            </button>
                                            <div id="payments-save-msg-${rowId}" style="font-size:12px; color:#666;"></div>
                                        </div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `;
                });

                tbody.innerHTML = html;
            }

            async function loadPaymentsData() {
                try {
                    const response = await fetch('/api/payments/open-ros', { credentials: 'include' });
                    const payload = await response.json();
                    paymentsRows = Array.isArray(payload.rows) ? payload.rows : [];
                    renderPaymentsTable(paymentsRows);
                } catch (err) {
                    console.error('Error loading payments data:', err);
                    const tbody = document.getElementById('paymentsRoTableBody');
                    if (tbody) {
                        tbody.innerHTML = '<tr><td colspan="7" style="padding:20px; text-align:center; color:#c62828;">Unable to load payments data</td></tr>';
                    }
                }
            }
        </script>
    """

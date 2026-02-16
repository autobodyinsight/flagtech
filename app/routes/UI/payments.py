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
                            </tr>
                        </thead>
                        <tbody id="paymentsRoTableBody">
                            <tr>
                                <td colspan="6" style="padding:20px; text-align:center; color:#999;">Loading...</td>
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

            async function loadPaymentsRoLog(roNumber) {
                const rowId = paymentsSafeId(roNumber);
                const target = document.getElementById(`payments-log-${rowId}`);
                if (!target) return;

                target.innerHTML = '<div style="color:#777; padding:6px 0;">Loading payment log...</div>';
                try {
                    const response = await fetch(`/api/payments/log?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' });
                    const payload = await response.json();
                    const entries = Array.isArray(payload.entries) ? payload.entries : [];

                    if (!entries.length) {
                        target.innerHTML = '<div style="color:#777; padding:6px 0;">No payment log entries.</div>';
                        return;
                    }

                    target.innerHTML = entries.map((entry) => {
                        const dateText = entry.paid_at || '-';
                        const techText = entry.tech_name || 'Unassigned';
                        return `
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#555; width:140px;">${dateText}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; color:#333;">${techText}</td>
                                <td style="padding:8px; border-bottom:1px solid #ececec; text-align:right; font-weight:bold; color:#333;">${paymentsFormatMoney(entry.amount)}</td>
                            </tr>
                        `;
                    }).join('');
                } catch (err) {
                    console.error('Error loading payment log:', err);
                    target.innerHTML = '<div style="color:#c62828; padding:6px 0;">Unable to load payment log.</div>';
                }
            }

            function togglePaymentsLog(event, roNumber) {
                if (event) event.stopPropagation();
                const rowId = paymentsSafeId(roNumber);
                const detailRow = document.getElementById(`payments-detail-row-${rowId}`);
                if (!detailRow) return;

                const isHidden = detailRow.style.display === 'none' || detailRow.style.display === '';
                if (isHidden) {
                    paymentsOpenRow(detailRow);
                    loadPaymentsRoLog(roNumber);
                    return;
                }

                paymentsCloseRow(detailRow);
            }

            function renderPaymentsTable(rows) {
                const tbody = document.getElementById('paymentsRoTableBody');
                if (!tbody) return;

                if (!Array.isArray(rows) || rows.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#999;">No open repair orders found</td></tr>';
                    return;
                }

                let html = '';
                rows.forEach((row, index) => {
                    const rowBg = index % 2 === 0 ? '#fff' : '#f9f9f9';
                    const ro = row.ro || '';
                    const rowId = paymentsSafeId(ro);

                    html += `
                        <tr style="background:${rowBg};">
                            <td style="padding:12px; border-bottom:1px solid #eee;">
                                <button type="button" onclick="togglePaymentsLog(event, '${String(ro).replace(/'/g, "\\'")}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                    ${ro || '-'}
                                </button>
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${row.customer || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${row.vehicle || '-'}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; color:#333;">${paymentsFormatMoney(row.insurance_total)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; color:#333;">${paymentsFormatMoney(row.customer_total)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#333;">${paymentsFormatMoney(row.grand_total)}</td>
                        </tr>
                        <tr id="payments-detail-row-${rowId}" style="display:none; background:${rowBg};">
                            <td colspan="6" style="padding:0 16px 12px 16px; border-bottom:1px solid #eee;">
                                <div class="ro-slide-panel" style="max-height:0; overflow:hidden; opacity:0; transition:max-height 0.22s ease, opacity 0.22s ease;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;">
                                        <div style="font-weight:bold; color:#333; margin-bottom:8px;">Payment Log</div>
                                        <table style="width:100%; border-collapse:collapse;">
                                            <thead>
                                                <tr style="background:#f7f7f7; text-align:left;">
                                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#666; width:140px;">Date</th>
                                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#666;">Tech</th>
                                                    <th style="padding:8px; border-bottom:1px solid #ddd; font-weight:bold; color:#666; text-align:right;">Amount</th>
                                                </tr>
                                            </thead>
                                            <tbody id="payments-log-${rowId}">
                                                <tr>
                                                    <td colspan="3" style="padding:10px; text-align:center; color:#777;">Click RO# to load payment log.</td>
                                                </tr>
                                            </tbody>
                                        </table>
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
                        tbody.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#c62828;">Unable to load payments data</td></tr>';
                    }
                }
            }
        </script>
    """

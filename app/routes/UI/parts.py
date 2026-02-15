"""Parts screen content for the FlagTech UI."""


def get_parts_screen_html():
    """Return the HTML content for the Parts screen."""
    return """
    <div id="parts" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">PARTS</h1>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:20px; margin-bottom:30px;">
            <div style="border:1px solid #ddd; border-radius:8px; padding:20px; background:#fafafa;">
                <h3 style="margin-bottom:15px;">Add Parts Vendor</h3>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
                    <div>
                        <label>Vendor:</label>
                        <input type="text" id="partsVendorName" style="width:100%; padding:8px; box-sizing:border-box;">
                    </div>
                    <div>
                        <label>Contact:</label>
                        <input type="text" id="partsVendorContact" style="width:100%; padding:8px; box-sizing:border-box;">
                    </div>
                </div>

                <label>Email:</label>
                <input type="email" id="partsVendorEmail" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Phone:</label>
                <input type="text" id="partsVendorPhone" style="width:100%; padding:8px; margin-bottom:15px; box-sizing:border-box;">

                <label>Street:</label>
                <input type="text" id="partsVendorStreet" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>City:</label>
                <input type="text" id="partsVendorCity" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>State:</label>
                <input type="text" id="partsVendorState" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Zip:</label>
                <input type="text" id="partsVendorZip" style="width:100%; padding:8px; margin-bottom:15px; box-sizing:border-box;">

                <button onclick="partsAddVendor()" style="padding:10px 16px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Add Vendor</button>

            </div>

            <div style="border:1px solid #ddd; border-radius:8px; padding:20px; background:#fff;">
                <h3 style="margin-bottom:15px;">Parts Vendors</h3>
                <div id="partsVendorsList"></div>
            </div>
        </div>

        <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.08);">
            <h3 style="margin:0 0 20px 0; color:#333;">Repair Orders</h3>
            <div style="overflow-x:auto;">
                <table id="partsRoTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="background:#f5f5f5; text-align:left;">
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">RO#</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Vehicle</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Parts Qty</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">On Order</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Arrival Date</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Arrived</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; color:#555;">Returned</th>
                        </tr>
                    </thead>
                    <tbody id="partsRoBody">
                        <tr>
                            <td colspan="7" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div id="partsOrderModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1000px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsOrderModal()">&times;</span>
                <h2 style="margin-bottom:20px;">Parts Order</h2>

                <div style="display:flex; justify-content:space-between; gap:20px; align-items:center; margin-bottom:15px;">
                    <div style="flex:1;">
                        <label style="font-weight:bold;">Vendor:</label>
                        <select id="partsOrderVendor" style="width:100%; padding:8px; margin-top:6px;"></select>
                    </div>
                    <div style="flex:1;">
                        <label style="font-weight:bold;">Arrival Date:</label>
                        <input type="date" id="partsOrderArrival" style="width:100%; padding:8px; margin-top:6px;" />
                    </div>
                </div>

                <hr style="margin:20px 0; border:none; border-top:1px solid #ddd;">

                <div>
                    <div style="display:flex; font-weight:bold; padding:10px 0; border-bottom:2px solid #ddd;">
                        <div style="width:40px;"></div>
                        <div style="width:80px;">Line</div>
                        <div style="flex:2;">Description</div>
                        <div style="flex:1;">Part Type</div>
                        <div style="width:120px; text-align:right;">Price</div>
                    </div>
                    <div id="partsOrderLines"></div>
                </div>

                <div style="margin-top:20px; text-align:right;">
                    <button onclick="savePartsOrder()" style="padding:10px 20px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Save</button>
                </div>
            </div>
        </div>

        <div id="partsVendorModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsVendorModal()">&times;</span>
                <h2 id="partsVendorModalName" style="margin-bottom:6px;">Vendor</h2>
                <div id="partsVendorModalContact" style="margin-bottom:12px; color:#333;"></div>
                <div id="partsVendorModalAddress" style="color:#333;"></div>
                <div id="partsVendorModalPhone" style="margin-top:6px; color:#333;"></div>
                <div id="partsVendorModalEmail" style="margin-top:4px; color:#333;"></div>

                <hr style="margin:20px 0; border:none; border-top:1px solid #ddd;">

                <h3 style="margin:0 0 12px 0; color:#333;">Invoices</h3>
                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f5f5f5; text-align:left;">
                                <th style="padding:10px; border-bottom:2px solid #ddd;">Date</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">Invoice #</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; text-align:right;">Total Cost</th>
                            </tr>
                        </thead>
                        <tbody id="partsVendorInvoicesBody">
                            <tr><td colspan="3" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>
                        </tbody>
                    </table>
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
    </div>
    """


def get_parts_script():
    """Return the JavaScript for the Parts screen."""
    return """
        let partsCurrentRo = null;
        let partsCurrentLines = [];
        let partsVendorsCache = [];
        let partsVendorModalVendor = null;

        function partsAddVendor() {
            const name = document.getElementById('partsVendorName').value.trim();
            const contactPerson = document.getElementById('partsVendorContact').value.trim();
            const email = document.getElementById('partsVendorEmail').value.trim();
            const phone = document.getElementById('partsVendorPhone').value.trim();
            const street = document.getElementById('partsVendorStreet').value.trim();
            const city = document.getElementById('partsVendorCity').value.trim();
            const state = document.getElementById('partsVendorState').value.trim();
            const zip = document.getElementById('partsVendorZip').value.trim();

            if (!name) {
                alert('Please enter a vendor name.');
                return;
            }

            fetch('/api/vendors/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ name, contact_person: contactPerson, email, phone, street, city, state, zip })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                document.getElementById('partsVendorName').value = '';
                document.getElementById('partsVendorContact').value = '';
                document.getElementById('partsVendorEmail').value = '';
                document.getElementById('partsVendorPhone').value = '';
                document.getElementById('partsVendorStreet').value = '';
                document.getElementById('partsVendorCity').value = '';
                document.getElementById('partsVendorState').value = '';
                document.getElementById('partsVendorZip').value = '';
                partsLoadVendors();
            })
            .catch(err => {
                console.error('Error saving vendor:', err);
                alert('Error saving vendor. Please try again.');
            });
        }

        function partsLoadVendors() {
            const container = document.getElementById('partsVendorsList');
            if (!container) return;

            container.innerHTML = '<p style="color:#777;">Loading...</p>';
            fetch('/api/vendors/list', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsVendorsCache = res.vendors || [];
                    if (!res.vendors || res.vendors.length === 0) {
                        container.innerHTML = '<p style="color:#777;">No vendors added yet.</p>';
                        return;
                    }

                    container.innerHTML = res.vendors.map(v => {
                        const parts = [
                            `<button type="button" onclick="openPartsVendorModal(${v.id})" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font-size:14px;">${partsEscapeHtml(v.name || '—')}</button>`
                        ];
                        if (v.phone) parts.push(v.phone);
                        if (v.email) parts.push(v.email);
                        return `<div style="padding:8px 0; border-bottom:1px solid #eee;">${parts.join(' • ')}</div>`;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading vendors:', err);
                    container.innerHTML = '<p style="color:red;">Error loading vendors.</p>';
                });
        }

        function partsFormatDisplayDate(value) {
            if (!value) return '—';
            const dateObj = new Date(value);
            if (Number.isNaN(dateObj.getTime())) return '—';
            return dateObj.toLocaleDateString();
        }

        function partsFormatCurrency(value) {
            const num = Number(value || 0);
            return `$${num.toFixed(2)}`;
        }

        function partsEscapeHtml(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function openPartsVendorModal(vendorId) {
            const vendor = (partsVendorsCache || []).find(v => Number(v.id) === Number(vendorId));
            if (!vendor) {
                alert('Vendor not found. Please refresh and try again.');
                return;
            }

            partsVendorModalVendor = vendor;

            const modal = document.getElementById('partsVendorModal');
            const nameEl = document.getElementById('partsVendorModalName');
            const contactEl = document.getElementById('partsVendorModalContact');
            const addressEl = document.getElementById('partsVendorModalAddress');
            const phoneEl = document.getElementById('partsVendorModalPhone');
            const emailEl = document.getElementById('partsVendorModalEmail');
            const invoicesBody = document.getElementById('partsVendorInvoicesBody');

            if (!modal || !nameEl || !contactEl || !addressEl || !phoneEl || !emailEl || !invoicesBody) return;

            const cityStateZip = [vendor.city, vendor.state].filter(Boolean).join(', ');
            const cityStateZipLine = [cityStateZip, vendor.zip].filter(Boolean).join(' ');

            nameEl.textContent = vendor.name || 'Vendor';
            contactEl.textContent = `Contact: ${vendor.contact_person || '—'}`;
            addressEl.innerHTML = `
                <div>${partsEscapeHtml(vendor.street || '—')}</div>
                <div>${partsEscapeHtml(cityStateZipLine || '—')}</div>
            `;
            phoneEl.textContent = `Phone: ${vendor.phone || '—'}`;
            emailEl.textContent = `Email: ${vendor.email || '—'}`;

            invoicesBody.innerHTML = '<tr><td colspan="3" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>';
            modal.style.display = 'block';

            fetch(`/api/vendors/invoices?vendor_id=${encodeURIComponent(vendor.id)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    const invoices = res.invoices || [];
                    if (invoices.length === 0) {
                        invoicesBody.innerHTML = '<tr><td colspan="3" style="padding:12px; text-align:center; color:#777;">No invoices found.</td></tr>';
                        return;
                    }

                    invoicesBody.innerHTML = invoices.map((inv, idx) => {
                        const rowBg = idx % 2 === 0 ? '#fff' : '#f9f9f9';
                        const invoiceNumber = inv.invoice_number || '—';
                        const invoiceKey = String(invoiceNumber).replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-+/g, '-').toLowerCase();
                        const toggleId = `parts-vendor-invoice-${vendor.id}-${invoiceKey}`;
                        return `
                            <tr style="background:${rowBg};">
                                <td style="padding:10px; border-bottom:1px solid #eee;">${partsFormatDisplayDate(inv.date)}</td>
                                <td style="padding:10px; border-bottom:1px solid #eee;">
                                    <button
                                        type="button"
                                        onclick="togglePartsVendorInvoiceParts(this)"
                                        data-vendor-id="${vendor.id}"
                                        data-invoice-number="${partsEscapeHtml(invoiceNumber)}"
                                        data-toggle-id="${toggleId}"
                                        style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;"
                                    >
                                        ${partsEscapeHtml(invoiceNumber)}
                                    </button>
                                </td>
                                <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(inv.total_cost)}</td>
                            </tr>
                            <tr id="${toggleId}" style="display:none; background:${rowBg};">
                                <td colspan="3" style="padding:12px; border-bottom:1px solid #eee;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px;">
                                        <div style="font-weight:bold; margin-bottom:8px;">Parts Received</div>
                                        <div id="${toggleId}-body" style="color:#777;">Loading...</div>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading vendor invoices:', err);
                    invoicesBody.innerHTML = '<tr><td colspan="3" style="padding:12px; text-align:center; color:red;">Error loading invoices.</td></tr>';
                });
        }

        function closePartsVendorModal() {
            const modal = document.getElementById('partsVendorModal');
            if (modal) modal.style.display = 'none';
        }

        function togglePartsVendorInvoiceParts(button) {
            const vendorId = button?.dataset?.vendorId;
            const invoiceNumber = button?.dataset?.invoiceNumber || '';
            const toggleId = button?.dataset?.toggleId;
            const row = document.getElementById(toggleId);
            const body = document.getElementById(`${toggleId}-body`);
            if (!row || !body) return;

            const isHidden = row.style.display === 'none' || row.style.display === '';
            row.style.display = isHidden ? 'table-row' : 'none';
            if (!isHidden) return;

            body.innerHTML = 'Loading...';

            fetch(`/api/vendors/invoice-parts?vendor_id=${encodeURIComponent(vendorId)}&invoice_number=${encodeURIComponent(invoiceNumber)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    const parts = res.parts || [];
                    if (parts.length === 0) {
                        body.innerHTML = '<div style="color:#777;">No received parts found for this invoice.</div>';
                        return;
                    }

                    body.innerHTML = `
                        <table style="width:100%; border-collapse:collapse;">
                            <thead>
                                <tr style="text-align:left; background:#f5f5f5;">
                                    <th style="padding:8px; border-bottom:1px solid #ddd; width:80px;">Line</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd;">Description</th>
                                    <th style="padding:8px; border-bottom:1px solid #ddd; width:140px; text-align:right;">Cost</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${parts.map((part) => `
                                    <tr>
                                        <td style="padding:8px; border-bottom:1px solid #eee;">${partsEscapeHtml(part.line)}</td>
                                        <td style="padding:8px; border-bottom:1px solid #eee;">${partsEscapeHtml(part.description || '—')}</td>
                                        <td style="padding:8px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(part.cost)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                })
                .catch(err => {
                    console.error('Error loading invoice parts:', err);
                    body.innerHTML = '<div style="color:red;">Error loading received parts.</div>';
                });
        }

        function partsLoadVendorOptions() {
            const select = document.getElementById('partsOrderVendor');
            if (!select) return;

            select.innerHTML = '<option value="">Select vendor...</option>';

            fetch('/api/vendors/list', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (!res.vendors || res.vendors.length === 0) {
                        return;
                    }
                    res.vendors.forEach(v => {
                        const option = document.createElement('option');
                        option.value = v.id;
                        option.textContent = v.name;
                        option.dataset.name = v.name;
                        select.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error('Error loading vendors:', err);
                });
        }

        function partsLoadRos() {
            const tbody = document.getElementById('partsRoBody');
            if (!tbody) return;

            tbody.innerHTML = '<tr><td colspan="7" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>';

            fetch('/api/parts/ros', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (!res.ros || res.ros.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="7" style="padding:20px; text-align:center; color:#999;">No repair orders found</td></tr>';
                        return;
                    }

                    tbody.innerHTML = res.ros.map((ro, idx) => {
                        const rowBg = idx % 2 === 0 ? '#fff' : '#f9f9f9';
                        const rowId = String(ro.ro || '').replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-+/g, '-').toLowerCase();
                        const arrival = ro.arrival_date ? new Date(ro.arrival_date).toLocaleDateString() : '—';
                        return `
                            <tr style="background:${rowBg};">
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.ro}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.vehicle || '—'}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                    <button class="link-button" onclick="openPartsOrderModal('${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                        ${ro.parts_qty || 0}
                                    </button>
                                </td>
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">
                                    <button class="link-button" onclick="togglePartsReceived('${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                        ${ro.on_order || 0}
                                    </button>
                                </td>
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${arrival}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.arrived || 0}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee; color:#333;">${ro.returned || 0}</td>
                            </tr>
                            <tr id="parts-recv-row-${rowId}" style="display:none; background:${rowBg};">
                                <td colspan="7" style="padding:12px 16px; border-bottom:1px solid #eee;">
                                    <div style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;">
                                        <div style="font-weight:bold; margin-bottom:8px;">Received Parts</div>
                                        <div style="display:flex; font-weight:bold; padding:8px 0; border-bottom:1px solid #ddd;">
                                            <div style="width:40px;"></div>
                                            <div style="width:80px;">Line</div>
                                            <div style="flex:2;">Description</div>
                                            <div style="flex:1;">Vendor</div>
                                            <div style="width:120px; text-align:right;">Cost</div>
                                        </div>
                                        <div id="parts-recv-body-${rowId}"></div>
                                        <div style="margin-top:12px; text-align:right;">
                                            <button onclick="savePartsReceived('${ro.ro}')" style="padding:8px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Save</button>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading parts ROs:', err);
                    tbody.innerHTML = '<tr><td colspan="7" style="padding:20px; text-align:center; color:red;">Error loading repair orders.</td></tr>';
                });
        }

        function togglePartsReceived(ro) {
            const rowId = String(ro || '').replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-+/g, '-').toLowerCase();
            const row = document.getElementById(`parts-recv-row-${rowId}`);
            const body = document.getElementById(`parts-recv-body-${rowId}`);
            if (!row || !body) return;

            const isHidden = row.style.display === 'none' || row.style.display === '';
            row.style.display = isHidden ? 'table-row' : 'none';
            if (isHidden) {
                loadPartsReceived(ro);
            }
        }

        function loadPartsReceived(ro) {
            const rowId = String(ro || '').replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-+/g, '-').toLowerCase();
            const body = document.getElementById(`parts-recv-body-${rowId}`);
            if (!body) return;

            body.innerHTML = '<div style="padding:8px; color:#777;">Loading...</div>';

            Promise.all([
                fetch(`/api/parts/ro-lines?ro=${encodeURIComponent(ro)}`, { credentials: 'include' }).then(r => r.json()),
                fetch(`/api/parts/received?ro=${encodeURIComponent(ro)}`, { credentials: 'include' }).then(r => r.json())
            ])
            .then(([linesRes, receivedRes]) => {
                const lines = linesRes.lines || [];
                const received = receivedRes.items || [];
                const receivedMap = {};
                received.forEach(item => {
                    receivedMap[item.line_id] = item;
                });

                if (lines.length === 0) {
                    body.innerHTML = '<div style="padding:8px; color:#777;">No parts found.</div>';
                    return;
                }

                body.innerHTML = lines.map(line => {
                    const existing = receivedMap[line.id] || {};
                    const checked = existing.line_id ? 'checked' : '';
                    const vendorVal = existing.vendor ? existing.vendor.replace(/"/g, '&quot;') : '';
                    const costVal = existing.cost ? Number(existing.cost).toFixed(2) : '';
                    return `
                        <div style="display:flex; align-items:center; padding:8px 0; border-bottom:1px solid #eee;">
                            <div style="width:40px;"><input type="checkbox" class="parts-recv-check" data-id="${line.id}" ${checked} /></div>
                            <div style="width:80px;">${line.line || '—'}</div>
                            <div style="flex:2;">${line.description || ''}</div>
                            <div style="flex:1;"><input type="text" class="parts-recv-vendor" data-id="${line.id}" value="${vendorVal}" style="width:100%; padding:6px;" placeholder="Vendor" /></div>
                            <div style="width:120px; text-align:right;"><input type="number" step="0.01" class="parts-recv-cost" data-id="${line.id}" value="${costVal}" style="width:100px; padding:6px;" placeholder="0.00" /></div>
                        </div>
                    `;
                }).join('');
            })
            .catch(err => {
                console.error('Error loading received parts:', err);
                body.innerHTML = '<div style="padding:8px; color:red;">Error loading parts.</div>';
            });
        }

        function savePartsReceived(ro) {
            const rowId = String(ro || '').replace(/[^a-zA-Z0-9_-]/g, '-').replace(/-+/g, '-').toLowerCase();
            const checks = Array.from(document.querySelectorAll(`#parts-recv-body-${rowId} .parts-recv-check`));
            const items = [];

            checks.forEach(check => {
                if (!check.checked) return;
                const lineId = parseInt(check.dataset.id, 10);
                const vendorInput = document.querySelector(`#parts-recv-body-${rowId} .parts-recv-vendor[data-id="${lineId}"]`);
                const costInput = document.querySelector(`#parts-recv-body-${rowId} .parts-recv-cost[data-id="${lineId}"]`);
                const vendor = (vendorInput?.value || '').trim();
                const costVal = costInput?.value ? parseFloat(costInput.value) : null;
                if (!vendor) {
                    return;
                }
                items.push({
                    line_id: lineId,
                    vendor,
                    cost: Number.isFinite(costVal) ? costVal : null
                });
            });

            if (items.length === 0) {
                alert('Please select at least one part and enter vendor.');
                return;
            }

            fetch('/api/parts/receive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ ro, items })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                partsLoadRos();
                loadPartsReceived(ro);
            })
            .catch(err => {
                console.error('Error saving received parts:', err);
                alert('Error saving received parts.');
            });
        }

        function openPartsOrderModal(ro) {
            partsCurrentRo = ro;
            const modal = document.getElementById('partsOrderModal');
            const linesContainer = document.getElementById('partsOrderLines');

            linesContainer.innerHTML = '<div style="padding:12px; color:#777;">Loading...</div>';
            partsLoadVendorOptions();

            fetch(`/api/parts/ro-lines?ro=${encodeURIComponent(ro)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsCurrentLines = res.lines || [];
                    if (partsCurrentLines.length === 0) {
                        linesContainer.innerHTML = '<div style="padding:12px; color:#777;">No parts found.</div>';
                        return;
                    }

                    linesContainer.innerHTML = partsCurrentLines.map(line => {
                        const price = line.price ? `$${Number(line.price).toFixed(2)}` : '—';
                        return `
                            <div style="display:flex; align-items:center; padding:10px 0; border-bottom:1px solid #eee;">
                                <div style="width:40px;"><input type="checkbox" class="parts-order-check" data-id="${line.id}" /></div>
                                <div style="width:80px;">${line.line || '—'}</div>
                                <div style="flex:2;">${line.description || ''}</div>
                                <div style="flex:1;">${line.part_type || '—'}</div>
                                <div style="width:120px; text-align:right;">${price}</div>
                            </div>
                        `;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading parts lines:', err);
                    linesContainer.innerHTML = '<div style="padding:12px; color:red;">Error loading parts.</div>';
                });

            modal.style.display = 'block';
        }

        function closePartsOrderModal() {
            const modal = document.getElementById('partsOrderModal');
            if (modal) modal.style.display = 'none';
        }

        function savePartsOrder() {
            if (!partsCurrentRo) {
                alert('No RO selected.');
                return;
            }

            const vendorSelect = document.getElementById('partsOrderVendor');
            const vendorId = vendorSelect.value;
            const vendorName = vendorSelect.options[vendorSelect.selectedIndex]?.dataset?.name || '';
            const arrivalDate = document.getElementById('partsOrderArrival').value;

            const checked = Array.from(document.querySelectorAll('.parts-order-check:checked'))
                .map(el => parseInt(el.dataset.id, 10))
                .filter(id => !Number.isNaN(id));

            if (!vendorId) {
                alert('Please select a vendor.');
                return;
            }

            if (!arrivalDate) {
                alert('Please select an arrival date.');
                return;
            }

            if (checked.length === 0) {
                alert('Please select at least one part.');
                return;
            }

            fetch('/api/parts/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    ro: partsCurrentRo,
                    vendor_id: vendorId,
                    vendor_name: vendorName,
                    arrival_date: arrivalDate,
                    ordered_lines: checked
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                closePartsOrderModal();
                partsLoadRos();
            })
            .catch(err => {
                console.error('Error saving parts order:', err);
                alert('Error saving parts order. Please try again.');
            });
        }
    """

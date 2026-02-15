"""Parts screen content for the FlagTech UI."""


def get_parts_screen_html():
    """Return the HTML content for the Parts screen."""
    return """
    <div id="parts" class="screen" style="padding:20px;">
        <div style="display:grid; grid-template-columns:1fr auto 1fr; align-items:center; margin-bottom:20px;">
            <div style="display:flex; justify-content:flex-start;">
                <button onclick="openPartsAddVendorModal()" style="padding:10px 16px; background-color:#3c4142; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">+ VENDOR</button>
            </div>
            <h1 style="text-align:center; margin:0;">PARTS</h1>
            <div style="display:flex; justify-content:flex-end;">
                <button onclick="openPartsVendorsModal()" style="padding:10px 16px; background-color:#3c4142; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Vendors</button>
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

        <div id="partsAddVendorModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:720px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsAddVendorModal()">&times;</span>
                <h2 style="margin-bottom:16px;">Add Parts Vendor</h2>

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

                <label>Type:</label>
                <select id="partsVendorType" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">
                    <option value="">Select type...</option>
                    <option value="OEM">OEM</option>
                    <option value="AFTERMARKET">Aftermarket</option>
                    <option value="USED">Used</option>
                    <option value="OTHER">Other</option>
                </select>

                <label>Email:</label>
                <input type="email" id="partsVendorEmail" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Phone:</label>
                <input type="text" id="partsVendorPhone" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Street:</label>
                <input type="text" id="partsVendorStreet" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:10px;">
                    <div>
                        <label>City:</label>
                        <input type="text" id="partsVendorCity" style="width:100%; padding:8px; box-sizing:border-box;">
                    </div>
                    <div>
                        <label>State:</label>
                        <input type="text" id="partsVendorState" style="width:100%; padding:8px; box-sizing:border-box;">
                    </div>
                    <div>
                        <label>Zip:</label>
                        <input type="text" id="partsVendorZip" style="width:100%; padding:8px; box-sizing:border-box;">
                    </div>
                </div>

                <div style="text-align:right; margin-top:16px;">
                    <button onclick="partsAddVendor()" style="padding:10px 18px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Save</button>
                </div>
            </div>
        </div>

        <div id="partsVendorsModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1050px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsVendorsModal()">&times;</span>
                <h2 style="margin-bottom:16px;">Vendors</h2>
                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f5f5f5; text-align:left;">
                                <th style="padding:10px; border-bottom:2px solid #ddd;">VENDOR</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">TYPE</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">PHONE</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">EMAIL</th>
                            </tr>
                        </thead>
                        <tbody id="partsVendorsTableBody">
                            <tr><td colspan="4" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>
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

        function partsAddVendor() {
            const name = document.getElementById('partsVendorName').value.trim();
            const vendorType = document.getElementById('partsVendorType').value.trim();
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
                body: JSON.stringify({
                    name,
                    vendor_type: vendorType,
                    contact_person: contactPerson,
                    email,
                    phone,
                    street,
                    city,
                    state,
                    zip
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                partsClearVendorForm();
                closePartsAddVendorModal();
                partsLoadVendors(true);
            })
            .catch(err => {
                console.error('Error saving vendor:', err);
                alert('Error saving vendor. Please try again.');
            });
        }

        function partsLoadVendors(renderTable = false) {
            fetch('/api/vendors/list', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsVendorsCache = res.vendors || [];
                    if (renderTable) {
                        partsRenderVendorsTable();
                    }
                })
                .catch(err => {
                    console.error('Error loading vendors:', err);
                    if (renderTable) {
                        const body = document.getElementById('partsVendorsTableBody');
                        if (body) {
                            body.innerHTML = '<tr><td colspan="4" style="padding:12px; text-align:center; color:red;">Error loading vendors.</td></tr>';
                        }
                    }
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

        function openPartsAddVendorModal() {
            const modal = document.getElementById('partsAddVendorModal');
            if (modal) modal.style.display = 'block';
        }

        function closePartsAddVendorModal() {
            const modal = document.getElementById('partsAddVendorModal');
            if (modal) modal.style.display = 'none';
        }

        function partsClearVendorForm() {
            const ids = [
                'partsVendorName',
                'partsVendorType',
                'partsVendorContact',
                'partsVendorEmail',
                'partsVendorPhone',
                'partsVendorStreet',
                'partsVendorCity',
                'partsVendorState',
                'partsVendorZip'
            ];
            ids.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
        }

        function openPartsVendorsModal() {
            const modal = document.getElementById('partsVendorsModal');
            const body = document.getElementById('partsVendorsTableBody');
            if (!modal || !body) return;

            body.innerHTML = '<tr><td colspan="4" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>';
            modal.style.display = 'block';
            partsLoadVendors(true);
        }

        function closePartsVendorsModal() {
            const modal = document.getElementById('partsVendorsModal');
            if (modal) modal.style.display = 'none';
        }

        function partsRenderVendorsTable() {
            const body = document.getElementById('partsVendorsTableBody');
            if (!body) return;

            if (!partsVendorsCache || partsVendorsCache.length === 0) {
                body.innerHTML = '<tr><td colspan="4" style="padding:12px; text-align:center; color:#777;">No vendors found.</td></tr>';
                return;
            }

            body.innerHTML = partsVendorsCache.map((vendor, idx) => {
                const rowBg = idx % 2 === 0 ? '#fff' : '#f9f9f9';
                const detailRowId = `parts-vendor-detail-row-${vendor.id}`;
                const detailWrapId = `parts-vendor-detail-wrap-${vendor.id}`;
                return `
                    <tr style="background:${rowBg};">
                        <td style="padding:10px; border-bottom:1px solid #eee;">
                            <button id="parts-vendor-main-name-${vendor.id}" type="button" onclick="togglePartsVendorRow(${vendor.id})" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font-size:14px;">
                                ${partsEscapeHtml(vendor.name || '—')}
                            </button>
                        </td>
                        <td id="parts-vendor-main-type-${vendor.id}" style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(vendor.vendor_type || '—')}</td>
                        <td id="parts-vendor-main-phone-${vendor.id}" style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(vendor.phone || '—')}</td>
                        <td id="parts-vendor-main-email-${vendor.id}" style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(vendor.email || '—')}</td>
                    </tr>
                    <tr id="${detailRowId}" style="display:none; background:${rowBg};">
                        <td colspan="4" style="padding:12px; border-bottom:1px solid #eee;">
                            <div id="${detailWrapId}" style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:12px;"></div>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function togglePartsVendorRow(vendorId) {
            const row = document.getElementById(`parts-vendor-detail-row-${vendorId}`);
            const wrap = document.getElementById(`parts-vendor-detail-wrap-${vendorId}`);
            if (!row || !wrap) return;

            const isHidden = row.style.display === 'none' || row.style.display === '';
            row.style.display = isHidden ? 'table-row' : 'none';
            if (!isHidden) return;

            const vendor = (partsVendorsCache || []).find(v => Number(v.id) === Number(vendorId));
            if (!vendor) {
                wrap.innerHTML = '<div style="color:red;">Vendor not found.</div>';
                return;
            }

            wrap.innerHTML = partsBuildVendorDetailHtml(vendor);
            partsSetVendorEditMode(vendorId, false);
            partsLoadVendorInvoices(vendorId);
        }

        function partsBuildVendorDetailHtml(vendor) {
            const id = vendor.id;
            const selectedType = String(vendor.vendor_type || '').toUpperCase();
            const optionSelected = (value) => selectedType === value ? 'selected' : '';
            return `
                <div style="font-weight:bold; margin-bottom:8px;">Vendor Information</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:8px;">
                    <div>
                        <label>Vendor Name</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="name" type="text" value="${partsEscapeHtml(vendor.name || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                    <div>
                        <label>Contact Person</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="contact_person" type="text" value="${partsEscapeHtml(vendor.contact_person || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:8px;">
                    <div>
                        <label>Type</label>
                        <select class="parts-vendor-edit-field-${id}" data-field="vendor_type" style="width:100%; padding:8px; box-sizing:border-box;">
                            <option value="" ${optionSelected('')}>Select type...</option>
                            <option value="OEM" ${optionSelected('OEM')}>OEM</option>
                            <option value="AFTERMARKET" ${optionSelected('AFTERMARKET')}>Aftermarket</option>
                            <option value="USED" ${optionSelected('USED')}>Used</option>
                            <option value="OTHER" ${optionSelected('OTHER')}>Other</option>
                        </select>
                    </div>
                    <div>
                        <label>Phone</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="phone" type="text" value="${partsEscapeHtml(vendor.phone || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                    <div>
                        <label>Email</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="email" type="email" value="${partsEscapeHtml(vendor.email || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:10px; margin-bottom:8px;">
                    <div>
                        <label>Street</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="street" type="text" value="${partsEscapeHtml(vendor.street || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                    <div>
                        <label>City</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="city" type="text" value="${partsEscapeHtml(vendor.city || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                    <div>
                        <label>State</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="state" type="text" value="${partsEscapeHtml(vendor.state || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                    <div>
                        <label>Zip</label>
                        <input class="parts-vendor-edit-field-${id}" data-field="zip" type="text" value="${partsEscapeHtml(vendor.zip || '')}" style="width:100%; padding:8px; box-sizing:border-box;" />
                    </div>
                </div>
                <div style="text-align:right; margin:10px 0 14px 0;">
                    <button id="parts-vendor-edit-btn-${id}" data-mode="view" onclick="partsToggleVendorEdit(${id})" style="padding:8px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">EDIT</button>
                </div>
                <div style="font-weight:bold; margin-bottom:8px;">Invoices</div>
                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f5f5f5; text-align:left;">
                                <th style="padding:8px; border-bottom:1px solid #ddd;">DATE</th>
                                <th style="padding:8px; border-bottom:1px solid #ddd;">INVOICE#</th>
                                <th style="padding:8px; border-bottom:1px solid #ddd; text-align:right;">TOTAL</th>
                            </tr>
                        </thead>
                        <tbody id="parts-vendor-invoices-${id}">
                            <tr><td colspan="3" style="padding:8px; color:#777; text-align:center;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            `;
        }

        function partsSetVendorEditMode(vendorId, isEditable) {
            const fields = document.querySelectorAll(`.parts-vendor-edit-field-${vendorId}`);
            fields.forEach(field => {
                field.disabled = !isEditable;
                field.style.background = isEditable ? '#fff' : '#f4f4f4';
            });
            const button = document.getElementById(`parts-vendor-edit-btn-${vendorId}`);
            if (button) {
                button.dataset.mode = isEditable ? 'edit' : 'view';
                button.textContent = 'EDIT';
            }
        }

        function partsToggleVendorEdit(vendorId) {
            const button = document.getElementById(`parts-vendor-edit-btn-${vendorId}`);
            if (!button) return;

            const isEditMode = button.dataset.mode === 'edit';
            if (!isEditMode) {
                partsSetVendorEditMode(vendorId, true);
                return;
            }

            const fields = document.querySelectorAll(`.parts-vendor-edit-field-${vendorId}`);
            const payload = { vendor_id: vendorId };
            fields.forEach(field => {
                payload[field.dataset.field] = (field.value || '').trim();
            });

            if (!payload.name) {
                alert('Vendor name is required.');
                return;
            }

            fetch('/api/vendors/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(payload)
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }

                const updated = res.vendor || {};
                partsVendorsCache = (partsVendorsCache || []).map(v => Number(v.id) === Number(vendorId) ? { ...v, ...updated } : v);

                const typeEl = document.getElementById(`parts-vendor-main-type-${vendorId}`);
                const phoneEl = document.getElementById(`parts-vendor-main-phone-${vendorId}`);
                const emailEl = document.getElementById(`parts-vendor-main-email-${vendorId}`);
                const nameEl = document.getElementById(`parts-vendor-main-name-${vendorId}`);

                if (nameEl) nameEl.textContent = updated.name || '—';
                if (typeEl) typeEl.textContent = updated.vendor_type || '—';
                if (phoneEl) phoneEl.textContent = updated.phone || '—';
                if (emailEl) emailEl.textContent = updated.email || '—';

                partsSetVendorEditMode(vendorId, false);
            })
            .catch(err => {
                console.error('Error updating vendor:', err);
                alert('Error updating vendor. Please try again.');
            });
        }

        function partsLoadVendorInvoices(vendorId) {
            const tbody = document.getElementById(`parts-vendor-invoices-${vendorId}`);
            if (!tbody) return;

            tbody.innerHTML = '<tr><td colspan="3" style="padding:8px; color:#777; text-align:center;">Loading...</td></tr>';

            fetch(`/api/vendors/invoices?vendor_id=${encodeURIComponent(vendorId)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    const invoices = res.invoices || [];
                    if (invoices.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="3" style="padding:8px; color:#777; text-align:center;">No invoices found.</td></tr>';
                        return;
                    }

                    tbody.innerHTML = invoices.map(inv => `
                        <tr>
                            <td style="padding:8px; border-bottom:1px solid #eee;">${partsFormatDisplayDate(inv.date)}</td>
                            <td style="padding:8px; border-bottom:1px solid #eee;">${partsEscapeHtml(inv.invoice_number || '—')}</td>
                            <td style="padding:8px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(inv.total_cost)}</td>
                        </tr>
                    `).join('');
                })
                .catch(err => {
                    console.error('Error loading vendor invoices:', err);
                    tbody.innerHTML = '<tr><td colspan="3" style="padding:8px; color:red; text-align:center;">Error loading invoices.</td></tr>';
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

"""Parts screen content for the FlagTech UI."""


def get_parts_screen_html():
    """Return the HTML content for the Parts screen."""
    return """
    <div id="parts" class="screen" style="padding:20px;">
        <style>
            #parts .dashboard-ro-title-tab {
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
            #parts .dashboard-ro-table-wrap {
                background: #ffffff;
                border-radius: 4px;
                overflow: hidden;
            }
            #parts .dashboard-header-row th,
            #parts .dashboard-header-cell {
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
            #partsRoBody tr.parts-ro-main-row td {
                background: #ffffff;
                border: none;
                border-bottom: 1px solid rgba(0,0,0,0.06) !important;
                min-height: 48px;
                height: 48px;
                vertical-align: middle;
                color: #333;
            }
            #partsRoBody tr.parts-ro-main-row:hover td {
                background: rgba(0,0,0,0.04) !important;
            }
        </style>
        <div style="display:flex; align-items:center; justify-content:center; gap:28px; margin-bottom:20px;">
            <h1 style="text-align:center; margin:0;">PARTS</h1>
            <div>
                <button onclick="openPartsVendorsModal()" style="padding:10px 16px; background-color:#b22222; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Manage Vendors</button>
            </div>
        </div>

        <div style="margin-top:8px;">
            <div style="display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:0; position:relative;">
                <h3 class="dashboard-ro-title-tab" style="margin:0; color:#333;">Repair Orders</h3>
            </div>
            <div class="dashboard-ro-table-wrap" style="overflow-x:auto;">
                <table id="partsRoTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr class="dashboard-header-row">
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">RO#</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Vehicle</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Estimator</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Tech</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Parts Qty</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">On Order</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Arrived</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Returned</th>
                        </tr>
                    </thead>
                    <tbody id="partsRoBody">
                        <tr>
                            <td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td>
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
                        <div style="width:40px;"><input type="checkbox" id="partsOrderSelectAll" onchange="partsToggleOrderSelectAll(this.checked)" /></div>
                        <div style="width:80px;"><button type="button" onclick="partsSortOrderLines('line')" style="background:none; border:none; font-weight:bold; cursor:pointer; padding:0;">Line <span id="partsOrderSortLine"></span></button></div>
                        <div style="flex:2;">Description</div>
                        <div style="flex:1; display:flex; align-items:center; gap:8px;">
                            <button type="button" onclick="partsSortOrderLines('part_type')" style="background:none; border:none; font-weight:bold; cursor:pointer; padding:0;">Part Type <span id="partsOrderSortPartType"></span></button>
                            <select id="partsOrderTypeQuickSelect" onchange="partsSelectByOrderType(this.value)" style="padding:4px; font-size:12px;">
                                <option value="">Select Type</option>
                                <option value="OEM">OEM</option>
                                <option value="A/M">A/M</option>
                                <option value="LKQ">LKQ</option>
                            </select>
                        </div>
                        <div style="width:80px; text-align:right;">QTY</div>
                        <div style="width:120px; text-align:right;"><button type="button" onclick="partsSortOrderLines('price')" style="background:none; border:none; font-weight:bold; cursor:pointer; padding:0;">Price <span id="partsOrderSortPrice"></span></button></div>
                    </div>
                    <div id="partsOrderLines"></div>
                </div>

                <div style="margin-top:20px; text-align:right;">
                    <button onclick="savePartsOrder()" style="padding:10px 20px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Save</button>
                </div>
            </div>
        </div>

        <div id="partsOnOrderModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1100px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsOnOrderModal()">&times;</span>
                <h2 style="margin-bottom:14px;">ON ORDER</h2>

                <div style="display:flex; gap:10px; margin-bottom:12px;">
                    <button type="button" id="partsOnOrderReceiveBtn" onclick="partsEnterReceiveMode()" style="padding:10px 16px; background-color:#b22222; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Receive</button>
                    <button type="button" id="partsOnOrderAddPartBtn" onclick="partsAddOnOrderManualLine()" style="display:none; padding:10px 16px; background-color:#b22222; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">+ Add Part</button>
                    <button type="button" id="partsOnOrderSaveBtn" onclick="partsSaveOnOrderReceive()" style="display:none; padding:10px 16px; background-color:#b22222; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Save</button>
                </div>

                <div id="partsOnOrderInvoiceWrap" style="display:none; margin-bottom:14px;">
                    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; max-width:820px;">
                        <div>
                            <label>Vendor:</label>
                            <select id="partsOnOrderVendorInput" style="width:100%; padding:8px; box-sizing:border-box;">
                                <option value="">Select vendor...</option>
                            </select>
                        </div>
                        <div>
                            <label>Invoice Number:</label>
                            <input type="text" id="partsOnOrderInvoiceNumber" style="width:100%; padding:8px; box-sizing:border-box;" />
                        </div>
                        <div>
                            <label>Total Invoice Amount:</label>
                            <input type="number" id="partsOnOrderInvoiceTotal" step="0.01" min="0" style="width:100%; padding:8px; box-sizing:border-box;" />
                        </div>
                    </div>
                </div>

                <div id="partsOnOrderValidation" style="display:none; margin-bottom:12px; padding:10px 12px; border:1px solid #c62828; background:#fdecea; color:#7f1d1d; border-radius:4px;"></div>

                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="parts-header-row">
                                <th id="partsOnOrderCheckHeader" style="padding:10px; border-bottom:2px solid #ddd; width:40px; display:none;"></th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:80px;">Line</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">Description</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:80px; text-align:right;">QTY</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:170px;">Part #</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:110px; text-align:right;">List</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:180px;">Vendor</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:120px;">ETA</th>
                                <th id="partsOnOrderCostHeader" style="padding:10px; border-bottom:2px solid #ddd; width:110px; text-align:right; display:none;">Cost</th>
                            </tr>
                        </thead>
                        <tbody id="partsOnOrderBody">
                            <tr><td colspan="9" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="partsArrivedModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1100px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsArrivedModal()">&times;</span>
                <h2 style="margin-bottom:14px;">ARRIVED</h2>

                <div style="display:flex; gap:10px; margin-bottom:12px;">
                    <button onclick="partsReturnArrivedLines()" style="padding:10px 16px; background-color:#b22222; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Return</button>
                </div>

                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="parts-header-row">
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:40px;"></th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:80px;">Line</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">Description</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:170px;">Part #</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:180px;">Vendor</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:110px; text-align:right;">List</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:110px; text-align:right;">Cost</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:120px;">Arrived</th>
                            </tr>
                        </thead>
                        <tbody id="partsArrivedBody">
                            <tr><td colspan="8" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="partsReturnedModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1100px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsReturnedModal()">&times;</span>
                <h2 style="margin-bottom:14px;">RETURNED HISTORY</h2>

                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="parts-header-row">
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:80px;">Line</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">Description</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:170px;">Part #</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:180px;">Vendor</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:110px; text-align:right;">Cost</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd; width:120px;">Return Date</th>
                            </tr>
                        </thead>
                        <tbody id="partsReturnedBody">
                            <tr><td colspan="6" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="partsVendorsModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1050px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closePartsVendorsModal()">&times;</span>
                <h2 style="margin-bottom:16px;">Manage Vendors</h2>

                <div style="background:#fff; border:1px solid #ddd; border-radius:6px; padding:12px; margin-bottom:14px;">
                    <div style="font-weight:bold; margin-bottom:10px;">Add Vendor</div>

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

                    <div style="text-align:right; margin-top:10px;">
                        <button onclick="partsAddVendor()" style="padding:10px 18px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Save</button>
                    </div>
                </div>

                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f5f5f5; text-align:left;">
                                <th style="padding:10px; border-bottom:2px solid #ddd;">VENDOR</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">TYPE</th>
                                <th style="padding:10px; border-bottom:2px solid #ddd;">PHONE</th>
                            </tr>
                        </thead>
                        <tbody id="partsVendorsTableBody">
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
        let partsOrderSelectedIds = new Set();
        let partsOrderSortField = 'line';
        let partsOrderSortDirection = 'asc';
        let partsVendorsCache = [];
        let partsOnOrderRo = null;
        let partsOnOrderLines = [];
        let partsOnOrderManualLines = [];
        let partsOnOrderReceiveMode = false;
        let partsArrivedRo = null;
        let partsArrivedItems = [];
        let partsReturnedRo = null;
        let partsReturnedItems = [];

        function partsAddVendor() {
            const name = document.getElementById('partsVendorName').value.trim();
            const vendorType = document.getElementById('partsVendorType').value.trim();
            const contactPerson = document.getElementById('partsVendorContact').value.trim();
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
                partsLoadVendors(true);
            })
            .catch(err => {
                console.error('Error saving vendor:', err);
                alert('Error saving vendor. Please try again.');
            });
        }

        function partsLoadVendors(renderTable = false) {
            return fetch('/api/vendors/list', { credentials: 'include' })
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
                            body.innerHTML = '<tr><td colspan="3" style="padding:12px; text-align:center; color:red;">Error loading vendors.</td></tr>';
                        }
                    }
                    throw err;
                });
        }

        function partsPopulateOnOrderVendorDropdown(selectedValue = '') {
            const select = document.getElementById('partsOnOrderVendorInput');
            if (!select) return;

            const currentValue = selectedValue || select.value || '';
            select.innerHTML = '<option value="">Select vendor...</option>';

            const names = Array.from(new Set((partsVendorsCache || [])
                .map(v => String(v.name || '').trim())
                .filter(Boolean)))
                .sort((a, b) => a.localeCompare(b));

            names.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            });

            if (currentValue && names.includes(currentValue)) {
                select.value = currentValue;
            }
        }

        function partsFormatDisplayDate(value) {
            return partsFormatBusinessDate(value);
        }

        function partsFormatBusinessDate(value) {
            if (!value) return '—';
            const raw = String(value).trim();
            if (!raw) return '—';
            const datePart = raw.split('T')[0];
            const match = datePart.match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
            if (!match) return '—';
            const [, year, month, day] = match;
            return `${month}-${day}-${year.slice(-2)}`;
        }

        function partsGetLocalBusinessDateIso() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
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
            openPartsVendorsModal();
        }

        function closePartsAddVendorModal() {
            closePartsVendorsModal();
        }

        function partsClearVendorForm() {
            const ids = [
                'partsVendorName',
                'partsVendorType',
                'partsVendorContact',
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

            body.innerHTML = '<tr><td colspan="3" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>';
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
                body.innerHTML = '<tr><td colspan="3" style="padding:12px; text-align:center; color:#777;">No vendors found.</td></tr>';
                return;
            }

            body.innerHTML = partsVendorsCache.map((vendor, idx) => {
                const rowBg = idx % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
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
                    </tr>
                    <tr id="${detailRowId}" style="display:none; background:${rowBg};">
                        <td colspan="3" style="padding:12px; border-bottom:1px solid #eee;">
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
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:8px;">
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
                const nameEl = document.getElementById(`parts-vendor-main-name-${vendorId}`);

                if (nameEl) nameEl.textContent = updated.name || '—';
                if (typeEl) typeEl.textContent = updated.vendor_type || '—';
                if (phoneEl) phoneEl.textContent = updated.phone || '—';

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

                    tbody.innerHTML = invoices.map(inv => {
                        const invoiceNumber = String(inv.invoice_number || '').trim();
                        const invoiceDisplay = partsEscapeHtml(invoiceNumber || '—');
                        const safeKey = String(invoiceNumber || 'blank').replace(/[^a-zA-Z0-9_-]/g, '_');
                        const detailRowId = `parts-vendor-invoice-detail-row-${vendorId}-${safeKey}`;
                        const detailWrapId = `parts-vendor-invoice-detail-wrap-${vendorId}-${safeKey}`;
                        return `
                            <tr>
                                <td style="padding:8px; border-bottom:1px solid #eee;">${partsFormatBusinessDate(inv.date)}</td>
                                <td style="padding:8px; border-bottom:1px solid #eee;">
                                    <button type="button" onclick="togglePartsVendorInvoiceRow(${vendorId}, ${JSON.stringify(invoiceNumber)}, ${JSON.stringify(safeKey)})" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                        ${invoiceDisplay}
                                    </button>
                                </td>
                                <td style="padding:8px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(inv.total_cost)}</td>
                            </tr>
                            <tr id="${detailRowId}" style="display:none;">
                                <td colspan="3" style="padding:10px 8px; border-bottom:1px solid #eee;">
                                    <div id="${detailWrapId}" style="background:#fafafa; border:1px solid #ddd; border-radius:6px; padding:10px;">Loading...</div>
                                </td>
                            </tr>
                        `;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading vendor invoices:', err);
                    tbody.innerHTML = '<tr><td colspan="3" style="padding:8px; color:red; text-align:center;">Error loading invoices.</td></tr>';
                });
        }

        function togglePartsVendorInvoiceRow(vendorId, invoiceNumber, safeKey) {
            const detailRow = document.getElementById(`parts-vendor-invoice-detail-row-${vendorId}-${safeKey}`);
            const detailWrap = document.getElementById(`parts-vendor-invoice-detail-wrap-${vendorId}-${safeKey}`);
            const invoicesBody = document.getElementById(`parts-vendor-invoices-${vendorId}`);
            if (!detailRow || !detailWrap || !invoicesBody) return;

            const isOpening = detailRow.style.display === 'none' || detailRow.style.display === '';

            Array.from(invoicesBody.querySelectorAll(`tr[id^="parts-vendor-invoice-detail-row-${vendorId}-"]`)).forEach(row => {
                if (row.id !== `parts-vendor-invoice-detail-row-${vendorId}-${safeKey}`) {
                    row.style.display = 'none';
                }
            });

            detailRow.style.display = isOpening ? 'table-row' : 'none';
            if (!isOpening) return;

            detailWrap.innerHTML = '<div style="color:#777;">Loading invoiced parts...</div>';
            partsLoadVendorInvoiceParts(vendorId, invoiceNumber, detailWrap);
        }

        function partsLoadVendorInvoiceParts(vendorId, invoiceNumber, container) {
            if (!container) return;
            fetch(`/api/vendors/invoice-parts?vendor_id=${encodeURIComponent(vendorId)}&invoice_number=${encodeURIComponent(invoiceNumber || '')}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }

                    const parts = res.parts || [];
                    if (!parts.length) {
                        container.innerHTML = '<div style="color:#777;">No invoiced parts lines found.</div>';
                        return;
                    }

                    const rows = parts.map(item => `
                        <tr>
                            <td style="padding:8px; border-bottom:1px solid #eee; width:80px;">${partsEscapeHtml(item.line || '—')}</td>
                            <td style="padding:8px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.description || '')}</td>
                            <td style="padding:8px; border-bottom:1px solid #eee; text-align:right; width:120px;">${partsFormatCurrency(item.cost || 0)}</td>
                        </tr>
                    `).join('');

                    container.innerHTML = `
                        <div style="font-weight:bold; margin-bottom:8px;">Invoiced Parts Lines</div>
                        <div style="overflow-x:auto;">
                            <table style="width:100%; border-collapse:collapse;">
                                <thead>
                                    <tr style="background:#f5f5f5; text-align:left;">
                                        <th style="padding:8px; border-bottom:1px solid #ddd; width:80px;">LINE</th>
                                        <th style="padding:8px; border-bottom:1px solid #ddd;">DESCRIPTION</th>
                                        <th style="padding:8px; border-bottom:1px solid #ddd; width:120px; text-align:right;">COST</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        </div>
                    `;
                })
                .catch(err => {
                    console.error('Error loading invoice parts:', err);
                    container.innerHTML = '<div style="color:red;">Error loading invoiced parts lines.</div>';
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

            tbody.innerHTML = '<tr><td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>';

            fetch('/api/parts/ros', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (!res.ros || res.ros.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="8" style="padding:20px; text-align:center; color:#999;">No repair orders found</td></tr>';
                        return;
                    }

                    tbody.innerHTML = res.ros.map((ro, idx) => {
                        return `
                            <tr class="parts-ro-main-row">
                                <td style="padding:12px; border-bottom:1px solid #eee;">${ro.ro}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">${ro.vehicle || '—'}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">${ro.estimator || '—'}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">${ro.tech || '—'}</td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">
                                    <button class="link-button" onclick="openPartsOrderModal('${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                        ${ro.parts_qty || 0}
                                    </button>
                                </td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">
                                    <div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
                                        <button class="link-button" onclick="openPartsOnOrderModal('${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                            ${ro.on_order || 0}
                                        </button>
                                        ${(ro.on_order_warning_count || 0) > 0
                                            ? `<span title="${ro.on_order_warning_count} overdue on-order part(s)" aria-label="${ro.on_order_warning_count} overdue on-order part(s)" style="font-size:16px; line-height:1;">⚠️</span>`
                                            : ''}
                                    </div>
                                </td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">
                                    <button class="link-button" onclick="openPartsArrivedModal('${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                        ${ro.arrived || 0}
                                    </button>
                                </td>
                                <td style="padding:12px; border-bottom:1px solid #eee;">
                                    <button class="link-button" onclick="openPartsReturnedModal('${ro.ro}')" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0;">
                                        ${ro.returned || 0}
                                    </button>
                                </td>
                            </tr>
                        `;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading parts ROs:', err);
                    tbody.innerHTML = '<tr><td colspan="8" style="padding:20px; text-align:center; color:red;">Error loading repair orders.</td></tr>';
                });
        }

        function openPartsOnOrderModal(ro) {
            partsOnOrderRo = ro;
            partsOnOrderReceiveMode = false;
            partsOnOrderManualLines = [];
            const modal = document.getElementById('partsOnOrderModal');
            if (!modal) return;
            modal.style.display = 'block';

            const receiveBtn = document.getElementById('partsOnOrderReceiveBtn');
            const addPartBtn = document.getElementById('partsOnOrderAddPartBtn');
            const saveBtn = document.getElementById('partsOnOrderSaveBtn');
            const vendorInput = document.getElementById('partsOnOrderVendorInput');
            const invoiceNumberInput = document.getElementById('partsOnOrderInvoiceNumber');
            const invoiceTotalInput = document.getElementById('partsOnOrderInvoiceTotal');
            if (receiveBtn) receiveBtn.textContent = 'Receive';
            if (addPartBtn) addPartBtn.style.display = 'none';
            if (saveBtn) saveBtn.style.display = 'none';
            if (vendorInput) vendorInput.value = '';
            if (invoiceNumberInput) invoiceNumberInput.value = '';
            if (invoiceTotalInput) invoiceTotalInput.value = '';
            partsRenderOnOrderValidation([]);

            if (modal && !modal.dataset.onOrderValidationBound) {
                modal.addEventListener('input', () => {
                    partsRenderOnOrderValidation([]);
                });
                modal.addEventListener('change', () => {
                    partsRenderOnOrderValidation([]);
                });
                modal.dataset.onOrderValidationBound = '1';
            }

            partsLoadVendors(false)
                .then(() => {
                    partsPopulateOnOrderVendorDropdown('');
                })
                .catch(() => {
                    partsPopulateOnOrderVendorDropdown('');
                });

            partsLoadOnOrderLines();
        }

        function closePartsOnOrderModal() {
            const modal = document.getElementById('partsOnOrderModal');
            if (modal) modal.style.display = 'none';
            partsOnOrderReceiveMode = false;
            partsOnOrderManualLines = [];
            partsRenderOnOrderValidation([]);
        }

        function openPartsArrivedModal(ro) {
            partsArrivedRo = ro;
            const modal = document.getElementById('partsArrivedModal');
            if (!modal) return;
            modal.style.display = 'block';
            partsLoadArrivedLines();
        }

        function closePartsArrivedModal() {
            const modal = document.getElementById('partsArrivedModal');
            if (modal) modal.style.display = 'none';
            partsArrivedRo = null;
            partsArrivedItems = [];
        }

        function partsLoadArrivedLines() {
            const body = document.getElementById('partsArrivedBody');
            if (!body || !partsArrivedRo) return;

            body.innerHTML = '<tr><td colspan="8" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>';
            fetch(`/api/parts/arrived-lines?ro=${encodeURIComponent(partsArrivedRo)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsArrivedItems = res.items || [];
                    partsRenderArrivedLines();
                })
                .catch(err => {
                    console.error('Error loading arrived parts:', err);
                    body.innerHTML = '<tr><td colspan="8" style="padding:12px; text-align:center; color:red;">Error loading arrived parts.</td></tr>';
                });
        }

        function partsRenderArrivedLines() {
            const body = document.getElementById('partsArrivedBody');
            if (!body) return;

            if (!partsArrivedItems || partsArrivedItems.length === 0) {
                body.innerHTML = '<tr><td colspan="8" style="padding:12px; text-align:center; color:#777;">No arrived parts for this RO.</td></tr>';
                return;
            }

            body.innerHTML = partsArrivedItems.map((item, idx) => {
                const rowBg = idx % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                const descriptionDisplay = String(item.description || '').replace(/\\s+/g, ' ').trim();
                const arrivedDisplay = item.arrived_date
                    ? partsFormatBusinessDate(item.arrived_date)
                    : (item.received_at ? partsFormatBusinessDate(item.received_at) : '—');
                return `
                    <tr style="background:${rowBg};">
                        <td style="padding:10px; border-bottom:1px solid #eee;"><input type="checkbox" class="parts-arrived-check" data-line-id="${item.line_id}" /></td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.line || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; white-space:nowrap;">${partsEscapeHtml(descriptionDisplay)}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.part_number || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.vendor || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(item.list || 0)}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(item.cost || 0)}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(arrivedDisplay)}</td>
                    </tr>
                `;
            }).join('');
        }

        function partsReturnArrivedLines() {
            if (!partsArrivedRo) {
                return;
            }

            const checked = Array.from(document.querySelectorAll('#partsArrivedBody .parts-arrived-check:checked'));
            const lineIds = checked
                .map(el => parseInt(el.dataset.lineId, 10))
                .filter(id => !Number.isNaN(id));

            if (lineIds.length === 0) {
                alert('Select at least one arrived part to return.');
                return;
            }

            fetch('/api/parts/arrived-return', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    ro: partsArrivedRo,
                    local_business_date: partsGetLocalBusinessDateIso(),
                    line_ids: lineIds,
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                partsLoadRos();
                partsLoadArrivedLines();
            })
            .catch(err => {
                console.error('Error returning arrived parts:', err);
                alert(err.message || 'Error returning selected parts.');
            });
        }

        function openPartsReturnedModal(ro) {
            partsReturnedRo = ro;
            const modal = document.getElementById('partsReturnedModal');
            if (!modal) return;
            modal.style.display = 'block';
            partsLoadReturnedLines();
        }

        function closePartsReturnedModal() {
            const modal = document.getElementById('partsReturnedModal');
            if (modal) modal.style.display = 'none';
            partsReturnedRo = null;
            partsReturnedItems = [];
        }

        function partsLoadReturnedLines() {
            const body = document.getElementById('partsReturnedBody');
            if (!body || !partsReturnedRo) return;

            body.innerHTML = '<tr><td colspan="6" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>';
            fetch(`/api/parts/returned-lines?ro=${encodeURIComponent(partsReturnedRo)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsReturnedItems = res.items || [];
                    partsRenderReturnedLines();
                })
                .catch(err => {
                    console.error('Error loading returned parts:', err);
                    body.innerHTML = '<tr><td colspan="6" style="padding:12px; text-align:center; color:red;">Error loading returned parts.</td></tr>';
                });
        }

        function partsRenderReturnedLines() {
            const body = document.getElementById('partsReturnedBody');
            if (!body) return;

            if (!partsReturnedItems || partsReturnedItems.length === 0) {
                body.innerHTML = '<tr><td colspan="6" style="padding:24px; text-align:center; color:#777;">No parts returned</td></tr>';
                return;
            }

            body.innerHTML = partsReturnedItems.map((item, idx) => {
                const rowBg = idx % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                const descriptionDisplay = String(item.description || '').replace(/\\s+/g, ' ').trim();
                const returnDateDisplay = item.return_date ? partsFormatBusinessDate(item.return_date) : '—';
                return `
                    <tr style="background:${rowBg};">
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.line || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; white-space:nowrap;">${partsEscapeHtml(descriptionDisplay)}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.part_number || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.vendor || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${partsFormatCurrency(item.cost || 0)}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(returnDateDisplay)}</td>
                    </tr>
                `;
            }).join('');
        }

        function partsEnterReceiveMode() {
            if (!partsOnOrderRo) return;
            if (partsOnOrderReceiveMode) {
                partsRenderOnOrderValidation([]);
                return;
            }
            partsOnOrderReceiveMode = true;

            const receiveBtn = document.getElementById('partsOnOrderReceiveBtn');
            const addPartBtn = document.getElementById('partsOnOrderAddPartBtn');
            const saveBtn = document.getElementById('partsOnOrderSaveBtn');
            if (receiveBtn) receiveBtn.textContent = partsOnOrderReceiveMode ? 'Receive (On)' : 'Receive';
            if (addPartBtn) addPartBtn.style.display = partsOnOrderReceiveMode ? 'inline-block' : 'none';
            if (saveBtn) saveBtn.style.display = partsOnOrderReceiveMode ? 'inline-block' : 'none';

            partsRenderOnOrderValidation([]);
            partsRenderOnOrderLines();
        }

        function partsAddOnOrderManualLine() {
            if (!partsOnOrderReceiveMode) {
                return;
            }
            const draft = {
                checkedKeys: new Set(),
                partNumbers: {},
                listValues: {},
                qtyValues: {},
                costValues: {},
            };

            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-check')).forEach((checkbox) => {
                const lineId = String(checkbox.getAttribute('data-line-id') || '').trim();
                const orderId = String(checkbox.getAttribute('data-order-id') || '').trim();
                if (!lineId || !orderId) return;
                if (checkbox.checked) {
                    draft.checkedKeys.add(`${orderId}:${lineId}`);
                }
            });

            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-partnum')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId) return;
                draft.partNumbers[lineId] = input.value;
            });
            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-list')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId) return;
                draft.listValues[lineId] = input.value;
            });
            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-qty')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId) return;
                draft.qtyValues[lineId] = input.value;
            });
            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-cost')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId) return;
                draft.costValues[lineId] = input.value;
            });

            partsOnOrderManualLines.push({
                description: '',
                qty_received: '1',
                part_number: '',
                cost: '',
            });
            partsRenderOnOrderLines();

            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-check')).forEach((checkbox) => {
                const lineId = String(checkbox.getAttribute('data-line-id') || '').trim();
                const orderId = String(checkbox.getAttribute('data-order-id') || '').trim();
                if (!lineId || !orderId) return;
                checkbox.checked = draft.checkedKeys.has(`${orderId}:${lineId}`);
            });

            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-partnum')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId || !(lineId in draft.partNumbers)) return;
                input.value = draft.partNumbers[lineId];
            });
            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-list')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId || !(lineId in draft.listValues)) return;
                input.value = draft.listValues[lineId];
            });
            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-qty')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId || !(lineId in draft.qtyValues)) return;
                input.value = draft.qtyValues[lineId];
            });
            Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-cost')).forEach((input) => {
                const lineId = String(input.getAttribute('data-line-id') || '').trim();
                if (!lineId || !(lineId in draft.costValues)) return;
                input.value = draft.costValues[lineId];
            });
        }

        function partsLoadOnOrderLines() {
            const body = document.getElementById('partsOnOrderBody');
            if (!body || !partsOnOrderRo) return;

            body.innerHTML = '<tr><td colspan="9" style="padding:12px; text-align:center; color:#777;">Loading...</td></tr>';
            fetch(`/api/parts/on-order-lines?ro=${encodeURIComponent(partsOnOrderRo)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsOnOrderLines = res.items || [];
                    partsRenderOnOrderLines();
                })
                .catch(err => {
                    console.error('Error loading on-order lines:', err);
                    body.innerHTML = '<tr><td colspan="9" style="padding:12px; text-align:center; color:red;">Error loading on-order parts.</td></tr>';
                });
        }

        function partsRenderOnOrderLines() {
            const body = document.getElementById('partsOnOrderBody');
            const checkHeader = document.getElementById('partsOnOrderCheckHeader');
            const costHeader = document.getElementById('partsOnOrderCostHeader');
            const invoiceWrap = document.getElementById('partsOnOrderInvoiceWrap');
            const saveBtn = document.getElementById('partsOnOrderSaveBtn');
            const addPartBtn = document.getElementById('partsOnOrderAddPartBtn');
            if (!body || !checkHeader || !costHeader || !invoiceWrap) return;

            checkHeader.style.display = partsOnOrderReceiveMode ? 'table-cell' : 'none';
            costHeader.style.display = partsOnOrderReceiveMode ? 'table-cell' : 'none';
            invoiceWrap.style.display = partsOnOrderReceiveMode ? 'block' : 'none';
            if (saveBtn) saveBtn.style.display = partsOnOrderReceiveMode ? 'inline-block' : 'none';
            if (addPartBtn) addPartBtn.style.display = partsOnOrderReceiveMode ? 'inline-block' : 'none';

            const hasManualLines = partsOnOrderReceiveMode && Array.isArray(partsOnOrderManualLines) && partsOnOrderManualLines.length > 0;
            if ((!partsOnOrderLines || partsOnOrderLines.length === 0) && !hasManualLines) {
                body.innerHTML = '<tr><td colspan="9" style="padding:12px; text-align:center; color:#777;">No parts currently on order.</td></tr>';
                return;
            }

            const existingLinesHtml = (partsOnOrderLines || []).map((item, idx) => {
                const lineId = Number(item.line_id);
                const checkboxCell = partsOnOrderReceiveMode
                    ? `<td style="padding:10px; border-bottom:1px solid #eee;"><input type="checkbox" class="parts-onorder-check" data-line-id="${lineId}" data-order-id="${item.order_id}" /></td>`
                    : '';

                const partNumberValue = partsEscapeHtml(item.part_number || '');
                const listValue = Number(item.list || 0).toFixed(2);
                const vendorValue = partsEscapeHtml(item.vendor || '');
                const etaValue = item.eta || '';
                const displayEta = etaValue ? partsFormatDisplayDate(etaValue) : '—';
                const qtyRaw = Number(item.qty || 0);
                const qtyDisplay = Number.isFinite(qtyRaw)
                    ? (Number.isInteger(qtyRaw) ? String(qtyRaw) : qtyRaw.toFixed(2).replace(/\\.00$/, ''))
                    : '0';

                const partNumberCell = partsOnOrderReceiveMode
                    ? `<input type="text" class="parts-onorder-partnum" data-line-id="${lineId}" value="${partNumberValue}" style="width:100%; padding:6px;" />`
                    : partNumberValue || '—';

                const listCell = partsOnOrderReceiveMode
                    ? `<input type="number" step="0.01" class="parts-onorder-list" data-line-id="${lineId}" value="${listValue}" style="width:100%; padding:6px; text-align:right;" />`
                    : `$${listValue}`;

                const qtyCell = partsOnOrderReceiveMode
                    ? `<input type="number" min="0" step="0.01" class="parts-onorder-qty" data-line-id="${lineId}" value="${qtyDisplay}" style="width:80px; padding:6px; text-align:right;" />`
                    : qtyDisplay;

                const vendorCell = vendorValue || '—';

                const etaCell = displayEta;

                const costCell = partsOnOrderReceiveMode
                    ? `<td style="padding:10px; border-bottom:1px solid #eee; text-align:right;"><input type="number" step="0.01" min="0" class="parts-onorder-cost" data-line-id="${lineId}" value="" style="width:100px; padding:6px; text-align:right;" /></td>`
                    : '';

                return `
                    <tr style="background:${idx % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)'};">
                        ${checkboxCell}
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.line || '—')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml(item.description || '')}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${qtyCell}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${partNumberCell}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">${listCell}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${vendorCell}</td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">${etaCell}</td>
                        ${costCell}
                    </tr>
                `;
            }).join('');

            const manualLinesHtml = hasManualLines
                ? partsOnOrderManualLines.map((line, idx) => {
                    const rowBg = ((partsOnOrderLines || []).length + idx) % 2 === 0 ? '#f2f0ef' : 'var(--list-row-white, #ffffff)';
                    return `
                        <tr style="background:${rowBg}; font-style:italic;">
                            <td style="padding:10px; border-bottom:1px solid #eee;"></td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">—</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">
                                <input type="text" class="parts-onorder-manual-description" data-manual-index="${idx}" value="${partsEscapeHtml(line.description || '')}" placeholder="Description" style="width:100%; padding:6px; font-style:italic;" />
                            </td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">
                                <input type="number" min="0" step="0.01" class="parts-onorder-manual-qty" data-manual-index="${idx}" value="${partsEscapeHtml(line.qty_received || '1')}" style="width:80px; padding:6px; text-align:right; font-style:italic;" />
                            </td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">
                                <input type="text" class="parts-onorder-manual-partnum" data-manual-index="${idx}" value="${partsEscapeHtml(line.part_number || '')}" placeholder="Part #" style="width:100%; padding:6px; font-style:italic;" />
                            </td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">—</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">${partsEscapeHtml((document.getElementById('partsOnOrderVendorInput')?.value || '').trim() || '—')}</td>
                            <td style="padding:10px; border-bottom:1px solid #eee;">—</td>
                            <td style="padding:10px; border-bottom:1px solid #eee; text-align:right;">
                                <input type="number" min="0" step="0.01" class="parts-onorder-manual-cost" data-manual-index="${idx}" value="${partsEscapeHtml(line.cost || '')}" placeholder="0.00" style="width:100px; padding:6px; text-align:right; font-style:italic;" />
                            </td>
                        </tr>
                    `;
                }).join('')
                : '';

            body.innerHTML = `${existingLinesHtml}${manualLinesHtml}`;
        }

        function partsRenderOnOrderValidation(messages = []) {
            const panel = document.getElementById('partsOnOrderValidation');
            if (!panel) return;

            const uniqueMessages = Array.from(new Set((messages || [])
                .map(msg => String(msg || '').trim())
                .filter(Boolean)));

            if (uniqueMessages.length === 0) {
                panel.style.display = 'none';
                panel.innerHTML = '';
                return;
            }

            panel.style.display = 'block';
            panel.innerHTML = `
                <div style="font-weight:700; margin-bottom:6px;">Please correct the following:</div>
                <ul style="margin:0; padding-left:18px;">
                    ${uniqueMessages.map(msg => `<li>${partsEscapeHtml(msg)}</li>`).join('')}
                </ul>
            `;
        }

        function partsSaveOnOrderReceive() {
            if (!partsOnOrderReceiveMode) {
                partsRenderOnOrderValidation(['Click Receive first.']);
                return;
            }

            const validationMessages = [];
            let firstFocusSelector = '';
            const addValidation = (message, focusSelector = '') => {
                validationMessages.push(message);
                if (!firstFocusSelector && focusSelector) {
                    firstFocusSelector = focusSelector;
                }
            };

            const vendorName = (document.getElementById('partsOnOrderVendorInput')?.value || '').trim();
            const invoiceNumber = (document.getElementById('partsOnOrderInvoiceNumber')?.value || '').trim();
            const invoiceTotalText = (document.getElementById('partsOnOrderInvoiceTotal')?.value || '').trim();
            const invoiceTotal = parseFloat(invoiceTotalText || '0');

            if (!vendorName) {
                addValidation('Vendor is required.', '#partsOnOrderVendorInput');
            }

            if (!invoiceNumber) {
                addValidation('Invoice Number is required.', '#partsOnOrderInvoiceNumber');
            }
            if (!Number.isFinite(invoiceTotal) || invoiceTotal <= 0) {
                addValidation('Total Invoice Amount is required.', '#partsOnOrderInvoiceTotal');
            }

            const selectedChecks = Array.from(document.querySelectorAll('.parts-onorder-check:checked'));

            const items = [];
            const manualItems = [];
            let selectedCostTotal = 0;

            for (const check of selectedChecks) {
                const lineId = Number(check.dataset.lineId);
                const orderId = Number(check.dataset.orderId);
                const partNumberInput = document.querySelector(`.parts-onorder-partnum[data-line-id="${lineId}"]`);
                const listInput = document.querySelector(`.parts-onorder-list[data-line-id="${lineId}"]`);
                const qtyInput = document.querySelector(`.parts-onorder-qty[data-line-id="${lineId}"]`);
                const costInput = document.querySelector(`.parts-onorder-cost[data-line-id="${lineId}"]`);
                const lineMeta = (partsOnOrderLines || []).find(item => Number(item.line_id) === lineId && Number(item.order_id) === orderId) || {};

                const cost = parseFloat((costInput?.value || '').trim());
                if (!Number.isFinite(cost) || cost < 0) {
                    addValidation('Cost is required for selected lines.', `.parts-onorder-cost[data-line-id="${lineId}"]`);
                }

                const qtyReceived = parseFloat((qtyInput?.value || '').trim());
                if (!Number.isFinite(qtyReceived) || qtyReceived <= 0) {
                    addValidation('Valid QTY is required for selected lines.', `.parts-onorder-qty[data-line-id="${lineId}"]`);
                }

                selectedCostTotal += cost;
                items.push({
                    order_id: orderId,
                    line_id: lineId,
                    part_number: (partNumberInput?.value || '').trim(),
                    list: parseFloat((listInput?.value || '').trim() || '0'),
                    qty_received: qtyReceived,
                    vendor: vendorName,
                    eta: (lineMeta.eta || '').trim(),
                    cost,
                });
            }

            const manualRows = Array.from(document.querySelectorAll('#partsOnOrderBody .parts-onorder-manual-description'));
            for (const descriptionInput of manualRows) {
                const manualIndex = descriptionInput.getAttribute('data-manual-index');
                const qtyInput = document.querySelector(`.parts-onorder-manual-qty[data-manual-index="${manualIndex}"]`);
                const partNumberInput = document.querySelector(`.parts-onorder-manual-partnum[data-manual-index="${manualIndex}"]`);
                const costInput = document.querySelector(`.parts-onorder-manual-cost[data-manual-index="${manualIndex}"]`);

                const description = (descriptionInput?.value || '').trim();
                const partNumber = (partNumberInput?.value || '').trim();
                const qtyText = (qtyInput?.value || '').trim();
                const costText = (costInput?.value || '').trim();

                const hasAnyValue = !!(description || partNumber || qtyText || costText);
                if (!hasAnyValue) {
                    continue;
                }

                const qtyReceived = parseFloat(qtyText || '0');
                const cost = parseFloat(costText || '0');
                if (!description) {
                    addValidation('Manual added parts require a description.', `.parts-onorder-manual-description[data-manual-index="${manualIndex}"]`);
                }
                if (!Number.isFinite(qtyReceived) || qtyReceived <= 0) {
                    addValidation('Manual added parts require a valid QTY.', `.parts-onorder-manual-qty[data-manual-index="${manualIndex}"]`);
                }
                if (!Number.isFinite(cost) || cost < 0) {
                    addValidation('Manual added parts require a valid Cost.', `.parts-onorder-manual-cost[data-manual-index="${manualIndex}"]`);
                }

                selectedCostTotal += cost;
                manualItems.push({
                    description,
                    qty_received: qtyReceived,
                    part_number: partNumber,
                    cost,
                    vendor: vendorName,
                });
            }

            if (selectedChecks.length === 0 && manualItems.length === 0) {
                addValidation('Select at least one part to receive.', '#partsOnOrderBody .parts-onorder-check');
            }

            if (Math.abs(Number(selectedCostTotal.toFixed(2)) - Number(invoiceTotal.toFixed(2))) > 0.009) {
                addValidation('Sum of selected/manual part costs must equal Total Invoice Amount.', '#partsOnOrderInvoiceTotal');
            }

            if (validationMessages.length > 0) {
                partsRenderOnOrderValidation(validationMessages);
                if (firstFocusSelector) {
                    const focusEl = document.querySelector(firstFocusSelector);
                    if (focusEl && typeof focusEl.focus === 'function') {
                        try {
                            focusEl.focus();
                        } catch (_) {
                        }
                    }
                }
                return;
            }

            partsRenderOnOrderValidation([]);

            fetch('/api/parts/on-order-receive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    ro: partsOnOrderRo,
                    vendor: vendorName,
                    invoice_number: invoiceNumber,
                    invoice_total_amount: invoiceTotal,
                    local_business_date: partsGetLocalBusinessDateIso(),
                    items,
                    manual_items: manualItems,
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }

                partsOnOrderReceiveMode = false;
                const receiveBtn = document.getElementById('partsOnOrderReceiveBtn');
                const saveBtn = document.getElementById('partsOnOrderSaveBtn');
                const vendorInput = document.getElementById('partsOnOrderVendorInput');
                const invoiceNumberInput = document.getElementById('partsOnOrderInvoiceNumber');
                const invoiceTotalInput = document.getElementById('partsOnOrderInvoiceTotal');
                if (receiveBtn) receiveBtn.textContent = 'Receive';
                const addPartBtn = document.getElementById('partsOnOrderAddPartBtn');
                if (saveBtn) saveBtn.style.display = 'none';
                if (addPartBtn) addPartBtn.style.display = 'none';
                if (vendorInput) vendorInput.value = '';
                if (invoiceNumberInput) invoiceNumberInput.value = '';
                if (invoiceTotalInput) invoiceTotalInput.value = '';
                partsOnOrderManualLines = [];
                partsRenderOnOrderValidation([]);

                partsLoadRos();
                partsLoadOnOrderLines();
            })
            .catch(err => {
                console.error('Error receiving on-order parts:', err);
                partsRenderOnOrderValidation([err.message || 'Error saving received parts.']);
            });
        }

        function partsNormalizeOrderType(value) {
            const text = String(value || '').trim().toUpperCase();
            if (!text) return '';
            if (text === 'OEM' || text.includes('OEM')) return 'OEM';
            if (text === 'A/M' || text === 'AM' || text.includes('AFTERMARKET') || text.includes('A/M')) return 'A/M';
            if (text === 'LKQ' || text.includes('LKQ') || text.includes('RECYCLED') || text.includes('USED')) return 'LKQ';
            return text;
        }

        function partsSetOrderLineChecked(lineId, checked) {
            const idNum = Number(lineId);
            if (!Number.isFinite(idNum)) return;
            if (checked) {
                partsOrderSelectedIds.add(idNum);
            } else {
                partsOrderSelectedIds.delete(idNum);
            }
            partsRefreshOrderSelectAllState();
        }

        function partsToggleOrderSelectAll(checked) {
            (partsCurrentLines || []).forEach(line => {
                const lineId = Number(line.id);
                if (!Number.isFinite(lineId)) return;
                if (line.is_ordered) return;
                if (checked) {
                    partsOrderSelectedIds.add(lineId);
                } else {
                    partsOrderSelectedIds.delete(lineId);
                }
            });
            partsRenderOrderLines();
        }

        function partsSelectByOrderType(typeValue) {
            const normalizedTarget = partsNormalizeOrderType(typeValue);
            if (!normalizedTarget) return;

            (partsCurrentLines || []).forEach(line => {
                const lineId = Number(line.id);
                if (!Number.isFinite(lineId)) return;
                if (line.is_ordered) return;
                if (partsNormalizeOrderType(line.part_type) === normalizedTarget) {
                    partsOrderSelectedIds.add(lineId);
                }
            });
            partsRenderOrderLines();
        }

        function partsSortOrderLines(field) {
            if (partsOrderSortField === field) {
                partsOrderSortDirection = partsOrderSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                partsOrderSortField = field;
                partsOrderSortDirection = 'asc';
            }
            partsRenderOrderLines();
        }

        function partsUpdateOrderSortIndicators() {
            const indicators = {
                line: document.getElementById('partsOrderSortLine'),
                part_type: document.getElementById('partsOrderSortPartType'),
                price: document.getElementById('partsOrderSortPrice')
            };

            Object.entries(indicators).forEach(([field, el]) => {
                if (!el) return;
                if (partsOrderSortField === field) {
                    el.textContent = partsOrderSortDirection === 'asc' ? '↑' : '↓';
                } else {
                    el.textContent = '';
                }
            });
        }

        function partsRefreshOrderSelectAllState() {
            const selectAll = document.getElementById('partsOrderSelectAll');
            if (!selectAll) return;

            const eligibleLines = (partsCurrentLines || []).filter(line => !line.is_ordered);
            const total = eligibleLines.length;
            const selected = eligibleLines.filter(line => partsOrderSelectedIds.has(Number(line.id))).length;

            selectAll.checked = total > 0 && selected === total;
            selectAll.indeterminate = selected > 0 && selected < total;
        }

        function partsRenderOrderLines() {
            const linesContainer = document.getElementById('partsOrderLines');
            if (!linesContainer) return;

            if (!partsCurrentLines || partsCurrentLines.length === 0) {
                linesContainer.innerHTML = '<div style="padding:12px; color:#777;">No parts found.</div>';
                partsRefreshOrderSelectAllState();
                partsUpdateOrderSortIndicators();
                return;
            }

            const sorted = [...partsCurrentLines].sort((a, b) => {
                const direction = partsOrderSortDirection === 'asc' ? 1 : -1;

                if (partsOrderSortField === 'price') {
                    const aVal = Number(a.price || 0);
                    const bVal = Number(b.price || 0);
                    return (aVal - bVal) * direction;
                }

                if (partsOrderSortField === 'part_type') {
                    const aVal = partsNormalizeOrderType(a.part_type);
                    const bVal = partsNormalizeOrderType(b.part_type);
                    return aVal.localeCompare(bVal) * direction;
                }

                const aNum = Number(a.line);
                const bNum = Number(b.line);
                if (Number.isFinite(aNum) && Number.isFinite(bNum)) {
                    return (aNum - bNum) * direction;
                }

                const aText = String(a.line || '');
                const bText = String(b.line || '');
                return aText.localeCompare(bText, undefined, { numeric: true, sensitivity: 'base' }) * direction;
            });

            linesContainer.innerHTML = sorted.map(line => {
                const lineId = Number(line.id);
                const isChecked = partsOrderSelectedIds.has(lineId) ? 'checked' : '';
                const price = line.price ? `$${Number(line.price).toFixed(2)}` : '—';
                const qtyNumber = Number(line.qty || 0);
                const qtyText = Number.isFinite(qtyNumber)
                    ? (Number.isInteger(qtyNumber) ? String(qtyNumber) : qtyNumber.toFixed(2).replace(/\\.00$/, ''))
                    : '0';
                const isBlocked = Boolean(line.is_ordered);
                const disabledAttr = isBlocked ? 'disabled' : '';
                const rowOpacity = isBlocked ? '0.6' : '1';
                const blockedLabel = isBlocked ? '<div style="color:#a33; font-size:11px;">Already on order (return first)</div>' : '';
                return `
                    <div style="display:flex; align-items:center; padding:10px 0; border-bottom:1px solid #eee; opacity:${rowOpacity};">
                        <div style="width:40px;"><input type="checkbox" class="parts-order-check" data-id="${lineId}" ${isChecked} ${disabledAttr} onchange="partsSetOrderLineChecked(${lineId}, this.checked)" /></div>
                        <div style="width:80px;">${line.line || '—'}</div>
                        <div style="flex:2;">${line.description || ''}${blockedLabel}</div>
                        <div style="flex:1;">${line.part_type || '—'}</div>
                        <div style="width:80px; text-align:right;">${qtyText}</div>
                        <div style="width:120px; text-align:right;">${price}</div>
                    </div>
                `;
            }).join('');

            partsRefreshOrderSelectAllState();
            partsUpdateOrderSortIndicators();
        }

        function openPartsOrderModal(ro) {
            partsCurrentRo = ro;
            const modal = document.getElementById('partsOrderModal');
            const linesContainer = document.getElementById('partsOrderLines');
            const selectAll = document.getElementById('partsOrderSelectAll');
            const typeSelect = document.getElementById('partsOrderTypeQuickSelect');

            partsOrderSelectedIds = new Set();
            partsOrderSortField = 'line';
            partsOrderSortDirection = 'asc';
            if (selectAll) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            }
            if (typeSelect) {
                typeSelect.value = '';
            }

            linesContainer.innerHTML = '<div style="padding:12px; color:#777;">Loading...</div>';
            partsLoadVendorOptions();

            fetch(`/api/parts/ro-lines?ro=${encodeURIComponent(ro)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    partsCurrentLines = res.lines || [];
                    partsRenderOrderLines();
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

        function partsGetRoEstimatorFromTable(ro) {
            const roKey = String(ro || '').trim();
            if (!roKey) return '';
            const roRow = Array.from(document.querySelectorAll('#partsRoBody tr.parts-ro-main-row')).find((row) => {
                const firstCell = row.querySelector('td');
                return String(firstCell?.textContent || '').trim() === roKey;
            });
            return String(roRow?.children?.[2]?.textContent || '').trim();
        }

        async function partsOpenPrintOrderView(options) {
            const ro = String(options?.ro || '').trim();
            const vendorName = String(options?.vendorName || '').trim();
            const arrivalDate = String(options?.arrivalDate || '').trim();
            const orderedLines = Array.isArray(options?.orderedLines) ? options.orderedLines : [];
            const vendorRecord = options?.vendorRecord || {};

            const popup = window.open('', '_blank', 'width=1000,height=800');
            if (!popup) {
                alert('Unable to open print preview. Please allow pop-ups for this site.');
                return;
            }

            const safe = (value) => String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');

            const formatMoney = (value) => {
                const amount = Number(value || 0);
                return '$' + amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            };

            const formatQty = (value) => {
                const qty = Number(value || 0);
                if (!Number.isFinite(qty)) return '0';
                return Number.isInteger(qty) ? String(qty) : qty.toFixed(2).replace(/\.00$/, '');
            };

            const formatDate = (isoDate) => {
                if (!isoDate) return '—';
                const dt = new Date(`${isoDate}T00:00:00`);
                if (Number.isNaN(dt.getTime())) return isoDate;
                return dt.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: '2-digit' });
            };

            const vendorContact = String(vendorRecord.contact_person || '').trim();
            const vendorPhone = String(vendorRecord.phone || '').trim();
            const vendorStreet = String(vendorRecord.street || '').trim();
            const vendorCity = String(vendorRecord.city || '').trim();
            const vendorState = String(vendorRecord.state || '').trim();
            const vendorZip = String(vendorRecord.zip || '').trim();
            const vendorAddress = [vendorStreet, [vendorCity, vendorState].filter(Boolean).join(', '), vendorZip]
                .filter(Boolean)
                .join(' ')
                .trim();

            let estimatorName = String(options?.estimatorName || '').trim();
            try {
                const snapshotResp = await fetch(`/api/ro-estimate?ro=${encodeURIComponent(ro)}`, { credentials: 'include' });
                const snapshotData = await snapshotResp.json();
                const snapshotEstimator = String(snapshotData?.estimate?.header?.estimator || '').trim();
                if (snapshotEstimator && snapshotEstimator !== '—') {
                    estimatorName = snapshotEstimator;
                }
            } catch (error) {
                // keep estimatorName fallback from options/table when API read fails
            }
            if (!estimatorName || estimatorName === '—') {
                try {
                    const roResp = await fetch('/api/parts/ros', { credentials: 'include' });
                    const roData = await roResp.json();
                    const matchedRo = (Array.isArray(roData?.ros) ? roData.ros : []).find((item) => String(item?.ro || '').trim() === ro);
                    const apiEstimator = String(matchedRo?.estimator || '').trim();
                    if (apiEstimator && apiEstimator !== '—') {
                        estimatorName = apiEstimator;
                    }
                } catch (error) {
                    // keep fallback chain
                }
            }
            if (!estimatorName) {
                estimatorName = partsGetRoEstimatorFromTable(ro);
            }
            const userEmail = String(appUiState?.currentUser?.email || appUiState?.sessionUser?.email || '').trim();

            let shopInfo = (typeof setupShopData !== 'undefined' && setupShopData) ? setupShopData : null;
            if (!shopInfo || !Object.keys(shopInfo).length) {
                try {
                    const shopScopeQuery = appUiState?.shopDomain
                        ? `?shop_domain=${encodeURIComponent(String(appUiState.shopDomain))}`
                        : '';
                    const shopResp = await fetch('/api/setup/shop' + shopScopeQuery, { credentials: 'include' });
                    const shopData = await shopResp.json();
                    shopInfo = shopData?.shop || null;
                } catch (error) {
                    shopInfo = null;
                }
            }
            const shopName = String(shopInfo?.shop_name || appUiState?.shopName || '').trim();
            const shopAddress = String(shopInfo?.address || '').trim();
            const shopCity = String(shopInfo?.city || '').trim();
            const shopState = String(shopInfo?.state || '').trim();
            const shopZip = String(shopInfo?.zip_code || '').trim();
            const shopPhone = String(shopInfo?.phone || '').trim();
            const shopCityStateZip = [shopCity, shopState].filter(Boolean).join(', ') + ([shopZip].filter(Boolean).length ? ((shopCity || shopState) ? ` ${shopZip}` : shopZip) : '');

            let totalAmount = 0;
            const rowsHtml = orderedLines.map((line, index) => {
                const qtyValue = Number(line.qty || 0);
                const unitPrice = Number(line.price || 0);
                const lineTotal = qtyValue * unitPrice;
                totalAmount += Number.isFinite(lineTotal) ? lineTotal : 0;
                return `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${safe(line.line || '—')}</td>
                        <td>${safe(line.description || '')}</td>
                        <td>${safe(line.part_type || '—')}</td>
                        <td class="num">${formatQty(qtyValue)}</td>
                        <td class="num">${formatMoney(unitPrice)}</td>
                        <td class="num">${formatMoney(lineTotal)}</td>
                    </tr>
                `;
            }).join('');

            const now = new Date();
            const generatedAt = now.toLocaleString('en-US', { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' });

            popup.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8" />
                    <title>Parts Order - RO ${safe(ro)}</title>
                    <style>
                        @page { margin: 24px; }
                        body { font-family: Arial, sans-serif; color: #1f2937; margin: 0; }
                        .sheet { max-width: 980px; margin: 0 auto; }
                        .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #e5e7eb; padding-bottom: 12px; margin-bottom: 14px; }
                        .title { font-size: 26px; font-weight: 700; letter-spacing: 0.2px; color: #111827; }
                        .sub { font-size: 13px; color: #4b5563; margin-top: 4px; }
                        .ro-emphasis { font-size: 26px; font-weight: 800; color: #111827; line-height: 1.1; }
                        .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }
                        .card { border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; background: #fafafa; }
                        .card h4 { margin: 0 0 8px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #374151; }
                        .line { margin: 4px 0; font-size: 14px; }
                        table { width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
                        thead th { background: #111827; color: #fff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.4px; padding: 10px 8px; text-align: left; }
                        tbody td { padding: 10px 8px; border-top: 1px solid #e5e7eb; font-size: 13px; }
                        tbody tr:nth-child(even) { background: #f9fafb; }
                        .num { text-align: right; white-space: nowrap; }
                        .footer { display: flex; justify-content: flex-end; margin-top: 10px; }
                        .total { min-width: 280px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px 12px; background: #f9fafb; }
                        .total-row { display: flex; justify-content: space-between; font-size: 14px; }
                        .total-row strong { color: #111827; }
                        .muted { color: #6b7280; font-size: 12px; margin-top: 12px; }
                        @media print {
                            .sheet { max-width: 100%; }
                        }
                    </style>
                </head>
                <body>
                    <div class="sheet">
                        <div class="header">
                            <div>
                                <div class="title">Parts Order</div>
                                <div class="ro-emphasis">RO #${safe(ro)}</div>
                                <div class="sub">Generated ${safe(generatedAt)}</div>
                            </div>
                        </div>

                        <div class="cards">
                            <div class="card">
                                <h4>Vendor</h4>
                                <div class="line"><strong>${safe(vendorName || '—')}</strong></div>
                                ${vendorContact ? `<div class="line">Contact: ${safe(vendorContact)}</div>` : ''}
                                ${vendorPhone ? `<div class="line">Phone: ${safe(vendorPhone)}</div>` : ''}
                                ${vendorAddress ? `<div class="line">Address: ${safe(vendorAddress)}</div>` : ''}
                            </div>
                            <div class="card">
                                <h4>SHOP INFO</h4>
                                <div class="line">${safe(shopName || '—')}</div>
                                <div class="line">${safe(shopAddress || '—')}</div>
                                <div class="line">${safe(shopCityStateZip || '—')}</div>
                                <div class="line">${safe(shopPhone || '—')}</div>
                                <div class="line">Estimator: <strong>${safe(estimatorName || '—')}</strong></div>
                                <div class="line">User Email: ${safe(userEmail || '—')}</div>
                            </div>
                        </div>

                        <table>
                            <thead>
                                <tr>
                                    <th style="width:42px;">#</th>
                                    <th style="width:80px;">Line</th>
                                    <th>Description</th>
                                    <th style="width:120px;">Part Type</th>
                                    <th style="width:70px; text-align:right;">Qty</th>
                                    <th style="width:110px; text-align:right;">Unit Price</th>
                                    <th style="width:120px; text-align:right;">Line Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml || '<tr><td colspan="7" style="text-align:center; color:#6b7280;">No lines selected</td></tr>'}
                            </tbody>
                        </table>

                        <div class="footer">
                            <div class="total">
                                <div class="total-row"><span>Order Total</span><strong>${formatMoney(totalAmount)}</strong></div>
                                <div class="total-row"><span>Line Count</span><strong>${orderedLines.length}</strong></div>
                            </div>
                        </div>

                        <div class="muted" style="text-align:right;">AutobodyOS</div>
                    </div>
                </body>
                </html>
            `);
            popup.document.close();
            popup.focus();
            setTimeout(() => popup.print(), 300);
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

            const checked = Array.from(partsOrderSelectedIds)
                .map(id => parseInt(id, 10))
                .filter(id => !Number.isNaN(id));

            const printEstimatorName = partsGetRoEstimatorFromTable(partsCurrentRo);

            const checkedIdSet = new Set(checked.map(id => String(id)));
            const selectedLines = (partsCurrentLines || []).filter(line => checkedIdSet.has(String(line.id)));
            const selectedVendor = (partsVendorsCache || []).find(v => String(v.id) === String(vendorId));

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
                    if (Array.isArray(res.duplicate_lines) && res.duplicate_lines.length > 0) {
                        fetch(`/api/parts/ro-lines?ro=${encodeURIComponent(partsCurrentRo)}`, { credentials: 'include' })
                            .then(resp => resp.json())
                            .then(fresh => {
                                partsCurrentLines = fresh.lines || [];
                                partsOrderSelectedIds = new Set(
                                    Array.from(partsOrderSelectedIds).filter(id => {
                                        const line = (partsCurrentLines || []).find(l => Number(l.id) === Number(id));
                                        return line && !line.is_ordered;
                                    })
                                );
                                partsRenderOrderLines();
                            })
                            .catch(() => {});
                    }
                    throw new Error(res.error);
                }
                closePartsOrderModal();
                partsLoadRos();
                try {
                    partsOpenPrintOrderView({
                        ro: partsCurrentRo,
                        vendorName,
                        arrivalDate,
                        estimatorName: printEstimatorName,
                        vendorRecord: selectedVendor || {},
                        orderedLines: selectedLines,
                    });
                } catch (printError) {
                    console.error('Error opening parts order print view:', printError);
                }
            })
            .catch(err => {
                console.error('Error saving parts order:', err);
                alert('Error saving parts order. Please try again.');
            });
        }
    """

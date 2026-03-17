"""Setup screen for shop profile and user management."""


def get_setup_screen_html():
    return """
    <div id="setup" class="screen" style="padding:20px;">
        <style>
            #setup #setupLayout {
                width: min(96vw, 1520px);
                margin: 0 auto;
                display: flex;
                align-items: flex-start;
                gap: 20px;
            }
            #setup #setupShopsPane,
            #setup #setupMainPane {
                background: #fbfaf9;
                border: 1px solid #ddd6d2;
                border-radius: 14px;
                box-shadow: 0 10px 26px rgba(20, 20, 20, 0.08);
            }
            #setup #setupShopsPane {
                display: none;
                width: 330px;
                padding: 16px;
            }
            #setup #setupMainPane {
                flex: 1;
                min-width: 0;
                padding: 26px;
            }
            #setup #setupShopsCards {
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-height: 74vh;
                overflow-y: auto;
                padding-right: 4px;
            }
            #setup .setup-users-title-tab {
                display: inline-flex;
                align-items: center;
                background: rgba(0,0,0,0.03);
                color: #000000;
                font-weight: 700;
                padding: 10px 14px;
                border-radius: 8px 8px 0 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: -1px;
                font-size: 20px;
                line-height: 1.2;
            }
            #setup .setup-users-table-wrap {
                background: #ffffff;
                border-radius: 4px;
                overflow: hidden;
            }
            #setup #setupUsersBody td,
            #setup #setupUsersBody span,
            #setup #setupUsersBody input,
            #setup #setupUsersBody select {
                font-size: 14px;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            }
            #setup #setupUsersBody tr:hover td {
                background: rgba(0,0,0,0.04) !important;
            }
            #setup .setup-action-btn {
                padding: 10px 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 700;
                letter-spacing: 0.2px;
            }
            #setup #setupUsersTable {
                width: 100%;
                border-collapse: collapse;
                border-spacing: 0;
                overflow: hidden;
                border-radius: 0;
                border: none;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
            }
            #setup #setupUsersTable thead tr {
                background: rgba(0,0,0,0.03) !important;
                color: #000;
                text-align: left;
            }
            #setup #setupUsersTable thead th {
                padding: 14px 12px;
                border: none !important;
                border-bottom: 1px solid #b22222 !important;
                font-size: 15px;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            @media (max-width: 980px) {
                #setup #setupLayout {
                    flex-direction: column;
                }
                #setup #setupShopsPane {
                    width: 100%;
                }
            }
        </style>

        <div id="setupLayout">
            <div id="setupShopsPane">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin:0 0 10px 0;">
                    <h4 style="margin:0; color:#333;">Shops</h4>
                    <button id="setupAddShopBtn" type="button" onclick="openSetupAddShopModal()" class="setup-action-btn" style="display:none; background:#b22222; color:#fff; padding:8px 12px;">+ SHOP</button>
                </div>
                <div id="setupShopsCards">
                    <div style="color:#999; padding:8px;">Loading shops...</div>
                </div>
            </div>

            <div id="setupMainPane">
                <h3 style="margin:0 0 18px 0; color:#333;">Setup</h3>

                <div id="setupShopDisplay" style="text-align:center; margin-bottom:18px; color:#333;">
                    <div style="color:#999;">Loading shop information...</div>
                </div>

                <hr style="margin:24px 0; border:none; border-top:2px solid #d2d2d2;" />

                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; gap:10px;">
                    <button type="button" onclick="openSetupShopModal()" class="setup-action-btn" style="background:#b22222; color:#fff;">SHOP INFO</button>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <button type="button" onclick="openSetupUserModal()" class="setup-action-btn" style="background:#b22222; color:#fff;">+ USER</button>
                        <button type="button" onclick="setupResetSelectedUsers()" class="setup-action-btn" style="background:#b22222; color:#fff;">RESET</button>
                        <button id="setupEditBtn" type="button" onclick="setupToggleEditUsers()" class="setup-action-btn" style="background:#b22222; color:#fff;">EDIT</button>
                    </div>
                </div>

                <h4 class="setup-users-title-tab" style="margin:0; color:#333;">Users</h4>

                <div class="setup-users-table-wrap" style="overflow-x:auto;">
                    <table id="setupUsersTable">
                        <thead>
                            <tr>
                                <th style="width:50px; text-align:center;">SEL</th>
                                <th>FIRST</th>
                                <th>LAST</th>
                                <th>EMAIL</th>
                                <th>ROLE</th>
                            </tr>
                        </thead>
                        <tbody id="setupUsersBody">
                            <tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="setupShopModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:760px; max-height:88vh; overflow-y:auto;">
                <h3 style="margin:0 0 14px 0; color:#333;">Shop Information</h3>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                    <div style="grid-column:1 / span 2;">
                        <label for="setupShopName" style="font-weight:bold; color:#333;">Shop Name</label>
                        <input id="setupShopName" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div style="grid-column:1 / span 2;">
                        <label for="setupShopAddress" style="font-weight:bold; color:#333;">Address</label>
                        <input id="setupShopAddress" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupShopCity" style="font-weight:bold; color:#333;">City</label>
                        <input id="setupShopCity" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupShopState" style="font-weight:bold; color:#333;">State</label>
                        <input id="setupShopState" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupShopZip" style="font-weight:bold; color:#333;">Zip Code</label>
                        <input id="setupShopZip" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupShopPhone" style="font-weight:bold; color:#333;">Phone</label>
                        <input id="setupShopPhone" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div style="grid-column:1 / span 2;">
                        <label for="setupShopEmail" style="font-weight:bold; color:#333;">Email</label>
                        <input id="setupShopEmail" type="email" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                </div>

                <div style="margin-top:14px; text-align:right;">
                    <button id="setupShopSaveBtn" type="button" onclick="setupSaveShop()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save</button>
                </div>
            </div>
        </div>

        <div id="setupUserModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:760px; max-height:88vh; overflow-y:auto;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <h3 style="margin:0; color:#333;">Add User</h3>
                    <button id="setupUserSaveBtn" type="button" onclick="setupSaveUser()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save</button>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                    <div>
                        <label for="setupUserFirst" style="font-weight:bold; color:#333;">First</label>
                        <input id="setupUserFirst" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupUserLast" style="font-weight:bold; color:#333;">Last</label>
                        <input id="setupUserLast" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div style="grid-column:1 / span 2;">
                        <label for="setupUserEmail" style="font-weight:bold; color:#333;">Email</label>
                        <input id="setupUserEmail" type="email" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupUserRole" style="font-weight:bold; color:#333;">Role</label>
                        <select id="setupUserRole" style="width:100%; padding:10px; margin-top:6px;">
                            <option value="">Select role...</option>
                            <option value="ARCHITECT">ARCHITECT</option>
                            <option value="Manager">Manager</option>
                            <option value="Estimator">Estimator</option>
                            <option value="Tech">Tech</option>
                            <option value="Receptionist">Receptionist</option>
                            <option value="HR">HR</option>
                            <option value="Support">Support</option>
                        </select>
                    </div>
                    <div>
                        <label for="setupUserPassword" style="font-weight:bold; color:#333;">Password</label>
                        <input id="setupUserPassword" type="password" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                </div>

                <div style="margin-top:14px; text-align:right;">
                    <button type="button" onclick="closeSetupUserModal()" style="padding:10px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Close</button>
                </div>
            </div>
        </div>

        <div id="setupAddShopModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:760px; max-height:88vh; overflow-y:auto;">
                <h3 style="margin:0 0 14px 0; color:#333;">Add Shop</h3>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                    <div style="grid-column:1 / span 2;">
                        <label for="setupAddShopDomain" style="font-weight:bold; color:#333;">Shop Domain (Optional)</label>
                        <input id="setupAddShopDomain" type="text" placeholder="optional" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div style="grid-column:1 / span 2;">
                        <label for="setupAddShopName" style="font-weight:bold; color:#333;">Shop Name</label>
                        <input id="setupAddShopName" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div style="grid-column:1 / span 2;">
                        <label for="setupAddShopAddress" style="font-weight:bold; color:#333;">Address</label>
                        <input id="setupAddShopAddress" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupAddShopCity" style="font-weight:bold; color:#333;">City</label>
                        <input id="setupAddShopCity" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupAddShopState" style="font-weight:bold; color:#333;">State</label>
                        <input id="setupAddShopState" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupAddShopZip" style="font-weight:bold; color:#333;">Zip Code</label>
                        <input id="setupAddShopZip" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div>
                        <label for="setupAddShopPhone" style="font-weight:bold; color:#333;">Phone</label>
                        <input id="setupAddShopPhone" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                    <div style="grid-column:1 / span 2;">
                        <label for="setupAddShopEmail" style="font-weight:bold; color:#333;">Email</label>
                        <input id="setupAddShopEmail" type="email" style="width:100%; padding:10px; margin-top:6px;" />
                    </div>
                </div>

                <div style="margin-top:14px; text-align:right; display:flex; justify-content:flex-end; gap:8px;">
                    <button type="button" onclick="closeSetupAddShopModal()" style="padding:10px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Close</button>
                    <button id="setupAddShopSaveBtn" type="button" onclick="setupSaveNewShop()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save</button>
                </div>
            </div>
        </div>
    </div>
    """


def get_setup_script():
    return """
        let setupShopData = null;
        let setupUsersData = [];
        let setupShopsData = [];
        let setupIsArchitect = false;
        let setupSelectedShopId = 0;
        let setupSelectedShopDomain = '';
        let setupDefaultDomain = '';
        let setupEditMode = false;

        function setupEscape(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        async function setupLoadContext() {
            const pane = document.getElementById('setupShopsPane');
            const addShopBtn = document.getElementById('setupAddShopBtn');
            try {
                const resp = await fetch('/api/setup/context', { credentials: 'include' });
                const data = await resp.json();
                setupIsArchitect = !!data.is_architect;
                setupDefaultDomain = String(data.default_domain || '').trim().toLowerCase();
                if (!setupSelectedShopId) {
                    setupSelectedShopId = Number(data.default_shop_id || 0) || 0;
                }
                if (pane) pane.style.display = setupIsArchitect ? 'block' : 'none';
                if (addShopBtn) addShopBtn.style.display = setupIsArchitect ? 'inline-block' : 'none';
            } catch (error) {
                console.error('Error loading setup context:', error);
                setupIsArchitect = false;
                if (pane) pane.style.display = 'none';
                if (addShopBtn) addShopBtn.style.display = 'none';
            }
        }

        function setupBuildScopeQuery() {
            if (!setupIsArchitect || !setupSelectedShopId) return '';
            return `?shop_id=${encodeURIComponent(String(setupSelectedShopId))}`;
        }

        function setupBuildScopePayload() {
            if (!setupIsArchitect || !setupSelectedShopId) return {};
            return { shop_id: setupSelectedShopId };
        }

        async function setupLoadData() {
            await setupLoadContext();
            if (setupIsArchitect) {
                await setupLoadShops();
            }
            await Promise.all([setupLoadShop(), setupLoadUsers()]);
        }

        function setupRenderShops() {
            const cardsWrap = document.getElementById('setupShopsCards');
            if (!cardsWrap || !setupIsArchitect) return;

            if (!setupShopsData.length) {
                cardsWrap.innerHTML = '<div style="color:#999; padding:8px;">No shops found.</div>';
                return;
            }

            cardsWrap.innerHTML = setupShopsData.map((shop) => {
                const shopId = Number(shop.id || shop.shop_id || 0);
                const domain = String(shop.domain || '').trim().toLowerCase();
                const isActive = shopId > 0 && shopId === setupSelectedShopId;
                const border = isActive ? '2px solid #b22222' : '1px solid #ddd';
                const bg = isActive ? '#ece9e7' : '#f2f0ef';
                const shopName = setupEscape(shop.shop_name || domain || 'Shop');
                const address = setupEscape(shop.address || '');
                const city = setupEscape(shop.city || '');
                const state = setupEscape(shop.state || '');
                const zip = setupEscape(shop.zip_code || '');
                const phone = setupEscape(shop.phone || '');
                const email = setupEscape(shop.email || '');
                const cityStateZip = [city, state, zip].filter(Boolean).join(', ').replace(/,\s([^,]+)$/, ' $1');
                return `
                    <div onclick="setupSelectShopCard(${shopId})" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();setupSelectShopCard(${shopId});}" tabindex="0" role="button" style="width:100%; text-align:left; background:${bg}; border:${border}; border-radius:6px; padding:10px; cursor:pointer; color:#000;">
                        <div style="font-weight:700; margin-bottom:4px; color:#000;">${shopName}</div>
                        ${address ? `<div style="font-size:12px; color:#000;">${address}</div>` : ''}
                        ${cityStateZip ? `<div style="font-size:12px; color:#000;">${cityStateZip}</div>` : ''}
                        ${phone ? `<div style="font-size:12px; color:#000;">${phone}</div>` : ''}
                        ${email ? `<div style="font-size:12px; color:#000;">${email}</div>` : ''}
                    </div>
                `;
            }).join('');
        }

        async function setupLoadShops() {
            const cardsWrap = document.getElementById('setupShopsCards');
            if (!setupIsArchitect) return;
            if (cardsWrap) cardsWrap.innerHTML = '<div style="color:#999; padding:8px;">Loading shops...</div>';
            try {
                const resp = await fetch('/api/setup/shops', { credentials: 'include' });
                const data = await resp.json();
                const shops = Array.isArray(data.shops) ? data.shops : [];
                setupShopsData = shops;
                if (!setupSelectedShopId || !shops.some((s) => Number(s.id || s.shop_id || 0) === setupSelectedShopId)) {
                    setupSelectedShopId = Number((shops[0] || {}).id || (shops[0] || {}).shop_id || 0) || 0;
                    if (!setupSelectedShopDomain) {
                        setupSelectedShopDomain = String((shops[0] || {}).domain || setupDefaultDomain || '').trim().toLowerCase();
                    }
                }
                setupRenderShops();
            } catch (error) {
                console.error('Error loading shops:', error);
                if (cardsWrap) cardsWrap.innerHTML = '<div style="color:#c00; padding:8px;">Error loading shops.</div>';
            }
        }

        async function setupSelectShopCard(shopId) {
            const nextShopId = Number(shopId || 0);
            if (!nextShopId || nextShopId === setupSelectedShopId) return;
            setupSelectedShopId = nextShopId;
            const selected = (setupShopsData || []).find((shop) => Number(shop.id || shop.shop_id || 0) === nextShopId) || {};
            setupSelectedShopDomain = String(selected.domain || '').trim().toLowerCase();
            setupRenderShops();
            await Promise.all([setupLoadShop(), setupLoadUsers()]);
        }

        function openSetupAddShopModal() {
            if (!setupIsArchitect) return;
            const modal = document.getElementById('setupAddShopModal');
            if (!modal) return;
            const ids = [
                'setupAddShopDomain',
                'setupAddShopName',
                'setupAddShopAddress',
                'setupAddShopCity',
                'setupAddShopState',
                'setupAddShopZip',
                'setupAddShopPhone',
                'setupAddShopEmail',
            ];
            ids.forEach((id) => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
            modal.style.display = 'block';
        }

        function closeSetupAddShopModal() {
            const modal = document.getElementById('setupAddShopModal');
            if (modal) modal.style.display = 'none';
        }

        async function setupSaveNewShop() {
            const saveBtn = document.getElementById('setupAddShopSaveBtn');
            if (saveBtn) saveBtn.disabled = true;
            try {
                const domain = String(document.getElementById('setupAddShopDomain')?.value || '').trim().toLowerCase();

                const payload = {
                    ...(domain ? { shop_domain: domain } : {}),
                    shop_name: (document.getElementById('setupAddShopName')?.value || '').trim(),
                    address: (document.getElementById('setupAddShopAddress')?.value || '').trim(),
                    city: (document.getElementById('setupAddShopCity')?.value || '').trim(),
                    state: (document.getElementById('setupAddShopState')?.value || '').trim(),
                    zip_code: (document.getElementById('setupAddShopZip')?.value || '').trim(),
                    phone: (document.getElementById('setupAddShopPhone')?.value || '').trim(),
                    email: (document.getElementById('setupAddShopEmail')?.value || '').trim(),
                };

                const resp = await fetch('/api/setup/shop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);

                setupSelectedShopId = Number(data.shop_id || 0) || setupSelectedShopId;
                if (domain) setupSelectedShopDomain = domain;
                closeSetupAddShopModal();
                await setupLoadShops();
                await Promise.all([setupLoadShop(), setupLoadUsers()]);
            } catch (error) {
                console.error('Error saving new shop:', error);
                alert('Error saving new shop.');
            } finally {
                if (saveBtn) saveBtn.disabled = false;
            }
        }

        function setupRenderShopDisplay() {
            const wrap = document.getElementById('setupShopDisplay');
            if (!wrap) return;
            const shop = setupShopData || {};
            const name = setupEscape(shop.shop_name || '');
            const address = setupEscape(shop.address || '');
            const city = setupEscape(shop.city || '');
            const state = setupEscape(shop.state || '');
            const zipCode = setupEscape(shop.zip_code || '');
            const phone = setupEscape(shop.phone || '');
            const email = setupEscape(shop.email || '');

            if (!name && !address && !city && !state && !zipCode && !phone && !email) {
                wrap.innerHTML = '<div style="color:#999;">No shop information saved yet.</div>';
                return;
            }

            const cityStateZip = [city, state, zipCode].filter(Boolean).join(', ').replace(/,\s([^,]+)$/, ' $1');
            wrap.innerHTML = `
                <div style="font-weight:700; font-size:20px; color:#222; margin-bottom:4px;">${name || 'Shop'}</div>
                ${address ? `<div style="color:#444; margin-bottom:2px;">${address}</div>` : ''}
                ${cityStateZip ? `<div style="color:#444; margin-bottom:2px;">${cityStateZip}</div>` : ''}
                <div style="color:#444;">${phone ? `<span>${phone}</span>` : ''}${phone && email ? ' | ' : ''}${email ? `<span>${email}</span>` : ''}</div>
            `;
        }

        async function setupLoadShop() {
            try {
                const resp = await fetch(`/api/setup/shop${setupBuildScopeQuery()}`, { credentials: 'include' });
                const data = await resp.json();
                const shop = data.shop || {};
                setupShopData = shop;
                const loadedShopId = Number(shop.shop_id || 0) || 0;
                if (loadedShopId) {
                    setupSelectedShopId = loadedShopId;
                }
                const set = (id, value) => {
                    const el = document.getElementById(id);
                    if (el) el.value = String(value || '');
                };
                set('setupShopName', shop.shop_name);
                set('setupShopAddress', shop.address);
                set('setupShopCity', shop.city);
                set('setupShopState', shop.state);
                set('setupShopZip', shop.zip_code);
                set('setupShopPhone', shop.phone);
                set('setupShopEmail', shop.email);
                setupRenderShopDisplay();
            } catch (error) {
                console.error('Error loading shop setup:', error);
            }
        }

        async function setupSaveShop() {
            const btn = document.getElementById('setupShopSaveBtn');
            if (btn) btn.disabled = true;
            try {
                if (setupIsArchitect && !setupSelectedShopId) {
                    alert('Select a shop first or create one with + SHOP.');
                    return;
                }
                const payload = {
                    shop_name: (document.getElementById('setupShopName')?.value || '').trim(),
                    address: (document.getElementById('setupShopAddress')?.value || '').trim(),
                    city: (document.getElementById('setupShopCity')?.value || '').trim(),
                    state: (document.getElementById('setupShopState')?.value || '').trim(),
                    zip_code: (document.getElementById('setupShopZip')?.value || '').trim(),
                    phone: (document.getElementById('setupShopPhone')?.value || '').trim(),
                    email: (document.getElementById('setupShopEmail')?.value || '').trim(),
                    ...setupBuildScopePayload(),
                };

                const resp = await fetch('/api/setup/shop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
                closeSetupShopModal();
                await setupLoadShop();
                if (setupIsArchitect) {
                    await setupLoadShops();
                }
            } catch (error) {
                console.error('Error saving shop setup:', error);
                alert('Error saving shop information.');
            } finally {
                if (btn) btn.disabled = false;
            }
        }

        function openSetupShopModal() {
            const modal = document.getElementById('setupShopModal');
            if (!modal) return;
            modal.style.display = 'block';
        }

        function closeSetupShopModal() {
            const modal = document.getElementById('setupShopModal');
            if (modal) modal.style.display = 'none';
        }

        async function setupLoadUsers() {
            const body = document.getElementById('setupUsersBody');
            if (!body) return;
            if (setupIsArchitect && !setupSelectedShopId) {
                body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">Select a shop card to load users.</td></tr>';
                return;
            }
            body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>';
            try {
                const resp = await fetch(`/api/setup/users${setupBuildScopeQuery()}`, { credentials: 'include' });
                const data = await resp.json();
                const users = Array.isArray(data.users) ? data.users : [];
                if (setupIsArchitect) {
                    const architectRows = users.filter((user) => !!user.role_locked);
                    const normalRows = users.filter((user) => !user.role_locked);
                    setupUsersData = [...architectRows, ...normalRows];
                } else {
                    setupUsersData = users;
                }
                if (!users.length) {
                    body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">No users found.</td></tr>';
                    return;
                }

                setupRenderUsers();
            } catch (error) {
                console.error('Error loading setup users:', error);
                body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#c00;">Error loading users.</td></tr>';
            }
        }

        function setupRenderUsers() {
            const body = document.getElementById('setupUsersBody');
            if (!body) return;
            const users = setupUsersData || [];
            if (!users.length) {
                body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">No users found.</td></tr>';
                return;
            }

            body.innerHTML = users.map((user, idx) => {
                    const userId = Number(user.id || 0);
                    const roleLocked = !!user.role_locked;
                    const rowWeight = roleLocked && setupIsArchitect ? '800' : '400';
                    const roleText = setupEscape(user.role || '');
                    const roleOptions = ['ARCHITECT', 'Manager', 'Estimator', 'Tech', 'Receptionist', 'HR', 'Support']
                        .map((role) => `<option value="${role}" ${String(user.role || '') === role ? 'selected' : ''}>${role}</option>`)
                        .join('');
                    const firstText = setupEscape(user.first_name || '');
                    const lastText = setupEscape(user.last_name || '');
                    const emailText = setupEscape(user.email || '');
                    const firstCell = (setupEditMode && !roleLocked)
                        ? `<input class="setup-user-first" data-user-id="${userId}" value="${firstText}" style="width:100%; padding:8px; font-size:14px; border:1px solid #ddd; border-radius:4px;" />`
                        : `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${firstText}</span>`;
                    const lastCell = (setupEditMode && !roleLocked)
                        ? `<input class="setup-user-last" data-user-id="${userId}" value="${lastText}" style="width:100%; padding:8px; font-size:14px; border:1px solid #ddd; border-radius:4px;" />`
                        : `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${lastText}</span>`;
                    const emailCell = (setupEditMode && !roleLocked)
                        ? `<input class="setup-user-email" data-user-id="${userId}" value="${emailText}" style="width:100%; padding:8px; font-size:14px; border:1px solid #ddd; border-radius:4px;" />`
                        : `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${emailText}</span>`;
                    const roleCell = (setupEditMode && !roleLocked)
                        ? `<select class="setup-user-role" data-user-id="${userId}" style="width:100%; padding:8px; font-size:14px; border:1px solid #ddd; border-radius:4px;">${roleOptions}</select>`
                        : `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${roleText}</span>`;
                    return `
                        <tr class="setup-users-main-row">
                            <td style="padding:12px; border-bottom:1px solid rgba(0,0,0,0.06); background:#fff; text-align:center; min-height:48px; height:48px; vertical-align:middle;">
                                <input type="checkbox" class="setup-user-select" data-user-id="${userId}" />
                            </td>
                            <td style="padding:12px; border-bottom:1px solid rgba(0,0,0,0.06); background:#fff; min-height:48px; height:48px; vertical-align:middle;">
                                ${firstCell}
                            </td>
                            <td style="padding:12px; border-bottom:1px solid rgba(0,0,0,0.06); background:#fff; min-height:48px; height:48px; vertical-align:middle;">
                                ${lastCell}
                            </td>
                            <td style="padding:12px; border-bottom:1px solid rgba(0,0,0,0.06); background:#fff; min-height:48px; height:48px; vertical-align:middle;">
                                ${emailCell}
                            </td>
                            <td style="padding:12px; border-bottom:1px solid rgba(0,0,0,0.06); background:#fff; min-height:48px; height:48px; vertical-align:middle;">
                                ${roleCell}
                            </td>
                        </tr>
                    `;
                }).join('');

            const editBtn = document.getElementById('setupEditBtn');
            if (editBtn) {
                editBtn.textContent = setupEditMode ? 'EDIT (SAVE)' : 'EDIT';
            }
        }

        async function setupToggleEditUsers() {
            if (!setupEditMode) {
                setupEditMode = true;
                setupRenderUsers();
                return;
            }

            const getValue = (selector, userId) => {
                const el = document.querySelector(`${selector}[data-user-id="${userId}"]`);
                return String(el?.value || '').trim();
            };

            const changes = [];
            (setupUsersData || []).forEach((user) => {
                const userId = Number(user.id || 0);
                if (user.role_locked) {
                    return;
                }
                const next = {
                    first_name: getValue('.setup-user-first', userId),
                    last_name: getValue('.setup-user-last', userId),
                    email: getValue('.setup-user-email', userId),
                    role: getValue('.setup-user-role', userId),
                };
                const changed =
                    next.first_name !== String(user.first_name || '') ||
                    next.last_name !== String(user.last_name || '') ||
                    next.email !== String(user.email || '') ||
                    next.role !== String(user.role || '');
                if (changed) {
                    changes.push({ id: userId, ...next });
                }
            });

            if (!changes.length) {
                setupEditMode = false;
                setupRenderUsers();
                return;
            }

            try {
                for (const payload of changes) {
                    const scopedPayload = {
                        ...payload,
                        ...setupBuildScopePayload(),
                    };
                    const resp = await fetch('/api/setup/users/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(scopedPayload),
                    });
                    const data = await resp.json();
                    if (data.error) throw new Error(data.error);
                }
                setupEditMode = false;
                await setupLoadUsers();
            } catch (error) {
                console.error('Error saving user edits:', error);
                alert('Error saving user edits.');
            }
        }

        async function setupResetSelectedUsers() {
            const selected = Array.from(document.querySelectorAll('.setup-user-select:checked'))
                .map((el) => Number(el.getAttribute('data-user-id') || 0))
                .filter((val) => Number.isFinite(val) && val > 0);

            if (!selected.length) {
                alert('Select at least one user to reset password.');
                return;
            }

            const newPassword = window.prompt('Enter new password for selected user(s):');
            if (!newPassword) return;

            try {
                const resp = await fetch('/api/setup/users/reset-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ user_ids: selected, new_password: newPassword, ...setupBuildScopePayload() }),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
                alert('Password reset complete.');
            } catch (error) {
                console.error('Error resetting passwords:', error);
                alert('Error resetting password.');
            }
        }

        function openSetupUserModal() {
            if (setupIsArchitect && !setupSelectedShopId) {
                alert('Select a shop card first.');
                return;
            }
            const modal = document.getElementById('setupUserModal');
            if (!modal) return;
            modal.style.display = 'block';
        }

        function closeSetupUserModal() {
            const modal = document.getElementById('setupUserModal');
            if (modal) modal.style.display = 'none';
            const ids = ['setupUserFirst', 'setupUserLast', 'setupUserEmail', 'setupUserRole', 'setupUserPassword'];
            ids.forEach((id) => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
        }

        async function setupSaveUser() {
            const saveBtn = document.getElementById('setupUserSaveBtn');
            if (saveBtn) saveBtn.disabled = true;
            try {
                const payload = {
                    first_name: (document.getElementById('setupUserFirst')?.value || '').trim(),
                    last_name: (document.getElementById('setupUserLast')?.value || '').trim(),
                    email: (document.getElementById('setupUserEmail')?.value || '').trim(),
                    role: (document.getElementById('setupUserRole')?.value || '').trim(),
                    password: (document.getElementById('setupUserPassword')?.value || ''),
                    ...setupBuildScopePayload(),
                };

                if (!payload.first_name || !payload.last_name || !payload.email || !payload.role || !payload.password) {
                    alert('Please fill out all user fields.');
                    return;
                }

                const resp = await fetch('/api/setup/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);

                closeSetupUserModal();
                await setupLoadUsers();
            } catch (error) {
                console.error('Error saving setup user:', error);
                alert('Error saving user.');
            } finally {
                if (saveBtn) saveBtn.disabled = false;
            }
        }

        window.addEventListener('click', (event) => {
            const shopModal = document.getElementById('setupShopModal');
            if (shopModal && shopModal.style.display === 'block' && event.target === shopModal) {
                closeSetupShopModal();
                return;
            }

            const addShopModal = document.getElementById('setupAddShopModal');
            if (addShopModal && addShopModal.style.display === 'block' && event.target === addShopModal) {
                closeSetupAddShopModal();
                return;
            }

            const modal = document.getElementById('setupUserModal');
            if (!modal || modal.style.display !== 'block') return;
            if (event.target === modal) {
                closeSetupUserModal();
            }
        });
    """

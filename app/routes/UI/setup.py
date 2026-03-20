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
            #setup #setupUsersTable {
                width: 100%;
                border-collapse: collapse;
            }
            #setup #setupUsersTable th,
            #setup #setupUsersTable td {
                padding: 12px;
                border-bottom: 1px solid rgba(0,0,0,0.08);
                text-align: left;
            }
            #setup .modal {
                display: none;
                position: fixed;
                z-index: 1200;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.45);
            }
            #setup .modal-content {
                background: #f2f2f2;
                margin: 3% auto;
                width: 95%;
                max-width: 900px;
                max-height: 90vh;
                overflow: auto;
                border-radius: 8px;
                border: 1px solid #888;
                padding: 18px;
            }
        </style>

        <div id="setupLayout">
            <div id="setupShopsPane">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin:0 0 10px 0;">
                    <h4 style="margin:0; color:#333;">Shops</h4>
                    <button id="setupAddShopBtn" type="button" onclick="openSetupAddShopModal()" style="display:none; background:#b22222; color:#fff; border:none; border-radius:6px; padding:8px 12px;">+ SHOP</button>
                </div>
                <div id="setupShopsCards"><div style="color:#999; padding:8px;">Loading shops...</div></div>
            </div>

            <div id="setupMainPane">
                <h3 style="margin:0 0 18px 0; color:#333;">Setup</h3>
                <div id="setupShopDisplay" style="margin-bottom:16px; color:#333;"><div style="color:#999;">Loading shop information...</div></div>

                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; gap:10px;">
                    <button type="button" onclick="openSetupShopModal()" style="background:#b22222; color:#fff; border:none; border-radius:6px; padding:10px 16px;">SHOP INFO</button>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <button type="button" onclick="openSetupUserModal()" style="background:#b22222; color:#fff; border:none; border-radius:6px; padding:10px 16px;">+ USER</button>
                        <button type="button" onclick="setupResetSelectedUsers()" style="background:#b22222; color:#fff; border:none; border-radius:6px; padding:10px 16px;">RESET</button>
                        <button id="setupEditBtn" type="button" onclick="setupToggleEditUsers()" style="background:#b22222; color:#fff; border:none; border-radius:6px; padding:10px 16px;">EDIT</button>
                    </div>
                </div>

                <table id="setupUsersTable">
                    <thead>
                        <tr><th>SEL</th><th>FIRST</th><th>LAST</th><th>EMAIL</th><th>ROLE</th></tr>
                    </thead>
                    <tbody id="setupUsersBody"><tr><td colspan="5" style="color:#999;">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>

        <div id="setupShopModal" class="modal">
            <div class="modal-content">
                <h3 style="margin:0 0 14px 0; color:#333;">Shop Information</h3>
                <input id="setupShopName" placeholder="Shop Name" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupShopAddress" placeholder="Address" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupShopCity" placeholder="City" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupShopState" placeholder="State" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupShopZip" placeholder="Zip" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupShopPhone" placeholder="Phone" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupShopEmail" placeholder="Email" style="width:100%;padding:10px;margin-bottom:8px;" />
                <button id="setupShopSaveBtn" type="button" onclick="setupSaveShop()" style="background:#b22222;color:#fff;border:none;border-radius:6px;padding:10px 16px;">Save</button>
            </div>
        </div>

        <div id="setupUserModal" class="modal">
            <div class="modal-content">
                <h3 style="margin:0 0 14px 0; color:#333;">Add User</h3>
                <input id="setupUserFirst" placeholder="First" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupUserLast" placeholder="Last" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupUserEmail" placeholder="Email" style="width:100%;padding:10px;margin-bottom:8px;" />
                <select id="setupUserRole" style="width:100%;padding:10px;margin-bottom:8px;">
                    <option value="">Select role...</option>
                    <option value="Manager">Manager</option>
                    <option value="Estimator">Estimator</option>
                    <option value="Tech">Tech</option>
                    <option value="Receptionist">Receptionist</option>
                    <option value="HR">HR</option>
                    <option value="Support">Support</option>
                </select>
                <input id="setupUserPassword" type="password" placeholder="Password" style="width:100%;padding:10px;margin-bottom:8px;" />
                <button id="setupUserSaveBtn" type="button" onclick="setupSaveUser()" style="background:#b22222;color:#fff;border:none;border-radius:6px;padding:10px 16px;">Save</button>
            </div>
        </div>

        <div id="setupAddShopModal" class="modal">
            <div class="modal-content">
                <h3 style="margin:0 0 14px 0; color:#333;">Add Shop</h3>
                <input id="setupAddShopDomain" placeholder="Shop Domain" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopName" placeholder="Shop Name" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopAddress" placeholder="Address" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopCity" placeholder="City" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopState" placeholder="State" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopZip" placeholder="Zip" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopPhone" placeholder="Phone" style="width:100%;padding:10px;margin-bottom:8px;" />
                <input id="setupAddShopEmail" placeholder="Email" style="width:100%;padding:10px;margin-bottom:8px;" />
                <button id="setupAddShopSaveBtn" type="button" onclick="setupSaveNewShop()" style="background:#b22222;color:#fff;border:none;border-radius:6px;padding:10px 16px;">Save</button>
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
        let setupSelectedShopDomain = '';
        let setupDefaultDomain = '';
        let setupEditMode = false;

        let setupUsersAbort = null;
        let setupShopsAbort = null;
        let setupShopAbort = null;

        function setupEscape(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function fetchWithTimeout(url, options = {}, timeout = 10000) {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeout);

            return fetch(url, {
                ...options,
                signal: controller.signal
            }).finally(() => clearTimeout(id));
        }

        async function safeFetch(url, options = {}) {
            const resp = await fetchWithTimeout(url, options, 10000);

            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}`);
            }

            try {
                return await resp.json();
            } catch {
                throw new Error('Invalid JSON response');
            }
        }

        async function setupLoadContext() {
            const pane = document.getElementById('setupShopsPane');
            const addShopBtn = document.getElementById('setupAddShopBtn');

            try {
                const data = await safeFetch('/api/setup/context', { credentials: 'include' });

                setupIsArchitect = !!data.is_architect;
                setupDefaultDomain = String(data.default_domain || '').trim().toLowerCase();

                if (!setupSelectedShopDomain) {
                    setupSelectedShopDomain = setupDefaultDomain;
                }

                if (pane) pane.style.display = setupIsArchitect ? 'block' : 'none';
                if (addShopBtn) addShopBtn.style.display = setupIsArchitect ? 'inline-block' : 'none';

            } catch (error) {
                console.error('Context error:', error);
                setupIsArchitect = false;
                if (pane) pane.style.display = 'none';
                if (addShopBtn) addShopBtn.style.display = 'none';
            }
        }

        function setupBuildScopeQuery() {
            if (!setupIsArchitect || !setupSelectedShopDomain) return '';
            return `?shop_domain=${encodeURIComponent(setupSelectedShopDomain)}`;
        }

        function setupBuildScopePayload() {
            if (!setupIsArchitect || !setupSelectedShopDomain) return {};
            return { shop_domain: setupSelectedShopDomain };
        }

        async function setupLoadData() {
            await setupLoadContext();

            if (setupIsArchitect) {
                await setupLoadShops();
            }

            await setupLoadShop();
            await setupLoadUsers();
        }

        async function setupLoadShops() {
            if (setupShopsAbort) setupShopsAbort.abort();
            setupShopsAbort = new AbortController();

            const wrap = document.getElementById('setupShopsCards');
            if (wrap) wrap.innerHTML = 'Loading shops...';

            try {
                const data = await safeFetch('/api/setup/shops', {
                    credentials: 'include',
                    signal: setupShopsAbort.signal
                });

                setupShopsData = Array.isArray(data.shops) ? data.shops : [];

                if (!setupSelectedShopDomain && setupShopsData.length) {
                    setupSelectedShopDomain = setupShopsData[0].domain;
                }

                setupRenderShops();

            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error(error);
                if (wrap) wrap.innerHTML = 'Error loading shops. <button onclick="setupLoadShops()">Retry</button>';
            }
        }

        async function setupLoadShop() {
            if (setupShopAbort) setupShopAbort.abort();
            setupShopAbort = new AbortController();

            try {
                const data = await safeFetch(`/api/setup/shop${setupBuildScopeQuery()}`, {
                    credentials: 'include',
                    signal: setupShopAbort.signal
                });

                setupShopData = data.shop || {};
                setupRenderShopDisplay();

            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error('Shop error:', error);
            }
        }

        async function setupLoadUsers() {
            if (setupUsersAbort) setupUsersAbort.abort();
            setupUsersAbort = new AbortController();

            const body = document.getElementById('setupUsersBody');
            if (body) body.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

            try {
                const data = await safeFetch(`/api/setup/users${setupBuildScopeQuery()}`, {
                    credentials: 'include',
                    signal: setupUsersAbort.signal
                });

                setupUsersData = Array.isArray(data.users) ? data.users : [];

                setupRenderUsers();

            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error(error);

                if (body) {
                    body.innerHTML = `
                        <tr>
                            <td colspan="5">
                                Error loading users.
                                <br/>
                                <button onclick="setupLoadUsers()">Retry</button>
                            </td>
                        </tr>
                    `;
                }
            }
        }

        function setupRenderShops() {
            const wrap = document.getElementById('setupShopsCards');
            if (!wrap) return;

            if (!setupShopsData.length) {
                wrap.innerHTML = 'No shops found.';
                return;
            }

            wrap.innerHTML = setupShopsData.map(shop => {
                const domain = setupEscape(shop.domain || '');
                const name = setupEscape(shop.shop_name || domain);

                return `
                    <div class="shop-card" data-domain="${domain}" style="padding:10px; border:1px solid #ddd; margin-bottom:6px; cursor:pointer;">
                        <strong>${name}</strong>
                    </div>
                `;
            }).join('');
        }

        document.addEventListener('click', (e) => {
            const card = e.target.closest('.shop-card');
            if (card) {
                setupSelectedShopDomain = card.dataset.domain;
                setupLoadShop();
                setupLoadUsers();
            }
        });
    """
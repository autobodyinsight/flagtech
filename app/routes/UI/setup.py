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
                    <div style="display:flex; gap:6px; align-items:center;">
                        <button id="setupManageShopsBtn" type="button" onclick="openSetupManageShopsModal()" class="setup-action-btn" style="display:none; background:#555; color:#fff; padding:8px 12px;">Manage</button>
                        <button id="setupAddShopBtn" type="button" onclick="openSetupAddShopModal()" class="setup-action-btn" style="display:none; background:#b22222; color:#fff; padding:8px 12px;">+ SHOP</button>
                    </div>
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
                        <button id="setupManageUsersBtn" type="button" onclick="openSetupManageUsersModal()" class="setup-action-btn" style="display:none; background:#555; color:#fff;">Manage</button>
                        <button type="button" onclick="setupResetSelectedUsers()" class="setup-action-btn" style="background:#b22222; color:#fff;">RESET</button>
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

        <div id="setupManageShopsModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; max-height:88vh; display:flex; flex-direction:column; padding:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-shrink:0;">
                    <h3 style="margin:0; color:#333;">Manage Shops</h3>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <button type="button" id="setupManageShopsEditBtn" onclick="setupManageShopsEdit()" class="setup-action-btn" style="background:#555; color:#fff;">Edit</button>
                        <button type="button" onclick="setupManageShopsDelete()" class="setup-action-btn" style="background:#b22222; color:#fff;">Delete</button>
                        <button type="button" onclick="closeSetupManageShopsModal()" style="padding:10px 14px; background:#888; color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:700;">Close</button>
                    </div>
                </div>
                <div style="overflow-y:auto; flex:1; border:1px solid #e0dbd8; border-radius:8px;">
                    <table id="setupManageShopsTable" style="width:100%; border-collapse:collapse; font-size:14px; font-family:'Segoe UI',Arial,sans-serif;">
                        <thead>
                            <tr style="background:rgba(0,0,0,0.03);">
                                <th style="padding:12px 10px; text-align:center; width:44px; border-bottom:2px solid #b22222;"><input type="checkbox" id="setupManageShopsSelectAll" onchange="setupManageShopsToggleAll(this)" /></th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">Shop Name</th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">Address</th>
                                <th style="padding:12px 10px; text-align:center; border-bottom:2px solid #b22222;">Users</th>
                            </tr>
                        </thead>
                        <tbody id="setupManageShopsBody">
                            <tr><td colspan="4" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="setupManageUsersModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:1000px; max-height:88vh; display:flex; flex-direction:column; padding:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-shrink:0;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <h3 style="margin:0; color:#333;">Manage Users</h3>
                        <div id="setupManageUsersCreateWrap" style="position:relative;">
                            <button type="button" onclick="setupToggleManageUsersCreateDropdown()" class="setup-action-btn" style="background:#b22222; color:#fff; padding:8px 12px;">+</button>
                            <div id="setupManageUsersCreateDropdown" style="display:none; position:absolute; top:calc(100% + 6px); left:0; z-index:20; width:340px; background:#fff; border:1px solid #e0dbd8; border-radius:8px; box-shadow:0 8px 20px rgba(0,0,0,0.12); padding:12px;">
                                <div style="font-weight:700; color:#333; margin-bottom:10px;">Create User</div>
                                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                                    <input id="setupManageUserFirst" type="text" placeholder="First" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                                    <input id="setupManageUserLast" type="text" placeholder="Last" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                                    <input id="setupManageUserEmail" type="email" placeholder="Email" style="grid-column:1 / span 2; width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                                    <select id="setupManageUserRole" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                                        <option value="">Select role...</option>
                                    </select>
                                    <input id="setupManageUserPassword" type="password" placeholder="Password" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                                </div>
                                <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:10px;">
                                    <button type="button" onclick="setupCloseManageUsersCreateDropdown()" style="padding:8px 12px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Close</button>
                                    <button id="setupManageUsersCreateSaveBtn" type="button" onclick="setupSaveUserFromManageDropdown()" style="padding:8px 12px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:700;">Save</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <button type="button" id="setupManageUsersEditBtn" onclick="setupManageUsersEdit()" class="setup-action-btn" style="background:#555; color:#fff;">Edit</button>
                        <button type="button" id="setupManageUsersDeleteBtn" onclick="setupManageUsersDelete()" class="setup-action-btn" style="background:#b22222; color:#fff;">Delete</button>
                        <button type="button" onclick="closeSetupManageUsersModal()" style="padding:10px 14px; background:#888; color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:700;">Close</button>
                    </div>
                </div>
                <div style="overflow-y:auto; flex:1; border:1px solid #e0dbd8; border-radius:8px;">
                    <table id="setupManageUsersTable" style="width:100%; border-collapse:collapse; font-size:14px; font-family:'Segoe UI',Arial,sans-serif;">
                        <thead>
                            <tr style="background:rgba(0,0,0,0.03);">
                                <th style="padding:12px 10px; text-align:center; width:44px; border-bottom:2px solid #b22222;"><input type="checkbox" id="setupManageUsersSelectAll" onchange="setupManageUsersToggleAll(this)" /></th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">First</th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">Last</th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">Email</th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">Shop</th>
                                <th style="padding:12px 10px; text-align:left; border-bottom:2px solid #b22222;">Role</th>
                            </tr>
                        </thead>
                        <tbody id="setupManageUsersBody">
                            <tr><td colspan="6" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>
                        </tbody>
                    </table>
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
        let setupCanManageUsers = false;
        let setupCanAddUsers = false;
        let setupCanAssignArchitect = false;
        let setupRequesterRole = '';
        let setupSelectedShopId = 0;
        let setupSelectedShopDomain = '';
        let setupDefaultDomain = '';

        // Manage Shops modal state
        let setupManageShopsData = [];
        let setupManageShopsEditingId = 0;
        let setupManageShopsEditSnapshot = null;

        // Manage Users modal state
        let setupManageAllUsersData = [];
        let setupManageAllShopsData = [];
        let setupManageUsersEditingId = 0;
        let setupManageUsersEditSnapshot = null;

        function setupEscape(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function setupGetAssignableRoles() {
            const baseRoles = ['Manager', 'Estimator', 'Tech', 'Receptionist', 'HR', 'Support'];
            if (setupCanAssignArchitect) {
                return ['ARCHITECT', ...baseRoles];
            }
            return baseRoles;
        }

        function setupBuildRoleOptions(selectedRole = '') {
            const options = ['<option value="">Select role...</option>'];
            setupGetAssignableRoles().forEach((role) => {
                const isSelected = String(selectedRole || '') === role ? ' selected' : '';
                options.push(`<option value="${role}"${isSelected}>${role}</option>`);
            });
            return options.join('');
        }

        async function setupLoadContext() {
            const pane = document.getElementById('setupShopsPane');
            const addShopBtn = document.getElementById('setupAddShopBtn');
            try {
                const resp = await fetch('/api/setup/context', { credentials: 'include' });
                const data = await resp.json();
                setupIsArchitect = !!data.is_architect;
                setupRequesterRole = String(data.requester_role || '').trim();
                setupCanManageUsers = !!data.can_manage_users;
                setupCanAddUsers = !!data.can_add_users;
                setupCanAssignArchitect = !!data.can_assign_architect;
                setupDefaultDomain = String(data.default_domain || '').trim().toLowerCase();
                if (!setupSelectedShopId) {
                    setupSelectedShopId = Number(data.default_shop_id || 0) || 0;
                }
                if (pane) pane.style.display = setupIsArchitect ? 'block' : 'none';
                if (addShopBtn) addShopBtn.style.display = setupIsArchitect ? 'inline-block' : 'none';
                const manageShopsBtn = document.getElementById('setupManageShopsBtn');
                if (manageShopsBtn) manageShopsBtn.style.display = setupIsArchitect ? 'inline-block' : 'none';
                const manageUsersBtn = document.getElementById('setupManageUsersBtn');
                if (manageUsersBtn) manageUsersBtn.style.display = setupCanManageUsers ? 'inline-block' : 'none';
            } catch (error) {
                console.error('Error loading setup context:', error);
                setupIsArchitect = false;
                setupCanManageUsers = false;
                setupCanAddUsers = false;
                setupCanAssignArchitect = false;
                setupRequesterRole = '';
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
                    const roleLocked = !!user.role_locked;
                    const rowWeight = roleLocked && setupIsArchitect ? '800' : '400';
                    const roleText = setupEscape(user.role || '');
                    const firstText = setupEscape(user.first_name || '');
                    const lastText = setupEscape(user.last_name || '');
                    const emailText = setupEscape(user.email || '');
                    const firstCell = `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${firstText}</span>`;
                    const lastCell = `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${lastText}</span>`;
                    const emailCell = `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${emailText}</span>`;
                    const roleCell = `<span style="font-size:14px; color:#111; font-weight:${rowWeight};">${roleText}</span>`;
                    const userId = Number(user.id || 0);
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
            setupToggleManageUsersCreateDropdown();
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
                const manageModal = document.getElementById('setupManageUsersModal');
                if (manageModal && manageModal.style.display === 'block') {
                    await openSetupManageUsersModal();
                }
            } catch (error) {
                console.error('Error saving setup user:', error);
                alert('Error saving user.');
            } finally {
                if (saveBtn) saveBtn.disabled = false;
            }
        }

        // ─── Manage Shops Modal ───────────────────────────────────────────────────

        async function openSetupManageShopsModal() {
            if (!setupIsArchitect) return;
            setupManageShopsEditingId = 0;
            setupManageShopsEditSnapshot = null;
            const modal = document.getElementById('setupManageShopsModal');
            if (!modal) return;
            modal.style.display = 'block';
            const body = document.getElementById('setupManageShopsBody');
            if (body) body.innerHTML = '<tr><td colspan="4" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>';
            try {
                const resp = await fetch('/api/setup/shops', { credentials: 'include' });
                const data = await resp.json();
                setupManageShopsData = Array.isArray(data.shops) ? data.shops : [];
            } catch (e) {
                setupManageShopsData = [];
            }
            setupManageShopsRender();
        }

        function closeSetupManageShopsModal() {
            setupManageShopsEditingId = 0;
            setupManageShopsEditSnapshot = null;
            const modal = document.getElementById('setupManageShopsModal');
            if (modal) modal.style.display = 'none';
            const editBtn = document.getElementById('setupManageShopsEditBtn');
            if (editBtn) editBtn.textContent = 'Edit';
        }

        function setupManageShopsRender() {
            const body = document.getElementById('setupManageShopsBody');
            if (!body) return;
            const shops = setupManageShopsData || [];
            if (!shops.length) {
                body.innerHTML = '<tr><td colspan="4" style="padding:18px; text-align:center; color:#999;">No shops found.</td></tr>';
                return;
            }
            body.innerHTML = shops.map((shop) => {
                const shopId = Number(shop.id || shop.shop_id || 0);
                const isEditing = setupManageShopsEditingId > 0 && shopId === setupManageShopsEditingId;
                const nameVal = setupEscape(shop.shop_name || '');
                const addrVal = setupEscape(shop.address || '');
                const cityVal = setupEscape(shop.city || '');
                const stateVal = setupEscape(shop.state || '');
                const zipVal = setupEscape(shop.zip_code || '');
                const phoneVal = setupEscape(shop.phone || '');
                const emailVal = setupEscape(shop.email || '');
                const userCount = Number(shop.user_count || 0);
                const addrDisplay = [shop.address, shop.city, shop.state].filter(Boolean).join(', ');

                if (isEditing) {
                    return `
                        <tr style="background:#fff7f0;">
                            <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); text-align:center;">
                                <input type="checkbox" class="setup-manage-shop-cb" data-shop-id="${shopId}" checked />
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                    <input id="mshopName_${shopId}" value="${nameVal}" placeholder="Shop Name" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                                    <input id="mshopPhone_${shopId}" value="${phoneVal}" placeholder="Phone" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                                    <input id="mshopEmail_${shopId}" value="${emailVal}" placeholder="Email" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px; grid-column:1/span 2;" />
                                </div>
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <div style="display:grid; grid-template-columns:1fr 1fr 80px; gap:6px;">
                                    <input id="mshopAddr_${shopId}" value="${addrVal}" placeholder="Address" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px; grid-column:1/span 3;" />
                                    <input id="mshopCity_${shopId}" value="${cityVal}" placeholder="City" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                                    <input id="mshopState_${shopId}" value="${stateVal}" placeholder="State" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                                    <input id="mshopZip_${shopId}" value="${zipVal}" placeholder="Zip" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                                </div>
                            </td>
                            <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); text-align:center; color:#555;">${userCount}</td>
                        </tr>
                    `;
                }
                return `
                    <tr style="background:#fff;">
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); text-align:center;">
                            <input type="checkbox" class="setup-manage-shop-cb" data-shop-id="${shopId}" />
                        </td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); font-weight:600; color:#222;">${nameVal || '<span style="color:#aaa;">—</span>'}</td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); color:#555;">${setupEscape(addrDisplay) || '<span style="color:#aaa;">—</span>'}</td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); text-align:center; color:#555;">${userCount}</td>
                    </tr>
                `;
            }).join('');

            const editBtn = document.getElementById('setupManageShopsEditBtn');
            if (editBtn) editBtn.textContent = setupManageShopsEditingId ? 'Edit (Save)' : 'Edit';
        }

        function setupManageShopsToggleAll(cb) {
            document.querySelectorAll('.setup-manage-shop-cb').forEach((el) => { el.checked = cb.checked; });
        }

        function setupManageShopsGetSelected() {
            return Array.from(document.querySelectorAll('.setup-manage-shop-cb:checked'))
                .map((el) => Number(el.getAttribute('data-shop-id') || 0))
                .filter((v) => v > 0);
        }

        async function setupManageShopsDelete() {
            const selected = setupManageShopsGetSelected();
            if (!selected.length) { alert('Select at least one shop to delete.'); return; }
            const count = selected.length;
            const names = setupManageShopsData
                .filter((s) => selected.includes(Number(s.id || s.shop_id || 0)))
                .map((s) => s.shop_name || s.domain || String(s.id || s.shop_id))
                .join(', ');
            if (!confirm(`Delete ${count} shop(s) and ALL associated data?\\n\\n${names}\\n\\nThis cannot be undone.`)) return;
            try {
                const resp = await fetch('/api/setup/shops/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ shop_ids: selected }),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
                // If we deleted the currently selected shop, reset selection
                if (selected.includes(setupSelectedShopId)) {
                    setupSelectedShopId = 0;
                    setupSelectedShopDomain = '';
                }
                closeSetupManageShopsModal();
                await setupLoadShops();
                await Promise.all([setupLoadShop(), setupLoadUsers()]);
            } catch (e) {
                console.error('Error deleting shops:', e);
                alert('Error deleting shops: ' + e.message);
            }
        }

        async function setupManageShopsEdit() {
            // If currently in edit mode → save or exit
            if (setupManageShopsEditingId) {
                const shopId = setupManageShopsEditingId;
                const snap = setupManageShopsEditSnapshot || {};
                const g = (id) => String(document.getElementById(id)?.value || '').trim();
                const newName = g(`mshopName_${shopId}`);
                const newAddr = g(`mshopAddr_${shopId}`);
                const newCity = g(`mshopCity_${shopId}`);
                const newState = g(`mshopState_${shopId}`);
                const newZip = g(`mshopZip_${shopId}`);
                const newPhone = g(`mshopPhone_${shopId}`);
                const newEmail = g(`mshopEmail_${shopId}`);
                const changed =
                    newName !== (snap.shop_name || '') ||
                    newAddr !== (snap.address || '') ||
                    newCity !== (snap.city || '') ||
                    newState !== (snap.state || '') ||
                    newZip !== (snap.zip_code || '') ||
                    newPhone !== (snap.phone || '') ||
                    newEmail !== (snap.email || '');
                if (changed) {
                    try {
                        const payload = {
                            shop_id: shopId,
                            shop_name: newName,
                            address: newAddr,
                            city: newCity,
                            state: newState,
                            zip_code: newZip,
                            phone: newPhone,
                            email: newEmail,
                        };
                        const resp = await fetch('/api/setup/shop', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            credentials: 'include',
                            body: JSON.stringify(payload),
                        });
                        const data = await resp.json();
                        if (data.error) throw new Error(data.error);
                        // Update local data
                        const idx = setupManageShopsData.findIndex((s) => Number(s.id || s.shop_id || 0) === shopId);
                        if (idx >= 0) {
                            setupManageShopsData[idx] = {
                                ...setupManageShopsData[idx],
                                shop_name: newName, address: newAddr, city: newCity,
                                state: newState, zip_code: newZip, phone: newPhone, email: newEmail,
                            };
                        }
                        // Refresh side panel shops too
                        await setupLoadShops();
                        if (shopId === setupSelectedShopId) await setupLoadShop();
                    } catch (e) {
                        console.error('Error saving shop edit:', e);
                        alert('Error saving shop: ' + e.message);
                        return;
                    }
                }
                setupManageShopsEditingId = 0;
                setupManageShopsEditSnapshot = null;
                setupManageShopsRender();
                return;
            }

            // Enter edit mode for single selected shop
            const selected = setupManageShopsGetSelected();
            if (!selected.length) { alert('Select one shop to edit.'); return; }
            if (selected.length > 1) { alert('Select only one shop to edit.'); return; }
            const shopId = selected[0];
            const shop = setupManageShopsData.find((s) => Number(s.id || s.shop_id || 0) === shopId);
            if (!shop) return;
            setupManageShopsEditingId = shopId;
            setupManageShopsEditSnapshot = { ...shop };
            setupManageShopsRender();
        }

        // ─── Manage Users Modal ───────────────────────────────────────────────────

        async function openSetupManageUsersModal() {
            if (!setupCanManageUsers) return;
            setupManageUsersEditingId = 0;
            setupManageUsersEditSnapshot = null;
            const modal = document.getElementById('setupManageUsersModal');
            if (!modal) return;
            modal.style.display = 'block';
            const createWrap = document.getElementById('setupManageUsersCreateWrap');
            if (createWrap) createWrap.style.display = setupCanAddUsers ? 'block' : 'none';
            const editBtn = document.getElementById('setupManageUsersEditBtn');
            if (editBtn) editBtn.style.display = setupCanManageUsers ? 'inline-block' : 'none';
            const deleteBtn = document.getElementById('setupManageUsersDeleteBtn');
            if (deleteBtn) deleteBtn.style.display = setupCanManageUsers ? 'inline-block' : 'none';
            const body = document.getElementById('setupManageUsersBody');
            if (body) body.innerHTML = '<tr><td colspan="6" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>';
            try {
                const usersUrl = `/api/setup/users${setupBuildScopeQuery()}`;
                const [uData, sData] = await Promise.all([
                    fetch(usersUrl, { credentials: 'include' })
                        .then((response) => response.json())
                        .catch(() => ({ users: [] })),
                    fetch('/api/setup/shops', { credentials: 'include' })
                        .then((response) => response.json())
                        .catch(() => ({ shops: [] })),
                ]);
                const fetchedShops = Array.isArray(sData.shops) ? sData.shops : [];
                if (setupIsArchitect && !Number(setupSelectedShopId || 0) && fetchedShops.length) {
                    setupSelectedShopId = Number((fetchedShops[0] || {}).id || (fetchedShops[0] || {}).shop_id || 0) || 0;
                }
                const selectedShopId = Number(setupSelectedShopId || 0);
                const fetchedUsers = Array.isArray(uData.users) ? uData.users : [];
                setupManageAllUsersData = selectedShopId > 0
                    ? fetchedUsers.filter((user) => Number(user.shop_id || 0) === selectedShopId)
                    : fetchedUsers;
                setupManageAllShopsData = fetchedShops;
                if (!setupManageAllShopsData.length) {
                    const fallbackShopMap = new Map();
                    (setupManageAllUsersData || []).forEach((user) => {
                        const userShopId = Number(user.shop_id || 0);
                        if (!userShopId || fallbackShopMap.has(userShopId)) return;
                        fallbackShopMap.set(userShopId, {
                            id: userShopId,
                            shop_id: userShopId,
                            shop_name: String(user.shop_name || '').trim() || `Shop ${userShopId}`,
                        });
                    });
                    setupManageAllShopsData = Array.from(fallbackShopMap.values());
                }
            } catch (e) {
                setupManageAllUsersData = [];
                setupManageAllShopsData = [];
            }
            setupManageUsersRender();
        }

        function closeSetupManageUsersModal() {
            setupManageUsersEditingId = 0;
            setupManageUsersEditSnapshot = null;
            setupCloseManageUsersCreateDropdown();
            const modal = document.getElementById('setupManageUsersModal');
            if (modal) modal.style.display = 'none';
            const editBtn = document.getElementById('setupManageUsersEditBtn');
            if (editBtn) editBtn.textContent = 'Edit';
        }

        function setupToggleManageUsersCreateDropdown() {
            if (!setupCanAddUsers) return;
            if (setupIsArchitect && !setupSelectedShopId) {
                alert('Select a shop card first.');
                return;
            }
            const dropdown = document.getElementById('setupManageUsersCreateDropdown');
            if (!dropdown) return;
            const isOpen = dropdown.style.display === 'block';
            if (isOpen) {
                setupCloseManageUsersCreateDropdown();
                return;
            }
            const roleSelect = document.getElementById('setupManageUserRole');
            if (roleSelect) {
                roleSelect.innerHTML = setupBuildRoleOptions('');
            }
            dropdown.style.display = 'block';
            const first = document.getElementById('setupManageUserFirst');
            if (first) first.focus();
        }

        function setupCloseManageUsersCreateDropdown() {
            const dropdown = document.getElementById('setupManageUsersCreateDropdown');
            if (dropdown) dropdown.style.display = 'none';
            const ids = ['setupManageUserFirst', 'setupManageUserLast', 'setupManageUserEmail', 'setupManageUserRole', 'setupManageUserPassword'];
            ids.forEach((id) => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
            const saveBtn = document.getElementById('setupManageUsersCreateSaveBtn');
            if (saveBtn) saveBtn.disabled = false;
        }

        async function setupSaveUserFromManageDropdown() {
            if (!setupCanAddUsers) return;
            const saveBtn = document.getElementById('setupManageUsersCreateSaveBtn');
            if (saveBtn) saveBtn.disabled = true;
            try {
                const payload = {
                    first_name: (document.getElementById('setupManageUserFirst')?.value || '').trim(),
                    last_name: (document.getElementById('setupManageUserLast')?.value || '').trim(),
                    email: (document.getElementById('setupManageUserEmail')?.value || '').trim(),
                    role: (document.getElementById('setupManageUserRole')?.value || '').trim(),
                    password: (document.getElementById('setupManageUserPassword')?.value || ''),
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

                setupCloseManageUsersCreateDropdown();
                await setupLoadUsers();
                await openSetupManageUsersModal();
            } catch (error) {
                console.error('Error saving setup user:', error);
                alert('Error saving user.');
            } finally {
                if (saveBtn) saveBtn.disabled = false;
            }
        }

        function setupManageUsersRender() {
            const body = document.getElementById('setupManageUsersBody');
            if (!body) return;
            const users = setupManageAllUsersData || [];
            if (!users.length) {
                body.innerHTML = '<tr><td colspan="6" style="padding:18px; text-align:center; color:#999;">No users found.</td></tr>';
                return;
            }
            const shopOptions = (setupManageAllShopsData || []).map((s) => {
                const sid = Number(s.id || s.shop_id || 0);
                const sname = setupEscape(s.shop_name || s.domain || String(sid));
                return `<option value="${sid}">${sname}</option>`;
            }).join('');

            body.innerHTML = users.map((user) => {
                const userId = Number(user.id || 0);
                const isEditing = setupManageUsersEditingId > 0 && userId === setupManageUsersEditingId;
                const first = setupEscape(user.first_name || '');
                const last = setupEscape(user.last_name || '');
                const email = setupEscape(user.email || '');
                const userShopId = Number(user.shop_id || 0);
                const _shopEntry = (setupManageAllShopsData || []).find((s) => Number(s.id || s.shop_id || 0) === userShopId) || {};
                const shopName = setupEscape(user.shop_name || _shopEntry.shop_name || _shopEntry.domain || '');
                const roleLocked = !!user.role_locked;
                const rowBg = roleLocked ? 'rgba(178,34,34,0.04)' : '#fff';
                const fontWeight = roleLocked ? '700' : '400';

                if (isEditing && !roleLocked) {
                    const roleOpts = setupGetAssignableRoles()
                        .map((r) => `<option value="${r}" ${user.role === r ? 'selected' : ''}>${r}</option>`)
                        .join('');
                    const shopSelectOpts = (setupManageAllShopsData || []).map((s) => {
                        const sid = Number(s.id || s.shop_id || 0);
                        const sname = setupEscape(s.shop_name || s.domain || String(sid));
                        return `<option value="${sid}" ${sid === userShopId ? 'selected' : ''}>${sname}</option>`;
                    }).join('');
                    return `
                        <tr style="background:#fff7f0;">
                            <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); text-align:center;">
                                <input type="checkbox" class="setup-manage-user-cb" data-user-id="${userId}" checked />
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <input id="mufirst_${userId}" value="${first}" style="width:100%; padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <input id="mulast_${userId}" value="${last}" style="width:100%; padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <input id="muemail_${userId}" value="${email}" style="width:100%; padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;" />
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <select id="mushop_${userId}" style="width:100%; padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;">${shopSelectOpts}</select>
                            </td>
                            <td style="padding:8px 10px; border-bottom:1px solid rgba(0,0,0,0.06);">
                                <select id="murole_${userId}" style="width:100%; padding:6px 8px; border:1px solid #ccc; border-radius:4px; font-size:13px;">${roleOpts}</select>
                            </td>
                        </tr>
                    `;
                }
                const roleText = setupEscape(user.role || '');
                return `
                    <tr style="background:${rowBg};">
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); text-align:center;">
                            <input type="checkbox" class="setup-manage-user-cb" data-user-id="${userId}" />
                        </td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); font-weight:${fontWeight}; color:#222;">${first || '<span style="color:#aaa;">—</span>'}</td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); font-weight:${fontWeight}; color:#222;">${last || '<span style="color:#aaa;">—</span>'}</td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); color:#444;">${email || '<span style="color:#aaa;">—</span>'}</td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); color:#444;">${shopName || '<span style="color:#aaa;">—</span>'}</td>
                        <td style="padding:10px; border-bottom:1px solid rgba(0,0,0,0.06); color:#444;">${roleText || '<span style="color:#aaa;">—</span>'}</td>
                    </tr>
                `;
            }).join('');

            const editBtn = document.getElementById('setupManageUsersEditBtn');
            if (editBtn) editBtn.textContent = setupManageUsersEditingId ? 'Edit (Save)' : 'Edit';
        }

        function setupManageUsersToggleAll(cb) {
            document.querySelectorAll('.setup-manage-user-cb').forEach((el) => { el.checked = cb.checked; });
        }

        function setupManageUsersGetSelected() {
            return Array.from(document.querySelectorAll('.setup-manage-user-cb:checked'))
                .map((el) => Number(el.getAttribute('data-user-id') || 0))
                .filter((v) => v > 0);
        }

        async function setupManageUsersDelete() {
            if (!setupCanManageUsers) return;
            const selected = setupManageUsersGetSelected();
            if (!selected.length) { alert('Select at least one user to delete.'); return; }
            const count = selected.length;
            const names = setupManageAllUsersData
                .filter((u) => selected.includes(Number(u.id || 0)))
                .map((u) => `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.email || String(u.id))
                .join(', ');
            if (!confirm(`Delete ${count} user(s)?\\n\\n${names}\\n\\nThis cannot be undone.`)) return;
            try {
                const resp = await fetch('/api/setup/users/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ user_ids: selected, shop_id: setupSelectedShopId || 0 }),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
                setupManageAllUsersData = setupManageAllUsersData.filter((u) => !selected.includes(Number(u.id || 0)));
                setupManageUsersRender();
                await setupLoadUsers();
            } catch (e) {
                console.error('Error deleting users:', e);
                alert('Error deleting users: ' + e.message);
            }
        }

        async function setupManageUsersEdit() {
            if (!setupCanManageUsers) return;
            // If currently in edit mode → save or exit
            if (setupManageUsersEditingId) {
                const userId = setupManageUsersEditingId;
                const snap = setupManageUsersEditSnapshot || {};
                const g = (id) => String(document.getElementById(id)?.value || '').trim();
                const newFirst = g(`mufirst_${userId}`);
                const newLast = g(`mulast_${userId}`);
                const newEmail = g(`muemail_${userId}`);
                const newShopId = Number(document.getElementById(`mushop_${userId}`)?.value || 0);
                const newRole = g(`murole_${userId}`);
                const changed =
                    newFirst !== (snap.first_name || '') ||
                    newLast !== (snap.last_name || '') ||
                    newEmail !== (snap.email || '') ||
                    newShopId !== Number(snap.shop_id || 0) ||
                    newRole !== (snap.role || '');
                if (changed) {
                    try {
                        const payload = {
                            id: userId,
                            first_name: newFirst,
                            last_name: newLast,
                            email: newEmail,
                            shop_id: newShopId || undefined,
                            role: newRole,
                        };
                        const resp = await fetch('/api/setup/users/admin-update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            credentials: 'include',
                            body: JSON.stringify(payload),
                        });
                        const data = await resp.json();
                        if (data.error) throw new Error(data.error);
                        // Update local list
                        const idx = setupManageAllUsersData.findIndex((u) => Number(u.id || 0) === userId);
                        if (idx >= 0) {
                            const newShopName = (setupManageAllShopsData.find((s) => Number(s.id || s.shop_id || 0) === newShopId) || {}).shop_name || snap.shop_name || '';
                            setupManageAllUsersData[idx] = {
                                ...setupManageAllUsersData[idx],
                                first_name: newFirst, last_name: newLast, email: newEmail,
                                shop_id: newShopId, shop_name: newShopName, role: newRole,
                            };
                        }
                        await setupLoadUsers();
                    } catch (e) {
                        console.error('Error saving user edit:', e);
                        alert('Error saving user: ' + e.message);
                        return;
                    }
                }
                setupManageUsersEditingId = 0;
                setupManageUsersEditSnapshot = null;
                setupManageUsersRender();
                return;
            }

            // Enter edit mode for single selected user
            const selected = setupManageUsersGetSelected();
            if (!selected.length) { alert('Select one user to edit.'); return; }
            if (selected.length > 1) { alert('Select only one user to edit.'); return; }
            const userId = selected[0];
            const user = setupManageAllUsersData.find((u) => Number(u.id || 0) === userId);
            if (!user) return;
            if (user.role_locked) { alert('Architect accounts cannot be edited here.'); return; }
            setupManageUsersEditingId = userId;
            setupManageUsersEditSnapshot = { ...user };
            setupManageUsersRender();
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

            const manageShopsModal = document.getElementById('setupManageShopsModal');
            if (manageShopsModal && manageShopsModal.style.display === 'block' && event.target === manageShopsModal) {
                closeSetupManageShopsModal();
                return;
            }

            const manageUsersModal = document.getElementById('setupManageUsersModal');
            if (manageUsersModal && manageUsersModal.style.display === 'block' && event.target === manageUsersModal) {
                closeSetupManageUsersModal();
                return;
            }

            const modal = document.getElementById('setupUserModal');
            if (!modal || modal.style.display !== 'block') return;
            if (event.target === modal) {
                closeSetupUserModal();
            }
        });
    """

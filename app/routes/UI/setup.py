"""Setup screen for shop profile and user management."""


def get_setup_screen_html():
    return """
    <div id="setup" class="screen" style="padding:20px;">
        <div id="setupLayout" style="width:80vw; margin:0 auto; display:flex; align-items:flex-start; gap:16px;">
            <div id="setupShopsPane" style="display:none; width:320px; background:#fff; padding:14px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="margin:0 0 10px 0; color:#333;">Shops</h4>
                <div id="setupShopsCards" style="display:flex; flex-direction:column; gap:10px; max-height:74vh; overflow-y:auto;">
                    <div style="color:#999; padding:8px;">Loading shops...</div>
                </div>
            </div>

            <div id="setupMainPane" style="flex:1; min-width:0; background:#fff; padding:24px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin:0 0 18px 0; color:#333;">Setup</h3>

                <div id="setupShopDisplay" style="text-align:center; margin-bottom:18px; color:#333;">
                    <div style="color:#999;">Loading shop information...</div>
                </div>

                <hr style="margin:24px 0; border:none; border-top:2px solid #d2d2d2;" />

                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; gap:10px;">
                    <button type="button" onclick="openSetupShopModal()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">SHOP INFO</button>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <button type="button" onclick="openSetupUserModal()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">+ USER</button>
                        <button type="button" onclick="setupResetSelectedUsers()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">RESET</button>
                        <button id="setupEditBtn" type="button" onclick="setupToggleEditUsers()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">EDIT</button>
                    </div>
                </div>

                <h4 style="margin:0 0 14px 0; color:#333;">Users</h4>

                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#23272a; color:#fff; text-align:left;">
                                <th style="padding:12px; border-bottom:2px solid #ddd; width:50px; text-align:center;">SEL</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd;">FIRST</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd;">LAST</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd;">EMAIL</th>
                                <th style="padding:12px; border-bottom:2px solid #ddd;">ROLE</th>
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
            try {
                const resp = await fetch('/api/setup/context', { credentials: 'include' });
                const data = await resp.json();
                setupIsArchitect = !!data.is_architect;
                setupDefaultDomain = String(data.default_domain || '').trim().toLowerCase();
                if (!setupSelectedShopDomain) {
                    setupSelectedShopDomain = setupDefaultDomain;
                }
                if (pane) pane.style.display = setupIsArchitect ? 'block' : 'none';
            } catch (error) {
                console.error('Error loading setup context:', error);
                setupIsArchitect = false;
                if (pane) pane.style.display = 'none';
            }
        }

        function setupBuildScopeQuery() {
            if (!setupIsArchitect || !setupSelectedShopDomain) return '';
            const scope = encodeURIComponent(setupSelectedShopDomain);
            return `?shop_domain=${scope}`;
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
                const domain = String(shop.domain || '').trim().toLowerCase();
                const isActive = domain && domain === setupSelectedShopDomain;
                const border = isActive ? '2px solid #b22222' : '1px solid #ddd';
                const bg = isActive ? '#f7ecec' : '#fff';
                const shopName = setupEscape(shop.shop_name || domain || 'Shop');
                const address = setupEscape(shop.address || '');
                const city = setupEscape(shop.city || '');
                const state = setupEscape(shop.state || '');
                const zip = setupEscape(shop.zip_code || '');
                const phone = setupEscape(shop.phone || '');
                const email = setupEscape(shop.email || '');
                const cityStateZip = [city, state, zip].filter(Boolean).join(', ').replace(/,\s([^,]+)$/, ' $1');
                return `
                    <button type="button" onclick="setupSelectShopCard('${setupEscape(domain)}')" style="width:100%; text-align:left; background:${bg}; border:${border}; border-radius:6px; padding:10px; cursor:pointer; color:#222;">
                        <div style="font-weight:700; margin-bottom:4px;">${shopName}</div>
                        ${address ? `<div style="font-size:12px; color:#444;">${address}</div>` : ''}
                        ${cityStateZip ? `<div style="font-size:12px; color:#444;">${cityStateZip}</div>` : ''}
                        ${phone ? `<div style="font-size:12px; color:#444;">${phone}</div>` : ''}
                        ${email ? `<div style="font-size:12px; color:#444;">${email}</div>` : ''}
                    </button>
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
                if (!setupSelectedShopDomain || !shops.some((s) => String(s.domain || '').trim().toLowerCase() === setupSelectedShopDomain)) {
                    setupSelectedShopDomain = String((shops[0] || {}).domain || setupDefaultDomain || '').trim().toLowerCase();
                }
                setupRenderShops();
            } catch (error) {
                console.error('Error loading shops:', error);
                if (cardsWrap) cardsWrap.innerHTML = '<div style="color:#c00; padding:8px;">Error loading shops.</div>';
            }
        }

        async function setupSelectShopCard(domain) {
            const nextDomain = String(domain || '').trim().toLowerCase();
            if (!nextDomain || nextDomain === setupSelectedShopDomain) return;
            setupSelectedShopDomain = nextDomain;
            setupRenderShops();
            await setupLoadUsers();
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
            body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>';
            try {
                const resp = await fetch(`/api/setup/users${setupBuildScopeQuery()}`, { credentials: 'include' });
                const data = await resp.json();
                const users = Array.isArray(data.users) ? data.users : [];
                setupUsersData = users;
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
                    const rowBg = idx % 2 === 0 ? '#f2f0ef' : '#ffffff';
                    const userId = Number(user.id || 0);
                    const roleOptions = ['Manager', 'Estimator', 'Tech', 'Receptionist', 'HR', 'Support']
                        .map((role) => `<option value="${role}" ${String(user.role || '') === role ? 'selected' : ''}>${role}</option>`)
                        .join('');
                    const disabledAttr = setupEditMode ? '' : 'disabled';
                    return `
                        <tr>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg}; text-align:center;">
                                <input type="checkbox" class="setup-user-select" data-user-id="${userId}" />
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">
                                <input ${disabledAttr} class="setup-user-first" data-user-id="${userId}" value="${setupEscape(user.first_name)}" style="width:100%; padding:8px;" />
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">
                                <input ${disabledAttr} class="setup-user-last" data-user-id="${userId}" value="${setupEscape(user.last_name)}" style="width:100%; padding:8px;" />
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">
                                <input ${disabledAttr} class="setup-user-email" data-user-id="${userId}" value="${setupEscape(user.email)}" style="width:100%; padding:8px;" />
                            </td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">
                                <select ${disabledAttr} class="setup-user-role" data-user-id="${userId}" style="width:100%; padding:8px;">${roleOptions}</select>
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

            const modal = document.getElementById('setupUserModal');
            if (!modal || modal.style.display !== 'block') return;
            if (event.target === modal) {
                closeSetupUserModal();
            }
        });
    """

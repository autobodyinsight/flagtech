"""Setup screen for user management."""


def get_setup_screen_html():
    return """
    <div id="setup" class="screen" style="padding:20px;">
        <style>
            #setup #setupMainPane {
                width: min(96vw, 1200px);
                margin: 0 auto;
                background: #fbfaf9;
                border: 1px solid #ddd6d2;
                border-radius: 14px;
                box-shadow: 0 10px 26px rgba(20, 20, 20, 0.08);
                padding: 26px;
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
        </style>

        <div id="setupMainPane">
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; margin:0 0 28px 0; padding:14px; background:rgba(0,0,0,0.02); border-radius:8px; border:1px solid rgba(0,0,0,0.06);">
                <h3 style="margin:0 0 8px 0; color:#333; font-size:18px;">Shop Information</h3>
                <div id="setupShopInfo" style="font-size:14px; color:#555; line-height:1.6;">Loading shop details...</div>
            </div>

            <h3 style="margin:0 0 18px 0; color:#333;">Setup</h3>

            <div style="display:flex; align-items:center; justify-content:flex-end; margin-bottom:8px; gap:8px;">
                <button type="button" onclick="openSetupUserModal()" class="setup-action-btn" style="background:#b22222; color:#fff;">+ USER</button>
                <button type="button" onclick="setupResetSelectedUsers()" class="setup-action-btn" style="background:#b22222; color:#fff;">RESET</button>
                <button type="button" onclick="setupPromptDeleteSelectedUsers()" class="setup-action-btn" style="background:#111; color:#fff;">DELETE</button>
                <button id="setupEditBtn" type="button" onclick="setupToggleEditUsers()" class="setup-action-btn" style="background:#b22222; color:#fff;">EDIT</button>
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

        <div id="setupDeleteConfirmModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:520px; padding:24px;">
                <div id="setupDeleteConfirmTitle" style="font-size:20px; font-weight:800; color:#111; margin-bottom:12px;">YOU'RE ABOUT TO DELETE SELECTED USER</div>
                <div style="font-size:14px; line-height:1.5; color:#333; margin-bottom:18px;">
                    This action permanently deletes the selected user record and cannot be undone.
                </div>
                <div style="display:flex; justify-content:flex-end; gap:10px;">
                    <button type="button" onclick="closeSetupDeleteConfirmModal()" style="padding:10px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Cancel</button>
                    <button id="setupDeleteConfirmBtn" type="button" onclick="setupDeleteSelectedUsers()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Confirm</button>
                </div>
            </div>
        </div>

        <div id="setupResetPasswordModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:520px; padding:24px;">
                <div style="font-size:20px; font-weight:800; color:#111; margin-bottom:12px;">RESET USER PASSWORD</div>
                <div style="font-size:14px; line-height:1.5; color:#333; margin-bottom:12px;">
                    Enter a new password for the selected user(s).
                </div>
                <div style="margin-bottom:18px;">
                    <label for="setupResetPasswordInput" style="display:block; font-weight:700; color:#333; margin-bottom:6px;">New Password</label>
                    <input id="setupResetPasswordInput" type="password" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div style="display:flex; justify-content:flex-end; gap:10px;">
                    <button type="button" onclick="closeSetupResetPasswordModal()" style="padding:10px 14px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Cancel</button>
                    <button id="setupResetPasswordSaveBtn" type="button" onclick="setupSaveResetPassword()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save</button>
                </div>
            </div>
        </div>

    </div>
    """


def get_setup_script():
    return """
        let setupUsersData = [];
        let setupShopData = {};
        let setupEditMode = false;
        let setupPendingDeleteUserIds = [];
        let setupPendingResetUserIds = [];
        let setupUsersLastLoadedAt = 0;
        let setupShopLastLoadedAt = 0;
        let setupUsersInFlightPromise = null;
        let setupShopInFlightPromise = null;
        let setupUsersRequestToken = 0;
        let setupShopRequestToken = 0;
        const setupUsersTtlMs = 15000;
        const setupShopTtlMs = 30000;

        function setupEscape(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        async function setupReadJsonResponse(resp) {
            const raw = await resp.text();
            if (!raw) return {};
            try {
                return JSON.parse(raw);
            } catch (_error) {
                return { error: raw };
            }
        }

        async function setupLoadData(force = false) {
            const hasCachedUsers = Array.isArray(setupUsersData) && setupUsersData.length > 0;
            const isFresh = hasCachedUsers && (Date.now() - setupUsersLastLoadedAt) < setupUsersTtlMs;
            if (!force && isFresh) {
                setupRenderUsers();
                return;
            }
            await Promise.all([setupLoadShop({ force }), setupLoadUsers({ force })]);
        }

        async function setupLoadShop(options = {}) {
            const force = !!options.force;
            const hasCachedShop = Object.keys(setupShopData).length > 0;
            const isFresh = hasCachedShop && (Date.now() - setupShopLastLoadedAt) < setupShopTtlMs;
            if (!force && isFresh) {
                setupRenderShopInfo();
                return;
            }

            if (setupShopInFlightPromise && !force) {
                return setupShopInFlightPromise;
            }

            const loadPromise = (async () => {
                const requestToken = ++setupShopRequestToken;
                try {
                    const resp = await fetch('/api/setup/shop', { credentials: 'include' });
                    const data = await resp.json().catch(() => ({}));
                    if (!resp.ok || data.error) {
                        throw new Error(data.error || `Failed to load shop (${resp.status})`);
                    }
                    if (requestToken !== setupShopRequestToken) {
                        return;
                    }
                    setupShopData = data.shop || {};
                    setupShopLastLoadedAt = Date.now();
                    setupRenderShopInfo();
                } catch (error) {
                    console.error('Error loading shop info:', error);
                    const shopInfoEl = document.getElementById('setupShopInfo');
                    if (shopInfoEl) {
                        shopInfoEl.innerHTML = '<span style="color:#c00;">Unable to load shop information.</span>';
                    }
                }
            })();

            setupShopInFlightPromise = loadPromise;
            try {
                await loadPromise;
            } finally {
                if (setupShopInFlightPromise === loadPromise) {
                    setupShopInFlightPromise = null;
                }
            }
        }

        function setupRenderShopInfo() {
            const infoEl = document.getElementById('setupShopInfo');
            if (!infoEl) return;
            const shop = setupShopData || {};
            const name = setupEscape(shop.shop_name || '');
            const address = setupEscape(shop.address || '');
            const city = setupEscape(shop.city || '');
            const state = setupEscape(shop.state || '');
            const zip = setupEscape(shop.zip_code || '');
            const phone = setupEscape(shop.phone || '');
            const email = setupEscape(shop.email || '');
            
            let html = `<strong>${name}</strong>`;
            if (address) html += `<div>${address}</div>`;
            const cityStateZip = [city, state].filter(v => v).join(', ') + (zip ? ` ${zip}` : '');
            if (cityStateZip.trim()) html += `<div>${cityStateZip}</div>`;
            if (phone) html += `<div>${phone}</div>`;
            if (email) html += `<div>${email}</div>`;
            
            infoEl.innerHTML = html;
        }

        async function setupLoadUsers(options = {}) {
            const force = !!options.force;
            const retryCount = Number.isFinite(Number(options.retryCount)) ? Number(options.retryCount) : 1;
            if (setupUsersInFlightPromise && !force) {
                return setupUsersInFlightPromise;
            }

            const loadPromise = (async () => {
            const body = document.getElementById('setupUsersBody');
            if (!body) return;
            const hasCachedUsers = Array.isArray(setupUsersData) && setupUsersData.length > 0;
            if (!hasCachedUsers) {
                body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>';
            }

            const requestToken = ++setupUsersRequestToken;
            let lastError = null;

            for (let attempt = 0; attempt <= retryCount; attempt += 1) {
                try {
                    const resp = await fetch('/api/setup/users', { credentials: 'include' });
                    const data = await resp.json().catch(() => ({}));
                    if (!resp.ok || data.error) {
                        throw new Error(data.error || `Failed to load users (${resp.status})`);
                    }
                    if (requestToken !== setupUsersRequestToken) {
                        return;
                    }

                    setupUsersData = Array.isArray(data.users) ? data.users : [];
                    setupUsersLastLoadedAt = Date.now();
                    if (!setupUsersData.length) {
                        body.innerHTML = '<tr><td colspan="5" style="padding:18px; text-align:center; color:#999;">No users found.</td></tr>';
                        return;
                    }

                    setupRenderUsers();
                    return;
                } catch (error) {
                    lastError = error;
                    if (attempt < retryCount) {
                        await new Promise((resolve) => setTimeout(resolve, 250));
                    }
                }
            }

            if (requestToken !== setupUsersRequestToken) {
                return;
            }

            console.error('Error loading setup users:', lastError);
            if (Array.isArray(setupUsersData) && setupUsersData.length) {
                setupRenderUsers();
                return;
                }
            body.innerHTML = `<tr><td colspan="5" style="padding:18px; text-align:center; color:#c00;">${setupEscape(String(lastError?.message || 'Error loading users.'))}</td></tr>`;
            })();

            setupUsersInFlightPromise = loadPromise;
            try {
                await loadPromise;
            } finally {
                if (setupUsersInFlightPromise === loadPromise) {
                    setupUsersInFlightPromise = null;
                }
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

            body.innerHTML = users.map((user) => {
                const userId = Number(user.id || 0);
                const roleLocked = !!user.role_locked;
                const rowWeight = roleLocked ? '800' : '400';
                const roleText = setupEscape(user.role || '');
                const roleOptions = ['Manager', 'Estimator', 'Tech', 'Receptionist', 'HR', 'Support']
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
                    const resp = await fetch('/api/setup/users/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(payload),
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

            setupPendingResetUserIds = selected;
            openSetupResetPasswordModal();
        }

        function openSetupResetPasswordModal() {
            const modal = document.getElementById('setupResetPasswordModal');
            const input = document.getElementById('setupResetPasswordInput');
            if (!modal) return;
            modal.style.display = 'block';
            if (input) {
                input.value = '';
                input.focus();
            }
        }

        function closeSetupResetPasswordModal() {
            const modal = document.getElementById('setupResetPasswordModal');
            const input = document.getElementById('setupResetPasswordInput');
            if (modal) modal.style.display = 'none';
            if (input) input.value = '';
            setupPendingResetUserIds = [];
        }

        async function setupSaveResetPassword() {
            if (!setupPendingResetUserIds.length) {
                closeSetupResetPasswordModal();
                return;
            }

            const input = document.getElementById('setupResetPasswordInput');
            const saveBtn = document.getElementById('setupResetPasswordSaveBtn');
            const newPassword = String(input?.value || '').trim();
            if (!newPassword) {
                alert('Enter a new password.');
                return;
            }

            if (saveBtn) saveBtn.disabled = true;

            try {
                const resp = await fetch('/api/setup/users/reset-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ user_ids: setupPendingResetUserIds, new_password: newPassword }),
                });
                const data = await setupReadJsonResponse(resp);
                if (!resp.ok || data.error) throw new Error(data.error || 'Unable to reset password');
                closeSetupResetPasswordModal();
                alert('Password reset complete.');
            } catch (error) {
                console.error('Error resetting passwords:', error);
                alert(String(error.message || 'Error resetting password.'));
            } finally {
                if (saveBtn) saveBtn.disabled = false;
            }
        }

        function openSetupDeleteConfirmModal() {
            const modal = document.getElementById('setupDeleteConfirmModal');
            if (modal) modal.style.display = 'block';
        }

        function closeSetupDeleteConfirmModal() {
            const modal = document.getElementById('setupDeleteConfirmModal');
            if (modal) modal.style.display = 'none';
            setupPendingDeleteUserIds = [];
        }

        function setupPromptDeleteSelectedUsers() {
            const selected = Array.from(document.querySelectorAll('.setup-user-select:checked'))
                .map((el) => Number(el.getAttribute('data-user-id') || 0))
                .filter((val) => Number.isFinite(val) && val > 0);

            if (!selected.length) {
                alert('Select at least one user to delete.');
                return;
            }

            setupPendingDeleteUserIds = selected;
            const titleEl = document.getElementById('setupDeleteConfirmTitle');
            if (titleEl) {
                titleEl.textContent = selected.length > 1
                    ? "YOU'RE ABOUT TO DELETE SELECTED USERS"
                    : "YOU'RE ABOUT TO DELETE SELECTED USER";
            }
            openSetupDeleteConfirmModal();
        }

        async function setupDeleteSelectedUsers() {
            if (!setupPendingDeleteUserIds.length) {
                closeSetupDeleteConfirmModal();
                return;
            }

            const confirmBtn = document.getElementById('setupDeleteConfirmBtn');
            if (confirmBtn) confirmBtn.disabled = true;
            try {
                const resp = await fetch('/api/setup/users/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ user_ids: setupPendingDeleteUserIds }),
                });
                const data = await setupReadJsonResponse(resp);
                if (!resp.ok || data.error) throw new Error(data.error || 'Unable to delete user');
                closeSetupDeleteConfirmModal();
                await setupLoadUsers();
            } catch (error) {
                console.error('Error deleting selected users:', error);
                alert(String(error.message || 'Error deleting selected user.'));
            } finally {
                if (confirmBtn) confirmBtn.disabled = false;
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
            const modal = document.getElementById('setupUserModal');
            if (modal && modal.style.display === 'block' && event.target === modal) {
                closeSetupUserModal();
            }

            const deleteModal = document.getElementById('setupDeleteConfirmModal');
            if (deleteModal && deleteModal.style.display === 'block' && event.target === deleteModal) {
                closeSetupDeleteConfirmModal();
            }

            const resetModal = document.getElementById('setupResetPasswordModal');
            if (resetModal && resetModal.style.display === 'block' && event.target === resetModal) {
                closeSetupResetPasswordModal();
            }
        });

        document.addEventListener('keydown', (event) => {
            const resetModal = document.getElementById('setupResetPasswordModal');
            const input = document.getElementById('setupResetPasswordInput');
            if (!resetModal || resetModal.style.display !== 'block') {
                return;
            }

            if (event.key === 'Escape') {
                closeSetupResetPasswordModal();
                return;
            }

            if (event.key === 'Enter' && document.activeElement === input) {
                event.preventDefault();
                setupSaveResetPassword();
            }
        });
    """

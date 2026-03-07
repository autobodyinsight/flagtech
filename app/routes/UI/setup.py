"""Setup screen for shop profile and user management."""


def get_setup_screen_html():
    return """
    <div id="setup" class="screen" style="padding:20px;">
        <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); max-width:980px;">
            <h3 style="margin:0 0 18px 0; color:#333;">Setup</h3>

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
                    <label for="setupShopPhone" style="font-weight:bold; color:#333;">Phone Number</label>
                    <input id="setupShopPhone" type="text" style="width:100%; padding:10px; margin-top:6px;" />
                </div>
                <div>
                    <label for="setupShopEmail" style="font-weight:bold; color:#333;">Email</label>
                    <input id="setupShopEmail" type="email" style="width:100%; padding:10px; margin-top:6px;" />
                </div>
            </div>

            <div style="margin-top:14px; text-align:right;">
                <button id="setupShopSaveBtn" type="button" onclick="setupSaveShop()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save</button>
            </div>

            <hr style="margin:24px 0; border:none; border-top:2px solid #d2d2d2;" />

            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
                <h4 style="margin:0; color:#333;">Users</h4>
                <button type="button" onclick="openSetupUserModal()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">+ USER</button>
            </div>

            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="background:#23272a; color:#fff; text-align:left;">
                            <th style="padding:12px; border-bottom:2px solid #ddd;">FIRST</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd;">LAST</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd;">EMAIL</th>
                            <th style="padding:12px; border-bottom:2px solid #ddd;">ROLE</th>
                        </tr>
                    </thead>
                    <tbody id="setupUsersBody">
                        <tr><td colspan="4" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>
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
    </div>
    """


def get_setup_script():
    return """
        async function setupLoadData() {
            await Promise.all([setupLoadShop(), setupLoadUsers()]);
        }

        async function setupLoadShop() {
            try {
                const resp = await fetch('/api/setup/shop', { credentials: 'include' });
                const data = await resp.json();
                const shop = data.shop || {};
                const set = (id, value) => {
                    const el = document.getElementById(id);
                    if (el) el.value = String(value || '');
                };
                set('setupShopName', shop.shop_name);
                set('setupShopAddress', shop.address);
                set('setupShopPhone', shop.phone);
                set('setupShopEmail', shop.email);
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
                    phone: (document.getElementById('setupShopPhone')?.value || '').trim(),
                    email: (document.getElementById('setupShopEmail')?.value || '').trim(),
                };

                const resp = await fetch('/api/setup/shop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
            } catch (error) {
                console.error('Error saving shop setup:', error);
                alert('Error saving shop information.');
            } finally {
                if (btn) btn.disabled = false;
            }
        }

        async function setupLoadUsers() {
            const body = document.getElementById('setupUsersBody');
            if (!body) return;
            body.innerHTML = '<tr><td colspan="4" style="padding:18px; text-align:center; color:#999;">Loading...</td></tr>';
            try {
                const resp = await fetch('/api/setup/users', { credentials: 'include' });
                const data = await resp.json();
                const users = Array.isArray(data.users) ? data.users : [];
                if (!users.length) {
                    body.innerHTML = '<tr><td colspan="4" style="padding:18px; text-align:center; color:#999;">No users found.</td></tr>';
                    return;
                }

                body.innerHTML = users.map((user, idx) => {
                    const rowBg = idx % 2 === 0 ? '#f2f0ef' : '#ffffff';
                    const esc = (val) => String(val || '')
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/\"/g, '&quot;')
                        .replace(/'/g, '&#39;');
                    return `
                        <tr>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">${esc(user.first_name)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">${esc(user.last_name)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">${esc(user.email)}</td>
                            <td style="padding:12px; border-bottom:1px solid #eee; background:${rowBg};">${esc(user.role)}</td>
                        </tr>
                    `;
                }).join('');
            } catch (error) {
                console.error('Error loading setup users:', error);
                body.innerHTML = '<tr><td colspan="4" style="padding:18px; text-align:center; color:#c00;">Error loading users.</td></tr>';
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
            if (!modal || modal.style.display !== 'block') return;
            if (event.target === modal) {
                closeSetupUserModal();
            }
        });
    """

"""Users management screen content."""


def get_users_screen_html():
    return r"""
    <div id="users" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">USERS</h1>

        <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:12px; margin-bottom:16px; flex-wrap:wrap;">
            <div>
                <div style="font-size:12px; color:#666;">Current Shop Domain</div>
                <div id="usersDomainLabel" style="font-weight:bold;">-</div>
                <div id="usersAccessLevelLabel" style="font-size:12px; color:#666; margin-top:4px;"></div>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                <div id="usersStatus" style="font-size:12px; color:#666; min-height:18px;"></div>
                <button onclick="logoutCurrentUser()" style="padding:10px 14px; background:#b22222; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Log Out</button>
            </div>
        </div>

        <div id="usersArchitectPanel" style="display:none; background:#fff; border:1px solid #ddd; border-radius:6px; padding:12px; margin-bottom:16px;">
            <div style="font-weight:bold; margin-bottom:10px;">Architect Controls</div>
            <div style="display:grid; grid-template-columns:1fr auto auto; gap:8px; align-items:end;">
                <div>
                    <label for="usersShopDomain" style="display:block; margin-bottom:4px;">Shop Domain</label>
                    <input id="usersShopDomain" type="text" placeholder="example.com" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <button onclick="applyUsersShopDomain()" style="padding:10px 14px; background:#3c4142; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Load Shop</button>
                <button onclick="clearShopData()" style="padding:10px 14px; background:#b22222; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Clear Shop Data</button>
            </div>

            <div style="margin-top:14px; border:1px solid #ddd; border-radius:6px; overflow:hidden;">
                <div style="display:flex; justify-content:space-between; align-items:center; background:#f7f7f7; padding:8px 10px; border-bottom:1px solid #ddd;">
                    <div style="font-weight:bold;">Architect Audit Log</div>
                    <button onclick="loadArchitectAuditLogs()" style="padding:6px 10px; background:#3c4142; color:#fff; border:none; border-radius:4px; cursor:pointer;">Refresh</button>
                </div>
                <div id="architectAuditList" style="max-height:240px; overflow:auto; background:#fff;"></div>
            </div>
        </div>

        <div id="usersAddPanel" style="background:#fff; border:1px solid #ddd; border-radius:6px; padding:12px; margin-bottom:16px;">
            <div style="font-weight:bold; margin-bottom:8px;">Add User</div>
            <div style="display:grid; grid-template-columns:1.1fr 0.8fr 0.8fr 1fr 1fr 1fr auto; gap:8px; align-items:end;">
                <div>
                    <label for="newUserEmail" style="display:block; margin-bottom:4px;">Email</label>
                    <input id="newUserEmail" type="email" placeholder="name@yourdomain.com" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div>
                    <label for="newUserFirstName" style="display:block; margin-bottom:4px;">First Name</label>
                    <input id="newUserFirstName" type="text" placeholder="First" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div>
                    <label for="newUserLastName" style="display:block; margin-bottom:4px;">Last Name</label>
                    <input id="newUserLastName" type="text" placeholder="Last" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div>
                    <label for="newUserPassword" style="display:block; margin-bottom:4px;">Password</label>
                    <input id="newUserPassword" type="password" placeholder="Minimum 8 chars" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div>
                    <label for="newUserCompany" style="display:block; margin-bottom:4px;">Company Name</label>
                    <input id="newUserCompany" type="text" placeholder="Shop Name" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div id="addUserShopDomainWrap" style="display:none;">
                    <label for="newUserShopDomain" style="display:block; margin-bottom:4px;">Shop Domain</label>
                    <input id="newUserShopDomain" type="text" placeholder="example.com" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div>
                    <label for="newUserAccessLevel" style="display:block; margin-bottom:4px;">Access Level</label>
                    <select id="newUserAccessLevel" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                        <option value="support">support</option>
                        <option value="reception">reception</option>
                        <option value="parts">parts</option>
                        <option value="estimator">estimator</option>
                        <option value="manager">manager</option>
                    </select>
                </div>
                <button onclick="createUser()" style="padding:10px 16px; background:#b22222; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Create</button>
            </div>
        </div>

        <div style="background:#fff; border:1px solid #ddd; border-radius:6px; overflow:hidden;">
            <div style="display:flex; background:#3c4142; color:#fff; padding:10px; font-weight:bold;">
                <div style="flex:1.3;">Email</div>
                <div style="flex:0.9;">First Name</div>
                <div style="flex:0.9;">Last Name</div>
                <div style="flex:1;">Shop</div>
                <div style="flex:1.1;">Company</div>
                <div style="flex:0.9; text-align:center;">Access Level</div>
                <div style="flex:0.8; text-align:center;">Status</div>
                <div style="flex:1.1; text-align:center;">Last Login</div>
                <div style="flex:1.1; text-align:right;">Actions</div>
            </div>
            <div id="usersListContainer"></div>
        </div>
    </div>

    <script>
    function usersEscapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function setUsersStatus(message, color) {
        const el = document.getElementById('usersStatus');
        if (!el) return;
        el.textContent = message || '';
        el.style.color = color || '#666';
    }

    function formatUsersDate(value) {
        if (!value) return '-';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return '-';
        return date.toLocaleString();
    }

    function usersCanManage() {
        return window.__usersCanManage === true;
    }

    function logoutCurrentUser() {
        window.location.href = '/auth/logout';
    }

    function usersIsArchitect() {
        return window.__usersIsArchitect === true;
    }

    function currentUsersShopDomain() {
        return String(window.__usersSelectedShopDomain || '').trim().toLowerCase();
    }

    function applyUsersShopDomain() {
        const input = document.getElementById('usersShopDomain');
        if (!input) return;
        window.__usersSelectedShopDomain = String(input.value || '').trim().toLowerCase();
        loadUsersList();
    }

    async function loadArchitectAuditLogs() {
        const list = document.getElementById('architectAuditList');
        if (!list || !usersIsArchitect()) return;

        list.innerHTML = '<div style="padding:10px; color:#666;">Loading audit log...</div>';
        try {
            const params = new URLSearchParams();
            if (currentUsersShopDomain()) {
                params.set('shop_domain', currentUsersShopDomain());
            }
            params.set('limit', '100');

            const response = await fetch(`/api/architect/audit-logs?${params.toString()}`, { credentials: 'include' });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to load audit log');
            }

            const logs = Array.isArray(payload.logs) ? payload.logs : [];
            if (!logs.length) {
                list.innerHTML = '<div style="padding:10px; color:#666;">No architect actions logged yet.</div>';
                return;
            }

            list.innerHTML = logs.map((entry) => {
                const when = formatUsersDate(entry.created_at);
                const action = usersEscapeHtml(entry.action || '-');
                const targetEmail = usersEscapeHtml(entry.target_email || '-');
                const targetDomain = usersEscapeHtml(entry.target_domain || '-');
                const actor = usersEscapeHtml(entry.actor_email || '-');
                return `
                    <div style="padding:8px 10px; border-top:1px solid #eee; font-size:12px;">
                        <div style="font-weight:bold;">${action}</div>
                        <div style="color:#444;">Actor: ${actor} | Target User: ${targetEmail} | Shop: ${targetDomain}</div>
                        <div style="color:#666;">${when}</div>
                    </div>
                `;
            }).join('');
        } catch (err) {
            console.error('Error loading architect audit log:', err);
            list.innerHTML = `<div style="padding:10px; color:#b22222;">${usersEscapeHtml(err.message || 'Unable to load audit log')}</div>`;
        }
    }

    async function loadUsersList() {
        const list = document.getElementById('usersListContainer');
        const domainLabel = document.getElementById('usersDomainLabel');
        const accessLevelLabel = document.getElementById('usersAccessLevelLabel');
        const addPanel = document.getElementById('usersAddPanel');
        const architectPanel = document.getElementById('usersArchitectPanel');
        const addUserShopDomainWrap = document.getElementById('addUserShopDomainWrap');
        const usersShopDomainInput = document.getElementById('usersShopDomain');
        if (!list) return;

        list.innerHTML = '<div style="padding:12px; color:#666;">Loading users...</div>';
        try {
            const params = new URLSearchParams();
            if (currentUsersShopDomain()) {
                params.set('shop_domain', currentUsersShopDomain());
            }
            const response = await fetch(`/api/users${params.toString() ? `?${params.toString()}` : ''}`, { credentials: 'include' });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to load users');
            }

            if (domainLabel) {
                domainLabel.textContent = payload.domain || '-';
            }

            const myAccessLevel = String(payload.my_access_level || 'support');
            window.__usersCanManage = !!payload.can_manage_users;
            window.__usersIsArchitect = !!payload.is_architect;
            if (accessLevelLabel) {
                accessLevelLabel.textContent = `My access level: ${myAccessLevel}`;
            }
            if (addPanel) {
                addPanel.style.display = usersCanManage() ? '' : 'none';
            }
            if (architectPanel) {
                architectPanel.style.display = usersIsArchitect() ? '' : 'none';
            }
            if (addUserShopDomainWrap) {
                addUserShopDomainWrap.style.display = usersIsArchitect() ? '' : 'none';
            }
            if (usersShopDomainInput && usersIsArchitect() && !usersShopDomainInput.value && payload.domain) {
                usersShopDomainInput.value = payload.domain;
                window.__usersSelectedShopDomain = payload.domain;
            }
            if (usersIsArchitect()) {
                await loadArchitectAuditLogs();
            }

            const users = Array.isArray(payload.users) ? payload.users : [];
            if (!users.length) {
                list.innerHTML = '<div style="padding:12px; color:#666;">No users for this shop.</div>';
                return;
            }

            list.innerHTML = users.map((user) => {
                const isActive = !!user.active;
                const canManage = usersCanManage();
                const actionsHtml = canManage
                    ? `
                        <button onclick="toggleUserActive(${user.id}, ${isActive ? 'false' : 'true'})" style="padding:6px 8px; border:1px solid #bbb; background:#fff; border-radius:4px; cursor:pointer;">${isActive ? 'Deactivate' : 'Activate'}</button>
                        <button onclick="resetUserPassword(${user.id})" style="padding:6px 8px; border:1px solid #bbb; background:#fff; border-radius:4px; cursor:pointer;">Reset Password</button>
                        ${usersIsArchitect() ? `<button onclick="deleteUser(${user.id}, '${usersEscapeHtml(user.email)}')" style="padding:6px 8px; border:1px solid #bbb; background:#fff; border-radius:4px; cursor:pointer;">Delete</button>` : ''}
                    `
                    : '<span style="color:#666;">-</span>';
                return `
                    <div style="display:flex; padding:10px; border-top:1px solid #eee; align-items:center; gap:10px;">
                        <div style="flex:1.3;">${usersEscapeHtml(user.email)}</div>
                        <div style="flex:0.9;">${usersEscapeHtml(user.first_name || '-')}</div>
                        <div style="flex:0.9;">${usersEscapeHtml(user.last_name || '-')}</div>
                        <div style="flex:1;">${usersEscapeHtml(user.domain || '-')}</div>
                        <div style="flex:1.1;">${usersEscapeHtml(user.company_name || '-')}</div>
                        <div style="flex:0.9; text-align:center; text-transform:capitalize;">${usersEscapeHtml(user.access_level || 'support')}</div>
                        <div style="flex:0.8; text-align:center; font-weight:bold; color:${isActive ? '#2e7d32' : '#9e9e9e'};">${isActive ? 'Active' : 'Inactive'}</div>
                        <div style="flex:1.1; text-align:center;">${usersEscapeHtml(formatUsersDate(user.last_login))}</div>
                        <div style="flex:1.1; text-align:right; display:flex; justify-content:flex-end; gap:6px;">
                            ${actionsHtml}
                        </div>
                    </div>
                `;
            }).join('');
        } catch (err) {
            console.error('Error loading users:', err);
            list.innerHTML = `<div style="padding:12px; color:#b22222;">${usersEscapeHtml(err.message || 'Unable to load users')}</div>`;
        }
    }

    async function createUser() {
        const emailEl = document.getElementById('newUserEmail');
        const firstNameEl = document.getElementById('newUserFirstName');
        const lastNameEl = document.getElementById('newUserLastName');
        const passwordEl = document.getElementById('newUserPassword');
        const companyEl = document.getElementById('newUserCompany');
        const shopDomainEl = document.getElementById('newUserShopDomain');
        const accessLevelEl = document.getElementById('newUserAccessLevel');
        if (!emailEl || !firstNameEl || !lastNameEl || !passwordEl || !companyEl || !accessLevelEl) return;

        const email = String(emailEl.value || '').trim().toLowerCase();
        const first_name = String(firstNameEl.value || '').trim();
        const last_name = String(lastNameEl.value || '').trim();
        const password = String(passwordEl.value || '');
        const company_name = String(companyEl.value || '').trim();
        const access_level = String(accessLevelEl.value || 'support').trim().toLowerCase();
        const shop_domain = usersIsArchitect()
            ? String((shopDomainEl && shopDomainEl.value) || currentUsersShopDomain()).trim().toLowerCase()
            : '';

        if (!email || !password) {
            setUsersStatus('Email and password are required.', '#b22222');
            return;
        }
        if (!first_name || !last_name) {
            setUsersStatus('First and last name are required.', '#b22222');
            return;
        }

        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, first_name, last_name, password, company_name, access_level, shop_domain }),
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to create user');
            }

            emailEl.value = '';
            firstNameEl.value = '';
            lastNameEl.value = '';
            passwordEl.value = '';
            if (shopDomainEl && usersIsArchitect()) {
                shopDomainEl.value = shop_domain || currentUsersShopDomain();
            }
            accessLevelEl.value = 'support';
            setUsersStatus('User created.', '#2e7d32');
            await loadUsersList();
        } catch (err) {
            console.error('Error creating user:', err);
            setUsersStatus(err.message || 'Unable to create user', '#b22222');
        }
    }

    async function toggleUserActive(userId, active) {
        try {
            const response = await fetch(`/api/users/${userId}/active`, {
                method: 'PATCH',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ active }),
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to update user');
            }

            setUsersStatus('User updated.', '#2e7d32');
            await loadUsersList();
        } catch (err) {
            console.error('Error updating user:', err);
            setUsersStatus(err.message || 'Unable to update user', '#b22222');
        }
    }

    async function resetUserPassword(userId) {
        const nextPassword = window.prompt('Enter new password (minimum 8 characters):');
        if (!nextPassword) return;

        try {
            const response = await fetch(`/api/users/${userId}/password`, {
                method: 'PATCH',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: nextPassword }),
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to reset password');
            }

            setUsersStatus('Password reset.', '#2e7d32');
        } catch (err) {
            console.error('Error resetting password:', err);
            setUsersStatus(err.message || 'Unable to reset password', '#b22222');
        }
    }

    async function deleteUser(userId, email) {
        if (!usersIsArchitect()) return;
        const confirmed = window.confirm(`Delete user ${email}? This cannot be undone.`);
        if (!confirmed) return;

        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'DELETE',
                credentials: 'include',
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to delete user');
            }

            setUsersStatus('User deleted.', '#2e7d32');
            await loadUsersList();
        } catch (err) {
            console.error('Error deleting user:', err);
            setUsersStatus(err.message || 'Unable to delete user', '#b22222');
        }
    }

    async function clearShopData() {
        if (!usersIsArchitect()) return;
        const shopDomain = currentUsersShopDomain();
        if (!shopDomain) {
            setUsersStatus('Enter a shop domain first.', '#b22222');
            return;
        }

        const confirmed = window.confirm(`Clear all data for shop ${shopDomain}? This cannot be undone.`);
        if (!confirmed) return;

        try {
            const response = await fetch(`/api/shops/${encodeURIComponent(shopDomain)}/clear-data`, {
                method: 'POST',
                credentials: 'include',
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to clear shop data');
            }

            setUsersStatus(`Shop data cleared for ${shopDomain}.`, '#2e7d32');
            await loadUsersList();
        } catch (err) {
            console.error('Error clearing shop data:', err);
            setUsersStatus(err.message || 'Unable to clear shop data', '#b22222');
        }
    }
    </script>
    """

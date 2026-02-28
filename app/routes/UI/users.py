"""Users management screen content."""


def get_users_screen_html():
    return r"""
    <div id="users" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">USERS</h1>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; gap:10px; flex-wrap:wrap;">
            <div id="usersStatus" style="font-size:12px; color:#666; min-height:18px;"></div>
            <div style="display:flex; gap:8px;">
                <button onclick="loadUsersList()" style="padding:10px 14px; border:none; border-radius:4px; cursor:pointer;">Refresh</button>
                <button onclick="logoutCurrentUser()" style="padding:10px 14px; border:none; border-radius:4px; cursor:pointer;">Log Out</button>
            </div>
        </div>

        <div style="background:#fff; border:1px solid #ddd; border-radius:6px; padding:12px; margin-bottom:16px;">
            <div style="font-weight:bold; margin-bottom:8px;">Create User</div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr auto; gap:8px; align-items:end;">
                <div>
                    <label for="newUserEmail" style="display:block; margin-bottom:4px;">Email</label>
                    <input id="newUserEmail" type="email" placeholder="name@domain.com" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div>
                    <label for="newUserRole" style="display:block; margin-bottom:4px;">Role</label>
                    <select id="newUserRole" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                        <option value="user">user</option>
                        <option value="admin">admin</option>
                        <option value="manager">manager</option>
                        <option value="estimator">estimator</option>
                        <option value="tech">tech</option>
                    </select>
                </div>
                <div>
                    <label for="newUserPassword" style="display:block; margin-bottom:4px;">Password</label>
                    <input id="newUserPassword" type="password" placeholder="minimum 8 chars" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                </div>
                <div style="font-size:12px; color:#666;">Use row actions to update role/email/password later.</div>
                <button onclick="createManagedUser()" style="padding:10px 16px; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Create</button>
            </div>
        </div>

        <div style="background:#fff; border:1px solid #ddd; border-radius:6px; overflow:hidden;">
            <div style="display:flex; background:#3c4142; color:#fff; padding:10px; font-weight:bold;">
                <div style="flex:1.6;">Email</div>
                <div style="flex:0.8; text-align:center;">Role</div>
                <div style="flex:1.1; text-align:center;">Created</div>
                <div style="flex:1.1; text-align:center;">Updated</div>
                <div style="flex:1.5; text-align:right;">Actions</div>
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

    function logoutCurrentUser() {
        window.location.href = '/auth/logout';
    }

    async function loadUsersList() {
        const list = document.getElementById('usersListContainer');
        if (!list) return;

        list.innerHTML = '<div style="padding:12px; color:#666;">Loading users...</div>';
        try {
            const response = await fetch('/api/users', { credentials: 'include' });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to load users');
            }

            const users = Array.isArray(payload.users) ? payload.users : [];
            if (!users.length) {
                list.innerHTML = '<div style="padding:12px; color:#666;">No users found.</div>';
                return;
            }

            list.innerHTML = users.map((user) => {
                const id = Number(user.id);
                return `
                    <div style="display:flex; padding:10px; border-top:1px solid #eee; align-items:center; gap:10px;">
                        <div style="flex:1.6;">${usersEscapeHtml(user.email)}</div>
                        <div style="flex:0.8; text-align:center; text-transform:lowercase;">${usersEscapeHtml(user.role || 'user')}</div>
                        <div style="flex:1.1; text-align:center;">${usersEscapeHtml(formatUsersDate(user.created_at))}</div>
                        <div style="flex:1.1; text-align:center;">${usersEscapeHtml(formatUsersDate(user.updated_at))}</div>
                        <div style="flex:1.5; text-align:right; display:flex; justify-content:flex-end; gap:6px;">
                            <button onclick="updateManagedUser(${id}, '${usersEscapeHtml(user.email)}', '${usersEscapeHtml(user.role || 'user')}')" style="padding:6px 8px; border:1px solid #bbb; background:#fff; border-radius:4px; cursor:pointer;">Update</button>
                            <button onclick="deleteManagedUser(${id}, '${usersEscapeHtml(user.email)}')" style="padding:6px 8px; border:1px solid #bbb; background:#fff; border-radius:4px; cursor:pointer;">Delete</button>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (err) {
            console.error('Error loading users:', err);
            list.innerHTML = `<div style="padding:12px; color:#b22222;">${usersEscapeHtml(err.message || 'Unable to load users')}</div>`;
        }
    }

    async function createManagedUser() {
        const emailEl = document.getElementById('newUserEmail');
        const roleEl = document.getElementById('newUserRole');
        const passwordEl = document.getElementById('newUserPassword');
        if (!emailEl || !roleEl || !passwordEl) return;

        const email = String(emailEl.value || '').trim().toLowerCase();
        const role = String(roleEl.value || 'user').trim().toLowerCase();
        const password = String(passwordEl.value || '');

        if (!email || !password) {
            setUsersStatus('Email and password are required.', '#b22222');
            return;
        }

        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, role, password }),
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to create user');
            }

            emailEl.value = '';
            roleEl.value = 'user';
            passwordEl.value = '';
            setUsersStatus('User created.', '#2e7d32');
            await loadUsersList();
        } catch (err) {
            setUsersStatus(err.message || 'Unable to create user', '#b22222');
        }
    }

    async function updateManagedUser(userId, currentEmail, currentRole) {
        const email = window.prompt('New email (leave blank to keep current):', currentEmail || '');
        const role = window.prompt('New role (user/admin/manager/estimator/tech):', currentRole || 'user');
        const password = window.prompt('Optional new password (blank to keep):', '');

        const body = {};
        if (email && String(email).trim()) body.email = String(email).trim().toLowerCase();
        if (role && String(role).trim()) body.role = String(role).trim().toLowerCase();
        if (password && String(password).trim()) body.password = String(password);

        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'PATCH',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || 'Unable to update user');
            }

            setUsersStatus('User updated.', '#2e7d32');
            await loadUsersList();
        } catch (err) {
            setUsersStatus(err.message || 'Unable to update user', '#b22222');
        }
    }

    async function deleteManagedUser(userId, email) {
        const confirmed = window.confirm(`Delete user ${email}?`);
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
            setUsersStatus(err.message || 'Unable to delete user', '#b22222');
        }
    }
    </script>
    """

"""Tech's screen content for the FlagTech UI."""


def get_techs_screen_html():
    """Return the HTML content for the Tech's screen."""
    return """
    <div id="tech" class="screen" style="padding:20px;">

        <h1 style="text-align:center; margin-bottom:20px;">TECHS</h1>

        <div style="display:flex; justify-content:center; gap:12px; margin-bottom:30px;">
            <button onclick="openManageTechsModal()"
                    style="padding:12px 24px; font-size:16px; cursor:pointer; background-color:#b22222; color:white; border:none; border-radius:4px; font-weight:bold;">
                Manage Techs
            </button>
        </div>

        <div style="margin-top:40px;">
            <h2 style="margin-bottom:20px;">Technicians</h2>
            <div id="techsTableContainer" style="width:100%; border:1px solid #ddd; border-radius:4px; overflow:visible;">
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:2px solid #ddd; font-weight:bold; position:sticky; top:0; z-index:5;">
                    <div style="flex:0.6; text-align:left;">Status</div>
                    <div style="flex:1.4; text-align:left;">Tech Name</div>
                    <div style="flex:0.9; text-align:center;">Role</div>
                    <div style="flex:0.8; text-align:center;">Total RO's</div>
                    <div style="flex:0.9; text-align:center;">Pay Rate</div>
                    <div style="flex:0.8; text-align:center;">Action</div>
                </div>
                <div id="techsListContainer"></div>
            </div>
        </div>

        <div id="statusDropdownMenu" style="display:none; position:fixed; z-index:3000; background:#fff; border:1px solid #ddd; border-radius:6px; box-shadow:0 4px 10px rgba(0,0,0,0.15); padding:6px;"></div>

        <div id="manageTechsModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:980px; max-height:85vh; overflow-y:auto; background:#f2f2f2;">
                <span class="close" onclick="closeManageTechsModal()">&times;</span>
                <h3 style="margin-bottom:14px;">Manage Techs</h3>

                <div style="border:1px solid #ddd; border-radius:6px; padding:12px; background:#fff; margin-bottom:14px;">
                    <div style="font-weight:bold; margin-bottom:10px;">Add New Tech</div>
                    <div style="display:grid; grid-template-columns:1.7fr 1fr 1fr auto; gap:8px; align-items:end;">
                        <div>
                            <label for="manageNewTechName" style="display:block; margin-bottom:4px;">Name</label>
                            <input id="manageNewTechName" type="text" placeholder="First Last" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
                        </div>
                        <div>
                            <label for="manageNewTechRole" style="display:block; margin-bottom:4px;">Role</label>
                            <select id="manageNewTechRole" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                                <option value="Body">Body</option>
                                <option value="Frame">Frame</option>
                                <option value="Mech">Mech</option>
                                <option value="Paint">Paint</option>
                            </select>
                        </div>
                        <div>
                            <label for="manageNewTechRate" style="display:block; margin-bottom:4px;">Pay Rate</label>
                            <input id="manageNewTechRate" type="number" step="0.01" min="0" placeholder="0.00" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; text-align:right;" />
                        </div>
                        <button onclick="queueManageTechAdd()" style="padding:10px 14px; background:#b22222; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">ADD</button>
                    </div>
                    <div id="managePendingAdds" style="margin-top:10px;"></div>
                </div>

                <div style="border:1px solid #ddd; border-radius:6px; background:#fff; overflow:hidden;">
                    <div style="display:flex; padding:10px; background:#f7f7f7; border-bottom:1px solid #ddd; font-weight:bold;">
                        <div style="flex:1.7;">Name</div>
                        <div style="flex:1; text-align:center;">Role</div>
                        <div style="flex:1; text-align:center;">Pay Rate</div>
                        <div style="width:110px; text-align:center;">Archive</div>
                    </div>
                    <div id="manageTechsList"></div>
                </div>

                <div style="display:flex; justify-content:flex-end; margin-top:14px;">
                    <button onclick="saveAllManageTechChanges()" style="padding:10px 18px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Save All Changes</button>
                </div>
            </div>
        </div>

        <style>
            .tech-row {
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:12px;
                border-bottom:1px solid #eee;
                background:#fff;
            }
            .tech-row:hover {
                background:#f7f7f7;
            }
            .tech-link {
                background:none;
                border:none;
                color:#0066cc;
                text-decoration:underline;
                cursor:pointer;
                padding:0;
                font:inherit;
                font-weight:bold;
            }
            .tech-inline-edit {
                cursor:pointer;
                border-radius:4px;
                padding:4px 6px;
                display:inline-block;
                min-width:72px;
            }
            .tech-inline-edit:hover {
                background:#f1f1f1;
            }
            .tech-slide-down {
                padding:12px 16px;
                border-bottom:1px solid #eee;
                background:#fff;
                overflow:visible;
            }
            .tech-slide-panel {
                border:1px solid #ddd;
                border-radius:6px;
                background:#fafafa;
                padding:10px;
            }
            .tech-slide-header {
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:10px;
                margin-bottom:10px;
                flex-wrap:wrap;
            }
            .tech-slide-title {
                font-weight:bold;
                color:#333;
            }
            .tech-ro-table {
                width:100%;
                border-collapse:collapse;
                background:#fff;
            }
            .tech-ro-table th,
            .tech-ro-table td {
                padding:9px 10px;
                border-bottom:1px solid #e6e6e6;
                vertical-align:top;
            }
            .tech-ro-table thead tr {
                background:#efefef;
            }
            .nested-ro-lines {
                background:#fcfcfc;
                border:1px solid #e5e5e5;
                border-radius:6px;
                padding:10px;
            }
            .nested-line-row {
                display:flex;
                align-items:center;
                gap:10px;
                padding:8px 6px;
                border-bottom:1px solid #eee;
            }
            .nested-line-row:last-child {
                border-bottom:none;
            }
            .manage-tech-row {
                display:flex;
                padding:10px;
                border-bottom:1px solid #eee;
                align-items:center;
                gap:8px;
            }
        </style>

        <script>
        let techPayRateById = {};
        let cachedTechRows = [];
        let currentStatusDropdownTechId = null;
        let openTechPanel = { techId: null, mode: null };
        let openNestedRoByTech = {};
        let selectedRosByTech = {};
        let manageQueuedAdds = [];

        function escapeHtml(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function formatCurrency(value) {
            const numeric = Number(value || 0);
            return `$${numeric.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }

        function splitNameParts(fullNameRaw) {
            const fullName = (fullNameRaw || '').trim().replace(/\s+/g, ' ');
            if (!fullName) return null;
            const parts = fullName.split(' ');
            if (parts.length < 2) return null;
            const first_name = parts.shift();
            const last_name = parts.join(' ');
            return { first_name, last_name };
        }

        function getStatusIcon(statusValue) {
            const status = (statusValue || '').trim();
            if (status === 'Active') return '<span title="Active" style="color:#2e7d32; font-weight:bold;">✅</span>';
            if (status === 'FMLA') return '<span title="FMLA">👪</span>';
            if (status === 'Vacation') return '<span title="Vacation">🌴</span>';
            return '<span>-</span>';
        }

        function closeStatusDropdown() {
            const menu = document.getElementById('statusDropdownMenu');
            if (!menu) return;
            menu.style.display = 'none';
            currentStatusDropdownTechId = null;
        }

        function openStatusDropdown(event, techId, currentStatus) {
            const menu = document.getElementById('statusDropdownMenu');
            if (!menu) return;
            event.stopPropagation();

            currentStatusDropdownTechId = techId;
            menu.innerHTML = `
                <select id="statusDropdownSelect" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; min-width:120px;">
                    <option value="Active" ${currentStatus === 'Active' ? 'selected' : ''}>Active</option>
                    <option value="Vacation" ${currentStatus === 'Vacation' ? 'selected' : ''}>Vacation</option>
                    <option value="FMLA" ${currentStatus === 'FMLA' ? 'selected' : ''}>FMLA</option>
                </select>
            `;

            menu.style.left = `${event.clientX || 0}px`;
            menu.style.top = `${(event.clientY || 0) + 6}px`;
            menu.style.display = 'block';

            const select = document.getElementById('statusDropdownSelect');
            if (!select) return;
            select.focus();
            select.addEventListener('change', function() {
                if (!currentStatusDropdownTechId) return;
                updateTechStatus(currentStatusDropdownTechId, select.value);
                closeStatusDropdown();
            });
            select.addEventListener('blur', function() {
                setTimeout(() => closeStatusDropdown(), 120);
            });
        }

        function updateTechStatus(techId, statusValue) {
            fetch('/api/techs/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id: techId, status: statusValue })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) throw new Error(res.error);
                loadTechsList();
            })
            .catch(err => {
                console.error('Error updating technician status:', err);
                alert('Error updating technician status.');
            });
        }

        function beginInlineRoleEdit(techId) {
            const cell = document.querySelector(`.role-cell[data-tech-id="${techId}"]`);
            if (!cell) return;
            const current = (cell.getAttribute('data-current-role') || 'Body').trim();
            const fallback = ['Body', 'Frame', 'Mech', 'Paint'].includes(current) ? current : 'Body';
            cell.innerHTML = `
                <select class="inline-role-input" style="padding:6px 8px; border:1px solid #ccc; border-radius:4px; width:110px;">
                    <option value="Body" ${fallback === 'Body' ? 'selected' : ''}>Body</option>
                    <option value="Frame" ${fallback === 'Frame' ? 'selected' : ''}>Frame</option>
                    <option value="Mech" ${fallback === 'Mech' ? 'selected' : ''}>Mech</option>
                    <option value="Paint" ${fallback === 'Paint' ? 'selected' : ''}>Paint</option>
                </select>
            `;
            const select = cell.querySelector('.inline-role-input');
            if (!select) return;
            select.focus();

            const restore = () => {
                cell.innerHTML = `<span class="tech-inline-edit">${escapeHtml(fallback)}</span>`;
                cell.setAttribute('data-current-role', fallback);
            };

            select.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    event.preventDefault();
                    restore();
                }
                if (event.key === 'Enter') {
                    event.preventDefault();
                    const role = (select.value || '').trim();
                    saveInlineTechUpdate(techId, { role })
                        .then(() => loadTechsList())
                        .catch(() => restore());
                }
            });

            select.addEventListener('blur', () => {
                restore();
            });
        }

        function beginInlineRateEdit(techId) {
            const cell = document.querySelector(`.rate-cell[data-tech-id="${techId}"]`);
            if (!cell) return;
            const currentRate = Number(cell.getAttribute('data-current-rate') || '0');
            cell.innerHTML = `<input class="inline-rate-input" type="number" step="0.01" min="0" value="${currentRate.toFixed(2)}" style="width:100px; padding:6px 8px; border:1px solid #ccc; border-radius:4px; text-align:right;" />`;

            const input = cell.querySelector('.inline-rate-input');
            if (!input) return;
            input.focus();
            input.select();

            const restore = () => {
                cell.innerHTML = `<span class="tech-inline-edit">${formatCurrency(currentRate)}/hr</span>`;
                cell.setAttribute('data-current-rate', String(currentRate));
            };

            input.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    event.preventDefault();
                    restore();
                }
                if (event.key === 'Enter') {
                    event.preventDefault();
                    const pay_rate = parseFloat(input.value || '0');
                    if (!Number.isFinite(pay_rate) || pay_rate <= 0) {
                        alert('Pay rate must be greater than zero.');
                        restore();
                        return;
                    }
                    saveInlineTechUpdate(techId, { pay_rate })
                        .then(() => loadTechsList())
                        .catch(() => restore());
                }
            });

            input.addEventListener('blur', () => {
                restore();
            });
        }

        function saveInlineTechUpdate(techId, payload) {
            return fetch('/api/techs/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id: techId, ...payload })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) throw new Error(res.error);
                return res;
            })
            .catch(err => {
                console.error('Error saving inline tech update:', err);
                alert('Unable to save technician update.');
                throw err;
            });
        }

        function loadTechsList() {
            const tableContainer = document.getElementById('techsListContainer');
            if (!tableContainer) return;
            tableContainer.innerHTML = "<p style='color:#777; text-align:center; padding:12px;'>Loading...</p>";

            fetch('/api/techs/list', { credentials: 'include' })
                .then(r => r.json())
                .then(techsRes => {
                    cachedTechRows = Array.isArray(techsRes.techs) ? techsRes.techs : [];
                    tableContainer.innerHTML = '';

                    if (!cachedTechRows.length) {
                        tableContainer.innerHTML = "<p style='color:#777; text-align:center; padding:12px;'>No techs added yet.</p>";
                        return;
                    }

                    cachedTechRows.forEach(tech => {
                        const techId = Number(tech.id);
                        const fullName = `${(tech.first_name || '').trim()} ${(tech.last_name || '').trim()}`.trim();
                        const role = (tech.role || '').trim() || 'Body';
                        const payRate = Number(tech.pay_rate || 0);
                        techPayRateById[String(techId)] = payRate;

                        const row = document.createElement('div');
                        row.className = 'tech-row';

                        const statusCell = document.createElement('div');
                        statusCell.style.flex = '0.6';
                        statusCell.style.textAlign = 'left';
                        statusCell.style.cursor = 'pointer';
                        statusCell.innerHTML = getStatusIcon(tech.status || 'Active');
                        statusCell.title = 'Update status';
                        statusCell.onclick = function(e) {
                            openStatusDropdown(e, techId, tech.status || 'Active');
                        };

                        const nameCell = document.createElement('div');
                        nameCell.style.flex = '1.4';
                        nameCell.style.textAlign = 'left';
                        nameCell.innerHTML = `<button type="button" class="tech-link" data-tech-id="${techId}" data-mode="list">${escapeHtml(fullName || 'Unnamed')}</button>`;

                        const roleCell = document.createElement('div');
                        roleCell.style.flex = '0.9';
                        roleCell.style.textAlign = 'center';
                        roleCell.className = 'role-cell';
                        roleCell.setAttribute('data-tech-id', String(techId));
                        roleCell.setAttribute('data-current-role', role);
                        roleCell.innerHTML = `<span class="tech-inline-edit">${escapeHtml(role)}</span>`;
                        roleCell.addEventListener('click', (event) => {
                            event.stopPropagation();
                            beginInlineRoleEdit(techId);
                        });

                        const totalRosCell = document.createElement('div');
                        totalRosCell.style.flex = '0.8';
                        totalRosCell.style.textAlign = 'center';
                        totalRosCell.style.fontWeight = 'bold';
                        totalRosCell.innerHTML = `<button type="button" class="tech-link" data-tech-id="${techId}" data-mode="flagout">${Number(tech.total_ros || 0)}</button>`;

                        const rateCell = document.createElement('div');
                        rateCell.style.flex = '0.9';
                        rateCell.style.textAlign = 'center';
                        rateCell.className = 'rate-cell';
                        rateCell.setAttribute('data-tech-id', String(techId));
                        rateCell.setAttribute('data-current-rate', String(payRate));
                        rateCell.innerHTML = `<span class="tech-inline-edit">${formatCurrency(payRate)}/hr</span>`;
                        rateCell.addEventListener('click', (event) => {
                            event.stopPropagation();
                            beginInlineRateEdit(techId);
                        });

                        const actionCell = document.createElement('div');
                        actionCell.style.flex = '0.8';
                        actionCell.style.textAlign = 'center';
                        actionCell.textContent = '-';

                        row.appendChild(statusCell);
                        row.appendChild(nameCell);
                        row.appendChild(roleCell);
                        row.appendChild(totalRosCell);
                        row.appendChild(rateCell);
                        row.appendChild(actionCell);

                        const slideDown = document.createElement('div');
                        slideDown.id = `tech-slide-${techId}`;
                        slideDown.className = 'tech-slide-down';
                        slideDown.style.display = 'none';

                        tableContainer.appendChild(row);
                        tableContainer.appendChild(slideDown);
                    });

                    bindTechLinks();
                })
                .catch(err => {
                    console.error('Error loading techs:', err);
                    tableContainer.innerHTML = "<p style='color:red; text-align:center; padding:12px;'>Error loading techs.</p>";
                });
        }

        function bindTechLinks() {
            document.querySelectorAll('.tech-link').forEach(button => {
                button.addEventListener('click', (event) => {
                    event.stopPropagation();
                    const techId = parseInt(button.getAttribute('data-tech-id') || '0', 10);
                    const mode = (button.getAttribute('data-mode') || 'list').trim();
                    const tech = cachedTechRows.find(item => Number(item.id) === techId);
                    if (!tech) return;
                    openTechSlideDown(tech, mode);
                });
            });
        }

        function closeOpenTechSlideDownIfDifferent(techId) {
            if (!openTechPanel.techId || openTechPanel.techId === techId) return;
            const openContainer = document.getElementById(`tech-slide-${openTechPanel.techId}`);
            if (openContainer) {
                openContainer.style.display = 'none';
                openContainer.innerHTML = '';
            }
            openTechPanel = { techId: null, mode: null };
        }

        function openTechSlideDown(tech, mode) {
            const techId = Number(tech.id);
            const container = document.getElementById(`tech-slide-${techId}`);
            if (!container) return;

            const sameOpen = openTechPanel.techId === techId && container.style.display === 'block';
            const sameMode = openTechPanel.mode === mode;

            if (sameOpen && sameMode) {
                container.style.display = 'none';
                container.innerHTML = '';
                openTechPanel = { techId: null, mode: null };
                return;
            }

            closeOpenTechSlideDownIfDifferent(techId);
            openTechPanel = { techId, mode };
            container.style.display = 'block';
            renderTechSlideDown(tech, mode, container);
        }

        function renderTechSlideDown(tech, mode, container) {
            const techId = Number(tech.id);
            const techName = `${(tech.first_name || '').trim()} ${(tech.last_name || '').trim()}`.trim();
            const payRate = Number(tech.pay_rate || 0);

            if (!selectedRosByTech[String(techId)]) {
                selectedRosByTech[String(techId)] = [];
            }

            const title = mode === 'flagout' ? `Flagout Queue — ${techName}` : `Assigned ROs — ${techName}`;
            const controls = mode === 'flagout'
                ? `
                    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                        <label style="display:flex; gap:6px; align-items:center; font-weight:bold;">
                            <input id="select-all-ros-${techId}" type="checkbox" onchange="toggleSelectAllRosForTech(${techId}, this.checked)" />
                            Select all ROs for this tech
                        </label>
                        <button onclick="sendSelectedRosToFlagout(${techId})" style="padding:8px 12px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Send selected to Flagout</button>
                    </div>
                `
                : '<div style="font-size:12px; color:#666;">Click an RO to open assigned repair lines.</div>';

            container.innerHTML = `
                <div class="tech-slide-panel">
                    <div class="tech-slide-header">
                        <div class="tech-slide-title">${escapeHtml(title)}</div>
                        ${controls}
                    </div>
                    <div id="tech-ro-list-${techId}"><div style="color:#777;">Loading assignments...</div></div>
                </div>
            `;

            loadTechAssignmentsForTech(techId, techName, payRate, mode);
        }

        function loadTechAssignmentsForTech(techId, techName, techRate, mode) {
            const listContainer = document.getElementById(`tech-ro-list-${techId}`);
            if (!listContainer) return;

            fetch(`/api/tech-assignments?tech_id=${encodeURIComponent(techId)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) throw new Error(res.error);
                    const assignments = Array.isArray(res.assignments) ? res.assignments : [];
                    const selectedRos = selectedRosByTech[String(techId)] || [];

                    if (!assignments.length) {
                        listContainer.innerHTML = '<div style="color:#999; padding:8px 0;">No assignments yet.</div>';
                        return;
                    }

                    const rows = assignments.map(item => {
                        const ro = String(item.ro || '').trim();
                        const roEscaped = escapeHtml(ro);
                        const vehicle = escapeHtml(item.vehicle || '—');
                        const totalHours = Number(item.total_hours || 0).toFixed(1);
                        const status = escapeHtml(item.status || 'Assigned');
                        const checked = selectedRos.includes(ro) ? 'checked' : '';
                        const nestedRowId = `nested-lines-${techId}-${ro.replace(/[^a-zA-Z0-9_-]/g, '_')}`;
                        return `
                            <tr class="tech-ro-entry" data-tech-id="${techId}" data-ro="${roEscaped}">
                                <td style="width:46px; text-align:center;"><input type="checkbox" class="tech-ro-checkbox" data-tech-id="${techId}" data-ro="${roEscaped}" ${checked} /></td>
                                <td><button type="button" class="tech-link ro-link" data-tech-id="${techId}" data-ro="${roEscaped}" data-tech-name="${escapeHtml(techName)}" data-tech-rate="${Number(techRate || 0).toFixed(2)}">RO# ${roEscaped}</button></td>
                                <td>${vehicle}</td>
                                <td style="text-align:right; font-weight:bold;">${totalHours}</td>
                                <td>${status}</td>
                            </tr>
                            <tr id="${nestedRowId}" style="display:none;">
                                <td colspan="5" style="padding:10px 6px;"></td>
                            </tr>
                        `;
                    }).join('');

                    listContainer.innerHTML = `
                        <table class="tech-ro-table">
                            <thead>
                                <tr>
                                    <th style="width:46px; text-align:center;">Sel</th>
                                    <th>RO#</th>
                                    <th>Vehicle</th>
                                    <th style="text-align:right;">Hours</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    `;

                    bindRosAndNestedLines(techId, mode);
                    syncSelectAllCheckbox(techId);
                })
                .catch(err => {
                    console.error('Error loading assignments:', err);
                    listContainer.innerHTML = '<div style="color:red; padding:8px 0;">Error loading assignments.</div>';
                });
        }

        function bindRosAndNestedLines(techId, mode) {
            const checkboxes = document.querySelectorAll(`.tech-ro-checkbox[data-tech-id="${techId}"]`);
            checkboxes.forEach(chk => {
                chk.addEventListener('change', () => {
                    const ro = (chk.getAttribute('data-ro') || '').trim();
                    updateTechRoSelection(techId, ro, chk.checked);
                    if (mode === 'flagout') {
                        syncSelectAllCheckbox(techId);
                    }
                });
            });

            document.querySelectorAll(`.ro-link[data-tech-id="${techId}"]`).forEach(button => {
                button.addEventListener('click', (event) => {
                    event.stopPropagation();
                    const ro = (button.getAttribute('data-ro') || '').trim();
                    const techName = button.getAttribute('data-tech-name') || '';
                    const techRate = parseFloat(button.getAttribute('data-tech-rate') || '0') || 0;
                    toggleNestedRoLines(techId, ro, techName, techRate);
                });
            });
        }

        function updateTechRoSelection(techId, ro, isSelected) {
            const key = String(techId);
            const current = Array.isArray(selectedRosByTech[key]) ? selectedRosByTech[key] : [];
            if (isSelected) {
                if (!current.includes(ro)) current.push(ro);
            } else {
                const idx = current.indexOf(ro);
                if (idx >= 0) current.splice(idx, 1);
            }
            selectedRosByTech[key] = current;
        }

        function syncSelectAllCheckbox(techId) {
            const selectAll = document.getElementById(`select-all-ros-${techId}`);
            if (!selectAll) return;
            const checks = Array.from(document.querySelectorAll(`.tech-ro-checkbox[data-tech-id="${techId}"]`));
            if (!checks.length) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
                return;
            }
            const checkedCount = checks.filter(item => item.checked).length;
            selectAll.checked = checkedCount === checks.length;
            selectAll.indeterminate = checkedCount > 0 && checkedCount < checks.length;
        }

        function toggleSelectAllRosForTech(techId, checked) {
            const checks = Array.from(document.querySelectorAll(`.tech-ro-checkbox[data-tech-id="${techId}"]`));
            checks.forEach(chk => {
                chk.checked = checked;
                const ro = (chk.getAttribute('data-ro') || '').trim();
                updateTechRoSelection(techId, ro, checked);
            });
            syncSelectAllCheckbox(techId);
        }

        function sendSelectedRosToFlagout(techId) {
            const selectedRos = (selectedRosByTech[String(techId)] || []).slice();
            if (!selectedRos.length) {
                alert('Select at least one RO for Flagout.');
                return;
            }
            const payRate = Number(techPayRateById[String(techId)] || 0);
            fetch('/api/tech-flag-out-ros', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    tech_id: techId,
                    ros: selectedRos,
                    pay_rate: payRate
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) throw new Error(res.error);
                selectedRosByTech[String(techId)] = [];
                loadTechsList();
            })
            .catch(err => {
                console.error('Error sending selected ROs to flagout:', err);
                alert('Error sending selected ROs to Flagout.');
            });
        }

        function toggleNestedRoLines(techId, ro, techName, techRate) {
            const safeRo = ro.replace(/[^a-zA-Z0-9_-]/g, '_');
            const nestedRow = document.getElementById(`nested-lines-${techId}-${safeRo}`);
            if (!nestedRow) return;

            const currentlyOpenRo = openNestedRoByTech[String(techId)] || null;
            if (currentlyOpenRo && currentlyOpenRo !== ro) {
                const priorSafe = currentlyOpenRo.replace(/[^a-zA-Z0-9_-]/g, '_');
                const priorRow = document.getElementById(`nested-lines-${techId}-${priorSafe}`);
                if (priorRow) {
                    priorRow.style.display = 'none';
                    priorRow.querySelector('td').innerHTML = '';
                }
            }

            const isOpen = nestedRow.style.display === 'table-row';
            if (isOpen) {
                nestedRow.style.display = 'none';
                nestedRow.querySelector('td').innerHTML = '';
                openNestedRoByTech[String(techId)] = null;
                return;
            }

            openNestedRoByTech[String(techId)] = ro;
            nestedRow.style.display = 'table-row';
            nestedRow.querySelector('td').innerHTML = '<div class="nested-ro-lines" style="color:#777;">Loading repair lines...</div>';

            fetch(`/api/tech-assignment-lines?ro=${encodeURIComponent(ro)}&tech_id=${encodeURIComponent(techId)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) throw new Error(res.error);
                    const lines = Array.isArray(res.lines) ? res.lines : [];
                    if (!lines.length) {
                        nestedRow.querySelector('td').innerHTML = '<div class="nested-ro-lines" style="color:#777;">No assigned repair lines.</div>';
                        return;
                    }

                    const lineRows = lines.map((line, idx) => {
                        const lineKey = escapeHtml(line.line_key || String(idx + 1));
                        const lineNum = escapeHtml(line.line || '—');
                        const desc = escapeHtml(line.description || '');
                        const repairType = escapeHtml(line.repair_type || '');
                        const hours = Number(line.value || 0).toFixed(1);
                        return `
                            <div class="nested-line-row">
                                <input type="checkbox" class="nested-line-checkbox" data-line-key="${lineKey}" data-hours="${hours}" checked />
                                <div style="flex:1;"><strong>Line ${lineNum}</strong> <span style="font-size:12px; color:#666;">[${repairType}]</span> - ${desc}</div>
                                <div style="min-width:72px; text-align:right; font-weight:bold;">${hours} hrs</div>
                            </div>
                        `;
                    }).join('');

                    nestedRow.querySelector('td').innerHTML = `
                        <div class="nested-ro-lines">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; gap:8px; flex-wrap:wrap;">
                                <div style="font-weight:bold;">RO# ${escapeHtml(ro)} — ${escapeHtml(techName)}</div>
                                <button type="button" class="flag-lines-btn" data-tech-id="${techId}" data-ro="${escapeHtml(ro)}" data-rate="${Number(techRate || 0).toFixed(2)}" style="padding:8px 12px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Flag selected lines</button>
                            </div>
                            <div>${lineRows}</div>
                            <div class="nested-lines-summary" style="margin-top:10px; font-size:13px; color:#555;"></div>
                        </div>
                    `;

                    attachNestedLineHandlers(nestedRow);
                })
                .catch(err => {
                    console.error('Error loading assigned repair lines:', err);
                    nestedRow.querySelector('td').innerHTML = '<div class="nested-ro-lines" style="color:red;">Error loading repair lines.</div>';
                });
        }

        function attachNestedLineHandlers(nestedRow) {
            const summary = nestedRow.querySelector('.nested-lines-summary');
            const checkboxes = Array.from(nestedRow.querySelectorAll('.nested-line-checkbox'));
            const flagBtn = nestedRow.querySelector('.flag-lines-btn');

            const recalc = () => {
                if (!summary) return;
                const selected = checkboxes.filter(chk => chk.checked);
                const totalHours = selected.reduce((sum, chk) => sum + (parseFloat(chk.getAttribute('data-hours') || '0') || 0), 0);
                summary.innerHTML = `<strong>Selected Lines:</strong> ${selected.length} <span style="margin-left:14px;"><strong>Total HRS:</strong> ${totalHours.toFixed(1)}</span>`;
            };

            checkboxes.forEach(chk => chk.addEventListener('change', recalc));
            recalc();

            if (!flagBtn) return;
            flagBtn.addEventListener('click', () => {
                const ro = (flagBtn.getAttribute('data-ro') || '').trim();
                const techId = parseInt(flagBtn.getAttribute('data-tech-id') || '0', 10);
                const payRate = parseFloat(flagBtn.getAttribute('data-rate') || '0') || 0;
                const selectedKeys = checkboxes.filter(chk => chk.checked).map(chk => chk.getAttribute('data-line-key')).filter(Boolean);
                if (!selectedKeys.length) {
                    alert('Select at least one line to flag.');
                    return;
                }

                fetch('/api/tech-flag-out', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        ro,
                        tech_id: techId,
                        line_keys: selectedKeys,
                        pay_rate: payRate
                    })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.error) throw new Error(res.error);
                    loadTechsList();
                })
                .catch(err => {
                    console.error('Error flagging selected lines:', err);
                    alert('Error flagging selected lines.');
                });
            });
        }

        function openManageTechsModal() {
            const modal = document.getElementById('manageTechsModal');
            if (!modal) return;
            manageQueuedAdds = [];
            renderManageQueuedAdds();
            renderManageTechsList();
            modal.style.display = 'block';
        }

        function closeManageTechsModal() {
            const modal = document.getElementById('manageTechsModal');
            if (!modal) return;
            modal.style.display = 'none';
        }

        function renderManageQueuedAdds() {
            const container = document.getElementById('managePendingAdds');
            if (!container) return;
            if (!manageQueuedAdds.length) {
                container.innerHTML = '<div style="font-size:12px; color:#777;">No queued additions.</div>';
                return;
            }
            container.innerHTML = manageQueuedAdds.map((item, idx) => `
                <div style="display:flex; justify-content:space-between; align-items:center; border:1px solid #eee; border-radius:4px; padding:6px 8px; margin-top:6px; background:#fafafa;">
                    <div>${escapeHtml(item.name)} — ${escapeHtml(item.role)} — ${formatCurrency(item.pay_rate)}/hr</div>
                    <button type="button" onclick="removeQueuedTechAdd(${idx})" style="background:none; border:none; color:#b22222; cursor:pointer; font-weight:bold;">Remove</button>
                </div>
            `).join('');
        }

        function queueManageTechAdd() {
            const nameInput = document.getElementById('manageNewTechName');
            const roleInput = document.getElementById('manageNewTechRole');
            const rateInput = document.getElementById('manageNewTechRate');
            if (!nameInput || !roleInput || !rateInput) return;

            const name = (nameInput.value || '').trim();
            const role = (roleInput.value || '').trim();
            const pay_rate = parseFloat(rateInput.value || '0');
            if (!name || !role || !Number.isFinite(pay_rate) || pay_rate <= 0) {
                alert('Enter a valid name, role, and pay rate.');
                return;
            }

            if (!splitNameParts(name)) {
                alert('Name must include first and last name.');
                return;
            }

            manageQueuedAdds.push({ name, role, pay_rate });
            nameInput.value = '';
            rateInput.value = '';
            roleInput.value = 'Body';
            renderManageQueuedAdds();
        }

        function removeQueuedTechAdd(index) {
            manageQueuedAdds = manageQueuedAdds.filter((_, idx) => idx !== index);
            renderManageQueuedAdds();
        }

        function renderManageTechsList() {
            const container = document.getElementById('manageTechsList');
            if (!container) return;
            if (!cachedTechRows.length) {
                container.innerHTML = '<div style="padding:12px; color:#777;">No techs available.</div>';
                return;
            }

            container.innerHTML = cachedTechRows.map(tech => {
                const techId = Number(tech.id);
                const fullName = `${(tech.first_name || '').trim()} ${(tech.last_name || '').trim()}`.trim();
                const role = (tech.role || '').trim() || 'Body';
                const payRate = Number(tech.pay_rate || 0).toFixed(2);
                return `
                    <div class="manage-tech-row" data-tech-id="${techId}" data-original-name="${escapeHtml(fullName)}" data-original-role="${escapeHtml(role)}" data-original-rate="${payRate}">
                        <div style="flex:1.7;"><input class="manage-name" type="text" value="${escapeHtml(fullName)}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" /></div>
                        <div style="flex:1; text-align:center;">
                            <select class="manage-role" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                                <option value="Body" ${role === 'Body' ? 'selected' : ''}>Body</option>
                                <option value="Frame" ${role === 'Frame' ? 'selected' : ''}>Frame</option>
                                <option value="Mech" ${role === 'Mech' ? 'selected' : ''}>Mech</option>
                                <option value="Paint" ${role === 'Paint' ? 'selected' : ''}>Paint</option>
                            </select>
                        </div>
                        <div style="flex:1; text-align:center;"><input class="manage-rate" type="number" min="0" step="0.01" value="${payRate}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; text-align:right;" /></div>
                        <div style="width:110px; text-align:center;"><label style="display:inline-flex; gap:6px; align-items:center;"><input class="manage-archive" type="checkbox" /> Archive</label></div>
                    </div>
                `;
            }).join('');
        }

        async function saveAllManageTechChanges() {
            try {
                for (const pending of manageQueuedAdds) {
                    const nameParts = splitNameParts(pending.name);
                    if (!nameParts) {
                        throw new Error(`Invalid queued name: ${pending.name}`);
                    }
                    const addRes = await fetch('/api/techs/add', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({
                            first_name: nameParts.first_name,
                            last_name: nameParts.last_name,
                            role: pending.role,
                            pay_rate: pending.pay_rate
                        })
                    });
                    const addData = await addRes.json();
                    if (addData.error) {
                        throw new Error(addData.error);
                    }
                }

                const rows = Array.from(document.querySelectorAll('.manage-tech-row'));
                const archiveIds = [];

                for (const row of rows) {
                    const techId = parseInt(row.getAttribute('data-tech-id') || '0', 10);
                    if (!Number.isFinite(techId) || techId <= 0) continue;

                    const archiveChecked = !!row.querySelector('.manage-archive')?.checked;
                    if (archiveChecked) {
                        archiveIds.push(techId);
                        continue;
                    }

                    const currentName = (row.querySelector('.manage-name')?.value || '').trim().replace(/\s+/g, ' ');
                    const currentRole = (row.querySelector('.manage-role')?.value || '').trim();
                    const currentRate = parseFloat(row.querySelector('.manage-rate')?.value || '0');

                    const originalName = (row.getAttribute('data-original-name') || '').trim();
                    const originalRole = (row.getAttribute('data-original-role') || '').trim();
                    const originalRate = parseFloat(row.getAttribute('data-original-rate') || '0');

                    if (!currentName) {
                        throw new Error('Name cannot be blank.');
                    }
                    if (!Number.isFinite(currentRate) || currentRate <= 0) {
                        throw new Error('Pay rate must be greater than zero.');
                    }

                    const changed = currentName !== originalName || currentRole !== originalRole || Math.abs(currentRate - originalRate) > 0.0001;
                    if (!changed) continue;

                    const parts = splitNameParts(currentName);
                    if (!parts) {
                        throw new Error(`Name must include first and last name: ${currentName}`);
                    }

                    const updateRes = await fetch('/api/techs/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({
                            id: techId,
                            first_name: parts.first_name,
                            last_name: parts.last_name,
                            role: currentRole,
                            pay_rate: currentRate
                        })
                    });
                    const updateData = await updateRes.json();
                    if (updateData.error) {
                        throw new Error(updateData.error);
                    }
                }

                if (archiveIds.length) {
                    const archiveRes = await fetch('/api/techs/archive', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ ids: archiveIds })
                    });
                    const archiveData = await archiveRes.json();
                    if (archiveData.error) {
                        throw new Error(archiveData.error);
                    }
                }

                closeManageTechsModal();
                loadTechsList();
            } catch (err) {
                console.error('Error saving manage tech changes:', err);
                alert(err?.message || 'Error saving tech changes.');
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            loadTechsList();
            document.addEventListener('click', (event) => {
                const menu = document.getElementById('statusDropdownMenu');
                if (!menu || menu.style.display !== 'block') return;
                if (menu.contains(event.target)) return;
                closeStatusDropdown();
            });
        });
        </script>

    </div>
    """

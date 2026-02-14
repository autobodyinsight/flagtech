"""Tech's screen content for the FlagTech UI."""


def get_techs_screen_html():
    """Return the HTML content for the Tech's screen."""
    return """
    <div id="tech" class="screen" style="padding:20px;">

        <h1 style="text-align:center; margin-bottom:20px;">TECHS</h1>

        <!-- Tech Action Buttons (centered) -->
        <div style="display:flex; justify-content:center; gap:12px; margin-bottom:30px;">
            <button onclick="openAddTechModal()"
                    style="padding:12px 24px; font-size:16px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:4px;">
                + tech
            </button>
            <button onclick="toggleTechEditMode()"
                    id="techEditBtn"
                    style="padding:12px 24px; font-size:16px; cursor:pointer; background-color:#d32f2f; color:#fff; border:none; border-radius:4px; font-weight:bold;">
                EDIT
            </button>
        </div>

        <!-- Techs Details Table -->
        <div style="margin-top:40px;">
            <h2 style="margin-bottom:20px;">Technicians</h2>
            <div id="techsTableContainer" style="width:100%; border:1px solid #ddd; border-radius:4px; overflow:hidden;">
                <!-- Header -->
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:2px solid #ddd; font-weight:bold; position:sticky; top:0;">
                    <div style="flex:1; text-align:left;">Tech Name</div>
                    <div style="flex:1; text-align:center;">Pay Rate</div>
                </div>
                <!-- Tech rows will be inserted here -->
                <div id="techsListContainer"></div>
            </div>
            <div id="techArchiveActions" style="display:none; margin-top:14px;">
                <button id="archiveTechBtn" onclick="archiveSelectedTechs()" style="padding:10px 20px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:14px; font-weight:bold;" disabled>
                    ARCHIVE
                </button>
            </div>
        </div>

        <div style="margin-top:28px;">
            <h2 style="margin-bottom:12px;">Archived Techs</h2>
            <div id="archivedTechsContainer" style="width:100%; border:1px solid #ddd; border-radius:4px; background:#fff; padding:12px;"></div>
        </div>

        <!-- Add Tech Modal -->
        <div id="addTechModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:400px; background-color:#f2f2f2;">
                <span class="close" onclick="closeAddTechModal()">&times;</span>
                <h3>Add Technician</h3>

                <label>First:</label>
                <input type="text" id="techFirstName" style="width:100%; padding:8px; margin-bottom:15px; box-sizing:border-box;">

                <label>Last:</label>
                <input type="text" id="techLastName" style="width:100%; padding:8px; margin-bottom:15px; box-sizing:border-box;">

                <label>Rate:</label>
                <input type="number" step="0.01" id="techRate" style="width:100%; padding:8px; margin-bottom:20px; box-sizing:border-box;">

                <div style="text-align:center;">
                    <button onclick="saveTech()"
                            style="padding:10px 20px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">
                        Save
                    </button>
                </div>
            </div>
        </div>

        <div id="techAssignmentModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; max-height:80vh; overflow-y:auto;">
                <span class="close" onclick="closeTechAssignmentModal()">&times;</span>
                <h3 id="techAssignmentTitle" style="margin-bottom:12px;">Assigned Repairs</h3>
                <div id="techAssignmentBody"></div>
                <div style="text-align:right; margin-top:12px;">
                    <button onclick="printTechAssignment()" style="padding:8px 16px; background:#505050; color:#fff; border:none; border-radius:4px; cursor:pointer;">Print</button>
                    <button onclick="flagOutSelectedLines()" style="padding:8px 16px; background:#d32f2f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold; margin-left:8px;">Flag Out</button>
                </div>
            </div>
        </div>

        <style>
            .tech-row.clickable {
                cursor: pointer;
            }
            .tech-assignments {
                padding: 12px 16px;
                border-bottom: 1px solid #eee;
                background: #fff;
            }
            .tech-assignments-panel {
                background:#fafafa;
                border:1px solid #ddd;
                border-radius:6px;
                padding:12px;
            }
            .tech-assignments-title {
                font-weight:bold;
                color:#333;
                margin-bottom:10px;
            }
            .tech-assignments-table {
                width:100%;
                border-collapse:collapse;
                margin-top:8px;
            }
            .tech-assignments-table thead tr {
                background:#d9d9d9;
                border-bottom:2px solid #999;
            }
            .tech-assignments-table th,
            .tech-assignments-table td {
                padding:8px 12px;
                border-bottom:1px solid #ddd;
                color:#333;
            }
            .tech-assignments-table th {
                font-weight:bold;
                text-align:left;
            }
            .tech-assignments-table th:last-child,
            .tech-assignments-table td:last-child {
                text-align:right;
            }
        </style>

        <script>
        let currentModalContext = null;
        let techPayRateById = {};
        let isTechEditMode = false;
        let selectedTechIds = new Set();

        // -----------------------------
        // Add Tech Modal
        // -----------------------------
        function openAddTechModal() {
            document.getElementById('addTechModal').style.display = 'block';
            // Clear fields
            document.getElementById('techFirstName').value = '';
            document.getElementById('techLastName').value = '';
            document.getElementById('techRate').value = '';
        }

        function closeAddTechModal() {
            document.getElementById('addTechModal').style.display = 'none';
        }

        function toggleTechEditMode() {
            isTechEditMode = !isTechEditMode;
            selectedTechIds = new Set();
            const editBtn = document.getElementById('techEditBtn');
            const archiveActions = document.getElementById('techArchiveActions');
            if (editBtn) {
                editBtn.textContent = isTechEditMode ? 'DONE' : 'EDIT';
            }
            if (archiveActions) {
                archiveActions.style.display = isTechEditMode ? 'block' : 'none';
            }
            updateArchiveButtonState();
            loadTechsList();
        }

        function updateArchiveButtonState() {
            const archiveBtn = document.getElementById('archiveTechBtn');
            if (!archiveBtn) return;
            archiveBtn.disabled = selectedTechIds.size === 0;
        }

        function onTechArchiveCheckboxChange(techId, isChecked) {
            if (isChecked) {
                selectedTechIds.add(String(techId));
            } else {
                selectedTechIds.delete(String(techId));
            }
            updateArchiveButtonState();
        }

        function archiveSelectedTechs() {
            const selected = Array.from(selectedTechIds);
            if (!selected.length) {
                alert('Select at least one technician to archive.');
                return;
            }

            if (!confirm(`Archive ${selected.length} technician(s)?`)) {
                return;
            }

            fetch('/api/techs/archive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ ids: selected.map(id => parseInt(id, 10)) })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                selectedTechIds = new Set();
                updateArchiveButtonState();
                loadTechsList();
                loadArchivedTechs();
            })
            .catch(err => {
                console.error('Error archiving techs:', err);
                alert('Error archiving selected technicians.');
            });
        }

        function saveTech() {
            const firstName = document.getElementById('techFirstName').value.trim();
            const lastName = document.getElementById('techLastName').value.trim();
            const rate = parseFloat(document.getElementById('techRate').value);

            if (!firstName || !lastName || !rate) {
                alert("Please enter first name, last name, and rate.");
                return;
            }

            fetch('/api/techs/add', {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    pay_rate: rate
                })
            })
            .then(r => r.json())
            .then(() => {
                closeAddTechModal();
                loadTechsList();
                loadArchivedTechs();
            })
            .catch(err => {
                console.error("Error saving tech:", err);
                alert("Error saving tech. Please try again.");
            });
        }

        // Load and Display Techs
        // -----------------------------
        function loadTechsList() {
            const tableContainer = document.getElementById('techsListContainer');
            tableContainer.innerHTML = "<p style='color:#777; text-align:center; padding:12px;'>Loading...</p>";

            fetch('/api/techs/list', { credentials: 'include' })
            .then(r => r.json())
            .then(techsRes => {
                tableContainer.innerHTML = "";

                if (!techsRes.techs || techsRes.techs.length === 0) {
                    tableContainer.innerHTML = "<p style='color:#777; text-align:center; padding:12px;'>No techs added yet.</p>";
                    return;
                }

                // Display tech details in table
                techsRes.techs.forEach(tech => {
                    const fullName = `${tech.first_name} ${tech.last_name}`;
                    const assignmentsId = `tech-assignments-${tech.id}`;
                    const techRate = Number(tech.pay_rate || 0);
                    techPayRateById[String(tech.id)] = techRate;

                    // Main tech row
                    const row = document.createElement('div');
                    row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee;';
                    row.className = 'tech-row clickable';

                    const techNameCell = document.createElement('div');
                    techNameCell.style.flex = "1";
                    techNameCell.style.textAlign = "left";
                    techNameCell.style.display = "flex";
                    techNameCell.style.alignItems = "center";
                    techNameCell.style.gap = "10px";

                    if (isTechEditMode) {
                        const check = document.createElement('input');
                        check.type = 'checkbox';
                        check.checked = selectedTechIds.has(String(tech.id));
                        check.style.width = '16px';
                        check.style.height = '16px';
                        check.style.cursor = 'pointer';
                        check.addEventListener('click', function(e) {
                            e.stopPropagation();
                        });
                        check.addEventListener('change', function() {
                            onTechArchiveCheckboxChange(tech.id, check.checked);
                        });
                        techNameCell.appendChild(check);
                    }

                    const techName = document.createElement('span');
                    techName.textContent = fullName;
                    techName.style.cursor = "default";
                    techName.style.color = "#333";
                    techName.style.textDecoration = "none";
                    techName.style.fontWeight = "bold";

                    techNameCell.appendChild(techName);

                    const rateCell = document.createElement('div');
                    rateCell.style.flex = "1";
                    rateCell.style.textAlign = "center";
                    rateCell.textContent = `$${tech.pay_rate.toFixed(2)}/hr`;

                    row.appendChild(techNameCell);
                    row.appendChild(rateCell);

                    row.onmouseover = function() { this.style.backgroundColor = "#f5f5f5"; };
                    row.onmouseout = function() { this.style.backgroundColor = "transparent"; };

                    row.onclick = function() {
                        if (isTechEditMode) {
                            return;
                        }
                        toggleTechAssignments(tech.id, fullName, assignmentsId, techRate);
                    };

                    const assignmentsRow = document.createElement('div');
                    assignmentsRow.id = assignmentsId;
                    assignmentsRow.className = 'tech-assignments';
                    assignmentsRow.style.display = 'none';

                    tableContainer.appendChild(row);
                    tableContainer.appendChild(assignmentsRow);
                });
            })
            .catch(err => {
                console.error("Error loading techs:", err);
                tableContainer.innerHTML = "<p style='color:red; text-align:center; padding:12px;'>Error loading techs.</p>";
            });
        }

        function loadArchivedTechs() {
            const container = document.getElementById('archivedTechsContainer');
            if (!container) return;
            container.innerHTML = "<p style='color:#777; text-align:center; padding:12px;'>Loading...</p>";

            fetch('/api/techs/archived', { credentials: 'include' })
            .then(r => r.json())
            .then(res => {
                const archived = res.archived || [];
                if (!archived.length) {
                    container.innerHTML = "<p style='color:#777; text-align:center; padding:12px;'>No archived technicians.</p>";
                    return;
                }

                const rows = archived.map(item => {
                    const roItems = (item.assigned_ros || []).map(ro => {
                        const roVal = ro.ro || '—';
                        const hrsVal = Number(ro.hours || 0).toFixed(1);
                        return `<span style=\"display:inline-block; margin-right:8px;\">RO ${roVal} (${hrsVal}h)</span>`;
                    }).join('') || '<span>—</span>';
                    return `
                        <div style="padding:10px 0; border-bottom:1px solid #eee;">
                            <div style="font-weight:bold; color:#333;">${item.tech_name || 'Unknown'}</div>
                            <div style="font-size:13px; color:#555; margin-top:4px;">Rate: $${Number(item.pay_rate || 0).toFixed(2)}/hr</div>
                            <div style="font-size:13px; color:#555; margin-top:4px;">Total Hours: ${Number(item.total_hours || 0).toFixed(1)}</div>
                            <div style="font-size:13px; color:#555; margin-top:6px;">Assigned ROs: ${roItems}</div>
                        </div>
                    `;
                }).join('');

                container.innerHTML = rows;
            })
            .catch(err => {
                console.error('Error loading archived techs:', err);
                container.innerHTML = "<p style='color:red; text-align:center; padding:12px;'>Error loading archived technicians.</p>";
            });
        }

        function toggleTechAssignments(techId, techName, containerId, techRate) {
            const container = document.getElementById(containerId);
            if (!container) return;
            const isVisible = container.style.display === 'block';
            container.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) {
                loadTechAssignmentsForTech(techId, techName, container, techRate);
            }
        }

        function loadTechAssignmentsForTech(techId, techName, container, techRate) {
            if (!container) return;
            container.innerHTML = `
                <div class="tech-assignments-panel">
                    <div class="tech-assignments-title">Tech List</div>
                    <div style="color:#777;">Loading assignments...</div>
                </div>
            `;

            fetch(`/api/tech-assignments?tech_id=${encodeURIComponent(techId)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    if (!container) return;
                    const assignments = res.assignments || [];
                    if (assignments.length === 0) {
                        container.innerHTML = `
                            <div class="tech-assignments-panel">
                                <div class="tech-assignments-title">Tech List</div>
                                <div style="color:#999; padding:8px 0;">No assignments yet.</div>
                            </div>
                        `;
                        return;
                    }
                    const rows = assignments.map(item => {
                        const total = Number.isFinite(parseFloat(item.total_hours)) ? parseFloat(item.total_hours).toFixed(1) : '0.0';
                        const ro = item.ro || '—';
                        const vehicle = item.vehicle || '—';
                        const textColor = '#333';
                        return `
                            <tr style="background:#fff; border-bottom:1px solid #ddd;">
                                <td style="font-weight:bold; color:${textColor};">
                                    <button type="button" class="assignment-link link-button" data-ro="${ro}" data-tech-id="${techId}" data-tech-rate="${Number(techRate || 0).toFixed(2)}" data-tech="${techName.replace(/"/g, '&quot;')}" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit; font-weight:bold;">
                                        RO# ${ro}
                                    </button>
                                </td>
                                <td>${vehicle}</td>
                                <td style="font-weight:bold;">${total}</td>
                            </tr>
                        `;
                    }).join('');

                    container.innerHTML = `
                        <div class="tech-assignments-panel">
                            <div class="tech-assignments-title">Tech List</div>
                            <table class="tech-assignments-table">
                                <thead>
                                    <tr>
                                        <th>RO#</th>
                                        <th>Vehicle</th>
                                        <th>HRS</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        </div>
                    `;

                    container.querySelectorAll('.assignment-link').forEach(button => {
                        button.addEventListener('click', (event) => {
                            event.stopPropagation();
                            const ro = button.dataset.ro || '';
                            const techIdValue = parseInt(button.dataset.techId || '0', 10);
                            const tech = button.dataset.tech || '';
                            const techRateValue = parseFloat(button.dataset.techRate || '0') || 0;
                            openTechAssignmentModal(event, ro, techIdValue, tech, techRateValue);
                        });
                    });
                })
                .catch(err => {
                    console.error('Error loading assignments:', err);
                    if (container) {
                        container.innerHTML = `
                            <div class="tech-assignments-panel">
                                <div class="tech-assignments-title">Tech List</div>
                                <div style="color:red; padding:8px 0;">Error loading assignments.</div>
                            </div>
                        `;
                    }
                });
        }

        let currentAssignmentPrintHtml = '';

        function openTechAssignmentModal(event, roNumber, techId, techName, techRate) {
            if (event) {
                event.stopPropagation();
            }
            const modal = document.getElementById('techAssignmentModal');
            const title = document.getElementById('techAssignmentTitle');
            const body = document.getElementById('techAssignmentBody');
            if (!modal || !title || !body) return;

            title.textContent = `Labor Lines - RO# ${roNumber} (${techName})`;
            body.innerHTML = '<div style="color:#777;">Loading...</div>';
            modal.style.display = 'block';
            const resolvedRate = Number.isFinite(Number(techRate)) ? Number(techRate) : Number(techPayRateById[String(techId)] || 0);
            currentModalContext = { ro: roNumber, tech_id: techId, tech_name: techName, pay_rate: resolvedRate };

            fetch(`/api/tech-assignment-lines?ro=${encodeURIComponent(roNumber)}&tech_id=${encodeURIComponent(techId)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    if (!body) return;
                    const visible = res.lines || [];
                    if (!visible.length) {
                        body.innerHTML = '<div style="color:#777;">No assigned repair lines.</div>';
                        currentAssignmentPrintHtml = '<div>No assigned repair lines.</div>';
                        return;
                    }

                    const rowsHtml = visible.map(item => {
                        const line = item.line || '—';
                        const desc = item.description || '';
                        const value = Number.isFinite(parseFloat(item.value)) ? parseFloat(item.value).toFixed(1) : '0.0';
                        const key = item.line_key || String(line);
                        return `
                            <label style="display:flex; align-items:center; gap:10px; padding:10px 8px; border-bottom:1px solid #eee; cursor:pointer;">
                                <input type="checkbox" class="flagout-line-checkbox" data-line-key="${key}" data-hours="${value}" checked onchange="updateFlagOutMasterCheckbox()" style="width:16px; height:16px; cursor:pointer;" />
                                <div class="print-line-desc" style="flex:1;"><strong>Line ${line}</strong> - ${desc}</div>
                                <div class="print-line-hours" style="min-width:80px; text-align:right; font-weight:bold;">${value} hrs</div>
                            </label>
                        `;
                    }).join('');

                    body.innerHTML = `
                        <div style="margin:0 0 10px 0; padding:8px; border:1px solid #ddd; background:#fafafa; border-radius:4px;">
                            <label style="display:flex; align-items:center; gap:8px; font-weight:bold; cursor:pointer;">
                                <input type="checkbox" id="flagout-master-checkbox" checked onchange="toggleAllFlagOutLines(this.checked)" style="width:16px; height:16px; cursor:pointer;" />
                                Select / Unselect All
                            </label>
                        </div>
                        <div>${rowsHtml}</div>
                        <div id="flagout-summary" style="margin-top:12px; padding:10px 12px; border:1px solid #ddd; background:#fafafa; border-radius:4px; font-size:14px;"></div>
                    `;
                    currentAssignmentPrintHtml = body.innerHTML;
                    updateFlagOutSummary();
                })
                .catch(err => {
                    console.error('Error loading repair lines:', err);
                    if (body) {
                        body.innerHTML = '<div style="color:red;">Error loading repair lines.</div>';
                    }
                    currentAssignmentPrintHtml = '<div>Error loading repair lines.</div>';
                });
        }

        function closeTechAssignmentModal() {
            const modal = document.getElementById('techAssignmentModal');
            if (modal) modal.style.display = 'none';
            currentModalContext = null;
        }

        function toggleAllFlagOutLines(checked) {
            const checks = document.querySelectorAll('.flagout-line-checkbox');
            checks.forEach(chk => {
                chk.checked = checked;
            });
            updateFlagOutMasterCheckbox();
        }

        function updateFlagOutMasterCheckbox() {
            const master = document.getElementById('flagout-master-checkbox');
            const checks = document.querySelectorAll('.flagout-line-checkbox');
            if (!master) return;
            if (checks.length === 0) {
                master.checked = false;
                master.indeterminate = false;
                updateFlagOutSummary();
                return;
            }
            const checkedCount = Array.from(checks).filter(chk => chk.checked).length;
            master.checked = checkedCount === checks.length;
            master.indeterminate = checkedCount > 0 && checkedCount < checks.length;
            updateFlagOutSummary();
        }

        function updateFlagOutSummary() {
            const summaryEl = document.getElementById('flagout-summary');
            if (!summaryEl) return;

            const payRate = Number(currentModalContext?.pay_rate || 0);
            const selected = Array.from(document.querySelectorAll('.flagout-line-checkbox:checked'));
            const totalHours = selected.reduce((sum, chk) => sum + (parseFloat(chk.getAttribute('data-hours') || '0') || 0), 0);
            const totalPay = totalHours * payRate;

            summaryEl.innerHTML = `
                <span style="font-weight:bold;">Total HRS</span> ${totalHours.toFixed(1)}
                <span style="font-weight:bold; margin-left:18px;">Rate</span> $${payRate.toFixed(2)}
                <span style="font-weight:bold; margin-left:18px;">Pay</span> $${totalPay.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            `;
        }

        function flagOutSelectedLines() {
            if (!currentModalContext?.ro || !currentModalContext?.tech_id) {
                return;
            }

            const selectedKeys = Array.from(document.querySelectorAll('.flagout-line-checkbox:checked'))
                .map(chk => chk.getAttribute('data-line-key'))
                .filter(Boolean);
            const totalHours = Array.from(document.querySelectorAll('.flagout-line-checkbox:checked'))
                .reduce((sum, chk) => sum + (parseFloat(chk.getAttribute('data-hours') || '0') || 0), 0);
            const payRate = Number(currentModalContext?.pay_rate || 0);
            const totalPay = totalHours * payRate;

            if (selectedKeys.length === 0) {
                alert('Select at least one line to flag out.');
                return;
            }

            fetch('/api/tech-flag-out', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    ro: currentModalContext.ro,
                    tech_id: currentModalContext.tech_id,
                    line_keys: selectedKeys,
                    pay_rate: payRate,
                    total_hours: totalHours,
                    total_pay: totalPay
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }

                closeTechAssignmentModal();
                loadTechsList();
            })
            .catch(err => {
                console.error('Error flagging out lines:', err);
                alert('Error flagging out selected lines.');
            });
        }

        function printTechAssignment() {
            const title = (document.getElementById('techAssignmentTitle')?.textContent || 'Repair Lines').trim();
            const selected = Array.from(document.querySelectorAll('.flagout-line-checkbox:checked'));
            if (selected.length === 0) {
                alert('Select at least one line to print.');
                return;
            }

            let totalHours = 0;
            const lineRows = selected.map((chk) => {
                const row = chk.closest('label');
                const desc = row?.querySelector('.print-line-desc')?.innerText || '';
                const hoursText = row?.querySelector('.print-line-hours')?.innerText || '';
                const hoursVal = parseFloat(chk.getAttribute('data-hours') || '0') || 0;
                totalHours += hoursVal;
                return `<div class="line"><div>${desc}</div><div><strong>${hoursText}</strong></div></div>`;
            }).join('');

            const payRate = Number(currentModalContext?.pay_rate || 0);
            const totalAmount = totalHours * payRate;

            const printWindow = window.open('', '_blank', 'width=900,height=700');
            if (!printWindow) return;
            printWindow.document.write(`
                <html>
                <head>
                    <title>${title}</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        h2 { margin: 0 0 14px 0; }
                        .summary-row { display:flex; gap:18px; align-items:center; margin:0 0 14px 0; font-size:16px; font-weight:bold; }
                        .summary-pill { padding:6px 10px; border:1px solid #ddd; border-radius:6px; background:#fafafa; }
                        .line { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee; }
                        .line strong { margin-right: 6px; }
                    </style>
                </head>
                <body>
                    <h2>${title}</h2>
                    <div class="summary-row">
                        <div class="summary-pill">Total HRS: ${totalHours.toFixed(1)}</div>
                        <div class="summary-pill">Pay Rate: $${payRate.toFixed(2)}/hr</div>
                        <div class="summary-pill">Total: $${totalAmount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                    ${lineRows}
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
        }

        // Load techs list on startup
        document.addEventListener("DOMContentLoaded", () => {
            loadTechsList();
            loadArchivedTechs();
        });

        </script>

    </div>
    """

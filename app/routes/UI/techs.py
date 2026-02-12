"""Tech's screen content for the FlagTech UI."""


def get_techs_screen_html():
    """Return the HTML content for the Tech's screen."""
    return """
    <div id="tech" class="screen" style="padding:20px;">

        <h1 style="text-align:center; margin-bottom:20px;">TECHS</h1>

        <!-- Add Tech Button (centered) -->
        <div style="text-align:center; margin-bottom:30px;">
            <button onclick="openAddTechModal()"
                    style="padding:12px 24px; font-size:16px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:4px;">
                + tech
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
                </div>
            </div>
        </div>

        <style>
            .tech-row.clickable {
                cursor: pointer;
            }
            .tech-assignments {
                padding: 10px 12px;
                border-bottom: 1px solid #eee;
                background: #fafafa;
            }
            .tech-assignments .assignment-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            .tech-assignments .assignment-item:last-child {
                border-bottom: none;
            }
            .tech-assignments .assignment-meta {
                display: flex;
                gap: 12px;
                align-items: center;
                font-size: 12px;
                color: #555;
            }
            .tech-assignments .assignment-role {
                padding: 2px 6px;
                border-radius: 10px;
                background: #e0e0e0;
                font-size: 11px;
                text-transform: uppercase;
            }
        </style>

        <script>

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

                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = "−";
                    deleteBtn.title = `Delete ${fullName}`;
                    deleteBtn.setAttribute('aria-label', `Delete ${fullName}`);
                    deleteBtn.style.width = "20px";
                    deleteBtn.style.height = "20px";
                    deleteBtn.style.borderRadius = "50%";
                    deleteBtn.style.border = "none";
                    deleteBtn.style.backgroundColor = "#d32f2f";
                    deleteBtn.style.color = "#fff";
                    deleteBtn.style.fontWeight = "bold";
                    deleteBtn.style.cursor = "pointer";
                    deleteBtn.style.display = "inline-flex";
                    deleteBtn.style.alignItems = "center";
                    deleteBtn.style.justifyContent = "center";
                    deleteBtn.onclick = function(e) {
                        e.stopPropagation();
                        deleteTech(tech.id, fullName);
                    };

                    const techName = document.createElement('span');
                    techName.textContent = fullName;
                    techName.style.cursor = "default";
                    techName.style.color = "#333";
                    techName.style.textDecoration = "none";
                    techName.style.fontWeight = "bold";

                    techNameCell.appendChild(deleteBtn);
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
                        toggleTechAssignments(tech.id, fullName, assignmentsId);
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

        function toggleTechAssignments(techId, techName, containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;
            const isVisible = container.style.display === 'block';
            container.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) {
                loadTechAssignmentsForTech(techId, techName, container);
            }
        }

        function loadTechAssignmentsForTech(techId, techName, container) {
            if (!container) return;
            container.innerHTML = '<div style="color:#777;">Loading assignments...</div>';

            fetch(`/api/tech-assignments?tech_id=${encodeURIComponent(techId)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    if (!container) return;
                    const assignments = res.assignments || [];
                    if (assignments.length === 0) {
                        container.innerHTML = '<div style="color:#999;">No assignments yet.</div>';
                        return;
                    }
                    container.innerHTML = assignments.map(item => {
                        const roleLabel = item.role === 'paint' ? 'Painter' : 'Labor';
                        const total = Number.isFinite(parseFloat(item.total_hours)) ? parseFloat(item.total_hours).toFixed(1) : '0.0';
                        const ro = item.ro || '—';
                        const excluded = encodeURIComponent(JSON.stringify(item.excluded_lines || []));
                        return `
                            <div class="assignment-item">
                                <div class="assignment-meta">
                                    <span class="assignment-role">${roleLabel}</span>
                                    <button type="button" class="assignment-link link-button" data-ro="${ro}" data-role="${item.role}" data-excluded="${excluded}" data-tech="${techName.replace(/"/g, '&quot;')}" style="background:none; border:none; color:#0066cc; text-decoration:underline; cursor:pointer; padding:0; font:inherit;">
                                        RO# ${ro}
                                    </button>
                                </div>
                                <div style="font-weight:bold;">${total} hrs</div>
                            </div>
                        `;
                    }).join('');

                    container.querySelectorAll('.assignment-link').forEach(button => {
                        button.addEventListener('click', (event) => {
                            event.stopPropagation();
                            const ro = button.dataset.ro || '';
                            const role = button.dataset.role || 'labor';
                            const tech = button.dataset.tech || '';
                            let excluded = [];
                            try {
                                excluded = JSON.parse(decodeURIComponent(button.dataset.excluded || '[]'));
                            } catch (e) {
                                excluded = [];
                            }
                            openTechAssignmentModal(event, ro, role, excluded, tech);
                        });
                    });
                })
                .catch(err => {
                    console.error('Error loading assignments:', err);
                    if (container) {
                        container.innerHTML = '<div style="color:red;">Error loading assignments.</div>';
                    }
                });
        }

        let currentAssignmentPrintHtml = '';

        function openTechAssignmentModal(event, roNumber, role, excludedLines, techName) {
            if (event) {
                event.stopPropagation();
            }
            const modal = document.getElementById('techAssignmentModal');
            const title = document.getElementById('techAssignmentTitle');
            const body = document.getElementById('techAssignmentBody');
            if (!modal || !title || !body) return;

            const roleLabel = role === 'paint' ? 'Painter' : 'Labor';
            title.textContent = `${roleLabel} Lines - RO# ${roNumber} (${techName})`;
            body.innerHTML = '<div style="color:#777;">Loading...</div>';
            modal.style.display = 'block';

            fetch(`/api/ro-repairs?ro=${encodeURIComponent(roNumber)}`, { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    if (!body) return;
                    const lines = role === 'paint' ? res.paint : res.labor;
                    const excluded = Array.isArray(excludedLines) ? excludedLines.map(String) : [];
                    const visible = (lines || []).filter((item, index) => {
                        const key = item.line !== null && item.line !== undefined ? String(item.line) : String(index + 1);
                        return !excluded.includes(key);
                    });
                    if (!visible.length) {
                        body.innerHTML = '<div style="color:#777;">No assigned repair lines.</div>';
                        currentAssignmentPrintHtml = '<div>No assigned repair lines.</div>';
                        return;
                    }
                    body.innerHTML = visible.map(item => {
                        const line = item.line || '—';
                        const desc = item.description || '';
                        const value = Number.isFinite(parseFloat(item.value)) ? parseFloat(item.value).toFixed(1) : '0.0';
                        return `
                            <div style="display:flex; justify-content:space-between; padding:10px 8px; border-bottom:1px solid #eee;">
                                <div style="flex:1;"><strong>Line ${line}</strong> - ${desc}</div>
                                <div style="min-width:80px; text-align:right; font-weight:bold;">${value} hrs</div>
                            </div>
                        `;
                    }).join('');
                    currentAssignmentPrintHtml = body.innerHTML;
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
        }

        function printTechAssignment() {
            const printWindow = window.open('', '_blank', 'width=900,height=700');
            if (!printWindow) return;
            printWindow.document.write(`
                <html>
                <head>
                    <title>Repair Lines</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .line { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee; }
                        .line strong { margin-right: 6px; }
                    </style>
                </head>
                <body>
                    ${currentAssignmentPrintHtml}
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
        }

        function deleteTech(techId, techName) {
            if (!confirm(`Delete ${techName}?`)) {
                return;
            }

            fetch('/api/techs/delete', {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: techId })
            })
            .then(r => r.json())
            .then(() => {
                loadTechsList();
            })
            .catch(err => {
                console.error("Error deleting tech:", err);
                alert("Error deleting tech. Please try again.");
            });
        }

        // Load techs list on startup
        document.addEventListener("DOMContentLoaded", loadTechsList);

        </script>

    </div>
    """

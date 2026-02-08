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

        <script>

        // Check if BACKEND_BASE is already defined, if not, define it
        if (typeof BACKEND_BASE === 'undefined') {
            var BACKEND_BASE = "https://flagtech1.onrender.com";
        }

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

            fetch(`${BACKEND_BASE}/api/techs/add`, {
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

            fetch(`${BACKEND_BASE}/api/techs/list`)
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

                    // Main tech row
                    const row = document.createElement('div');
                    row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee;';
                    row.className = 'tech-row';

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

                    tableContainer.appendChild(row);
                });
            })
            .catch(err => {
                console.error("Error loading techs:", err);
                tableContainer.innerHTML = "<p style='color:red; text-align:center; padding:12px;'>Error loading techs.</p>";
            });
        }

        function deleteTech(techId, techName) {
            if (!confirm(`Delete ${techName}?`)) {
                return;
            }

            fetch(`${BACKEND_BASE}/api/techs/delete`, {
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

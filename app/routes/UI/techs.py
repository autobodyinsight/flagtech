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

        <!-- Techs Cards Grid -->
        <div id="techsCardsContainer" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:15px; margin-bottom:40px;">
        </div>

        <!-- Techs Details Table -->
        <div style="margin-top:40px;">
            <h2 style="margin-bottom:20px;">Assignments</h2>
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background-color:#f5f5f5; border-bottom:2px solid #ddd;">
                        <th style="padding:12px; text-align:left; font-weight:bold;">Tech Name</th>
                        <th style="padding:12px; text-align:center; font-weight:bold;">Pay Rate</th>
                        <th style="padding:12px; text-align:center; font-weight:bold;">Total RO's</th>
                        <th style="padding:12px; text-align:right; font-weight:bold;">Total Hours</th>
                    </tr>
                </thead>
                <tbody id="techsListContainer">
                </tbody>
            </table>
        </div>

        <!-- Tech Details Modal -->
        <div id="techDetailsModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:900px; max-height:90vh; overflow-y:auto;">
                <span class="close" onclick="closeTechDetailsModal()">&times;</span>
                <h2 id="techDetailsTitle" style="margin-bottom:20px;"></h2>

                <!-- RO's List -->
                <div id="rosListContainer" style="margin-bottom:20px;">
                </div>

                <!-- Repair Lines for Selected RO -->
                <div id="repairLinesContainer" style="display:none; margin-top:30px; border-top:2px solid #ddd; padding-top:20px;">
                    <h3 id="repairLinesTitle" style="margin-bottom:15px;"></h3>
                    <div id="repairLinesList" style="background-color:#f9f9f9; border:1px solid #ddd; border-radius:4px; max-height:400px; overflow-y:auto;">
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Tech Modal -->
        <div id="addTechModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:400px;">
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

            fetch(`${BACKEND_BASE}/ui/techs/add`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    pay_rate: rate
                })
            })
            .then(r => r.json())
            .then(res => {
                closeAddTechModal();
                loadTechsList();
            })
            .catch(err => {
                console.error("Error saving tech:", err);
                alert("Error saving tech. Please try again.");
            });
        }

        // -----------------------------
        // Load and Display Techs
        // -----------------------------
        function loadTechsList() {
            const cardsContainer = document.getElementById('techsCardsContainer');
            const tableContainer = document.getElementById('techsListContainer');
            cardsContainer.innerHTML = "<p style='color:#777; text-align:center; grid-column:1/-1;'>Loading...</p>";
            tableContainer.innerHTML = "";

            // Fetch techs list and tech assignments to get total ROs and hours
            Promise.all([
                fetch(`${BACKEND_BASE}/ui/techs/list`).then(r => r.json()),
                fetch(`${BACKEND_BASE}/ui/tech-assignments`).then(r => r.json())
            ])
            .then(([techsRes, assignmentsRes]) => {
                cardsContainer.innerHTML = "";
                tableContainer.innerHTML = "";

                if (!techsRes.techs || techsRes.techs.length === 0) {
                    cardsContainer.innerHTML = "<p style='color:#777; text-align:center; grid-column:1/-1;'>No techs added yet.</p>";
                    return;
                }

                // Create a map of tech assignments by full name
                const assignmentsMap = {};
                if (assignmentsRes.tech_summary) {
                    assignmentsRes.tech_summary.forEach(t => {
                        assignmentsMap[t.tech] = {
                            total_vehicles: t.total_vehicles || 0,
                            total_hours: t.total_hours || 0
                        };
                    });
                }

                // Display tech cards
                techsRes.techs.forEach(tech => {
                    const fullName = `${tech.first_name} ${tech.last_name}`;
                    const assignments = assignmentsMap[fullName] || { total_vehicles: 0, total_hours: 0 };

                    const card = document.createElement('div');
                    card.style.padding = "20px";
                    card.style.border = "1px solid #ddd";
                    card.style.borderRadius = "8px";
                    card.style.backgroundColor = "#f9f9f9";
                    card.style.textAlign = "center";
                    card.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";

                    card.innerHTML = `
                        <div style="font-weight:bold; font-size:16px; margin-bottom:5px;">
                            ${tech.first_name}
                        </div>
                        <div style="font-size:14px; color:#666;">
                            ${tech.last_name}
                        </div>
                    `;

                    cardsContainer.appendChild(card);
                });

                // Display tech details in table
                techsRes.techs.forEach(tech => {
                    const fullName = `${tech.first_name} ${tech.last_name}`;
                    const assignments = assignmentsMap[fullName] || { total_vehicles: 0, total_hours: 0 };

                    const row = document.createElement('tr');
                    row.style.borderBottom = "1px solid #eee";
                    row.innerHTML = `
                        <td style="padding:12px; text-align:left;"><span onclick="openTechDetailsModal('${fullName}')" style="cursor:pointer; color:#0066cc; text-decoration:underline;">${fullName}</span></td>
                        <td style="padding:12px; text-align:center;">$${tech.pay_rate.toFixed(2)}/hr</td>
                        <td style="padding:12px; text-align:center;">${assignments.total_vehicles}</td>
                        <td style="padding:12px; text-align:right;">${assignments.total_hours.toFixed(1)}</td>
                    `;
                    row.onmouseover = function() { this.style.backgroundColor = "#f5f5f5"; };
                    row.onmouseout = function() { this.style.backgroundColor = "transparent"; };

                    tableContainer.appendChild(row);
                });
            })
            .catch(err => {
                console.error("Error loading techs:", err);
                cardsContainer.innerHTML = "<p style='color:red; text-align:center; grid-column:1/-1;'>Error loading techs.</p>";
            });
        }

        // Load techs list on startup
        document.addEventListener("DOMContentLoaded", loadTechsList);

        // Tech Details Modal Functions
        function openTechDetailsModal(techName) {
            const modal = document.getElementById('techDetailsModal');
            document.getElementById('techDetailsTitle').textContent = `${techName} - RO Details`;
            document.getElementById('rosListContainer').innerHTML = "<p style='text-align:center; color:#777;'>Loading RO's...</p>";
            document.getElementById('repairLinesContainer').style.display = 'none';
            
            modal.style.display = 'block';

            // Fetch tech assignment details
            fetch(`${BACKEND_BASE}/ui/tech-assignments`)
                .then(r => r.json())
                .then(res => {
                    const rosListContainer = document.getElementById('rosListContainer');
                    rosListContainer.innerHTML = '';

                    if (!res.tech_summary) {
                        rosListContainer.innerHTML = "<p style='text-align:center; color:#777;'>No RO assignments found.</p>";
                        return;
                    }

                    // Find the tech's assignments
                    const techData = res.tech_summary.find(t => t.tech === techName);
                    if (!techData || !techData.ros || techData.ros.length === 0) {
                        rosListContainer.innerHTML = "<p style='text-align:center; color:#777;'>No RO assignments found for this technician.</p>";
                        return;
                    }

                    // Create header for RO list
                    const header = document.createElement('div');
                    header.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:2px solid #ddd; font-weight:bold; margin-bottom:10px;';
                    header.innerHTML = `
                        <div style="flex:1; text-align:left;">RO Number</div>
                        <div style="flex:2; text-align:center;">Vehicle Info</div>
                        <div style="flex:1; text-align:right;">Total Hours</div>
                    `;
                    rosListContainer.appendChild(header);

                    // Display each RO
                    techData.ros.forEach(ro => {
                        const roDiv = document.createElement('div');
                        roDiv.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee; cursor:pointer;';
                        roDiv.onmouseover = function() { this.style.backgroundColor = '#f9f9f9'; };
                        roDiv.onmouseout = function() { this.style.backgroundColor = 'transparent'; };

                        roDiv.innerHTML = `
                            <div style="flex:1; text-align:left;"><span onclick="loadRepairLines('${techName}', '${ro.ro}', '${ro.vehicle_info.replace(/'/g, "\\'")}', ${ro.total_hours})" style="color:#0066cc; text-decoration:underline; cursor:pointer;">${ro.ro}</span></div>
                            <div style="flex:2; text-align:center;">${ro.vehicle_info}</div>
                            <div style="flex:1; text-align:right;">${ro.total_hours.toFixed(1)} hrs</div>
                        `;
                        rosListContainer.appendChild(roDiv);
                    });
                })
                .catch(err => {
                    console.error("Error loading tech assignments:", err);
                    document.getElementById('rosListContainer').innerHTML = "<p style='color:red; text-align:center;'>Error loading RO assignments.</p>";
                });
        }

        function closeTechDetailsModal() {
            document.getElementById('techDetailsModal').style.display = 'none';
        }

        function loadRepairLines(techName, roNumber, vehicleInfo, totalHours) {
            const repairLinesContainer = document.getElementById('repairLinesContainer');
            const repairLinesList = document.getElementById('repairLinesList');

            document.getElementById('repairLinesTitle').textContent = `Repair Lines - ${roNumber}`;
            repairLinesList.innerHTML = "<p style='text-align:center; color:#777; padding:20px;'>Loading repair lines...</p>";
            repairLinesContainer.style.display = 'block';

            // Fetch repair lines for this tech and RO
            fetch(`${BACKEND_BASE}/ui/tech-repair-lines?tech=${encodeURIComponent(techName)}&ro=${encodeURIComponent(roNumber)}`)
                .then(r => r.json())
                .then(res => {
                    repairLinesList.innerHTML = '';

                    if (!res.lines || res.lines.length === 0) {
                        repairLinesList.innerHTML = "<p style='text-align:center; color:#777; padding:20px;'>No repair lines assigned.</p>";
                        return;
                    }

                    // Create header
                    const header = document.createElement('div');
                    header.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:1px solid #ddd; font-weight:bold; position:sticky; top:0;';
                    header.innerHTML = `
                        <div style="flex:2; text-align:left;">Description</div>
                        <div style="flex:1; text-align:right;">Hours</div>
                    `;
                    repairLinesList.appendChild(header);

                    // Display repair lines
                    res.lines.forEach(line => {
                        const lineDiv = document.createElement('div');
                        lineDiv.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee;';
                        lineDiv.onmouseover = function() { this.style.backgroundColor = '#fafafa'; };
                        lineDiv.onmouseout = function() { this.style.backgroundColor = 'transparent'; };

                        lineDiv.innerHTML = `
                            <div style="flex:2; text-align:left;">${line.description || 'N/A'}</div>
                            <div style="flex:1; text-align:right;">${line.hours ? line.hours.toFixed(1) : '0'} hrs</div>
                        `;
                        repairLinesList.appendChild(lineDiv);
                    });
                })
                .catch(err => {
                    console.error("Error loading repair lines:", err);
                    repairLinesList.innerHTML = "<p style='color:red; text-align:center; padding:20px;'>Error loading repair lines.</p>";
                });
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('techDetailsModal');
            if (event.target === modal) {
                closeTechDetailsModal();
            }
        };

        </script>

    </div>
    """
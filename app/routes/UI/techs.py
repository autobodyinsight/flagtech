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

        <!-- Techs List -->
        <div id="techsListContainer">
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

        const BACKEND_BASE = "https://flagtech1.onrender.com";

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
            const container = document.getElementById('techsListContainer');
            container.innerHTML = "<p style='color:#777; text-align:center;'>Loading...</p>";

            // Fetch techs list and tech assignments to get total ROs and hours
            Promise.all([
                fetch(`${BACKEND_BASE}/ui/techs/list`).then(r => r.json()),
                fetch(`${BACKEND_BASE}/ui/tech-assignments`).then(r => r.json())
            ])
            .then(([techsRes, assignmentsRes]) => {
                container.innerHTML = "";

                if (!techsRes.techs || techsRes.techs.length === 0) {
                    container.innerHTML = "<p style='color:#777; text-align:center;'>No techs added yet.</p>";
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

                // Display each tech
                techsRes.techs.forEach(tech => {
                    const fullName = `${tech.first_name} ${tech.last_name}`;
                    const assignments = assignmentsMap[fullName] || { total_vehicles: 0, total_hours: 0 };

                    const techDiv = document.createElement('div');
                    techDiv.style.display = "flex";
                    techDiv.style.justifyContent = "space-between";
                    techDiv.style.alignItems = "center";
                    techDiv.style.padding = "15px";
                    techDiv.style.borderBottom = "1px solid #ddd";
                    techDiv.style.fontSize = "14px";

                    techDiv.innerHTML = `
                        <div style="flex:1; text-align:left;">
                            <strong>${tech.first_name} ${tech.last_name}</strong>
                        </div>
                        <div style="flex:1; text-align:center;">
                            Total RO's: ${assignments.total_vehicles}
                        </div>
                        <div style="flex:1; text-align:right;">
                            Total Hours: ${assignments.total_hours.toFixed(1)}
                        </div>
                    `;

                    container.appendChild(techDiv);
                });
            })
            .catch(err => {
                console.error("Error loading techs:", err);
                container.innerHTML = "<p style='color:red; text-align:center;'>Error loading techs.</p>";
            });
        }

        // Load techs list on startup
        document.addEventListener("DOMContentLoaded", loadTechsList);

        </script>

    </div>
    """
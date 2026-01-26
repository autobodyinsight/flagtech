"""Tech's screen content for the FlagTech UI."""

def get_techs_screen_html():
    """Return the HTML content for the Tech's screen."""
    return """
    <div id="tech" class="screen" style="padding:20px;">

        <h2>TECH MANAGEMENT</h2>

        <!-- Add Tech Button -->
        <button onclick="openAddTechModal()" 
                style="padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:4px; margin-top:10px;">
            Add Tech
        </button>

        <hr style="margin:20px 0;">

        <!-- Tech Cards -->
        <div id="techCardsContainer" style="display:flex; flex-wrap:wrap; gap:12px;">
        </div>

        <!-- Add Tech Modal -->
        <div id="addTechModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:400px;">
                <span class="close" onclick="closeAddTechModal()">&times;</span>
                <h3>Add Technician</h3>

                <label>First Name:</label>
                <input type="text" id="techFirstName" style="width:100%; padding:6px; margin-bottom:10px;">

                <label>Last Name:</label>
                <input type="text" id="techLastName" style="width:100%; padding:6px; margin-bottom:10px;">

                <label>Pay Rate (per hour):</label>
                <input type="number" step="0.01" id="techPayRate" style="width:100%; padding:6px; margin-bottom:10px;">

                <button onclick="saveTech()" 
                        style="padding:8px 16px; background-color:#505050; color:white; border:none; border-radius:3px; cursor:pointer;">
                    Save Tech
                </button>

                <h4 style="margin-top:20px;">Existing Techs</h4>
                <div id="techListContainer" style="max-height:200px; overflow-y:auto; border-top:1px solid #ddd; margin-top:10px; padding-top:10px;">
                </div>
            </div>
        </div>

        <!-- RO List Modal -->
        <div id="techROModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:600px;">
                <span class="close" onclick="closeTechROModal()">&times;</span>
                <h3 id="techROModalTitle">Tech ROs</h3>
                <div id="techROList"></div>
            </div>
        </div>

        <!-- Repair Line Modal -->
        <div id="techRODetailModal" class="modal" style="display:none;">
          <div class="modal-content" style="max-width:700px;">
            <span class="close" onclick="closeTechRODetailModal()">&times;</span>
            <h3 id="techRODetailTitle">Repair Lines</h3>

            <div id="techRODetailList"></div>

            <div style="margin-top:20px; padding:10px; background:#fffacd; font-weight:bold;">
              Total Flagged: <span id="flaggedTotal">0.0</span> hrs
            </div>

            <button onclick="flagHours()" 
                    style="margin-top:15px; padding:10px 20px; background:#505050; color:white; border:none; border-radius:4px; cursor:pointer;">
              FLAG
            </button>
          </div>
        </div>

        <script>

        const BACKEND_BASE = "https://flagtech1.onrender.com";

        // -----------------------------
        // Add Tech Modal
        // -----------------------------
        function openAddTechModal() {
            document.getElementById('addTechModal').style.display = 'block';
            loadTechList();
        }

        function closeAddTechModal() {
            document.getElementById('addTechModal').style.display = 'none';
        }

        function saveTech() {
            const firstName = document.getElementById('techFirstName').value.trim();
            const lastName = document.getElementById('techLastName').value.trim();
            const payRate = parseFloat(document.getElementById('techPayRate').value);

            if (!firstName || !lastName || !payRate) {
                alert("Please enter first name, last name, and pay rate.");
                return;
            }

            fetch(`${BACKEND_BASE}/ui/techs/add`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    pay_rate: payRate
                })
            })
            .then(r => r.json())
            .then(res => {
                loadTechList();
                loadTechCards();
            });
        }

        function loadTechList() {
            fetch(`${BACKEND_BASE}/ui/techs/list`)
                .then(r => r.json())
                .then(res => {
                    const container = document.getElementById('techListContainer');
                    container.innerHTML = "";
                    res.techs.forEach(t => {
                        const div = document.createElement('div');
                        div.style.display = "flex";
                        div.style.justifyContent = "space-between";
                        div.style.padding = "4px 0";
                        div.innerHTML = `
                            <span>${t.first_name} ${t.last_name} ($${t.pay_rate.toFixed(2)}/hr)</span>
                            <button onclick="deleteTech(${t.id})"
                                    style="padding:2px 6px; background-color:#b00000; color:white; border:none; border-radius:3px; cursor:pointer;">
                                Delete
                            </button>
                        `;
                        container.appendChild(div);
                    });
                });
        }

        function deleteTech(id) {
            if (!confirm("Delete this tech?")) return;
            fetch(`${BACKEND_BASE}/ui/techs/${id}`, { method: "DELETE" })
                .then(() => {
                    loadTechList();
                    loadTechCards();
                });
        }

        // -----------------------------
        // Tech Summary Cards
        // -----------------------------
        function loadTechCards() {
            const container = document.getElementById('techCardsContainer');
            container.innerHTML = "<p style='color:#777;'>Loading...</p>";

            fetch(`${BACKEND_BASE}/ui/techs/summary`)
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                })
                .then(res => {
                    console.log("Tech summary response:", res);
                    container.innerHTML = "";

                    if (!res.summary || res.summary.length === 0) {
                        container.innerHTML = "<p style='color:#777;'>No tech activity yet.</p>";
                        return;
                    }

                    res.summary.forEach(t => {
                        const card = document.createElement('div');
                        card.style.border = "1px solid #ccc";
                        card.style.borderRadius = "6px";
                        card.style.padding = "12px";
                        card.style.width = "220px";
                        card.style.cursor = "pointer";
                        card.style.background = "#f9f9f9";

                        card.onclick = () => openTechROList(t.tech);

                        card.innerHTML = `
                            <div style="font-size:16px; font-weight:bold;">${t.tech}</div>
                            <div style="margin-top:6px;">ROs: ${t.ro_count}</div>
                            <div style="margin-top:4px;">Unpaid Hours: ${t.hours.toFixed(1)}</div>
                        `;

                        container.appendChild(card);
                    });
                })
                .catch(err => {
                    console.error("Error loading tech cards:", err);
                    container.innerHTML = "<p style='color:red;'>Error loading techs: " + err.message + "</p>";
                });
        }

        // -----------------------------
        // RO List Modal
        // -----------------------------
        function openTechROList(techName) {
            document.getElementById('techROModalTitle').innerText = techName + " — Assigned ROs";
            document.getElementById('techROModal').style.display = 'block';

            fetch(`${BACKEND_BASE}/ui/techs/${encodeURIComponent(techName)}/ros`)
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                })
                .then(res => {
                    console.log("Tech RO list response:", res);
                    const container = document.getElementById('techROList');
                    container.innerHTML = "";

                    if (!res.ros || res.ros.length === 0) {
                        container.innerHTML = "<p>No ROs assigned.</p>";
                        return;
                    }

                    res.ros.forEach(ro => {
                        const div = document.createElement('div');
                        div.style.padding = "10px";
                        div.style.borderBottom = "1px solid #ddd";
                        div.style.cursor = "pointer";

                        div.onclick = () => openTechRODetail(techName, ro.ro);

                        div.innerHTML = `
                            <strong>${ro.ro}</strong><br>
                            <span style="color:#555;">${ro.vehicle}</span><br>
                            <span style="color:#333;">${ro.total_hours.toFixed(1)} hrs</span>
                        `;

                        container.appendChild(div);
                    });
                })
                .catch(err => {
                    console.error("Error loading ROs:", err);
                    document.getElementById('techROList').innerHTML = "<p style='color:red;'>Error loading ROs: " + err.message + "</p>";
                });
        }

        function closeTechROModal() {
            document.getElementById('techROModal').style.display = 'none';
        }

        // -----------------------------
        // Repair Line Modal (Step 3)
        // -----------------------------
        let currentTech = null;
        let currentRO = null;
        let flaggedLines = [];

        function openTechRODetail(techName, roNumber) {
            currentTech = techName;
            currentRO = roNumber;

            document.getElementById('techRODetailTitle').innerText = techName + " — RO " + roNumber;
            document.getElementById('techRODetailModal').style.display = 'block';

            fetch(`${BACKEND_BASE}/ui/techs/${encodeURIComponent(techName)}/${encodeURIComponent(roNumber)}/lines`)
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                })
                .then(res => {
                    console.log("Tech RO lines response:", res);
                    const container = document.getElementById('techRODetailList');
                    container.innerHTML = "";
                    flaggedLines = [];

                    if (!res.lines || res.lines.length === 0) {
                        container.innerHTML = "<p>No lines found for this RO.</p>";
                        return;
                    }

                    res.lines.forEach((line, index) => {
                        const div = document.createElement('div');
                        div.style.display = "flex";
                        div.style.justifyContent = "space-between";
                        div.style.alignItems = "center";
                        div.style.padding = "10px";
                        div.style.borderBottom = "1px solid #ddd";

                        div.innerHTML = `
                            <input type="checkbox" onchange="toggleFlag(${index}, ${line.value})">
                            <div style="flex:1; margin-left:10px;">
                                <strong>Line ${line.line}</strong> — ${line.description}
                            </div>
                            <div>${line.value.toFixed(1)} hrs</div>
                            <div id="flag-${index}" style="width:80px; text-align:right; background:#fffacd; padding:5px;">
                                0.0
                            </div>
                        `;

                        container.appendChild(div);
                    });
                })
                .catch(err => {
                    console.error("Error loading lines:", err);
                    document.getElementById('techRODetailList').innerHTML = "<p style='color:red;'>Error loading lines: " + err.message + "</p>";
                });
        }

        function toggleFlag(index, value) {
            const box = document.querySelectorAll('#techRODetailList input[type="checkbox"]')[index];
            const yellowCell = document.getElementById(`flag-${index}`);

            if (box.checked) {
                yellowCell.innerText = value.toFixed(1);
                flaggedLines.push(value);
            } else {
                yellowCell.innerText = "0.0";
                flaggedLines = flaggedLines.filter(v => v !== value);
            }

            const total = flaggedLines.reduce((a, b) => a + b, 0);
            document.getElementById('flaggedTotal').innerText = total.toFixed(1);
        }

        function closeTechRODetailModal() {
            document.getElementById('techRODetailModal').style.display = 'none';
        }

        function flagHours() {
            const total = parseFloat(document.getElementById('flaggedTotal').innerText);

            if (total <= 0) {
                alert("No hours selected.");
                return;
            }

            console.log("FLAGGING:", {
                tech: currentTech,
                ro: currentRO,
                hours: total
            });

            alert("Hours flagged successfully.");
            closeTechRODetailModal();
        }

        // Load cards on startup
        document.addEventListener("DOMContentLoaded", loadTechCards);

        </script>

    </div>
    """
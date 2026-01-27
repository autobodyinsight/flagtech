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
            <div id="techsTableContainer" style="width:100%; border:1px solid #ddd; border-radius:4px; overflow:hidden;">
                <!-- Header -->
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:2px solid #ddd; font-weight:bold; position:sticky; top:0;">
                    <div style="flex:1; text-align:left;">Tech Name</div>
                    <div style="flex:1; text-align:center;">Pay Rate</div>
                    <div style="flex:1; text-align:center;">Total RO's</div>
                    <div style="flex:1; text-align:right;">Total Hours</div>
                </div>
                <!-- Tech rows will be inserted here -->
                <div id="techsListContainer"></div>
            </div>
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
        // Toggle Tech Details Inline
        // -----------------------------
        function toggleTechDetails(techName) {
            const detailsId = `tech-details-${techName.replace(/\s+/g, '-')}`;
            const detailsSection = document.getElementById(detailsId);
            
            if (detailsSection.style.display === 'none') {
                // Load RO details when expanding
                loadTechDetailsInline(techName);
                detailsSection.style.display = 'block';
            } else {
                detailsSection.style.display = 'none';
                // Clear repair lines when collapsing
                const repairSection = document.getElementById(`repair-section-${techName.replace(/\s+/g, '-')}`);
                if (repairSection) {
                    repairSection.style.display = 'none';
                }
            }
        }

        function loadTechDetailsInline(techName) {
            const rosList = document.getElementById(`ros-list-${techName.replace(/\s+/g, '-')}`);
            
            if (rosList.innerHTML) return; // Already loaded

            // Use global variable that was set during loadTechsList
            if (window.techAssignmentsData && window.techAssignmentsData.tech_summary) {
                const res = window.techAssignmentsData;
                rosList.innerHTML = '';

                // Find the tech's assignments
                const techData = res.tech_summary.find(t => t.tech === techName);
                if (!techData || !techData.ros || techData.ros.length === 0) {
                    rosList.innerHTML = "<p style='text-align:center; color:#777;'>No RO assignments found for this technician.</p>";
                    return;
                }

                // Display each RO
                techData.ros.forEach(ro => {
                    const roDiv = document.createElement('div');
                    roDiv.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee; cursor:pointer;';
                    roDiv.onmouseover = function() { this.style.backgroundColor = '#f0f0f0'; };
                    roDiv.onmouseout = function() { this.style.backgroundColor = 'transparent'; };
                    
                    const roCell = document.createElement('div');
                    roCell.style.flex = "1";
                    roCell.style.textAlign = "left";
                    roCell.style.color = "#0066cc";
                    roCell.style.fontWeight = "bold";
                    roCell.style.cursor = "pointer";
                    roCell.textContent = ro.ro;
                    roCell.addEventListener('click', function(e) {
                        e.stopPropagation();
                        loadRepairLinesInline(techName, ro.ro);
                    });
                    
                    const vehicleCell = document.createElement('div');
                    vehicleCell.style.flex = "2";
                    vehicleCell.style.textAlign = "center";
                    vehicleCell.textContent = ro.vehicle_info;
                    
                    const hoursCell = document.createElement('div');
                    hoursCell.style.flex = "1";
                    hoursCell.style.textAlign = "right";
                    hoursCell.textContent = ro.total_hours.toFixed(1) + ' hrs';
                    
                    roDiv.appendChild(roCell);
                    roDiv.appendChild(vehicleCell);
                    roDiv.appendChild(hoursCell);
                    
                    rosList.appendChild(roDiv);
                });
            }
        }

        function loadRepairLinesInline(techName, roNumber) {
            const repairSection = document.getElementById(`repair-section-${techName.replace(/\s+/g, '-')}`);
            repairSection.innerHTML = '';
            
            const roHeader = document.createElement('div');
            roHeader.style.cssText = 'font-size:14px; font-weight:bold; margin-bottom:10px;';
            roHeader.textContent = `RO ${roNumber} - Repair Lines`;
            repairSection.appendChild(roHeader);

            fetch(`${BACKEND_BASE}/ui/tech-repair-lines?tech=${encodeURIComponent(techName)}&ro=${encodeURIComponent(roNumber)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.lines && data.lines.length > 0) {
                        const linesDiv = document.createElement('div');
                        linesDiv.style.marginLeft = "20px";
                        
                        data.lines.forEach(line => {
                            const lineItem = document.createElement('div');
                            lineItem.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:10px; border-left:3px solid #0066cc; background-color:#f9f9f9; margin-bottom:8px;';
                            
                            const typeCell = document.createElement('span');
                            typeCell.textContent = line.type;
                            typeCell.style.fontWeight = "bold";
                            typeCell.style.marginRight = "20px";
                            
                            const descCell = document.createElement('span');
                            descCell.textContent = line.description;
                            descCell.style.flex = "1";
                            
                            const hoursCell = document.createElement('span');
                            hoursCell.textContent = line.hours.toFixed(1) + ' hrs';
                            hoursCell.style.marginLeft = "20px";
                            
                            lineItem.appendChild(typeCell);
                            lineItem.appendChild(descCell);
                            lineItem.appendChild(hoursCell);
                            linesDiv.appendChild(lineItem);
                        });
                        
                        repairSection.appendChild(linesDiv);
                    } else {
                        const noLines = document.createElement('div');
                        noLines.textContent = 'No repair lines found for this RO';
                        noLines.style.color = '#999';
                        repairSection.appendChild(noLines);
                    }
                })
                .catch(err => {
                    console.error('Error loading repair lines:', err);
                    const error = document.createElement('div');
                    error.textContent = 'Error loading repair lines';
                    error.style.color = 'red';
                    repairSection.appendChild(error);
                });
            
            repairSection.style.display = 'block';
        }

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

                // Cache assignments data for inline use
                window.techAssignmentsData = assignmentsRes;

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

                    // Main tech row
                    const row = document.createElement('div');
                    row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee;';
                    row.className = 'tech-row';
                    
                    const techNameCell = document.createElement('div');
                    techNameCell.style.flex = "1";
                    techNameCell.style.textAlign = "left";
                    
                    const techLink = document.createElement('span');
                    techLink.textContent = fullName;
                    techLink.style.cursor = "pointer";
                    techLink.style.color = "#0066cc";
                    techLink.style.textDecoration = "underline";
                    techLink.style.fontWeight = "bold";
                    techLink.onclick = function(e) {
                        e.stopPropagation();
                        toggleTechDetails(fullName);
                    };
                    techNameCell.appendChild(techLink);
                    
                    const rateCell = document.createElement('div');
                    rateCell.style.flex = "1";
                    rateCell.style.textAlign = "center";
                    rateCell.textContent = `$${tech.pay_rate.toFixed(2)}/hr`;
                    
                    const rosCell = document.createElement('div');
                    rosCell.style.flex = "1";
                    rosCell.style.textAlign = "center";
                    rosCell.textContent = assignments.total_vehicles;
                    
                    const hoursCell = document.createElement('div');
                    hoursCell.style.flex = "1";
                    hoursCell.style.textAlign = "right";
                    hoursCell.textContent = assignments.total_hours.toFixed(1);
                    
                    row.appendChild(techNameCell);
                    row.appendChild(rateCell);
                    row.appendChild(rosCell);
                    row.appendChild(hoursCell);
                    
                    row.onmouseover = function() { this.style.backgroundColor = "#f5f5f5"; };
                    row.onmouseout = function() { this.style.backgroundColor = "transparent"; };

                    tableContainer.appendChild(row);

                    // Details section (hidden by default)
                    const detailsSection = document.createElement('div');
                    detailsSection.id = `tech-details-${fullName.replace(/\s+/g, '-')}`;
                    detailsSection.style.cssText = 'display:none; padding:20px; background-color:#f9f9f9; border-bottom:1px solid #eee;';
                    
                    const rosHeader = document.createElement('div');
                    rosHeader.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; background-color:#f5f5f5; border-bottom:1px solid #ddd; font-weight:bold; margin-bottom:10px;';
                    rosHeader.innerHTML = `
                        <div style="flex:1; text-align:left;">RO Number</div>
                        <div style="flex:2; text-align:center;">Vehicle Info</div>
                        <div style="flex:1; text-align:right;">Total Hours</div>
                    `;
                    detailsSection.appendChild(rosHeader);

                    const rosListDiv = document.createElement('div');
                    rosListDiv.id = `ros-list-${fullName.replace(/\s+/g, '-')}`;
                    rosListDiv.style.marginBottom = "20px";
                    detailsSection.appendChild(rosListDiv);

                    const repairLinesSection = document.createElement('div');
                    repairLinesSection.id = `repair-section-${fullName.replace(/\s+/g, '-')}`;
                    repairLinesSection.style.cssText = 'display:none; margin-top:20px; border-top:1px solid #ddd; padding-top:20px;';
                    detailsSection.appendChild(repairLinesSection);

                    tableContainer.appendChild(detailsSection);
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
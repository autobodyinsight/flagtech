"""RO's screen content for the FlagTech UI."""


def get_ros_screen_html():
    """Return the HTML content for the RO's screen."""
    return """
    <div id="ros" class="screen" style="padding:20px;">

        <h2>RO MANAGEMENT</h2>

        <hr style="margin:20px 0;">

        <!-- RO Cards -->
        <div id="roCardsContainer" style="display:flex; flex-wrap:wrap; gap:12px;">
        </div>

        <!-- RO Detail Modal -->
        <div id="roDetailModal" class="modal" style="display:none;">
            <div class="modal-content" style="max-width:800px;">
                <span class="close" onclick="closeRODetailModal()">&times;</span>
                <h3 id="roDetailTitle">RO Details</h3>
                
                <div id="roDetailContent" style="margin-top:20px;">
                    <h4>Labor Assignments</h4>
                    <div id="roLaborList"></div>
                    
                    <h4 style="margin-top:20px;">Refinish Assignments</h4>
                    <div id="roRefinishList"></div>
                </div>

                <div style="margin-top:20px; padding:10px; background:#f0f0f0; font-weight:bold;">
                    Total Hours: <span id="roTotalHours">0.0</span> hrs
                </div>
            </div>
        </div>

        <script>

        const BACKEND_BASE = "https://flagtech1.onrender.com";

        // -----------------------------
        // RO Summary Cards
        // -----------------------------
        window.loadROCards = function() {
            const container = document.getElementById('roCardsContainer');
            container.innerHTML = "<p style='color:#777;'>Loading...</p>";

            fetch(`${BACKEND_BASE}/ui/ros/summary`)
                .then(r => r.json())
                .then(res => {
                    container.innerHTML = "";

                    if (res.summary.length === 0) {
                        container.innerHTML = "<p style='color:#777;'>No RO activity yet.</p>";
                        return;
                    }

                    res.summary.forEach(ro => {
                        const card = document.createElement('div');
                        card.style.border = "1px solid #ccc";
                        card.style.borderRadius = "6px";
                        card.style.padding = "12px";
                        card.style.width = "250px";
                        card.style.cursor = "pointer";
                        card.style.background = "#f9f9f9";

                        card.onclick = () => openRODetail(ro.ro);

                        card.innerHTML = `
                            <div style="font-size:16px; font-weight:bold;">${ro.ro}</div>
                            <div style="margin-top:6px; font-size:14px; color:#555;">${ro.vehicle}</div>
                            <div style="margin-top:4px;">Techs: ${ro.tech_count}</div>
                            <div style="margin-top:4px;">Total Hours: ${ro.total_hours.toFixed(1)}</div>
                        `;

                        container.appendChild(card);
                    });
                })
                .catch(err => {
                    console.error("Error loading RO cards:", err);
                    container.innerHTML = "<p style='color:red;'>Error loading ROs</p>";
                });
        }

        // -----------------------------
        // RO Detail Modal
        // -----------------------------
        function openRODetail(roNumber) {
            document.getElementById('roDetailTitle').innerText = "RO: " + roNumber;
            document.getElementById('roDetailModal').style.display = 'block';

            fetch(`${BACKEND_BASE}/ui/ros/${encodeURIComponent(roNumber)}/details`)
                .then(r => r.json())
                .then(res => {
                    const laborContainer = document.getElementById('roLaborList');
                    const refinishContainer = document.getElementById('roRefinishList');
                    
                    laborContainer.innerHTML = "";
                    refinishContainer.innerHTML = "";
                    
                    let totalHours = 0;

                    // Display Labor Assignments
                    if (res.labor.length === 0) {
                        laborContainer.innerHTML = "<p style='color:#777;'>No labor assignments</p>";
                    } else {
                        res.labor.forEach(assignment => {
                            const div = document.createElement('div');
                            div.style.padding = "10px";
                            div.style.borderBottom = "1px solid #ddd";
                            div.style.marginBottom = "10px";

                            const assigned = JSON.parse(assignment.assigned);
                            const additional = JSON.parse(assignment.additional);
                            
                            let itemsHtml = "";
                            assigned.forEach(item => {
                                itemsHtml += `<div style="margin-left:20px;">• Line ${item.line}: ${item.description} - ${item.value.toFixed(1)} hrs</div>`;
                            });
                            
                            if (additional.length > 0) {
                                additional.forEach(item => {
                                    itemsHtml += `<div style="margin-left:20px; background:#fffacd; padding:2px;">• Additional: ${item.description} - ${item.value.toFixed(1)} hrs</div>`;
                                });
                            }

                            div.innerHTML = `
                                <strong>Tech: ${assignment.tech}</strong>
                                <div style="color:#555;">Vehicle: ${assignment.vehicle}</div>
                                <div style="margin-top:8px;">${itemsHtml}</div>
                                <div style="margin-top:8px; font-weight:bold;">Total Labor: ${assignment.total_labor.toFixed(1)} hrs</div>
                            `;

                            laborContainer.appendChild(div);
                            totalHours += parseFloat(assignment.total_labor);
                        });
                    }

                    // Display Refinish Assignments
                    if (res.refinish.length === 0) {
                        refinishContainer.innerHTML = "<p style='color:#777;'>No refinish assignments</p>";
                    } else {
                        res.refinish.forEach(assignment => {
                            const div = document.createElement('div');
                            div.style.padding = "10px";
                            div.style.borderBottom = "1px solid #ddd";
                            div.style.marginBottom = "10px";

                            const assigned = JSON.parse(assignment.assigned);
                            const additional = JSON.parse(assignment.additional);
                            
                            let itemsHtml = "";
                            assigned.forEach(item => {
                                itemsHtml += `<div style="margin-left:20px;">• Line ${item.line}: ${item.description} - ${item.value.toFixed(1)} hrs</div>`;
                            });
                            
                            if (additional.length > 0) {
                                additional.forEach(item => {
                                    itemsHtml += `<div style="margin-left:20px; background:#fffacd; padding:2px;">• Additional: ${item.description} - ${item.value.toFixed(1)} hrs</div>`;
                                });
                            }

                            div.innerHTML = `
                                <strong>Tech: ${assignment.tech}</strong>
                                <div style="color:#555;">Vehicle: ${assignment.vehicle}</div>
                                <div style="margin-top:8px;">${itemsHtml}</div>
                                <div style="margin-top:8px; font-weight:bold;">Total Paint: ${assignment.total_paint.toFixed(1)} hrs</div>
                            `;

                            refinishContainer.appendChild(div);
                            totalHours += parseFloat(assignment.total_paint);
                        });
                    }

                    document.getElementById('roTotalHours').innerText = totalHours.toFixed(1);
                })
                .catch(err => {
                    console.error("Error loading RO details:", err);
                    document.getElementById('roDetailContent').innerHTML = "<p style='color:red;'>Error loading RO details</p>";
                });
        }

        function closeRODetailModal() {
            document.getElementById('roDetailModal').style.display = 'none';
        }

        // Load cards on startup
        document.addEventListener("DOMContentLoaded", window.loadROCards);

        </script>

    </div>
    """

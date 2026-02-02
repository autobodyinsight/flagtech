"""Dashboard screen content for the FlagTech UI."""


def get_dashboard_screen_html():
    """Return the HTML content for the Dashboard screen."""
    return """
        <div id="dashboard" class="screen" style="padding:20px;">
            <h1 style="text-align:center; margin-bottom:30px;">DASHBOARD</h1>
            
            <div style="display:flex; gap:20px;">
                <!-- Left Side: Vertical Bars -->
                <div style="flex:0 0 300px; display:flex; flex-direction:column; gap:20px;">
                    <!-- Total Sales Bar -->
                    <div style="background:#f9f9f9; padding:20px; border-radius:8px; border:1px solid #ddd; flex:1; display:flex; flex-direction:column; height:calc((100% - 20px) / 2);">
                        <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Total Sales</h3>
                        <div style="position:relative; flex:1; background:#e0e0e0; border-radius:4px; overflow:hidden;">
                            <div id="totalSalesBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #4caf50, #81c784); transition:height 0.5s ease;">
                            </div>
                        </div>
                        <div id="totalSalesValue" style="text-align:center; font-size:20px; font-weight:bold; color:#4caf50; margin-top:10px;">
                            $0
                        </div>
                    </div>
                    
                    <!-- Pending Payments Bar -->
                    <div style="background:#f9f9f9; padding:20px; border-radius:8px; border:1px solid #ddd; flex:1; display:flex; flex-direction:column; height:calc((100% - 20px) / 2);">
                        <h3 style="margin:0 0 10px 0; text-align:center; color:#333;">Pending Payments</h3>
                        <div style="position:relative; flex:1; background:#e0e0e0; border-radius:4px; overflow:hidden;">
                            <div id="pendingPaymentsBar" style="position:absolute; bottom:0; width:100%; background:linear-gradient(to top, #ff9800, #ffb74d); transition:height 0.5s ease;">
                            </div>
                        </div>
                        <div id="pendingPaymentsValue" style="text-align:center; font-size:20px; font-weight:bold; color:#ff9800; margin-top:10px;">
                            $0
                        </div>
                    </div>
                </div>
                
                <!-- Right Side: 6 Display Cards in 2 Columns -->
                <div style="flex:1; display:grid; grid-template-columns:1fr 1fr; gap:20px; align-content:start;">
                    <!-- Current GP Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #2196f3; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Current GP</h4>
                        <div id="currentGP" style="font-size:32px; font-weight:bold; color:#2196f3;">
                            0%
                        </div>
                    </div>
                    
                    <!-- Parts Cost Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #e91e63; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Parts Cost</h4>
                        <div id="partsCost" style="font-size:32px; font-weight:bold; color:#e91e63;">
                            $0
                        </div>
                    </div>
                    
                    <!-- Average Hours Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #9c27b0; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Average Hrs</h4>
                        <div id="averageHrs" style="font-size:32px; font-weight:bold; color:#9c27b0;">
                            0.0
                        </div>
                    </div>
                    
                    <!-- Average RO Card -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #ff5722; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Average RO</h4>
                        <div id="averageRO" style="font-size:32px; font-weight:bold; color:#ff5722;">
                            $0
                        </div>
                    </div>
                    
                    <!-- Total Hrs per Tech - Pie Chart -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #00bcd4; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Total Hrs per Tech</h4>
                        <canvas id="hoursPerTechChart" style="max-height:150px;"></canvas>
                    </div>
                    
                    <!-- Total ROs per Tech - List View -->
                    <div style="background:#fff; padding:20px; border-radius:8px; border:2px solid #795548; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 15px 0; color:#666; font-size:14px;">Total ROs per Tech</h4>
                        <div id="rosPerTechList" style="max-height:150px; overflow-y:auto; font-size:14px;">
                            <div style="color:#999; text-align:center;">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Global variables for dashboard
            let dashboardData = null;
            let hoursPerTechChartInstance = null;
            
            // Check if BACKEND_BASE is already defined, if not, define it
            if (typeof BACKEND_BASE === 'undefined') {
                var BACKEND_BASE = "https://flagtech1.onrender.com";
            }
            
            // Load dashboard data
            async function loadDashboardData() {
                try {
                    const response = await fetch(BACKEND_BASE + '/api/dashboard-data');
                    const data = await response.json();
                    dashboardData = data;
                    updateDashboard(data);
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }
            }
            
            // Update all dashboard elements
            function updateDashboard(data) {
                // Update Total Sales bar and value
                const maxSales = Math.max(data.totalSales, data.pendingPayments, 10000); // minimum scale
                const salesPercent = (data.totalSales / maxSales) * 100;
                document.getElementById('totalSalesBar').style.height = salesPercent + '%';
                document.getElementById('totalSalesValue').innerText = '$' + data.totalSales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Pending Payments bar and value
                const pendingPercent = (data.pendingPayments / maxSales) * 100;
                document.getElementById('pendingPaymentsBar').style.height = pendingPercent + '%';
                document.getElementById('pendingPaymentsValue').innerText = '$' + data.pendingPayments.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Current GP
                document.getElementById('currentGP').innerText = data.currentGP.toFixed(1) + '%';
                
                // Update Parts Cost
                document.getElementById('partsCost').innerText = '$' + data.partsCost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Average Hours
                document.getElementById('averageHrs').innerText = data.averageHrs.toFixed(1);
                
                // Update Average RO
                document.getElementById('averageRO').innerText = '$' + data.averageRO.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                // Update Total Hrs per Tech - Pie Chart
                updateHoursPerTechChart(data.hoursPerTech);
                
                // Update Total ROs per Tech - List
                updateRosPerTechList(data.rosPerTech);
            }
            
            // Update pie chart for hours per tech
            function updateHoursPerTechChart(hoursPerTech) {
                const ctx = document.getElementById('hoursPerTechChart');
                
                if (!ctx) return;
                
                const labels = hoursPerTech.map(item => item.tech);
                const dataValues = hoursPerTech.map(item => item.hours);
                
                // Generate colors for each tech
                const colors = [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ];
                
                // Destroy existing chart if it exists
                if (hoursPerTechChartInstance) {
                    hoursPerTechChartInstance.destroy();
                }
                
                hoursPerTechChartInstance = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: dataValues,
                            backgroundColor: colors.slice(0, labels.length),
                            borderWidth: 2,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    font: {
                                        size: 10
                                    },
                                    padding: 8
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.label + ': ' + context.parsed.toFixed(1) + ' hrs';
                                    }
                                }
                            }
                        }
                    }
                });
            }
            
            // Update list for ROs per tech
            function updateRosPerTechList(rosPerTech) {
                const container = document.getElementById('rosPerTechList');
                
                if (rosPerTech.length === 0) {
                    container.innerHTML = '<div style="color:#999; text-align:center;">No data</div>';
                    return;
                }
                
                let html = '';
                rosPerTech.forEach(item => {
                    html += `
                        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #eee;">
                            <span style="color:#333;">${item.tech}</span>
                            <span style="font-weight:bold; color:#795548;">${item.ros}</span>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            // Load dashboard data when dashboard screen is shown
            // We'll call this from the switchScreen function
            window.loadDashboardDataIfNeeded = function() {
                // Check if dashboard screen is active
                const dashboardScreen = document.getElementById('dashboard');
                if (dashboardScreen && dashboardScreen.classList.contains('active')) {
                    loadDashboardData();
                }
            };
            
            // Load initially if dashboard is the first screen (unlikely but handle it)
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', loadDashboardDataIfNeeded);
            } else {
                loadDashboardDataIfNeeded();
            }
        </script>
    """

"""Setup screen content for the FlagTech UI."""


def get_setup_screen_html():
    """Return the HTML content for the Setup screen."""
    return """
    <div id="setup" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">SETUP</h1>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:20px;">
            <div style="border:1px solid #ddd; border-radius:8px; padding:20px; background:#fafafa;">
                <h3 style="margin-bottom:15px;">Add Technician</h3>
                <label>First:</label>
                <input type="text" id="setupTechFirst" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Last:</label>
                <input type="text" id="setupTechLast" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Rate:</label>
                <input type="number" step="0.01" id="setupTechRate" style="width:100%; padding:8px; margin-bottom:15px; box-sizing:border-box;">

                <button onclick="setupAddTech()" style="padding:10px 16px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Add Tech</button>

            </div>

            <div style="border:1px solid #ddd; border-radius:8px; padding:20px; background:#fafafa;">
                <h3 style="margin-bottom:15px;">Add Parts Vendor</h3>
                <label>Name:</label>
                <input type="text" id="setupVendorName" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Email:</label>
                <input type="email" id="setupVendorEmail" style="width:100%; padding:8px; margin-bottom:10px; box-sizing:border-box;">

                <label>Phone:</label>
                <input type="text" id="setupVendorPhone" style="width:100%; padding:8px; margin-bottom:15px; box-sizing:border-box;">

                <button onclick="setupAddVendor()" style="padding:10px 16px; background-color:#505050; color:white; border:none; border-radius:4px; cursor:pointer; font-size:14px;">Add Vendor</button>

            </div>
        </div>

        <hr style="margin:30px 0; border:none; border-top:1px solid #ddd;">

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:20px;">
            <div style="border:1px solid #ddd; border-radius:8px; padding:20px; background:#fff;">
                <h3 style="margin-bottom:15px;">Technicians</h3>
                <div id="setupTechsList"></div>
            </div>

            <div style="border:1px solid #ddd; border-radius:8px; padding:20px; background:#fff;">
                <h3 style="margin-bottom:15px;">Parts Vendors</h3>
                <div id="setupVendorsList"></div>
            </div>
        </div>
    </div>
    """


def get_setup_script():
    """Return the JavaScript for the Setup screen."""
    return """
        function setupAddTech() {
            const firstName = document.getElementById('setupTechFirst').value.trim();
            const lastName = document.getElementById('setupTechLast').value.trim();
            const rate = parseFloat(document.getElementById('setupTechRate').value);

            if (!firstName || !lastName || !rate) {
                alert('Please enter first name, last name, and rate.');
                return;
            }

            fetch('/api/techs/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    pay_rate: rate
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                document.getElementById('setupTechFirst').value = '';
                document.getElementById('setupTechLast').value = '';
                document.getElementById('setupTechRate').value = '';
                setupLoadTechs();
            })
            .catch(err => {
                console.error('Error saving tech:', err);
                alert('Error saving tech. Please try again.');
            });
        }

        function setupLoadTechs() {
            const container = document.getElementById('setupTechsList');
            if (!container) return;

            container.innerHTML = '<p style="color:#777;">Loading...</p>';
            fetch('/api/techs/list', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (!res.techs || res.techs.length === 0) {
                        container.innerHTML = '<p style="color:#777;">No techs added yet.</p>';
                        return;
                    }

                    container.innerHTML = res.techs.map(t => {
                        return `<div style="padding:8px 0; border-bottom:1px solid #eee;">${t.first_name} ${t.last_name} - $${t.pay_rate.toFixed(2)}/hr</div>`;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading techs:', err);
                    container.innerHTML = '<p style="color:red;">Error loading techs.</p>';
                });
        }

        function setupAddVendor() {
            const name = document.getElementById('setupVendorName').value.trim();
            const email = document.getElementById('setupVendorEmail').value.trim();
            const phone = document.getElementById('setupVendorPhone').value.trim();

            if (!name) {
                alert('Please enter a vendor name.');
                return;
            }

            fetch('/api/vendors/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ name, email, phone })
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    throw new Error(res.error);
                }
                document.getElementById('setupVendorName').value = '';
                document.getElementById('setupVendorEmail').value = '';
                document.getElementById('setupVendorPhone').value = '';
                setupLoadVendors();
            })
            .catch(err => {
                console.error('Error saving vendor:', err);
                alert('Error saving vendor. Please try again.');
            });
        }

        function setupLoadVendors() {
            const container = document.getElementById('setupVendorsList');
            if (!container) return;

            container.innerHTML = '<p style="color:#777;">Loading...</p>';
            fetch('/api/vendors/list', { credentials: 'include' })
                .then(r => r.json())
                .then(res => {
                    if (!res.vendors || res.vendors.length === 0) {
                        container.innerHTML = '<p style="color:#777;">No vendors added yet.</p>';
                        return;
                    }

                    container.innerHTML = res.vendors.map(v => {
                        const parts = [v.name];
                        if (v.email) parts.push(v.email);
                        if (v.phone) parts.push(v.phone);
                        return `<div style="padding:8px 0; border-bottom:1px solid #eee;">${parts.join(' • ')}</div>`;
                    }).join('');
                })
                .catch(err => {
                    console.error('Error loading vendors:', err);
                    container.innerHTML = '<p style="color:red;">Error loading vendors.</p>';
                });
        }
    """
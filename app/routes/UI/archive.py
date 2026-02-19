"""ARCHIVE window for historical data display in FlagTech UI."""

def get_archive_screen_html():
    """Return the HTML content for the ARCHIVE window."""
    return r'''
    <div id="archive" class="screen" style="padding:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
            <h1 style="text-align:center; margin:0; flex:1;">ARCHIVE</h1>
        </div>
        <div style="background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 18px 0; color:#333;">Closed Repair Orders</h3>
            <div style="overflow-x:auto;">
                <table id="archiveRoListTable" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr class="dashboard-header-row">
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">RO#</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">VEHICLE</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">TECH</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">PARTS</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">INSURANCE</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">CUSTOMER</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">IN</th>
                            <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; cursor:pointer; user-select:none;">PICKED UP</th>
                        </tr>
                    </thead>
                    <tbody id="archiveRoListBody">
                        <tr>
                            <td colspan="8" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <style>
            .dashboard-header-row th, .dashboard-header-cell {
                font-family: inherit;
                font-size: 16px;
                font-weight: bold;
                background: #23272a;
                color: #fff;
            }
        </style>
        <script>
        // Helper: get estimator name (same as dashboard)
        function getRoEstimatorName(ro) {
            let preferred = String(ro?.written_by || '').trim() || String(ro?.estimator || '').trim();
            if (!preferred) {
                const ownerInfo = String(ro?.owner_info || '').trim();
                if (ownerInfo) {
                    const writtenByMatch = ownerInfo.match(/written\s*by\s*:\s*([^\n,]+)/i);
                    if (writtenByMatch && writtenByMatch[1]) {
                        preferred = String(writtenByMatch[1]).trim();
                    }
                    if (!preferred) {
                        const estimatorMatch = ownerInfo.match(/estimator\s*:\s*([^\n,]+)/i);
                        if (estimatorMatch && estimatorMatch[1]) {
                            preferred = String(estimatorMatch[1]).trim();
                        }
                    }
                }
            }
            return preferred || '—';
        }

        // Load closed ROs from dashboard data (auto-archive logic)
        async function loadArchiveClosedRos() {
            try {
                const resp = await fetch('/api/dashboard-data', { credentials: 'include' });
                const data = await resp.json();
                const allRos = Array.isArray(data.roList) ? data.roList : [];
                // Closed = status is 'closed' (regardless of picked_up date)
                const closedRos = allRos.filter(ro => String(ro.status).toLowerCase() === 'closed');
                const body = document.getElementById('archiveRoListBody');
                body.innerHTML = '';
                if (!closedRos.length) {
                    body.innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#999;'>No closed repair orders found.</td></tr>`;
                    return;
                }
                for (const ro of closedRos) {
                    const estimator = getRoEstimatorName(ro);
                    body.innerHTML += `<tr>
                        <td style='padding:12px;'>${ro.ro || ''}</td>
                        <td style='padding:12px;'>${ro.vehicle || ''}</td>
                        <td style='padding:12px;'>${estimator}</td>
                        <td style='padding:12px;'>${ro.parts || ''}</td>
                        <td style='padding:12px;'>${ro.insurance || ''}</td>
                        <td style='padding:12px;'>${ro.customer || ''}</td>
                        <td style='padding:12px;'>${ro.in_date || ''}</td>
                        <td style='padding:12px;'>${ro.picked_up || ''}</td>
                    </tr>`;
                }
            } catch (e) {
                document.getElementById('archiveRoListBody').innerHTML = `<tr><td colspan='8' style='padding:20px; text-align:center; color:#c00;'>Error loading data</td></tr>`;
            }
        }
        document.addEventListener('DOMContentLoaded', loadArchiveClosedRos);
        </script>
    </div>
    '''

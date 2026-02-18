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
                background: #f5f5f5;
            }
        </style>
        <script>
            // Clickable column behaviors
            document.addEventListener('DOMContentLoaded', function() {
                const table = document.getElementById('archiveRoListTable');
                if (!table) return;
                table.addEventListener('click', function(e) {
                    const cell = e.target.closest('td,th');
                    if (!cell) return;
                    const row = cell.parentElement;
                    if (row.rowIndex === 0) return; // skip header
                    const colIndex = cell.cellIndex;
                    // Implement slide-down/modal behaviors here
                    // RO#: colIndex 0
                    // TECH: colIndex 2
                    // PARTS: colIndex 3
                    // INSURANCE: colIndex 4
                    // CUSTOMER: colIndex 5
                    // PICKED UP: colIndex 7
                    // Example:
                    if (colIndex === 0) {
                        alert('Show notes for RO# ' + row.cells[0].innerText);
                    } else if (colIndex === 2) {
                        alert('Show tech details for ' + row.cells[2].innerText);
                    } else if (colIndex === 3) {
                        alert('Show parts invoices for RO# ' + row.cells[0].innerText);
                    } else if (colIndex === 4) {
                        alert('Show insurance log for RO# ' + row.cells[0].innerText);
                    } else if (colIndex === 5) {
                        alert('Show customer log for RO# ' + row.cells[0].innerText);
                    } else if (colIndex === 7) {
                        alert('Re-Open RO modal for RO# ' + row.cells[0].innerText);
                    }
                });
            });
        </script>
    </div>
    '''

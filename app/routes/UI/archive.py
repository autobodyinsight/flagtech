"""ARCHIVE window for historical data display in FlagTech UI."""

def get_archive_screen_html():
    """Return the HTML content for the ARCHIVE window."""
    return r'''
    <div id="archive" class="screen" style="padding:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; gap:20px;">
            <h1 style="text-align:center; margin:0; flex:1;">ARCHIVE</h1>
        </div>
        <div style="display:flex; height:80vh;">
            <!-- Left Control Pane -->
            <div style="width:220px; background:#23272a; color:#fff; border-radius:8px 0 0 8px; display:flex; flex-direction:column; align-items:stretch; padding:0;">
                <div id="archive-tab-ros" class="archive-tab active" onclick="switchArchiveTab('ros')">RO'S</div>
                <div id="archive-tab-techs" class="archive-tab" onclick="switchArchiveTab('techs')">TECHS</div>
                <div id="archive-tab-invoices" class="archive-tab" onclick="switchArchiveTab('invoices')">INVOICES</div>
                <div id="archive-tab-payments" class="archive-tab" onclick="switchArchiveTab('payments')">PAYMENTS</div>
            </div>
            <!-- Main Content Area -->
            <div id="archive-content" style="flex:1; background:#f2f0ef; border-radius:0 8px 8px 0; padding:32px; overflow-y:auto;">
                <div id="archive-ros-list" class="archive-content-section active">
                    <!-- Closed ROs list will be loaded here -->
                    <div style="font-size:18px; color:#333;">Closed Repair Orders will appear here.</div>
                </div>
                <div id="archive-techs-list" class="archive-content-section" style="display:none;">
                    <!-- Deactivated techs list -->
                    <div style="font-size:18px; color:#333;">Deactivated Technicians will appear here.</div>
                </div>
                <div id="archive-invoices-list" class="archive-content-section" style="display:none;">
                    <!-- Invoices for closed ROs -->
                    <div style="font-size:18px; color:#333;">Invoices for Closed ROs will appear here.</div>
                </div>
                <div id="archive-payments-list" class="archive-content-section" style="display:none;">
                    <!-- Payments for closed ROs -->
                    <div style="font-size:18px; color:#333;">Payments for Closed ROs will appear here.</div>
                </div>
            </div>
        </div>
        <style>
            .archive-tab {
                padding: 22px 0;
                text-align: center;
                font-weight: bold;
                font-size: 16px;
                border-bottom: 1px solid #444;
                cursor: pointer;
                background: #23272a;
                color: #fff;
                transition: background 0.2s, color 0.2s;
            }
            .archive-tab.active {
                background: #444950;
                color: #ffb300;
            }
            .archive-content-section {
                display: none;
            }
            .archive-content-section.active {
                display: block;
            }
        </style>
        <script>
            function switchArchiveTab(tab) {
                const tabs = ['ros', 'techs', 'invoices', 'payments'];
                tabs.forEach(t => {
                    document.getElementById('archive-tab-' + t).classList.remove('active');
                    document.getElementById('archive-' + t + '-list').style.display = 'none';
                });
                document.getElementById('archive-tab-' + tab).classList.add('active');
                document.getElementById('archive-' + tab + '-list').style.display = 'block';
            }
        </script>
    </div>
    '''

"""Phase screen content for the FlagTech UI."""


def get_phase_screen_html():
    """Return the HTML content for the Phase screen."""
    return """
    <div id="phase" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">PHASE</h1>

        <div style="display:grid; grid-template-columns:repeat(9, minmax(140px, 1fr)); gap:12px; align-items:start;">
            <div class="phase-column">
                <div class="phase-header">Teardown</div>
                <div id="phase-teardown" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Auth</div>
                <div id="phase-auth" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Parts</div>
                <div id="phase-parts" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Body</div>
                <div id="phase-body" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Refinish</div>
                <div id="phase-refinish" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Reassy</div>
                <div id="phase-reassy" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Sublet</div>
                <div id="phase-sublet" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Wash/QC</div>
                <div id="phase-washqc" class="phase-cards"></div>
            </div>
            <div class="phase-column">
                <div class="phase-header">Complete/Finish</div>
                <div id="phase-complete" class="phase-cards"></div>
            </div>
        </div>

        <style>
            .phase-column {
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                min-height: 200px;
            }
            .phase-header {
                font-weight: bold;
                padding: 10px 8px;
                border-bottom: 2px solid #eee;
                margin-bottom: 10px;
                text-align: center;
                background: #f7f7f7;
                border-radius: 6px;
            }
            .phase-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                background: #fafafa;
                font-size: 12px;
            }
            .phase-card .ro {
                font-weight: bold;
                color: #333;
                margin-bottom: 4px;
            }
            .phase-card .vehicle {
                color: #555;
                margin-bottom: 6px;
            }
            .phase-card .meta {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 4px 8px;
                font-size: 11px;
                color: #666;
            }
            .phase-cards {
                min-height: 140px;
            }
        </style>

        <script>
            function clearPhaseColumns() {
                const columns = [
                    'phase-teardown', 'phase-auth', 'phase-parts', 'phase-body', 'phase-refinish',
                    'phase-reassy', 'phase-sublet', 'phase-washqc', 'phase-complete'
                ];
                columns.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.innerHTML = '';
                });
            }

            function phaseColumnFor(phase) {
                const key = (phase || '').toLowerCase();
                if (key === 'auth') return 'phase-auth';
                if (key === 'parts') return 'phase-parts';
                if (key === 'body') return 'phase-body';
                if (key === 'refinish') return 'phase-refinish';
                if (key === 'reassy') return 'phase-reassy';
                if (key === 'sublet') return 'phase-sublet';
                if (key === 'wash/qc' || key === 'washqc') return 'phase-washqc';
                if (key === 'complete/finish' || key === 'complete') return 'phase-complete';
                return 'phase-teardown';
            }

            function renderPhaseCards(items) {
                clearPhaseColumns();

                if (!items || items.length === 0) {
                    const teardown = document.getElementById('phase-teardown');
                    if (teardown) {
                        teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">No repair orders found</div>';
                    }
                    return;
                }

                items.forEach(item => {
                    const colId = phaseColumnFor(item.phase);
                    const col = document.getElementById(colId);
                    if (!col) return;

                    const card = document.createElement('div');
                    card.className = 'phase-card';
                    card.innerHTML = `
                        <div class="ro">RO# ${item.ro || '—'}</div>
                        <div class="vehicle">${item.vehicle || '—'}</div>
                        <div class="meta">
                            <div><strong>Tech:</strong> ${item.tech || '—'}</div>
                            <div><strong>Labor:</strong> ${item.labor_hours?.toFixed ? item.labor_hours.toFixed(1) : (item.labor_hours || 0)} hrs</div>
                            <div><strong>Total:</strong> ${item.total_hours?.toFixed ? item.total_hours.toFixed(1) : (item.total_hours || 0)} hrs</div>
                            <div><strong>Days In:</strong> ${item.days_in ?? '—'}</div>
                            <div><strong>ECD:</strong> ${item.ecd || '—'}</div>
                        </div>
                    `;
                    col.appendChild(card);
                });
            }

            function loadPhaseData() {
                fetch('/api/phase-data', { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        renderPhaseCards(res.items || []);
                    })
                    .catch(err => {
                        console.error('Error loading phase data:', err);
                        clearPhaseColumns();
                        const teardown = document.getElementById('phase-teardown');
                        if (teardown) {
                            teardown.innerHTML = '<div style="color:red; text-align:center; padding:10px;">Error loading data</div>';
                        }
                    });
            }
        </script>
    </div>
    """

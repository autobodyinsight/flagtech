"""Phase screen content for the FlagTech UI."""


def get_phase_screen_html():
    """Return the HTML content for the Phase screen."""
    return """
    <div id="phase" class="screen" style="padding:20px;">
        <h1 style="text-align:center; margin-bottom:20px;">ROADMAP</h1>

        <div class="phase-board" style="display:grid; grid-template-columns:repeat(9, minmax(140px, 1fr)); gap:12px; align-items:start;">
            <div class="phase-lane">
                <div class="phase-header">Teardown <span class="phase-count" id="phase-count-teardown">0</span></div>
                <div id="phase-teardown" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Auth <span class="phase-count" id="phase-count-auth">0</span></div>
                <div id="phase-auth" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Parts <span class="phase-count" id="phase-count-parts">0</span></div>
                <div id="phase-parts" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Body <span class="phase-count" id="phase-count-body">0</span></div>
                <div id="phase-body" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Refinish <span class="phase-count" id="phase-count-refinish">0</span></div>
                <div id="phase-refinish" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Reassy <span class="phase-count" id="phase-count-reassy">0</span></div>
                <div id="phase-reassy" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Sublet <span class="phase-count" id="phase-count-sublet">0</span></div>
                <div id="phase-sublet" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Wash/QC <span class="phase-count" id="phase-count-washqc">0</span></div>
                <div id="phase-washqc" class="phase-cards"></div>
            </div>
            <div class="phase-lane">
                <div class="phase-header">Done <span class="phase-count" id="phase-count-complete">0</span></div>
                <div id="phase-complete" class="phase-cards"></div>
            </div>
        </div>

        <style>
            .phase-lane {
                position: relative;
                min-height: 200px;
                padding: 0 12px;
            }
            .phase-lane:not(:last-child)::after {
                content: '';
                position: absolute;
                top: 10px;
                bottom: 10px;
                right: -6px;
                width: 1px;
                background: rgba(0, 0, 0, 0.12);
            }
            .phase-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                color: #222;
                font-weight: 700;
                font-size: 12px;
                letter-spacing: 0.4px;
                text-transform: uppercase;
                padding: 0 2px 8px;
                margin: 6px 0 12px;
                border-bottom: 2px solid #b22222;
            }
            .phase-count {
                display: inline-block;
                margin-left: 8px;
                padding: 0;
                font-size: 12px;
                font-weight: 700;
                color: #b22222;
            }
            .phase-card {
                border: 1.5px solid #e0e0e0;
                border-radius: 12px;
                padding: 0;
                margin-bottom: 14px;
                background: #fff;
                font-size: 13px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.07);
                overflow: hidden;
                transition: box-shadow 0.18s;
            }
            .phase-card:hover {
                box-shadow: 0 4px 16px rgba(0,0,0,0.13);
            }
            .phase-card .ro-bar {
                font-weight: bold;
                color: #fff;
                padding: 8px 0 8px 0;
                text-align: center;
                font-size: 15px;
                letter-spacing: 1px;
                background: var(--ro-bar-color, #00BFFF);
                border-bottom: 1.5px solid #e0e0e0;
                transition: background 0.2s;
            }
            .phase-card .vehicle {
                color: #222;
                font-weight: 500;
                padding: 10px 12px 0 12px;
                font-size: 14px;
                margin-bottom: 2px;
            }
            .phase-card .meta {
                display: flex;
                flex-direction: column;
                gap: 2px;
                font-size: 12px;
                color: #444;
                padding: 0 12px 10px 12px;
            }
            .phase-cards {
                min-height: 140px;
                padding-bottom: 10px;
            }
            .phase-cards.drag-over {
                outline: 2px dashed #4caf50;
                outline-offset: 4px;
                background: #f3fff3;
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

                const counts = [
                    'phase-count-teardown', 'phase-count-auth', 'phase-count-parts', 'phase-count-body',
                    'phase-count-refinish', 'phase-count-reassy', 'phase-count-sublet',
                    'phase-count-washqc', 'phase-count-complete'
                ];
                counts.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = '0';
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

                const tally = {
                    teardown: 0,
                    auth: 0,
                    parts: 0,
                    body: 0,
                    refinish: 0,
                    reassy: 0,
                    sublet: 0,
                    washqc: 0,
                    complete: 0
                };

                // Pie chart colors from dashboard
                const roBarColors = [
                    '#00BFFF', // blue
                    '#FF8C00', // orange
                    '#32CD32', // green
                    '#FFD700', // yellow
                    '#40E0D0', // turquoise
                    '#8A2BE2', // purple
                    '#708090'  // slate
                ];
                items.forEach((item, idx) => {
                    const colId = phaseColumnFor(item.phase);
                    const col = document.getElementById(colId);
                    if (!col) return;

                    const phaseKey = colId.replace('phase-', '');
                    if (tally[phaseKey] !== undefined) {
                        tally[phaseKey] += 1;
                    }

                    const card = document.createElement('div');
                    card.className = 'phase-card';
                    card.setAttribute('draggable', 'true');
                    card.dataset.ro = item.ro || '';
                    card.dataset.phase = item.phase || 'teardown';
                    // Assign color from pie chart palette
                    const roBarColor = roBarColors[idx % roBarColors.length];
                    card.innerHTML = `
                        <div class="ro-bar" style="background:${roBarColor}">RO# ${item.ro || '—'}</div>
                        <div class="vehicle">${item.vehicle || '—'}</div>
                        <div class="meta">
                            <div>TECH: ${item.labor_tech || 'Unassigned'}</div>
                            <div>ESTIMATOR: ${item.estimator || '—'}</div>
                        </div>
                    `;
                    card.addEventListener('dragstart', (event) => {
                        event.dataTransfer.setData('text/plain', JSON.stringify({
                            ro: card.dataset.ro,
                            from: card.dataset.phase
                        }));
                    });
                    col.appendChild(card);
                });

                Object.keys(tally).forEach(key => {
                    const countEl = document.getElementById(`phase-count-${key}`);
                    if (countEl) {
                        countEl.textContent = String(tally[key]);
                    }
                });

                wirePhaseDropZones();
            }

            function wirePhaseDropZones() {
                const zones = document.querySelectorAll('.phase-cards');
                zones.forEach(zone => {
                    zone.addEventListener('dragover', (event) => {
                        event.preventDefault();
                        zone.classList.add('drag-over');
                    });
                    zone.addEventListener('dragleave', () => {
                        zone.classList.remove('drag-over');
                    });
                    zone.addEventListener('drop', (event) => {
                        event.preventDefault();
                        zone.classList.remove('drag-over');
                        const payload = event.dataTransfer.getData('text/plain');
                        if (!payload) return;
                        let data;
                        try {
                            data = JSON.parse(payload);
                        } catch (e) {
                            return;
                        }
                        const ro = data.ro;
                        if (!ro) return;
                        const targetPhase = zone.id.replace('phase-', '');
                        updatePhase(ro, targetPhase);
                    });
                });
            }

            function updatePhase(ro, phaseKey) {
                fetch('/api/phase/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ ro, phase: phaseKey })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    loadPhaseData();
                    if (typeof loadDashboardData === 'function') {
                        loadDashboardData();
                    }
                })
                .catch(err => {
                    console.error('Error updating phase:', err);
                    loadPhaseData();
                });
            }

            function loadPhaseData() {
                clearPhaseColumns();
                const teardown = document.getElementById('phase-teardown');
                if (teardown) {
                    teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">Loading...</div>';
                }

                fetch('/api/phase/board', { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        renderPhaseCards(res.items || []);
                    })
                    .catch(err => {
                        console.error('Error loading phase data:', err);
                        if (teardown) {
                            teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">Unable to load phase board</div>';
                        }
                    });
            }
        </script>
    </div>
    """

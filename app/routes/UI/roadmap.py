def get_roadmap_screen_html():
    """Return the HTML content for the Roadmap screen."""
    return """
    <div id='roadmap' class='screen' style='padding:20px;'>
        <h1 style='text-align:center; margin-bottom:20px;'>ROADMAP</h1>

        <div class='roadmap-columns'>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Teardown <span class='roadmap-count' id='roadmap-count-teardown'>0</span></div>
                <div id='roadmap-teardown' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Parts <span class='roadmap-count' id='roadmap-count-parts'>0</span></div>
                <div id='roadmap-parts' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Body <span class='roadmap-count' id='roadmap-count-body'>0</span></div>
                <div id='roadmap-body' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Refinish <span class='roadmap-count' id='roadmap-count-refinish'>0</span></div>
                <div id='roadmap-refinish' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Reassy <span class='roadmap-count' id='roadmap-count-reassy'>0</span></div>
                <div id='roadmap-reassy' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Sublet <span class='roadmap-count' id='roadmap-count-sublet'>0</span></div>
                <div id='roadmap-sublet' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Wash/QC <span class='roadmap-count' id='roadmap-count-washqc'>0</span></div>
                <div id='roadmap-washqc' class='roadmap-cards'></div>
            </div>

            <div class='roadmap-column'>
                <div class='roadmap-header'>Complete <span class='roadmap-count' id='roadmap-count-complete'>0</span></div>
                <div id='roadmap-complete' class='roadmap-cards'></div>
            </div>

        </div>

        <style>
            .roadmap-column {
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                min-height: 200px;
            }
            .roadmap-header {
                font-weight: bold;
                padding: 10px 8px;
                border-bottom: 2px solid #eee;
                margin-bottom: 10px;
                text-align: center;
                background: #f7f7f7;
                border-radius: 6px;
            }
            .roadmap-count {
                display: inline-block;
                margin-left: 6px;
                padding: 2px 6px;
                font-size: 11px;
                border-radius: 10px;
                background: #e0e0e0;
                color: #333;
            }
            .roadmap-card {
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
            .roadmap-card:hover {
                box-shadow: 0 4px 16px rgba(0,0,0,0.13);
            }
            .roadmap-card .ro-bar {
                font-weight: bold;
                color: #fff;
                padding: 8px 0;
                text-align: center;
                font-size: 15px;
                letter-spacing: 1px;
                background: var(--ro-bar-color, #00BFFF);
                border-bottom: 1.5px solid #e0e0e0;
                transition: background 0.2s;
            }
            .roadmap-card .vehicle {
                color: #222;
                font-weight: 500;
                padding: 10px 12px 0 12px;
                font-size: 14px;
                margin-bottom: 2px;
            }
            .roadmap-card .meta {
                display: flex;
                flex-direction: column;
                gap: 2px;
                font-size: 12px;
                color: #444;
                padding: 0 12px 10px 12px;
            }
            .roadmap-cards {
                min-height: 140px;
                padding-bottom: 10px;
            }
            .roadmap-cards.drag-over {
                outline: 2px dashed #4caf50;
                outline-offset: 4px;
                background: #f3fff3;
            }
        </style>

        <script>
            function clearroadmapColumns() {
                const columns = [
                    'roadmap-teardown', 'roadmap-auth', 'roadmap-parts', 'roadmap-body',
                    'roadmap-refinish', 'roadmap-reassy', 'roadmap-sublet',
                    'roadmap-washqc', 'roadmap-complete'
                ];
                columns.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.innerHTML = '';
                });

                const counts = [
                    'roadmap-count-teardown', 'roadmap-count-auth', 'roadmap-count-parts',
                    'roadmap-count-body', 'roadmap-count-refinish', 'roadmap-count-reassy',
                    'roadmap-count-sublet', 'roadmap-count-washqc', 'roadmap-count-complete'
                ];
                counts.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = '0';
                });
            }

            function roadmapColumnFor(roadmap) {
                const key = (roadmap || '').toLowerCase();
                if (key === 'auth') return 'roadmap-auth';
                if (key === 'parts') return 'roadmap-parts';
                if (key === 'body') return 'roadmap-body';
                if (key === 'refinish') return 'roadmap-refinish';
                if (key === 'reassy') return 'roadmap-reassy';
                if (key === 'sublet') return 'roadmap-sublet';
                if (key === 'wash/qc' || key === 'washqc') return 'roadmap-washqc';
                if (key === 'complete/finish' || key === 'complete') return 'roadmap-complete';
                return 'roadmap-teardown';
            }

            function renderroadmapCards(items) {
                clearroadmapColumns();

                if (!items || items.length === 0) {
                    const teardown = document.getElementById('roadmap-teardown');
                    if (teardown) {
                        teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">No repair orders found</div>';
                    }
                    return;
                }

                const tally = {
                    teardown: 0, auth: 0, parts: 0, body: 0,
                    refinish: 0, reassy: 0, sublet: 0,
                    washqc: 0, complete: 0
                };

                const roBarColors = [
                    '#00BFFF', '#FF8C00', '#32CD32',
                    '#FFD700', '#40E0D0', '#8A2BE2', '#708090'
                ];

                function getRoEstimatorName(item) {
                    let preferred = String(item?.written_by || '').trim() || String(item?.estimator || '').trim();
                    if (!preferred) {
                        const ownerInfo = String(item?.owner_info || '').trim();
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

                items.forEach((item, idx) => {
                    const colId = roadmapColumnFor(item.roadmap);
                    const col = document.getElementById(colId);
                    if (!col) return;

                    const roadmapKey = colId.replace('roadmap-', '');
                    if (tally[roadmapKey] !== undefined) {
                        tally[roadmapKey] += 1;
                    }

                    const card = document.createElement('div');
                    card.className = 'roadmap-card';
                    card.setAttribute('draggable', 'true');
                    card.dataset.ro = item.ro || '';
                    card.dataset.roadmap = item.roadmap || 'teardown';

                    const roBarColor = roBarColors[idx % roBarColors.length];
                    const estimatorName = getRoEstimatorName(item);

                    card.innerHTML = `
                        <div class="ro-bar" style="background:${roBarColor}">RO# ${item.ro || '—'}</div>
                        <div class="vehicle">${item.vehicle || '—'}</div>
                        <div class="meta">
                            <div>TECH: ${item.labor_tech || 'Unassigned'}</div>
                            <div>Estimator: ${estimatorName}</div>
                        </div>
                    `;

                    card.addEventListener('dragstart', (event) => {
                        event.dataTransfer.setData('text/plain', JSON.stringify({
                            ro: card.dataset.ro,
                            from: card.dataset.roadmap
                        }));
                    });

                    col.appendChild(card);
                });

                Object.keys(tally).forEach(key => {
                    const countEl = document.getElementById(`roadmap-count-${key}`);
                    if (countEl) {
                        countEl.textContent = String(tally[key]);
                    }
                });

                wireroadmapDropZones();
            }

            function wireroadmapDropZones() {
                const zones = document.querySelectorAll('.roadmap-cards');
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
                        const targetroadmap = zone.id.replace('roadmap-', '');
                        updateroadmap(ro, targetroadmap);
                    });
                });
            }

            function updateroadmap(ro, roadmapKey) {
                fetch('/api/roadmap/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ ro, roadmap: roadmapKey })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        throw new Error(res.error);
                    }
                    loadroadmapData();
                    if (typeof loadDashboardData === 'function') {
                        loadDashboardData();
                    }
                })
                .catch(err => {
                    console.error('Error updating roadmap:', err);
                    loadroadmapData();
                });
            }

            function loadroadmapData() {
                clearroadmapColumns();
                const teardown = document.getElementById('roadmap-teardown');
                if (teardown) {
                    teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">Loading...</div>';
                }

                fetch('/api/roadmap/board', { credentials: 'include' })
                    .then(r => r.json())
                    .then(res => {
                        if (res.error) {
                            throw new Error(res.error);
                        }
                        renderroadmapCards(res.items || []);
                    })
                    .catch(err => {
                        console.error('Error loading roadmap data:', err);
                        if (teardown) {
                            teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">Unable to load roadmap board</div>';
                        }
                    });
            }
        </script>
    </div>
    """
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
            .phase-card .meta-block {
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid #ececec;
            }
            .phase-mini-modal {
                position: fixed;
                z-index: 2500;
                width: min(300px, calc(100vw - 24px));
                background: #fff;
                border: 1px solid #d8d8d8;
                border-radius: 10px;
                box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22);
                padding: 10px;
            }
            .phase-mini-modal h3 {
                margin: 0 0 8px;
                font-size: 13px;
                color: #222;
                letter-spacing: 0.4px;
                text-transform: uppercase;
            }
            .phase-mini-modal .phase-form-row {
                display: flex;
                flex-direction: column;
                margin-bottom: 7px;
            }
            .phase-mini-modal label {
                font-size: 11px;
                font-weight: 700;
                color: #555;
                margin-bottom: 2px;
            }
            .phase-mini-modal input {
                border: 1px solid #cfcfcf;
                border-radius: 5px;
                padding: 6px 7px;
                font-size: 12px;
            }
            .phase-mini-modal .phase-actions {
                margin-top: 10px;
                display: flex;
                justify-content: flex-end;
                gap: 6px;
            }
            .phase-mini-modal .phase-btn {
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: 700;
                padding: 6px 10px;
                cursor: pointer;
            }
            .phase-mini-modal .phase-btn-cancel {
                background: #ececec;
                color: #333;
            }
            .phase-mini-modal .phase-btn-save {
                background: #b22222;
                color: #fff;
            }
        </style>

        <script>
            const PHASE_SPECIAL_SHOP = 'The Spray Gun Auto Body';
            let phaseBoardItems = [];
            let phaseEditModalEl = null;

            function getPhaseSessionSnapshot() {
                if (window.appUiState && window.appUiState.sessionSnapshot) {
                    return window.appUiState.sessionSnapshot;
                }
                try {
                    const raw = sessionStorage.getItem('flagtechSessionSnapshot');
                    return raw ? JSON.parse(raw) : null;
                } catch (_) {
                    return null;
                }
            }

            function isPhaseSpecialShop() {
                const sessionSnapshot = getPhaseSessionSnapshot() || {};
                const currentShopName = String(
                    sessionSnapshot.shop_name || sessionSnapshot?.shop?.shop_name || ''
                ).trim();
                return currentShopName === PHASE_SPECIAL_SHOP;
            }

            function phaseEscapeHtml(value) {
                return String(value === null || value === undefined ? '' : value)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }

            function phaseDisplayValue(value) {
                const normalized = String(value || '').trim();
                return normalized || '—';
            }

            function closePhaseEditModal() {
                if (phaseEditModalEl && phaseEditModalEl.parentNode) {
                    phaseEditModalEl.parentNode.removeChild(phaseEditModalEl);
                }
                phaseEditModalEl = null;
            }

            async function savePhaseModalChanges() {
                if (!phaseEditModalEl || !isPhaseSpecialShop()) return;

                const originalRoKey = String(phaseEditModalEl.dataset.originalRoKey || '').trim();
                const roInput = document.getElementById('phaseEditRoNumber');
                const customerInput = document.getElementById('phaseEditCustomerName');
                const unitInput = document.getElementById('phaseEditUnitNumber');
                const vehicleTypeInput = document.getElementById('phaseEditVehicleType');
                const locationInput = document.getElementById('phaseEditLocation');

                const nextRo = String(roInput?.value || '').trim();
                if (!nextRo) {
                    alert('RO number is required.');
                    roInput?.focus();
                    return;
                }

                const index = phaseBoardItems.findIndex((entry) => String(entry.ro_key || entry.ro || '').trim() === originalRoKey);
                if (index < 0) {
                    closePhaseEditModal();
                    return;
                }

                const payload = {
                    ro_key: originalRoKey,
                    ro: nextRo,
                    customer: String(customerInput?.value || '').trim(),
                    unit_number: String(unitInput?.value || '').trim(),
                    vehicle_type: String(vehicleTypeInput?.value || '').trim(),
                    location: String(locationInput?.value || '').trim(),
                };

                try {
                    const response = await fetch('/api/phase/roadmap-edit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(payload),
                    });
                    const result = await response.json();
                    if (!response.ok || result.error) {
                        throw new Error(result.error || 'Unable to save roadmap edit');
                    }
                    closePhaseEditModal();
                    loadPhaseData();
                } catch (error) {
                    alert(error?.message || 'Unable to save roadmap edit.');
                }
            }

            function openPhaseEditModal(anchorEl, roValue) {
                if (!isPhaseSpecialShop() || !anchorEl) return;
                const match = phaseBoardItems.find((entry) => String(entry.ro_key || entry.ro || '').trim() === String(roValue || '').trim());
                if (!match) return;

                closePhaseEditModal();

                const modal = document.createElement('div');
                modal.className = 'phase-mini-modal';
                modal.dataset.originalRoKey = String(match.ro_key || match.ro || '').trim();
                modal.innerHTML = `
                    <h3>Edit RO</h3>
                    <div class="phase-form-row">
                        <label for="phaseEditRoNumber">RO number</label>
                        <input id="phaseEditRoNumber" type="text" value="${phaseEscapeHtml(match.ro || '')}" />
                    </div>
                    <div class="phase-form-row">
                        <label for="phaseEditCustomerName">Customer name</label>
                        <input id="phaseEditCustomerName" type="text" value="${phaseEscapeHtml(match.customer || '')}" />
                    </div>
                    <div class="phase-form-row">
                        <label for="phaseEditUnitNumber">Unit #</label>
                        <input id="phaseEditUnitNumber" type="text" value="${phaseEscapeHtml(match.unit_number || '')}" />
                    </div>
                    <div class="phase-form-row">
                        <label for="phaseEditVehicleType">Vehicle type</label>
                        <input id="phaseEditVehicleType" type="text" value="${phaseEscapeHtml(match.vehicle_type || '')}" />
                    </div>
                    <div class="phase-form-row">
                        <label for="phaseEditLocation">Location</label>
                        <input id="phaseEditLocation" type="text" value="${phaseEscapeHtml(match.location || '')}" />
                    </div>
                    <div class="phase-actions">
                        <button type="button" class="phase-btn phase-btn-cancel" id="phaseEditCancel">Cancel</button>
                        <button type="button" class="phase-btn phase-btn-save" id="phaseEditSave">Save</button>
                    </div>
                `;

                document.body.appendChild(modal);
                const rect = anchorEl.getBoundingClientRect();
                const modalWidth = Math.min(300, window.innerWidth - 24);
                const left = Math.max(12, Math.min(window.innerWidth - modalWidth - 12, rect.left + 6));
                let top = rect.bottom + 8;
                const modalHeight = modal.offsetHeight || 320;
                if (top + modalHeight > window.innerHeight - 12) {
                    top = Math.max(12, rect.top - modalHeight - 8);
                }
                modal.style.left = `${left}px`;
                modal.style.top = `${top}px`;

                const saveBtn = modal.querySelector('#phaseEditSave');
                const cancelBtn = modal.querySelector('#phaseEditCancel');
                const roInput = modal.querySelector('#phaseEditRoNumber');
                saveBtn?.addEventListener('click', savePhaseModalChanges);
                cancelBtn?.addEventListener('click', closePhaseEditModal);
                modal.addEventListener('keydown', (event) => {
                    if (event.key === 'Escape') {
                        event.preventDefault();
                        closePhaseEditModal();
                    }
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        savePhaseModalChanges();
                    }
                });

                phaseEditModalEl = modal;
                roInput?.focus();
            }

            document.addEventListener('click', (event) => {
                if (!phaseEditModalEl) return;
                const target = event.target;
                if (phaseEditModalEl.contains(target)) return;
                if (target && target.closest && target.closest('.phase-ro-link')) return;
                closePhaseEditModal();
            });

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
                closePhaseEditModal();

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
                    const featureEnabled = isPhaseSpecialShop();
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
                    card.dataset.ro = item.ro_key || item.ro || '';
                    card.dataset.phase = item.phase || 'teardown';
                    // Assign color from pie chart palette
                    const roBarColor = roBarColors[idx % roBarColors.length];
                    const roText = item.ro || '—';
                    const roHeaderHtml = featureEnabled
                        ? `<button type="button" class="phase-ro-link" style="background:none; border:none; color:#fff; font:inherit; font-weight:bold; text-decoration:underline; cursor:pointer; padding:0;">RO# ${phaseEscapeHtml(roText)}</button>`
                        : `RO# ${roText}`;
                    const sprayGunExtraHtml = featureEnabled
                        ? `
                            <div class="meta-block">
                                <div>UNIT #: ${phaseDisplayValue(item.unit_number)}</div>
                                <div>VEHICLE TYPE: ${phaseDisplayValue(item.vehicle_type)}</div>
                                <div>LOCATION: ${phaseDisplayValue(item.location)}</div>
                            </div>
                        `
                        : '';
                    card.innerHTML = `
                        <div class="ro-bar" style="background:${roBarColor}">${roHeaderHtml}</div>
                        <div class="vehicle">${item.vehicle || '—'}</div>
                        <div class="meta">
                            <div>TECH: ${item.labor_tech || 'Unassigned'}</div>
                            <div>ESTIMATOR: ${(item.estimator || '—').split(/\s+/)[0]}</div>
                            ${sprayGunExtraHtml}
                        </div>
                    `;
                    if (featureEnabled) {
                        const roLink = card.querySelector('.phase-ro-link');
                        roLink?.addEventListener('click', (event) => {
                            event.preventDefault();
                            event.stopPropagation();
                            openPhaseEditModal(roLink, item.ro_key || item.ro || '');
                        });
                    }
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
                        phaseBoardItems = Array.isArray(res.items) ? res.items : [];
                        renderPhaseCards(phaseBoardItems);
                    })
                    .catch(err => {
                        console.error('Error loading phase data:', err);
                        phaseBoardItems = [];
                        closePhaseEditModal();
                        if (teardown) {
                            teardown.innerHTML = '<div style="color:#999; text-align:center; padding:10px;">Unable to load phase board</div>';
                        }
                    });
            }
        </script>
    </div>
    """

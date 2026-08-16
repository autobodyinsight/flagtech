"""Estimates screen content for the FlagTech UI."""


def get_estimates_screen_html():
    """Return the HTML content for the Estimates screen."""
    return r"""
        <div id="estimate" class="screen" style="padding:20px;">
            <style>
                #estimate .dashboard-ro-title-tab {
                    display: inline-flex;
                    align-items: center;
                    background: rgba(0,0,0,0.03);
                    color: #000000;
                    font-weight: 700;
                    padding: 10px 14px;
                    border-radius: 8px 8px 0 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    margin-bottom: -1px;
                    gap: 10px;
                }
                #estimate .estimate-tab-add {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 7px 12px;
                    border-radius: 8px;
                    background: #2e9d53;
                    color: #fff;
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 0.2px;
                    box-shadow: none;
                    border: none;
                    line-height: 1;
                }
                #estimate .dashboard-ro-table-wrap {
                    background: #ffffff;
                    border-radius: 4px;
                    overflow: hidden;
                }
                #estimate .dashboard-header-row th,
                #estimate .dashboard-header-cell {
                    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                    font-size: 15px;
                    font-weight: 600;
                    background: rgba(0,0,0,0.03) !important;
                    color: #000000;
                    text-align: left;
                    border: none !important;
                    border-bottom: 1px solid #b22222 !important;
                    padding-top: 14px !important;
                    padding-bottom: 14px !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }
                #estimateListBody tr.estimate-row td {
                    background: #ffffff;
                    border: none;
                    border-bottom: 1px solid rgba(0,0,0,0.06) !important;
                    min-height: 48px;
                    height: 48px;
                    vertical-align: middle;
                    color: #333;
                }
                #estimateListBody tr.estimate-row:hover td {
                    background: rgba(0,0,0,0.04) !important;
                }
                #estimateListBody .estimate-number {
                    font-weight: 700;
                    color: #111;
                }
            </style>

            <div style="display:flex; align-items:center; justify-content:center; margin-bottom:20px;">
                <h1 style="text-align:center; margin:0;">ESTIMATES</h1>
            </div>

            <div style="margin-top:8px;">
                <div style="display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:0; position:relative;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <h3 class="dashboard-ro-title-tab" style="margin:0; color:#333;">Estimate List</h3>
                        <button type="button" class="estimate-tab-add" aria-label="Add Estimate" onclick="openEstimateWindowFromEstimateList(event)">+ Estimate</button>
                    </div>
                </div>
                <div class="dashboard-ro-table-wrap" style="overflow-x:auto;">
                    <table id="estimateListTable" style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr class="dashboard-header-row">
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Estimate #</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Vehicle</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Customer</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Insurance</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold;">Claim Number</th>
                                <th class="dashboard-header-cell" style="padding:12px; border-bottom:2px solid #ddd; font-weight:bold; text-align:right;">Total</th>
                            </tr>
                        </thead>
                        <tbody id="estimateListBody">
                            <tr>
                                <td colspan="6" style="padding:20px; text-align:center; color:#999;">Loading...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            window.currentEstimateRows = [];

            function formatCurrency(value) {
                const numeric = Number(value || 0);
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                }).format(numeric);
            }

            function getNextEstimateNumber(startingAt = 702) {
                const numbers = (window.currentEstimateRows || [])
                    .map((row) => Number(row.estimate_number))
                    .filter((value) => Number.isFinite(value) && value > 0);
                if (!numbers.length) return startingAt;
                return Math.max(...numbers) + 1;
            }

            function openEstimateWindowFromEstimateList(event) {
                if (event) event.stopPropagation();

                const nextEstimateNumber = getNextEstimateNumber();
                const win = window.open('', `Estimate_Window_${nextEstimateNumber}`, 'width=1100,height=760,scrollbars=yes,resizable=yes');
                if (!win) {
                    alert('Popup blocked. Please allow popups for this site.');
                    return;
                }

                const manufacturerModels = {
                    Acura: ['CL', 'CSX', 'EL', 'ILX', 'Integra', 'MDX', 'NSX', 'RDX', 'RL', 'RSX', 'TL', 'TLX', 'TSX', 'ZDX'],
                    Alfa Romeo: ['4C', 'Giulia', 'MiTo', 'Stelvio'],
                    Audi: ['A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'Q3', 'Q4', 'Q5', 'Q7', 'Q8', 'R8', 'RS3', 'RS5', 'RS7', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'SQ5', 'SQ7', 'TT'],
                    BMW: ['1 Series', '2 Series', '3 Series', '4 Series', '5 Series', '6 Series', '7 Series', '8 Series', 'i3', 'i4', 'i8', 'M2', 'M3', 'M4', 'M5', 'M8', 'X1', 'X3', 'X4', 'X5', 'X6', 'X7', 'Z4'],
                    Buick: ['Cascada', 'Enclave', 'Encore', 'Encore GX', 'Envision', 'Envista', 'LaCrosse', 'Lucerne', 'Regal', 'Verano'],
                    Cadillac: ['ATS', 'CT4', 'CT5', 'CTS', 'CT6', 'Escalade', 'Lyriq', 'SRX', 'XT4', 'XT5', 'XT6'],
                    Chevrolet: ['Astro', 'Blazer', 'Bolt EV', 'Camaro', 'Caprice', 'Cavalier', 'Colorado', 'Corvette', 'Cruze', 'Equinox', 'Express', 'Impala', 'Malibu', 'Malibu Maxx', 'Metro', 'Monte Carlo', 'Prizm', 'S10', 'Silverado', 'Sonic', 'Spark', 'Suburban', 'Tahoe', 'Trailblazer', 'Traverse', 'Trax', 'Volt'],
                    Chrysler: ['200', '300', 'Aspen', 'Cirrus', 'Concorde', 'Crossfire', 'Pacifica', 'PT Cruiser', 'Sebring', 'Town & Country', 'Voyager'],
                    Dodge: ['Avenger', 'Challenger', 'Charger', 'Dakota', 'Dart', 'Durango', 'Grand Caravan', 'Journey', 'Magnum', 'Neon', 'Nitro', 'Ram 1500', 'Ram 2500', 'Ram 3500', 'Viper'],
                    Ferrari: ['488', 'F8 Tributo', 'California', 'F430', 'FF', 'Roma', 'SF90 Stradale'],
                    Fiat: ['124 Spider', '500', '500L', '500X', 'Doblo', 'Panda', 'Punto'],
                    Ford: ['Bronco', 'C-Max', 'Contour', 'Crown Victoria', 'EcoSport', 'Edge', 'Escape', 'Expedition', 'Explorer', 'F-150', 'F-250', 'F-350', 'Fiesta', 'Flex', 'Focus', 'Fusion', 'GT', 'Mustang', 'Ranger', 'Shelby GT500', 'Taurus', 'Thunderbird', 'Transit', 'Windstar'],
                    Genesis: ['G80', 'G90', 'GV60', 'GV70', 'GV80'],
                    GMC: ['Acadia', 'Canyon', 'Envoy', 'Jimmy', 'Sierra', 'Terrain', 'Yukon'],
                    Honda: ['Accord', 'Civic', 'CR-V', 'CR-Z', 'Fit', 'HR-V', 'Insight', 'Odyssey', 'Passport', 'Pilot', 'Prelude', 'Ridgeline', 'S2000'],
                    Hyundai: ['Accent', 'Azera', 'Elantra', 'Genesis', 'Ioniq', 'Kona', 'Nexo', 'Palisade', 'Santa Fe', 'Sonata', 'Staria', 'Tucson', 'Veloster', 'Venue'],
                    Infiniti: ['EX', 'FX', 'G', 'JX', 'M', 'Q50', 'Q60', 'Q70', 'QX30', 'QX50', 'QX60', 'QX80'],
                    Jaguar: ['E-Pace', 'F-Pace', 'F-Type', 'I-Pace', 'XE', 'XF', 'XJ'],
                    Jeep: ['Cherokee', 'Commander', 'Compass', 'Gladiator', 'Grand Cherokee', 'Liberty', 'Patriot', 'Renegade', 'Wrangler'],
                    Kia: ['Carens', 'EV6', 'Forte', 'K5', 'Niro', 'Optima', 'Rio', 'Seltos', 'Sorento', 'Soul', 'Sportage', 'Stinger', 'Telluride'],
                    Lamborghini: ['Aventador', 'Huracan', 'Urus'],
                    Land Rover: ['Defender', 'Discovery', 'Discovery Sport', 'Range Rover', 'Range Rover Evoque', 'Range Rover Sport', 'Range Rover Velar'],
                    Lexus: ['CT', 'ES', 'GX', 'IS', 'LS', 'LX', 'NX', 'RC', 'RX', 'TX', 'UX'],
                    Lincoln: ['Aviator', 'Continental', 'Corsair', 'MKC', 'MKS', 'MKZ', 'Navigator', 'Nautilus', 'Town Car'],
                    Maserati: ['Ghibli', 'GranTurismo', 'Levante', 'Quattroporte'],
                    Mazda: ['3', '5', '6', 'CX-3', 'CX-30', 'CX-5', 'CX-9', 'MX-5 Miata', 'Mazda2', 'Mazda3', 'Mazda6', 'MX-5'],
                    Mercedes-Benz: ['A-Class', 'C-Class', 'CLA', 'CLS', 'E-Class', 'G-Class', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'M-Class', 'R-Class', 'S-Class', 'SL', 'SLK', 'Sprinter', 'V-Class'],
                    Mini: ['Clubman', 'Cooper', 'Countryman', 'Convertible', 'John Cooper Works', 'One'],
                    Mitsubishi: ['Eclipse', 'Eclipse Cross', 'Galant', 'Lancer', 'Mirage', 'Montero', 'Outlander', 'Pajero', 'Raider'],
                    Nissan: ['350Z', '370Z', 'Altima', 'Armada', 'Frontier', 'GT-R', 'Juke', 'Leaf', 'Maxima', 'Murano', 'NV200', 'Pathfinder', 'Quest', 'Rogue', 'Sentra', 'Skyline', 'Titan', 'Versa', 'Xterra'],
                    Porsche: ['911', '718 Boxster', '718 Cayman', 'Cayenne', 'Macan', 'Panthar', 'Taycan'],
                    Ram: ['1500', '2500', '3500', 'ProMaster'],
                    Subaru: ['Ascent', 'BRZ', 'Crosstrek', 'Forester', 'Impreza', 'Legacy', 'Outback', 'WRX', 'XV Crosstrek'],
                    Tesla: ['Model 3', 'Model S', 'Model X', 'Model Y', 'Roadster'],
                    Toyota: ['4Runner', 'Avalon', 'Camry', 'Corolla', 'Cressida', 'GR Supra', 'Highlander', 'Land Cruiser', 'Matrix', 'Prius', 'RAV4', 'Sequoia', 'Sienna', 'Tacoma', 'Tundra', 'Yaris'],
                    Volkswagen: ['Atlas', 'Beetle', 'CC', 'Eos', 'Golf', 'GTI', 'Jetta', 'Passat', 'Phaeton', 'Routan', 'Taos', 'Tiguan', 'Touareg'],
                    Volvo: ['S60', 'S80', 'V60', 'V70', 'V90', 'XC40', 'XC60', 'XC70', 'XC90']
                };

                const usStates = [
                    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'
                ];

                const years = Array.from({ length: 2030 - 1960 + 1 }, (_, index) => 1960 + index);
                const makeOptions = Object.keys(manufacturerModels).sort();

                const createMakeOptions = (selectedMake = '') => {
                    const options = ['<option value="">Select Make</option>'];
                    makeOptions.forEach((make) => {
                        options.push(`<option value="${make}" ${make === selectedMake ? 'selected' : ''}>${make}</option>`);
                    });
                    return options.join('');
                };

                const createModelOptions = (selectedMake = '', selectedModel = '') => {
                    const models = manufacturerModels[selectedMake] || [];
                    const options = ['<option value="">Select Model</option>'];
                    models.forEach((model) => {
                        options.push(`<option value="${model}" ${model === selectedModel ? 'selected' : ''}>${model}</option>`);
                    });
                    return options.join('');
                };

                const bannerHtml = `
                    <div id="estimateHeaderBar" style="background:linear-gradient(90deg, #111 0%, #23272a 48%, #d32f2f 100%); color:#fff; padding:12px 24px; position:relative; z-index:120; display:flex; align-items:center; justify-content:space-between; gap:16px;">
                        <div class="estimate-header-item" style="margin:0; display:flex; align-items:center; gap:10px;">
                            <span class="estimate-header-label" style="font-size:16px;">Estimate #:</span>
                            <span class="estimate-header-value" style="font-size:18px; font-weight:800;">${nextEstimateNumber}</span>
                        </div>
                        <button id="estimateSaveButton" type="button" style="background:#2e9d53; color:#fff; border:none; border-radius:8px; padding:10px 18px; font-size:14px; font-weight:700; cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,0.18);">Save</button>
                    </div>
                `;

                const formHtml = `
                    <div id="estimateWindowContent" style="padding:26px 28px 40px; min-height:180px; background:#f5f7fb; color:#23272a; overflow:auto;">
                        <div style="max-width:980px; margin:0 auto; display:flex; flex-direction:column; gap:20px;">
                            <div class="estimate-card" style="background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:20px;">
                                <div class="estimate-section-header" style="font-weight:800; font-size:18px; color:#111827; margin:0 0 16px;">Customer</div>
                                <div style="display:grid; grid-template-columns:repeat(2, minmax(220px, 1fr)); gap:16px;">
                                    <div class="estimate-field"><label>First Name</label><input id="estimateFirstName" type="text" placeholder="First name" /></div>
                                    <div class="estimate-field"><label>Last Name</label><input id="estimateLastName" type="text" placeholder="Last name" /></div>
                                    <div class="estimate-field" style="grid-column:1 / -1;"><label>Address</label><input id="estimateAddress" type="text" placeholder="Street address" /></div>
                                    <div class="estimate-field"><label>City</label><input id="estimateCity" type="text" placeholder="City" /></div>
                                    <div class="estimate-field"><label>State</label><input id="estimateCustomerState" type="text" maxlength="2" placeholder="ST" /></div>
                                    <div class="estimate-field"><label>Zip Code</label><input id="estimateZip" type="text" inputmode="numeric" maxlength="10" placeholder="Zip code" /></div>
                                    <div class="estimate-field"><label>Phone Number</label><input id="estimatePhone" type="tel" placeholder="(555) 123-4567" /></div>
                                    <div class="estimate-field"><label>Email</label><input id="estimateEmail" type="email" placeholder="example@email.com" /></div>
                                    <div class="estimate-field"><label>Insurance Company</label><input id="estimateInsuranceCompany" type="text" placeholder="Insurance company" /></div>
                                    <div class="estimate-field"><label>Claim Number</label><input id="estimateClaimNumber" type="text" placeholder="Claim #" /></div>
                                </div>
                            </div>

                            <div class="estimate-card" style="background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:20px;">
                                <div class="estimate-section-header" style="font-weight:800; font-size:18px; color:#111827; margin:0 0 16px;">Vehicle Info</div>
                                <div style="display:grid; grid-template-columns:repeat(2, minmax(220px, 1fr)); gap:16px;">
                                    <div class="estimate-field" style="grid-column:1 / -1;"><label>VIN</label><input id="estimateVin" type="text" maxlength="17" placeholder="VIN" style="letter-spacing:0.12em; text-transform:uppercase;" /></div>
                                    <div class="estimate-field"><label>Year</label><select id="estimateYear">${years.map((year) => `<option value="${year}">${year}</option>`).join('')}</select></div>
                                    <div class="estimate-field"><label>Make</label><select id="estimateMake">${createMakeOptions()}</select></div>
                                    <div class="estimate-field"><label>Model</label><select id="estimateModel">${createModelOptions()}</select></div>
                                    <div class="estimate-field"><label>Production Date</label><input id="estimateProductionDate" type="date" /></div>
                                    <div class="estimate-field"><label>Paint Code</label><input id="estimatePaintCode" type="text" placeholder="Paint code" /></div>
                                    <div class="estimate-field"><label>Trim Code</label><input id="estimateTrimCode" type="text" placeholder="Trim code" /></div>
                                    <div class="estimate-field"><label>Miles</label><input id="estimateMiles" type="number" min="0" step="1" placeholder="0" /></div>
                                    <div class="estimate-field"><label>License Plate</label><input id="estimateLicensePlate" type="text" placeholder="License plate" /></div>
                                    <div class="estimate-field"><label>State</label><select id="estimatePlateState">${['<option value="">Select</option>', ...usStates.map((state) => `<option value="${state}">${state}</option>`)].join('')}</select></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                win.document.title = `Estimate Window - ${nextEstimateNumber}`;
                win.document.body.innerHTML = `<div id='estimatePopupRoot' style='display:flex; flex-direction:column; height:100vh; width:100vw; background:#f2f2f2; overflow:hidden;'>${bannerHtml}<div id='estimatePopupLowerLayout' style='display:flex; flex:1 1 auto; min-height:0;'>${formHtml}</div></div>`;

                const style = win.document.createElement('style');
                style.textContent = `
                    body { margin:0; font-family:Segoe UI,Arial,sans-serif; background:#f2f2f2; }
                    .estimate-card {
                        background:#fff;
                        border:1px solid #e5e7eb;
                        border-radius:14px;
                        box-shadow:0 8px 20px rgba(15,23,42,0.06);
                        padding:20px;
                    }
                    .estimate-field {
                        display:flex;
                        flex-direction:column;
                        gap:8px;
                    }
                    .estimate-field label {
                        font-size:12px;
                        font-weight:700;
                        letter-spacing:0.08em;
                        text-transform:uppercase;
                        color:#475569;
                    }
                    .estimate-field input,
                    .estimate-field select {
                        width:100%;
                        height:42px;
                        background:#f8fafc;
                        border:1px solid #dfe6ee;
                        border-radius:10px;
                        padding:10px 12px;
                        font-size:15px;
                        color:#0f172a;
                        box-sizing:border-box;
                    }
                    .estimate-field input:focus,
                    .estimate-field select:focus {
                        outline:2px solid rgba(178,34,34,0.18);
                        border-color:#cbd5e1;
                    }
                    #estimateSaveButton {
                        transition:filter 0.15s ease, transform 0.15s ease;
                    }
                    #estimateSaveButton:hover {
                        filter:brightness(1.04);
                        transform:translateY(-1px);
                    }
                    .estimate-header-label {
                        color:#fff;
                        font-weight:700;
                        margin-right:0;
                    }
                    .estimate-header-value {
                        color:#fff;
                        font-weight:800;
                    }
                `;
                win.document.head.appendChild(style);

                const makeSelect = win.document.getElementById('estimateMake');
                const modelSelect = win.document.getElementById('estimateModel');
                if (makeSelect) {
                    makeSelect.innerHTML = createMakeOptions();
                    makeSelect.addEventListener('change', () => {
                        modelSelect.innerHTML = createModelOptions(makeSelect.value, '');
                    });
                }

                const saveButton = win.document.getElementById('estimateSaveButton');
                if (saveButton) {
                    saveButton.addEventListener('click', async () => {
                        const firstName = (win.document.getElementById('estimateFirstName')?.value || '').trim();
                        const lastName = (win.document.getElementById('estimateLastName')?.value || '').trim();
                        const address = (win.document.getElementById('estimateAddress')?.value || '').trim();
                        const city = (win.document.getElementById('estimateCity')?.value || '').trim();
                        const customerState = (win.document.getElementById('estimateCustomerState')?.value || '').trim();
                        const zipCode = (win.document.getElementByById('estimateZip')?.value || '').trim();
                        const phone = (win.document.getElementById('estimatePhone')?.value || '').trim();
                        const email = (win.document.getElementById('estimateEmail')?.value || '').trim();
                        const insuranceCompany = (win.document.getElementById('estimateInsuranceCompany')?.value || '').trim();
                        const claimNumber = (win.document.getElementById('estimateClaimNumber')?.value || '').trim();
                        const vin = (win.document.getElementById('estimateVin')?.value || '').trim().toUpperCase();
                        const year = (win.document.getElementById('estimateYear')?.value || '').trim();
                        const make = (win.document.getElementById('estimateMake')?.value || '').trim();
                        const model = (win.document.getElementById('estimateModel')?.value || '').trim();
                        const productionDate = (win.document.getElementById('estimateProductionDate')?.value || '').trim();
                        const paintCode = (win.document.getElementById('estimatePaintCode')?.value || '').trim();
                        const trimCode = (win.document.getElementById('estimateTrimCode')?.value || '').trim();
                        const miles = (win.document.getElementById('estimateMiles')?.value || '').trim();
                        const licensePlate = (win.document.getElementById('estimateLicensePlate')?.value || '').trim();
                        const plateState = (win.document.getElementById('estimatePlateState')?.value || '').trim();

                        const payload = {
                            ro_number: `EST-${nextEstimateNumber}`,
                            ro: `EST-${nextEstimateNumber}`,
                            owner_info: [firstName, lastName].filter(Boolean).join(' ') || '',
                            customer_first_name: firstName,
                            customer_last_name: lastName,
                            address,
                            city,
                            state: customerState,
                            zip_code: zipCode,
                            phone,
                            email,
                            insurance_company: insuranceCompany,
                            claim_number: claimNumber,
                            vehicle: [year, make, model].filter(Boolean).join(' '),
                            year,
                            make,
                            model,
                            vin,
                            in_date: productionDate || new Date().toISOString().split('T')[0],
                            ecd_date: '',
                            picked_up: '',
                            paint_code: paintCode,
                            trim_code: trimCode,
                            miles,
                            license_plate: licensePlate,
                            license_plate_state: plateState,
                            estimate_totals: {},
                            estimate_snapshot: {},
                            labor_repairs: [],
                            paint_repairs: [],
                            parts_repairs: [],
                            local_upload_date: productionDate || new Date().toISOString().split('T')[0],
                            saved_by: 'estimate-window-form'
                        };

                        try {
                            saveButton.disabled = true;
                            saveButton.textContent = 'Saving...';
                            const response = await fetch('/save-estimate', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include',
                                body: JSON.stringify(payload)
                            });
                            const result = await response.json().catch(() => ({}));
                            if (!response.ok || result?.error || result?.status !== 'success') {
                                throw new Error(result?.error || 'Unable to save estimate.');
                            }
                            saveButton.textContent = 'Saved';
                            saveButton.style.background = '#1c7c4d';
                            setTimeout(() => {
                                saveButton.textContent = 'Save';
                                saveButton.style.background = '#2e9d53';
                                saveButton.disabled = false;
                            }, 1400);
                        } catch (error) {
                            console.error('Save estimate failed:', error);
                            alert(error.message || 'Unable to save estimate.');
                            saveButton.disabled = false;
                            saveButton.textContent = 'Save';
                        }
                    });
                }
            }

            async function loadEstimateList() {
                const body = document.getElementById('estimateListBody');
                if (!body) return;
                body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#999;">Loading...</td></tr>';

                try {
                    const response = await fetch('/api/estimate-list', { credentials: 'include' });
                    const data = await response.json();
                    if (!response.ok || data.error) throw new Error(data.error || 'Unable to load estimates');

                    const rows = Array.isArray(data.estimateList) ? data.estimateList : [];
                    window.currentEstimateRows = rows;

                    if (!rows.length) {
                        body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#666;">NO CURRENT ESTIMATES</td></tr>';
                        return;
                    }

                    body.innerHTML = rows.map((row) => {
                        const estimateNumber = row.estimate_number ?? '';
                        const vehicle = row.vehicle || '-';
                        const customer = row.customer || '-';
                        const insurance = row.insurance || '-';
                        const claimNumber = row.claim_number || '-';
                        const total = Number(row.total || 0);

                        return `
                            <tr class="estimate-row">
                                <td class="estimate-number">${estimateNumber}</td>
                                <td>${vehicle}</td>
                                <td>${customer}</td>
                                <td>${insurance}</td>
                                <td>${claimNumber}</td>
                                <td style="text-align:right; font-weight:600; color:#111;">${formatCurrency(total)}</td>
                            </tr>
                        `;
                    }).join('');
                } catch (error) {
                    console.error('Error loading estimate list:', error);
                    body.innerHTML = '<tr><td colspan="6" style="padding:20px; text-align:center; color:#b22222;">Unable to load estimates.</td></tr>';
                }
            }
        </script>
    """

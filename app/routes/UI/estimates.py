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
                    'Alfa Romeo': ['4C', 'Giulia', 'MiTo', 'Stelvio'],
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
                    'Land Rover': ['Defender', 'Discovery', 'Discovery Sport', 'Range Rover', 'Range Rover Evoque', 'Range Rover Sport', 'Range Rover Velar'],
                    Lexus: ['CT', 'ES', 'GX', 'IS', 'LS', 'LX', 'NX', 'RC', 'RX', 'TX', 'UX'],
                    Lincoln: ['Aviator', 'Continental', 'Corsair', 'MKC', 'MKS', 'MKZ', 'Navigator', 'Nautilus', 'Town Car'],
                    Maserati: ['Ghibli', 'GranTurismo', 'Levante', 'Quattroporte'],
                    Mazda: ['3', '5', '6', 'CX-3', 'CX-30', 'CX-5', 'CX-9', 'MX-5 Miata', 'Mazda2', 'Mazda3', 'Mazda6', 'MX-5'],
                    'Mercedes-Benz': ['A-Class', 'C-Class', 'CLA', 'CLS', 'E-Class', 'G-Class', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'M-Class', 'R-Class', 'S-Class', 'SL', 'SLK', 'Sprinter', 'V-Class'],
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

                const defaultRateValues = {
                    body: 0,
                    paint: 0,
                    frame: 0,
                    mechanical: 0,
                    glass: 0,
                    paintMaterials: 0,
                    taxRate: 0
                };

                const formHtml = `
                    <div id="estimateWindowContent" style="padding:24px 20px 30px 20px; min-height:180px; background:#f5f7fb; color:#23272a; overflow:auto; box-sizing:border-box; flex:1 1 auto;">
                        <div id="estimateWindowShell" style="display:flex; align-items:stretch; gap:18px; width:100%; min-height:100%; box-sizing:border-box;">
                            <aside id="estimateSidebarNav" style="width:120px; min-width:120px; background:linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border:1px solid #e5e7eb; border-radius:16px; box-shadow:0 8px 20px rgba(15,23,42,.06); display:flex; flex-direction:column; gap:14px; padding:14px 10px; box-sizing:border-box; align-self:stretch;">
                                <div class="estimate-nav-label" style="font-size:11px; font-weight:800; letter-spacing:0.12em; text-transform:uppercase; color:#64748b; text-align:center; padding:0 4px 8px;">Menu</div>
                                <button type="button" class="estimate-nav-button estimate-nav-button-selected" data-estimate-view="customerVehicle" style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; width:100%; min-height:82px; border:1px solid #dbe2ea; border-radius:12px; background:linear-gradient(180deg, #fff1f2 0%, #fff 100%); color:#b22222; font-size:12px; font-weight:700; cursor:pointer; box-shadow:inset 0 0 0 1px rgba(178,34,34,0.08);">
                                    <span aria-hidden="true" style="font-size:22px; line-height:1;">👤</span>
                                    <span>Customer / Vehicle</span>
                                </button>
                                <button type="button" class="estimate-nav-button" data-estimate-view="estimate" style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; width:100%; min-height:74px; border:1px solid #e5e7eb; border-radius:12px; background:#fff; color:#374151; font-size:11px; font-weight:700; cursor:pointer;">
                                    <span aria-hidden="true" style="font-size:20px; line-height:1;">🧩</span>
                                    <span>Estimate</span>
                                </button>
                                <button type="button" class="estimate-nav-button" data-estimate-view="rates" style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; width:100%; min-height:74px; border:1px solid #e5e7eb; border-radius:12px; background:#fff; color:#374151; font-size:11px; font-weight:700; cursor:pointer;">
                                    <span aria-hidden="true" style="font-size:20px; line-height:1;">📊</span>
                                    <span>Rates</span>
                                </button>
                                <button type="button" class="estimate-nav-button" data-estimate-view="notes" style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; width:100%; min-height:74px; border:1px solid #e5e7eb; border-radius:12px; background:#fff; color:#374151; font-size:11px; font-weight:700; cursor:pointer;">
                                    <span aria-hidden="true" style="font-size:20px; line-height:1;">📝</span>
                                    <span>Notes</span>
                                </button>
                            </aside>

                            <div id="estimateContentLayout" style="display:flex; align-items:stretch; gap:24px; flex:1 1 auto; min-width:0; min-height:560px; height:100%; overflow:visible; box-sizing:border-box; margin-left:0;">
                                <div id="estimateCustomerVehiclePanel" style="display:flex; flex:1 1 auto; min-width:0; gap:18px; align-items:stretch; overflow:visible; box-sizing:border-box;">
                                    <div id="estimateInfoPane" style="flex:1 1 auto; min-width:0; display:flex; flex-direction:row; gap:20px; transition:all 0.35s ease; overflow:visible; box-sizing:border-box;">
                                        <div class="estimate-card" style="background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:20px; width:100%; min-width:0; box-sizing:border-box; flex:1 1 50%;">
                                            <div class="estimate-section-header" style="font-weight:800; font-size:18px; color:#111827; margin:0 0 16px;">Customer</div>
                                            <div style="display:grid; grid-template-columns:repeat(2, minmax(180px, 1fr)); gap:16px; width:100%; box-sizing:border-box;">
                                                <div class="estimate-field"><label>First Name</label><input id="estimateFirstName" type="text" placeholder="First name" /></div>
                                                <div class="estimate-field"><label>Last Name</label><input id="estimateLastName" type="text" placeholder="Last name" /></div>
                                                <div class="estimate-field" style="grid-column:1 / -1;"><label>Address</label><input id="estimateAddress" type="text" placeholder="Street address" /></div>
                                                <div class="estimate-field"><label>City</label><input id="estimateCity" type="text" placeholder="City" /></div>
                                                <div class="estimate-field"><label>State</label><select id="estimateCustomerState"><option value="">Select</option>${usStates.map((state) => `<option value="${state}">${state}</option>`).join('')}</select></div>
                                                <div class="estimate-field"><label>Zip Code</label><input id="estimateZip" type="text" inputmode="numeric" maxlength="10" placeholder="Zip code" /></div>
                                                <div class="estimate-field"><label>Phone Number</label><input id="estimatePhone" type="tel" placeholder="(555) 123-4567" /></div>
                                                <div class="estimate-field"><label>Email</label><input id="estimateEmail" type="email" placeholder="example@email.com" /></div>
                                                <div class="estimate-field"><label>Insurance Company</label><input id="estimateInsuranceCompany" type="text" placeholder="Insurance company" /></div>
                                                <div class="estimate-field"><label>Claim Number</label><input id="estimateClaimNumber" type="text" placeholder="Claim #" /></div>
                                            </div>
                                        </div>

                                        <div class="estimate-card" style="background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:20px; width:100%; min-width:0; box-sizing:border-box; flex:1 1 50%;">
                                            <div class="estimate-section-header" style="font-weight:800; font-size:18px; color:#111827; margin:0 0 16px;">Vehicle Info</div>
                                            <div style="display:grid; grid-template-columns:repeat(2, minmax(180px, 1fr)); gap:16px; width:100%; box-sizing:border-box;">
                                                <div class="estimate-field" style="grid-column:1 / -1;"><label>VIN</label><input id="estimateVin" type="text" maxlength="17" placeholder="VIN" style="letter-spacing:0.12em; text-transform:uppercase;" /></div>
                                                <div class="estimate-field"><label>Year</label><select id="estimateYear">${years.map((year) => `<option value="${year}">${year}</option>`).join('')}</select></div>
                                                <div class="estimate-field"><label>Make</label><select id="estimateMake">${createMakeOptions()}</select></div>
                                                <div class="estimate-field"><label>Model</label><select id="estimateModel">${createModelOptions()}</select></div>
                                                <div class="estimate-field"><label>Production Date</label><input id="estimateProductionDate" type="text" inputmode="numeric" maxlength="7" placeholder="MM/YYYY" /></div>
                                                <div class="estimate-field"><label>Paint Code</label><input id="estimatePaintCode" type="text" placeholder="Paint code" /></div>
                                                <div class="estimate-field"><label>Trim Code</label><input id="estimateTrimCode" type="text" placeholder="Trim code" /></div>
                                                <div class="estimate-field"><label>Miles</label><input id="estimateMiles" type="number" min="0" step="1" placeholder="0" /></div>
                                                <div class="estimate-field"><label>License Plate</label><input id="estimateLicensePlate" type="text" placeholder="License plate" /></div>
                                                <div class="estimate-field"><label>State</label><select id="estimatePlateState">${['<option value="">Select</option>', ...usStates.map((state) => `<option value="${state}">${state}</option>`)].join('')}</select></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div id="estimateWorkPanel" style="display:none; flex:1 1 auto; min-width:0; gap:24px; align-items:stretch; overflow:visible; box-sizing:border-box;">
                                    <aside id="estimateCategoriesPane" style="flex:0 0 230px; min-width:230px; background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:0; overflow:visible; display:flex; flex-direction:column; transition:all 0.35s ease; box-sizing:border-box;">
                                        <div style="background:linear-gradient(180deg, #111827 0%, #1f2937 100%); color:#fff; padding:16px 18px; font-weight:800; letter-spacing:0.06em; font-size:13px; text-transform:uppercase;">Part Categories</div>
                                        <div id="estimateCategoryList" style="padding:16px 14px; display:flex; flex-direction:column; gap:8px; overflow:auto; flex:1; min-height:0;"></div>
                                    </aside>

                                    <div id="estimateRightPane" style="flex:1 1 auto; min-width:420px; display:flex; flex-direction:column; gap:18px; overflow:visible; box-sizing:border-box; margin-left:0; margin-right:0; padding-right:10px;">
                                        <div id="estimateSchematicPane" style="flex:1.4; background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:0; overflow:visible; display:flex; flex-direction:column; box-sizing:border-box;">
                                            <div style="background:linear-gradient(180deg, #1f2937 0%, #374151 100%); color:#fff; padding:16px 18px; font-weight:800; letter-spacing:0.06em; font-size:13px; text-transform:uppercase;">Schematic</div>
                                            <div style="padding:14px; display:flex; flex-direction:column; gap:12px; background:#f8fafc; min-height:0; flex:1; overflow:visible; box-sizing:border-box;">
                                                <div id="estimateIllustrationArea" style="min-height:220px; overflow:visible; width:100%;"></div>
                                            </div>
                                        </div>

                                        <div id="estimateLinesPane" style="flex:0.8; background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:0; overflow:visible; display:flex; flex-direction:column; box-sizing:border-box;">
                                            <div style="background:linear-gradient(180deg, #374151 0%, #4b5563 100%); color:#fff; padding:16px 18px; font-weight:800; letter-spacing:0.06em; font-size:13px; text-transform:uppercase;">Estimate Lines</div>
                                            <div id="estimateLineList" style="padding:14px; display:flex; flex-direction:column; gap:8px; overflow:auto; flex:1; min-height:0; width:100%; box-sizing:border-box;"></div>
                                        </div>
                                    </div>
                                </div>

                                <div id="estimateRatesPanel" style="display:none; flex:1 1 auto; min-width:0; background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:18px; box-sizing:border-box;">
                                    <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:16px;">
                                        <div style="font-size:18px; font-weight:800; color:#111827;">Rate Settings</div>
                                    </div>
                                    <div style="overflow:auto; border:1px solid #e5e7eb; border-radius:12px; background:#f8fafc;">
                                        <table style="width:100%; border-collapse:collapse; min-width:520px;">
                                            <thead>
                                                <tr style="background:#f1f5f9;">
                                                    <th style="padding:12px 14px; text-align:left; font-size:12px; letter-spacing:0.08em; text-transform:uppercase; color:#475569;">Category</th>
                                                    <th style="padding:12px 14px; text-align:right; font-size:12px; letter-spacing:0.08em; text-transform:uppercase; color:#475569;">Rate</th>
                                                </tr>
                                            </thead>
                                            <tbody id="estimateRatesTableBody">
                                                ${Object.entries(defaultRateValues).map(([key, value]) => `
                                                    <tr style="border-top:1px solid #e5e7eb;">
                                                        <td style="padding:12px 14px; font-weight:600; color:#111827; text-transform:capitalize;">${key === 'paintMaterials' ? 'Paint Materials' : key === 'taxRate' ? 'Tax Rate' : key.replace(/([A-Z])/g, ' $1').trim()}</td>
                                                        <td style="padding:12px 14px; text-align:right;">
                                                            <input type="number" class="estimate-rate-input" data-rate-key="${key}" value="${value}" step="0.01" min="0" style="width:150px; height:40px; border:1px solid #dfe6ee; border-radius:10px; background:#fff; padding:8px 10px; text-align:right; font-size:15px; color:#0f172a; box-sizing:border-box;" />
                                                        </td>
                                                    </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                <div id="estimateNotesPanel" style="display:none; flex:1 1 auto; min-width:0; background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 8px 20px rgba(15,23,42,.06); padding:18px; box-sizing:border-box;">
                                    <div style="font-size:18px; font-weight:800; color:#111827; margin-bottom:14px;">Notes</div>
                                    <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:18px;">
                                        <textarea id="estimateNotesInput" rows="4" placeholder="Add a note for this estimate..." style="width:100%; resize:vertical; min-height:120px; border:1px solid #dfe6ee; border-radius:12px; background:#f8fafc; padding:12px 14px; font-size:14px; color:#0f172a; box-sizing:border-box;"></textarea>
                                        <div style="display:flex; justify-content:flex-end;">
                                            <button type="button" id="estimateAddNoteButton" style="background:#b22222; color:#fff; border:none; border-radius:10px; padding:10px 16px; font-weight:700; cursor:pointer;">Add Note</button>
                                        </div>
                                    </div>
                                    <div id="estimateNotesHistory" style="display:flex; flex-direction:column; gap:10px; max-height:420px; overflow:auto; padding-right:4px;">
                                        <div style="color:#64748b; font-size:14px; font-weight:600;">No notes yet.</div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                `;

                win.document.title = `Estimate Window - ${nextEstimateNumber}`;
                win.document.body.innerHTML = `<div id='estimatePopupRoot' style='display:flex; flex-direction:column; min-height:100vh; width:100vw; background:#f2f2f2; overflow:auto;'>${bannerHtml}<div id='estimatePopupLowerLayout' style='display:flex; flex:1 1 auto; min-height:0; width:100%;'>${formHtml}</div></div>`;

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
                    .estimate-nav-button {
                        transition:all 0.2s ease;
                    }
                    .estimate-nav-button-selected {
                        background:linear-gradient(180deg, #fff1f2 0%, #fff 100%);
                        border-color:#f3c4c8;
                        box-shadow:inset 0 0 0 1px rgba(178,34,34,0.08), 0 6px 14px rgba(178,34,34,0.08);
                    }
                    #estimateWindowContent,
                    #estimateWindowShell,
                    #estimateContentLayout,
                    #estimateLeftPane,
                    #estimateRightPane,
                    #estimateInfoPane,
                    #estimateCategoriesPane,
                    #estimateSchematicPane,
                    #estimateLinesPane {
                        overflow:visible;
                        transition:all 0.35s ease;
                    }
                    #estimateCategoryList,
                    #estimateLineList {
                        scrollbar-width: thin;
                        overflow:auto;
                    }
                `;
                win.document.head.appendChild(style);

                const makeSelect = win.document.getElementById('estimateMake');
                const modelSelect = win.document.getElementById('estimateModel');
                const leftPane = win.document.getElementById('estimateLeftPane');
                const infoPane = win.document.getElementById('estimateInfoPane');
                const categoryPane = win.document.getElementById('estimateCategoriesPane');
                const rightPane = win.document.getElementById('estimateRightPane');
                const categoryList = win.document.getElementById('estimateCategoryList');
                const illustrationArea = win.document.getElementById('estimateIllustrationArea');
                const estimateLineList = win.document.getElementById('estimateLineList');
                const productionDateInput = win.document.getElementById('estimateProductionDate');
                const toggleButton = win.document.getElementById('estimateSidebarToggle');

                const getVehicleBodyType = (make = '', model = '') => {
                    const normalized = `${make || ''} ${model || ''}`.toLowerCase();
                    if (/(pickup|truck|1500|2500|3500|silverado|sierra|tacoma|tundra|f-150|f-250|f-350|ranger|ridgeline|dakota|ram |frontier|canyon|colorado|sequoia|tahoe|yukon|escalade|bedside|tailgate)/i.test(normalized)) return 'truck';
                    if (/(transit|sprinter|promaster|express|voyager|caravan|pacifica|town & country|full-size van|minivan|van|liftgate)/i.test(normalized)) return 'van';
                    if (/(x1|x3|x4|x5|x6|x7|xc40|xc60|xc70|xc90|qx|mdx|rdx|cr-v|rav4|highlander|pilot|explorer|escape|equinox|traverse|sportage|seltos|outback|forester|crosstrek|atlas|tiguan|pathfinder|murano|jeep|cherokee|wrangler|grand cherokee|durango|gladiator|nexo|palisade|telluride|ascent|cx-|m5|m4|m3|suv)/i.test(normalized)) return 'suv';
                    return 'car';
                };

                const getVehicleCategoryList = (make = '', model = '') => {
                    const basePartCategories = [
                        'front bumper', 'grille', 'headlight', 'hood', 'fender', 'radiator support', 'radiator',
                        'condenser', 'frame', 'windshield', 'front door', 'rear door', 'roof', 'rear body',
                        'floor', 'tail light', 'rear bumper'
                    ];
                    const bodyType = getVehicleBodyType(make, model);
                    const categories = [...basePartCategories];

                    if (bodyType === 'truck') {
                        categories.splice(categories.indexOf('roof') + 1, 0, 'bedside', 'tailgate');
                    } else if (bodyType === 'van' || bodyType === 'suv') {
                        categories.splice(categories.indexOf('roof') + 1, 0, 'quarter panel', 'liftgate');
                    } else {
                        categories.splice(categories.indexOf('roof') + 1, 0, 'quarter panel', 'trunk');
                    }

                    return categories.filter((item) => !(
                        (bodyType === 'truck' && ['quarter panel', 'trunk', 'liftgate'].includes(item)) ||
                        (bodyType === 'van' && ['bedside', 'tailgate', 'trunk'].includes(item)) ||
                        (bodyType === 'suv' && ['bedside', 'tailgate', 'trunk'].includes(item)) ||
                        (bodyType === 'car' && ['bedside', 'liftgate', 'tailgate'].includes(item))
                    ));
                };

                const makeComponentMap = {
                    'front bumper': ['bumper cover', 'bumper reinforcement', 'brackets', 'molding', 'lower valance'],
                    grille: ['grille shell', 'grille insert', 'retainer clips', 'emblem'],
                    headlight: ['lamp housing', 'lens', 'mounting bracket', 'aiming screw'],
                    hood: ['hood skin', 'hinges', 'latch', 'insulation'],
                    fender: ['outer fender', 'inner liner', 'brackets', 'molding'],
                    'radiator support': ['core support', 'mounting tabs', 'support braces'],
                    radiator: ['radiator core', 'fan shroud', 'hoses'],
                    condenser: ['condenser core', 'lines', 'brackets'],
                    frame: ['left rail', 'right rail', 'crossmember', 'mounting tabs'],
                    windshield: ['glass', 'weatherstrip', 'adhesive', 'molding'],
                    'front door': ['outer skin', 'inner panel', 'window regulator', 'hinges'],
                    'rear door': ['outer skin', 'inner panel', 'window regulator', 'hinges'],
                    'quarter panel': ['outer quarter panel', 'inner brace', 'wheelhouse', 'molding'],
                    bedside: ['outer bedside', 'inner bedside', 'support braces', 'molding'],
                    roof: ['roof skin', 'roof bows', 'weatherstrip', 'trim'],
                    trunk: ['trunk lid', 'latch', 'striker', 'weatherstrip'],
                    liftgate: ['liftgate shell', 'hinges', 'striker', 'glass'],
                    'tailgate': ['tailgate shell', 'latches', 'hinges', 'support cables'],
                    'rear body': ['rear quarter shell', 'reinforcement', 'sealant', 'trim'],
                    floor: ['floor pan', 'inner brace', 'seam sealer', 'mounting points'],
                    'tail light': ['tail lamp housing', 'lens', 'gasket', 'mounting clips'],
                    'rear bumper': ['bumper cover', 'reinforcement', 'brackets', 'lower valance']
                };

                const partPriceMap = {
                    'front bumper': [320, 145, 70, 55, 70],
                    grille: [180, 120, 35, 25],
                    headlight: [420, 190, 60, 35],
                    hood: [640, 120, 95, 110],
                    fender: [480, 145, 80, 45],
                    'radiator support': [390, 90, 60],
                    radiator: [240, 95, 65],
                    condenser: [220, 70, 50],
                    frame: [920, 590, 200, 80],
                    windshield: [540, 80, 120, 60],
                    'front door': [640, 240, 180, 95],
                    'rear door': [620, 220, 170, 90],
                    'quarter panel': [510, 230, 110, 70],
                    bedside: [690, 330, 170, 80],
                    roof: [760, 340, 125, 80],
                    trunk: [420, 95, 75, 60],
                    liftgate: [520, 115, 85, 80],
                    'tailgate': [470, 105, 85, 65],
                    'rear body': [710, 220, 160, 110],
                    floor: [980, 420, 180, 120],
                    'tail light': [210, 120, 35, 25],
                    'rear bumper': [350, 160, 80, 65]
                };

                const makePartMap = {
                    car: ['front bumper', 'grille', 'headlight', 'hood', 'fender', 'radiator support', 'radiator', 'condenser', 'frame', 'windshield', 'front door', 'rear door', 'quarter panel', 'roof', 'trunk', 'rear body', 'floor', 'tail light', 'rear bumper'],
                    suv: ['front bumper', 'grille', 'headlight', 'hood', 'fender', 'radiator support', 'radiator', 'condenser', 'frame', 'windshield', 'front door', 'rear door', 'quarter panel', 'roof', 'liftgate', 'rear body', 'floor', 'tail light', 'rear bumper'],
                    van: ['front bumper', 'grille', 'headlight', 'hood', 'fender', 'radiator support', 'radiator', 'condenser', 'frame', 'windshield', 'front door', 'rear door', 'quarter panel', 'roof', 'liftgate', 'rear body', 'floor', 'tail light', 'rear bumper'],
                    truck: ['front bumper', 'grille', 'headlight', 'hood', 'fender', 'radiator support', 'radiator', 'condenser', 'frame', 'windshield', 'front door', 'rear door', 'bedside', 'roof', 'tailgate', 'rear body', 'floor', 'tail light', 'rear bumper']
                };

                const normalizePartName = (part) => String(part || '').trim().toLowerCase();

                const getActiveVehicleType = () => getVehicleBodyType(makeSelect?.value || '', modelSelect?.value || '');

                const getVehicleSpecificEstimateLines = (partName) => {
                    const normalized = normalizePartName(partName);
                    const bodyType = getActiveVehicleType();
                    const componentList = makeComponentMap[normalized] || makeComponentMap['front bumper'];
                    const priceList = partPriceMap[normalized] || partPriceMap['front bumper'];
                    const components = componentList.map((component, index) => ({
                        label: component,
                        qty: index < 2 ? 1 : (bodyType === 'truck' && index === 2 ? 2 : 1),
                        price: priceList[index] || 0,
                        unit: 'EA'
                    }));
                    return components;
                };

                const getVehicleProfile = (make = '', model = '') => {
                    const normalized = `${make || ''} ${model || ''}`.toLowerCase();
                    if (/(pickup|truck|silverado|sierra|tacoma|tundra|ram|frontier|canyon|colorado|ridgeline|sequoia|yukon|f-150|f-250|f-350)/i.test(normalized)) return 'truck';
                    if (/(transit|sprinter|promaster|express|voyager|caravan|pacifica|minivan|van)/i.test(normalized)) return 'van';
                    if (/(cr-v|rav4|explorer|escape|equinox|sportage|forester|outback|pilot|atlas|rogue|pathfinder|murano|xc60|xc90|x5|x3|g80|g90|palisade|telluride|suv|crosstrek|ascent|mdx|rdx|range rover|defender)/i.test(normalized)) return 'suv';
                    if (/(mustang|camaro|challenger|corvette|miata|supra|911|z4|carrera|coupe|2 door|2-door|2dr)/i.test(normalized)) return 'coupe';
                    return 'car';
                };

                const getVehicleDoorCount = (make = '', model = '') => {
                    const normalized = `${make || ''} ${model || ''}`.toLowerCase();
                    if (/(coupe|convertible|roadster|2 door|2-door|2dr|2 door coupe)/i.test(normalized) || getVehicleProfile(make, model) === 'coupe') return 2;
                    if (/(sedan|4 door|4-door|4dr|family sedan)/i.test(normalized)) return 4;
                    return 4;
                };

                const getVehicleImageAsset = (make = '', model = '') => {
                    const profile = getVehicleProfile(make, model);
                    if (profile === 'truck') return '/static/truck.jpg';
                    if (profile === 'suv') return '/static/suv.jpg';
                    if (profile === 'coupe' || getVehicleDoorCount(make, model) === 2) return '/static/car%202%20door.jpg';
                    return '/static/car%204%20door.jpg';
                };

                const getHotspotConfiguration = (profile = 'car') => {
                    const common = [
                        { part: 'front bumper', label: 'Front Bumper', left: '7%', top: '70%', width: '24%', height: '14%' },
                        { part: 'grille', label: 'Grille', left: '23%', top: '56%', width: '18%', height: '12%' },
                        { part: 'headlight', label: 'Headlights', left: '21%', top: '42%', width: '12%', height: '11%' },
                        { part: 'fender', label: 'Fender', left: '4%', top: '45%', width: '12%', height: '22%' },
                        { part: 'hood', label: 'Hood', left: '18%', top: '30%', width: '48%', height: '21%' },
                        { part: 'windshield', label: 'Windshield', left: '42%', top: '24%', width: '24%', height: '14%' },
                        { part: 'front door', label: 'Front Door', left: '26%', top: '48%', width: '16%', height: '28%' },
                        { part: 'rear door', label: 'Rear Door', left: '52%', top: '48%', width: '17%', height: '28%' },
                        { part: 'quarter panel', label: 'Quarter Panel', left: '68%', top: '52%', width: '14%', height: '20%' },
                        { part: 'bedside', label: 'Bedside', left: '67%', top: '45%', width: '17%', height: '24%' }
                    ];

                    if (profile === 'truck') {
                        return common.map((item) => {
                            if (item.part === 'front bumper') return { ...item, left: '7%', top: '72%', width: '26%', height: '12%' };
                            if (item.part === 'grille') return { ...item, left: '28%', top: '58%', width: '20%', height: '11%' };
                            if (item.part === 'headlight') return { ...item, left: '22%', top: '45%', width: '12%', height: '10%' };
                            if (item.part === 'hood') return { ...item, left: '20%', top: '33%', width: '44%', height: '19%' };
                            if (item.part === 'windshield') return { ...item, left: '42%', top: '21%', width: '22%', height: '15%' };
                            if (item.part === 'rear door') return { ...item, left: '52%', top: '45%', width: '18%', height: '29%' };
                            if (item.part === 'bedside') return { ...item, left: '67%', top: '42%', width: '18%', height: '27%' };
                            return item;
                        });
                    }

                    if (profile === 'suv') {
                        return common.map((item) => {
                            if (item.part === 'front bumper') return { ...item, left: '9%', top: '68%', width: '20%', height: '14%' };
                            if (item.part === 'grille') return { ...item, left: '25%', top: '56%', width: '18%', height: '12%' };
                            if (item.part === 'headlight') return { ...item, left: '23%', top: '42%', width: '12%', height: '10%' };
                            if (item.part === 'hood') return { ...item, left: '20%', top: '32%', width: '48%', height: '20%' };
                            if (item.part === 'windshield') return { ...item, left: '42%', top: '23%', width: '24%', height: '14%' };
                            if (item.part === 'bedside') return { ...item, left: '69%', top: '44%', width: '18%', height: '24%' };
                            return item;
                        });
                    }

                    return common;
                };

                const getHotspotColor = (partName) => {
                    const normalized = normalizePartName(partName);
                    const colorMap = {
                        'front bumper': '#d32f2f',
                        grille: '#f472b6',
                        headlight: '#7c3aed',
                        fender: '#facc15',
                        hood: '#14b8a6',
                        'front door': '#22c55e',
                        'rear door': '#67e8f9',
                        'quarter panel': '#8b5e34',
                        bedside: '#8b5e34'
                    };
                    return colorMap[normalized] || '#cbd5e1';
                };

                const getSupportComponents = (partName) => {
                    const part = normalizePartName(partName || 'front bumper');
                    const supportParts = {
                        'front bumper': ['Front Bumper', 'Lower Bumper', 'RT Fog Lamp Cover', 'LT Fog Lamp Cover', 'Lower Grille', 'Lower Valance', 'Tow Hook Cover'],
                        grille: ['Upper Grille', 'Lower Grille', 'Grille Insert', 'Grille Mounting Tabs', 'Grille Emblem'],
                        headlight: ['Headlight Housing', 'Headlight Lens', 'RT Headlamp', 'LT Headlamp', 'Lamp Adjuster', 'Harness'],
                        hood: ['Hood Skin', 'Hood Hinge', 'Hood Latch', 'Hood Insulation', 'Hood Support'],
                        fender: ['Front Fender', 'Fender Liner', 'Fender Molding', 'Wheelhouse', 'Fender Bracket'],
                        windshield: ['Windshield Glass', 'Windshield Molding', 'Weatherstrip', 'Sealant', 'Adhesive'],
                        'front door': ['Front Door Shell', 'Door Inner Panel', 'Door Glass', 'Window Regulator', 'Door Hinges'],
                        'rear door': ['Rear Door Shell', 'Door Inner Panel', 'Door Glass', 'Window Regulator', 'Door Hinges'],
                        'quarter panel': ['Quarter Panel Outer', 'Quarter Panel Inner', 'Wheelhouse', 'Molding', 'Quarter Panel Brace'],
                        bedside: ['Bedside Outer', 'Bedside Inner', 'Bedside Bracket', 'Bedside Molding', 'Support Brace'],
                        'rear bumper': ['Rear Bumper Cover', 'Rear Bumper Reinforcement', 'Energy Absorber', 'Bracket Set'],
                        'tail light': ['Tail Lamp Housing', 'Tail Lamp Lens', 'Gasket', 'Mounting Clips'],
                        'tailgate': ['Tailgate Shell', 'Tailgate Hinges', 'Tailgate Latch', 'Support Cables'],
                        liftgate: ['Liftgate Shell', 'Liftgate Hinges', 'Liftgate Striker', 'Glass'],
                        roof: ['Roof Skin', 'Roof Bow', 'Weatherstrip', 'Trim'],
                        'radiator support': ['Core Support', 'Support Braces', 'Mounting Tabs', 'Fascia Support'],
                        radiator: ['Radiator Core', 'Fan Shroud', 'Upper Hose', 'Lower Hose'],
                        condenser: ['Condenser Core', 'Line Set', 'Mounting Bracket', 'Seal'],
                        frame: ['Left Rail', 'Right Rail', 'Crossmember', 'Mounting Tabs']
                    };

                    return supportParts[part] || supportParts['front bumper'];
                };

                const estimateSelectedLines = [];

                const ensureEstimateLineForPart = (partName) => {
                    const normalized = normalizePartName(partName || 'front bumper');
                    const existing = estimateSelectedLines.find((line) => normalizePartName(line.part) === normalized);
                    if (existing) return existing;

                    const line = {
                        part: normalized,
                        partNumber: '',
                        description: normalized,
                        qty: 1,
                        price: 0,
                        body: 0,
                        paint: 0
                    };
                    estimateSelectedLines.push(line);
                    return line;
                };

                const saveEstimateLineFromRow = (rowIndex) => {
                    const row = estimateSelectedLines[rowIndex];
                    if (!row) return;
                    const rowEl = estimateLineList?.querySelector(`[data-row-index="${rowIndex}"]`);
                    if (!rowEl) return;

                    const descriptionInput = rowEl.querySelector('[data-field="description"]');
                    const qtyInput = rowEl.querySelector('[data-field="qty"]');
                    const partInput = rowEl.querySelector('[data-field="partNumber"]');
                    const priceInput = rowEl.querySelector('[data-field="price"]');
                    const bodyInput = rowEl.querySelector('[data-field="body"]');
                    const paintInput = rowEl.querySelector('[data-field="paint"]');

                    row.description = (descriptionInput?.value || row.part || '').trim() || row.part || '';
                    row.qty = Number(qtyInput?.value || 1) || 1;
                    row.partNumber = partInput?.value || '';
                    row.price = Number(priceInput?.value || 0) || 0;
                    row.body = Number(bodyInput?.value || 0) || 0;
                    row.paint = Number(paintInput?.value || 0) || 0;

                    renderEstimateLines();
                };

                const renderEstimateLines = () => {
                    if (!estimateLineList) return;
                    if (!estimateSelectedLines.length) {
                        estimateLineList.innerHTML = `
                            <div style="display:flex; align-items:center; justify-content:center; min-height:160px; border:1px dashed #dfe6ee; border-radius:12px; background:#fafbfc; color:#64748b; font-size:14px; font-weight:600;">
                                No selected parts yet.
                            </div>
                        `;
                        return;
                    }

                    const rows = estimateSelectedLines.map((line, index) => `
                        <div data-row-index="${index}" style="display:grid; grid-template-columns:68px 1.3fr 80px 120px 100px 100px 100px; align-items:center; gap:8px; padding:10px 12px; border:1px solid #e2e8f0; border-radius:10px; background:#f8fafc; font-size:12px; color:#111827;">
                            <div style="font-weight:800; color:#334155;">${index + 1}</div>
                            <input data-field="description" data-row-index="${index}" value="${(line.description || line.part || '').replace(/"/g, '&quot;')}" style="width:100%; border:1px solid #dfe6ee; border-radius:8px; background:#fff; padding:6px 8px; font-size:12px; color:#111827; box-sizing:border-box;" />
                            <input data-field="qty" data-row-index="${index}" type="number" min="0" step="1" value="${Number(line.qty || 1)}" style="width:100%; border:1px solid #dfe6ee; border-radius:8px; background:#fff; padding:6px 8px; font-size:12px; color:#111827; box-sizing:border-box; text-align:center;" />
                            <input data-field="partNumber" data-row-index="${index}" value="${(line.partNumber || '').replace(/"/g, '&quot;')}" placeholder="" style="width:100%; border:1px solid #dfe6ee; border-radius:8px; background:#fff; padding:6px 8px; font-size:12px; color:#111827; box-sizing:border-box;" />
                            <input data-field="price" data-row-index="${index}" type="number" min="0" step="0.01" value="${Number(line.price || 0).toFixed(2)}" style="width:100%; border:1px solid #dfe6ee; border-radius:8px; background:#fff; padding:6px 8px; font-size:12px; color:#111827; box-sizing:border-box; text-align:right;" />
                            <input data-field="body" data-row-index="${index}" type="number" min="0" step="0.01" value="${Number(line.body || 0).toFixed(2)}" style="width:100%; border:1px solid #dfe6ee; border-radius:8px; background:#fff; padding:6px 8px; font-size:12px; color:#111827; box-sizing:border-box; text-align:right;" />
                            <input data-field="paint" data-row-index="${index}" type="number" min="0" step="0.01" value="${Number(line.paint || 0).toFixed(2)}" style="width:100%; border:1px solid #dfe6ee; border-radius:8px; background:#fff; padding:6px 8px; font-size:12px; color:#111827; box-sizing:border-box; text-align:right;" />
                        </div>
                    `).join('');

                    estimateLineList.innerHTML = `
                        <div style="display:flex; flex-direction:column; gap:8px; min-width:760px;">
                            <div style="display:grid; grid-template-columns:68px 1.3fr 80px 120px 100px 100px 100px; align-items:center; gap:8px; padding:8px 12px; border-bottom:1px solid #e2e8f0; font-size:11px; letter-spacing:0.08em; text-transform:uppercase; color:#475569; font-weight:800;">
                                <div>Line #</div>
                                <div>Description</div>
                                <div style="text-align:center;">Qty</div>
                                <div style="text-align:center;">Part #</div>
                                <div style="text-align:right;">Price</div>
                                <div style="text-align:right;">Body</div>
                                <div style="text-align:right;">Paint</div>
                            </div>
                            ${rows}
                        </div>
                    `;

                    estimateLineList.querySelectorAll('input').forEach((input) => {
                        input.addEventListener('keydown', (event) => {
                            if (event.key === 'Enter') {
                                event.preventDefault();
                                const rowIndex = Number(input.getAttribute('data-row-index') || 0);
                                saveEstimateLineFromRow(rowIndex);
                            }
                        });
                    });
                };

                const buildSchematicSvg = (partName, bodyType, make = '', model = '') => {
                    const part = normalizePartName(partName || 'front bumper');
                    const profile = getVehicleProfile(make, model) || bodyType || 'car';
                    const selectedPart = part;
                    const vehicleImage = getVehicleImageAsset(make, model);

                    return `
                        <div style="width:100%; max-width:980px; margin:0 auto;">
                            <div style="position:relative; width:100%; border:1px solid #dfe6ee; border-radius:14px; overflow:hidden; background:linear-gradient(180deg,#f8fafc 0%, #eef2ff 100%); box-shadow:inset 0 0 0 1px rgba(148,163,184,0.12);">
                                <img src="${vehicleImage}" alt="${profile} vehicle schematic" style="display:block; width:100%; height:auto; max-height:360px; object-fit:contain; background:#fff;" />
                            </div>
                            <div style="margin-top:14px; border:1px solid #e2e8f0; border-radius:12px; background:#fff; padding:14px; box-sizing:border-box;">
                                <div style="font-size:11px; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:#475569; margin-bottom:10px;">Component Group</div>
                                <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:10px; flex-wrap:wrap;">
                                    <div style="font-size:16px; font-weight:800; color:#111827; text-transform:capitalize;">${selectedPart}</div>
                                    <div style="font-size:12px; color:#475569; font-weight:700;">${make || 'Vehicle'} ${model || ''}</div>
                                </div>
                                <div style="display:flex; flex-wrap:wrap; gap:8px;">
                                    ${getSupportComponents(selectedPart).map((item) => `
                                        <span style="display:inline-flex; align-items:center; padding:6px 10px; border-radius:999px; background:#f8fafc; border:1px solid #e2e8f0; font-size:12px; color:#111827; font-weight:600;">${item}</span>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                };

                const renderIllustration = () => {
                    const make = makeSelect?.value || '';
                    const model = modelSelect?.value || '';
                    const selectedPart = categoryList?.dataset.selectedPart || 'front bumper';
                    const bodyType = getVehicleBodyType(make, model);
                    const svgMarkup = buildSchematicSvg(selectedPart, bodyType, make, model);
                    if (illustrationArea) {
                        illustrationArea.innerHTML = svgMarkup;
                    }
                };

                const renderCategories = () => {
                    const estimateWorkPanel = win.document.getElementById('estimateWorkPanel');
                    if (estimateWorkPanel && estimateWorkPanel.style.display === 'none') {
                        clearEstimateWorkContent();
                        return;
                    }

                    const make = makeSelect?.value || '';
                    const model = modelSelect?.value || '';
                    const categories = getVehicleCategoryList(make, model);
                    if (!categoryList) return;
                    const selectedPart = normalizePartName(categoryList.dataset.selectedPart || categories[0] || 'front bumper');
                    categoryList.dataset.selectedPart = selectedPart;
                    categoryList.innerHTML = categories.map((category) => {
                        const normalized = normalizePartName(category);
                        const isSelected = normalized === selectedPart;
                        return `
                            <button type="button" data-part="${category}" style="width:100%; text-align:left; border:1px solid ${isSelected ? '#b22222' : '#e2e8f0'}; background:${isSelected ? '#fff1f2' : '#f8fafc'}; color:#111827; border-radius:10px; padding:10px 12px; font-size:14px; font-weight:600; cursor:pointer; text-transform:capitalize; ${isSelected ? 'box-shadow: inset 0 0 0 1px rgba(178,34,34,0.2);' : ''}">
                                ${category}
                            </button>
                        `;
                    }).join('');

                    categoryList.querySelectorAll('button[data-part]').forEach((button) => {
                        button.addEventListener('click', () => {
                            const chosen = button.getAttribute('data-part');
                            categoryList.dataset.selectedPart = normalizePartName(chosen);
                            ensureEstimateLineForPart(chosen);
                            renderEstimateLines();
                            renderIllustration();
                            renderCategories();
                        });
                    });

                    renderIllustration();
                };

                const estimateNotesHistory = [];
                const estimateRatesState = { ...defaultRateValues };

                const getLocalDateTimeStamp = (date = new Date()) => {
                    const pad = (value) => String(value).padStart(2, '0');
                    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
                };

                const collectEstimateRateValues = () => {
                    const nextState = { ...defaultRateValues };
                    const inputs = win.document.querySelectorAll('.estimate-rate-input');
                    inputs.forEach((input) => {
                        const key = input.getAttribute('data-rate-key');
                        if (!key) return;
                        const value = Number(input.value || 0);
                        nextState[key] = Number.isFinite(value) ? value : 0;
                    });
                    Object.assign(estimateRatesState, nextState);
                    return { ...estimateRatesState };
                };

                const renderNotesHistory = () => {
                    const notesHistory = win.document.getElementById('estimateNotesHistory');
                    if (!notesHistory) return;
                    if (!estimateNotesHistory.length) {
                        notesHistory.innerHTML = '<div style="color:#64748b; font-size:14px; font-weight:600;">No notes yet.</div>';
                        return;
                    }

                    notesHistory.innerHTML = estimateNotesHistory.map((note) => `
                        <div style="border:1px solid #e5e7eb; border-radius:12px; background:#f8fafc; padding:12px 14px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:8px;">
                                <div style="font-weight:700; color:#111827;">${note.user}</div>
                                <div style="font-size:12px; color:#64748b;">${note.timestamp}</div>
                            </div>
                            <div style="white-space:pre-wrap; color:#334155; line-height:1.5;">${note.text}</div>
                        </div>
                    `).join('');
                };

                const clearEstimateWorkContent = () => {
                    if (categoryList) {
                        categoryList.innerHTML = '';
                        categoryList.dataset.actionMenuFor = '';
                    }
                    if (illustrationArea) illustrationArea.innerHTML = '';
                    if (estimateLineList) estimateLineList.innerHTML = '';
                    estimateSelectedLines.length = 0;
                };

                const setEstimateView = (viewName) => {
                    const navButtons = win.document.querySelectorAll('.estimate-nav-button');
                    navButtons.forEach((button) => {
                        const isSelected = button.getAttribute('data-estimate-view') === viewName;
                        button.classList.toggle('estimate-nav-button-selected', isSelected);
                        button.style.borderColor = isSelected ? '#f3c4c8' : '#e5e7eb';
                        button.style.background = isSelected ? 'linear-gradient(180deg, #fff1f2 0%, #fff 100%)' : '#fff';
                        button.style.color = isSelected ? '#b22222' : '#374151';
                        button.style.boxShadow = isSelected ? 'inset 0 0 0 1px rgba(178,34,34,0.08), 0 6px 14px rgba(178,34,34,0.08)' : 'none';
                    });

                    const customerVehiclePanel = win.document.getElementById('estimateCustomerVehiclePanel');
                    const estimateWorkPanel = win.document.getElementById('estimateWorkPanel');
                    const ratesPanel = win.document.getElementById('estimateRatesPanel');
                    const notesPanel = win.document.getElementById('estimateNotesPanel');

                    if (customerVehiclePanel) customerVehiclePanel.style.display = viewName === 'customerVehicle' ? 'flex' : 'none';
                    if (estimateWorkPanel) estimateWorkPanel.style.display = viewName === 'estimate' ? 'flex' : 'none';
                    if (ratesPanel) ratesPanel.style.display = viewName === 'rates' ? 'block' : 'none';
                    if (notesPanel) notesPanel.style.display = viewName === 'notes' ? 'block' : 'none';

                    if (viewName === 'estimate') {
                        renderCategories();
                    } else {
                        clearEstimateWorkContent();
                    }
                };

                const addEstimateNote = () => {
                    const notesInput = win.document.getElementById('estimateNotesInput');
                    if (!notesInput) return;
                    const text = notesInput.value.trim();
                    if (!text) {
                        notesInput.focus();
                        return;
                    }
                    estimateNotesHistory.unshift({
                        text,
                        user: (window.currentUserName || window.user?.name || 'Current User'),
                        timestamp: getLocalDateTimeStamp(new Date())
                    });
                    notesInput.value = '';
                    renderNotesHistory();
                };

                const applyPanelLayout = (isCollapsed) => {
                    if (!leftPane || !rightPane || !infoPane || !categoryPane) return;
                    if (isCollapsed) {
                        infoPane.style.transform = 'translateX(-120%)';
                        infoPane.style.opacity = '0';
                        infoPane.style.pointerEvents = 'none';
                        infoPane.style.visibility = 'hidden';
                        infoPane.style.maxWidth = '0';
                        infoPane.style.flex = '0 0 0px';
                        infoPane.style.width = '0';
                        infoPane.style.minWidth = '0';
                        infoPane.style.marginRight = '-18px';
                        categoryPane.style.flex = '1 1 auto';
                        leftPane.style.flex = '0.8';
                        rightPane.style.flex = '1.7';
                    } else {
                        infoPane.style.transform = 'translateX(0)';
                        infoPane.style.opacity = '1';
                        infoPane.style.pointerEvents = 'auto';
                        infoPane.style.visibility = 'visible';
                        infoPane.style.maxWidth = 'none';
                        infoPane.style.flex = '1.4';
                        infoPane.style.width = 'auto';
                        infoPane.style.minWidth = '0';
                        infoPane.style.marginRight = '0';
                        categoryPane.style.flex = '0 0 220px';
                        leftPane.style.flex = '1.2';
                        rightPane.style.flex = '1.4';
                    }
                };

                if (productionDateInput) {
                    productionDateInput.addEventListener('input', (event) => {
                        const raw = event.target.value.replace(/[^0-9]/g, '').slice(0, 6);
                        if (!raw) {
                            event.target.value = '';
                            return;
                        }
                        let month = raw.slice(0, 2);
                        const year = raw.slice(2, 6);
                        if (month.length === 1) month = month.padStart(2, '0');
                        if (Number(month) > 12) month = '12';
                        event.target.value = year ? `${month}/${year}` : month;
                    });
                }

                if (makeSelect) {
                    makeSelect.innerHTML = createMakeOptions();
                    makeSelect.addEventListener('change', () => {
                        modelSelect.innerHTML = createModelOptions(makeSelect.value, '');
                        renderCategories();
                    });
                }

                if (modelSelect) {
                    modelSelect.addEventListener('change', renderCategories);
                }

                win.document.querySelectorAll('.estimate-nav-button').forEach((button) => {
                    button.addEventListener('click', () => {
                        setEstimateView(button.getAttribute('data-estimate-view') || 'customerVehicle');
                    });
                });

                const addNoteButton = win.document.getElementById('estimateAddNoteButton');
                if (addNoteButton) {
                    addNoteButton.addEventListener('click', addEstimateNote);
                    const notesInput = win.document.getElementById('estimateNotesInput');
                    if (notesInput) {
                        notesInput.addEventListener('keydown', (event) => {
                            if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                                addEstimateNote();
                            }
                        });
                    }
                }

                setEstimateView('customerVehicle');
                renderNotesHistory();

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
                        const estimateRates = collectEstimateRateValues();

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
                            estimate_snapshot: {
                                rates: estimateRates,
                                notes: [...estimateNotesHistory]
                            },
                            estimate_rates: estimateRates,
                            estimate_notes: [...estimateNotesHistory],
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

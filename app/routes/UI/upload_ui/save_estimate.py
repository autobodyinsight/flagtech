"""Save estimate modal and functions."""

import json


def get_save_estimate_modal_html(
  second_ro_line,
  vehicle_info_line,
  total_labor,
  total_paint,
  parts_total,
  grand_total,
  deductible,
  customer_pay,
  insurance_pay,
):
    """Return the HTML for the save estimate modal."""
    return f"""
<div id="saveEstimateModal" class="modal" style="display: none;">
  <div class="modal-content modal-large">
    <span class="close" onclick="closeSaveEstimateModal()">&times;</span>

    <div style="margin-bottom: 15px;">
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 5px;">{second_ro_line}</div>
      <div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>
      <div style="margin-top: 10px; padding: 12px; background-color: #f9f9f9; border-radius: 3px; border: 1px solid #ddd;">
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
          <div>
            <label style="font-weight: bold; font-size: 12px; color: #666;">YEAR</label>
            <div id="vehicleYear" style="font-size: 14px; margin-top: 3px;">-</div>
          </div>
          <div>
            <label style="font-weight: bold; font-size: 12px; color: #666;">MAKE</label>
            <div id="vehicleMake" style="font-size: 14px; margin-top: 3px;">-</div>
          </div>
          <div>
            <label style="font-weight: bold; font-size: 12px; color: #666;">MODEL</label>
            <div id="vehicleModel" style="font-size: 14px; margin-top: 3px;">-</div>
          </div>
        </div>
      </div>
    </div>

    <h2>Save Estimate Data</h2>

    <!-- Tabs for Labor, Paint, and Estimate Totals -->
    <div style="display: flex; gap: 10px; margin-bottom: 15px; border-bottom: 2px solid #ddd;">
      <button onclick="switchTab('repairsTab')" class="tab-button active" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#f0f0f0; border:none; border-bottom:3px solid #505050;'>REPAIRS</button>
      <button onclick="switchTab('totalsTab')" class="tab-button" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#f0f0f0; border:none;'>ESTIMATE TOTALS</button>
    </div>

    <!-- Repairs Tab -->
    <div id="repairsTab" class="tab-content" style="display: block;">
      <div style="margin-bottom: 15px;">
        <h3>Labor Repairs</h3>
        <div id="saveEstimateLaborList" class="repair-list"></div>
        <div class="repair-total">Total Labor: <span id="saveEstimateTotalLabor">{total_labor}</span> hrs</div>
      </div>

      <div style="margin-bottom: 15px;">
        <h3>Refinish Repairs</h3>
        <div id="saveEstimatePaintList" class="repair-list"></div>
        <div class="repair-total">Total Refinish: <span id="saveEstimateTotalPaint">{total_paint}</span> hrs</div>
      </div>

      <div style="margin-bottom: 15px;">
        <h3>Parts Replacements</h3>
        <div id="saveEstimatePartsList" class="repair-list"></div>
      </div>
    </div>

    <!-- Estimate Totals Tab -->
    <div id="totalsTab" class="tab-content" style="display: none;">
      <div style="padding: 15px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px;">
        <h3>Estimate Summary</h3>
        <div id="saveEstimateTotalsSummary" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;"></div>
      </div>
    </div>

    <!-- Save Status -->
    <div id="saveEstimateStatus" style="margin-top: 15px; text-align: center; font-weight: bold; min-height: 20px;"></div>

    <!-- Action Buttons -->
    <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
      <button onclick="closeSaveEstimateModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#999; color:white; border:none; border-radius:3px;'>Cancel</button>
      <button onclick="executeSaveEstimate()" id="executeSaveBtn" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#4CAF50; color:white; border:none; border-radius:3px;'>Save Estimate</button>
    </div>
  </div>
</div>
"""


def get_save_estimate_modal_styles():
    """Return the CSS styles for the save estimate modal."""
    return """
.modal-large {
  max-width: 900px;
  max-height: 80vh;
  overflow-y: auto;
}
.tab-button {
  transition: all 0.3s ease;
}
.tab-button.active {
  border-bottom: 3px solid #505050 !important;
  background-color: white !important;
}
.tab-content {
  padding: 15px 0;
}
.repair-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 3px;
  margin-bottom: 10px;
}
.repair-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}
.repair-item:hover {
  background-color: #f9f9f9;
}
.repair-item-label {
  flex: 1;
  font-size: 13px;
}
.repair-item-value {
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}
.repair-total {
  padding: 10px 12px;
  font-weight: bold;
  background-color: #f0f0f0;
  text-align: right;
  border-radius: 3px;
  margin-top: 5px;
}
.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}
.total-label {
  font-weight: bold;
  flex: 1;
}
.total-value {
  font-weight: bold;
  min-width: 100px;
  text-align: right;
}
"""


def get_save_estimate_modal_script(
  labor_items_json,
  paint_items_json,
  parts_items_json,
  second_ro_line,
  vehicle_info_line,
  ro_number,
  total_labor,
  total_paint,
  parts_total,
  grand_total,
  deductible,
  customer_pay,
  insurance_pay,
):
    """Return the JavaScript for the save estimate modal functionality."""
    return f"""
// Save Estimate Modal Variables
var saveLaborItems = {labor_items_json};
var savePaintItems = {paint_items_json};
var savePartsItems = {parts_items_json};
var saveRoNumber = {json.dumps(ro_number or '').replace("<", "\\u003c")};
var saveSecondRoLine = {json.dumps(second_ro_line or '').replace("<", "\\u003c")};
var saveVehicleInfoLine = {json.dumps(vehicle_info_line or '').replace("<", "\\u003c")};
var saveEstimateTotalsData = {{}};
var preloadedEstimateTotals = {json.dumps({
    "parts_total": parts_total,
    "grand_total": grand_total,
    "deductible": deductible,
    "customer_pay": customer_pay,
    "insurance_pay": insurance_pay,
})};

if (
  typeof window.currentEstimateTotals === 'undefined' ||
  !window.currentEstimateTotals ||
  Object.keys(window.currentEstimateTotals).length === 0
) {{
  window.currentEstimateTotals = preloadedEstimateTotals;
}} else {{
  window.currentEstimateTotals = Object.assign({{}}, preloadedEstimateTotals, window.currentEstimateTotals);
}}

// Vehicle info parsed from vehicle_info_line
var vehicleYear = null;
var vehicleMake = null;
var vehicleModel = null;

var apiBase = window.API_BASE || 'https://flagtech1.onrender.com';

function parseVehicleInfo(vehicleStr) {{
  if (!vehicleStr) return {{year: null, make: null, model: null}};
  
  // Extract year (4 digits starting with 19 or 20)
  const yearMatch = vehicleStr.match(/\\b(19\\d{{2}}|20\\d{{2}})\\b/);
  const year = yearMatch ? yearMatch[1] : null;
  
  // Remove year from string for make/model parsing
  const remaining = yearMatch ? vehicleStr.replace(yearMatch[0], '').trim() : vehicleStr.trim();
  
  // Split remaining text - typically: Make Model [trim/body info]
  const parts = remaining.split(/\\s+/);
  const make = parts.length > 0 ? parts[0] : null;
  const model = parts.length > 1 ? parts[1] : null;
  
  return {{year, make, model}};
}}

function getAuthHeaders() {{
  const token = localStorage.getItem('auth_token');
  const headers = {{}};
  if (token) {{
    headers['Authorization'] = `Bearer ${{token}}`;
  }}
  return headers;
}}

function normalizeSummaryValue(raw) {{
  if (raw === null || raw === undefined) return null;
  if (typeof raw === 'number') return raw;
  if (typeof raw !== 'string') return null;
  const trimmed = raw.trim();
  if (!trimmed || trimmed === '-' || trimmed.toLowerCase() === 'null') return null;
  const numeric = trimmed.replace(/[^0-9.-]/g, '');
  if (!numeric) return trimmed;
  const parsed = parseFloat(numeric);
  return Number.isNaN(parsed) ? trimmed : parsed;
}}

function resolvePartType(item) {{
  if (!item) return 'OEM';
  const explicit = String(item.part_type || '').trim();
  if (explicit) return explicit;
  const description = String(item.description || '').toUpperCase();
  const rowText = String(item.row_text || '').toUpperCase();
  const combined = description + ' ' + rowText;
  if (combined.includes('LKQ')) return 'LKQ';
  if (combined.includes('A/M') || combined.includes('A M') || combined.includes('AFTERMARKET')) return 'A/M';
  return 'OEM';
}}

function formatPartPrice(value) {{
  if (value === null || value === undefined || value === '') return '-';
  const parsed = parseFloat(value);
  if (!Number.isFinite(parsed)) return value;
  const fixed = parsed.toFixed(2);
  return fixed.endsWith('.00') ? String(parseInt(fixed, 10)) : fixed;
}}

function formatEstimateValue(value) {{
  const normalized = normalizeSummaryValue(value);
  if (normalized === null || normalized === undefined) return '-';
  if (typeof normalized === 'number' && Number.isFinite(normalized)) {{
    return normalized.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
  }}
  return normalized;
}}

function readSummaryValue(elementId) {{
  const el = document.getElementById(elementId);
  if (!el) return null;
  return normalizeSummaryValue(el.textContent);
}}

function resolveEstimateTotals(estimateTotals) {{
  const baseTotals = estimateTotals && typeof estimateTotals === 'object' ? estimateTotals : {{}};
  const fallbackTotals = (typeof currentEstimateTotals !== 'undefined' && currentEstimateTotals && typeof currentEstimateTotals === 'object')
    ? currentEstimateTotals
    : (window.currentEstimateTotals && typeof window.currentEstimateTotals === 'object')
      ? window.currentEstimateTotals
      : {{}};

  const totalDefs = [
    {{key: 'parts_total', label: 'PARTS TOTAL', fallbackId: 'summaryPartsTotal'}},
    {{key: 'grand_total', label: 'GRAND TOTAL', fallbackId: 'summaryGrandTotal'}},
    {{key: 'deductible', label: 'DEDUCTIBLE', fallbackId: 'summaryDeductible'}},
    {{key: 'customer_pay', label: 'CUSTOMER PAY', fallbackId: 'summaryCustomerPay'}},
    {{key: 'insurance_pay', label: 'INSURANCE PAY', fallbackId: 'summaryInsurancePay'}},
  ];

  const resolved = {{}};
  totalDefs.forEach((def) => {{
    let value = baseTotals[def.key];
    if (value === null || value === undefined) {{
      value = fallbackTotals[def.key];
    }}
    if (value === null || value === undefined) {{
      value = readSummaryValue(def.fallbackId);
    }}
    resolved[def.key] = value;
  }});

  return {{resolved, totalDefs}};
}}

function switchTab(tabName) {{
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
  
  // Show selected tab
  document.getElementById(tabName).style.display = 'block';
  event.target.classList.add('active');
}}

function openSaveEstimateModal(estimateTotals) {{
  // Store estimate totals globally
  const resolvedTotals = resolveEstimateTotals(estimateTotals);
  saveEstimateTotalsData = resolvedTotals.resolved;
  
  // Parse vehicle info
  const vehicleInfo = parseVehicleInfo(saveVehicleInfoLine);
  vehicleYear = vehicleInfo.year;
  vehicleMake = vehicleInfo.make;
  vehicleModel = vehicleInfo.model;
  
  const modal = document.getElementById('saveEstimateModal');
  
  // Display vehicle information
  document.getElementById('vehicleYear').textContent = vehicleYear || '-';
  document.getElementById('vehicleMake').textContent = vehicleMake || '-';
  document.getElementById('vehicleModel').textContent = vehicleModel || '-';
  
  // Populate labor repairs
  let laborHtml = '';
  if (saveLaborItems.length === 0) {{
    laborHtml = '<p style="padding: 12px; color: #666;">No labor items found.</p>';
  }} else {{
    saveLaborItems.forEach((item, index) => {{
      laborHtml += '<div class="repair-item" id="labor-item-' + index + '">';
      laborHtml += '<div class="repair-item-label"><strong>Line ' + item.line + '</strong> - ' + item.description + '</div>';
      laborHtml += '<div class="repair-item-value">' + parseFloat(item.value).toFixed(1) + ' hrs</div>';
      laborHtml += '</div>';
    }});
  }}
  document.getElementById('saveEstimateLaborList').innerHTML = laborHtml;
  
  // Populate paint repairs
  let paintHtml = '';
  if (savePaintItems.length === 0) {{
    paintHtml = '<p style="padding: 12px; color: #666;">No paint items found.</p>';
  }} else {{
    savePaintItems.forEach((item, index) => {{
      paintHtml += '<div class="repair-item" id="paint-item-' + index + '">';
      paintHtml += '<div class="repair-item-label"><strong>Line ' + item.line + '</strong> - ' + item.description + '</div>';
      paintHtml += '<div class="repair-item-value">' + parseFloat(item.value).toFixed(1) + ' hrs</div>';
      paintHtml += '</div>';
    }});
  }}
  document.getElementById('saveEstimatePaintList').innerHTML = paintHtml;

  // Populate parts replacements
  let partsHtml = '';
  let partsCount = 0;
  if (savePartsItems && savePartsItems.length > 0) {{
    savePartsItems.forEach((item) => {{
      const priceVal = parseFloat(item.price);
      if (!Number.isFinite(priceVal) || priceVal <= 0) {{
        return;
      }}
      const descText = String(item.description || '').trim();
      const rowText = String(item.row_text || '').trim();
      const sourceText = (rowText || descText).toLowerCase();
      if (!sourceText.includes('repl')) {{
        return;
      }}
      const partType = resolvePartType(item);
      const lineText = item.line ? ('Line ' + item.line + ' - ') : '';
      const priceText = '$' + formatPartPrice(priceVal);
      partsHtml += '<div class="repair-item" id="part-item-' + partsCount + '">';
      partsHtml += '<div class="repair-item-label"><strong>' + lineText + '</strong>' + descText + ' - ' + partType + '</div>';
      partsHtml += '<div class="repair-item-value">' + priceText + '</div>';
      partsHtml += '</div>';
      partsCount += 1;
    }});
  }}
  if (partsCount === 0) {{
    partsHtml = '<p style="padding: 12px; color: #666;">No parts items found.</p>';
  }}
  document.getElementById('saveEstimatePartsList').innerHTML = partsHtml;
  
  // Populate estimate totals summary
  let totalsHtml = '';
  resolvedTotals.totalDefs.forEach((def) => {{
    const value = saveEstimateTotalsData[def.key];
    const displayValue = formatEstimateValue(value);
    totalsHtml += '<div class="total-row"><div class="total-label">' + def.label + '</div><div class="total-value">' + displayValue + '</div></div>';
  }});
  document.getElementById('saveEstimateTotalsSummary').innerHTML = totalsHtml || '<p style="color:#666;">No totals data available.</p>';
  
  document.getElementById('saveEstimateStatus').textContent = '';
  
  modal.style.display = 'block';
}}

function closeSaveEstimateModal() {{
  document.getElementById('saveEstimateModal').style.display = 'none';
}}

function executeSaveEstimate() {{
  const saveBtn = document.getElementById('executeSaveBtn');
  const statusDiv = document.getElementById('saveEstimateStatus');
  
  if (saveLaborItems.length === 0 && savePaintItems.length === 0) {{
    statusDiv.textContent = 'No repair lines found to save';
    statusDiv.style.color = 'red';
    return;
  }}
  
  saveBtn.disabled = true;
  statusDiv.textContent = 'Saving...';
  statusDiv.style.color = 'blue';
  
  // Build payload
  const laborData = saveLaborItems.slice();
  const paintData = savePaintItems.slice();
  
  const payload = {{
    ro: saveRoNumber,
    vehicle: saveVehicleInfoLine,
    year: vehicleYear,
    make: vehicleMake,
    model: vehicleModel,
    labor_repairs: laborData,
    paint_repairs: paintData,
    estimate_totals: saveEstimateTotalsData,
    timestamp: new Date().toISOString()
  }};
  
  fetch('/ui/save-estimate', {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    }},
    body: JSON.stringify(payload),
    credentials: 'include'
  }})
  .then(response => response.json())
  .then(result => {{
    if (result.status === 'success') {{
      statusDiv.textContent = 'Saved successfully!';
      statusDiv.style.color = 'green';
      setTimeout(() => {{
        closeSaveEstimateModal();
        const uploadStatus = document.getElementById('uploadStatus');
        if (uploadStatus) {{
          uploadStatus.innerHTML = '';
        }}
        const estimateSummary = document.getElementById('estimateSummary');
        if (estimateSummary) {{
          estimateSummary.style.display = 'none';
        }}
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {{
          fileInput.value = '';
        }}
        statusDiv.textContent = '';
        saveBtn.disabled = false;
      }}, 2000);
    }} else {{
      statusDiv.textContent = 'Error: ' + (result.message || 'Failed to save');
      statusDiv.style.color = 'red';
      saveBtn.disabled = false;
    }}
  }})
  .catch(error => {{
    statusDiv.textContent = 'Error: ' + error.message;
    statusDiv.style.color = 'red';
    saveBtn.disabled = false;
  }});
}}

window.openSaveEstimateModal = openSaveEstimateModal;
window.executeSaveEstimate = executeSaveEstimate;
"""

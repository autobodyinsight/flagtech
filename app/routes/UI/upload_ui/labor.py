"""Labor assignment modal and functions."""

def get_labor_modal_html(second_ro_line, vehicle_info_line, total_labor):
    """Return the HTML for the labor assignment modal."""
    return f"""
<div id="laborModal" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closeLaborModal()">&times;</span>

    <div style="margin-bottom: 15px;">
      <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{second_ro_line}</div>
      <div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>
    </div>

    <div style="margin-bottom: 15px;">
      <label style="font-weight: bold; font-size: 14px;">TECH:</label>
      <input type="text" id="techInput" style="padding: 8px; font-size: 14px; margin-left: 10px; width: 200px; border: 1px solid #ccc; border-radius: 3px;" placeholder="Enter technician name" />
    </div>

    <h2>Labor Assignment</h2>

    <div id="laborList"></div>
    <div id="laborAdditionalHours"></div>

    <div class="labor-total">Total Labor: <span id="totalLabor">{total_labor}</span></div>

    <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: space-between;">
      <button onclick="addLaborAdditionalHours()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#666; color:white; border:none; border-radius:3px;'>Adtl HRS</button>

      <div style="display: flex; gap: 10px;">
        <button onclick="printModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Print</button>
        <button onclick="saveModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Save</button>
      </div>
    </div>

  </div>
</div>
"""


def get_labor_modal_styles():
    """Return the CSS styles for the labor modal."""
    return """
.labor-item {
  padding: 12px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
.labor-item.deducted {
  background-color: #f0f0f0;
  text-decoration: line-through;
  opacity: 0.6;
}
.labor-item-checkbox {
  cursor: pointer;
  width: 18px;
  height: 18px;
  margin-right: 10px;
}
.labor-total {
  padding: 12px 8px;
  font-weight: bold;
  background-color: #f0f0f0;
  margin-top: 10px;
  text-align: right;
}
.labor-additional-item {
  padding: 12px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background-color: #fffacd;
}
.labor-additional-item input[type="text"] {
  flex: 1;
  padding: 6px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 3px;
}
.labor-additional-item input[type="number"] {
  width: 80px;
  padding: 6px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 3px;
}
"""


def get_labor_modal_script(labor_items_json, total_labor, second_ro_line, vehicle_info_line):
    """Return the JavaScript for the labor modal functionality."""
    return f"""
const laborItems = {labor_items_json};
const initialTotal = {total_labor};
let laborAdditionalCounter = 0;

// This will store ONLY the items displayed in the modal
let displayLaborItems = [];

function addLaborAdditionalHours() {{
  const container = document.getElementById('laborAdditionalHours');
  const itemId = 'labor-addl-' + laborAdditionalCounter++;

  const itemDiv = document.createElement('div');
  itemDiv.className = 'labor-additional-item';
  itemDiv.id = itemId;

  itemDiv.innerHTML =
    '<input type="text" class="labor-addl-desc" placeholder="Enter description" />' +
    '<input type="number" class="labor-addl-value" step="0.1" placeholder="0.0" onchange="updateTotal()" /> hrs' +
    '<button onclick="removeLaborAdditionalItem(\\'' + itemId + '\\')">Remove</button>';

  container.appendChild(itemDiv);
}}

function removeLaborAdditionalItem(itemId) {{
  const item = document.getElementById(itemId);
  if (item) {{
    item.remove();
    updateTotal();
  }}
}}

function formatHours(val) {{
  const num = Number(val);
  return Number.isFinite(num) ? num.toFixed(1) : val;
}}

function updateTotal() {{
  const checkboxes = document.querySelectorAll('.labor-item-checkbox');
  let deductedTotal = 0;

  checkboxes.forEach((checkbox, index) => {{
    if (checkbox.checked) {{
      deductedTotal += displayLaborItems[index].value;
    }}
  }});

  let additionalTotal = 0;
  const additionalInputs = document.querySelectorAll('.labor-addl-value');
  additionalInputs.forEach(input => {{
    const val = parseFloat(input.value) || 0;
    additionalTotal += val;
  }});

  const newTotal = (initialTotal - deductedTotal + additionalTotal).toFixed(1);
  document.getElementById('totalLabor').innerText = newTotal;
}}

function toggleDeduction(index) {{
  const item = document.getElementById('item-' + index);
  item.classList.toggle('deducted');
  updateTotal();
}}

function openLaborModal() {{
  const modal = document.getElementById('laborModal');
  let html = '';

  // Store EXACTLY what is displayed
  displayLaborItems = laborItems.slice();

  if (displayLaborItems.length === 0) {{
    html = '<p>No labor items found.</p>';
  }} else {{
    displayLaborItems.forEach((item, index) => {{
      html += '<div class="labor-item" id="item-' + index + '">';
      html += '<input type="checkbox" class="labor-item-checkbox" onchange="toggleDeduction(' + index + ')" />';
      html += '<div style="flex: 1;"><strong>Line ' + item.line + '</strong> - ' + item.description + '</div>';
      html += '<div>' + formatHours(item.value) + ' hrs</div>';
      html += '</div>';
    }});
  }}

  document.getElementById('laborList').innerHTML = html;
  modal.style.display = 'block';
}}

function closeLaborModal() {{
  document.getElementById('laborModal').style.display = 'none';
}}

function printModal() {{
  const printWindow = window.open('', '', 'height=600,width=800');
  const techValue = document.getElementById('techInput').value;

  const checkboxes = document.querySelectorAll('.labor-item-checkbox');
  let deductedTotal = 0;

  let printContent = '<html><head><title>Labor Assignment</title></head><body style="font-family: Arial; padding: 20px;">';

  printContent += '<div style="margin-bottom: 15px;">';
  printContent += '<div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{second_ro_line}</div>';
  printContent += '<div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>';
  printContent += '</div>';

  printContent += '<div style="margin-bottom: 15px;">';
  printContent += '<label style="font-weight: bold; font-size: 14px;">TECH:</label>';
  printContent += '<span style="font-size: 14px; margin-left: 10px;">' + techValue + '</span>';
  printContent += '</div>';

  printContent += '<h2>Labor Assignment</h2>';

  let totalLabor = 0;

  checkboxes.forEach((checkbox, index) => {{
    if (!checkbox.checked) {{
      const item = displayLaborItems[index];
      printContent += '<div style="padding: 12px 8px; border-bottom: 1px solid #ddd;">';
      printContent += '<input type="checkbox" disabled style="margin-right: 10px;" />';
      printContent += '<strong>Line ' + item.line + '</strong> - ' + item.description;
      printContent += ' <div style="display: inline; float: right;">' + formatHours(item.value) + ' hrs</div>';
      printContent += '</div>';
      totalLabor += item.value;
    }} else {{
      deductedTotal += displayLaborItems[index].value;
    }}
  }});

  const additionalDescs = document.querySelectorAll('.labor-addl-desc');
  const additionalValues = document.querySelectorAll('.labor-addl-value');

  additionalDescs.forEach((descInput, index) => {{
    const desc = descInput.value;
    const val = parseFloat(additionalValues[index].value) || 0;

    if (desc || val) {{
      printContent += '<div style="padding: 12px 8px; border-bottom: 1px solid #ddd; background-color: #fffacd;">';
      printContent += '<input type="checkbox" disabled style="margin-right: 10px;" />';
      printContent += '<strong>Additional</strong> - ' + desc;
      printContent += ' <div style="display: inline; float: right;">' + formatHours(val) + ' hrs</div>';
      printContent += '</div>';
      totalLabor += val;
    }}
  }});

  printContent += '<div style="padding: 12px 8px; font-weight: bold; background-color: #f0f0f0; margin-top: 10px; text-align: right;">';
  printContent += 'Total Labor: ' + totalLabor.toFixed(1);
  printContent += '</div>';

  printContent += '</body></html>';

  printWindow.document.write(printContent);
  printWindow.document.close();
  printWindow.print();
}}

function saveModal() {{
  const checkboxes = document.querySelectorAll('.labor-item-checkbox');

  let assigned = [];
  let unassigned = [];

  checkboxes.forEach((checkbox, index) => {{
    const item = displayLaborItems[index];
    if (checkbox.checked) {{
      unassigned.push(item);
    }} else {{
      assigned.push(item);
    }}
  }});

  // Additional hours
  let additional = [];
  const descs = document.querySelectorAll('.labor-addl-desc');
  const values = document.querySelectorAll('.labor-addl-value');

  descs.forEach((descInput, i) => {{
    const desc = descInput.value;
    const val = parseFloat(values[i].value) || 0;
    if (desc || val) {{
      additional.push({{ description: desc, value: val }});
    }}
  }});

  const tech = document.getElementById('techInput').value;

  // 🔥 Only compute total unassigned
  const totalUnassigned = unassigned.reduce((sum, item) => sum + item.value, 0);

  // Already displayed in modal
  const totalLabor = parseFloat(document.getElementById('totalLabor').innerText) || 0;

  const data = {{
    assigned,
    unassigned,
    additional,
    totalUnassigned,   // 🔥 the only total you need
    totalLabor,        // already correct
    tech,
    ro: "{second_ro_line}",
    vehicle: "{vehicle_info_line}",
    timestamp: new Date().toISOString()
  }};

  fetch('https://flagtech1.onrender.com/ui/save-labor', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data)
  }})
  .then(r => r.json())
  .then(res => {{
    console.log("Labor saved:", res);
    closeLaborModal();
  }})
  .catch(err => console.error("Save labor error:", err));
}}
"""
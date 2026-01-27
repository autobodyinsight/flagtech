"""Refinish (paint) assignment modal and functions."""


def get_refinish_modal_html(second_ro_line, vehicle_info_line, total_paint):
    """Return the HTML for the refinish assignment modal."""
    return f"""
<div id="refinishModal" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closeRefinishModal()">&times;</span>
    <div style="margin-bottom: 15px;">
      <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{second_ro_line}</div>
      <div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>
    </div>
    <div style="margin-bottom: 15px;">
      <label style="font-weight: bold; font-size: 14px;">TECH:</label>
      <select id="refinishTechInput" style="padding: 8px; font-size: 14px; margin-left: 10px; width: 220px; border: 1px solid #ccc; border-radius: 3px;">
        <option value="">Select technician...</option>
      </select>
    </div>
    <h2>Refinish Assignment</h2>
    <div id="paintList"></div>
    <div id="paintAdditionalHours"></div>
    <div class="paint-total">Total Refinish: <span id="totalPaint">{total_paint}</span></div>
    <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: space-between;">
      <button onclick="addPaintAdditionalHours()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#666; color:white; border:none; border-radius:3px;'>Adtl HRS</button>
      <div style="display: flex; gap: 10px;">
        <button onclick="printRefinishModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Print</button>
        <button onclick="saveRefinishModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Save</button>
      </div>
    </div>
  </div>
</div>
"""


def get_refinish_modal_styles():
    """Return the CSS styles for the refinish modal."""
    return """
  .paint-item {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
  }
  .paint-item.deducted {
    background-color: #f0f0f0;
    text-decoration: line-through;
    opacity: 0.6;
  }
  .paint-item-checkbox {
    cursor: pointer;
    width: 18px;
    height: 18px;
    margin-right: 10px;
  }
  .paint-total {
    padding: 12px 8px;
    font-weight: bold;
    background-color: #f0f0f0;
    margin-top: 10px;
    text-align: right;
  }
  .paint-additional-item {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    background-color: #fffacd;
  }
  .paint-additional-item input[type="text"] {
    flex: 1;
    padding: 6px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 3px;
  }
  .paint-additional-item input[type="number"] {
    width: 80px;
    padding: 6px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 3px;
  }
"""


def get_refinish_modal_script(paint_items_json, total_paint, second_ro_line, vehicle_info_line):
    """Return the JavaScript for the refinish modal functionality."""
    return f"""
  // Refinish Modal Functions
  const paintItems = {paint_items_json};
  const initialPaintTotal = {total_paint};
  // This will store ONLY the items displayed in the modal
  let displayPaintItems = [];
  let paintAdditionalCounter = 0;

  function addPaintAdditionalHours() {{
    const container = document.getElementById('paintAdditionalHours');
    const itemId = 'paint-addl-' + paintAdditionalCounter++;
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'paint-additional-item';
    itemDiv.id = itemId;
    itemDiv.innerHTML = '<input type="text" class="paint-addl-desc" placeholder="Enter description" />' +
                        '<input type="number" class="paint-addl-value" step="0.1" placeholder="0.0" onchange="updatePaintTotal()" /> hrs' +
                        '<button onclick="removePaintAdditionalItem(\\'' + itemId + '\\')">Remove</button>';
    
    container.appendChild(itemDiv);
  }}
  
  function removePaintAdditionalItem(itemId) {{
    const item = document.getElementById(itemId);
    if (item) {{
      item.remove();
      updatePaintTotal();
    }}
  }}

  function formatHours(val) {{
    const num = Number(val);
    return Number.isFinite(num) ? num.toFixed(1) : val;
  }}
  
  function updatePaintTotal() {{
    const checkboxes = document.querySelectorAll('.paint-item-checkbox');
    let deductedTotal = 0;
    
    checkboxes.forEach((checkbox, index) => {{
      if (checkbox.checked) {{
        const item = displayPaintItems[index];
        if (item) {{
          deductedTotal += item.value;
        }}
      }}
    }});
    
    // Add additional hours
    let additionalTotal = 0;
    const additionalInputs = document.querySelectorAll('.paint-addl-value');
    additionalInputs.forEach(input => {{
      const val = parseFloat(input.value) || 0;
      additionalTotal += val;
    }});
    
    const newTotal = (initialPaintTotal - deductedTotal + additionalTotal).toFixed(1);
    document.getElementById('totalPaint').innerText = newTotal;
  }}
  
  function togglePaintDeduction(index) {{
    const item = document.getElementById('paint-item-' + index);
    item.classList.toggle('deducted');
    updatePaintTotal();
  }}

  function loadTechsIntoRefinishDropdown() {{
    fetch('https://flagtech1.onrender.com/api/techs/list')
      .then(r => r.json())
      .then(data => {{
        const select = document.getElementById('refinishTechInput');
        select.innerHTML = '<option value="">Select technician...</option>';
        
        if (data.techs && data.techs.length > 0) {{
          data.techs.forEach(tech => {{
            const option = document.createElement('option');
            option.value = `${{tech.first_name}} ${{tech.last_name}}`;
            option.textContent = `${{tech.first_name}} ${{tech.last_name}}`;
            select.appendChild(option);
          }});
        }}
      }})
      .catch(err => {{
        console.error('Error loading techs:', err);
      }});
  }}
  
  function openRefinishModal() {{
    const modal = document.getElementById('refinishModal');
    let html = '';

    // Load techs into dropdown
    loadTechsIntoRefinishDropdown();

    // Store EXACTLY what is displayed
    displayPaintItems = paintItems.slice();
    
    if (displayPaintItems.length === 0) {{
      html = '<p>No refinish items found.</p>';
    }} else {{
      displayPaintItems.forEach((item, index) => {{
        html += '<div class="paint-item" id="paint-item-' + index + '">';
        html += '<input type="checkbox" class="paint-item-checkbox" onchange="togglePaintDeduction(' + index + ')" />';
        html += '<div style="flex: 1;"><strong>Line ' + item.line + '</strong> - ' + item.description + '</div>';
        html += '<div>' + formatHours(item.value) + ' hrs</div>';
        html += '</div>';
      }});
    }}
    
    document.getElementById('paintList').innerHTML = html;
    modal.style.display = 'block';
  }}
  
  function closeRefinishModal() {{
    document.getElementById('refinishModal').style.display = 'none';
  }}
  
  function printRefinishModal() {{
    const printWindow = window.open('', '', 'height=600,width=800');
    const techValue = document.getElementById('refinishTechInput').value;
    
    const checkboxes = document.querySelectorAll('.paint-item-checkbox');
    let deductedTotal = 0;
    let printContent = '<html><head><title>Refinish Assignment</title></head><body style="font-family: Arial; padding: 20px;">';
    
    printContent += '<div style="margin-bottom: 15px;">';
    printContent += '<div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{second_ro_line}</div>';
    printContent += '<div style="font-size: 14px; color: #333;">{vehicle_info_line}</div>';
    printContent += '</div>';
    printContent += '<div style="margin-bottom: 15px;">';
    printContent += '<label style="font-weight: bold; font-size: 14px;">TECH:</label>';
    printContent += '<span style="font-size: 14px; margin-left: 10px;">' + techValue + '</span>';
    printContent += '</div>';
    
    printContent += '<h2>Refinish Assignment</h2>';
    
    let totalPaint = 0;
    checkboxes.forEach((checkbox, index) => {{
      const item = displayPaintItems[index];
      if (!item) {{
        return;
      }}
      if (!checkbox.checked) {{
        printContent += '<div style="padding: 12px 8px; border-bottom: 1px solid #ddd;">';
        printContent += '<input type="checkbox" disabled style="margin-right: 10px;" />';
        printContent += '<strong>Line ' + item.line + '</strong> - ' + item.description;
        printContent += ' <div style="display: inline; float: right;">' + formatHours(item.value) + ' hrs</div>';
        printContent += '</div>';
        totalPaint += item.value;
      }} else {{
        deductedTotal += item.value;
      }}
    }});
    
    // Add additional hours to print
    const additionalDescs = document.querySelectorAll('.paint-addl-desc');
    const additionalValues = document.querySelectorAll('.paint-addl-value');
    additionalDescs.forEach((descInput, index) => {{
      const desc = descInput.value;
      const val = parseFloat(additionalValues[index].value) || 0;
      if (desc || val) {{
        printContent += '<div style="padding: 12px 8px; border-bottom: 1px solid #ddd; background-color: #fffacd;">';
        printContent += '<input type="checkbox" disabled style="margin-right: 10px;" />';
        printContent += '<strong>Additional</strong> - ' + desc;
        printContent += ' <div style="display: inline; float: right;">' + formatHours(val) + ' hrs</div>';
        printContent += '</div>';
        totalPaint += val;
      }}
    }});
    
    printContent += '<div style="padding: 12px 8px; font-weight: bold; background-color: #f0f0f0; margin-top: 10px; text-align: right;">';
    printContent += 'Total Refinish: ' + totalPaint.toFixed(1);
    printContent += '</div>';
    
    printContent += '</body></html>';
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  }}
  
  function saveRefinishModal() {{
  const checkboxes = document.querySelectorAll('.paint-item-checkbox');

  let assigned = [];
  let unassigned = [];

  checkboxes.forEach((checkbox, index) => {{
    const item = displayPaintItems[index];
    if (checkbox.checked) {{
      unassigned.push(item);
    }} else {{
      assigned.push(item);
    }}
  }});

  // Additional hours
  let additional = [];
  const descs = document.querySelectorAll('.paint-addl-desc');
  const values = document.querySelectorAll('.paint-addl-value');

  descs.forEach((descInput, i) => {{
    const desc = descInput.value;
    const val = parseFloat(values[i].value) || 0;
    if (desc || val) {{
      additional.push({{ description: desc, value: val }});
    }}
  }});

  const tech = document.getElementById('refinishTechInput').value;

  // 🔥 Only compute total unassigned
  const totalUnassigned = unassigned.reduce((sum, item) => sum + item.value, 0);

  // 🔥 Modal’s displayed total
  const totalPaint = parseFloat(document.getElementById('totalPaint').innerText) || 0;

  const data = {{
    assigned,
    unassigned,
    additional,
    totalUnassigned,
    totalPaint,
    tech,
    ro: "{second_ro_line}",
    vehicle: "{vehicle_info_line}",
    timestamp: new Date().toISOString()
  }};

  fetch('https://flagtech1.onrender.com/ui/save-refinish', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data)
  }})
  .then(r => r.json())
  .then(res => {{
    console.log("Refinish saved:", res);
    closeRefinishModal();
  }})
  .catch(err => {{
    console.error("Save refinish error:", err);
    closeRefinishModal();
  }});
}}
"""


def get_modal_close_handler():
    """Return the JavaScript to handle modal close on outside click."""
    return """
  window.onclick = function(event) {  
    const laborModal = document.getElementById('laborModal');
    const refinishModal = document.getElementById('refinishModal');
    if (event.target == laborModal) {
      laborModal.style.display = 'none';
    }
    if (event.target == refinishModal) {
      refinishModal.style.display = 'none';
    }
  }
"""

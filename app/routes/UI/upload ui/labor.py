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
    <div class="labor-total">Total Labor: <span id="totalLabor">{total_labor}</span></div>
    <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
      <button onclick="printModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Print</button>
        <button onclick="saveModal()" style='padding:10px 20px; font-size:14px; cursor:pointer; background-color:#505050; color:white; border:none; border-radius:3px;'>Save</button>
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
"""


def get_labor_modal_script(labor_items_json, total_labor, second_ro_line, vehicle_info_line):
    """Return the JavaScript for the labor modal functionality."""
    return f"""
  const laborItems = {labor_items_json};
  const initialTotal = {total_labor};
  
  function updateTotal() {{
    const checkboxes = document.querySelectorAll('.labor-item-checkbox');
    let deductedTotal = 0;
    
    checkboxes.forEach((checkbox, index) => {{
      if (checkbox.checked) {{
        deductedTotal += laborItems[index].value;
      }}
    }});
    
    const newTotal = (initialTotal - deductedTotal).toFixed(1);
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
    
    if (laborItems.length === 0) {{
      html = '<p>No labor items found.</p>';
    }} else {{
      laborItems.forEach((item, index) => {{
        html += '<div class="labor-item" id="item-' + index + '">';
        html += '<input type="checkbox" class="labor-item-checkbox" onchange="toggleDeduction(' + index + ')" />';
        html += '<div style="flex: 1;"><strong>Line ' + item.line + '</strong> - ' + item.description + '</div>';
        html += '<div>' + item.value + ' hrs</div>';
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
        printContent += '<div style="padding: 12px 8px; border-bottom: 1px solid #ddd;">';
        printContent += '<input type="checkbox" disabled style="margin-right: 10px;" />';
        printContent += '<strong>Line ' + laborItems[index].line + '</strong> - ' + laborItems[index].description;
        printContent += ' <div style="display: inline; float: right;">' + laborItems[index].value + ' hrs</div>';
        printContent += '</div>';
        totalLabor += laborItems[index].value;
      }} else {{
        deductedTotal += laborItems[index].value;
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
    let selectedItems = [];
    let deductedTotal = 0;
    
    checkboxes.forEach((checkbox, index) => {{
      if (checkbox.checked) {{
        selectedItems.push(laborItems[index]);
        deductedTotal += laborItems[index].value;
      }}
    }});
    
    const newTotal = (initialTotal - deductedTotal).toFixed(1);
    
    const data = {{
      items: selectedItems,
      totalLabor: newTotal,
      timestamp: new Date().toISOString()
    }};
    
    // Create and download JSON file
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {{ type: 'application/json' }});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'labor-assignment-' + new Date().getTime() + '.json';
    link.click();
    URL.revokeObjectURL(url);
  }}
"""

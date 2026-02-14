"""Upload screen content for the FlagTech UI."""


def get_upload_screen_html():
    """Return the HTML content for the upload screen."""
    return """
        <div id="upload" class="screen">
            <style>
                #upload.active {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: calc(100vh - 180px);
                }
                #upload .upload-center {
                    width: 100%;
                    display: flex;
                    justify-content: center;
                    transform: translateY(-50%);
                }
                #upload .import-button {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 14px 26px;
                    background-color: #d32f2f;
                    color: #fff;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                }
            </style>
            <form id="uploadForm" enctype="multipart/form-data">
                <div id="importButtonWrap" class="upload-center">
                    <label for="fileInput" class="import-button">+ import</label>
                </div>
                <input type="file" id="fileInput" name="file" accept="application/pdf" onchange="handleFileUpload()" style="display: none;" />
            </form>
            <div id="uploadStatus"></div>
        </div>
    """


def get_estimate_summary_html():
    """Return the HTML for the estimate summary with save button."""
    return """
        <div id="estimateSummary" style="display: none; margin-top: 20px; padding: 15px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px;">
            <h3>Estimate Summary</h3>
            <div style="display: flex; gap: 40px; margin-bottom: 15px;">
                <div>
                    <div style="font-weight: bold; margin-bottom: 8px;">Grand Total</div>
                    <div id="summaryGrandTotal" style="font-size: 18px; font-weight: bold;">-</div>
                </div>
                <div>
                    <div style="font-weight: bold; margin-bottom: 8px;">Deductible</div>
                    <div id="summaryDeductible" style="font-size: 18px; font-weight: bold;">-</div>
                </div>
                <div>
                    <div style="font-weight: bold; margin-bottom: 8px;">Customer Pay</div>
                    <div id="summaryCustomerPay" style="font-size: 18px; font-weight: bold;">-</div>
                </div>
                <div>
                    <div style="font-weight: bold; margin-bottom: 8px;">Insurance Pay</div>
                    <div id="summaryInsurancePay" style="font-size: 18px; font-weight: bold;">-</div>
                </div>
            </div>
        </div>
    """


def get_upload_script():
    """Return the JavaScript for handling file uploads."""
    return """
        // Store estimate totals data globally
        let currentEstimateTotals = {};
        let currentRO = '';
        let currentVehicle = '';
        
        function handleFileUpload() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) return;

            const importButtonWrap = document.getElementById('importButtonWrap');
            if (importButtonWrap) {
                importButtonWrap.style.display = 'none';
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.innerHTML = '<p>Processing...</p>';
            
            fetch('/ui/grid?ajax=true', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                statusDiv.innerHTML = html;
                fileInput.value = '';
                
                // Execute any scripts in the loaded content
                const scripts = statusDiv.querySelectorAll('script');
                scripts.forEach(oldScript => {
                    const newScript = document.createElement('script');
                    newScript.innerHTML = oldScript.innerHTML;
                    document.body.appendChild(newScript);
                });
            })
            .catch(error => {
                statusDiv.innerHTML = '<p>Error: ' + error.message + '</p>';
                const importButtonWrap = document.getElementById('importButtonWrap');
                if (importButtonWrap) {
                    importButtonWrap.style.display = 'flex';
                }
            });
        }
        
        function displayEstimateSummary(totals, ro, vehicle) {
            currentEstimateTotals = totals;
            currentRO = ro;
            currentVehicle = vehicle;
            window.currentEstimateTotals = totals;
            
            const summaryDiv = document.getElementById('estimateSummary');
            if (!summaryDiv) {
                console.error('Summary div not found');
                return;
            }
            
            // Format numbers
            const formatMoney = (val) => {
                if (val === null || val === undefined) return '-';
                return parseFloat(val).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            };
            
            document.getElementById('summaryGrandTotal').textContent = formatMoney(totals.grand_total);
            document.getElementById('summaryDeductible').textContent = formatMoney(totals.deductible);
            document.getElementById('summaryCustomerPay').textContent = formatMoney(totals.customer_pay);
            document.getElementById('summaryInsurancePay').textContent = formatMoney(totals.insurance_pay);
            
            summaryDiv.style.display = 'block';
        }
        
        function saveEstimateSummary() {
            const saveBtn = document.getElementById('saveSummaryBtn');
            const saveStatus = document.getElementById('saveStatus');
            
            saveBtn.disabled = true;
            saveStatus.textContent = 'Saving...';
            
            const data = {
                ro: currentRO,
                vehicle: currentVehicle,
                grand_total: currentEstimateTotals.grand_total,
                deductible: currentEstimateTotals.deductible,
                customer_pay: currentEstimateTotals.customer_pay,
                insurance_pay: currentEstimateTotals.insurance_pay,
                timestamp: new Date().toISOString()
            };
            
            fetch('/ui/save-estimate-totals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'success') {
                    saveStatus.textContent = 'Saved successfully!';
                    saveStatus.style.color = 'green';
                    // Reset the form after 2 seconds
                    setTimeout(() => {
                        document.getElementById('uploadStatus').innerHTML = '';
                        document.getElementById('estimateSummary').style.display = 'none';
                        document.getElementById('fileInput').value = '';
                        const importButtonWrap = document.getElementById('importButtonWrap');
                        if (importButtonWrap) {
                            importButtonWrap.style.display = 'flex';
                        }
                        saveStatus.textContent = '';
                        saveBtn.disabled = false;
                    }, 2000);
                } else {
                    saveStatus.textContent = 'Error: ' + (result.message || 'Failed to save');
                    saveStatus.style.color = 'red';
                    saveBtn.disabled = false;
                }
            })
            .catch(error => {
                saveStatus.textContent = 'Error: ' + error.message;
                saveStatus.style.color = 'red';
                saveBtn.disabled = false;
            });
        }
    """

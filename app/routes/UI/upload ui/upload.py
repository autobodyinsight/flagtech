"""Upload screen content for the FlagTech UI."""


def get_upload_screen_html():
    """Return the HTML content for the upload screen."""
    return """
        <div id="upload" class="screen active">
            <h2>Upload an Estimate PDF</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="fileInput" name="file" accept="application/pdf" onchange="handleFileUpload()" style="padding: 10px; cursor: pointer;" />
            </form>
            <div id="uploadStatus"></div>
        </div>
    """


def get_upload_script():
    """Return the JavaScript for handling file uploads."""
    return """
        function handleFileUpload() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) return;
            
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
            });
        }
    """

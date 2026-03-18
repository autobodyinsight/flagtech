"""Setup screen shell."""


def get_setup_screen_html():
    return """
    <div id="setup" class="screen" style="padding:20px;">
        <style>
            #setup #setupLayout {
                width: min(96vw, 1520px);
                margin: 0 auto;
                display: flex;
                align-items: flex-start;
                gap: 20px;
            }
            #setup #setupMainPane {
                flex: 1;
                min-width: 0;
                padding: 26px;
                background: #fbfaf9;
                border: 1px solid #ddd6d2;
                border-radius: 14px;
                box-shadow: 0 10px 26px rgba(20, 20, 20, 0.08);
            }
            #setup .setup-card {
                background: #ffffff;
                border: 1px solid #e5dfdc;
                border-radius: 10px;
                padding: 16px;
            }
            #setup .setup-note {
                color: #555;
                line-height: 1.5;
                font-size: 14px;
            }
        </style>

        <div id="setupLayout">
            <div id="setupMainPane">
                <h3 style="margin:0 0 18px 0; color:#333;">Setup</h3>
                <div class="setup-card">
                    <div class="setup-note">
                        Setup is available and running with authentication, access control, and identity management removed.
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def get_setup_script():
    return """
    <script>
        function setupInit() {
            return;
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupInit);
        } else {
            setupInit();
        }
    </script>
    """

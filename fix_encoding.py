#!/usr/bin/env python3
"""Fix encoding issues in ro_routes.py"""

import re

# Read the file
with open('app/routes/estimate_routes/ro_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace mojibake em-dashes with proper em-dash
# The mojibake "â€"" is UTF-8 bytes for em-dash interpreted as text
content = content.replace('â€"', '—')

# Also fix any tech lines with the same issue
content = content.replace('"tech": tech_by_ro.get(ro, "â€"")', '"tech": tech_by_ro.get(ro, "—")')

# Write back
with open('app/routes/estimate_routes/ro_routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Fixed encoding issues in ro_routes.py')
print('  - Replaced mojibake em-dashes (â€") with proper em-dashes (—)')

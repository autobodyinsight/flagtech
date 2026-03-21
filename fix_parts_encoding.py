#!/usr/bin/env python3
"""Fix estimator/tech name encoding in ro_routes.py"""

filePath = r'c:\Users\702se\Desktop\flagtech\app\routes\estimate_routes\ro_routes.py'

# Read file as text
with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences before replacement
before = content.count('â€"')
print(f'Found {before} instances of mojibake em-dash')

# Replace mojibake em-dash sequences with proper em-dash
# The mojibake â€" is UTF-8 byte sequence E2 80 9C for " interpreted as three separate characters
content = content.replace('â€"', '—')  # Replace mojbbibake with proper em-dash

# Double-check replacement
after = content.count('â€"')
print(f'After replacement: {after} instances of mojibake remaining')

# Write back to file
with open(filePath, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Fixed estimator and tech name encoding')

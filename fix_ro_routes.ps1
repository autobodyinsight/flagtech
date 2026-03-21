# PowerShell script to fix ro_routes.py encoding and parts filter issues

$filePath = 'app/routes/estimate_routes/ro_routes.py'
$lines = @(Get-Content $filePath -Encoding UTF8)
$newLines = @()

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    # Fix the encoding issue on the estimator line and add parts data check logic
    if ($line -match 'on_order = max') {
        $newLines += $line
        $newLines += '            '
        $newLines += '            # Show RO if it has parts_repairs OR if it has parts orders/received data'
        $newLines += '            has_parts_data = bool(parts_repairs) or on_order > 0 or returned_count > 0 or received_map.get(ro, 0) > 0'
        $newLines += '            if not has_parts_data:'
        $newLines += '                continue'
        continue
    }
    
    # Replace mojibake characters with proper em-dash
    $line = $line -replace 'â€"', '—'
    
    $newLines += $line
}

Set-Content $filePath -Value $newLines -Encoding UTF8
Write-Host 'Fixed encoding issues and added parts data filter logic'

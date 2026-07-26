@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$markerPattern = '(?m)^# pre commit test trigger\r?\n?$';" ^
  "$utf8 = New-Object System.Text.UTF8Encoding($false);" ^
  "Get-ChildItem -LiteralPath . -Filter '*.py' -File -Recurse |" ^
  "Where-Object { $_.FullName -notmatch '\\(?:\.git|\.venv|venv|env|__pycache__|node_modules)\\' } |" ^
  "ForEach-Object {" ^
  "    $path = $_.FullName;" ^
  "    $content = [System.IO.File]::ReadAllText($path);" ^
  "    $updated = [regex]::Replace($content, $markerPattern, '');" ^
  "    if ($updated -ne $content) {" ^
  "        [System.IO.File]::WriteAllText($path, $updated, $utf8);" ^
  "        Write-Host ('Removed: ' + $_.FullName);" ^
  "    }" ^
  "}"

echo.
echo Finished removing pre-commit trigger comments.
endlocal

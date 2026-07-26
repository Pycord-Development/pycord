@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$marker = '# pre commit test trigger';" ^
  "$utf8 = New-Object System.Text.UTF8Encoding($false);" ^
  "Get-ChildItem -LiteralPath . -Filter '*.py' -File -Recurse |" ^
  "Where-Object { $_.FullName -notmatch '\\(?:\.git|\.venv|venv|env|__pycache__|node_modules)\\' } |" ^
  "ForEach-Object {" ^
  "    $path = $_.FullName;" ^
  "    $content = [System.IO.File]::ReadAllText($path);" ^
  "    if ($content -notmatch '(?s)(?:^|\r?\n)# pre commit test trigger(?:\r?\n)?$') {" ^
  "        $newline = if ($content.Contains(\"`r`n\")) { \"`r`n\" } else { \"`n\" };" ^
  "        $separator = if ($content.Length -eq 0 -or $content.EndsWith(\"`n\")) { '' } else { $newline };" ^
  "        [System.IO.File]::WriteAllText($path, $content + $separator + $marker + $newline, $utf8);" ^
  "        Write-Host ('Added: ' + $_.FullName);" ^
  "    }" ^
  "}"

echo.
echo Finished adding pre-commit trigger comments.
endlocal

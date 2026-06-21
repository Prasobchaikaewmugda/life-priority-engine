[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$appPath = Join-Path $projectRoot "app.py"
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $appPath -PathType Leaf)) {
    throw "Streamlit entry point not found: $appPath"
}

if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
    $pythonPath = $venvPython
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python was not found. Create .venv or add Python to PATH."
    }
    $pythonPath = $pythonCommand.Source
}

Write-Host "Starting Life Priority Engine from $projectRoot"
& $pythonPath -m streamlit run $appPath
exit $LASTEXITCODE

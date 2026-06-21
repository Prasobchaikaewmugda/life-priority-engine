[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$requiredFiles = @(
    "app.py"
    "requirements.txt"
    "README.md"
    "data/.gitkeep"
    "docs/00_LIFE_PRIORITY_ENGINE_MASTER_PROJECT_MAP_V1.md"
    "docs/01_LIFE_PRIORITY_ENGINE_CODEX_WORKFLOW_AND_GATE_ROADMAP_V1.md"
    "docs/02_LIFE_PRIORITY_ENGINE_RULES_V1.md"
    "docs/CURRENT_BOOT_PACKET.md"
    "scripts/run_app.ps1"
    "scripts/run_app.sh"
    "scripts/check_project_state.ps1"
)

$missingFiles = @()

Write-Host "Checking Life Priority Engine at $projectRoot"
foreach ($relativePath in $requiredFiles) {
    $fullPath = Join-Path $projectRoot $relativePath
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
        Write-Host "[OK]      $relativePath"
    } else {
        Write-Host "[MISSING] $relativePath" -ForegroundColor Red
        $missingFiles += $relativePath
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error "Project check failed: $($missingFiles.Count) required file(s) missing."
    exit 1
}

Write-Host "Project check passed: all $($requiredFiles.Count) required files exist." -ForegroundColor Green
exit 0

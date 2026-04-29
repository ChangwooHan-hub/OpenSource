$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$repoRoot = (& git -C $projectRoot rev-parse --show-toplevel).Trim()
$hookSource = Join-Path $projectRoot "scripts\post-commit"
$hookTarget = Join-Path $repoRoot ".git\hooks\post-commit"

if (-not (Test-Path $hookSource)) {
    throw "Hook source not found: $hookSource"
}

Copy-Item -LiteralPath $hookSource -Destination $hookTarget -Force
Write-Host "Installed post-commit hook: $hookTarget"

$ErrorActionPreference = "Stop"

$processRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$repoRoot = Resolve-Path (Join-Path $processRoot "..")
$hookSource = Join-Path $processRoot "scripts\seat-post-commit"
$hookTarget = Join-Path $repoRoot ".git\hooks\post-commit"

if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    throw "Watched repository .git directory not found: $repoRoot"
}

if (-not (Test-Path $hookSource)) {
    throw "Hook source not found: $hookSource"
}

if (Test-Path $hookTarget) {
    $backup = "$hookTarget.backup-$(Get-Date -Format yyyyMMddHHmmss)"
    Copy-Item -LiteralPath $hookTarget -Destination $backup -Force
    Write-Host "Backed up existing hook: $backup"
}

Copy-Item -LiteralPath $hookSource -Destination $hookTarget -Force
Write-Host "Installed Seat watcher hook: $hookTarget"

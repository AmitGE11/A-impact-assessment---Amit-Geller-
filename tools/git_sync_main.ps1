param(
  [string]$Message = "chore: sync"
)
$ErrorActionPreference = "Stop"
function Run($cmd){ Write-Host "→ $cmd" -ForegroundColor Cyan; iex $cmd }
Write-Host "`n=== GIT SYNC TO MAIN (Windows) ===`n"

Run "git rev-parse --abbrev-ref HEAD"
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host "Current branch: $branch"

if ($branch -eq "master") {
  Run "git branch -M main"
  $branch = "main"
}

Run "git config --global init.defaultBranch main"

# Ensure origin exists
try { git remote get-url origin | Out-Null }
catch {
  Write-Error "No 'origin' remote is configured. Set it via: git remote add origin <url>"
  exit 1
}

Run "git fetch origin"
Run "git checkout -B main"
# Try fast-forward merge if remote main exists
try { Run "git merge --ff-only origin/main" } catch { Write-Host "No remote main to merge (first push?)" -ForegroundColor Yellow }

# Stage/commit if there are changes
$changes = git status --porcelain
if ($changes) {
  Run "git add ."
  Run "git commit -m `"$Message`""
} else {
  Write-Host "No local changes to commit."
}

Run "git push -u origin main"
Write-Host "`nSYNC TO MAIN OK`n"

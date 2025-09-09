#!/usr/bin/env bash
set -euo pipefail
msg="${1:-chore: sync}"
echo -e "\n=== GIT SYNC TO MAIN (bash) ===\n"

branch="$(git rev-parse --abbrev-ref HEAD)"
echo "Current branch: $branch"
if [ "$branch" = "master" ]; then
  git branch -M main
  branch="main"
fi

git config --global init.defaultBranch main

# Ensure origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "No 'origin' remote is configured. Set it via: git remote add origin <url>" >&2
  exit 1
fi

git fetch origin
git checkout -B main
# Try fast-forward if remote main exists
if git ls-remote --exit-code origin main >/dev/null 2>&1; then
  git merge --ff-only origin/main || true
else
  echo "No remote main to merge (first push?)"
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  git add .
  git commit -m "$msg" || true
else
  echo "No local changes to commit."
fi

git push -u origin main
echo -e "\nSYNC TO MAIN OK\n"

#!/bin/bash
# OpenClaw workspace backup to GitHub
# Runs daily at 2 AM UTC

cd /home/ubuntu/.openclaw/workspace

# Add all changes
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "No changes to commit at $(date)"
    exit 0
fi

# Commit with timestamp
git commit -m "Daily backup: $(date +'%Y-%m-%d %H:%M UTC')"

# Push to GitHub
git push origin main

echo "Backup completed at $(date)"

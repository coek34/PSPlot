#!/bin/bash
# Script to force download iCloud files for PSPlot project
PROJECT_DIR="/Users/macots/Library/Mobile Documents/com~apple~CloudDocs/Documents/Projects/PSPlot"

echo "🔄 Starting iCloud sync (materialization) for PSPlot..."
find "$PROJECT_DIR" -maxdepth 3 -type f -exec brctl download {} +

# Wait for background downloads
sleep 3

echo "✅ All project files triggered for download."
ls -laO "$PROJECT_DIR" | grep -v "dataless" | head -n 5

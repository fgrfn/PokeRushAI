#!/usr/bin/env pwsh
# Start PokéRushAI WebUI

Write-Host "🎮 Starting PokéRushAI WebUI..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists and activate it
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Start the WebUI
Write-Host "✓ Starting Flask server on http://0.0.0.0:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

python web_ui/app.py

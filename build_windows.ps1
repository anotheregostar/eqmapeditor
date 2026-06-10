$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Creating virtual environment..."
py -3 -m venv .venv

Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Installing build requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

Write-Host "Building standalone executable..."
pyinstaller --noconfirm eq_map_editor.spec

Write-Host ""
Write-Host "Build complete:"
Write-Host "$PSScriptRoot\dist\EQMapEditor"

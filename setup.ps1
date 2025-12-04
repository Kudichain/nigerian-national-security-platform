# Quick Start Script
# Run this to set up the development environment

Write-Host "Security AI Platform - Setup Script" -ForegroundColor Green
Write-Host "====================================`n" -ForegroundColor Green

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Cyan
} else {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Copy environment file
Write-Host "`nSetting up environment..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file. Please edit with your configurations." -ForegroundColor Green
} else {
    Write-Host ".env already exists" -ForegroundColor Cyan
}

# Create necessary directories
Write-Host "`nCreating directories..." -ForegroundColor Yellow
$dirs = @("data", "mlruns", "mlartifacts", "logs")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created $dir/" -ForegroundColor Green
    }
}

Write-Host "`n====================================`n" -ForegroundColor Green
Write-Host "Setup complete! Next steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Edit .env with your configurations" -ForegroundColor Cyan
Write-Host "2. Start infrastructure:" -ForegroundColor Cyan
Write-Host "   cd infra/docker" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "3. Train a model:" -ForegroundColor Cyan
Write-Host "   python models/nids/train.py --data data/sample.parquet" -ForegroundColor White
Write-Host ""
Write-Host "4. Start inference service:" -ForegroundColor Cyan
Write-Host "   python services/nids/app.py" -ForegroundColor White
Write-Host ""
Write-Host "For full documentation, see README.md" -ForegroundColor Yellow

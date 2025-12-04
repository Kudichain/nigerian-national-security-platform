# Common development tasks for Security AI Platform
# Usage: .\Makefile.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Security AI Platform - Development Commands`n" -ForegroundColor Green
    Write-Host "Usage: .\Makefile.ps1 <command>`n" -ForegroundColor Cyan
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  setup          - Initial project setup"
    Write-Host "  install        - Install Python dependencies"
    Write-Host "  test           - Run all tests"
    Write-Host "  lint           - Run linters (black, flake8, mypy)"
    Write-Host "  format         - Format code with black"
    Write-Host "  docker-up      - Start Docker infrastructure"
    Write-Host "  docker-down    - Stop Docker infrastructure"
    Write-Host "  train-nids     - Train NIDS model"
    Write-Host "  train-phishing - Train phishing model"
    Write-Host "  train-auth     - Train auth risk model"
    Write-Host "  serve-nids     - Start NIDS inference service"
    Write-Host "  serve-phishing - Start phishing inference service"
    Write-Host "  serve-auth     - Start auth inference service"
    Write-Host "  clean          - Clean generated files"
    Write-Host "  help           - Show this help message"
}

function Invoke-Setup {
    Write-Host "Running setup..." -ForegroundColor Yellow
    .\setup.ps1
}

function Invoke-Install {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

function Invoke-Test {
    Write-Host "Running tests..." -ForegroundColor Yellow
    pytest tests/ -v --cov=. --cov-report=html
    Write-Host "`nCoverage report generated in htmlcov/index.html" -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host "Running linters..." -ForegroundColor Yellow
    Write-Host "`nBlack (check only):" -ForegroundColor Cyan
    black --check .
    
    Write-Host "`nFlake8:" -ForegroundColor Cyan
    flake8 . --count --statistics
    
    Write-Host "`nMypy:" -ForegroundColor Cyan
    mypy --ignore-missing-imports .
}

function Invoke-Format {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    black .
    Write-Host "Code formatted!" -ForegroundColor Green
}

function Invoke-DockerUp {
    Write-Host "Starting Docker infrastructure..." -ForegroundColor Yellow
    Push-Location infra/docker
    docker-compose up -d
    Pop-Location
    Write-Host "`nInfrastructure started!" -ForegroundColor Green
    Write-Host "Kafka: localhost:9092" -ForegroundColor Cyan
    Write-Host "Redis: localhost:6379" -ForegroundColor Cyan
    Write-Host "MLflow: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "Prometheus: http://localhost:9090" -ForegroundColor Cyan
    Write-Host "Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
}

function Invoke-DockerDown {
    Write-Host "Stopping Docker infrastructure..." -ForegroundColor Yellow
    Push-Location infra/docker
    docker-compose down
    Pop-Location
    Write-Host "Infrastructure stopped!" -ForegroundColor Green
}

function Invoke-TrainNIDS {
    Write-Host "Training NIDS model..." -ForegroundColor Yellow
    if (!(Test-Path "data/netflow_sample.parquet")) {
        Write-Host "Error: data/netflow_sample.parquet not found" -ForegroundColor Red
        Write-Host "Please add sample data or specify --data path" -ForegroundColor Yellow
        return
    }
    python models/nids/train.py --data data/netflow_sample.parquet --model isoforest
}

function Invoke-TrainPhishing {
    Write-Host "Training phishing model..." -ForegroundColor Yellow
    if (!(Test-Path "data/emails_labeled.parquet")) {
        Write-Host "Error: data/emails_labeled.parquet not found" -ForegroundColor Red
        return
    }
    python models/phishing/train.py --data data/emails_labeled.parquet --model tfidf
}

function Invoke-TrainAuth {
    Write-Host "Training auth risk model..." -ForegroundColor Yellow
    if (!(Test-Path "data/auth_events_labeled.parquet")) {
        Write-Host "Error: data/auth_events_labeled.parquet not found" -ForegroundColor Red
        return
    }
    python models/auth/train.py --data data/auth_events_labeled.parquet
}

function Invoke-ServeNIDS {
    Write-Host "Starting NIDS inference service on port 8080..." -ForegroundColor Yellow
    python services/nids/app.py
}

function Invoke-ServePhishing {
    Write-Host "Starting phishing inference service on port 8081..." -ForegroundColor Yellow
    python services/phishing/app.py
}

function Invoke-ServeAuth {
    Write-Host "Starting auth risk inference service on port 8082..." -ForegroundColor Yellow
    python services/auth/app.py
}

function Invoke-Clean {
    Write-Host "Cleaning generated files..." -ForegroundColor Yellow
    
    # Python cache
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Filter "*.pyo" | Remove-Item -Force
    
    # Test cache
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    
    # Build artifacts
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    Get-ChildItem -Recurse -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force
    
    Write-Host "Clean complete!" -ForegroundColor Green
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "setup" { Invoke-Setup }
    "install" { Invoke-Install }
    "test" { Invoke-Test }
    "lint" { Invoke-Lint }
    "format" { Invoke-Format }
    "docker-up" { Invoke-DockerUp }
    "docker-down" { Invoke-DockerDown }
    "train-nids" { Invoke-TrainNIDS }
    "train-phishing" { Invoke-TrainPhishing }
    "train-auth" { Invoke-TrainAuth }
    "serve-nids" { Invoke-ServeNIDS }
    "serve-phishing" { Invoke-ServePhishing }
    "serve-auth" { Invoke-ServeAuth }
    "clean" { Invoke-Clean }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command`n" -ForegroundColor Red
        Show-Help
    }
}

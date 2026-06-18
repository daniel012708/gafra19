chcp 65001 | Out-Null
Set-Location -Path $PSScriptRoot
Write-Host "Running Django checks and starting dev server in $PWD"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Write-Error "Python not found on PATH"; exit 1 }
python -V
python manage.py check
python manage.py makemigrations -n auto || Write-Warning "makemigrations failed"
python manage.py migrate || Write-Error "migrate failed"; exit 1
Write-Host "Optional: to populate sample data run: python manage.py populate_sample"
python manage.py runserver

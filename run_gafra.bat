@echo off
rem Set console to UTF-8
chcp 65001 >nul
rem Ensure we are in the script directory (project root)
cd /d "%~dp0"
echo Running Django checks and starting dev server in %CD%
python -V || (echo Python not found on PATH & pause & exit /b 1)
python manage.py check || (echo "manage.py check" failed & pause & exit /b 1)
python manage.py makemigrations --noinput || (echo "makemigrations" failed & pause & exit /b 1)
python manage.py migrate --noinput || (echo "migrate" failed & pause & exit /b 1)
echo Optional: to populate sample data run: python manage.py populate_sample
python manage.py runserver
pause

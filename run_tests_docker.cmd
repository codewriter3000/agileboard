@echo off
echo === Running Agileboard Backend Tests in Docker ===
echo.
echo Building backend image...
docker-compose build backend
if errorlevel 1 (
    echo Failed to build backend image
    exit /b 1
)

echo.
echo Starting database...
docker-compose up -d db
if errorlevel 1 (
    echo Failed to start database
    exit /b 1
)

echo.
echo Running tests...
docker-compose run --rm backend python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo Tests failed
    exit /b 1
) else (
    echo.
    echo All tests passed!
)

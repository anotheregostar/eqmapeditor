@echo off
title Extract EQ Map Points

if "%~1"=="" (
    echo Drag a folder onto this batch file to extract EQ map point labels.
    echo.
    pause
    exit /b 1
)

if not exist "%~1\" (
    echo The dropped item is not a folder:
    echo "%~1"
    echo.
    pause
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%extract_eq_map_points.py"

if not exist "%PY_SCRIPT%" (
    echo Could not find:
    echo "%PY_SCRIPT%"
    echo.
    echo Make sure this batch file is in the same folder as extract_eq_map_points.py
    echo.
    pause
    exit /b 1
)

python "%PY_SCRIPT%" "%~1" "%SCRIPT_DIR%."

echo.
pause
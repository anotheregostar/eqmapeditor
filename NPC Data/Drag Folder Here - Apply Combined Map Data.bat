@echo off
title Apply EQ Combined Map Data

if "%~1"=="" (
    echo Drag a folder of EQ map .txt files onto this batch file.
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
set "PY_SCRIPT=%SCRIPT_DIR%apply_combined_map_data.py"

if not exist "%PY_SCRIPT%" (
    echo Could not find:
    echo "%PY_SCRIPT%"
    echo.
    echo Make sure this batch file is in the same folder as apply_combined_map_data.py
    echo.
    pause
    exit /b 1
)

python "%PY_SCRIPT%" "%~1" "%SCRIPT_DIR%."

echo.
pause

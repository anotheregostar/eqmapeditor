@echo off
setlocal
cd /d "%~dp0"

echo Cleaning old build output...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Creating virtual environment...
py -3 -m venv .venv
if errorlevel 1 goto :error

call .venv\Scripts\activate.bat

echo Installing build requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller pillow
if errorlevel 1 goto :error

echo Building standalone executable with icon...
pyinstaller --clean --noconfirm eq_map_editor.spec
if errorlevel 1 goto :error

echo.
echo Build complete.
echo EXE folder:
echo %CD%\dist\EQMapEditor
echo.
echo If Windows still shows the old generic icon, right-click the EXE, create a new shortcut,
echo or restart Explorer to clear Windows' icon cache.
echo.
pause
exit /b 0

:error
echo.
echo Build failed. Review the error messages above.
pause
exit /b 1

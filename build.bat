@echo off
REM Build script for Drug Dosage Calculator
REM Run this from Command Prompt or by double-clicking

echo ==================================
echo Building Drug Dosage Calculator
echo ==================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully
) else (
    echo PyInstaller found
)

echo.
echo Building executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using the spec file (includes all dependencies)
pyinstaller DrugCalculator.spec

if %errorlevel% equ 0 (
    echo.
    echo ==================================
    echo Build successful!
    echo ==================================
    echo.
    echo Your .exe is located at:
    echo    dist\DrugCalculator.exe
    echo.
    echo Next steps:
    echo    1. Test the .exe by double-clicking it
    echo    2. Run some calculations to verify it works
    echo    3. Check that history saves correctly
    echo.
    echo When ready to release:
    echo    - Create a GitHub release (v1.1.1)
    echo    - Attach dist\DrugCalculator.exe to the release
    echo    - Make repository public
    echo.
) else (
    echo.
    echo ==================================
    echo Build failed
    echo ==================================
    echo.
    echo Check the error messages above.
    echo.
)

pause

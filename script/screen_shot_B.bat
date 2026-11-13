@echo off
chcp 65001 >nul 2>&1

echo Starting ADB...

for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set timestamp=%%i

set "script_dir=%~dp0"
set "save_dir=ECUlog\%timestamp%_screenshot_B"
if not exist "%save_dir%" md "%save_dir%"

echo Save dir: %save_dir%

set "B1=%timestamp%_B1.png"
echo Capturing B1...
adb -host shell weston-screenshooter /private/%B1% --output_id=2
adb -host pull /private/%B1% "%save_dir%"
adb -host shell rm /private/%B1%

echo.
echo B screen capture completed!
echo Save path: %save_dir%

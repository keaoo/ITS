@echo off
chcp 65001 >nul 2>&1

echo Starting ADB...

for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set timestamp=%%i

set "script_dir=%~dp0"
set "save_dir=ECUlog\%timestamp%_screenshot_C"
if not exist "%save_dir%" md "%save_dir%"

echo Save dir: %save_dir%

set "C1=%timestamp%_C1.png"
echo Capturing C1...
adb -host shell weston-screenshooter /private/%C1% --output_id=3
adb -host pull /private/%C1% "%save_dir%"
adb -host shell rm /private/%C1%

echo.
echo C screen capture completed!
echo Save path: %save_dir%


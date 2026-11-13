@echo off
chcp 65001 >nul 2>&1

echo Starting ADB...

for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set timestamp=%%i

set "script_dir=%~dp0"
set "save_dir=ECUlog\%timestamp%_screenshot_A"
if not exist "%save_dir%" md "%save_dir%"

echo Save dir: %save_dir%

set "A1=%timestamp%_A1.png"
echo Capturing A1...
adb -host shell weston-screenshooter /private/%A1% --output_id=0
adb -host pull /private/%A1% "%save_dir%"
adb -host shell rm /private/%A1%

set "A2=%timestamp%_A2.png"
echo Capturing A2...
adb -host shell weston-screenshooter /private/%A2% --output_id=1
adb -host pull /private/%A2% "%save_dir%"
adb -host shell rm /private/%A2%

echo.
echo A screen capture completed!
echo Save path: %save_dir%


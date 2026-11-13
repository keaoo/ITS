@echo off
chcp 65001 >nul 2>&1

echo Starting ADB...

for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set timestamp=%%i

set "script_dir=%~dp0"
set "save_dir=%script_dir%..\ECUlog\%timestamp%_screenshot_full"
if not exist "%save_dir%" md "%save_dir%"

echo Save dir: %save_dir%

set "F1=%timestamp%_full.png"
echo Capturing full screen...
adb -host shell weston-screenshooter /private/%F1%
adb -host pull /private/%F1% "%save_dir%"
adb -host shell rm /private/%F1%

echo.
echo Full screen capture completed!
echo Save path: %save_dir%

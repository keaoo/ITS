@echo off
chcp 65001 >nul 2>&1

echo Starting ADB...

adb -host shell "qshell ' gles2-gears_screen -display=2; exit'"

call script/end.bat
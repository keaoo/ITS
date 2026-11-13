@echo off
chcp 65001 >nul 2>&1

echo Starting ADB...

adb -host shell "qshell ' gles2-gears_screen -display=4; exit'"

call script/end.bat
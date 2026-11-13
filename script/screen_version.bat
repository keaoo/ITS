@echo off
chcp 65001 >nul

adb -host shell "echo 'enable n' > /proc/alog"
adb -host shell "qshell 'screen_upgrade --g; exit'"
echo 可以复制到文本

call script/end.bat
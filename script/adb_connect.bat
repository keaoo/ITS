@echo off
chcp 65001 >nul


echo adb connect 192.168.100.1:9555
adb -host connect 192.168.100.1:9555

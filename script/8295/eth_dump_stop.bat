@echo off
chcp 65001 >nul


adb -host shell "pkill tcpdump"

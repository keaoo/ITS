@echo off
chcp 65001 >nul

adb -host shell "setprop voice.4mic.debug.speech 0"
echo 停止录音
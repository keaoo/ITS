@echo off
chcp 65001 >nul

adb -host shell "echo 'enable n' > /proc/alog"
adb -host shell "mount -o remount rw /"
adb -host shell setprop  voice.4mic.debug.speech 0
adb -host shell systemctl stop front
::adb -host shell rm /private/*.pcm
adb -host shell setprop  voice.4mic.debug.speech 1
adb -host shell date
adb -host shell systemctl restart front
::adb -host shell "logctl | grep -iE 'dmasp_callback'"
adb -host shell date
echo 开始录音


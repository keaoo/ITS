@echo off
chcp 65001 >nul

adb -host shell "echo 'enable n;' > /proc/alog"
adb -host shell mount -o remount rw /

adb -host shell setprop persist.audio.dump 0


adb -host shell setprop persist.audio.dump i
adb -host shell setprop bt.phonecall.dump true
adb -host shell setprop persist.ecnr.dump true
adb -host shell systemctl restart audiostreamer
adb -host shell systemctl restart audiostreamer
adb -host shell systemctl restart bt
timeout /t 5 /nobreak
adb -host shell systemctl restart bluetooth-daemon

echo 复现问题拨打蓝牙电话


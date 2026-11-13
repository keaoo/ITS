@echo off
chcp 65001 >nul

call script\8295\eth_dump_stop.bat
call script\8295\eth_dump_clear.bat

echo.
echo 以太网已开始录制，完成后点击停止录制

adb -host shell "tcpdump -i any -C 100 -W 5 -w /data/eth.pcap"

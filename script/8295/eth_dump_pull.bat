@echo off
chcp 65001 >nul


for /f %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set datetime=%%i
set dir=ECUlog\%datetime%_eth
md %dir%


call script\8295\eth_dump_stop.bat

adb -host pull /data/eth.pcap0 %dir%
adb -host pull /data/eth.pcap1 %dir%
adb -host pull /data/eth.pcap2 %dir%
adb -host pull /data/eth.pcap3 %dir%
adb -host pull /data/eth.pcap4 %dir%

call script\8295\eth_dump_clear.bat

call script\end.bat
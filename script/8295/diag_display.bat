@echo off
chcp 65001 >nul

setlocal enabledelayedexpansion
set adb_path=
rem %adb_path%adb -host kill-server
%adb_path%adb -host wait-for-device
%adb_path%adb.exe -host shell "echo 'enable n;' > /proc/alog"

%adb_path%adb.exe -host push script\8295\slay.sh /share/
%adb_path%adb.exe -host push script\8295\diag_display.sh /share/

%adb_path%adb.exe -host shell "(echo 'root';sleep 2;echo 'cd /var;sh slay.sh diag-display.sh;on -p 40 sh diag-display.sh&';sleep 10) | telnet 192.168.2.1"

call script\8295\waiting_dump_finish.bat

:: 使用 PowerShell 获取日期时间
for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set datetime=%%i
set dir=ECUlog\%datetime%_display
md %dir%

adb -host pull /share/diag_display.tar.gz %dir%
adb -host shell "rm /share/diag_display.tar.gz"
adb -host shell "rm /share/dump_finish"

set A1=%datetime%_A1.png
adb -host shell "weston-screenshooter /tmp/%A1% --output_id=0"
adb -host pull /tmp/%A1% %dir%

set A2=%datetime%_A2.png
adb -host shell "weston-screenshooter /tmp/%A2% --output_id=1"
adb -host pull /tmp/%A2% %dir%

set B=%datetime%_B.png
adb -host shell "weston-screenshooter /tmp/%B% --output_id=2"
adb -host pull /tmp/%B% %dir%

set C=%datetime%_C.png
adb -host shell "weston-screenshooter /tmp/%C% --output_id=3"
adb -host pull /tmp/%C% %dir%

set ABC=%datetime%_ABC.png
adb -host shell "weston-screenshooter /tmp/%ABC%"
adb -host pull /tmp/%ABC% %dir%

adb -host shell "cat /proc/interrupts > /tmp/interrupts.txt 2>&1"
adb -host pull /tmp/interrupts.txt %dir%

call script\end.bat

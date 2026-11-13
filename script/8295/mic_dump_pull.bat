@echo off
chcp 65001 >nul

for /f %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set datetime=%%i
set dir=ECUlog\%datetime%_mic
md %dir%

adb -host shell "echo 'enable 0' > /proc/alog"
adb -host shell mount -o remount rw /
  
echo Compressing pcm files ...

adb -host shell tar cvf /private/%datetime%.tar /private/*.pcm
adb -host pull /private/%datetime%.tar %dir%
adb -host shell rm -rf /private/%datetime%.tar

call script\end.bat
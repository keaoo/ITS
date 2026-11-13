@echo off
chcp 65001 >nul

for /f %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set datetime=%%i
set dir=ECUlog\%datetime%_mic
md %dir%

adb -host shell "echo 'enable 0' > /proc/alog"
adb -host shell mount -o remount rw /
  

adb -host pull /tmp/audio_c_xxxx %dir%
adb -host pull /tmp/audio_s_xxx %dir%
adb -host pull /private/audio/audio_s/  %dir%
adb -host pull /private/audio/audio_pipeline %dir%


adb adb -hostpull /data/sco_*.wav %dir%
adb adb -host pull private/audio/ecnr  %dir%

pause
call script\end.bat
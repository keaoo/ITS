@echo off
chcp 65001 >nul

call script\audio_dump_stop.bat

adb -host shell "amixer contents > /private/audio/contents_pull.txt"

:: 使用 PowerShell 获取日期时间
for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set datetime=%%i
set dir=ECUlog\%datetime%_audio
md %dir%


adb -host shell cp -a /tmp/audio_c* /private/audio/
adb -host pull /private/audio %dir%
adb -host pull /private/audiohal %dir%


call script\audio_dump_clear.bat
call script\end.bat
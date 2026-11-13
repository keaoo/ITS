@echo off
chcp 65001 >nul


adb shell "echo 'enable n;' > /proc/alog"
adb shell mount -o remount rw /

adb push script\8295\dump_alios.sh /share/

adb shell "sh /share/dump_alios.sh"


for /f "tokens=1-2 delims= " %%i in ('wmic os get localdatetime ^| find "."') do set datetime=%%i
set datetime=%datetime:~0,8%_%datetime:~8,6%
set dir=..\ECUlog\%datetime%_alios
md %dir%


adb pull /private/alios.tar %dir%
adb shell "rm /private/alios.tar"

adb pull /private/bmlog/screenshot %dir%


call script/end.bat
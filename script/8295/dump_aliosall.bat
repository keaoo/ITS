@echo off
chcp 65001 >nul


adb shell "echo 'enable n;' > /proc/alog"
adb shell mount -o remount rw /

adb push script\8295\dump_aliosall.sh /share/

adb shell "sh /share/dump_aliosall.sh"


for /f "tokens=1-2 delims= " %%i in ('wmic os get localdatetime ^| find "."') do set datetime=%%i
set datetime=%datetime:~0,8%_%datetime:~8,6%
set dir=..\ECUlog\%datetime%_aliosall
md %dir%


adb pull /private/alios-bmlogall.tar %dir%
adb shell "rm /private/alios-bmlogall.tar"

adb pull /private/alios-yuntoolall.tar %dir%
adb shell "rm /private/alios-yuntoolall.tar"


call script/end.bat
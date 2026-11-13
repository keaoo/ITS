@echo off
chcp 65001 >nul


adb -host shell "echo 'enable n;' > /proc/alog"


for /f "tokens=1-2 delims= " %%i in ('wmic os get localdatetime ^| find "."') do set datetime=%%i
set datetime=%datetime:~0,8%_%datetime:~8,6%
set dir=..\ECUlog\%datetime%_yuntool
md %dir%


adb -host pull /private/yuntool/ %dir%


call script/end.bat
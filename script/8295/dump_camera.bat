@echo off
chcp 65001 >nul


adb shell "echo 'enable n;' > /proc/alog"
adb shell mount -o remount rw /

adb push script\8295\slay.sh /share/
adb push script\8295\dump_camera.sh /share/

adb shell "(echo 'root';sleep 2;echo 'cd /var;sh slay.sh dump_camera;on -p 40 sh dump_camera.sh&';sleep 40) | telnet 192.168.2.1"


call script\8295\waiting_dump_finish.bat


for /f "tokens=1-2 delims= " %%i in ('wmic os get localdatetime ^| find "."') do set datetime=%%i
set datetime=%datetime:~0,8%_%datetime:~8,6%
set dir=..\ECUlog\%datetime%_camera
md %dir%


adb pull /share/dump_camera.tar.gz	%dir%
adb shell "rm /share/dump_camera.tar.gz"
adb shell "rm /share/dump_finish"


call script/end.bat
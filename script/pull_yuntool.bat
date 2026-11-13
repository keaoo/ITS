@echo off
chcp 65001 >nul


adb -host shell "echo 'enable n;' > /proc/alog"


:: 使用 powershell 获取稳定的时间格式
for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set datetime=%%i
set dir=ECUlog\%datetime%_yuntool

:: 如果目录已存在，先删除旧的
if exist %dir% (
    echo 清理旧目录：%dir%
    rmdir /s /q %dir%
)
md %dir%


adb -host pull /private/yuntool/ %dir%


call script/end.bat
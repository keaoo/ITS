@echo off
chcp 65001 >nul
set dir=ECUlog
for /f "delims=" %%r in (' adb -host shell date') do echo 当前时间: %%r
for /f "delims=" %%r in (' adb -host shell date') do echo 当前时间: %%r >> %dir%/version.txt
for /f "delims=" %%r in (' adb -host shell getprop ro.yunos.build.version.release') do echo 编译时间: %%r
for /f "delims=" %%r in (' adb -host shell getprop ro.yunos.build.version.release') do echo 编译时间: %%r >> %dir%/version.txt
for /f "delims=" %%v in (' adb -host shell getprop ro.zxq.release.version') do echo 镜像版本: %%v
for /f "delims=" %%v in (' adb -host shell getprop ro.zxq.release.version') do echo 镜像版本: %%v >>%dir%/version.txt
for /f "delims=" %%b in (' adb -host shell getprop ro.product.branch') do echo 版本分支: %%b
for /f "delims=" %%b in (' adb -host shell getprop ro.product.branch') do echo 版本分支: %%b >>%dir%/version.txt
for /f "delims=:_ tokens=9" %%m in ('adb -host shell sys-test --get-ver') do echo MCU版本:%%m
for /f "delims=:_ tokens=9" %%m in ('adb -host shell sys-test --get-ver') do echo MCU版本:%%m >>%dir%/version.txt
for /f "delims=: tokens=2" %%d in ('adb -host shell dsp_upgrade --get_ver') do echo DSP版本:%%d
for /f "delims=: tokens=2" %%d in ('adb -host shell dsp_upgrade --get_ver') do echo DSP版本:%%d >>%dir%/version.txt
for /f "delims=" %%s in (' adb -host shell getprop ro.serialno') do echo SN: %%s
for /f "delims=" %%s in (' adb -host shell getprop ro.serialno') do echo SN: %%s >>%dir%/version.txt
for /f "delims=" %%n in (' adb -host shell getprop persist.sys.vin') do echo VIN: %%n
for /f "delims=" %%n in (' adb -host shell getprop persist.sys.vin') do echo VIN: %%n >>%dir%/version.txt
for /f "delims=" %%n in (' adb -host shell "getprop | grep uuid"') do echo UUID: %%n
for /f "delims=" %%n in (' adb -host shell "getprop | grep uuid"') do echo UUID: %%n >>%dir%/version.txt

call script/end.bat
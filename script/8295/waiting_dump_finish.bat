

:loop_tar
adb -host shell "ls /share/dump_finish | grep No" | findstr . >nul 2>&1
if errorlevel 1 (
	goto :screen_shot
) else (
    echo waitting /share/dump_finish
    ping 127.0.0.1 -n 4 >nul
    goto :loop_tar
)
:screen_shot

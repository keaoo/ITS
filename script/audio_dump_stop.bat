@echo off
chcp 65001 >nul

adb -host shell setprop persist.audio.dump 0
adb -host shell setprop audiohal.dump.write 0
adb -host shell audio_cli --set_params update_alsa_dump_prop=1

@echo off
chcp 65001 >nul

adb -host shell "echo 'enable n;' > /proc/alog"
adb -host shell mount -o remount rw /

call script\audio_dump_stop.bat
call script\audio_dump_clear.bat

echo.
echo  audiodump已开启，请复现问题后拉取log
echo.

adb -host shell mkdir -p /private/audio/audio_pipeline
adb -host shell mkdir -p /private/audio/audio_s
adb -host shell mkdir -p /private/audiohal

adb -host shell chown audio:audio /private/audio/audio_pipeline
adb -host shell chown audio:audio /private/audio/audio_s
adb -host shell chown audio:audio /private/audiohal

adb -host shell ln -s /private/audio/audio_pipeline /tmp/audio_pipeline
adb -host shell ln -s /private/audio/audio_s /tmp/audio_s
adb -host shell ln -s /private/audiohal /tmp/audiohal

adb -host shell setprop persist.audio.dump io
adb -host shell setprop audiohal.dump.write 1

adb -host shell audio_cli --set_params update_alsa_dump_prop=1



adb -host shell "amixer contents > /private/audio/contents_prepare.txt"
adb -host shell "audio_cli --capture_file /private/audio/as_record12.pcm --stream_type 1 --rate 16000 --num_channels 12 --block_size 1024 &"
echo audio_cli 已在后台运行

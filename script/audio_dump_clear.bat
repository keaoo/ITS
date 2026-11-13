@echo off
chcp 65001 >nul


adb -host shell rm -rf /tmp/audio*
adb -host shell rm -rf /tmp/audiohal

adb -host shell rm -rf /private/audio/audio_dump
adb -host shell rm -rf /private/audio/audio_pipeline
adb -host shell rm -rf /private/audio/audio_s
adb -host shell rm -rf /private/audio/audio_c_*
adb -host shell rm -rf /private/audio/as_record12*.pcm

adb -host shell rm -rf /private/audiohal

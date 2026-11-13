#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音测试指令配置 - 集中管理所有语音测试指令
"""

VOICE_INSTRUCTIONS = {
    "你好智己": {
        "mode": "tts",
        "tts_text": "你好智己",
        "tts_text_en": "Hello IM",
        "audio_file": "hello_zhiji.wav",
        "wait_seconds": 3,
        "expected_recognition": "你好智己",
        "verify_signals": []
    },
    "打开车窗": {
        "mode": "tts",
        "tts_text": "打开车窗",
        "tts_text_en": "Turn on the window",
        "audio_file": "open_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭车窗": {
        "mode": "tts",
        "tts_text": "关闭车窗",
        "tts_text_en": "Turn off the window",
        "audio_file": "close_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开主驾车窗": {
        "mode": "tts",
        "tts_text": "打开主驾车窗",
        "tts_text_en": "Open driver window",
        "audio_file": "open_driver_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭主驾车窗": {
        "mode": "tts",
        "tts_text": "关闭主驾车窗",
        "tts_text_en": "Close driver window",
        "audio_file": "close_driver_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭主驾车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开副驾车窗": {
        "mode": "tts",
        "tts_text": "打开副驾车窗",
        "tts_text_en": "Open passenger window",
        "audio_file": "open_passenger_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开副驾车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭副驾车窗": {
        "mode": "tts",
        "tts_text": "关闭副驾车窗",
        "tts_text_en": "Close passenger window",
        "audio_file": "close_passenger_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭副驾车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开左后车窗": {
        "mode": "tts",
        "tts_text": "打开左后车窗",
        "tts_text_en": "Open left rear window",
        "audio_file": "open_left_rear_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开左后车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭左后车窗": {
        "mode": "tts",
        "tts_text": "关闭左后车窗",
        "tts_text_en": "Close left rear window",
        "audio_file": "close_left_rear_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭左后车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开右后车窗": {
        "mode": "tts",
        "tts_text": "打开右后车窗",
        "tts_text_en": "Open right rear window",
        "audio_file": "open_right_rear_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开右后车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭右后车窗": {
        "mode": "tts",
        "tts_text": "关闭右后车窗",
        "tts_text_en": "Close right rear window",
        "audio_file": "close_right_rear_window.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭右后车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开前排车窗": {
        "mode": "tts",
        "tts_text": "打开前排车窗",
        "tts_text_en": "Open front windows",
        "audio_file": "open_front_windows.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开前排车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭前排车窗": {
        "mode": "tts",
        "tts_text": "关闭前排车窗",
        "tts_text_en": "Close front windows",
        "audio_file": "close_front_windows.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭前排车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开后排车窗": {
        "mode": "tts",
        "tts_text": "打开后排车窗",
        "tts_text_en": "Open rear windows",
        "audio_file": "open_rear_windows.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开后排车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭后排车窗": {
        "mode": "tts",
        "tts_text": "关闭后排车窗",
        "tts_text_en": "Close rear windows",
        "audio_file": "close_rear_windows.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭后排车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开全车车窗": {
        "mode": "tts",
        "tts_text": "打开全车车窗",
        "tts_text_en": "Open all windows",
        "audio_file": "open_all_windows.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开全车车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭全车车窗": {
        "mode": "tts",
        "tts_text": "关闭全车车窗",
        "tts_text_en": "Close all windows",
        "audio_file": "close_all_windows.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭全车车窗",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开车窗通风": {
        "mode": "tts",
        "tts_text": "打开车窗通风",
        "tts_text_en": "Open window vent",
        "audio_file": "open_window_vent.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开车窗通风",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "关闭车窗通风": {
        "mode": "tts",
        "tts_text": "关闭车窗通风",
        "tts_text_en": "Close window vent",
        "audio_file": "close_window_vent.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭车窗通风",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开全车车窗通风": {
        "mode": "tts",
        "tts_text": "打开全车车窗通风",
        "tts_text_en": "Open all window vents",
        "audio_file": "open_all_window_vents.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开全车车窗通风",
        "verify_signals": [
            ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl", 2),
            ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl", 2),
            ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl", 2),
            ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl", 2)
        ]
    },
    "打开悬架轻松进出": {
        "mode": "tts",
        "tts_text": "打开悬架轻松进出",
        "tts_text_en": "Open suspension easy access",
        "audio_file": "open_suspension_easy_access.wav",
        "wait_seconds": 15,
        "expected_recognition": "打开悬架轻松进出",
        "verify_signals": [
            ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
            ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
            ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
            ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
        ]
    },
    "关闭悬架轻松进出": {
        "mode": "tts",
        "tts_text": "关闭悬架轻松进出",
        "tts_text_en": "Close suspension easy access",
        "audio_file": "close_suspension_easy_access.wav",
        "wait_seconds": 15,
        "expected_recognition": "关闭悬架轻松进出",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "打开悬架轻松载物": {
        "mode": "tts",
        "tts_text": "打开悬架轻松载物",
        "tts_text_en": "Open suspension easy load",
        "audio_file": "open_suspension_easy_load.wav",
        "wait_seconds": 15,
        "expected_recognition": "打开悬架轻松载物",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "关闭悬架轻松载物": {
        "mode": "tts",
        "tts_text": "关闭悬架轻松载物",
        "tts_text_en": "Close suspension easy load",
        "audio_file": "close_suspension_easy_load.wav",
        "wait_seconds": 15,
        "expected_recognition": "关闭悬架轻松载物",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "打开悬架轻松通过": {
        "mode": "tts",
        "tts_text": "打开悬架轻松通过",
        "tts_text_en": "Open suspension easy pass",
        "audio_file": "open_suspension_easy_pass.wav",
        "wait_seconds": 20,
        "expected_recognition": "打开悬架轻松通过",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "关闭悬架轻松通过": {
        "mode": "tts",
        "tts_text": "关闭悬架轻松通过",
        "tts_text_en": "Close suspension easy pass",
        "audio_file": "close_suspension_easy_pass.wav",
        "wait_seconds": 20,
        "expected_recognition": "关闭悬架轻松通过",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "打开悬架极限通过": {
        "mode": "tts",
        "tts_text": "打开悬架极限通过",
        "tts_text_en": "Open suspension extreme pass",
        "audio_file": "open_suspension_extreme_pass.wav",
        "wait_seconds": 20,
        "expected_recognition": "打开悬架极限通过",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "关闭悬架极限通过": {
        "mode": "tts",
        "tts_text": "关闭悬架极限通过",
        "tts_text_en": "Close suspension extreme pass",
        "audio_file": "close_suspension_extreme_pass.wav",
        "wait_seconds": 20,
        "expected_recognition": "关闭悬架极限通过",
        "verify_signals": [("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 5),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 5),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 5),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 5)
                           ]
    },
    "打开空调": {
        "mode": "tts",
        "tts_text": "打开空调",
        "tts_text_en": "Turn on the air conditioner",
        "audio_file": "open_ac.wav",
        "wait_seconds": 4,
        "expected_recognition": "打开空调",
        "verify_signals": [
            ("空调状态", "adb -host shell vapisend -get ctrl.ac.power_status", 0)
        ]
    },
    "关闭空调": {
        "mode": "tts",
        "tts_text": "关闭空调",
        "tts_text_en": "Turn off the air conditioner",
        "audio_file": "close_ac.wav",
        "wait_seconds": 4,
        "expected_recognition": "关闭空调",
        "verify_signals": [
            ("空调状态", "adb -host shell vapisend -get ctrl.ac.power_status", 0)
        ]
    },
    "打开空调AC": {
        "mode": "tts",
        "tts_text": "打开空调AC",
        "tts_text_en": "Turn on AC",
        "audio_file": "open_ac.wav",
        "wait_seconds": 4,
        "expected_recognition": "打开空调AC",
        "verify_signals": [("AC状态", "adb -host shell vapisend -get ctrl.ac.compressor_switch", 0)
                           ]
    },
    "关闭空调AC": {
        "mode": "tts",
        "tts_text": "关闭空调AC",
        "tts_text_en": "Turn off AC",
        "audio_file": "close_ac.wav",
        "wait_seconds": 4,
        "expected_recognition": "关闭空调AC",
        "verify_signals": [("AC状态", "adb -host shell vapisend -get ctrl.ac.compressor_switch", 0)
                           ]
    },
    "空调温度调节到20.5度": {
        "mode": "tts",
        "tts_text": "空调温度调节到20.5度",
        "tts_text_en": "Set AC temperature to 20.5 degrees",
        "audio_file": "set_ac_temp_20.5.wav",
        "wait_seconds": 5,
        "expected_recognition": "空调温度调节到20.5度",
        "verify_signals": [("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
                           ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
                           ]
    },
    "空调温度调节到最低": {
        "mode": "tts",
        "tts_text": "空调温度调节到最低",
        "tts_text_en": "Set AC temperature to minimum",
        "audio_file": "set_ac_temp_min.wav",
        "wait_seconds": 10,
        "expected_recognition": "空调温度调节到最低",
        "verify_signals": [
            ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
            ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
        ]
    },
    "空调温度调节到30度": {
        "mode": "tts",
        "tts_text": "空调温度调节到30度",
        "tts_text_en": "Set AC temperature to 30 degrees",
        "audio_file": "set_ac_temp_30.wav",
        "wait_seconds": 5,
        "expected_recognition": "空调温度调节到30度",
        "verify_signals": [("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
                           ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
                           ]
    },
    "空调温度调节到最高": {
        "mode": "tts",
        "tts_text": "空调温度调节到最高",
        "tts_text_en": "Set AC temperature to maximum",
        "audio_file": "set_ac_temp_max.wav",
        "wait_seconds": 10,
        "expected_recognition": "空调温度调节到最高",
        "verify_signals": [("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
                           ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
                           ]
    },
    "副驾空调温度调节到25度": {
        "mode": "tts",
        "tts_text": "副驾空调温度调节到25度",
        "tts_text_en": "Set passenger AC temperature to 25 degrees",
        "audio_file": "set_passenger_ac_temp_25.wav",
        "wait_seconds": 5,
        "expected_recognition": "副驾空调温度调节到25度",
        "verify_signals": [("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
                           ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
                           ]
    },
    "打开温度同步": {
        "mode": "tts",
        "tts_text": "打开温度同步",
        "tts_text_en": "Turn on temperature sync",
        "audio_file": "turn_on_temp_sync.wav",
        "wait_seconds": 4,
        "expected_recognition": "打开温度同步",
        "verify_signals": [("温度同步状态", "adb -host shell vapisend -get ctrl.ac.dual_ctrl_status", 0),
                           ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
                           ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
                           ]
    },
    "关闭温度同步": {
        "mode": "tts",
        "tts_text": "关闭温度同步",
        "tts_text_en": "Turn on temperature sync",
        "audio_file": "turn_on_temp_sync.wav",
        "wait_seconds": 4,
        "expected_recognition": "关闭温度同步",
        "verify_signals": [("温度同步状态", "adb -host shell vapisend -get ctrl.ac.dual_ctrl_status", 0),
                           ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature", 0),
                           ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature", 0)
                           ]
    },
    "空调风量设置成最低": {
        "mode": "tts",
        "tts_text": "空调风量设置成最低",
        "tts_text_en": "Set AC fan speed to minimum",
        "audio_file": "set_ac_fan_min.wav",
        "wait_seconds": 4,
        "expected_recognition": "空调风量设置成最低",
        "verify_signals": [("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level", 0), ]
    },
    "空调风量5档": {
        "mode": "tts",
        "tts_text": "空调风量5档",
        "tts_text_en": "Set AC fan speed to 5",
        "audio_file": "set_ac_fan_5.wav",
        "wait_seconds": 4,
        "expected_recognition": "空调风量5档",
        "verify_signals": [("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level", 0), ]
    },
    "空调风量设置成最高": {
        "mode": "tts",
        "tts_text": "空调风量设置成最高",
        "tts_text_en": "Set AC fan speed to maximum",
        "audio_file": "set_ac_fan_max.wav",
        "wait_seconds": 4,
        "expected_recognition": "空调风量设置成最高",
        "verify_signals": [("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level", 0), ]
    },
    "空调风量3档": {
        "mode": "tts",
        "tts_text": "空调风量3档",
        "tts_text_en": "Set AC fan speed to 3",
        "audio_file": "set_ac_fan_3.wav",
        "wait_seconds": 4,
        "expected_recognition": "空调风量3档",
        "verify_signals": [("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level", 0), ]
    },
    "打开前排遮阳帘": {
        "mode": "tts",
        "tts_text": "打开前排遮阳帘",
        "tts_text_en": "Open front sunshade",
        "audio_file": "open_front_sunshade.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开前排遮阳帘",
        "verify_signals": [("前遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.shade_percentage", 2)]
    },
    "打开后排遮阳帘": {
        "mode": "tts",
        "tts_text": "打开后排遮阳帘",
        "tts_text_en": "Open rear sunshade",
        "audio_file": "open_rear_sunshade.wav",
        "wait_seconds": 15,
        "expected_recognition": "打开后排遮阳帘",
        "verify_signals": [("后遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.rear_shade_percentage", 2)]
    },
    "关闭前排遮阳帘": {
        "mode": "tts",
        "tts_text": "关闭前排遮阳帘",
        "tts_text_en": "Close front sunshade",
        "audio_file": "close_front_sunshade.wav",
        "wait_seconds": 10,
        "expected_recognition": "关闭前排遮阳帘",
        "verify_signals": [("前遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.shade_percentage", 2)]
    },
    "关闭后排遮阳帘": {
        "mode": "tts",
        "tts_text": "关闭后排遮阳帘",
        "tts_text_en": "Close rear sunshade",
        "audio_file": "close_rear_sunshade.wav",
        "wait_seconds": 15,
        "expected_recognition": "关闭后排遮阳帘",
        "verify_signals": [("后遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.rear_shade_percentage", 2)]
    },
    "打开前排空调自动模式": {
        "mode": "tts",
        "tts_text": "打开前排空调自动模式",
        "tts_text_en": "Turn on front AC auto mode",
        "audio_file": "open_front_ac_auto.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开前排空调自动模式",
        "verify_signals": [("前排空调Auto模式状态", "adb -host shell vapisend -get ctrl.ac.auto_mode", 0),
                           ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level", 0),
                           ]
    },
    "关闭前排空调自动模式": {
        "mode": "tts",
        "tts_text": "关闭前排空调自动模式",
        "tts_text_en": "Turn off front AC auto mode",
        "audio_file": "close_front_ac_auto.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭前排空调自动模式",
        "verify_signals": [("前排空调Auto模式状态", "adb -host shell vapisend -get ctrl.ac.auto_mode", 0),
                           ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level", 0),
                           ]
    },
    "打开后视镜加热": {
        "mode": "tts",
        "tts_text": "打开后视镜加热",
        "tts_text_en": "Turn on mirror heater",
        "audio_file": "open_mirror_heater.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开后视镜加热",
        "verify_signals": [("后视镜加热状态", "adb -host shell vapisend -get ctrl.mirror.heating", 0)]
    },
    "关闭后视镜加热": {
        "mode": "tts",
        "tts_text": "关闭后视镜加热",
        "tts_text_en": "Turn off mirror heater",
        "audio_file": "close_mirror_heater.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭后视镜加热",
        "verify_signals": [("后视镜加热状态", "adb -host shell vapisend -get ctrl.mirror.heating", 0)]
    },
    "折叠后视镜": {
        "mode": "tts",
        "tts_text": "折叠后视镜",
        "tts_text_en": "Fold mirror",
        "audio_file": "fold_mirror.wav",
        "wait_seconds": 8,
        "expected_recognition": "折叠后视镜",
        "verify_signals": [("后视镜状态", "adb -host shell vapisend -get ctrl.custom.536871720", 0)]
    },
    "展开后视镜": {
        "mode": "tts",
        "tts_text": "展开后视镜",
        "tts_text_en": "Unfold mirror",
        "audio_file": "unfold_mirror.wav",
        "wait_seconds": 8,
        "expected_recognition": "展开后视镜",
        "verify_signals": [("后视镜状态", "adb -host shell vapisend -get ctrl.custom.536871720", 0)]
    },
    "打开方向盘加热": {
        "mode": "tts",
        "tts_text": "打开方向盘加热",
        "tts_text_en": "Turn on steering wheel heater",
        "audio_file": "open_steering_heater.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开方向盘加热",
        "verify_signals": [("方向盘加热状态", "adb -host shell vapisend -get ctrl.custom.536871754", 0)]
    },
    "方向盘加热调节到2档": {
        "mode": "tts",
        "tts_text": "方向盘加热调节到2档",
        "tts_text_en": "Set steering wheel heater to level 2",
        "audio_file": "set_steering_heater_level2.wav",
        "wait_seconds": 2,
        "expected_recognition": "方向盘加热调节到2档",
        "verify_signals": [("方向盘加热挡位", "adb -host shell vapisend -get ctrl.custom.536871754", 0)]
    },
    "关闭方向盘加热": {
        "mode": "tts",
        "tts_text": "关闭方向盘加热",
        "tts_text_en": "Turn off steering wheel heater",
        "audio_file": "close_steering_heater.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭方向盘加热",
        "verify_signals": [("方向盘加热状态", "adb -host shell vapisend -get ctrl.custom.536871754", 0)]
    },
    "打开后备箱": {
        "mode": "tts",
        "tts_text": "打开后备箱",
        "tts_text_en": "Open trunk",
        "audio_file": "open_trunk.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开后备箱",
        "verify_signals": [("尾门开度", "adb -host shell vapisend -get ctrl.door.elec_plg_status", 0),
                           ("尾门锁状态", "adb -host shell vapisend -get ctrl.door.trunk_status", 0),
                           ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 8),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 8),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 8),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 8)]
    },
    "关闭后备箱": {
        "mode": "tts",
        "tts_text": "关闭后备箱",
        "tts_text_en": "Close trunk",
        "audio_file": "close_trunk.wav",
        "wait_seconds": 8,
        "expected_recognition": "关闭后备箱",
        "verify_signals": [("尾门开度", "adb -host shell vapisend -get ctrl.door.elec_plg_status", 0),
                           ("尾门锁状态", "adb -host shell vapisend -get ctrl.door.trunk_status", 0),
                           ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241", 8),
                           ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243", 8),
                           ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245", 8),
                           ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247", 8)
                           ]
    },
    "打开充电小门": {
        "mode": "tts",
        "tts_text": "打开充电小门",
        "tts_text_en": "Open charge port door",
        "audio_file": "open_charge_port.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开充电小门",
        "verify_signals": [("充电小门状态", "adb -host shell vapisend -get ctrl.custom.536871466", 0)]
    },
    "关闭充电小门": {
        "mode": "tts",
        "tts_text": "关闭充电小门",
        "tts_text_en": "Close charge port door",
        "audio_file": "close_charge_port.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭充电小门",
        "verify_signals": [("充电小门状态", "adb -host shell vapisend -get ctrl.custom.536871466", 0)]
    },
    "打开进出位置": {
        "mode": "tts",
        "tts_text": "打开进出位置",
        "tts_text_en": "Open Entry/Exit Position",
        "audio_file": "open_entry_exit.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开进出位置",
        "verify_signals": [
                    ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
                    ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ]
    },
    "退出进出位置": {
        "mode": "tts",
        "tts_text": "退出进出位置",
        "tts_text_en": "Exit Entry/Exit Position",
        "audio_file": "exit_entry_exit.wav",
        "wait_seconds": 5,
        "expected_recognition": "退出进出位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ]
    },
    "打开驾驶位置": {
        "mode": "tts",
        "tts_text": "打开驾驶位置",
        "tts_text_en": "Open Driving Position",
        "audio_file": "open_driving.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开驾驶位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
        ]
    },
    "退出驾驶位置": {
        "mode": "tts",
        "tts_text": "退出驾驶位置",
        "tts_text_en": "Exit Driving Position",
        "audio_file": "exit_driving.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出驾驶位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
        ]
    },
    "打开休息位置": {
        "mode": "tts",
        "tts_text": "打开休息位置",
        "tts_text_en": "Open Rest Position",
        "audio_file": "open_rest.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开休息位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ]
    },
    "退出休息位置": {
        "mode": "tts",
        "tts_text": "退出休息位置",
        "tts_text_en": "Exit Rest Position",
        "audio_file": "exit_rest.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出休息位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ]
    },
    "打开备用位置": {
        "mode": "tts",
        "tts_text": "打开备用位置",
        "tts_text_en": "Open Backup Position",
        "audio_file": "open_backup.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开备用位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ]
    },
    "退出备用位置": {
        "mode": "tts",
        "tts_text": "退出备用位置",
        "tts_text_en": "Exit Backup Position",
        "audio_file": "exit_backup.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出备用位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ]
    },
    "打开其他位置": {
        "mode": "tts",
        "tts_text": "打开其他位置",
        "tts_text_en": "Open Other Position",
        "audio_file": "open_other.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开其他位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "退出其他位置": {
        "mode": "tts",
        "tts_text": "退出其他位置",
        "tts_text_en": "Exit Other Position",
        "audio_file": "exit_other.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出其他位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636"),
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "打开主驾进出位置": {
        "mode": "tts",
        "tts_text": "打开主驾进出位置",
        "tts_text_en": "Open Driver's Entry/Exit Position",
        "audio_file": "open_driver_entry_exit.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开主驾进出位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "退出主驾进出位置": {
        "mode": "tts",
        "tts_text": "退出主驾进出位置",
        "tts_text_en": "Exit Driver's Entry/Exit Position",
        "audio_file": "exit_driver_entry_exit.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出主驾进出位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "打开主驾驾驶位置": {
        "mode": "tts",
        "tts_text": "打开主驾驾驶位置",
        "tts_text_en": "Open Driver's Driving Position",
        "audio_file": "open_driver_driving.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开主驾驾驶位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "退出主驾驾驶位置": {
        "mode": "tts",
        "tts_text": "退出主驾驾驶位置",
        "tts_text_en": "Exit Driver's Driving Position",
        "audio_file": "exit_driver_driving.wav",
        "wait_seconds": 5,
        "expected_recognition": "退出主驾驾驶位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "打开主驾休息位置": {
        "mode": "tts",
        "tts_text": "打开主驾休息位置",
        "tts_text_en": "Open Driver's Rest Position",
        "audio_file": "open_driver_rest.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾休息位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "退出主驾休息位置": {
        "mode": "tts",
        "tts_text": "退出主驾休息位置",
        "tts_text_en": "Exit Driver's Rest Position",
        "audio_file": "exit_driver_rest.wav",
        "wait_seconds": 5,
        "expected_recognition": "退出主驾休息位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "打开主驾备用位置": {
        "mode": "tts",
        "tts_text": "打开主驾备用位置",
        "tts_text_en": "Open Driver's Backup Position",
        "audio_file": "open_driver_backup.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾备用位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "退出主驾备用位置": {
        "mode": "tts",
        "tts_text": "退出主驾备用位置",
        "tts_text_en": "Exit Driver's Backup Position",
        "audio_file": "exit_driver_backup.wav",
        "wait_seconds": 5,
        "expected_recognition": "退出主驾备用位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "打开主驾其他位置": {
        "mode": "tts",
        "tts_text": "打开主驾其他位置",
        "tts_text_en": "Open Driver's Other Position",
        "audio_file": "open_driver_other.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾其他位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "退出主驾其他位置": {
        "mode": "tts",
        "tts_text": "退出主驾其他位置",
        "tts_text_en": "Exit Driver's Other Position",
        "audio_file": "exit_driver_other.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出主驾其他位置",
        "verify_signals": [
            ("主驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
            ("主驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
            ("主驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
            ("主驾靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
        ]
    },
    "打开座椅按摩": {
        "mode": "tts",
        "tts_text": "打开座椅按摩",
        "tts_text_en": "Open Seat Massage",
        "audio_file": "open_seat_massage.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开座椅按摩",
        "verify_signals": [
            ("主驾按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871649"),
        ]
    },
    "关闭座椅按摩": {
        "mode": "tts",
        "tts_text": "关闭座椅按摩",
        "tts_text_en": "Close Seat Massage",
        "audio_file": "close_seat_massage.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭座椅按摩",
        "verify_signals": [
            ("主驾按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871649"),
        ]
    },
    "打开座椅加热": {
        "mode": "tts",
        "tts_text": "打开座椅加热",
        "tts_text_en": "Open Seat Heating",
        "audio_file": "open_seat_heating.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开座椅加热",
        "verify_signals": [
            ("主驾座椅加热状态", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
        ]
    },
    "座椅加热调节到2档": {
        "mode": "tts",
        "tts_text": "座椅加热调节到2档",
        "tts_text_en": "Set Seat Heating to Level 2",
        "audio_file": "seat_heating_level2.wav",
        "wait_seconds": 5,
        "expected_recognition": "座椅加热调节到2档",
        "verify_signals": [
            ("主驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
        ]
    },
    "关闭座椅加热": {
        "mode": "tts",
        "tts_text": "关闭座椅加热",
        "tts_text_en": "Close Seat Heating",
        "audio_file": "close_seat_heating.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭座椅加热",
        "verify_signals": [
            ("主驾座椅加热状态", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
        ]
    },
    "打开座椅通风": {
        "mode": "tts",
        "tts_text": "打开座椅通风",
        "tts_text_en": "Open Seat Ventilation",
        "audio_file": "open_seat_ventilation.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开座椅通风",
        "verify_signals": [
            ("主驾座椅通风2档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
        ]
    },
    "座椅通风调节到2档": {
        "mode": "tts",
        "tts_text": "座椅通风调节到2档",
        "tts_text_en": "Set Seat Ventilation to Level 2",
        "audio_file": "seat_ventilation_level2.wav",
        "wait_seconds": 5,
        "expected_recognition": "座椅通风调节到2档",
        "verify_signals": [
            ("主驾座椅通风2档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
        ]
    },
    "关闭座椅通风": {
        "mode": "tts",
        "tts_text": "关闭座椅通风",
        "tts_text_en": "Close Seat Ventilation",
        "audio_file": "close_seat_ventilation.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭座椅通风",
        "verify_signals": [
            ("主驾座椅通风状态", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
        ]
    },
    "打开主驾座椅按摩": {
        "mode": "tts",
        "tts_text": "打开主驾座椅按摩",
        "tts_text_en": "Open Driver's Seat Massage",
        "audio_file": "open_driver_seat_massage.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾座椅按摩",
        "verify_signals": [
            ("主驾按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871649"),
        ]
    },
    "关闭主驾座椅按摩": {
        "mode": "tts",
        "tts_text": "关闭主驾座椅按摩",
        "tts_text_en": "Close Driver's Seat Massage",
        "audio_file": "close_driver_seat_massage.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭主驾座椅按摩",
        "verify_signals": [
            ("主驾按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871649"),
        ]
    },
    "打开主驾座椅加热": {
        "mode": "tts",
        "tts_text": "打开主驾座椅加热",
        "tts_text_en": "Open Driver's Seat Heating",
        "audio_file": "open_driver_seat_heating.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾座椅加热",
        "verify_signals": [
            ("主驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
        ]
    },
    "主驾座椅加热调节到2档": {
        "mode": "tts",
        "tts_text": "主驾座椅加热调节到2档",
        "tts_text_en": "Set Driver's Seat Heating to Level 2",
        "audio_file": "driver_seat_heating_level2.wav",
        "wait_seconds": 5,
        "expected_recognition": "主驾座椅加热调节到2档",
        "verify_signals": [
            ("主驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
        ]
    },
    "关闭主驾座椅加热": {
        "mode": "tts",
        "tts_text": "关闭主驾座椅加热",
        "tts_text_en": "Close Driver's Seat Heating",
        "audio_file": "close_driver_seat_heating.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭主驾座椅加热",
        "verify_signals": [
            ("主驾座椅加热状态", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
        ]
    },
    "打开主驾座椅通风": {
        "mode": "tts",
        "tts_text": "打开主驾座椅通风",
        "tts_text_en": "Open Driver's Seat Ventilation",
        "audio_file": "open_driver_seat_ventilation.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾座椅通风",
        "verify_signals": [
            ("主驾座椅通风2档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
        ]
    },
    "主驾座椅通风调节到2档": {
        "mode": "tts",
        "tts_text": "主驾座椅通风调节到2档",
        "tts_text_en": "Set Driver's Seat Ventilation to Level 2",
        "audio_file": "driver_seat_ventilation_level2.wav",
        "wait_seconds": 5,
        "expected_recognition": "主驾座椅通风调节到2档",
        "verify_signals": [
            ("主驾座椅通风2档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
        ]
    },
    "关闭主驾座椅通风": {
        "mode": "tts",
        "tts_text": "关闭主驾座椅通风",
        "tts_text_en": "Close Driver's Seat Ventilation",
        "audio_file": "close_driver_seat_ventilation.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭主驾座椅通风",
        "verify_signals": [
            ("主驾座椅通风状态", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
        ]
    },
    "打开副驾常用位置": {
        "mode": "tts",
        "tts_text": "打开副驾常用位置",
        "tts_text_en": "Open Passenger's Common Position",
        "audio_file": "open_passenger_common.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开副驾常用位置",
        "verify_signals": [
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "退出副驾常用位置": {
        "mode": "tts",
        "tts_text": "退出副驾常用位置",
        "tts_text_en": "Exit Passenger's Common Position",
        "audio_file": "exit_passenger_common.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出副驾常用位置",
        "verify_signals": [
            ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "打开副驾休息位置": {
        "mode": "tts",
        "tts_text": "打开副驾休息位置",
        "tts_text_en": "Open Passenger's Rest Position",
        "audio_file": "open_passenger_rest.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开副驾休息位置",
        "verify_signals": [
            ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "退出副驾休息位置": {
        "mode": "tts",
        "tts_text": "退出副驾休息位置",
        "tts_text_en": "Exit Passenger's Rest Position",
        "audio_file": "exit_passenger_rest.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出副驾休息位置",
        "verify_signals": [
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "打开副驾备用位置": {
        "mode": "tts",
        "tts_text": "打开副驾备用位置",
        "tts_text_en": "Open Passenger's Backup Position",
        "audio_file": "open_passenger_backup.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开副驾备用位置",
        "verify_signals": [
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "退出副驾备用位置": {
        "mode": "tts",
        "tts_text": "退出副驾备用位置",
        "tts_text_en": "Exit Passenger's Backup Position",
        "audio_file": "exit_passenger_backup.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出副驾备用位置",
        "verify_signals": [
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "打开副驾其他位置": {
        "mode": "tts",
        "tts_text": "打开副驾其他位置",
        "tts_text_en": "Open Passenger's Other Position",
        "audio_file": "open_passenger_other.wav",
        "wait_seconds": 10,
        "expected_recognition": "打开副驾其他位置",
        "verify_signals": [
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "退出副驾其他位置": {
        "mode": "tts",
        "tts_text": "退出副驾其他位置",
        "tts_text_en": "Exit Passenger's Other Position",
        "audio_file": "exit_passenger_other.wav",
        "wait_seconds": 10,
        "expected_recognition": "退出副驾其他位置",
        "verify_signals": [
            ("副驾前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
            ("副驾上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
            ("副驾抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
            ("副驾靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
        ]
    },
    "打开副驾座椅按摩": {
        "mode": "tts",
        "tts_text": "打开副驾座椅按摩",
        "tts_text_en": "Open Passenger's Seat Massage",
        "audio_file": "open_passenger_seat_massage.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开副驾座椅按摩",
        "verify_signals": [
            ("副驾座椅按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871657"),
        ]
    },
    "关闭副驾座椅按摩": {
        "mode": "tts",
        "tts_text": "关闭副驾座椅按摩",
        "tts_text_en": "Close Passenger's Seat Massage",
        "audio_file": "close_passenger_seat_massage.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭副驾座椅按摩",
        "verify_signals": [
            ("副驾座椅按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871657"),
        ]
    },
    "打开副驾座椅加热": {
        "mode": "tts",
        "tts_text": "打开副驾座椅加热",
        "tts_text_en": "Open Passenger's Seat Heating",
        "audio_file": "open_passenger_seat_heating.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开副驾座椅加热",
        "verify_signals": [
            ("副驾座椅加热状态", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
        ]
    },
    "副驾座椅加热调节到2档": {
        "mode": "tts",
        "tts_text": "副驾座椅加热调节到2档",
        "tts_text_en": "Set Passenger's Seat Heating to Level 2",
        "audio_file": "passenger_seat_heating_level2.wav",
        "wait_seconds": 5,
        "expected_recognition": "副驾座椅加热调节到2档",
        "verify_signals": [
            ("副驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
        ]
    },
    "关闭副驾座椅加热": {
        "mode": "tts",
        "tts_text": "关闭副驾座椅加热",
        "tts_text_en": "Close Passenger's Seat Heating",
        "audio_file": "close_passenger_seat_heating.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭副驾座椅加热",
        "verify_signals": [
            ("副驾座椅加热关闭", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
        ]
    },
    "打开副驾座椅通风": {
        "mode": "tts",
        "tts_text": "打开副驾座椅通风",
        "tts_text_en": "Open Passenger's Seat Ventilation",
        "audio_file": "open_passenger_seat_ventilation.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开副驾座椅通风",
        "verify_signals": [
            ("副驾座椅通风2档态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
        ]
    },
    "副驾座椅通风调节到2档": {
        "mode": "tts",
        "tts_text": "副驾座椅通风调节到2档",
        "tts_text_en": "Set Passenger's Seat Ventilation to Level 2",
        "audio_file": "passenger_seat_ventilation_level2.wav",
        "wait_seconds": 5,
        "expected_recognition": "副驾座椅通风调节到2档",
        "verify_signals": [
            ("副驾座椅通风2档态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
        ]
    },
    "关闭副驾座椅通风": {
        "mode": "tts",
        "tts_text": "关闭副驾座椅通风",
        "tts_text_en": "Close Passenger's Seat Ventilation",
        "audio_file": "close_passenger_seat_ventilation.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭副驾座椅通风",
        "verify_signals": [
            ("副驾座椅通风状态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
        ]
    },
    "打开全车阅读灯": {
        "mode": "tts",
        "tts_text": "打开全车阅读灯",
        "tts_text_en": "Open All Reading Lights",
        "audio_file": "open_all_reading_lights.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开全车阅读灯",
        "verify_signals": [
             ("整车阅读状态", "adb -host shell vapisend -get ctrl.custom.536871681"),
        ]
    },
    "关闭全车阅读灯": {
        "mode": "tts",
        "tts_text": "关闭全车阅读灯",
        "tts_text_en": "Close All Reading Lights",
        "audio_file": "close_all_reading_lights.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭全车阅读灯",
        "verify_signals": [
            ("整车阅读状态", "adb -host shell vapisend -get ctrl.custom.536871681"),
        ]
    },
    "打开阅读灯": {
        "mode": "tts",
        "tts_text": "打开阅读灯",
        "tts_text_en": "Open Reading Light",
        "audio_file": "open_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "关闭阅读灯": {
        "mode": "tts",
        "tts_text": "关闭阅读灯",
        "tts_text_en": "Close Reading Light",
        "audio_file": "close_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]

    },
    "打开主驾阅读灯": {
        "mode": "tts",
        "tts_text": "打开主驾阅读灯",
        "tts_text_en": "Open Driver's Reading Light",
        "audio_file": "open_driver_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开主驾阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "关闭主驾阅读灯": {
        "mode": "tts",
        "tts_text": "关闭主驾阅读灯",
        "tts_text_en": "Close Driver's Reading Light",
        "audio_file": "close_driver_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭主驾阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "打开副驾阅读灯": {
        "mode": "tts",
        "tts_text": "打开副驾阅读灯",
        "tts_text_en": "Open Passenger's Reading Light",
        "audio_file": "open_passenger_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开副驾阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "关闭副驾阅读灯": {
        "mode": "tts",
        "tts_text": "关闭副驾阅读灯",
        "tts_text_en": "Close Passenger's Reading Light",
        "audio_file": "close_passenger_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭副驾阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "打开左后阅读灯": {
        "mode": "tts",
        "tts_text": "打开左后阅读灯",
        "tts_text_en": "Open Left Rear Reading Light",
        "audio_file": "open_left_rear_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开左后阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "关闭左后阅读灯": {
        "mode": "tts",
        "tts_text": "关闭左后阅读灯",
        "tts_text_en": "Close Left Rear Reading Light",
        "audio_file": "close_left_rear_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭左后阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    "打开右后阅读灯": {
        "mode": "tts",
        "tts_text": "打开右后阅读灯",
        "tts_text_en": "Open Right Rear Reading Light",
        "audio_file": "open_right_rear_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "打开右后阅读灯",
        "verify_signals": [
             ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
             ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
             ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
             ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),]
    },
    "关闭右后阅读灯": {
        "mode": "tts",
        "tts_text": "关闭右后阅读灯",
        "tts_text_en": "Close Right Rear Reading Light",
        "audio_file": "close_right_rear_reading_light.wav",
        "wait_seconds": 5,
        "expected_recognition": "关闭右后阅读灯",
        "verify_signals": [
            ("左前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871682"),
            ("右前阅读状态", "adb -host shell vapisend -get ctrl.custom.536871684"),
            ("左后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871686"),
            ("右后阅读状态", "adb -host shell vapisend -get ctrl.custom.536871688"),
        ]
    },
    # ==================== 应用控制指令 ====================
    "打开爱奇艺": {
        "mode": "tts",
        "tts_text": "打开爱奇艺",
        "tts_text_en": "Open iQiyi",
        "audio_file": "open_iqiyi.wav",
        "wait_seconds": 3,
        "expected_recognition": "打开爱奇艺",
        "verify_signals": []
    },
    "关闭爱奇艺": {
        "mode": "tts",
        "tts_text": "关闭爱奇艺",
        "tts_text_en": "Close iQiyi",
        "audio_file": "close_iqiyi.wav",
        "wait_seconds": 3,
        "expected_recognition": "关闭爱奇艺",
        "verify_signals": []
    },
    "打开哔哩哔哩": {
        "mode": "tts",
        "tts_text": "打开哔哩哔哩",
        "tts_text_en": "Open Bilibili",
        "audio_file": "open_bilibili.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开哔哩哔哩",
        "verify_signals": []
    },
    "关闭哔哩哔哩": {
        "mode": "tts",
        "tts_text": "关闭哔哩哔哩",
        "tts_text_en": "Close Bilibili",
        "audio_file": "close_bilibili.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭哔哩哔哩",
        "verify_signals": []
    },
    "打开上观新闻": {
        "mode": "tts",
        "tts_text": "打开上观新闻",
        "tts_text_en": "Open Shangguan News",
        "audio_file": "open_shangguan_news.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开上观新闻",
        "verify_signals": []
    },
    "关闭上观新闻": {
        "mode": "tts",
        "tts_text": "关闭上观新闻",
        "tts_text_en": "Close Shangguan News",
        "audio_file": "close_shangguan_news.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭上观新闻",
        "verify_signals": []
    },
    "打开一路刷": {
        "mode": "tts",
        "tts_text": "打开一路刷",
        "tts_text_en": "Open Yilu Shua",
        "audio_file": "open_yilu_shua.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开一路刷",
        "verify_signals": []
    },
    "关闭一路刷": {
        "mode": "tts",
        "tts_text": "关闭一路刷",
        "tts_text_en": "Close Yilu Shua",
        "audio_file": "close_yilu_shua.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭一路刷",
        "verify_signals": []
    },
    "打开 QQ 音乐": {
        "mode": "tts",
        "tts_text": "打开 QQ 音乐",
        "tts_text_en": "Open QQ Music",
        "audio_file": "open_qq_music.wav",
        "wait_seconds": 3,
        "expected_recognition": "打开 QQ 音乐",
        "verify_signals": []
    },
    "关闭 QQ 音乐": {
        "mode": "tts",
        "tts_text": "关闭 QQ 音乐",
        "tts_text_en": "Close QQ Music",
        "audio_file": "close_qq_music.wav",
        "wait_seconds": 3,
        "expected_recognition": "关闭 QQ 音乐",
        "verify_signals": []
    },
    "打开网易云音乐": {
        "mode": "tts",
        "tts_text": "打开网易云音乐",
        "tts_text_en": "Open NetEase Cloud Music",
        "audio_file": "open_netease_music.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开网易云音乐",
        "verify_signals": []
    },
    "关闭网易云音乐": {
        "mode": "tts",
        "tts_text": "关闭网易云音乐",
        "tts_text_en": "Close NetEase Cloud Music",
        "audio_file": "close_netease_music.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭网易云音乐",
        "verify_signals": []
    },
    "打开蓝牙音乐": {
        "mode": "tts",
        "tts_text": "打开蓝牙音乐",
        "tts_text_en": "Open Bluetooth Music",
        "audio_file": "open_bluetooth_music.wav",
        "wait_seconds": 2,
        "expected_recognition": "打开蓝牙音乐",
        "verify_signals": []
    },
    "关闭蓝牙音乐": {
        "mode": "tts",
        "tts_text": "关闭蓝牙音乐",
        "tts_text_en": "Close Bluetooth Music",
        "audio_file": "close_bluetooth_music.wav",
        "wait_seconds": 2,
        "expected_recognition": "关闭蓝牙音乐",
        "verify_signals": []
    },


}


_WINDOW_INSTRUCTION_NAMES = {
    "\u6253\u5f00\u8f66\u7a97",
    "\u5173\u95ed\u8f66\u7a97",
    "\u6253\u5f00\u4e3b\u9a7e\u8f66\u7a97",
    "\u5173\u95ed\u4e3b\u9a7e\u8f66\u7a97",
    "\u6253\u5f00\u526f\u9a7e\u8f66\u7a97",
    "\u5173\u95ed\u526f\u9a7e\u8f66\u7a97",
    "\u6253\u5f00\u5de6\u540e\u8f66\u7a97",
    "\u5173\u95ed\u5de6\u540e\u8f66\u7a97",
    "\u6253\u5f00\u53f3\u540e\u8f66\u7a97",
    "\u5173\u95ed\u53f3\u540e\u8f66\u7a97",
    "\u6253\u5f00\u524d\u6392\u8f66\u7a97",
    "\u5173\u95ed\u524d\u6392\u8f66\u7a97",
    "\u6253\u5f00\u540e\u6392\u8f66\u7a97",
    "\u5173\u95ed\u540e\u6392\u8f66\u7a97",
    "\u6253\u5f00\u5168\u8f66\u8f66\u7a97",
    "\u5173\u95ed\u5168\u8f66\u8f66\u7a97",
    "\u6253\u5f00\u8f66\u7a97\u901a\u98ce",
    "\u5173\u95ed\u8f66\u7a97\u901a\u98ce",
    "\u6253\u5f00\u5168\u8f66\u8f66\u7a97\u901a\u98ce",
}
_WINDOW_VERIFY_SIGNALS = [
    ("\u4e3b\u9a7e\u8f66\u7a97", "adb -host shell vapisend -get Vehicle.Cabin.Door.Row1.DriverSide.Window.Position", 2),
    ("\u526f\u9a7e\u8f66\u7a97", "adb -host shell vapisend -get Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position", 2),
    ("\u5de6\u540e\u8f66\u7a97", "adb -host shell vapisend -get Vehicle.Cabin.Door.Row2.DriverSide.Window.Position", 2),
    ("\u53f3\u540e\u8f66\u7a97", "adb -host shell vapisend -get Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position", 2),
]
for _window_name in _WINDOW_INSTRUCTION_NAMES:
    if _window_name in VOICE_INSTRUCTIONS:
        VOICE_INSTRUCTIONS[_window_name]["verify_signals"] = list(_WINDOW_VERIFY_SIGNALS)

_SUSPENSION_INSTRUCTION_NAMES = {
    "\u6253\u5f00\u60ac\u67b6\u8f7b\u677e\u8fdb\u51fa",
    "\u5173\u95ed\u60ac\u67b6\u8f7b\u677e\u8fdb\u51fa",
    "\u6253\u5f00\u60ac\u67b6\u8f7b\u677e\u8f7d\u7269",
    "\u5173\u95ed\u60ac\u67b6\u8f7b\u677e\u8f7d\u7269",
    "\u6253\u5f00\u60ac\u67b6\u8f7b\u677e\u901a\u8fc7",
    "\u5173\u95ed\u60ac\u67b6\u8f7b\u677e\u901a\u8fc7",
    "\u6253\u5f00\u60ac\u67b6\u6781\u9650\u901a\u8fc7",
    "\u5173\u95ed\u60ac\u67b6\u6781\u9650\u901a\u8fc7",
}
_SUSPENSION_VERIFY_SIGNALS = [
    ("\u5de6\u524d\u9ad8\u5ea6", "adb shell vapisend -get Vehicle.Chassis.Suspension.HeightChange.FrontLeft", 5),
    ("\u53f3\u524d\u9ad8\u5ea6", "adb shell vapisend -get Vehicle.Chassis.Suspension.HeightChange.FrontRight", 5),
    ("\u5de6\u540e\u9ad8\u5ea6", "adb shell vapisend -get Vehicle.Chassis.Suspension.HeightChange.RearLeft", 5),
    ("\u53f3\u540e\u9ad8\u5ea6", "adb shell vapisend -get Vehicle.Chassis.Suspension.HeightChange.RearRight", 5),
]
_AC_POWER_INSTRUCTION_NAMES = {"\u6253\u5f00\u7a7a\u8c03", "\u5173\u95ed\u7a7a\u8c03"}
_AC_POWER_VERIFY_SIGNALS = [
    ("\u7a7a\u8c03\u72b6\u6001", "adb shell vapisend -get Vehicle.Cabin.HVAC.IsAirConditioningActive", 0),
]
_AC_COMPRESSOR_INSTRUCTION_NAMES = {"\u6253\u5f00\u7a7a\u8c03AC", "\u5173\u95ed\u7a7a\u8c03AC"}
_AC_COMPRESSOR_VERIFY_SIGNALS = [
    ("AC\u72b6\u6001", "adb shell vapisend -get Vehicle.Cabin.HVAC.IsCompressorActive", 0),
]
_AC_AUTO_MODE_INSTRUCTION_NAMES = {"打开前排空调自动模式", "关闭前排空调自动模式"}
_AC_AUTO_MODE_VERIFY_SIGNALS = [
    ("前排空调自动模式状态", "adb shell vapisend -get Vehicle.Cabin.HVAC.Station.Row1.IsAutoModeActive", 0),
]
_AC_TEMPERATURE_INSTRUCTION_NAMES = {
    "空调温度调节到20.5度",
    "\u7a7a\u8c03\u6e29\u5ea6\u8c03\u8282\u5230\u6700\u4f4e",
    "\u7a7a\u8c03\u6e29\u5ea6\u8c03\u8282\u5230\u0033\u0030\u5ea6",
    "\u7a7a\u8c03\u6e29\u5ea6\u8c03\u8282\u5230\u6700\u9ad8",
    "\u526f\u9a7e\u7a7a\u8c03\u6e29\u5ea6\u8c03\u8282\u5230\u0032\u0035\u5ea6",
}
_AC_TEMPERATURE_VERIFY_SIGNALS = [
    ("\u4e3b\u9a7e\u6e29\u5ea6", "adb shell vapisend -get Vehicle.Cabin.HVAC.Station.Row1.HardButton.DriverTemperature", 0),
    ("\u526f\u9a7e\u6e29\u5ea6", "adb shell vapisend -get Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature", 0),
]
_AC_SYNC_INSTRUCTION_NAMES = {"\u6253\u5f00\u6e29\u5ea6\u540c\u6b65", "\u5173\u95ed\u6e29\u5ea6\u540c\u6b65"}
_AC_SYNC_VERIFY_SIGNALS = list(_AC_TEMPERATURE_VERIFY_SIGNALS)
_AC_FAN_INSTRUCTION_NAMES = {
    "\u7a7a\u8c03\u98ce\u91cf\u8bbe\u7f6e\u6210\u6700\u4f4e",
    "\u7a7a\u8c03\u98ce\u91cf5\u6863",
    "\u7a7a\u8c03\u98ce\u91cf\u8bbe\u7f6e\u6210\u6700\u9ad8",
    "\u7a7a\u8c03\u98ce\u91cf3\u6863",
}
_AC_FAN_VERIFY_SIGNALS = [
    ("\u524d\u6392\u98ce\u91cf\u6321\u4f4d", "adb shell vapisend -get Vehicle.Cabin.HVAC.Station.Row1.FanSpeedLevel", 0),
]
_FRONT_SHADE_INSTRUCTION_NAMES = {"\u6253\u5f00\u524d\u6392\u906e\u9633\u5e18", "\u5173\u95ed\u524d\u6392\u906e\u9633\u5e18"}
_FRONT_SHADE_VERIFY_SIGNALS = [
    ("\u524d\u906e\u9633\u5e18\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Sunroof.Shade.Position", 2),
]
_REAR_SHADE_INSTRUCTION_NAMES = {"\u6253\u5f00\u540e\u6392\u906e\u9633\u5e18", "\u5173\u95ed\u540e\u6392\u906e\u9633\u5e18"}
_REAR_SHADE_VERIFY_SIGNALS = [
    ("\u540e\u906e\u9633\u5e18\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.RearShade.Position", 2),
]
_MIRROR_HEATING_INSTRUCTION_NAMES = {"\u6253\u5f00\u540e\u89c6\u955c\u52a0\u70ed", "\u5173\u95ed\u540e\u89c6\u955c\u52a0\u70ed"}
_MIRROR_HEATING_VERIFY_SIGNALS = [
    ("\u540e\u89c6\u955c\u52a0\u70ed\u72b6\u6001", "adb shell vapisend -get Vehicle.Body.Mirrors.IsHeatingOn", 0),
]
_MIRROR_FOLD_INSTRUCTION_NAMES = {"\u6298\u53e0\u540e\u89c6\u955c", "\u5c55\u5f00\u540e\u89c6\u955c"}
_MIRROR_FOLD_VERIFY_SIGNALS = [
    ("\u540e\u89c6\u955c\u72b6\u6001", "adb shell vapisend -get Vehicle.Body.Mirrors.FoldStatus", 0),
]
_STEERING_WHEEL_HEATING_INSTRUCTION_NAMES = {"打开方向盘加热", "关闭方向盘加热"}
_STEERING_WHEEL_HEATING_VERIFY_SIGNALS = [
    ("方向盘加热状态", "adb shell vapisend -get Vehicle.Chassis.SteeringWheel.HeatingLevel", 0),
]
_STEERING_WHEEL_LEVEL2_INSTRUCTION_NAMES = {"\u65b9\u5411\u76d8\u52a0\u70ed\u8c03\u8282\u5230\u0032\u6863"}
_STEERING_WHEEL_LEVEL2_VERIFY_SIGNALS = [
    ("\u540e\u89c6\u955c\u52a0\u70ed\u72b6\u6001", "adb shell vapisend -get Vehicle.Body.Mirrors.IsHeatingOn", 0),
    ("\u65b9\u5411\u76d8\u52a0\u70ed\u6321\u4f4d", "adb shell vapisend -get Vehicle.Chassis.SteeringWheel.HeatingLevel", 0),
]
_READING_LIGHT_INSTRUCTION_NAMES = {
    f"{action}{position}阅读灯"
    for action in ("打开", "关闭")
    for position in ("全车", "", "主驾", "副驾", "左后", "右后")
}
_READING_LIGHT_VERIFY_SIGNALS = [
    ("左前阅读状态", "adb shell vapisend -get Vehicle.Cabin.Light.Spotlight.Row1.DriverSide.IsLightOn"),
    ("右前阅读状态", "adb shell vapisend -get Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn"),
    ("左后阅读状态", "adb shell vapisend -get Vehicle.Cabin.Light.Spotlight.Row2.DriverSide.IsLightOn"),
    ("右后阅读状态", "adb shell vapisend -get Vehicle.Cabin.Light.Spotlight.Row2.PassengerSide.IsLightOn"),
]
_SEAT_VENTILATION_INSTRUCTION_NAMES = {
    "打开座椅通风", "座椅通风调节到2档", "关闭座椅通风",
    "打开主驾座椅通风", "主驾座椅通风调节到2档", "关闭主驾座椅通风",
    "打开副驾座椅通风", "副驾座椅通风调节到2档", "关闭副驾座椅通风",
}
_SEAT_VENTILATION_VERIFY_SIGNALS = [
    ("主驾座椅通风挡位", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.VentilationLevel"),
    ("副驾座椅通风挡位", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.VentilationLevel"),
]
_PASSENGER_SEAT_HEATING_INSTRUCTION_NAMES = {
    "打开副驾座椅加热", "副驾座椅加热调节到2档", "关闭副驾座椅加热",
}
_PASSENGER_SEAT_HEATING_VERIFY_SIGNALS = [
    ("副驾座椅加热挡位", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.HeatingLevel"),
]
_SEAT_HEATING_INSTRUCTION_NAMES = {
    "打开座椅加热", "座椅加热调节到2档", "关闭座椅加热",
    "打开主驾座椅加热", "主驾座椅加热调节到2档", "关闭主驾座椅加热",
}
_SEAT_HEATING_VERIFY_SIGNALS = [
    ("主驾座椅加热挡位", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.HeatingLevel"),
    ("副驾座椅加热挡位", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.HeatingLevel"),
]
_PASSENGER_SEAT_MASSAGE_INSTRUCTION_NAMES = {"打开副驾座椅按摩", "关闭副驾座椅按摩"}
_PASSENGER_SEAT_MASSAGE_VERIFY_SIGNALS = [
    ("副驾座椅按摩开关状态", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.IsMassageActive"),
]
_DRIVER_SEAT_MASSAGE_INSTRUCTION_NAMES = {"打开主驾座椅按摩", "关闭主驾座椅按摩"}
_DRIVER_SEAT_MASSAGE_VERIFY_SIGNALS = [
    ("主驾按摩开关状态", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.IsMassageActive"),
]
_SEAT_MASSAGE_INSTRUCTION_NAMES = {"打开座椅按摩", "关闭座椅按摩"}
_SEAT_MASSAGE_VERIFY_SIGNALS = [
    ("主驾按摩开关状态", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.IsMassageActive"),
    ("副驾按摩开关状态", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.IsMassageActive"),
]
_PASSENGER_SEAT_POSITION_INSTRUCTION_NAMES = {
    f"{action}副驾{position}位置"
    for action in ("打开", "退出")
    for position in ("常用", "休息", "备用", "其他")
}
_PASSENGER_SEAT_POSITION_VERIFY_SIGNALS = [
    ("副驾上下位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.HeightPercent"),
    ("副驾前后位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.PositionPercent"),
    ("副驾腿托折叠位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.LegSupport.FoldPosition"),
    ("副驾靠背位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.ReclinePercent"),
]
_SEAT_POSITION_INSTRUCTION_NAMES = {
    f"{action}{seat}{position}位置"
    for action in ("打开", "退出")
    for seat in ("", "主驾")
    for position in ("进出", "驾驶", "休息", "备用", "其他")
}
_SEAT_POSITION_VERIFY_SIGNALS = [
    ("主驾前后位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.PositionPercent"),
    ("主驾上下位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.HeightPercent"),
    ("主驾腿托折叠位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.LegSupport.FoldPosition"),
    ("副驾靠背位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.ReclinePercent"),
]
_TRUNK_INSTRUCTION_NAMES = {"打开后备箱", "关闭后备箱"}
_TRUNK_VERIFY_SIGNALS = [
    ("尾门开度", "adb shell vapisend -get Vehicle.Body.Trunk.Rear.Position", 0),
]
_CHARGING_PORT_INSTRUCTION_NAMES = {"\u6253\u5f00\u5145\u7535\u5c0f\u95e8", "\u5173\u95ed\u5145\u7535\u5c0f\u95e8"}
_CHARGING_PORT_VERIFY_SIGNALS = [
    ("\u5145\u7535\u5c0f\u95e8\u72b6\u6001", "adb shell vapisend -get Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.Status", 0),
]
def _instructions_for_platform(vehicle_platform):
    platform = str(vehicle_platform or "8295").strip()
    if platform == "8797":
        supported = {
            "\u4f60\u597d\u667a\u5df1",
            "\u6253\u5f00\u7231\u5947\u827a",
            "\u5173\u95ed\u7231\u5947\u827a",
            "\u6253\u5f00\u54d4\u54e9\u54d4\u54e9",
            "\u5173\u95ed\u54d4\u54e9\u54d4\u54e9",
            "\u6253\u5f00\u4e0a\u89c2\u65b0\u95fb",
            "\u5173\u95ed\u4e0a\u89c2\u65b0\u95fb",
            "\u6253\u5f00\u4e00\u8def\u5237",
            "\u5173\u95ed\u4e00\u8def\u5237",
            "\u6253\u5f00 QQ \u97f3\u4e50",
            "\u5173\u95ed QQ \u97f3\u4e50",
            "\u6253\u5f00\u7f51\u6613\u4e91\u97f3\u4e50",
            "\u5173\u95ed\u7f51\u6613\u4e91\u97f3\u4e50",
            "\u6253\u5f00\u84dd\u7259\u97f3\u4e50",
            "\u5173\u95ed\u84dd\u7259\u97f3\u4e50",
        }
        supported |= (
            _WINDOW_INSTRUCTION_NAMES
            | _SUSPENSION_INSTRUCTION_NAMES
            | _AC_POWER_INSTRUCTION_NAMES
            | _AC_AUTO_MODE_INSTRUCTION_NAMES
            | _AC_COMPRESSOR_INSTRUCTION_NAMES
            | _AC_TEMPERATURE_INSTRUCTION_NAMES
            | _AC_SYNC_INSTRUCTION_NAMES
            | _AC_FAN_INSTRUCTION_NAMES
            | _FRONT_SHADE_INSTRUCTION_NAMES
            | _REAR_SHADE_INSTRUCTION_NAMES
            | _MIRROR_HEATING_INSTRUCTION_NAMES
            | _MIRROR_FOLD_INSTRUCTION_NAMES
            | _STEERING_WHEEL_LEVEL2_INSTRUCTION_NAMES
            | _STEERING_WHEEL_HEATING_INSTRUCTION_NAMES
            | _SEAT_POSITION_INSTRUCTION_NAMES
            | _PASSENGER_SEAT_POSITION_INSTRUCTION_NAMES
            | _SEAT_MASSAGE_INSTRUCTION_NAMES
            | _DRIVER_SEAT_MASSAGE_INSTRUCTION_NAMES
            | _PASSENGER_SEAT_MASSAGE_INSTRUCTION_NAMES
            | _SEAT_HEATING_INSTRUCTION_NAMES
            | _PASSENGER_SEAT_HEATING_INSTRUCTION_NAMES
            | _SEAT_VENTILATION_INSTRUCTION_NAMES
            | _READING_LIGHT_INSTRUCTION_NAMES
            | _TRUNK_INSTRUCTION_NAMES
            | _CHARGING_PORT_INSTRUCTION_NAMES
        )
        platform_instructions = {
            name: config
            for name, config in VOICE_INSTRUCTIONS.items()
            if name in supported
        }
        for _suspension_name in _SUSPENSION_INSTRUCTION_NAMES:
            if _suspension_name in platform_instructions:
                platform_instructions[_suspension_name] = dict(
                    platform_instructions[_suspension_name]
                )
                platform_instructions[_suspension_name]["verify_signals"] = list(
                    _SUSPENSION_VERIFY_SIGNALS
                )
        for _ac_auto_mode_name in _AC_AUTO_MODE_INSTRUCTION_NAMES:
            if _ac_auto_mode_name in platform_instructions:
                platform_instructions[_ac_auto_mode_name] = dict(
                    platform_instructions[_ac_auto_mode_name]
                )
                platform_instructions[_ac_auto_mode_name]["verify_signals"] = list(
                    _AC_AUTO_MODE_VERIFY_SIGNALS
                )
        for _ac_power_name in _AC_POWER_INSTRUCTION_NAMES:
            if _ac_power_name in platform_instructions:
                platform_instructions[_ac_power_name] = dict(
                    platform_instructions[_ac_power_name]
                )
                platform_instructions[_ac_power_name]["verify_signals"] = list(
                    _AC_POWER_VERIFY_SIGNALS
                )
        for _ac_compressor_name in _AC_COMPRESSOR_INSTRUCTION_NAMES:
            if _ac_compressor_name in platform_instructions:
                platform_instructions[_ac_compressor_name] = dict(
                    platform_instructions[_ac_compressor_name]
                )
                platform_instructions[_ac_compressor_name]["verify_signals"] = list(
                    _AC_COMPRESSOR_VERIFY_SIGNALS
                )
        for _ac_temperature_name in _AC_TEMPERATURE_INSTRUCTION_NAMES:
            if _ac_temperature_name in platform_instructions:
                platform_instructions[_ac_temperature_name] = dict(
                    platform_instructions[_ac_temperature_name]
                )
                platform_instructions[_ac_temperature_name]["verify_signals"] = list(
                    _AC_TEMPERATURE_VERIFY_SIGNALS
                )
        for _ac_sync_name in _AC_SYNC_INSTRUCTION_NAMES:
            if _ac_sync_name in platform_instructions:
                platform_instructions[_ac_sync_name] = dict(
                    platform_instructions[_ac_sync_name]
                )
                platform_instructions[_ac_sync_name]["verify_signals"] = list(
                    _AC_SYNC_VERIFY_SIGNALS
                )
        for _ac_fan_name in _AC_FAN_INSTRUCTION_NAMES:
            if _ac_fan_name in platform_instructions:
                platform_instructions[_ac_fan_name] = dict(
                    platform_instructions[_ac_fan_name]
                )
                platform_instructions[_ac_fan_name]["verify_signals"] = list(
                    _AC_FAN_VERIFY_SIGNALS
                )
        for _front_shade_name in _FRONT_SHADE_INSTRUCTION_NAMES:
            if _front_shade_name in platform_instructions:
                platform_instructions[_front_shade_name] = dict(
                    platform_instructions[_front_shade_name]
                )
                platform_instructions[_front_shade_name]["verify_signals"] = list(
                    _FRONT_SHADE_VERIFY_SIGNALS
                )
        for _rear_shade_name in _REAR_SHADE_INSTRUCTION_NAMES:
            if _rear_shade_name in platform_instructions:
                platform_instructions[_rear_shade_name] = dict(
                    platform_instructions[_rear_shade_name]
                )
                platform_instructions[_rear_shade_name]["verify_signals"] = list(
                    _REAR_SHADE_VERIFY_SIGNALS
                )
        for _mirror_heating_name in _MIRROR_HEATING_INSTRUCTION_NAMES:
            if _mirror_heating_name in platform_instructions:
                platform_instructions[_mirror_heating_name] = dict(
                    platform_instructions[_mirror_heating_name]
                )
                platform_instructions[_mirror_heating_name]["verify_signals"] = list(
                    _MIRROR_HEATING_VERIFY_SIGNALS
                )
        for _mirror_fold_name in _MIRROR_FOLD_INSTRUCTION_NAMES:
            if _mirror_fold_name in platform_instructions:
                platform_instructions[_mirror_fold_name] = dict(
                    platform_instructions[_mirror_fold_name]
                )
                platform_instructions[_mirror_fold_name]["verify_signals"] = list(
                    _MIRROR_FOLD_VERIFY_SIGNALS
                )
        for _steering_wheel_heating_name in _STEERING_WHEEL_HEATING_INSTRUCTION_NAMES:
            if _steering_wheel_heating_name in platform_instructions:
                platform_instructions[_steering_wheel_heating_name] = dict(
                    platform_instructions[_steering_wheel_heating_name]
                )
                platform_instructions[_steering_wheel_heating_name]["verify_signals"] = list(
                    _STEERING_WHEEL_HEATING_VERIFY_SIGNALS
                )
        for _steering_wheel_name in _STEERING_WHEEL_LEVEL2_INSTRUCTION_NAMES:
            if _steering_wheel_name in platform_instructions:
                platform_instructions[_steering_wheel_name] = dict(
                    platform_instructions[_steering_wheel_name]
                )
                platform_instructions[_steering_wheel_name]["verify_signals"] = list(
                    _STEERING_WHEEL_LEVEL2_VERIFY_SIGNALS
                )
        for _reading_light_name in _READING_LIGHT_INSTRUCTION_NAMES:
            if _reading_light_name in platform_instructions:
                platform_instructions[_reading_light_name] = dict(
                    platform_instructions[_reading_light_name]
                )
                platform_instructions[_reading_light_name]["verify_signals"] = list(
                    _READING_LIGHT_VERIFY_SIGNALS
                )
        for _seat_ventilation_name in _SEAT_VENTILATION_INSTRUCTION_NAMES:
            if _seat_ventilation_name in platform_instructions:
                platform_instructions[_seat_ventilation_name] = dict(
                    platform_instructions[_seat_ventilation_name]
                )
                platform_instructions[_seat_ventilation_name]["verify_signals"] = list(
                    _SEAT_VENTILATION_VERIFY_SIGNALS
                )
        for _passenger_seat_heating_name in _PASSENGER_SEAT_HEATING_INSTRUCTION_NAMES:
            if _passenger_seat_heating_name in platform_instructions:
                platform_instructions[_passenger_seat_heating_name] = dict(
                    platform_instructions[_passenger_seat_heating_name]
                )
                platform_instructions[_passenger_seat_heating_name]["verify_signals"] = list(
                    _PASSENGER_SEAT_HEATING_VERIFY_SIGNALS
                )
        for _seat_heating_name in _SEAT_HEATING_INSTRUCTION_NAMES:
            if _seat_heating_name in platform_instructions:
                platform_instructions[_seat_heating_name] = dict(
                    platform_instructions[_seat_heating_name]
                )
                platform_instructions[_seat_heating_name]["verify_signals"] = list(
                    _SEAT_HEATING_VERIFY_SIGNALS
                )
        for _passenger_seat_massage_name in _PASSENGER_SEAT_MASSAGE_INSTRUCTION_NAMES:
            if _passenger_seat_massage_name in platform_instructions:
                platform_instructions[_passenger_seat_massage_name] = dict(
                    platform_instructions[_passenger_seat_massage_name]
                )
                platform_instructions[_passenger_seat_massage_name]["verify_signals"] = list(
                    _PASSENGER_SEAT_MASSAGE_VERIFY_SIGNALS
                )
        for _driver_seat_massage_name in _DRIVER_SEAT_MASSAGE_INSTRUCTION_NAMES:
            if _driver_seat_massage_name in platform_instructions:
                platform_instructions[_driver_seat_massage_name] = dict(
                    platform_instructions[_driver_seat_massage_name]
                )
                platform_instructions[_driver_seat_massage_name]["verify_signals"] = list(
                    _DRIVER_SEAT_MASSAGE_VERIFY_SIGNALS
                )
        for _seat_massage_name in _SEAT_MASSAGE_INSTRUCTION_NAMES:
            if _seat_massage_name in platform_instructions:
                platform_instructions[_seat_massage_name] = dict(
                    platform_instructions[_seat_massage_name]
                )
                platform_instructions[_seat_massage_name]["verify_signals"] = list(
                    _SEAT_MASSAGE_VERIFY_SIGNALS
                )
        for _passenger_seat_position_name in _PASSENGER_SEAT_POSITION_INSTRUCTION_NAMES:
            if _passenger_seat_position_name in platform_instructions:
                platform_instructions[_passenger_seat_position_name] = dict(
                    platform_instructions[_passenger_seat_position_name]
                )
                platform_instructions[_passenger_seat_position_name]["verify_signals"] = list(
                    _PASSENGER_SEAT_POSITION_VERIFY_SIGNALS
                )
        for _seat_position_name in _SEAT_POSITION_INSTRUCTION_NAMES:
            if _seat_position_name in platform_instructions:
                platform_instructions[_seat_position_name] = dict(
                    platform_instructions[_seat_position_name]
                )
                platform_instructions[_seat_position_name]["verify_signals"] = list(
                    _SEAT_POSITION_VERIFY_SIGNALS
                )
        for _trunk_name in _TRUNK_INSTRUCTION_NAMES:
            if _trunk_name in platform_instructions:
                platform_instructions[_trunk_name] = dict(
                    platform_instructions[_trunk_name]
                )
                platform_instructions[_trunk_name]["verify_signals"] = list(
                    _TRUNK_VERIFY_SIGNALS
                )
        for _charging_port_name in _CHARGING_PORT_INSTRUCTION_NAMES:
            if _charging_port_name in platform_instructions:
                platform_instructions[_charging_port_name] = dict(
                    platform_instructions[_charging_port_name]
                )
                platform_instructions[_charging_port_name]["verify_signals"] = list(
                    _CHARGING_PORT_VERIFY_SIGNALS
                )
        return platform_instructions
    return VOICE_INSTRUCTIONS


def get_instruction_names(vehicle_platform="8295"):
    """Return voice instructions configured for the selected platform."""
    return list(_instructions_for_platform(vehicle_platform))


def get_instruction_config(name, vehicle_platform="8295"):
    return _instructions_for_platform(vehicle_platform).get(name)


# ==================== 日志分析工具 ====================
def parse_logs_for_baseline(log_content, instruction_name=None):
    import re
    import json

    result = {
        "recognition": "",
        "response": "",
        "response_time_ms": 0,
        "intent": "",
        "voice_zone": ""
    }

    lines = log_content.strip().split("\n")

    wake_word = ""
    asr_result = ""
    tts_responses = []

    # 检查是否是唤醒指令
    is_wakeup = False
    if instruction_name and ("智己" in instruction_name or "IM" in instruction_name):
        is_wakeup = True
    # 还可以检查唤醒词
    if not is_wakeup:
        for line in lines:
            if "OrchASR4BMSp: word = " in line:
                word_part = line.split("OrchASR4BMSp: word = ")[-1].strip()
                if "智己" in word_part or "IM" in word_part:
                    is_wakeup = True
                    break

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 0. 优先提取响应时间 totalCost（跟 JSON 解析解耦，参考备份逻辑）
        if "totalCost" in line:
            match = re.search(r'"totalCost":\s*(\d+)', line)
            if match:
                result["response_time_ms"] = int(match.group(1))

        # 1. 本地识别结果 - voice_handleASRKeyWord（关键词/唤醒词，参考备份逻辑）
        if "voice_handleASRKeyWord" in line:
            keyword_match = re.search(r'keyword:([^,]+)', line)
            if keyword_match:
                wake_word = keyword_match.group(1).strip()

        # 2. 远程 ASR 识别结果 - remote dialog result（finish=1 的，参考备份逻辑）
        if "remote dialog result" in line and ('finish":1' in line or 'finish=1' in line):
            try:
                json_str = line[line.find('{'):]
                brace_count = 0
                for i, char in enumerate(json_str):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = json_str[:i+1]
                            break
                data = json.loads(json_str)
                if "results" in data and "asr_out" in data["results"]:
                    asr_text = data["results"]["asr_out"].get("result", "")
                    if asr_text:
                        asr_result = asr_text
                
                # 再提取 NLG 响应内容（LLM 指令的响应在这里，如 written_text/spoken_text）
                try:
                    nlg = data.get("results", {}).get("xy_out", {}).get("response", {}).get("nlg_result", {})
                    # spoken_text 优先（车机会说出来的），没有就用 written_text（屏幕显示的）
                    spoken_list = nlg.get("spoken_text", []) or []
                    written_list = nlg.get("written_text", []) or []
                    # 收集所有有内容的文本
                    nlg_texts = []
                    for t in spoken_list:
                        if t and t.strip():
                            nlg_texts.append(t.strip())
                    for t in written_list:
                        if t and t.strip() and t.strip() not in nlg_texts:
                            nlg_texts.append(t.strip())
                    if nlg_texts:
                        tts_responses.extend(nlg_texts)
                except:
                    pass
            except:
                pass

        # 3. 车机响应 - play tts
        if "play tts:" in line:
            try:
                json_str = line.split("play tts:")[-1].strip()
                start_idx = json_str.find("{")
                brace_count = 0
                if start_idx >= 0:
                    for i in range(start_idx, len(json_str)):
                        if json_str[i] == "{":
                            brace_count += 1
                        elif json_str[i] == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                json_str = json_str[start_idx:i+1]
                                break
                data = json.loads(json_str)
                content = data.get("content", "")
                if content:
                    # 去掉 HTML 标签，还原纯文本（如 <emo>好啦</emo> → 好啦）
                    clean_content = re.sub(r'<[^>]*>', '', content).strip()
                    # 对于唤醒指令，优先选择简短的响应（"来啦"、"我在"等）
                    if is_wakeup:
                        if len(clean_content) <= 10 and ("来" in clean_content or "在" in clean_content or "好" in clean_content):
                            tts_responses.insert(0, clean_content)
                        else:
                            tts_responses.append(clean_content)
                    else:
                        # 对于控制指令，跳过简短的唤醒响应
                        if len(clean_content) <= 10 and ("来" in clean_content or "在" in clean_content):
                            continue
                        tts_responses.append(clean_content)

                voice_zone = data.get("voiceZone", "")
                if voice_zone and not result["voice_zone"]:
                    zone_map = {"0": "主驾", "1": "主驾", "2": "副驾", "3": "左后", "4": "右后"}
                    result["voice_zone"] = zone_map.get(str(voice_zone), str(voice_zone))
            except:
                pass

    # 最终识别结果：远程ASR优先，没有就用本地关键词（参考备份逻辑）
    result["recognition"] = asr_result if asr_result else wake_word

    # 选择最合适的响应：拼接所有不重复的内容
    if tts_responses:
        # 去重后拼接（如 "好的，" + "主驾空调温度调至最低。" → "好的，主驾空调温度调至最低。"）
        seen = set()
        combined = []
        for r in tts_responses:
            if r and r not in seen:
                seen.add(r)
                combined.append(r)
        result["response"] = "".join(combined)

    return result


def is_wakeup_instruction(instruction_name):
    """判断是否是唤醒指令"""
    return ("智己" in instruction_name or "IM" in instruction_name or "哈喽" in instruction_name or "你好" in instruction_name or "Hi" in instruction_name or "Hello" in instruction_name)


def check_wakeup_response(response):
    """检查唤醒指令的TTS响应是否是正反馈"""
    positive_keywords = ["来", "在", "好", "嗯", "Hi", "Hello", "哈喽", "我在", "我来", "来了"]
    response_lower = response.lower()
    
    for keyword in positive_keywords:
        if keyword.lower() in response_lower:
            return True
    
    return False


def check_is_negative_response(response):
    """检查响应是否为负反馈（不在负反馈列表里的就是正反馈）"""
    negative_keywords = [
        "抱歉", "无法", "不支持", "不行", "错误", "失败", "请重试",
        "网络", "听不懂", "没有", "识别不了", "暂时不能", "不明白",
    ]
    response_lower = response.lower()
    for keyword in negative_keywords:
        if keyword.lower() in response_lower:
            return True
    return False


def calculate_similarity(str1, str2):
    """计算两个字符串的相似度（基于字符匹配）"""
    if not str1 or not str2:
        return 0
    
    # 如果完全相同，返回100
    if str1 == str2:
        return 100
    
    # 计算最长公共子序列长度
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    lcs_length = dp[m][n]
    
    # 计算相似度：(2 * LCS) / (len1 + len2)
    similarity = (2 * lcs_length) / (m + n) * 100
    return similarity


def compare_test_result(test_result, baseline, instruction_name, actual_signal_values=None, baseline_signal_values=None):
    """对比测试结果与基准
    
    Returns:
        dict: {
            "passed": bool,
            "details": list,
            "asr_match": bool,
            "tts_match": bool,
            "time_match": bool,
            "signal_match": bool
        }
    """
    details = []
    passed = True
    
    is_wakeup = is_wakeup_instruction(instruction_name)
    
    # 1. ASR识别结果对比（唤醒指令严格匹配，其他指令只要识别到就算正反馈）
    asr_match = False
    baseline_asr = baseline.get("recognition", "")
    actual_asr = test_result.get("recognition", "")
    
    if baseline_asr and actual_asr:
        if is_wakeup:
            # 唤醒指令：ASR必须完全一致或关键词匹配
            if actual_asr == baseline_asr or (baseline_asr in actual_asr) or (actual_asr in baseline_asr):
                asr_match = True
                details.append(f"✅ ASR识别匹配: 期望[{baseline_asr}] 实际[{actual_asr}]")
            else:
                asr_match = False
                passed = False
                details.append(f"❌ ASR识别不匹配: 期望[{baseline_asr}] 实际[{actual_asr}]")
        else:
            # 非唤醒指令：ASR识别到内容且不是负反馈就算通过
            if check_is_negative_response(actual_asr):
                asr_match = False
                passed = False
                details.append(f"❌ ASR识别异常(负反馈): [{actual_asr}]")
            else:
                asr_match = True
                details.append(f"✅ ASR识别有效: [{actual_asr}]")
    else:
        details.append(f"⚠️ ASR识别无数据")
        passed = False
    
    # 2. TTS响应对比（不在负反馈列表里的都是正反馈）
    tts_match = False
    actual_tts = test_result.get("response", "")
    
    if actual_tts:
        if check_is_negative_response(actual_tts):
            tts_match = False
            passed = False
            details.append(f"❌ TTS响应异常(负反馈): [{actual_tts}]")
        else:
            tts_match = True
            details.append(f"✅ TTS响应有效: [{actual_tts}]")
    else:
        details.append(f"⚠️ TTS响应无数据")
        passed = False
    
    # 3. 响应时间对比（唤醒指令跳过，其他指令都需要）
    time_match = True
    if not is_wakeup:
        baseline_time = baseline.get("response_time_ms", 0)
        actual_time = test_result.get("response_time_ms", 0)
        if baseline_time > 0 and actual_time > 0:
            time_diff = abs(actual_time - baseline_time)
            if time_diff <= 200:
                time_match = True
                details.append(f"✅ 响应时间匹配: 期望[{baseline_time}ms] 实际[{actual_time}ms] 误差[{time_diff}ms]")
            else:
                time_match = False
                passed = False
                details.append(f"❌ 响应时间不匹配: 期望[{baseline_time}ms] 实际[{actual_time}ms] 误差[{time_diff}ms]")
        else:
            details.append(f"⚠️ 响应时间无数据")
    else:
        details.append(f"ℹ️ 唤醒指令不需要对比响应时间")
    
    # 4. 状态信号对比（只针对控制指令）
    signal_match = True
    if not is_wakeup and baseline_signal_values and actual_signal_values:
        for signal_name in baseline_signal_values:
            if signal_name in actual_signal_values:
                baseline_val = baseline_signal_values[signal_name]
                actual_val = actual_signal_values[signal_name]
                
                # 兼容两种格式：原始值 1 或 dict {'value': 1, 'tolerance': 0}
                if isinstance(baseline_val, dict):
                    base_num = baseline_val.get("value", baseline_val)
                    tolerance = baseline_val.get("tolerance", 0)
                else:
                    base_num = baseline_val
                    tolerance = 0
                
                # 尝试转换成数字对比
                try:
                    base_num = float(base_num)
                    actual_num = float(actual_val)
                    diff = abs(actual_num - base_num)
                    if diff <= tolerance:
                        details.append(f"✅ 信号{signal_name}匹配: 期望[{base_num}] 实际[{actual_num}] 容差[{tolerance}]")
                    else:
                        signal_match = False
                        passed = False
                        details.append(f"❌ 信号{signal_name}不匹配: 期望[{base_num}] 实际[{actual_num}] 误差[{diff}] 容差[{tolerance}]")
                except:
                    # 非数字类型完全对比
                    if str(baseline_val) == str(actual_val):
                        details.append(f"✅ 信号{signal_name}匹配: 期望[{baseline_val}] 实际[{actual_val}]")
                    else:
                        signal_match = False
                        passed = False
                        details.append(f"❌ 信号{signal_name}不匹配: 期望[{baseline_val}] 实际[{actual_val}]")
            else:
                details.append(f"⚠️ 信号{signal_name}无数据")
    
    return {
        "passed": passed,
        "details": details,
        "asr_match": asr_match,
        "tts_match": tts_match,
        "time_match": time_match,
        "signal_match": signal_match
    }

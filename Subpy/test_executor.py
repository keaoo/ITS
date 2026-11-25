import os
import re
import time
import json
import subprocess
import serial
import socket
from datetime import datetime


class TestExecutor:
    FOLD_MIRROR_INSTRUCTION_NAME_8797 = (
        "\u6298\u53e0\u540e\u89c6\u955c"
    )
    UNFOLD_MIRROR_INSTRUCTION_NAME_8797 = (
        "\u5c55\u5f00\u540e\u89c6\u955c"
    )
    FOLDED_MIRROR_STATUS_INSTRUCTION_NAME_8797 = (
        "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001"
    )
    UNFOLDED_MIRROR_STATUS_INSTRUCTION_NAME_8797 = (
        "\u540e\u89c6\u955c\u5c55\u5f00\u72b6\u6001"
    )
    ELECTRIC_STEERING_WHEEL_POSITION_INSTRUCTION_NAME_8797 = (
        "\u7535\u52a8\u65b9\u5411\u76d8\u4f4d\u7f6e"
    )
    ELECTRIC_STEERING_WHEEL_POSITION_READ_COMMAND_8797 = r'''powershell -NoProfile -Command "$r = & adb shell su 0 timeout 3 tcpdump -i br0.17 -nn -s 256 -X -c 1 udp port 37519 2>&1; $m = [regex]::Match(($r -join [Environment]::NewLine),'0x0030:\s+([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})'); if ($m.Success) { 'Tilt(up-down)={0}; Tele(front-back)={1}' -f [Convert]::ToInt32($m.Groups[1].Value,16),[Convert]::ToInt32($m.Groups[2].Value,16) } else { 'Position read failed' }"'''
    ELECTRIC_STEERING_WHEEL_POSITION_READ_COMMAND_8295 = (
        r"""powershell -NoProfile -Command "$r = & adb -host shell 'su -c ''tcpdump -i br0.17 -nn -s 256 -X -c 1 udp port 37519''';$text = $r -join [Environment]::NewLine; $m = [regex]::Match($text,'(?m)^\s*0x0030:\s+([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})'); if ($m.Success) { 'Tilt(up-down)={0}; Tele(front-back)={1}' -f [Convert]::ToInt32($m.Groups[1].Value,16),[Convert]::ToInt32($m.Groups[2].Value,16) } else { 'Position read failed: ' + $text.Trim() }"""
        + '"'
    )
    MIRROR_POSITION_INSTRUCTION_NAME_8295 = "\u540e\u89c6\u955c\u4f4d\u7f6e"
    MIRROR_POSITION_TCPDUMP_COMMAND_8295 = (
        "tcpdump -i br0.17 -nn -s 256 -X -c 1 udp port 35593"
    )
    MIRROR_POSITION_READ_COMMAND_8295 = (
        'adb -host shell su -c "' + MIRROR_POSITION_TCPDUMP_COMMAND_8295 + '"'
    )
    MIRROR_POSITION_FIELDS_8295 = (
        "\u5de6\u4fa7\u540e\u89c6\u955c\u6c34\u5e73\u4f4d\u7f6e",
        "\u5de6\u4fa7\u540e\u89c6\u955c\u5782\u76f4\u4f4d\u7f6e",
        "\u53f3\u4fa7\u540e\u89c6\u955c\u6c34\u5e73\u4f4d\u7f6e",
        "\u53f3\u4fa7\u540e\u89c6\u955c\u5782\u76f4\u4f4d\u7f6e",
    )
    MIRROR_STATUS_INSTRUCTION_NAMES_8797 = {
        "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001",
        "\u540e\u89c6\u955c\u5c55\u5f00\u72b6\u6001",
    }
    STEP_BOARD_STATUS_INSTRUCTION_NAME_8797 = "\u7535\u52a8\u8e0f\u677f\u72b6\u6001"
    STEP_BOARD_STATUS_VALUES_8797 = {
        "RETRCTED": "\u6536\u56de",
        "EXTNDED": "\u4f38\u51fa",
        "RETRCTING": "\u6536\u56de\u4e2d",
        "EXTNDING": "\u4f38\u51fa\u4e2d",
        "UNKNOWN": "\u672a\u77e5",
    }
    STEP_BOARD_RESULT_COMMANDS_8797 = (
        (
            "\u5de6\u4fa7\u8e0f\u677f\u72b6\u6001",
            "adb shell vapisend -get Vehicle.Body.StepBoard.Left.Status",
            "status",
        ),
        (
            "\u5de6\u4fa7\u8e0f\u677f\u4f4d\u7f6e",
            "adb shell vapisend -get Vehicle.Body.StepBoard.Left.PositionPercent",
            "position",
        ),
        (
            "\u53f3\u4fa7\u8e0f\u677f\u72b6\u6001",
            "adb shell vapisend -get Vehicle.Body.StepBoard.Right.Status",
            "status",
        ),
        (
            "\u53f3\u4fa7\u8e0f\u677f\u4f4d\u7f6e",
            "adb shell vapisend -get Vehicle.Body.StepBoard.Right.PositionPercent",
            "position",
        ),
    )
    STEP_BOARD_BASELINE_FIELDS_8797 = tuple(
        label for label, _command, _value_type in STEP_BOARD_RESULT_COMMANDS_8797
    )
    REAR_SHADE_INSTRUCTION_NAMES_8797 = {
        "\u6253\u5f00\u540e\u906e\u9633\u5e18",
        "\u5173\u95ed\u540e\u906e\u9633\u5e18",
    }
    FRONT_SHADE_INSTRUCTION_NAMES_8797 = {
        "\u6253\u5f00\u524d\u906e\u9633\u5e18",
        "\u5173\u95ed\u524d\u906e\u9633\u5e18",
    }
    EXECUTABLE_SHADE_INSTRUCTION_NAMES_8797 = (
        REAR_SHADE_INSTRUCTION_NAMES_8797
        | FRONT_SHADE_INSTRUCTION_NAMES_8797
    )
    DRIVER_SEAT_POSITION_VALUES_8797 = {
        "\u4e3b\u9a7e\u5ea7\u6905\u9a7e\u9a76\u4f4d\u7f6e": "DRIVER",
        "\u4e3b\u9a7e\u5ea7\u6905\u8fdb\u51fa\u4f4d\u7f6e": "EASY_EXIT",
        "\u4e3b\u9a7e\u5ea7\u6905\u5176\u4ed6\u4f4d\u7f6e": "OTHER",
        "\u4e3b\u9a7e\u5ea7\u6905\u5907\u7528\u4f4d\u7f6e": "BACKUP",
        "\u4e3b\u9a7e\u5ea7\u6905\u4f11\u606f\u4f4d\u7f6e": "RESTING",
    }
    DRIVER_SEAT_HEATING_VALUES_8797 = {
        "\u5173\u95ed\u4e3b\u9a7e\u5ea7\u6905\u52a0\u70ed": "0",
        "\u4e3b\u9a7e\u5ea7\u6905\u52a0\u70ed1\u6863": "1",
        "\u4e3b\u9a7e\u5ea7\u6905\u52a0\u70ed2\u6863": "2",
        "\u4e3b\u9a7e\u5ea7\u6905\u52a0\u70ed3\u6863": "3",
    }
    DRIVER_SEAT_VENTILATION_VALUES_8797 = {
        "\u5173\u95ed\u4e3b\u9a7e\u5ea7\u6905\u901a\u98ce": "0",
        "\u4e3b\u9a7e\u5ea7\u6905\u901a\u98ce1\u6863": "1",
        "\u4e3b\u9a7e\u5ea7\u6905\u901a\u98ce2\u6863": "2",
        "\u4e3b\u9a7e\u5ea7\u6905\u901a\u98ce3\u6863": "3",
    }
    DRIVER_SEAT_MASSAGE_VALUES_8797 = {
        "\u6253\u5f00\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469": ("IsMassageActive", "true", "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u72b6\u6001"),
        "\u5173\u95ed\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469": ("IsMassageActive", "false", "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u72b6\u6001"),
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u8f7b\u7f13": ("MassageIntensity", "1", "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6\u72b6\u6001"),
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u6807\u51c6": ("MassageIntensity", "2", "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6\u72b6\u6001"),
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u5f3a\u529b": ("MassageIntensity", "3", "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6\u72b6\u6001"),
    }
    DRIVER_SEAT_MASSAGE_AREA_VALUES_8797 = {
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\uff08\u4e0a\u8170\u90e8\uff09": "1",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170\uff08\u4e0b\u8170\u90e8\uff09": "2",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u4e0b\u534a\u8eab": "3",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9+\u8170(\u5168\u80cc\uff09": "4",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9+\u4e0b\u534a\u8eab": "5",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170+\u4e0b\u534a\u8eab": "6",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9+\u8170+\u4e0b\u534a\u8eab": "7",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u5927\u817f": "8",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u5750\u57ab": "9",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80cc\u90e8\u8212\u7f13": "10",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80cc\u90e8\u8212\u7f13+\u5927\u817f+\u5750\u57ab": "11",
    }
    DRIVER_SEAT_MASSAGE_MODE_VALUES_8797 = {
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8109\u51b2/\u5168\u8eab\u8212\u5c55": "1",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u6ce2\u6d6a/\u6572\u63c9\u8212\u538b": "2",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u732b\u6b65/\u63a8\u62ff\u5524\u9192": "3",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u5355\u6392/\u63c9\u6413\u6d3b\u8840": "4",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8212\u7f13/\u8170\u90e8\u53e4\u6cd5": "5",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u789f\u5f62": "6",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8170\u90e8": "7",
        "\u4e3b\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u86c7\u5f62": "8",
    }
    PASSENGER_SEAT_POSITION_VALUES_8797 = {
        "\u526f\u9a7e\u5ea7\u6905\u8fdb\u51fa\u4f4d\u7f6e": ("EASY_EXIT", 15),
        "\u526f\u9a7e\u5ea7\u6905\u5e38\u7528\u4f4d\u7f6e": ("COMMON", 15),
        "\u526f\u9a7e\u5ea7\u6905\u4f11\u606f\u4f4d\u7f6e": ("RESTING", 15),
        "\u526f\u9a7e\u5ea7\u6905\u5907\u7528\u4f4d\u7f6e": ("BACKUP", 15),
        "\u526f\u9a7e\u5ea7\u6905\u5176\u4ed6\u4f4d\u7f6e": ("OTHER", 15),
    }
    SEAT_SCENE_INSTRUCTION_NAMES_8797 = (
        "\u9000\u51fa\u4e3b\u9a7e\u8d35\u5983\u6905",
        "\u5f00\u542f\u4e3b\u9a7e\u8d35\u5983\u6905",
        "\u5f00\u542f\u526f\u9a7e\u8d35\u5983\u6905",
        "\u9000\u51fa\u526f\u9a7e\u8d35\u5983\u6905",
        "\u5f00\u542f\u526f\u9a7e\u96f6\u91cd\u529b",
        "\u5173\u95ed\u526f\u9a7e\u96f6\u91cd\u529b",
        "\u5f00\u542f\u53f3\u540e\u96f6\u91cd\u529b",
        "\u9000\u51fa\u53f3\u540e\u96f6\u91cd\u529b",
        "\u5f00\u542f\u5de6\u540e\u96f6\u91cd\u529b",
        "\u9000\u51fa\u5de6\u540e\u96f6\u91cd\u529b",
        "\u56db\u4eba\u8212\u4eab\u6a21\u5f0f\u5f00\u542f",
        "\u56db\u4eba\u8212\u4eab\u6a21\u5f0f\u5173\u95ed",
        "\u540e\u5907\u7bb1\u6536\u7eb3\u6a21\u5f0f\u5f00\u542f",
        "\u540e\u5907\u7bb1\u6536\u7eb3\u6a21\u5f0f\u5173\u95ed",
    )
    SEAT_SCENE_COMMANDS_8797 = {
        "\u9000\u51fa\u4e3b\u9a7e\u8d35\u5983\u6905": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row1.DriverSide.PositionMemory.Restore DRIVER; sleep 1; '
            'vapisend -set Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore DEFAULT"',
            20,
        ),
        "\u5f00\u542f\u4e3b\u9a7e\u8d35\u5983\u6905": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore FLAT && '
            'vapisend -set Vehicle.Cabin.Seat.Row1.DriverSide.PositionMemory.Restore FLAT"',
            20,
        ),
        "\u5f00\u542f\u526f\u9a7e\u8d35\u5983\u6905": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore FLAT && '
            'vapisend -set Vehicle.Cabin.Seat.Row1.PassengerSide.PositionMemory.Restore FLAT"',
            20,
        ),
        "\u9000\u51fa\u526f\u9a7e\u8d35\u5983\u6905": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row1.PassengerSide.PositionMemory.Restore COMMON; sleep 1; '
            'vapisend -set Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore DEFAULT"',
            20,
        ),
        "\u5f00\u542f\u526f\u9a7e\u96f6\u91cd\u529b": (
            "adb shell vapisend -set Vehicle.Cabin.Seat.Row1.PassengerSide.PositionMemory.Restore 0G",
            38,
        ),
        "\u5173\u95ed\u526f\u9a7e\u96f6\u91cd\u529b": (
            "adb shell vapisend -set Vehicle.Cabin.Seat.Row1.PassengerSide.PositionMemory.Restore COMMON",
            38,
        ),
        "\u5f00\u542f\u53f3\u540e\u96f6\u91cd\u529b": (
            "adb shell vapisend -set Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore 0G",
            38,
        ),
        "\u9000\u51fa\u53f3\u540e\u96f6\u91cd\u529b": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore DEFAULT && '
            'vapisend -set Vehicle.Cabin.Seat.Row1.PassengerSide.PositionMemory.Restore COMMON"',
            38,
        ),
        "\u5f00\u542f\u5de6\u540e\u96f6\u91cd\u529b": (
            "adb shell vapisend -set Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore 0G",
            38,
        ),
        "\u9000\u51fa\u5de6\u540e\u96f6\u91cd\u529b": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore DEFAULT && '
            'vapisend -set Vehicle.Cabin.Seat.Row1.DriverSide.PositionMemory.Restore DRIVER"',
            38,
        ),
        "\u56db\u4eba\u8212\u4eab\u6a21\u5f0f\u5f00\u542f": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore LARGE_FOUR && '
            'vapisend -set Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore LARGE_FOUR"',
            30,
        ),
        "\u56db\u4eba\u8212\u4eab\u6a21\u5f0f\u5173\u95ed": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore DEFAULT && '
            'vapisend -set Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore DEFAULT"',
            30,
        ),
        "\u540e\u5907\u7bb1\u6536\u7eb3\u6a21\u5f0f\u5f00\u542f": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row3.DriverSide.PositionMemory.Restore FOLD_ENTRY && '
            'vapisend -set Vehicle.Cabin.Seat.Row3.PassengerSide.PositionMemory.Restore FOLD_ENTRY"',
            30,
        ),
        "\u540e\u5907\u7bb1\u6536\u7eb3\u6a21\u5f0f\u5173\u95ed": (
            'adb shell "vapisend -set Vehicle.Cabin.Seat.Row3.DriverSide.PositionMemory.Restore FOLD_EXIT && '
            'vapisend -set Vehicle.Cabin.Seat.Row3.PassengerSide.PositionMemory.Restore FOLD_EXIT"',
            30,
        ),
    }
    SEAT_SCENE_COMMANDS_8797.update({
        "\u4e3b\u9a7e\u5ea7\u6905\u8d35\u5983\u6905\u4f4d\u7f6e": SEAT_SCENE_COMMANDS_8797[
            "\u5f00\u542f\u4e3b\u9a7e\u8d35\u5983\u6905"
        ],
        "\u526f\u9a7e\u5ea7\u6905\u8d35\u5983\u6905\u4f4d\u7f6e": SEAT_SCENE_COMMANDS_8797[
            "\u5f00\u542f\u526f\u9a7e\u8d35\u5983\u6905"
        ],
        "\u526f\u9a7e\u5ea7\u6905\u96f6\u91cd\u529b\u4f4d\u7f6e": SEAT_SCENE_COMMANDS_8797[
            "\u5f00\u542f\u526f\u9a7e\u96f6\u91cd\u529b"
        ],
    })
    DRIVER_SEAT_POSITION_RESULT_COMMANDS_8797 = (
        ("\u4e3b\u9a7e\u5ea7\u6905\u9760\u80cc\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.ReclinePercent"),
        ("\u4e3b\u9a7e\u5ea7\u6905\u524d\u540e\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.PositionPercent"),
        ("\u4e3b\u9a7e\u5ea7\u6905\u4e0a\u4e0b\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.HeightPercent"),
        ("\u4e3b\u9a7e\u5ea7\u6905\u817f\u6258\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.LegSupport.FoldPosition"),
    )
    PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 = (
        ("\u526f\u9a7e\u5ea7\u6905\u9760\u80cc\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.ReclinePercent"),
        ("\u526f\u9a7e\u5ea7\u6905\u524d\u540e\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.PositionPercent"),
        ("\u526f\u9a7e\u5ea7\u6905\u4e0a\u4e0b\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.HeightPercent"),
        ("\u526f\u9a7e\u5ea7\u6905\u817f\u6258\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.LegSupport.FoldPosition"),
    )
    LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797 = (
        ("\u5de6\u540e\u5ea7\u6905\u9760\u80cc\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.ReclinePercent"),
        ("\u5de6\u540e\u5ea7\u6905\u524d\u540e\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.HorizontalPosition"),
        ("\u5de6\u540e\u5ea7\u6905\u503e\u89d2", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.TiltPercent"),
        ("\u5de6\u540e\u5ea7\u6905\u817f\u6258\u4f38\u7f29", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.LegSupport.Position"),
    )
    RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797 = (
        ("\u53f3\u540e\u5ea7\u6905\u9760\u80cc\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.ReclinePercent"),
        ("\u53f3\u540e\u5ea7\u6905\u524d\u540e\u4f4d\u7f6e", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.HorizontalPosition"),
        ("\u53f3\u540e\u5ea7\u6905\u503e\u89d2", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.TiltPercent"),
        ("\u53f3\u540e\u5ea7\u6905\u817f\u6258\u4f38\u7f29", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.LegSupport.Position"),
    )
    SEAT_SCENE_RESULT_COMMANDS_8797 = {
        "\u9000\u51fa\u4e3b\u9a7e\u8d35\u5983\u6905": DRIVER_SEAT_POSITION_RESULT_COMMANDS_8797 + LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u5f00\u542f\u4e3b\u9a7e\u8d35\u5983\u6905": DRIVER_SEAT_POSITION_RESULT_COMMANDS_8797 + LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u4e3b\u9a7e\u5ea7\u6905\u8d35\u5983\u6905\u4f4d\u7f6e": DRIVER_SEAT_POSITION_RESULT_COMMANDS_8797 + LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u5f00\u542f\u526f\u9a7e\u8d35\u5983\u6905": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u9000\u51fa\u526f\u9a7e\u8d35\u5983\u6905": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u526f\u9a7e\u5ea7\u6905\u8d35\u5983\u6905\u4f4d\u7f6e": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u5f00\u542f\u5de6\u540e\u96f6\u91cd\u529b": DRIVER_SEAT_POSITION_RESULT_COMMANDS_8797 + LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u9000\u51fa\u5de6\u540e\u96f6\u91cd\u529b": DRIVER_SEAT_POSITION_RESULT_COMMANDS_8797 + LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u5f00\u542f\u53f3\u540e\u96f6\u91cd\u529b": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u9000\u51fa\u53f3\u540e\u96f6\u91cd\u529b": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u5f00\u542f\u526f\u9a7e\u96f6\u91cd\u529b": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u5173\u95ed\u526f\u9a7e\u96f6\u91cd\u529b": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u526f\u9a7e\u5ea7\u6905\u96f6\u91cd\u529b\u4f4d\u7f6e": PASSENGER_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u56db\u4eba\u8212\u4eab\u6a21\u5f0f\u5f00\u542f": LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
        "\u56db\u4eba\u8212\u4eab\u6a21\u5f0f\u5173\u95ed": LEFT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797 + RIGHT_REAR_SEAT_POSITION_RESULT_COMMANDS_8797,
    }
    PASSENGER_SEAT_HEATING_VALUES_8797 = {
        "\u5173\u95ed\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed": "0",
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed1\u6863": "1",
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed2\u6863": "2",
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed3\u6863": "3",
    }
    PASSENGER_SEAT_HEATING_OFF_NAME_8797 = (
        "\u5173\u95ed\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed"
    )
    PASSENGER_SEAT_HEATING_LEVEL_NAMES_8797 = {
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed1\u6863": "1",
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed2\u6863": "2",
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed3\u6863": "3",
    }
    PASSENGER_SEAT_HEATING_LEVEL_1_NAME_8797 = (
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed1\u6863"
    )
    PASSENGER_SEAT_HEATING_LEVEL_2_NAME_8797 = (
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed2\u6863"
    )
    PASSENGER_SEAT_HEATING_LEVEL_3_NAME_8797 = (
        "\u526f\u9a7e\u5ea7\u6905\u52a0\u70ed3\u6863"
    )
    PASSENGER_SEAT_VENTILATION_VALUES_8797 = {
        "\u5173\u95ed\u526f\u9a7e\u5ea7\u6905\u901a\u98ce": "0",
        "\u526f\u9a7e\u5ea7\u6905\u901a\u98ce1\u6863": "1",
        "\u526f\u9a7e\u5ea7\u6905\u901a\u98ce2\u6863": "2",
        "\u526f\u9a7e\u5ea7\u6905\u901a\u98ce3\u6863": "3",
    }
    PASSENGER_SEAT_VENTILATION_OFF_NAME_8797 = (
        "\u5173\u95ed\u526f\u9a7e\u5ea7\u6905\u901a\u98ce"
    )
    PASSENGER_SEAT_VENTILATION_LEVEL_1_NAME_8797 = (
        "\u526f\u9a7e\u5ea7\u6905\u901a\u98ce1\u6863"
    )
    PASSENGER_SEAT_VENTILATION_LEVEL_2_NAME_8797 = (
        "\u526f\u9a7e\u5ea7\u6905\u901a\u98ce2\u6863"
    )
    PASSENGER_SEAT_VENTILATION_LEVEL_3_NAME_8797 = (
        "\u526f\u9a7e\u5ea7\u6905\u901a\u98ce3\u6863"
    )
    PASSENGER_SEAT_MASSAGE_SWITCH_VALUES_8797 = {
        "\u6253\u5f00\u526f\u9a7e\u5ea7\u6905\u6309\u6469": ("IsMassageActive", "true", "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u5f00\u5173\u72b6\u6001"),
        "\u5173\u95ed\u526f\u9a7e\u5ea7\u6905\u6309\u6469": ("IsMassageActive", "false", "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u5f00\u5173\u72b6\u6001"),
    }
    PASSENGER_SEAT_MASSAGE_INTENSITY_VALUES_8797 = {
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u8f7b\u7f13": "1",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u6807\u51c6": "2",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u5f3a\u529b": "3",
    }
    PASSENGER_SEAT_MASSAGE_AREA_VALUES_8797 = {
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\uff08\u4e0a\u8170\u90e8\uff09": "1",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170\uff08\u4e0b\u8170\u90e8\uff09": "2",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u4e0b\u534a\u8eab": "3",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9+\u8170(\u5168\u80cc\uff09": "4",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9+\u4e0b\u534a\u8eab": "5",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170+\u4e0b\u534a\u8eab": "6",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9+\u8170+\u4e0b\u534a\u8eab": "7",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u5927\u817f": "8",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u5750\u57ab": "9",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80cc\u90e8\u8212\u7f13": "10",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80cc\u90e8\u8212\u7f13+\u5927\u817f+\u5750\u57ab": "11",
    }
    PASSENGER_SEAT_MASSAGE_MODE_VALUES_8797 = {
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8109\u51b2": "1",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u6ce2\u6d6a": "2",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u732b\u6b65": "3",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u5355\u6392": "4",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8212\u7f13": "5",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u789f\u5f62": "6",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8170\u90e8": "7",
        "\u526f\u9a7e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u86c7\u5f62": "8",
    }
    LEFT_REAR_SEAT_CLIMATE_VALUES_8797 = {
        "\u5173\u95ed\u5de6\u540e\u5ea7\u6905\u901a\u98ce": ("VentilationLevel", "0"),
        "\u5de6\u540e\u5ea7\u6905\u901a\u98ce1\u6863": ("VentilationLevel", "1"),
        "\u5de6\u540e\u5ea7\u6905\u901a\u98ce2\u6863": ("VentilationLevel", "2"),
        "\u5de6\u540e\u5ea7\u6905\u901a\u98ce3\u6863": ("VentilationLevel", "3"),
        "\u5173\u95ed\u5de6\u540e\u5ea7\u6905\u52a0\u70ed": ("HeatingLevel", "0"),
        "\u5de6\u540e\u5ea7\u6905\u52a0\u70ed1\u6863": ("HeatingLevel", "1"),
        "\u5de6\u540e\u5ea7\u6905\u52a0\u70ed2\u6863": ("HeatingLevel", "2"),
        "\u5de6\u540e\u5ea7\u6905\u52a0\u70ed3\u6863": ("HeatingLevel", "3"),
    }
    LEFT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797 = {
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u8f7b\u7f13": "1",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u6807\u51c6": "2",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u5f3a\u529b": "3",
    }
    LEFT_REAR_SEAT_MASSAGE_AREA_VALUES_8797 = {
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\uff08\u4e0a\u8170\u90e8\uff09": "1",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170\uff08\u4e0b\u8170\u90e8\uff09": "2",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u4e0b\u534a\u8eab": "3",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\u548c\u8170\uff08\u5168\u80cc\uff09": "4",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\u548c\u4e0b\u534a\u8eab": "5",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170\u548c\u4e0b\u534a\u8eab": "6",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\u548c\u8170\u548c\u4e0b\u534a\u8eab": "7",
    }
    LEFT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797 = {
        "\u6253\u5f00\u5de6\u540e\u5ea7\u6905\u6309\u6469\u5f00\u5173": "true",
        "\u5173\u95ed\u5de6\u540e\u5ea7\u6905\u6309\u6469\u5f00\u5173": "false",
    }
    LEFT_REAR_SEAT_MASSAGE_MODE_VALUES_8797 = {
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8109\u51b2": "1",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u6ce2\u6d6a": "2",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u732b\u6b65": "3",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u5355\u6392": "4",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8212\u7f13": "5",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u789f\u5f62": "6",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8170\u90e8": "7",
        "\u5de6\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u86c7\u5f62": "8",
    }
    LEFT_REAR_SEAT_FOLD_VALUES_8797 = {
        "\u5de6\u540e\u5ea7\u6905\u6298\u53e0": ("FOLDING_MODE_ENTRY", 30),
        "\u5de6\u540e\u5ea7\u6905\u5c55\u5f00": ("FOLDING_MODE_EXIT", 30),
    }
    RIGHT_REAR_SEAT_CLIMATE_VALUES_8797 = {
        "\u5173\u95ed\u53f3\u540e\u5ea7\u6905\u901a\u98ce": ("VentilationLevel", "0"),
        "\u53f3\u540e\u5ea7\u6905\u901a\u98ce1\u6863": ("VentilationLevel", "1"),
        "\u53f3\u540e\u5ea7\u6905\u901a\u98ce2\u6863": ("VentilationLevel", "2"),
        "\u53f3\u540e\u5ea7\u6905\u901a\u98ce3\u6863": ("VentilationLevel", "3"),
        "\u5173\u95ed\u53f3\u540e\u5ea7\u6905\u52a0\u70ed": ("HeatingLevel", "0"),
        "\u53f3\u540e\u5ea7\u6905\u52a0\u70ed1\u6863": ("HeatingLevel", "1"),
        "\u53f3\u540e\u5ea7\u6905\u52a0\u70ed2\u6863": ("HeatingLevel", "2"),
        "\u53f3\u540e\u5ea7\u6905\u52a0\u70ed3\u6863": ("HeatingLevel", "3"),
    }
    RIGHT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797 = {
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u8f7b\u7f13": "1",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u6807\u51c6": "2",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u5f3a\u5ea6-\u5f3a\u529b": "3",
    }
    RIGHT_REAR_SEAT_MASSAGE_AREA_VALUES_8797 = {
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\uff08\u4e0a\u8170\u90e8\uff09": "1",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170\uff08\u4e0b\u8170\u90e8\uff09": "2",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u4e0b\u534a\u8eab": "3",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\u548c\u8170\uff08\u5168\u80cc\uff09": "4",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\u548c\u4e0b\u534a\u8eab": "5",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u8170\u548c\u4e0b\u534a\u8eab": "6",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u90e8\u4f4d-\u80a9\u548c\u8170\u548c\u4e0b\u534a\u8eab": "7",
    }
    RIGHT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797 = {
        "\u6253\u5f00\u53f3\u540e\u5ea7\u6905\u6309\u6469\u5f00\u5173": "true",
        "\u5173\u95ed\u53f3\u540e\u5ea7\u6905\u6309\u6469\u5f00\u5173": "false",
    }
    RIGHT_REAR_SEAT_MASSAGE_MODE_VALUES_8797 = {
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8109\u51b2": "1",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u6ce2\u6d6a": "2",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u732b\u6b65": "3",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u5355\u6392": "4",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8212\u7f13": "5",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u789f\u5f62": "6",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u8170\u90e8": "7",
        "\u53f3\u540e\u5ea7\u6905\u6309\u6469\u6a21\u5f0f-\u86c7\u5f62": "8",
    }
    RIGHT_REAR_SEAT_FOLD_VALUES_8797 = {
        "\u53f3\u540e\u5ea7\u6905\u6298\u53e0": ("FOLDING_MODE_ENTRY", 30),
        "\u53f3\u540e\u5ea7\u6905\u5c55\u5f00": ("FOLDING_MODE_EXIT", 30),
    }
    THIRD_ROW_LEFT_SEAT_FOLD_VALUES_8797 = {
        "\u4e09\u6392\u5de6\u4fa7\u5ea7\u6905\u6298\u53e0": ("FOLD_ENTRY", 30),
        "\u4e09\u6392\u5de6\u4fa7\u5ea7\u6905\u5c55\u5f00": ("FOLD_EXIT", 30),
    }
    THIRD_ROW_LEFT_SEAT_HEATING_VALUES_8797 = {
        "\u4e09\u6392\u5de6\u4fa7\u5173\u95ed\u5ea7\u6905\u52a0\u70ed": "0",
        "\u4e09\u6392\u5de6\u4fa7\u5ea7\u6905\u52a0\u70ed1\u6863": "1",
        "\u4e09\u6392\u5de6\u4fa7\u5ea7\u6905\u52a0\u70ed2\u6863": "2",
        "\u4e09\u6392\u5de6\u4fa7\u5ea7\u6905\u52a0\u70ed3\u6863": "3",
    }
    THIRD_ROW_RIGHT_SEAT_FOLD_VALUES_8797 = {
        "\u4e09\u6392\u53f3\u4fa7\u5ea7\u6905\u6298\u53e0": ("FOLD_ENTRY", 30),
        "\u4e09\u6392\u53f3\u4fa7\u5ea7\u6905\u5c55\u5f00": ("FOLD_EXIT", 30),
    }
    THIRD_ROW_RIGHT_SEAT_HEATING_VALUES_8797 = {
        "\u4e09\u6392\u53f3\u4fa7\u5173\u95ed\u5ea7\u6905\u52a0\u70ed": "0",
        "\u4e09\u6392\u53f3\u4fa7\u5ea7\u6905\u52a0\u70ed1\u6863": "1",
        "\u4e09\u6392\u53f3\u4fa7\u5ea7\u6905\u52a0\u70ed2\u6863": "2",
        "\u4e09\u6392\u53f3\u4fa7\u5ea7\u6905\u52a0\u70ed3\u6863": "3",
    }
    CHARGING_PORT_OPERATION_VALUES_8797 = {
        "\u6253\u5f00\u5145\u7535\u5c0f\u95e8": "OPEN",
        "\u5173\u95ed\u5145\u7535\u5c0f\u95e8": "CLOSE",
    }
    REAR_DISPLAY_OPERATION_VALUES_8797 = {
        "\u6253\u5f00\u540e\u6392\u5c4f": "ACTIVE",
        "\u5173\u95ed\u540e\u6392\u5c4f": "ACTIVE",
    }
    LASTMODE_CACHE_REMOTE_PATH = (
        "/mnt/share/carcontrolservice/vehicle_settings_cache.properties"
    )
    LASTMODE_CACHE_IGNORED_KEY_MARKERS = (
        "addedmileage",
        "current_battery_life",
        "total_mileage",
        "total_range",
        "range_standard",
    )
    PASSENGER_SEAT_CLIMATE_NAMES_8797 = (
        set(PASSENGER_SEAT_HEATING_VALUES_8797)
        | set(PASSENGER_SEAT_VENTILATION_VALUES_8797)
    )
    DRIVER_TEMPERATURE_VALUES_8797 = (
        "16", "16.5", "17", "17.5", "18", "18.5", "19", "19.5",
        "20", "20.5", "21", "21.5", "22", "22.5", "23", "23.5",
        "24", "24.5", "25", "25.5", "26", "26.5", "27", "27.5",
        "28", "28.5", "29", "29.5", "30", "30.5", "31", "31.5",
        "32",
    )
    DRIVER_TEMPERATURE_INSTRUCTION_NAMES_8797 = (
        "空调调节主驾温度-Lo",
        *(
            f"空调调节主驾温度-{temperature}度"
            for temperature in DRIVER_TEMPERATURE_VALUES_8797
        ),
        "空调调节主驾温度-High",
    )
    PASSENGER_TEMPERATURE_INSTRUCTION_NAMES_8797 = (
        "空调调节副驾温度-Lo",
        *(
            f"空调调节副驾温度-{temperature}度"
            for temperature in DRIVER_TEMPERATURE_VALUES_8797
        ),
        "空调调节副驾温度-High",
    )
    FRONT_FAN_LEVEL_VALUES_8797 = tuple(str(level) for level in range(1, 11))
    FRONT_FAN_LEVEL_INSTRUCTION_NAMES_8797 = (
        *(
            f"空调前排风量{level}挡"
            for level in FRONT_FAN_LEVEL_VALUES_8797
        ),
        "空调前排风量MAX挡",
    )
    RECIRCULATION_MODE_VALUES_8797 = {
        "打开空调循环模式-内循环": "RECIRCULATION",
        "打开空调循环模式-外循环": "FRESH",
        "打开空调循环模式-自动循环": "AUTO",
    }
    REAR_HVAC_VALUES_8797 = {
        "打开后排空调": (
            "Vehicle.Cabin.HVAC.Station.Row2.IsAirConditioningActive",
            "true",
        ),
        "关闭后排空调": (
            "Vehicle.Cabin.HVAC.Station.Row2.IsAirConditioningActive",
            "false",
        ),
    }
    HVAC_SWITCH_VALUES_8797 = {
        "开启后控制屏童锁": (
            "Vehicle.Cabin.HVAC.Rear.ControlPanel.LockedRequest",
            "LOCK",
        ),
        "关闭后控制屏童锁": (
            "Vehicle.Cabin.HVAC.Rear.ControlPanel.LockedRequest",
            "UNLOCK",
        ),
        "打开空调经济模式": (
            "Vehicle.Cabin.HVAC.IsEconomyModeActive",
            "true",
        ),
        "打开空调自动模式": (
            "Vehicle.Cabin.HVAC.IsEconomyModeActive",
            "true",
        ),
        "打开后排空调自动模式": (
            "Vehicle.Cabin.HVAC.Station.Row2.IsAutoModeActive",
            "true",
        ),
        "打开极速降温开关": (
            "Vehicle.Cabin.HVAC.IsMaxCoolingActive",
            "true",
        ),
        "关闭极速降温开关": (
            "Vehicle.Cabin.HVAC.IsMaxCoolingActive",
            "false",
        ),
        "打开极速升温开关": (
            "Vehicle.Cabin.HVAC.IsMaxHeatingActive",
            "true",
        ),
        "关闭极速升温开关": (
            "Vehicle.Cabin.HVAC.IsMaxHeatingActive",
            "false",
        ),
    }
    MIRROR_SHADE_VALUES_8797 = {
        "折叠后视镜": (
            "Vehicle.Body.Mirrors.FoldRequest",
            "FOLD",
            "Vehicle.Body.Mirrors.FoldStatus",
            "后视镜折叠状态",
        ),
        "展开后视镜": (
            "Vehicle.Body.Mirrors.FoldRequest",
            "UNFOLD",
            "Vehicle.Body.Mirrors.FoldStatus",
            "后视镜折叠状态",
        ),
        "后视镜折叠状态": (None, None, "Vehicle.Body.Mirrors.FoldStatus", "后视镜折叠状态"),
        "后视镜展开状态": (None, None, "Vehicle.Body.Mirrors.FoldStatus", "后视镜折叠状态"),
        "打开后遮阳帘": (
            "Vehicle.Cabin.RearShade.AutoAdjust",
            "AUTO_OPEN",
            "Vehicle.Cabin.RearShade.Position",
            "后遮阳帘位置",
        ),
        "关闭后遮阳帘": (
            "Vehicle.Cabin.RearShade.AutoAdjust",
            "AUTO_CLOSE",
            "Vehicle.Cabin.RearShade.Position",
            "后遮阳帘位置",
        ),
        "打开前遮阳帘": (
            "Vehicle.Cabin.Sunroof.Shade.AutoAdjust",
            "AUTO_OPEN",
            "Vehicle.Cabin.Sunroof.Shade.Position",
            "前遮阳帘位置",
        ),
        "关闭前遮阳帘": (
            "Vehicle.Cabin.Sunroof.Shade.AutoAdjust",
            "AUTO_CLOSE",
            "Vehicle.Cabin.Sunroof.Shade.Position",
            "前遮阳帘位置",
        ),
    }
    EASY_SUSPENSION_VALUES_8797 = {
        "打开轻松通过": (
            "Vehicle.ADAS.EasyPassActiveRequest",
            "ON",
            "Vehicle.ADAS.EasyPassActiveStatus",
            "轻松通过状态",
        ),
        "关闭轻松通过": (
            "Vehicle.ADAS.EasyPassActiveRequest",
            "OFF",
            "Vehicle.ADAS.EasyPassActiveStatus",
            "轻松通过状态",
        ),
        "打开轻松载物": (
            "Vehicle.Chassis.Suspension.IsManualEasyLoadModeEnabled",
            "true",
            "Vehicle.Chassis.Suspension.ManualEasyLoadStatus",
            "轻松载物状态",
        ),
        "关闭轻松载物": (
            "Vehicle.Chassis.Suspension.IsManualEasyLoadModeEnabled",
            "false",
            "Vehicle.Chassis.Suspension.ManualEasyLoadStatus",
            "轻松载物状态",
        ),
        "打开轻松进出": (
            "Vehicle.Chassis.Suspension.IsManualEasyEntryActive",
            "true",
            "Vehicle.Chassis.Suspension.ManualEasyLoadStatus",
            "轻松进出状态",
        ),
        "关闭轻松进出": (
            "Vehicle.Chassis.Suspension.IsManualEasyEntryActive",
            "false",
            "Vehicle.Chassis.Suspension.ManualEasyLoadStatus",
            "轻松进出状态",
        ),
    }
    EASY_SUSPENSION_HEIGHT_RESULT_COMMANDS_8797 = (
        ("左前悬架高度", "Vehicle.Chassis.Suspension.HeightChange.FrontLeft"),
        ("右前悬架高度", "Vehicle.Chassis.Suspension.HeightChange.FrontRight"),
        ("左后悬架高度", "Vehicle.Chassis.Suspension.HeightChange.RearLeft"),
        ("右后悬架高度", "Vehicle.Chassis.Suspension.HeightChange.RearRight"),
    )
    HYBRID_MODE_VALUES_8797 = {
        "打开强制纯电": (
            "Vehicle.Powertrain.Hybrid.ModeSelectionRequested",
            "FORCE_EV",
        ),
        "关闭强制纯电": (
            "Vehicle.Powertrain.Hybrid.ModeSelectionRequested",
            "EV_FIRST",
        ),
    }
    EXTREME_PASS_VALUES_8797 = {
        "打开极限通过": (
            "Vehicle.VehicleMotionControl.ExtremePassSwitch",
            "ON",
        ),
        "关闭极限通过": (
            "Vehicle.VehicleMotionControl.ExtremePassSwitch",
            "OFF",
        ),
    }
    MIRROR_HEATING_VALUES_8797 = {
        "打开后视镜加热": (
            "Vehicle.Body.Mirrors.IsHeatingOn",
            "true",
        ),
        "关闭后视镜加热": (
            "Vehicle.Body.Mirrors.IsHeatingOn",
            "false",
        ),
    }
    STEERING_WHEEL_HEATING_VALUES_8797 = {
        "方向盘加热1挡": (
            "Vehicle.Chassis.SteeringWheel.HeatingLevel",
            "1",
        ),
        "方向盘加热2挡": (
            "Vehicle.Chassis.SteeringWheel.HeatingLevel",
            "2",
        ),
        "方向盘加热3挡": (
            "Vehicle.Chassis.SteeringWheel.HeatingLevel",
            "3",
        ),
        "关闭方向盘加热": (
            "Vehicle.Chassis.SteeringWheel.HeatingLevel",
            "4",
        ),
    }
    DRIVING_MODE_READ_COMMANDS_8797 = {
        "驾驶模式": (
            "驾驶模式当前选项",
            "Vehicle.Powertrain.Transmission.OEMPerformanceMode",
        ),
        "驾驶模式线控转向自定义": (
            "驾驶模式线控转向自定义当前选项",
            "Vehicle.Chassis.SteeringWheel.AngleCustomizationSetting",
        ),
        "驾驶模式动力自定义": (
            "驾驶模式动力自定义当前选项",
            "Vehicle.Powertrain.ElectricMotor.TorqueCustomizationSetting",
        ),
        "驾驶模式转向自定义": (
            "驾驶模式转向自定义当前选项",
            "Vehicle.Chassis.SteeringWheel.SteerMode",
        ),
        "驾驶模式制动自定义": (
            "驾驶模式制动自定义当前选项",
            "Vehicle.Chassis.Brake.PedalFeedbackMode",
        ),
        "驾驶模式悬架硬度自定义": (
            "驾驶模式悬架硬度自定义当前选项",
            "Vehicle.Chassis.Suspension.Damping.CustomSetting",
        ),
        "驾驶模式悬架高度自定义": (
            "驾驶模式悬架高度自定义当前选项",
            "Vehicle.Chassis.Suspension.LevelControl.CustomSetting",
        ),
        "驾驶-超级节能开关": (
            "驾驶-超级节能开关状态",
            "Vehicle.Powertrain.Transmission.OEMPerformanceMode",
        ),
        "驾驶-能源模式": (
            "驾驶-能源模式当前选项",
            "Vehicle.Powertrain.Hybrid.ModeSelectionRequested",
        ),
    }
    DRIVE_AND_LOCK_READ_COMMANDS_8797 = {
        "驾驶-强制纯电开关": (
            (
                "驾驶-强制纯电开关状态",
                "Vehicle.Powertrain.Hybrid.ModeSelectionRequested",
            ),
        ),
        "驾驶-目标电量": (
            (
                "驾驶-目标电量当前选项",
                "Vehicle.Powertrain.TractionBattery.Charging.TargetSOC.Requested",
            ),
        ),
        "驾驶-autohold自动驻车": (
            (
                "驾驶-autohold自动驻车当前选项",
                "Vehicle.ADAS.AutoHold.Mode",
            ),
        ),
        "驾驶-能量回收设置": (
            (
                "驾驶-能量回收设置当前选项",
                "Vehicle.Powertrain.Regeneration.Mode",
            ),
        ),
        "驾驶-自动轻松进出开关": (
            (
                "驾驶-自动轻松进出开关当前选项",
                "Vehicle.Chassis.Suspension.SmartEasyEntryStatus",
            ),
        ),
        "驾驶-自动轻松载物开关": (
            (
                "驾驶-自动轻松载物开关当前选项",
                "Vehicle.Chassis.Suspension.IntelligentEasyLoadStatus",
            ),
        ),
        "驾驶-云台悬架开关": (
            (
                "驾驶-云台悬架开关当前选项",
                "Vehicle.ADAS.TCS.IsActivePreviewControlEnabled",
            ),
        ),
        "驾驶-极限通过开关": (
            (
                "驾驶-极限通过开关当前选项",
                "Vehicle.VehicleMotionControl.ExtremePassSwitch",
            ),
        ),
        "驾驶-陡坡缓降开关": (
            (
                "驾驶-陡坡缓降开关当前选项",
                "Vehicle.ADAS.HDC.SystemStatus",
            ),
        ),
        "驾驶-ICS智能舒适制动开关": (
            (
                "驾驶-ICS智能舒适制动开关当前选项",
                "Vehicle.ADAS.ComfortBrake.EnableStatus",
            ),
        ),
        "驾驶-智能防滑开关": (
            (
                "驾驶-智能防滑开关当前选项",
                "Vehicle.ADAS.Navigation.IsRoadPreviewOn",
            ),
        ),
        "驾驶-车身稳定系统开关": (
            (
                "车身稳定系统开关状态",
                "Vehicle.ADAS.VehicleStabilityEnhancement.IsEnabled",
            ),
        ),
        "门锁-童锁开关": (
            (
                "后排左侧童锁当前选项",
                "Vehicle.Cabin.Door.Row2.DriverSide.IsChildLockEnabled",
            ),
            (
                "后排右侧童锁当前选项",
                "Vehicle.Cabin.Door.Row2.PassengerSide.IsChildLockEnabled",
            ),
        ),
        "门锁-尾门开启高度设置状态": (
            (
                "门锁-尾门开启高度设置状态当前选项",
                "Vehicle.Body.Trunk.Rear.MaxPosition",
            ),
        ),
        "门锁-门开合力度设置状态": (
            (
                "门开合力度设置状态当前选项",
                "Vehicle.Body.Door.LeftFront.ServoAssistForce.Percentage",
            ),
        ),
        "倒车后视镜下翻开关": (
            (
                "倒车后视镜下翻开关当前选项",
                "Vehicle.Body.Mirrors.DriverSide.IsAutoTiltOnReverse",
            ),
        ),
        "雨刮灵敏度": (
            (
                "雨刮灵敏度当前选项",
                "Vehicle.Body.Windshield.Front.Wiping.Intensity",
            ),
        ),
        "主驾座椅便利进出开关": (
            (
                "主驾座椅便利进出开关当前选项",
                "Vehicle.Cabin.Seat.Row1.DriverSide.IsEasyEntryEnabled",
            ),
        ),
        "副驾座椅便利进出开关": (
            (
                "副驾座椅便利进出开关当前选项",
                "Vehicle.Cabin.Seat.Row1.PassengerSide.IsEasyEntryEnabled",
            ),
        ),
        "锁车自动关闭遮阳帘开关": (
            (
                "锁车自动关闭遮阳帘当前选项",
                "Vehicle.Cabin.Sunroof.Shade.IsAutoCloseOnLockEnabled",
            ),
        ),
        "锁车自动关窗开关": (
            (
                "锁车自动关窗当前选项",
                "Vehicle.Cabin.Door.IsAutoCloseWindowOnLockEnabled",
            ),
        ),
        "信号敲一敲开关尾门": (
            (
                "信号敲一敲开关尾门当前选项",
                "Vehicle.Body.Trunk.Rear.IsEWSEnabled",
            ),
        ),
    }

    # 8797 当前已确认沿用 8295 执行逻辑的指令白名单。
    # 8295 不做限制，继续使用完整内置指令表。
    PLATFORM_INSTRUCTION_NAMES = {
        "8797": (
            "音频探测",
            "账号",
            "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001",
            "\u9884\u7ea6\u5145\u7535\u5f00\u59cb\u65f6\u95f4",
            "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u65f6\u95f4",
            "Lastmode快速校验",
            "C屏下电",
            "踩刹车",
            "占座",
            "电机前进",
            "电机后退",
            "亮屏检测",
            "等待",
            "机器人上锁",
            "机器人解锁开门",
            "机器人上车关门",
            "机器人正负30度",
            "机器人正负60度",
            "机器人正负90度",
            "打开后备箱",
            "关闭后备箱",
            "打开空调",
            "关闭空调",
            "空调打开AC",
            "空调关闭AC",
            "打开前排空调Auto模式",
            "关闭前排空调Auto模式",
            "空调打开温度同步",
            "空调关闭温度同步",
            *DRIVER_TEMPERATURE_INSTRUCTION_NAMES_8797,
            *PASSENGER_TEMPERATURE_INSTRUCTION_NAMES_8797,
            *FRONT_FAN_LEVEL_INSTRUCTION_NAMES_8797,
            *RECIRCULATION_MODE_VALUES_8797,
            *REAR_HVAC_VALUES_8797,
            *HVAC_SWITCH_VALUES_8797,
            *MIRROR_SHADE_VALUES_8797,
            *EASY_SUSPENSION_VALUES_8797,
            *HYBRID_MODE_VALUES_8797,
            *EXTREME_PASS_VALUES_8797,
            *MIRROR_HEATING_VALUES_8797,
            *STEERING_WHEEL_HEATING_VALUES_8797,
            *DRIVING_MODE_READ_COMMANDS_8797,
            *DRIVE_AND_LOCK_READ_COMMANDS_8797,
            STEP_BOARD_STATUS_INSTRUCTION_NAME_8797,
            *SEAT_SCENE_INSTRUCTION_NAMES_8797,
            *DRIVER_SEAT_POSITION_VALUES_8797,
            *DRIVER_SEAT_HEATING_VALUES_8797,
            *DRIVER_SEAT_VENTILATION_VALUES_8797,
            *DRIVER_SEAT_MASSAGE_VALUES_8797,
            *DRIVER_SEAT_MASSAGE_AREA_VALUES_8797,
            *DRIVER_SEAT_MASSAGE_MODE_VALUES_8797,
            *PASSENGER_SEAT_POSITION_VALUES_8797,
            *PASSENGER_SEAT_HEATING_VALUES_8797,
            *PASSENGER_SEAT_VENTILATION_VALUES_8797,
            *PASSENGER_SEAT_MASSAGE_SWITCH_VALUES_8797,
            *PASSENGER_SEAT_MASSAGE_INTENSITY_VALUES_8797,
            *PASSENGER_SEAT_MASSAGE_AREA_VALUES_8797,
            *PASSENGER_SEAT_MASSAGE_MODE_VALUES_8797,
            *LEFT_REAR_SEAT_CLIMATE_VALUES_8797,
            *LEFT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797,
            *LEFT_REAR_SEAT_MASSAGE_AREA_VALUES_8797,
            *LEFT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797,
            *LEFT_REAR_SEAT_MASSAGE_MODE_VALUES_8797,
            *LEFT_REAR_SEAT_FOLD_VALUES_8797,
            *RIGHT_REAR_SEAT_CLIMATE_VALUES_8797,
            *RIGHT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797,
            *RIGHT_REAR_SEAT_MASSAGE_AREA_VALUES_8797,
            *RIGHT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797,
            *RIGHT_REAR_SEAT_MASSAGE_MODE_VALUES_8797,
            *RIGHT_REAR_SEAT_FOLD_VALUES_8797,
            *THIRD_ROW_LEFT_SEAT_FOLD_VALUES_8797,
            *THIRD_ROW_LEFT_SEAT_HEATING_VALUES_8797,
            *THIRD_ROW_RIGHT_SEAT_FOLD_VALUES_8797,
            *THIRD_ROW_RIGHT_SEAT_HEATING_VALUES_8797,
            *CHARGING_PORT_OPERATION_VALUES_8797,
            *REAR_DISPLAY_OPERATION_VALUES_8797,
            ELECTRIC_STEERING_WHEEL_POSITION_INSTRUCTION_NAME_8797,
            "整车 reset",
            "截图",
        ),
    }

    def __init__(self):
        # 所有基准都存在这一个文件里
        # 配置基准文件夹（打包后在程序目录下）
        import sys
        if hasattr(sys, '_MEIPASS'):
            # 打包后：配置文件保存在程序所在目录
            base_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发模式：配置文件保存在脚本所在目录
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.baseline_dir = os.path.join(base_path, "配置基准文件")
        if not os.path.exists(self.baseline_dir):
            os.makedirs(self.baseline_dir)
        self.baseline_file = os.path.join(self.baseline_dir, "all_baselines.json")
        os.makedirs(self.baseline_dir, exist_ok=True)
        
        # 继电器配置（默认值，实际由主程序动态传入）
        self.relay_port = "COM4"
        self.relay_baudrate = 9600
        self.relay_channel_map = {
            "踩刹车": 1,
            "按启动键": 2,
            "开门": 3,
            "关门": 4,
            "占座": 3,
            "电机前进": 1,
            "电机后退": 2
        }
        
        # 休眠唤醒等待时间配置（由综合测试面板传入）
        self.sleep_wake_delay = 0.0    # 休眠唤醒延迟时间（初始值）
        self.initial_sleep_wake_delay = 0.0
        self.increment_time = 0.0      # 递增时间
        self.current_cycle_count = 0   # 当前循环次数
        self.stop_check = None         # 由 TestRunner 注入，用于长等待期间快速停止
        self.last_execution_detail = {}  # 最近一次执行的读取/对比详情，供失败日志使用
        self.vehicle_platform = "8295"
        
        # 机器人TCP/IP配置
        self.robot_ip = "192.168.1.10"
        self.robot_port = 2000
        self.robot_timeout = 5  # TCP连接超时时间（秒）
        
        # 内置所有指令配置（直接在这里添加所有指令）
        self.instructions = {
            "云台摄像头连接状态": {
                "platforms": ("8295",),
                "wait_seconds": 0,
                "skip_read_wait": True,
                "result_parser": "connected_camera_status",
                "result_cmds": [
                    ("云台摄像头连接状态", "adb -host shell busctl --no-pager call extenderservice.yunos.com /extenderservice/yunos/com extenderservice.yunos.com.interface getConnectedCamera s '{}'"),
                ],
                "tolerance": 0,
            },
            "音频探测": {
                "special_type": "audio_detection",  # 标记为特殊指令
                "wait_seconds": 0,
                "result_cmds": [],
                "tolerance": 0
            },
            "账号": {
                "wait_seconds": 0,
                "raw_output": True,
                "result_cmds": [
                    ("账号信息", "adb -host shell getprop account.sysprop.info")
                ],
                "tolerance": 0
            },
            "Lastmode快速校验": {
                "platforms": ("8797",),
                "special_type": "lastmode_cache",
                "wait_seconds": 0,
                "result_cmds": [],
                "exact_compare_fields": ["*"],
                "tolerance": 0
            },
            "JS-语音设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "voice",
                "value_normalizer": "speech_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 5.0,
                "result_cmds": [
                    ("语音设置开关状态", "adb -host shell node --output-console /data/voice.js")
                ],
                "tolerance": 0
            },
            "JS-声音设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "Snd",
                "value_normalizer": "sound_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 5.0,
                "result_cmds": [
                    ("声音设置", "adb -host shell node --output-console /data/sound.js")
                ],
                "tolerance": 0
            },
            "JS-智驾设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "Plt",
                "value_normalizer": "pilot_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 3.0,
                "result_cmds": [
                    ("智驾设置状态", "adb -host shell node --output-console /data/AIPilot.js")
                ],
                "tolerance": 0
            },
            "JS-连接设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "Con",
                "value_normalizer": "connection_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 3.0,
                "result_cmds": [
                    ("连接设置开关状态", "adb -host shell node --output-console /data/connect.js")
                ],
                "tolerance": 0
            },
            "JS-显示设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "Show",
                "value_normalizer": "display_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_quiet_seconds": 1.0,
                "key_value_max_collect_seconds": 5.0,
                "result_cmds": [
                    ("显示设置开关状态", "adb -host shell node --output-console /data/show.js")
                ],
                "tolerance": 0
            },
            "JS-通用设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "Gen",
                "value_normalizer": "display_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 5.0,
                "result_cmds": [
                    ("通用设置开关状态", "adb -host shell node --output-console /data/general.js")
                ],
                "tolerance": 0
            },
            "JS-车辆设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "veh",
                "value_normalizer": "voice_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 3.0,
                "result_cmds": [
                    ("车辆设置开关状态", "adb -host shell node --output-console /data/vehicle.js")
                ],
                "tolerance": 0
            },
            "JS-灯光设置开关状态": {
                "wait_seconds": 0,
                "parse_key_values": True,
                "filter_key_values": True,
                "value_key_prefix": "Light",
                "value_normalizer": "display_settings",
                "exact_compare_fields": ["*"],
                "read_retries": 1,
                "read_retry_interval": 1,
                "read_timeout": 300,
                "key_value_max_collect_seconds": 5.0,
                "result_cmds": [
                    ("灯光设置开关状态", "adb -host shell node --output-console /data/light.js")
                ],
                "tolerance": 0
            },
            "JS-1": {
                "execute_cmd": "adb -host shell node --output-console /data/1.js",
                "wait_seconds": 0,
                "read_timeout": 300,
                "success_by_exit_code": True,
                "suppress_output": True,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "JS-2": {
                "execute_cmd": "adb -host shell node --output-console /data/2.js",
                "wait_seconds": 0,
                "read_timeout": 300,
                "success_by_exit_code": True,
                "suppress_output": True,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "JS-3": {
                "execute_cmd": "adb -host shell node --output-console /data/3.js",
                "wait_seconds": 0,
                "read_timeout": 300,
                "success_by_exit_code": True,
                "suppress_output": True,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "JS-4": {
                "execute_cmd": "adb -host shell node --output-console /data/4.js",
                "wait_seconds": 0,
                "read_timeout": 300,
                "success_by_exit_code": True,
                "suppress_output": True,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "JS-5": {
                "execute_cmd": "adb -host shell node --output-console /data/5.js",
                "wait_seconds": 0,
                "read_timeout": 300,
                "success_by_exit_code": True,
                "suppress_output": True,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "语音-千问大模型开关状态": {
                "wait_seconds": 0,
                "raw_output": True,
                "exact_compare_fields": ["千问大模型开关状态"],
                "read_retries": 2,
                "read_retry_interval": 1,
                "result_cmds": [
                    ("千问大模型开关状态", "adb -host shell getprop persist.llm.enhanced")
                ],
                "tolerance": 0
            },
            "车窗全开": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872231 2",
                "wait_seconds": 5,
                "result_cmds": [
                    ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl"),
                    ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl"),
                    ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl"),
                    ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl")
                ],
                "tolerance": 3
            },
            "车窗全关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872231 1",
                "wait_seconds": 3,
                "result_cmds": [
                    ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl"),
                    ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl"),
                    ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl"),
                    ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl")
                ],
                "tolerance": 3
            },
            "车窗通风": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872231 3",
                "wait_seconds": 3,
                "result_cmds": [
                    ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl"),
                    ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl"),
                    ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl"),
                    ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl")
                ],
                "tolerance": 3
            },
            "车窗状态": {
                #"execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872231 3",
                #"wait_seconds": 3,
                "result_cmds": [
                    ("主驾车窗", "adb -host shell vapisend -get ctrl.window.driver_ctrl"),
                    ("副驾车窗", "adb -host shell vapisend -get ctrl.window.passenger_ctrl"),
                    ("左后车窗", "adb -host shell vapisend -get ctrl.window.rear_left_ctrl"),
                    ("右后车窗", "adb -host shell vapisend -get ctrl.window.rear_right_ctrl")
                ],
                "tolerance": 3
            },
            "打开空调": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.power_status 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调状态", "adb -host shell vapisend -get ctrl.ac.power_status")
                ],
                "tolerance": 0
            },
            "关闭空调": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.power_status 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调状态", "adb -host shell vapisend -get ctrl.ac.power_status")
                ],
                "tolerance": 0
            },
            "空调打开AC": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.compressor_switch 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("AC状态", "adb -host shell vapisend -get ctrl.ac.compressor_switch"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调关闭AC": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.compressor_switch 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("AC状态", "adb -host shell vapisend -get ctrl.ac.compressor_switch"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "打开前排空调Auto模式": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.auto_mode 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排空调Auto模式状态", "adb -host shell vapisend -get ctrl.ac.auto_mode"),
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level"),
                ],
                "tolerance": 0
            },
            "关闭前排空调Auto模式": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.auto_mode 0",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排空调Auto模式状态", "adb -host shell vapisend -get ctrl.ac.auto_mode"),
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.blower_level"),
                ],
                "tolerance": 0
            },
            "空调打开温度同步": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.dual_ctrl_status 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("温度同步状态", "adb -host shell vapisend -get ctrl.ac.dual_ctrl_status"),
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调关闭温度同步": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.dual_ctrl_status 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("温度同步状态", "adb -host shell vapisend -get ctrl.ac.dual_ctrl_status"),
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-Lo": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 15.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-16度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 16",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-16.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 16.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                   # ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-17度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 17",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-17.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 17.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                   # ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-18度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 18",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                   # ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-18.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 18.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-19度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 19",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-19.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 19.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-20度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 20",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-20.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 20.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-21度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 21",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-21.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 21.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-22度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 22",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                   # ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-22.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 22.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-23度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 23",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                    #("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature")
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-23.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 23.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-24度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 24",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-24.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 24.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-25度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 25",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-25.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 25.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-26度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 26",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-26.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 26.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-27度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 27",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-27.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 27.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-28度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 28",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-28.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 28.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-29度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 29",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-29.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 29.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-30度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 30",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-30.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 30.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-31度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 31",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-31.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 31.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-32度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 32",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节主驾温度-High": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.driver_temperature 32.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-Lo": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 15.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-16度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 16",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-16.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 16.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-17度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 17",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-17.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 17.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-18度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 18",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-18.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 18.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-19度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 19",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-19.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 19.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-20度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 20",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-20.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 20.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-21度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 21",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-21.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 21.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-22度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 22",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-22.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 22.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-23度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 23",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-23.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 23.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-24度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 24",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-24.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 22",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-25度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 25",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-25.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 25.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-26度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 26",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-26.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 26.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-27度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 27",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-27.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 27.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-28度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 28",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-28.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 28.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-29度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 29",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-29.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 29.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-30度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 30",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-30.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 30.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-31度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 31",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-31.5度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 31.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-32度": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 32",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调调节副驾温度-High": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.passenger_temperature 32.5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                    ("压缩机状态", "adb -host shell vapisend -get ctrl.custom.536872059"),
                ],
                "tolerance": 0
            },
            "空调前排风量1挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量2挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量3挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量4挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量5挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量6挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量7挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量8挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 8",
                "wait_seconds": 1,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量9挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 9",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量10挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 10",
                "wait_seconds": 1,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "空调前排风量MAX挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.front_blower_level 11",
                "wait_seconds": 1,
                "result_cmds": [
                    ("前排风量挡位", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },


            "打开空调循环模式-内循环": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.recirculation_mode 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调循环模式", "adb -host shell vapisend -get ctrl.ac.recirculation_mode"),
                ],
                "tolerance": 0
            },
            "打开空调循环模式-外循环": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.recirculation_mode 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调循环模式", "adb -host shell vapisend -get ctrl.ac.recirculation_mode"),
                ],
                "tolerance": 0
            },
            "打开空调循环模式-自动循环": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.recirculation_mode 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调循环模式", "adb -host shell vapisend -get ctrl.ac.recirculation_mode"),
                ],
                "tolerance": 0
            },

            "打开后排空调": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.rear_power_status 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("后排空调状态", "adb -host shell vapisend -get ctrl.ac.rear_power_status"),
                ],
                "tolerance": 0
            },
            "关闭后排空调": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.rear_power_status 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("后排空调状态", "adb -host shell vapisend -get ctrl.ac.rear_power_status"),
                ],
                "tolerance": 0
            },
            "打开空调前排锁后排开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.rear_lock 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排锁后排状态", "adb -host shell vapisend -get ctrl.ac.rear_lock"),
                ],
                "tolerance": 0
            },
            "关闭空调前排锁后排开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.rear_lock 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("前排锁后排状态", "adb -host shell vapisend -get ctrl.ac.rear_lock"),
                ],
                "tolerance": 0
            },
            "打开空调经济模式": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.eco_switch 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调经济模式状态", "adb -host shell vapisend -get ctrl.ac.eco_switch"),
                    ("空调风量状态", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "打开空调经济模式": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.economy_mode 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("空调经济模式状态", "adb -host shell vapisend -get ctrl.ac.economy_mode"),
                    ("空调风量状态", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                ],
                "tolerance": 0
            },
            "打开后排空调自动模式": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.rear_auto_mode 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("后排空调自动模式状态", "adb -host shell vapisend -get ctrl.ac.rear_auto_mode"),
                    ("后排空调风量状态", "adb -host shell vapisend -get ctrl.ac.rear_blower_level"),
                ],
                "tolerance": 0
            },
            "打开极速降温开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.max_cooling 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("极速降温开关状态", "adb -host shell vapisend -get ctrl.ac.max_cooling"),
                    ("空调风量状态", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                    ("空调主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("空调副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                ],
                "tolerance": 0
            },
            "关闭极速降温开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.max_cooling 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("极速降温开关状态", "adb -host shell vapisend -get ctrl.ac.max_cooling"),
                    ("空调风量状态", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                    ("空调主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("空调副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                ],
                "tolerance": 0
            },
            "打开极速升温开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.max_heating 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("极速升温开关状态", "adb -host shell vapisend -get ctrl.ac.max_heating"),
                    ("空调风量状态", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                    ("空调主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("空调副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                ],
                "tolerance": 0
            },
            "关闭极速升温开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.ac.max_heating 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("极速升温开关状态", "adb -host shell vapisend -get ctrl.ac.max_heating"),
                    ("空调风量状态", "adb -host shell vapisend -get ctrl.ac.front_blower_level"),
                    ("空调主驾温度", "adb -host shell vapisend -get ctrl.ac.driver_temperature"),
                    ("空调副驾温度", "adb -host shell vapisend -get ctrl.ac.passenger_temperature"),
                ],
                "tolerance": 0
            },

            "折叠后视镜": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871720 1",
                "wait_seconds": 10,
                "result_cmds": [
                    ("后视镜状态", "adb -host shell vapisend -get ctrl.custom.536871720")
                ],
                "tolerance": 0
            },
            "后视镜折叠": {
                #"execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871720 1",
                "wait_seconds": 10,
                "result_cmds": [
                    ("后视镜状态", "adb -host shell vapisend -get ctrl.custom.536871720")
                ],
                "tolerance": 0
            },
            "后视镜折叠状态": {
                "wait_seconds": 0,
                "result_cmds": [
                    ("后视镜折叠状态", "adb -host shell vapisend -get ctrl.custom.536871720")
                ],
                "tolerance": 0
            },
            "展开后视镜": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871720 2",
                "wait_seconds": 10,
                "result_cmds": [
                    ("后视镜状态", "adb -host shell vapisend -get ctrl.custom.536871720")
                ],
                "tolerance": 0
            },
            "后视镜展开": {
                "wait_seconds": 10,
                "result_cmds": [
                    ("后视镜状态", "adb -host shell vapisend -get ctrl.custom.536871720")
                ],
                "tolerance": 0
            },
            "后视镜展开状态": {
                "wait_seconds": 0,
                "result_cmds": [
                    ("后视镜折叠状态", "adb -host shell vapisend -get ctrl.custom.536871720")
                ],
                "tolerance": 0
            },
            "打开后遮阳帘": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.sunroof.rear_shade_switch 1",
                "wait_seconds": 10,
                "result_cmds": [
                    ("后遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.rear_shade_percentage")
                ],
                "tolerance": 0
            },
            "关闭后遮阳帘": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.sunroof.rear_shade_switch 2",
                "wait_seconds": 10,
                "result_cmds": [
                    ("后遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.rear_shade_percentage")
                ],
                "tolerance": 2
            },
            "打开前遮阳帘": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.sunroof.shade_switch 1",
                "wait_seconds": 10,
                "result_cmds": [
                    ("前遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.shade_percentage")
                ],
                "tolerance": 2
            },
            "关闭前遮阳帘": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.sunroof.shade_switch 2",
                "wait_seconds": 10,
                "result_cmds": [
                    ("前遮阳帘位置", "adb -host shell vapisend -get ctrl.sunroof.shade_percentage")
                ],
                "tolerance": 2
            },
            "主驾座椅驾驶位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_pos_switch_group_restore 2",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
                ],
                "tolerance": 2
            },
            "主驾座椅进出位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_pos_switch_group_restore 3",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
                ],
                "tolerance": 2
            },
            "主驾座椅其他位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_pos_switch_group_restore 6",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
                ],
                "tolerance": 2
            },
            "主驾座椅备用位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_pos_switch_group_restore 4",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
                ],
                "tolerance": 2
            },
            "主驾座椅休息位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_pos_switch_group_restore 5",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
                ],
                "tolerance": 2
            },
            "主驾座椅贵妃椅位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_pos_switch_group_restore 11",
                "wait_seconds": 20,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871633"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871634"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871635"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.custom.536871636")
                ],
                "tolerance": 2
            },

            "关闭主驾座椅加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_heating 4",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅加热状态", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
                ],
                "tolerance": 0
            },
            "主驾座椅加热1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_heating 1",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅加热1档", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
                ],
                "tolerance": 0
            },
            "主驾座椅加热2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_heating 2",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
                ],
                "tolerance": 0
            },
            "主驾座椅加热3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_heating 3",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅加热3档", "adb -host shell vapisend -get ctrl.seat.driver_heating"),
                ],
                "tolerance": 0
            },
            "关闭主驾座椅通风": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_ventilation 4",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅通风状态", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
                ],
                "tolerance": 0
            },

            "主驾座椅通风1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_ventilation 1",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅通风1档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
                ],
                "tolerance": 0
            },
            "主驾座椅通风2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_ventilation 2",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅通风2档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
                ],
                "tolerance": 0
            },
            "主驾座椅通风3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.driver_ventilation 3",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾座椅通风2档", "adb -host shell vapisend -get ctrl.seat.driver_ventilation"),
                ],
                "tolerance": 0
            },
            "打开主驾座椅按摩": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871649 1",
                "wait_seconds": 1,
                "result_cmds": [
                    ("主驾按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871649"),
                ],
                "tolerance": 0
            },
            "关闭主驾座椅按摩": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871649 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871649"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩强度-轻缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871651 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-轻缓", "adb -host shell vapisend -get ctrl.custom.536871651"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩强度-标准": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871651 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-标准", "adb -host shell vapisend -get ctrl.custom.536871651"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩强度-强力": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871651 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-强力", "adb -host shell vapisend -get ctrl.custom.536871651"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-肩（上腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-肩", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-腰（下腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-腰（下腰部）", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-下半身", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-肩+腰(全背）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-肩+腰(全背）", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-肩+下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-肩+下半身", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-腰+下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-腰+下半身", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-肩+腰+下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-肩+腰+下半身", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-大腿": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 8",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-大腿", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-坐垫": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 9",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-坐垫", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-背部舒缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 A",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-背部舒缓", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩部位-背部舒缓+大腿+坐垫": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872205 B",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩强度-背部舒缓+大腿+坐垫", "adb -host shell vapisend -get ctrl.custom.536872205"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-脉冲/全身舒展": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-脉冲/全身舒展", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-波浪/敲揉舒压": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-波浪/敲揉舒压", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-猫步/推拿唤醒": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-猫步/推拿唤醒", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-单排/揉搓活血": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-单排/揉搓活血", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-舒缓/腰部古法": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-舒缓/腰部古法", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-碟形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-碟形", "adb -host shell vapisend -get cctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-腰部": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-腰部", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },
            "主驾座椅按摩模式-蛇形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871650 8",
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾座椅按摩模式-蛇形", "adb -host shell vapisend -get ctrl.custom.536871650"),
                ],
                "tolerance": 0
            },



            "副驾座椅贵妃椅位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 11",
                "wait_seconds": 20,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "副驾座椅零重力位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 9",
                "wait_seconds": 20,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "副驾座椅进出位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 3",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "副驾座椅常用位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 2",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "副驾座椅休息位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 5",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "副驾座椅备用位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 4",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "副驾座椅其他位置": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_pos_switch_group_restore 6",
                "wait_seconds": 15,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.custom.536871642"),
                    ("上下位置", "adb -host shell vapisend -get ctrl.custom.536871643"),
                    ("抬升位置", "adb -host shell vapisend -get ctrl.custom.536871644"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.passenger_back_pos")
                ],
                "tolerance": 2
            },
            "关闭副驾座椅加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_heating 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅加热关闭", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
                ],
                "tolerance": 0
            },
            "副驾座椅加热1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_heating 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅加热1档", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
                ],
                "tolerance": 0
            },
            "副驾座椅加热2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_heating 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
                ],
                "tolerance": 0
            },
            "副驾座椅加热3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_heating 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅加热2档", "adb -host shell vapisend -get ctrl.seat.passenger_heating"),
                ],
                "tolerance": 0
            },
            "关闭副驾座椅通风": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_ventilation 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅通风状态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
                ],
                "tolerance": 0
            },
            "副驾座椅通风1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_ventilation 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅通风1档态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
                ],
                "tolerance": 0
            },
            "副驾座椅通风2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_ventilation 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅通风2档态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
                ],
                "tolerance": 0
            },
            "副驾座椅通风3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.passenger_ventilation 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅通风3档态", "adb -host shell vapisend -get ctrl.seat.passenger_ventilation"),
                ],
                "tolerance": 0
            },
            "打开副驾座椅按摩": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871657 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871657"),
                ],
                "tolerance": 0
            },
            "关闭副驾座椅按摩": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871657 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩开关状态", "adb -host shell vapisend -get ctrl.custom.536871657"),
                ],
                "tolerance": 0
            },
#必须按摩开关是打开状态才行
            "副驾座椅按摩强度-轻缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871659 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-轻缓", "adb -host shell vapisend -get ctrl.custom.536871659"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩强度-标准": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871659 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-标准", "adb -host shell vapisend -get ctrl.custom.536871659"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩强度-强力": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871659 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-强力", "adb -host shell vapisend -get ctrl.custom.536871659"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-肩（上腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩部位-肩（上腰部）", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-腰（下腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-腰（下腰部）", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-下半身", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-肩+腰(全背）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-肩+腰(全背）", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-肩+下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-肩+下半身", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-腰+下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-腰+下半身", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-肩+腰+下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-肩+腰+下半身", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-大腿": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 8",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-大腿", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-坐垫": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 9",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-坐垫", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-背部舒缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 A",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-背部舒缓", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩部位-背部舒缓+大腿+坐垫": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872206 B",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩强度-背部舒缓+大腿+坐垫", "adb -host shell vapisend -get ctrl.custom.536872206"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-脉冲": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-脉冲", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-波浪": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-波浪", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-猫步": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-猫步", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-单排": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-单排", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-舒缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-单排", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-碟形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-碟形", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-腰部": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-腰部", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },
            "副驾座椅按摩模式-蛇形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871658 8",
                "wait_seconds": 2,
                "result_cmds": [
                    ("副驾座椅按摩模式-蛇形", "adb -host shell vapisend -get ctrl.custom.536871658"),
                ],
                "tolerance": 0
            },

            "关闭左后座椅通风": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872207 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅通风状态", "adb -host shell vapisend -get ctrl.custom.536872207"),
                ],
                "tolerance": 0
            },
            "左后座椅通风1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872207 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅通风1档态", "adb -host shell vapisend -get ctrl.custom.536872207"),
                ],
                "tolerance": 0
            },
            "左后座椅通风2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872207 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅通风2档态", "adb -host shell vapisend -get ctrl.custom.536872207"),
                ],
                "tolerance": 0
            },
            "左后座椅通风3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872207 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅通风1档态", "adb -host shell vapisend -get ctrl.custom.536872207"),
                ],
                "tolerance": 0
            },
            "关闭左后座椅加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.left_rear_heating 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅加热状态", "adb -host shell vapisend -get ctrl.seat.left_rear_heating"),
                ],
                "tolerance": 0
            },
            "左后座椅加热1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.left_rear_heating 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅加热1档态", "adb -host shell vapisend -get ctrl.seat.left_rear_heating"),
                ],
                "tolerance": 0
            },
            "左后座椅加热2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.left_rear_heating 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅加热2档态", "adb -host shell vapisend -get ctrl.seat.left_rear_heating"),
                ],
                "tolerance": 0
            },
            "左后座椅加热3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.left_rear_heating 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅加热3档态", "adb -host shell vapisend -get ctrl.seat.left_rear_heating"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩强度-轻缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_intensity 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩强度-轻缓", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_intensity"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩强度-标准": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_intensity 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩强度-标准", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_intensity"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩强度-强力": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_intensity 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩强度-强力", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_intensity"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-肩（上腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-肩（上腰部）", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-腰（下腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-肩（上腰部）", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-下半身", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-肩和腰（全背）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-肩和腰（全背）", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-肩和下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-肩和下半身", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-腰和下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-腰和下半身",
                     "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩部位-肩和腰和下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_part 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩部位-肩和腰和下半身",
                     "adb -host shell vapisend -get ctrl.seat.rear_left_massage_part"),
                ],
                "tolerance": 0
            },
            "打开左后座椅按摩开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.massage_onoff_status_rearleft 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩状态", "adb -host shell vapisend -get ctrl.seat.massage_onoff_status_rearleft"),
                ],
                "tolerance": 0
            },
            "关闭左后座椅按摩开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.massage_onoff_status_rearleft 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩状态", "adb -host shell vapisend -get ctrl.seat.massage_onoff_status_rearleft"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-脉冲": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-脉冲", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-波浪": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-波浪", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-猫步": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-猫步", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-单排": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-单排", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-舒缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-单排", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-碟形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-碟形", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-腰部": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-腰部", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅按摩模式-蛇形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.rear_left_massage_mode 8",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-蛇形", "adb -host shell vapisend -get ctrl.seat.rear_left_massage_mode"),
                ],
                "tolerance": 0
            },
            "左后座椅折叠": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872479 31",
                "wait_seconds": 30,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.seat.rear_left_hozt_pos"),
                    ("倾斜位置", "adb -host shell vapisend -get ctrl.seat.rear_left_tilt_pos"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.rear_left_back_pos"),
                    ("腿托位置", "adb -host shell vapisend -get ctrl.seat.rear_left_leg_fold_pos")
                ],
                "tolerance": 0
            },
            "左后座椅展开": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872479 32",
                "wait_seconds": 30,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.seat.rear_left_hozt_pos"),
                    ("倾斜位置", "adb -host shell vapisend -get ctrl.seat.rear_left_tilt_pos"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.rear_left_back_pos"),
                    ("腿托位置", "adb -host shell vapisend -get ctrl.seat.rear_left_leg_fold_pos")
                ],
                "tolerance": 0
            },
            "关闭右后座椅通风": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872208 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅通风状态", "adb -host shell vapisend -get ctrl.custom.536872208"),
                ],
                "tolerance": 0
            },
            "右后座椅通风1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872208 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅通风1档态", "adb -host shell vapisend -get ctrl.custom.536872208"),
                ],
                "tolerance": 0
            },
            "右后座椅通风2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872208 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅通风2档态", "adb -host shell vapisend -get ctrl.custom.536872208"),
                ],
                "tolerance": 0
            },
            "右后座椅通风3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872208 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅通风1档态", "adb -host shell vapisend -get ctrl.custom.536872208"),
                ],
                "tolerance": 0
            },
            "关闭右后座椅加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.right_seat_heating 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅加热状态", "adb -host shell vapisend -get ctrl.seat.right_seat_heating"),
                ],
                "tolerance": 0
            },
            "右后座椅加热1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.right_seat_heating 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅加热1档态", "adb -host shell vapisend -get ctrl.seat.right_seat_heating"),
                ],
                "tolerance": 0
            },
            "右后座椅加热2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.right_seat_heating 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅加热2档态", "adb -host shell vapisend -get ctrl.seat.right_seat_heating"),
                ],
                "tolerance": 0
            },
            "右后座椅加热3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.right_seat_heating 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅加热3档态", "adb -host shell vapisend -get ctrl.seat.right_seat_heating"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩强度-轻缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872213 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩强度-轻缓", "adb -host shell vapisend -get ctrl.custom.536872213"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩强度-标准": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872213 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩强度-标准", "adb -host shell vapisend -get ctrl.custom.536872213"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩强度-强力": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872213 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩强度-强力", "adb -host shell vapisend -get ctrl.custom.536872213"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-肩（上腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-肩（上腰部）", "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-腰（下腰部）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-肩（上腰部）", "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-下半身", "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-肩和腰（全背）": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-肩和腰（全背）", "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-肩和下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-肩和下半身", "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-腰和下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-腰和下半身",
                     "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩部位-肩和腰和下半身": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872211 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩部位-肩和腰和下半身",
                     "adb -host shell vapisend -get ctrl.custom.536872211"),
                ],
                "tolerance": 0
            },
            "打开右后座椅按摩开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.massage_onoff_status_rearright 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩状态", "adb -host shell vapisend -get ctrl.seat.massage_onoff_status_rearright"),
                ],
                "tolerance": 0
            },
            "关闭右后座椅按摩开关": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.massage_onoff_status_rearright 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩状态", "adb -host shell vapisend -get ctrl.seat.massage_onoff_status_rearright"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-脉冲": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-脉冲", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-波浪": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-波浪", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-猫步": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-猫步", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-单排": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-单排", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-舒缓": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 5",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式-单排", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-碟形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 6",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-碟形", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-腰部": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 7",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-腰部", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅按摩模式-蛇形": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872212 8",
                "wait_seconds": 2,
                "result_cmds": [
                    ("右后座椅按摩模式-蛇形", "adb -host shell vapisend -get ctrl.custom.536872212"),
                ],
                "tolerance": 0
            },
            "右后座椅折叠": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872481 31",
                "wait_seconds": 30,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.seat.rear_right_hozt_pos"),
                    ("倾斜位置", "adb -host shell vapisend -get ctrl.seat.rear_right_tilt_pos"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.rear_right_back_pos"),
                    ("腿托位置", "adb -host shell vapisend -get ctrl.seat.rear_right_leg_fold_pos")
                ],
                "tolerance": 0
            },
            "右后座椅展开": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872481 32",
                "wait_seconds": 30,
                "result_cmds": [
                    ("前后位置", "adb -host shell vapisend -get ctrl.seat.rear_right_hozt_pos"),
                    ("倾斜位置", "adb -host shell vapisend -get ctrl.seat.rear_right_tilt_pos"),
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.rear_right_back_pos"),
                    ("腿托位置", "adb -host shell vapisend -get ctrl.seat.rear_right_leg_fold_pos")
                ],
                "tolerance": 0
            },
            "三排左侧座椅折叠": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872483 31",
                "wait_seconds": 30,
                "result_cmds": [
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.third_left_back_pos"),
                ],
                "tolerance": 0
            },
            "三排左侧座椅展开": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872483 32",
                "wait_seconds": 30,
                "result_cmds": [
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.third_left_back_pos"),
                ],
                "tolerance": 0
            },
            "三排左侧座椅加热1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_left_heating 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_left_heating"),
                ],
                "tolerance": 0
            },
            "三排左侧座椅加热2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_left_heating 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_left_heating"),
                ],
                "tolerance": 0
            },
            "三排左侧座椅加热3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_left_heating 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_left_heating"),
                ],
                "tolerance": 0
            },
            "三排左侧关闭座椅加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_left_heating 0",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_left_heating"),
                ],
                "tolerance": 0
            },
            "三排右侧座椅折叠": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872485 31",
                "wait_seconds": 30,
                "result_cmds": [
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.third_right_back_pos"),
                ],
                "tolerance": 0
            },
            "三排右侧座椅展开": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872485 32",
                "wait_seconds": 30,
                "result_cmds": [
                    ("靠背位置", "adb -host shell vapisend -get ctrl.seat.third_right_back_pos"),
                ],
                "tolerance": 0
            },
            "三排右侧座椅加热1档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_right_heating 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_right_heating"),
                ],
                "tolerance": 0
            },
            "三排右侧座椅加热2档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_right_heating 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_right_heating"),
                ],
                "tolerance": 0
            },
            "三排右侧座椅加热3档": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_right_heating 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_right_heating"),
                ],
                "tolerance": 0
            },
            "三排右侧关闭座椅加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.seat.third_right_heating 0",
                "wait_seconds": 2,
                "result_cmds": [
                    ("加热档位", "adb -host shell vapisend -get ctrl.seat.third_right_heating"),
                ],
                "tolerance": 0
            },




            "打开后备箱": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872172 2",
                "wait_seconds": 10,
                "result_cmds": [
                    ("尾门开度", "adb -host shell vapisend -get ctrl.door.elec_plg_status"),
                    ("尾门锁状态", "adb -host shell vapisend -get ctrl.door.trunk_status"),
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 4
            },
            "关闭后备箱": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872172 3",
                "wait_seconds": 10,
                "result_cmds": [
                    ("尾门开度", "adb -host shell vapisend -get ctrl.door.elec_plg_status"),
                    ("尾门锁状态", "adb -host shell vapisend -get ctrl.door.trunk_status"),
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 4
            },
            "打开充电小门": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871466 1",
                "wait_seconds": 5,
                "result_cmds": [
                    ("尾门开度", "adb -host shell vapisend -get ctrl.custom.536871466")
                ],
                "tolerance": 2
            },
            "关闭充电小门": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871466 2",
                "wait_seconds": 5,
                "result_cmds": [
                    ("尾门开度", "adb -host shell vapisend -get ctrl.custom.536871466")
                ],
                "tolerance": 2
            },
            "打开轻松通过": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872285 2",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "关闭轻松通过": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872285 1",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "打开轻松载物": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872089 2",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "关闭轻松载物": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872089 1",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "打开轻松进出": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872088 2",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "关闭轻松进出": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872088 1",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "打开强制纯电": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.bms.hybrid_power_switch 0",
                "wait_seconds": 2,
                "result_cmds": [
                    ("强制纯电开关状态", "adb -host shell vapisend -get ctrl.bms.hybrid_power_switch"),
                ],
                "tolerance": 0
            },
            "关闭强制纯电": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.bms.hybrid_power_switch 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("强制纯电开关状态", "adb -host shell vapisend -get ctrl.bms.hybrid_power_switch"),
                ],
                "tolerance": 0
            },
            "打开极限通过": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.vmc.extreme_pass_switch 1",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "关闭极限通过": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.vmc.extreme_pass_switch 0",
                "wait_seconds": 20,
                "result_cmds": [
                    ("左前高度", "adb -host shell vapisend -get ctrl.custom.536872241"),
                    ("右前高度", "adb -host shell vapisend -get ctrl.custom.536872243"),
                    ("左后高度", "adb -host shell vapisend -get ctrl.custom.536872245"),
                    ("右后高度", "adb -host shell vapisend -get ctrl.custom.536872247")
                ],
                "tolerance": 5
            },
            "打开后视镜加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 1",
                "wait_seconds": 1,
                "result_cmds": [
                    ("后视镜加热状态", "adb -host shell vapisend -get ctrl.mirror.heating")
                ],
                "tolerance": 0
            },
            "关闭后视镜加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                "wait_seconds": 1,
                "result_cmds": [
                    ("后视镜加热状态", "adb -host shell vapisend -get ctrl.mirror.heating")
                ],
                "tolerance": 0
            },
            "方向盘加热1挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871754 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("方向盘加热挡位", "adb -host shell vapisend -get ctrl.custom.536871754")
                ],
                "tolerance": 0
            },
            "方向盘加热2挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871754 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("方向盘加热挡位", "adb -host shell vapisend -get ctrl.custom.536871754")
                ],
                "tolerance": 0
            },
            "方向盘加热3挡": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871754 3",
                "wait_seconds": 2,
                "result_cmds": [
                    ("方向盘加热挡位", "adb -host shell vapisend -get ctrl.custom.536871754")
                ],
                "tolerance": 0
            },
            "关闭方向盘加热": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871754 4",
                "wait_seconds": 2,
                "result_cmds": [
                    ("方向盘加热状态", "adb -host shell vapisend -get ctrl.custom.536871754")
                ],
                "tolerance": 0
            },

            "驾驶模式": {
                #"execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                #"wait_seconds": 5,
                "result_cmds": [
                    ("当前驾驶模式", "adb -host shell vapisend -get ctrl.drive_mode")
                ],
                "tolerance": 0
            },
            "驾驶模式线控转向自定义": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("驾驶模式线控转向自定义", "adb -host shell vapisend -get ctrl.personal.steering_angle")
                ],
                "tolerance": 0
            },
            "驾驶模式动力自定义": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("驾驶模式动力自定义", "adb -host shell vapisend -get ctrl.personal.powertrain_mode")
                ],
                "tolerance": 0
            },
            "驾驶模式转向自定义": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("驾驶模式转向自定义", "adb -host shell vapisend -get ctrl.personal.steering_status")
                ],
                "tolerance": 0
            },
            "驾驶模式制动自定义": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("驾驶模式制动自定义", "adb -host shell vapisend -get ctrl.brake.pedal_feedback_mode")
                ],
                "tolerance": 0
            },
            "驾驶模式悬架硬度自定义": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("驾驶模式悬架硬度自定义", "adb -host shell vapisend -get ctrl.custom.536872085")
                ],
                "tolerance": 0
            },
            "驾驶模式悬架高度自定义": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("驾驶模式悬架高度自定义", "adb -host shell vapisend -get ctrl.custom.536872086")
                ],
                "tolerance": 0
            },
            "驾驶-超级节能开关": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("超级节能开关状态", "adb -host shell vapisend -get ctrl.custom.536872151")
                ],
                "tolerance": 0
            },
            "驾驶-能源模式": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("当前能源模式", "adb -host shell vapisend -get ctrl.bms.hybrid_power_switch")
                ],
                "tolerance": 0
            },
            "驾驶-强制纯电开关": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("强制纯电开关状态", "adb -host shell vapisend -get ctrl.bms.hybrid_power_switch")
                ],
                "tolerance": 0
            },
            "驾驶-目标电量": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("目标电量设置", "adb -host shell vapisend -get ctrl.bms.target_battery")
                ],
                "tolerance": 0
            },

            "驾驶-autohold自动驻车": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("autohold自动驻车开关状态", "adb -host shell vapisend -get ctrl.sys.auto_hold_mode_switch")
                ],
                "tolerance": 0
            },
            "驾驶-能量回收设置": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("能量回收设置", "adb -host shell vapisend -get ctrl.bms.power_recycle_mode")
                ],
                "tolerance": 0
            },
            "驾驶-自动轻松进出开关": {
                "result_cmds": [
                    ("自动轻松进出开关状态", "adb -host shell vapisend -get ctrl.custom.536872282")
                ],
                "tolerance": 0
            },
            "驾驶-自动轻松载物开关": {
                "result_cmds": [
                    ("自动轻松载物开关状态", "adb -host shell vapisend -get ctrl.vmc.intelligent_easy_load_mode")
                ],
                "tolerance": 0
            },
            "驾驶-云台悬架开关": {
                # "execute_cmd": "adb -host shell vapisend -set ctrl.mirror.heating 0",
                # "wait_seconds": 5,
                "result_cmds": [
                    ("云台悬架开关状态", "adb -host shell vapisend -get ctrl.custom.536872068")
                ],
                "tolerance": 0
            },
            "驾驶-极限通过开关": {
                "result_cmds": [
                    ("极限通过开关状态", "adb -host shell vapisend -get ctrl.vmc.extreme_pass_switch")
                ],
                "tolerance": 0
            },
            "驾驶-一键调平开关": {
                "result_cmds": [
                    ("一键调平开关状态", "adb -host shell vapisend -get ctrl.vmc.easy_level_mode")
                ],
                "tolerance": 0
            },
            "驾驶-陡坡缓降开关": {
                "result_cmds": [
                    ("陡坡缓降开关状态", "adb -host shell vapisend -get ctrl.custom.536872235")
                ],
                "tolerance": 0
            },
            "驾驶-ICS智能舒适制动开关": {
                "result_cmds": [
                    ("ICS智能舒适制动开关状态", "adb -host shell vapisend -get ctrl.brake.comfort_braking")
                ],
                "tolerance": 0
            },
            "驾驶-智能防滑开关": {
                "result_cmds": [
                    ("智能防滑开关状态", "adb -host shell vapisend -get ctrl.sys.road_preview_system_switch")
                ],
                "tolerance": 0
            },
            "驾驶-车身稳定系统开关": {
                "result_cmds": [
                    ("车身稳定系统开关状态", "adb -host shell vapisend -get ctrl.esp.status")
                ],
                "tolerance": 0
            },
            "门锁-童锁开关": {
                "result_cmds": [
                    ("左后童锁开关状态", "adb -host shell vapisend -get ctrl.custom.536871240"),
                    ("右后童锁开关状态", "adb -host shell vapisend -get ctrl.custom.536871241")
                ],
                "tolerance": 0
            },
            "门锁-尾门开启高度设置状态": {
                "result_cmds": [
                    ("尾门开启高度设置状态", "adb -host shell vapisend -get ctrl.door.elec_plg_open_percent"),
                ],
                "tolerance": 0
            },
            "门锁-门开合力度设置状态": {
                "result_cmds": [
                    ("左前门开合力度设置状态", "adb -host shell vapisend -get ctrl.door.fl_actuator_servo_force_set"),
                ],
                "tolerance": 0
            },
            "踏板-电动踏板临时开启": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.brake.pwr_foot_board_mode 1",
                "wait_seconds": 5,
                "result_cmds": [
                    ("左侧踏板位置", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_left_percentage"),
                    ("右侧踏板位置", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_right_percentage"),
                ],
                "tolerance": 0
            },
            "踏板-电动踏板临时关闭": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.brake.pwr_foot_board_mode 2",
                "wait_seconds": 5,
                "result_cmds": [
                    ("左侧踏板位置", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_left_percentage"),
                    ("右侧踏板位置", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_right_percentage"),
                ],
                "tolerance": 0
            },
            "踏板-电动踏板临时开启开关状态": {
                "result_cmds": [
                    ("临时开启开关状态", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_mode",),
                ],
                "tolerance": 0
            },
            "踏板电动踏板模式设置状态": {
                "result_cmds": [
                    ("踏板模式设置状态", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_mode"),
                ],
                "tolerance": 0
            },
            "踏板-左右侧电动踏板位置": {

                "result_cmds": [
                    ("左侧踏板位置", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_left_percentage"),
                    ("右侧踏板位置", "adb -host shell vapisend -get ctrl.brake.pwr_foot_board_right_percentage"),
                ],
                "tolerance": 0
            },
            "主驾座椅便利进出开关": {
                "result_cmds": [
                    ("主驾座椅便利进出开关状态", "adb -host shell vapisend -get ctrl.custom.536871668")
                ],
                "tolerance": 0
            },
            "副驾座椅便利进出开关": {
                "result_cmds": [
                    ("主驾座椅便利进出开关状态", "adb -host shell vapisend -get ctrl.custom.536871669")
                ],
                "tolerance": 0
            },
            "左后座椅便利进出开关": {
                "result_cmds": [
                    ("主驾座椅便利进出开关状态", "adb -host shell vapisend -get ctrl.seat.second_row_left_easy_access")
                ],
                "tolerance": 0
            },
            "右后座椅便利进出开关": {
                "result_cmds": [
                    ("主驾座椅便利进出开关状态", "adb -host shell vapisend -get ctrl.seat.second_row_right_easy_access")
                ],
                "tolerance": 0
            },
            "冰箱-电源开关状态": {
                "result_cmds": [
                    ("冰箱电源开关状态", "adb -host shell vapisend -get ctrl.icebox.power_status")
                ],
                "tolerance": 0
            },
            "冰箱-制冷制热设置状态": {
                "result_cmds": [
                    ("冰箱制冷制热设置状态", "adb -host shell vapisend -get ctrl.icebox.ctrl_mode")
                ],
                "tolerance": 0
            },
            "冰箱-温度设置设置状态": {
                "result_cmds": [
                    ("冰箱温度设置状态", "adb -host shell vapisend -get ctrl.icebox.temp_set")
                ],
                "tolerance": 0
            },
            "冰箱-离车恒温及时长设置状态": {
                "result_parser": "sigval_json_fields",
                "sigval_fields": [
                    "ConstantTempOnOff",
                    "TemperatureSet",
                    "TimeSet"
                ],
                "result_cmds": [
                    ("冰箱离车恒温及时长设置状态", "adb -host shell vapisend -get ctrl.icebox.lock_hold_fridge_switch")
                ],
                "tolerance": 0
            },
            "冰箱-童锁开关状态": {
                "result_cmds": [
                    ("冰箱童锁开关状态", "adb -host shell vapisend -get ctrl.ac.rear_panel_child_lock")
                ],
                "tolerance": 0
            },
            "无线充电开关": {
                "result_cmds": [
                    ("无线充电开关状态", "adb -host shell vapisend -get ctrl.bms.phone_wireless_charge_switch")
                ],
                "tolerance": 0
            },

            "倒车后视镜下翻开关": {
                "result_cmds": [
                    ("左侧下翻开关状态", "adb -host shell vapisend -get ctrl.custom.536872314"),
                    ("右侧下翻开关状态", "adb -host shell vapisend -get ctrl.custom.536872315")
                ],
                "tolerance": 0
            },
            "雨刮灵敏度": {
                "result_cmds": [
                    ("当前雨刮灵敏度", "adb -host shell vapisend -get ctrl.wiper.sensitivity_level"),
                ],
                "tolerance": 0
            },

            "锁车自动关闭遮阳帘开关": {
                "result_cmds": [
                    ("锁车自动关闭遮阳帘开关状态", "adb -host shell vapisend -get ctrl.sunroof.shade_lock_auto_close"),
                ],
                "tolerance": 0
            },
            "锁车自动关窗开关": {
                "result_cmds": [
                    ("锁车自动关窗开关状态", "adb -host shell vapisend -get ctrl.custom.536872317"),
                ],
                "tolerance": 0
            },
            "信号敲一敲开关尾门": {
                "result_cmds": [],
                "wait_seconds": 0,
                "tolerance": 0,
                "platforms": ("8797",),
            },
            "智驾-驾驶辅助Pilot开关": {
                "result_cmds": [
                    ("驾驶辅助Pilot开关状态", "adb -host shell vapisend -get ctrl.custom.536871300"),
                ],
                "tolerance": 0
            },
            "智驾-通勤辅助开关": {
                "result_cmds": [
                    ("通勤辅助开关状态", "adb -host shell vapisend -get ctrl.custom.536872399"),
                ],
                "tolerance": 0
            },
            "智驾-全速自适应巡航ACC开关": {
                "result_cmds": [
                    ("全速自适应巡航ACC开关状态", "adb -host shell vapisend -get ctrl.adas.quit_acc_switch"),
                ],
                "tolerance": 0
            },
            "智驾-高速高架领航辅助开关": {
                "result_cmds": [
                    ("高速高架领航辅助开关状态", "adb -host shell vapisend -get ctrl.custom.536871304"),
                ],
                "tolerance": 0
            },
            "智驾-高速高架变道确认方式设置状态": {
                "result_cmds": [
                    ("高速高架变道确认方式设置状态", "adb -host shell vapisend -get ctrl.custom.536871798"),
                ],
                "tolerance": 0
            },
            "智驾-收费站通行ETC开关": {
                "result_cmds": [
                    ("收费站通行ETC开关状态", "adb -host shell vapisend -get ctrl.custom.536872401"),
                ],
                "tolerance": 0
            },
            "智驾-信任增强开关": {
                "result_cmds": [
                    ("收费站通行ETC开关状态", "adb -host shell vapisend -get  ctrl.custom.536871803"),
                ],
                "tolerance": 0
            },
            "智驾-驾驶辅助风格设置状态": {
                "result_cmds": [
                    ("驾驶辅助风格设置状态", "adb -host shell vapisend -get ctrl.custom.536871301"),
                ],
                "tolerance": 0
            },
            "智驾-跟车距离设置状态": {
                "result_cmds": [
                    ("跟车距离设置状态", "adb -host shell vapisend -get ctrl.custom.536871354"),
                ],
                "tolerance": 0
            },
            "智驾-疲劳驾驶减速辅助开关状态": {
                "result_cmds": [
                    ("疲劳驾驶减速辅助开关状态", "adb -host shell vapisend -get ctrl.adas.DMS_integrated_ctrl_switch"),
                ],
                "tolerance": 0
            },
            "智驾-限速调整设置状态": {
                "result_cmds": [
                    ("限速调整设置状态", "adb -host shell vapisend -get ctrl.custom.536872396"),
                ],
                "tolerance": 0
            },
            "智驾-限速调整固定值偏置状态": {
                "result_cmds": [
                    ("限速调整固定值偏置状态", "adb -host shell vapisend -get ctrl.custom.536872397"),
                ],
                "tolerance": 0
            },
            "智驾-限速调整百分比偏置状态": {
                "result_cmds": [
                    ("限速调整百分比偏置状态", "adb -host shell vapisend -get ctrl.custom.536872398"),
                ],
                "tolerance": 0
            },
            "智驾-泊车风格设置状态": {
                "result_cmds": [
                    ("泊车风格设置状态", "adb -host shell vapisend -get ctrl.sys.aiparking_driving_style"),
                ],
                "tolerance": 0
            },
            "智驾-一键泊车方向盘静止开关状态": {
                "result_cmds": [
                    ("一键泊车方向盘静止开关状态", "adb -host shell vapisend -get ctrl.adas.sbw_silent_mode_switch"),
                ],
                "tolerance": 0
            },
            "智驾-前向碰撞预警开关": {
                "result_cmds": [
                    ("前向碰撞预警开关状态", "adb -host shell vapisend -get ctrl.adas.fcw_status"),
                ],
                "tolerance": 0
            },
            "智驾-前向碰撞灵敏度设置状态": {
                "result_cmds": [
                    ("前向碰撞灵敏度设置状态", "adb -host shell vapisend -get ctrl.adas.fcw_sensitivity"),
                ],
                "tolerance": 0
            },
            "智驾-前向自动紧急制动开关": {
                "result_cmds": [
                    ("前向自动紧急制动开关状态", "adb -host shell vapisend -get ctrl.aeb.status"),
                ],
                "tolerance": 0
            },
            "智驾-超感自动紧急制动开关": {
                "result_cmds": [
                    ("超感自动紧急制动开关状态", "adb -host shell vapisend -get ctrl.adas.pre_deceleration_assist_switch"),
                ],
                "tolerance": 0
            },
            "智驾-前向横穿碰撞预警开关": {
                "result_cmds": [
                    ("前向横穿碰撞预警开关状态", "adb -host shell vapisend -get ctrl.adas.fcta_sw_sts"),
                ],
                "tolerance": 0
            },
            "智驾-前向自动紧急避让开关": {
                "result_cmds": [
                    ("前向自动紧急避让开关状态", "adb -host shell vapisend -get ctrl.ipd.aes_switch"),
                ],
                "tolerance": 0
            },

            "智驾-后向自防碰撞辅助开关": {
                "result_cmds": [
                    ("后向自防碰撞辅助开关", "adb -host shell vapisend -get ctrl.adas.rear_drive_assisant_switch"),
                ],
                "tolerance": 0
            },
            "智驾-侧后方来车辅助开关": {
                "result_cmds": [
                    ("侧后方来车辅助开关", "adb -host shell vapisend -get ctrl.adas.rct_switch"),
                ],
                "tolerance": 0
            },
            "智驾-盲区预警开关": {
                "result_cmds": [
                    ("盲区预警开关", "adb -host shell vapisend -get ctrl.adas.blind_spot_monitor"),
                ],
                "tolerance": 0
            },
            "智驾-开门预警关": {
                "result_cmds": [
                    ("开门预警关", "adb -host shell vapisend -get ctrl.door.parking_warning"),
                ],
                "tolerance": 0
            },
            "智驾-后向自动紧急制动开关": {
                "result_cmds": [
                    ("后向自动紧急制动开关状态", "adb -host shell vapisend -get ctrl.ipd.raeb_switch"),
                ],
                "tolerance": 0
            },

            "智驾-低速紧急制动设置状态": {
                "result_cmds": [
                    ("低速紧急制动设置状态", "adb -host shell vapisend -get ctrl.custom.536872452"),
                ],
                "tolerance": 0
            },
            "智驾-误加速抑制辅助开关": {
                "result_cmds": [
                    ("误加速抑制辅助开关状态", "adb -host shell vapisend -get ctrl.speed_assistant.prevention_brake_misuse"),
                ],
                "tolerance": 0
            },

            "智驾-车道偏离辅助模式设置状态": {
                "result_cmds": [
                    ("车道偏离辅助模式设置状态", "adb -host shell vapisend -get ctrl.adas.lane_assistant"),
                ],
                "tolerance": 0
            },
            "智驾-车道偏离辅助灵敏度设置状态": {
                "result_cmds": [
                    ("车道偏离辅助灵敏度设置状态", "adb -host shell vapisend -get ctrl.custom.536871307"),
                ],
                "tolerance": 0
            },
            "智驾-车道偏离辅助警示方式": {
                "result_cmds": [
                    ("车道偏离辅助警示方式状态", "adb -host shell vapisend -get ctrl.custom.536871309"),
                ],
                "tolerance": 0
            },
            "智驾-紧急车道保持开关": {
                "result_cmds": [
                    ("紧急车道保持开关状态", "adb -host shell vapisend -get ctrl.adas.rcw_status"),
                ],
                "tolerance": 0
            },

            "智驾-起步与红绿灯提醒开关": {
                "result_cmds": [
                    ("起步与红绿灯提醒开关状态", "adb -host shell vapisend -get ctrl.custom.536871305"),
                ],
                "tolerance": 0
            },
            "智驾-限速报警开关": {
                "result_cmds": [
                    ("限速报警开关状态", "adb -host shell vapisend -get ctrl.custom.536871305"),
                ],
                "tolerance": 0
            },
            "智驾-驾驶员注意力监测设置状态": {
                "result_cmds": [
                    ("驾驶员注意力监测设置状态", "adb -host shell vapisend -get ctrl.custom.536871978"),
                ],
                "tolerance": 0
            },

            "灯光-灯光开关": {
                "result_cmds": [
                    ("灯光开关状态", "adb -host shell vapisend -get ctrl.custom.536871174"),
                ],
                "tolerance": 0
            },
            "灯光-智能远光灯开关状态": {
                "result_cmds": [
                    ("智能远光灯开关状态", "adb -host shell vapisend -get ctrl.light.IHC_enable"),
                ],
                "tolerance": 0
            },
            "灯光-打开智能远光灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.light.IHC_enable 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("智能远光灯开关状态", "adb -host shell vapisend -get ctrl.light.IHC_enable"),
                ],
                "tolerance": 2
            },
            "灯光-关闭智能远光灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.light.IHC_enable 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("智能远光灯开关状态", "adb -host shell vapisend -get ctrl.light.IHC_enable"),
                ],
                "tolerance": 2
            },

            "灯光-猎鹰智慧灯光系统开关": {
                "result_cmds": [
                    ("猎鹰智慧灯光系统开关状态", "adb -host shell vapisend -get ctrl.light.dlp_scene_enable"),
                ],
                "tolerance": 0
            },

            "灯光-ISC灯语主题设置": {
                "result_cmds": [
                    ("ISC灯语主题设置状态", "adb -host shell vapisend -get ctrl.custom.536871907"),
                ],
                "tolerance": 0
            },
            "灯光-驾驶辅助联动开关": {
                "result_cmds": [
                    ("驾驶辅助联动开关状态", "adb -host shell vapisend -get ctrl.custom.536871906"),
                ],
                "tolerance": 0
            },
            "灯光-露营灯开关": {
                "result_cmds": [
                    ("露营灯开关状态", "adb -host shell vapisend -get ctrl.light.roofspot_led_ctrl_enable_set"),
                ],
                "tolerance": 0
            },
            "灯光-迎宾灯效开关状态": {
                "result_cmds": [
                    ("迎宾灯效开关状态", "adb -host shell vapisend -get ctrl.custom.536871778"),
                ],
                "tolerance": 0
            },
            "灯光-大灯延迟关闭开关": {
                "result_cmds": [
                    ("大灯延迟关闭开关状态", "adb -host shell vapisend -get ctrl.personal.follow_me_home_switch"),
                ],
                "tolerance": 0
            },
            "灯光-大灯高度设置状态": {
                "result_cmds": [
                    ("大灯高度设置状态", "adb -host shell vapisend -get ctrl.custom.536871958"),
                ],
                "tolerance": 0
            },

            "灯光-氛围灯总开关": {
                "result_cmds": [
                    ("氛围灯总开关状态", "adb -host shell vapisend -get ctrl.ambient_light.switch"),
                ],
                "tolerance": 0
            },
            "灯光-氛围灯呼吸模式设置状态": {
                "result_cmds": [
                    ("氛围灯呼吸模式设置状态", "adb -host shell vapisend -get ctrl.ambient_light.vehicle_breath_mode_req"),
                ],
                "tolerance": 0
            },


            "灯光-开门照明开关": {
                "result_cmds": [
                    ("开门照明开关状态", "adb -host shell vapisend -get ctrl.custom.536871693"),
                ],
                "tolerance": 0
            },

            "灯光-阅读灯亮度设置状态": {
                "result_cmds": [
                    ("阅读灯亮度设置状态", "adb -host shell vapisend -get ctrl.custom.536872182"),
                ],
                "tolerance": 0
            },




            "打开后排屏": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872487 1",
                "wait_seconds": 5,
                "result_cmds": [],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "关闭后排屏": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536872487 1",
                "wait_seconds": 5,
                "result_cmds": [],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-打开左前阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871682 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("左前阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871682")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-关闭左前阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871682 2",
                "wait_seconds": 0,
                "result_cmds": [
                    ("左前阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871682")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-打开右前阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871684 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("右前阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871684")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-关闭右前阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871684 2",
                "wait_seconds": 0,
                "result_cmds": [
                    ("右前阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871684")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-打开左后阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871686 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("左后阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871686")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-关闭左后阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871686 2",
                "wait_seconds": 0,
                "result_cmds": [
                    ("左后阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871686")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-打开右后阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871688 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("右后阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871688")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-关闭右后阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871688 2",
                "wait_seconds": 0,
                "result_cmds": [
                    ("右后阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871688")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-打开全车阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871681 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("全车阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871681")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-关闭全车阅读灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871681 2",
                "wait_seconds": 0,
                "result_cmds": [
                    ("全车阅读灯状态", "adb -host shell vapisend -get ctrl.custom.536871681")
                ],  # 不需要读取结果，执行成功就成功
                "tolerance": 0
            },
            "灯光-打开近光灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871174 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("近光灯状态", "adb -host shell vapisend -get ctrl.custom.536871174")
                ],
                "tolerance": 0
            },
            "灯光-打开后雾灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871175 1",
                "wait_seconds": 0,
                "result_cmds": [
                    ("后雾灯状态", "adb -host shell vapisend -get ctrl.custom.536871175")
                ],
                "tolerance": 0
            },
            "灯光-关闭后雾灯": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.custom.536871175 0",
                "wait_seconds": 0,
                "result_cmds": [
                    ("后雾灯状态", "adb -host shell vapisend -get ctrl.custom.536871175")
                ],
                "tolerance": 0
            },




            "C屏下电": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.sys.hmivs_req 1",
                "wait_seconds": 5,
                "result_cmds": [
                    ("电源模式状态", "adb -host shell vapisend -get ctrl.sys.power_status"),
                ],
                "tolerance": 0
            },
            "打开220V插座": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.bms.inner_discharge_switch 1",
                "wait_seconds": 2,
                "result_cmds": [
                    ("220V插座状态", "adb -host shell vapisend -get ctrl.bms.inner_discharge_switch"),
                ],
                "tolerance": 0
            },
            "关闭220V插座": {
                "execute_cmd": "adb -host shell vapisend -set ctrl.bms.inner_discharge_switch 2",
                "wait_seconds": 2,
                "result_cmds": [
                    ("220V插座状态", "adb -host shell vapisend -get ctrl.bms.inner_discharge_switch"),
                ],
                "tolerance": 0
            },

            
            # ==================== 继电器控制指令 ====================
            # 通道号由综合测试面板动态传入，这里的 relay_channel 只是默认值
            "踩刹车": {
                "is_relay": True,          # 标记为继电器指令
                "relay_channel": 1,        # 默认通道（实际使用综合测试面板配置的 relayID_shache）
                "press_duration": 2.0,     # 按下持续时间（秒）
                "wait_seconds": 25,         # 动作后等待时间
                "result_cmds": [
                    ("电源模式", "adb -host shell vapisend -get ctrl.sys.power_mode")
                ],
                "tolerance": 0
            },
            "占座": {
                "is_relay": True,
                "relay_channel": 3,        # 默认通道（实际使用综合测试面板配置的 relayID_zhanzuo）
                "press_duration": 2.0,
                "wait_seconds": 2,
                "result_cmds": [
                    ("主驾占座状态", "adb -host shell vapisend -get ctrl.custom.536872320")
                ],
                "tolerance": 0
            },
            "电机前进": {
                "is_relay": True,
                "relay_channel": 1,        # 默认通道（实际使用综合测试面板配置的 relayID_qianjin）
                "press_duration": 5.0,
                "wait_seconds": 2,
                "result_cmds": [
                    ("车速", "adb -host shell vapisend -get ctrl.drive.vehicle_speed")
                ],
                "tolerance": 0
            },
            "电机后退": {
                "is_relay": True,
                "relay_channel": 2,        # 默认通道（实际使用综合测试面板配置的 relayID_houtui）
                "press_duration": 5.0,
                "wait_seconds": 2,
                "result_cmds": [
                    ("车速", "adb -host shell vapisend -get ctrl.drive.vehicle_speed")
                ],
                "tolerance": 0
            },
            
            # ==================== 视觉检测专用指令 ====================
            "亮屏检测": {
                "is_visual_only": True,    # 标记为纯视觉检测指令（不执行ADB/继电器）
                "wait_seconds": 3,         # 等待屏幕点亮时间
                "result_cmds": [],         # 不需要ADB读取，纯视觉检测
                "tolerance": 0
            },
            
            # ==================== 等待指令 ====================
            # 等待时间 = 休眠唤醒延迟时间 + 递增时间
            # 基准测试：保存空结果
            # 循环测试：等待时间完成，直接成功
            "等待": {
                "is_wait_only": True,      # 标记为纯等待指令（不执行ADB/继电器/读取）
                "result_cmds": [],         # 不需要读取结果
                "tolerance": 0
            },

            # ==================== 截图指令 ====================
            # 通过 uiautomator_screencap 截屏 → adb pull → 删除车机文件
            # 三个 adb 命令全部成功即通过，无需基准对比
            "截图": {
                "is_screenshot": True,     # 标记为截图指令
                "wait_seconds": 1,         # 截图后等待
                "result_cmds": [],
                "tolerance": 0
            },

            # ==================== 机器人控制指令 ====================
            # 通过TCP/IP发送机器人控制指令
            "机器人上锁": {
                "robot_command": "lock",   # 机器人指令
                "wait_seconds": 5,         # 动作后等待时间
                "result_cmds": [
                    ("锁状态", "adb -host shell vapisend -get ctrl.lock.lock_status"),
                ],
                "tolerance": 0
            },
            "机器人解锁开门": {
                "robot_command": "unlockopen",  # 机器人指令
                "wait_seconds": 50,              # 动作后等待时间
                "result_cmds": [
                    ("锁状态", "adb -host shell vapisend -get ctrl.lock.lock_status"),
                    ("主驾门状态", "adb -host shell vapisend -get ctrl.door.driver_door_status"),
                ],
                "tolerance": 0
            },
            "机器人上车关门": {
                "robot_command": "closedoor",  # 机器人指令
                "wait_seconds": 8,             # 动作后等待时间
                "result_cmds": [
                    ("主驾门状态", "adb -host shell vapisend -get ctrl.door.driver_door_status"),
                ],
                "tolerance": 0
            },
            "机器人正负30度": {
                "robot_command": "turn30",
                "robot_ip": "192.168.1.11",
                "robot_port": 2000,
                "wait_seconds": 0,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "机器人正负60度": {
                "robot_command": "turn60",
                "robot_ip": "192.168.1.11",
                "robot_port": 2000,
                "wait_seconds": 0,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "机器人正负90度": {
                "robot_command": "turn90",
                "robot_ip": "192.168.1.11",
                "robot_port": 2000,
                "wait_seconds": 0,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "机器人正负120度": {
                "robot_command": "turn120",
                "robot_ip": "192.168.1.11",
                "robot_port": 2000,
                "wait_seconds": 0,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },
            "诊断-左前门电释放": {
                "diagnostic_action": "lhzcu_left_front_door_e_release",
                "diagnostic_wait_seconds": 1,
                "read_retries": 5,
                "read_retry_interval": 1,
                "result_cmds": [
                    ("锁状态", "adb -host shell vapisend -get ctrl.lock.lock_status"),
                    ("主驾门状态", "adb -host shell vapisend -get ctrl.door.driver_door_status"),
                ],
                "tolerance": 0
            },
            "诊断-左后门电释放": {
                "diagnostic_action": "lhzcu_left_rear_door_e_release",
                "diagnostic_wait_seconds": 1,
                "read_retries": 5,
                "read_retry_interval": 1,
                "result_cmds": [
                    ("锁状态", "adb -host shell vapisend -get ctrl.lock.lock_status"),
                    ("左后门状态", "adb -host shell vapisend -get ctrl.door.rear_left_door_status"),
                ],
                "tolerance": 0
            },
            "诊断-右前门电释放": {
                "diagnostic_action": "rhzcu_right_front_door_e_release",
                "diagnostic_wait_seconds": 1,
                "read_retries": 5,
                "read_retry_interval": 1,
                "result_cmds": [
                    ("锁状态", "adb -host shell vapisend -get ctrl.lock.lock_status"),
                    ("副驾门状态", "adb -host shell vapisend -get ctrl.door.front_passenger_door_status"),
                ],
                "tolerance": 0
            },
            "诊断-右后门电释放": {
                "diagnostic_action": "rhzcu_right_rear_door_e_release",
                "diagnostic_wait_seconds": 1,
                "read_retries": 5,
                "read_retry_interval": 1,
                "result_cmds": [
                    ("锁状态", "adb -host shell vapisend -get ctrl.lock.lock_status"),
                    ("右后门状态", "adb -host shell vapisend -get ctrl.door.rear_right_door_status"),
                ],
                "tolerance": 0
            },




            "整车 reset": {
                "diagnostic_action": "vehicle_reset",
                "wait_seconds": 5,
                "doip_timeout": 5,
                "session_response_timeout": 4,
                "reset_response_timeout": 4,
                "reset_reconnect_delay": 0.5,
                "min_reset_total_responses": 1,
                "skip_baseline_compare": True,
                "result_cmds": [],
                "tolerance": 0
            },

            # 在这里继续添加更多指令...
        }
        for instruction_name in self.SEAT_SCENE_INSTRUCTION_NAMES_8797:
            self.instructions[instruction_name] = {
                "wait_seconds": 0,
                "result_cmds": [],
                "tolerance": 2,
                "platforms": ("8797",),
            }
        for instruction_name in ("开启后控制屏童锁", "关闭后控制屏童锁"):
            self.instructions[instruction_name] = {
                "wait_seconds": 1,
                "result_cmds": [],
                "tolerance": 0,
                "platforms": ("8797",),
            }
        self.instructions[
            self.ELECTRIC_STEERING_WHEEL_POSITION_INSTRUCTION_NAME_8797
        ] = {
            "wait_seconds": 0,
            "result_cmds": [],
            "tolerance": 0,
            "platforms": ("8295", "8797"),
        }
        self.instructions[self.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797] = {
            "wait_seconds": 0,
            "skip_read_wait": True,
            "result_cmds": [],
            "tolerance": 3,
            "platforms": ("8797",),
        }
        self.instructions[self.MIRROR_POSITION_INSTRUCTION_NAME_8295] = {
            "wait_seconds": 0,
            "result_cmds": [
                (self.MIRROR_POSITION_INSTRUCTION_NAME_8295, self.MIRROR_POSITION_READ_COMMAND_8295)
            ],
            "result_parser": "mirror_position_8295",
            "parse_key_values": True,
            "baseline_fields": self.MIRROR_POSITION_FIELDS_8295,
            "tolerance": 0,
            "platforms": ("8295",),
        }
        self.instructions[
            "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001"
        ] = {
            "wait_seconds": 0,
            "result_cmds": [
                (
                    "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001",
                    "adb -host shell vapisend -get ctrl.bms.reservation_switch",
                )
            ],
            "tolerance": 0,
            "platforms": ("8295", "8797"),
        }
        self.instructions[
            "\u9884\u7ea6\u5145\u7535\u5f00\u59cb\u65f6\u95f4"
        ] = {
            "wait_seconds": 0,
            "result_cmds": [
                (
                    "\u9884\u7ea6\u5145\u7535\u5c0f\u65f6",
                    "adb -host shell vapisend -get ctrl.custom.536872162",
                ),
                (
                    "\u9884\u7ea6\u5145\u7535\u5206\u949f",
                    "adb -host shell vapisend -get ctrl.custom.536872163",
                ),
            ],
            "tolerance": 0,
            "platforms": ("8295", "8797"),
        }
        self.instructions[
            "\u9884\u7ea6\u5145\u7535\u5f00\u59cb\u65f6\u95f4"
        ]["baseline_fields"] = (
            "\u9884\u7ea6\u5145\u7535\u5c0f\u65f6",
            "\u9884\u7ea6\u5145\u7535\u5206\u949f",
        )
        self.instructions[
            "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u65f6\u95f4"
        ] = {
            "wait_seconds": 0,
            "result_cmds": [
                (
                    "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u5c0f\u65f6",
                    "adb -host shell vapisend -get ctrl.custom.536872164",
                ),
                (
                    "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u5206\u949f",
                    "adb -host shell vapisend -get ctrl.custom.536872165",
                ),
            ],
            "tolerance": 0,
            "platforms": ("8295", "8797"),
        }
        self.instructions[
            "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u65f6\u95f4"
        ]["baseline_fields"] = (
            "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u5c0f\u65f6",
            "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u5206\u949f",
        )
        self.instructions[
            "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001"
        ]["baseline_fields"] = (
            "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001",
        )
        self.instruction_aliases = {
            "JS-语音服务开关状态": "JS-语音设置开关状态",
            "JS-声音设置": "JS-声音设置开关状态",
            "JS-智驾设置状态": "JS-智驾设置开关状态",
            "机器人正负60度：": "机器人正负60度",
            "机器人正负60度:": "机器人正负60度",
            "机器人正负90度：": "机器人正负90度",
            "机器人正负90度:": "机器人正负90度",
            "机器人正负120度：": "机器人正负120度",
            "机器人正负120度:": "机器人正负120度",
        }
    
    def add_instruction(self, name, config):
        """手动添加新指令"""
        self.instructions[name] = config

    def _canonical_instruction_name(self, instruction_name):
        name = str(instruction_name or "").strip()
        numbered_pattern = (
            rf"^{re.escape(self.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797)}\s*"
            r"[1-9]\d*$"
        )
        if re.fullmatch(numbered_pattern, name):
            return self.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797
        return self.instruction_aliases.get(name, name)

    def _baseline_instruction_name(self, instruction_name):
        """返回基准身份；可重复踏板指令保留并规范化序号。"""
        name = str(instruction_name or "").strip()
        match = re.fullmatch(
            rf"{re.escape(self.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797)}\s*"
            r"(?P<index>[1-9]\d*)",
            name,
        )
        if match:
            return (
                f"{self.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797} "
                f"{int(match.group('index'))}"
            )
        return self._canonical_instruction_name(name)

    def set_vehicle_platform(self, vehicle_platform):
        """设置当前车型平台。"""
        platform = str(vehicle_platform or "8295").strip()
        self.vehicle_platform = platform if platform in ("8295", "8797") else "8295"

    def _get_instruction_config(self, instruction_name):
        """获取当前平台下的指令配置，默认沿用 8295 配置。"""
        canonical_name = self._canonical_instruction_name(instruction_name)
        config = self.instructions.get(canonical_name, {})
        if (
            self.vehicle_platform == "8797"
            and canonical_name in {
                self.PASSENGER_SEAT_HEATING_LEVEL_1_NAME_8797,
                self.PASSENGER_SEAT_HEATING_LEVEL_2_NAME_8797,
                self.PASSENGER_SEAT_HEATING_LEVEL_3_NAME_8797,
                self.PASSENGER_SEAT_VENTILATION_OFF_NAME_8797,
                self.PASSENGER_SEAT_VENTILATION_LEVEL_1_NAME_8797,
                self.PASSENGER_SEAT_VENTILATION_LEVEL_2_NAME_8797,
                self.PASSENGER_SEAT_VENTILATION_LEVEL_3_NAME_8797,
            }
            and not isinstance(config, dict)
        ):
            config = {}
        if not isinstance(config, dict):
            return config

        if (
            self.vehicle_platform == "8797"
            and canonical_name == self.STEP_BOARD_STATUS_INSTRUCTION_NAME_8797
        ):
            config = dict(config)
            config.pop("execute_cmd", None)
            config.update({
                "wait_seconds": 0,
                "skip_read_wait": True,
                "special_type": "step_board_status",
                "result_cmds": [
                    (label, command)
                    for label, command, _value_type
                    in self.STEP_BOARD_RESULT_COMMANDS_8797
                ],
                "baseline_fields": self.STEP_BOARD_BASELINE_FIELDS_8797,
                "save_baseline_fields_only": True,
                "repeat_baseline_for_duplicates": True,
                "tolerance": 3,
                "platforms": ("8797",),
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.SEAT_SCENE_COMMANDS_8797
        ):
            execute_cmd, wait_seconds = self.SEAT_SCENE_COMMANDS_8797[canonical_name]
            config = dict(config)
            result_cmds = self.SEAT_SCENE_RESULT_COMMANDS_8797.get(
                canonical_name, ()
            )
            config.update({
                "execute_cmd": execute_cmd,
                "wait_seconds": wait_seconds,
                "result_cmds": list(result_cmds),
                "result_parser": "sigval_value",
                "baseline_fields": tuple(
                    label for label, _command in result_cmds
                ),
                "tolerance": 2,
                "platforms": ("8797",),
            })
        elif self.vehicle_platform == "8797" and canonical_name == "C屏下电":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell \"vapisend -set Vehicle.Cabin.Infotainment.PowerMode.Requested "
                    "POWER_DOWNREQUEST && vapisend -set Vehicle.LowVoltageBattery.PowerUsageModeControl "
                    "'{\\\"source\\\":1,\\\"mode\\\":2}'\""
                ),
                "wait_seconds": 5,
                "result_cmds": [
                    (
                        "电源模式状态",
                        "adb shell vapisend -get Vehicle.LowVoltageSystemState",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "账号":
            config = dict(config)
            config.update({
                "result_cmds": [
                    (
                        "账号信息",
                        'adb shell "getprop persist.account.user.id"',
                    )
                ],
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name == "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001"
        ):
            config = dict(config)
            config.update({
                "result_cmds": [
                    (
                        "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001",
                        "adb shell vapisend -get "
                        "Vehicle.Powertrain.TractionBattery.Charging.ReservationSwitch",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name == "\u9884\u7ea6\u5145\u7535\u5f00\u59cb\u65f6\u95f4"
        ):
            config = dict(config)
            config.update({
                "result_cmds": [
                    (
                        "\u9884\u7ea6\u5145\u7535\u5c0f\u65f6",
                        "adb shell vapisend -get "
                        "Vehicle.Powertrain.TractionBattery.Charging."
                        "ScheduledCharge.StartTime.Hours",
                    ),
                    (
                        "\u9884\u7ea6\u5145\u7535\u5206\u949f",
                        "adb shell vapisend -get "
                        "Vehicle.Powertrain.TractionBattery.Charging."
                        "ScheduledCharge.StartTime.Minutes",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name == "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u65f6\u95f4"
        ):
            config = dict(config)
            config.update({
                "result_cmds": [
                    (
                        "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u5c0f\u65f6",
                        "adb shell vapisend -get "
                        "Vehicle.Powertrain.TractionBattery.Charging."
                        "ScheduledCharge.EndTime.Hours",
                    ),
                    (
                        "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u5206\u949f",
                        "adb shell vapisend -get "
                        "Vehicle.Powertrain.TractionBattery.Charging."
                        "ScheduledCharge.EndTime.Minutes",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.EASY_SUSPENSION_VALUES_8797
        ):
            execute_signal, execute_value, status_signal, status_label = (
                self.EASY_SUSPENSION_VALUES_8797[canonical_name]
            )
            config = dict(config)
            config.update({
                "execute_cmd": (
                    f"adb shell vapisend -set {execute_signal} {execute_value}"
                ),
                "result_cmds": [
                    (
                        status_label,
                        f"adb shell vapisend -get {status_signal}",
                    ),
                    *[
                        (label, f"adb shell vapisend -get {signal}")
                        for label, signal
                        in self.EASY_SUSPENSION_HEIGHT_RESULT_COMMANDS_8797
                    ],
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.HYBRID_MODE_VALUES_8797
        ):
            signal, value = self.HYBRID_MODE_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "result_cmds": [
                    (
                        "强制纯电状态",
                        f"adb shell vapisend -get {signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.EXTREME_PASS_VALUES_8797
        ):
            signal, value = self.EXTREME_PASS_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "result_cmds": [
                    (
                        "极限通过状态",
                        f"adb shell vapisend -get {signal}",
                    ),
                    *[
                        (label, f"adb shell vapisend -get {height_signal}")
                        for label, height_signal
                        in self.EASY_SUSPENSION_HEIGHT_RESULT_COMMANDS_8797
                    ],
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.MIRROR_HEATING_VALUES_8797
        ):
            signal, value = self.MIRROR_HEATING_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "result_cmds": [
                    (
                        "后视镜加热状态",
                        f"adb shell vapisend -get {signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.STEERING_WHEEL_HEATING_VALUES_8797
        ):
            signal, value = self.STEERING_WHEEL_HEATING_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "result_cmds": [
                    (
                        "方向盘加热状态",
                        f"adb shell vapisend -get {signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8295"
            and canonical_name == self.ELECTRIC_STEERING_WHEEL_POSITION_INSTRUCTION_NAME_8797
        ):
            config = dict(config)
            config.pop("execute_cmd", None)
            config.update({
                "wait_seconds": 0,
                "result_cmds": [
                    (
                        "\u7535\u52a8\u65b9\u5411\u76d8\u4f4d\u7f6e",
                        self.ELECTRIC_STEERING_WHEEL_POSITION_READ_COMMAND_8295,
                    )
                ],
                "parse_key_values": True,
                "result_parser": "electric_steering_wheel_position",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name == self.ELECTRIC_STEERING_WHEEL_POSITION_INSTRUCTION_NAME_8797
        ):
            config = dict(config)
            config.pop("execute_cmd", None)
            config.update({
                "wait_seconds": 0,
                "result_cmds": [
                    (
                        "\u7535\u52a8\u65b9\u5411\u76d8\u4f4d\u7f6e",
                        self.ELECTRIC_STEERING_WHEEL_POSITION_READ_COMMAND_8797,
                    )
                ],
                "parse_key_values": True,
                "result_parser": "electric_steering_wheel_position",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVING_MODE_READ_COMMANDS_8797
        ):
            result_label, signal = self.DRIVING_MODE_READ_COMMANDS_8797[canonical_name]
            config = dict(config)
            config.pop("execute_cmd", None)
            config.update({
                "wait_seconds": 0,
                "result_cmds": [
                    (
                        result_label,
                        f"adb shell vapisend -get {signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
            if canonical_name == "驾驶-超级节能开关":
                config["enum_switch_active_value"] = "SUPER_ECO"
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVE_AND_LOCK_READ_COMMANDS_8797
        ):
            result_items = self.DRIVE_AND_LOCK_READ_COMMANDS_8797[canonical_name]
            config = dict(config)
            config.pop("execute_cmd", None)
            config.update({
                "wait_seconds": 0,
                "result_cmds": [
                    (
                        result_label,
                        f"adb shell vapisend -get {signal}",
                    )
                    for result_label, signal in result_items
                ],
                "result_parser": "sigval_value",
            })
            if canonical_name == "驾驶-强制纯电开关":
                config["enum_switch_active_value"] = "FORCE_EV"
        elif self.vehicle_platform == "8797" and canonical_name == "踩刹车":
            config = dict(config)
            config.update({
                "result_cmds": [
                    (
                        "电源模式",
                        "adb shell vapisend -get Vehicle.LowVoltageSystemState",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "车窗全开":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Door.WindowLazyModeControl AUTO_DOWN"
                ),
                "result_cmds": [
                    (
                        "左前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position",
                    ),
                    (
                        "右前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position",
                    ),
                    (
                        "左后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.DriverSide.Window.Position",
                    ),
                    (
                        "右后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "车窗全关":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Door.WindowLazyModeControl AUTO_UP"
                ),
                "wait_seconds": 5,
                "tolerance": 3,
                "result_cmds": [
                    (
                        "左前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position",
                    ),
                    (
                        "右前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position",
                    ),
                    (
                        "左后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.DriverSide.Window.Position",
                    ),
                    (
                        "右后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "车窗通风":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Door.WindowLazyModeControl AERATION"
                ),
                "wait_seconds": 5,
                "tolerance": 3,
                "result_cmds": [
                    (
                        "左前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position",
                    ),
                    (
                        "右前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position",
                    ),
                    (
                        "左后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.DriverSide.Window.Position",
                    ),
                    (
                        "右后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "车窗状态":
            config = dict(config)
            config.update({
                "tolerance": 3,
                "result_cmds": [
                    (
                        "左前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position",
                    ),
                    (
                        "右前车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position",
                    ),
                    (
                        "左后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.DriverSide.Window.Position",
                    ),
                    (
                        "右后车窗状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "打开后备箱":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Body.Trunk.Rear.Control OPEN"
                ),
                "result_cmds": [
                    (
                        "后备箱位置状态",
                        "adb shell vapisend -get Vehicle.Body.Trunk.Rear.Position",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "关闭后备箱":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Body.Trunk.Rear.Control CLOSE"
                ),
                "result_cmds": [
                    (
                        "后备箱位置状态",
                        "adb shell vapisend -get Vehicle.Body.Trunk.Rear.Position",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "打开空调":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.IsAirConditioningActive true"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "空调开关状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsAirConditioningActive",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "关闭空调":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.IsAirConditioningActive false"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "空调开关状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsAirConditioningActive",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "空调打开AC":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.IsCompressorActive true"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "AC状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsCompressorActive",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "空调关闭AC":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.IsCompressorActive false"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "AC状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsCompressorActive",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "打开前排空调Auto模式":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.Station.Row1.IsAutoModeActive true"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "前排空调Auto模式状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.IsAutoModeActive",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "关闭前排空调Auto模式":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.Station.Row1.IsAutoModeActive false"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "前排空调Auto模式状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.IsAutoModeActive",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "空调打开温度同步":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.IsDualZoneSyncActive true"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "主驾温度状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature",
                    ),
                    (
                        "副驾温度状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif self.vehicle_platform == "8797" and canonical_name == "空调关闭温度同步":
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.IsDualZoneSyncActive false"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "主驾温度状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature",
                    ),
                    (
                        "副驾温度状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_TEMPERATURE_INSTRUCTION_NAMES_8797
        ):
            temperature_label = canonical_name.rsplit("-", 1)[-1]
            if temperature_label == "Lo":
                temperature_value = "15.5"
            elif temperature_label == "High":
                temperature_value = "32.5"
            else:
                temperature_value = temperature_label.removesuffix("度")

            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature "
                    f"{temperature_value}"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "主驾空调温度状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_TEMPERATURE_INSTRUCTION_NAMES_8797
        ):
            temperature_label = canonical_name.rsplit("-", 1)[-1]
            if temperature_label == "Lo":
                temperature_value = "15.5"
            elif temperature_label == "High":
                temperature_value = "32.5"
            else:
                temperature_value = temperature_label.removesuffix("度")

            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature "
                    f"{temperature_value}"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "副驾空调温度状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.FRONT_FAN_LEVEL_INSTRUCTION_NAMES_8797
        ):
            level_label = canonical_name.rsplit("风量", 1)[-1]
            level_value = "11" if level_label == "MAX挡" else level_label.removesuffix("挡")

            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.Station.Row1.FanSpeedLevel "
                    f"{level_value}"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "前排风量挡位",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.FanSpeedLevel",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RECIRCULATION_MODE_VALUES_8797
        ):
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.HVAC.RecirculationMode "
                    f"{self.RECIRCULATION_MODE_VALUES_8797[canonical_name]}"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "空调循环模式",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.RecirculationMode",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.REAR_HVAC_VALUES_8797
        ):
            signal_name, value = self.REAR_HVAC_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    f"adb shell vapisend -set {signal_name} {value}"
                ),
                "wait_seconds": 1,
                "result_cmds": [
                    (
                        "后排空调开关状态",
                        f"adb shell vapisend -get {signal_name}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.HVAC_SWITCH_VALUES_8797
        ):
            signal_name, value = self.HVAC_SWITCH_VALUES_8797[canonical_name]
            if canonical_name in {
                "打开空调经济模式",
                "打开空调自动模式",
            }:
                result_cmds = [
                    (
                        "空调经济模式状态"
                        if canonical_name == "打开空调经济模式"
                        else "空调自动模式状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsEconomyModeActive",
                    ),
                    (
                        "空调风量状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.FanSpeedLevel",
                    ),
                ]
            elif canonical_name == "打开后排空调自动模式":
                result_cmds = [
                    (
                        "后排空调自动模式状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row2.IsAutoModeActive",
                    ),
                    (
                        "后排空调风量状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row2.FanSpeedLevel",
                    ),
                ]
            elif "极速降温" in canonical_name:
                result_cmds = [
                    (
                        "极速降温开关状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsMaxCoolingActive",
                    ),
                    (
                        "空调风量状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.FanSpeedLevel",
                    ),
                    (
                        "空调主驾温度",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature",
                    ),
                    (
                        "空调副驾温度",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature",
                    ),
                ]
            elif "极速升温" in canonical_name:
                result_cmds = [
                    (
                        "极速升温开关状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.IsMaxHeatingActive",
                    ),
                    (
                        "空调风量状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.FanSpeedLevel",
                    ),
                    (
                        "空调主驾温度",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature",
                    ),
                    (
                        "空调副驾温度",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature",
                    ),
                ]
            else:
                result_cmds = [
                    (
                        "后控制屏童锁状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.HVAC.Rear.ControlPanel.LockedRequest",
                    )
                ]

            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal_name} {value}",
                "wait_seconds": 1,
                "result_cmds": result_cmds,
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and (
                canonical_name in self.MIRROR_SHADE_VALUES_8797
                or canonical_name == self.FOLD_MIRROR_INSTRUCTION_NAME_8797
                or canonical_name == self.UNFOLD_MIRROR_INSTRUCTION_NAME_8797
                or canonical_name == self.FOLDED_MIRROR_STATUS_INSTRUCTION_NAME_8797
                or canonical_name == self.UNFOLDED_MIRROR_STATUS_INSTRUCTION_NAME_8797
                or canonical_name in self.MIRROR_STATUS_INSTRUCTION_NAMES_8797
                or canonical_name in self.EXECUTABLE_SHADE_INSTRUCTION_NAMES_8797
            )
        ):
            if canonical_name == self.FOLD_MIRROR_INSTRUCTION_NAME_8797:
                execute_signal = "Vehicle.Body.Mirrors.FoldRequest"
                execute_value = "FOLD"
                result_signal = "Vehicle.Body.Mirrors.FoldStatus"
                result_label = "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001"
            elif canonical_name == self.UNFOLD_MIRROR_INSTRUCTION_NAME_8797:
                execute_signal = "Vehicle.Body.Mirrors.FoldRequest"
                execute_value = "UNFOLD"
                result_signal = "Vehicle.Body.Mirrors.FoldStatus"
                result_label = "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001"
            elif canonical_name in self.MIRROR_STATUS_INSTRUCTION_NAMES_8797:
                execute_signal = None
                execute_value = None
                result_signal = "Vehicle.Body.Mirrors.FoldStatus"
                result_label = "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001"
            elif canonical_name == self.FOLDED_MIRROR_STATUS_INSTRUCTION_NAME_8797:
                execute_signal = None
                execute_value = None
                result_signal = "Vehicle.Body.Mirrors.FoldStatus"
                result_label = "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001"
            elif canonical_name == self.UNFOLDED_MIRROR_STATUS_INSTRUCTION_NAME_8797:
                execute_signal = None
                execute_value = None
                result_signal = "Vehicle.Body.Mirrors.FoldStatus"
                result_label = "\u540e\u89c6\u955c\u6298\u53e0\u72b6\u6001"
            elif canonical_name in self.REAR_SHADE_INSTRUCTION_NAMES_8797:
                execute_signal = "Vehicle.Cabin.RearShade.AutoAdjust"
                execute_value = (
                    "AUTO_OPEN"
                    if canonical_name.startswith("\u6253\u5f00")
                    else "AUTO_CLOSE"
                )
                result_signal = "Vehicle.Cabin.RearShade.Position"
                result_label = "\u540e\u906e\u9633\u5e18\u4f4d\u7f6e"
            elif canonical_name in self.FRONT_SHADE_INSTRUCTION_NAMES_8797:
                execute_signal = "Vehicle.Cabin.Sunroof.Shade.AutoAdjust"
                execute_value = (
                    "AUTO_OPEN"
                    if canonical_name.startswith("\u6253\u5f00")
                    else "AUTO_CLOSE"
                )
                result_signal = "Vehicle.Cabin.Sunroof.Shade.Position"
                result_label = "\u524d\u906e\u9633\u5e18\u4f4d\u7f6e"
            else:
                execute_signal, execute_value, result_signal, result_label = (
                    self.MIRROR_SHADE_VALUES_8797[canonical_name]
                )
            config = dict(config)
            config.update({
                "result_cmds": [
                    (
                        result_label,
                        f"adb shell vapisend -get {result_signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
            if execute_signal:
                config["execute_cmd"] = (
                    f"adb shell vapisend -set {execute_signal} {execute_value}"
                )
            else:
                config.pop("execute_cmd", None)
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_SEAT_POSITION_VALUES_8797
        ):
            restore_value = self.DRIVER_SEAT_POSITION_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row1.DriverSide.PositionMemory.Restore "
                    f"{restore_value}"
                ),
                "result_cmds": [
                    ("前后位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.PositionPercent"),
                    ("上下位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.HeightPercent"),
                    ("抬升位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.LegSupport.FoldPosition"),
                    ("靠背位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.ReclinePercent"),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_POSITION_VALUES_8797
        ):
            restore_value, wait_seconds = (
                self.PASSENGER_SEAT_POSITION_VALUES_8797[canonical_name]
            )
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row1.PassengerSide.PositionMemory.Restore "
                    f"{restore_value}"
                ),
                "wait_seconds": wait_seconds,
                "result_cmds": [
                    ("前后位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.PositionPercent"),
                    ("上下位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.HeightPercent"),
                    ("抬升位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.LegSupport.FoldPosition"),
                    ("靠背位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.ReclinePercent"),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and (
                canonical_name in self.PASSENGER_SEAT_HEATING_VALUES_8797
                or canonical_name in self.PASSENGER_SEAT_HEATING_LEVEL_NAMES_8797
                or canonical_name == self.PASSENGER_SEAT_HEATING_OFF_NAME_8797
            )
        ) or (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_VENTILATION_VALUES_8797
        ):
            is_heating = (
                canonical_name in self.PASSENGER_SEAT_HEATING_VALUES_8797
                or canonical_name in self.PASSENGER_SEAT_HEATING_LEVEL_NAMES_8797
            )
            values = (
                {
                    **self.PASSENGER_SEAT_HEATING_VALUES_8797,
                    **self.PASSENGER_SEAT_HEATING_LEVEL_NAMES_8797,
                }
                if is_heating
                else self.PASSENGER_SEAT_VENTILATION_VALUES_8797
            )
            signal_suffix = "HeatingLevel" if is_heating else "VentilationLevel"
            result_label = "副驾座椅加热状态" if is_heating else "副驾座椅通风状态"
            value = values[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    f"Vehicle.Cabin.Seat.Row1.PassengerSide.{signal_suffix} {value}"
                ),
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        result_label,
                        "adb shell vapisend -get "
                        f"Vehicle.Cabin.Seat.Row1.PassengerSide.{signal_suffix}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_CLIMATE_NAMES_8797
        ):
            value = self.PASSENGER_SEAT_HEATING_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row1.PassengerSide.HeatingLevel "
                    f"{value}"
                ),
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        "副驾座椅加热状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Seat.Row1.PassengerSide.HeatingLevel",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_MASSAGE_SWITCH_VALUES_8797
        ):
            suffix, value, label = self.PASSENGER_SEAT_MASSAGE_SWITCH_VALUES_8797[canonical_name]
            signal = f"Vehicle.Cabin.Seat.Row1.PassengerSide.{suffix}"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [(label, f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_MASSAGE_INTENSITY_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row1.PassengerSide.MassageIntensity"
            value = self.PASSENGER_SEAT_MASSAGE_INTENSITY_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("副驾座椅按摩强度状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_MASSAGE_AREA_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row1.PassengerSide.MassageArea"
            value = self.PASSENGER_SEAT_MASSAGE_AREA_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("副驾座椅按摩部位状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_MASSAGE_MODE_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row1.PassengerSide.MassageMode"
            value = self.PASSENGER_SEAT_MASSAGE_MODE_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("副驾座椅按摩模式状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.PASSENGER_SEAT_VENTILATION_VALUES_8797
        ):
            value = self.PASSENGER_SEAT_VENTILATION_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row1.PassengerSide.VentilationLevel "
                    f"{value}"
                ),
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        "副驾座椅通风状态",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Seat.Row1.PassengerSide.VentilationLevel",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_SEAT_HEATING_VALUES_8797
        ):
            value = self.DRIVER_SEAT_HEATING_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set Vehicle.Cabin.Seat.Row1.DriverSide.HeatingLevel {value}",
                "result_cmds": [
                    ("主驾座椅加热状态", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.HeatingLevel")
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_SEAT_VENTILATION_VALUES_8797
        ):
            value = self.DRIVER_SEAT_VENTILATION_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set Vehicle.Cabin.Seat.Row1.DriverSide.VentilationLevel {value}",
                "result_cmds": [
                    ("主驾座椅通风状态", "adb shell vapisend -get Vehicle.Cabin.Seat.Row1.DriverSide.VentilationLevel")
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_SEAT_MASSAGE_VALUES_8797
        ):
            signal_suffix, value, label = self.DRIVER_SEAT_MASSAGE_VALUES_8797[canonical_name]
            signal = f"Vehicle.Cabin.Seat.Row1.DriverSide.{signal_suffix}"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "result_cmds": [(label, f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_SEAT_MASSAGE_AREA_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row1.DriverSide.MassageArea"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {self.DRIVER_SEAT_MASSAGE_AREA_VALUES_8797[canonical_name]}",
                "result_cmds": [("主驾座椅按摩部位状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.DRIVER_SEAT_MASSAGE_MODE_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row1.DriverSide.MassageMode"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {self.DRIVER_SEAT_MASSAGE_MODE_VALUES_8797[canonical_name]}",
                "result_cmds": [("主驾座椅按摩模式状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.LEFT_REAR_SEAT_CLIMATE_VALUES_8797
        ):
            signal_suffix, value = self.LEFT_REAR_SEAT_CLIMATE_VALUES_8797[canonical_name]
            is_heating = signal_suffix == "HeatingLevel"
            signal = f"Vehicle.Cabin.Seat.Row2.DriverSide.{signal_suffix}"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        "左后座椅加热状态" if is_heating else "左后座椅通风状态",
                        f"adb shell vapisend -get {signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.LEFT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.DriverSide.MassageIntensity"
            value = self.LEFT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("左后座椅按摩强度状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.LEFT_REAR_SEAT_MASSAGE_AREA_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.DriverSide.MassageArea"
            value = self.LEFT_REAR_SEAT_MASSAGE_AREA_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("左后座椅按摩部位状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.LEFT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797
        ):
            value = self.LEFT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797[canonical_name]
            signal = "Vehicle.Cabin.Seat.Row2.DriverSide.IsMassageActive"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩开关状态", f"adb shell vapisend -get {signal}")
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.LEFT_REAR_SEAT_MASSAGE_MODE_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.DriverSide.MassageMode"
            value = self.LEFT_REAR_SEAT_MASSAGE_MODE_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [
                    ("左后座椅按摩模式状态", f"adb shell vapisend -get {signal}")
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.LEFT_REAR_SEAT_FOLD_VALUES_8797
        ):
            value, wait_seconds = self.LEFT_REAR_SEAT_FOLD_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row2.DriverSide.PositionMemory.Restore "
                    f"{value}"
                ),
                "wait_seconds": wait_seconds,
                "result_cmds": [
                    ("前后位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.HorizontalPosition"),
                    ("抬升位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.TiltPercent"),
                    ("靠背位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.ReclinePercent"),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RIGHT_REAR_SEAT_CLIMATE_VALUES_8797
        ):
            suffix, value = self.RIGHT_REAR_SEAT_CLIMATE_VALUES_8797[canonical_name]
            is_heating = suffix == "HeatingLevel"
            signal = f"Vehicle.Cabin.Seat.Row2.PassengerSide.{suffix}"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        "右后座椅加热状态" if is_heating else "右后座椅通风状态",
                        f"adb shell vapisend -get {signal}",
                    )
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RIGHT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.PassengerSide.MassageIntensity"
            value = self.RIGHT_REAR_SEAT_MASSAGE_INTENSITY_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("右后座椅按摩强度状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RIGHT_REAR_SEAT_MASSAGE_AREA_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.PassengerSide.MassageArea"
            value = self.RIGHT_REAR_SEAT_MASSAGE_AREA_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("右后座椅按摩部位状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RIGHT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.PassengerSide.IsMassageActive"
            value = self.RIGHT_REAR_SEAT_MASSAGE_SWITCH_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("右后座椅按摩开关状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RIGHT_REAR_SEAT_MASSAGE_MODE_VALUES_8797
        ):
            signal = "Vehicle.Cabin.Seat.Row2.PassengerSide.MassageMode"
            value = self.RIGHT_REAR_SEAT_MASSAGE_MODE_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [("右后座椅按摩模式状态", f"adb shell vapisend -get {signal}")],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.RIGHT_REAR_SEAT_FOLD_VALUES_8797
        ):
            value, wait_seconds = self.RIGHT_REAR_SEAT_FOLD_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row2.PassengerSide.PositionMemory.Restore "
                    f"{value}"
                ),
                "wait_seconds": wait_seconds,
                "result_cmds": [
                    ("前后位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.HorizontalPosition"),
                    ("抬升位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.TiltPercent"),
                    ("靠背位置", "adb shell vapisend -get Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.ReclinePercent"),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.THIRD_ROW_LEFT_SEAT_FOLD_VALUES_8797
        ):
            value, wait_seconds = self.THIRD_ROW_LEFT_SEAT_FOLD_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row3.DriverSide.PositionMemory.Restore "
                    f"{value}"
                ),
                "wait_seconds": wait_seconds,
                "result_cmds": [
                    (
                        "\u6295\u5347\u4f4d\u7f6e",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Seat.Row3.DriverSide.TiltPercent",
                    ),
                    (
                        "\u9760\u80cc\u4f4d\u7f6e",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Seat.Row3.DriverSide.Backrest.ReclinePercent",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.THIRD_ROW_LEFT_SEAT_HEATING_VALUES_8797
        ):
            value = self.THIRD_ROW_LEFT_SEAT_HEATING_VALUES_8797[canonical_name]
            signal = "Vehicle.Cabin.Seat.Row3.DriverSide.HeatingLevel"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        "\u4e09\u6392\u5de6\u4fa7\u9a7e\u5ea7\u6905\u52a0\u70ed\u72b6\u6001",
                        f"adb shell vapisend -get {signal}",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.THIRD_ROW_RIGHT_SEAT_FOLD_VALUES_8797
        ):
            value, wait_seconds = self.THIRD_ROW_RIGHT_SEAT_FOLD_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Cabin.Seat.Row3.PassengerSide.PositionMemory.Restore "
                    f"{value}"
                ),
                "wait_seconds": wait_seconds,
                "result_cmds": [
                    (
                        "\u6295\u5347\u4f4d\u7f6e",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Seat.Row3.PassengerSide.TiltPercent",
                    ),
                    (
                        "\u9760\u80cc\u4f4d\u7f6e",
                        "adb shell vapisend -get "
                        "Vehicle.Cabin.Seat.Row3.PassengerSide.Backrest.ReclinePercent",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.THIRD_ROW_RIGHT_SEAT_HEATING_VALUES_8797
        ):
            value = self.THIRD_ROW_RIGHT_SEAT_HEATING_VALUES_8797[canonical_name]
            signal = "Vehicle.Cabin.Seat.Row3.PassengerSide.HeatingLevel"
            config = dict(config)
            config.update({
                "execute_cmd": f"adb shell vapisend -set {signal} {value}",
                "wait_seconds": 2,
                "result_cmds": [
                    (
                        "\u4e09\u6392\u53f3\u4fa7\u9a7e\u5ea7\u6905\u52a0\u70ed\u72b6\u6001",
                        f"adb shell vapisend -get {signal}",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.CHARGING_PORT_OPERATION_VALUES_8797
        ):
            value = self.CHARGING_PORT_OPERATION_VALUES_8797[canonical_name]
            config = dict(config)
            config.update({
                "execute_cmd": (
                    "adb shell vapisend -set "
                    "Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.Operation "
                    f"{value}"
                ),
                "wait_seconds": 5,
                "result_cmds": [
                    (
                        "\u5145\u7535\u5c0f\u95e8\u72b6\u6001",
                        "adb shell vapisend -get "
                        "Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.Status",
                    ),
                ],
                "result_parser": "sigval_value",
            })
        elif (
            self.vehicle_platform == "8797"
            and canonical_name in self.REAR_DISPLAY_OPERATION_VALUES_8797
        ):
            config = dict(config)
            if canonical_name == "打开后排屏":
                power_value = "1"
            elif canonical_name == "关闭后排屏":
                power_value = "0"
            else:
                power_value = None

            if power_value is not None:
                config.update({
                    "execute_cmd": (
                        "adb shell vapisend -set "
                        f"system.power.rear_screen_power_switch {power_value}"
                    ),
                    "wait_seconds": 5,
                    "result_cmds": [
                        (
                            "后排屏状态",
                            "adb shell vapisend -get "
                            "system.power.rear_screen_power_switch",
                        )
                    ],
                    "result_parser": "rear_screen_power",
                    "tolerance": 0,
                })
            else:
                value = self.REAR_DISPLAY_OPERATION_VALUES_8797[canonical_name]
                config.update({
                    "execute_cmd": (
                        "adb shell vapisend -set "
                        "Vehicle.Cabin.Infotainment.RearDisplay.ShortPress "
                        f"{value}"
                    ),
                    "wait_seconds": 5,
                    "result_cmds": [],
                    "tolerance": 0,
                })
        return config

    def _baseline_key_candidates(self, instruction_name):
        names = []
        canonical_name = self._canonical_instruction_name(instruction_name)
        baseline_name = self._baseline_instruction_name(instruction_name)
        if baseline_name == canonical_name:
            alias_names = [
                alias
                for alias, target in self.instruction_aliases.items()
                if target == canonical_name
            ]
            candidate_names = (
                canonical_name,
                str(instruction_name or "").strip(),
                *alias_names,
            )
        else:
            candidate_names = (baseline_name,)
        for name in candidate_names:
            if name and name not in names:
                names.append(name)

        keys = []
        if self.vehicle_platform == "8797" and canonical_name in {
            "C屏下电",
            "账号",
            "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001",
            "\u9884\u7ea6\u5145\u7535\u5f00\u59cb\u65f6\u95f4",
            "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u65f6\u95f4",
        }:
            platform_name = f"{self.vehicle_platform}_{canonical_name}"
            return [f"综合_{platform_name}", platform_name]
        for name in names:
            prefixed = f"综合_{name}"
            if prefixed not in keys:
                keys.append(prefixed)
            if name not in keys:
                keys.append(name)
        return keys

    def set_stop_check(self, callback):
        """设置停止检查回调，避免长时间 sleep 时压测线程无法响应停止。"""
        self.stop_check = callback

    def should_stop(self):
        """检查外部是否请求停止。"""
        if not self.stop_check:
            return False
        try:
            return bool(self.stop_check())
        except Exception:
            return False

    def interruptible_sleep(self, seconds, interval=0.2):
        """可中断等待；返回 False 表示等待过程中收到停止请求。"""
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            seconds = 0
        if seconds <= 0:
            return not self.should_stop()

        deadline = time.time() + seconds
        while time.time() < deadline:
            if self.should_stop():
                return False
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            time.sleep(min(interval, remaining))
        return not self.should_stop()

    def _lastmode_value_is_ignored(self, key):
        key_lower = str(key or "").strip().lower()
        return any(marker in key_lower for marker in self.LASTMODE_CACHE_IGNORED_KEY_MARKERS)

    def _parse_lastmode_cache_file(self, file_path):
        """读取 Lastmode 缓存，只保留 isExist=true 且存在 value 的记忆项。"""
        results = {}
        try:
            with open(file_path, "r", encoding="utf-8-sig") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, raw_value = line.split("=", 1)
                    key = key.strip()
                    if not key or self._lastmode_value_is_ignored(key):
                        continue

                    # properties 文件中的 JSON 对引号和冒号做了反斜杠转义。
                    json_text = (
                        raw_value.strip()
                        .replace(r"\"", '"')
                        .replace(r"\:", ":")
                    )
                    try:
                        payload = json.loads(json_text)
                    except (TypeError, ValueError, json.JSONDecodeError):
                        continue

                    result = payload.get("result") if isinstance(payload, dict) else None
                    if not isinstance(result, dict):
                        continue
                    if result.get("isExist") is not True or "value" not in result:
                        continue

                    results[key] = self._parse_number_like(result.get("value"))
        except (OSError, UnicodeError) as exc:
            raise RuntimeError(f"读取 Lastmode 文件失败: {exc}") from exc

        return results

    def execute_lastmode_cache(self, save_folder, current_cycle=0, tolerance=0):
        """抓取并解析 Lastmode 缓存文件，返回可用于基准比较的记忆值。"""
        save_folder = os.path.normpath(str(save_folder or "").strip())
        if not save_folder:
            return None, tolerance, "未设置测试文件夹路径，无法保存 Lastmode 文件"

        try:
            os.makedirs(save_folder, exist_ok=True)
        except OSError as exc:
            return None, tolerance, f"创建 Lastmode 保存目录失败: {exc}"

        try:
            cycle = int(current_cycle)
        except (TypeError, ValueError):
            cycle = 0
        cycle = max(0, cycle)
        file_name = f"cycle{cycle}_vehicle_settings_cache.properties"
        local_path = os.path.join(save_folder, file_name)
        pull_cmd = [
            "adb",
            "pull",
            self.LASTMODE_CACHE_REMOTE_PATH,
            local_path,
        ]
        print(f"[Lastmode] 抓取文件: {' '.join(pull_cmd)}")

        try:
            result = subprocess.run(
                pull_cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
            return None, tolerance, f"抓取 Lastmode 文件失败: {exc}"

        output = "\n".join(
            part.strip()
            for part in (result.stdout, result.stderr)
            if part and part.strip()
        )
        if result.returncode != 0 or not os.path.isfile(local_path):
            return None, tolerance, (
                f"抓取 Lastmode 文件失败: {output or '文件未生成'}"
            )

        try:
            results = self._parse_lastmode_cache_file(local_path)
        except RuntimeError as exc:
            return None, tolerance, str(exc)
        if not results:
            return None, tolerance, (
                f"Lastmode 文件没有可比较的记忆值: {local_path}"
            )

        print(f"[Lastmode] 已保存: {local_path}")
        print(f"[Lastmode] 可比较记忆项: {len(results)}")
        return results, tolerance, None

    def run_adb_cmd(self, cmd):
        """执行adb命令，从返回的JSON中提取 sigVal 的值
        支持正数、负数、零
        """
        import json
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            output = "\n".join(
                part.strip()
                for part in (result.stdout, result.stderr)
                if part and part.strip()
            )

            if result.returncode != 0:
                print(f"命令失败: {cmd}\n返回码: {result.returncode}\n输出: {output}")
                return None

            if not output:
                print(f"⚠️  命令无输出: {cmd}")
                return None
            
            # 方法1: 匹配 sigVal 后面的数字（支持小数和负数）
            match = re.search(r'sigVal[^0-9.-]*(-?\d+(?:\.\d+)?)', output)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)

            # 方法2: 兼容 JSON 返回，例如 {"sigVal": 1} / {"value": 1}
            for json_text in re.findall(r'\{.*?\}', output, flags=re.S):
                try:
                    payload = json.loads(json_text)
                except Exception:
                    continue
                value = self._extract_numeric_from_json(payload)
                if value is not None:
                    return value
            
            # 方法3: 如果没找到，再尝试 value 字段（兼容旧格式，支持小数和负数）
            match = re.search(r'vapisend -get value:\s*(-?\d+(?:\.\d+)?)', output)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)

            # 方法4: 兼容普通 value/sig_value 字段
            match = re.search(r'(?:value|sig_value|sigValue)\s*[:=]\s*["\']?(-?\d+(?:\.\d+)?)', output, re.IGNORECASE)
            if match:
                val_str = match.group(1)
                return float(val_str) if '.' in val_str else int(val_str)

            # 方法5: 输出整体只有一个数字时直接返回
            if re.fullmatch(r'\s*-?\d+(?:\.\d+)?\s*', output):
                return float(output) if '.' in output else int(output)
            
            print(f"⚠️  无法解析返回值: {output}")
            return None
        except Exception as e:
            print(f"命令失败: {cmd}\n错误: {e}")
            return None

    def _extract_numeric_from_json(self, payload):
        if isinstance(payload, dict):
            for key in ("sigVal", "value", "sig_value", "sigValue", "data"):
                if key not in payload:
                    continue
                value = payload.get(key)
                if isinstance(value, (int, float)):
                    return value
                if isinstance(value, str):
                    text = value.strip()
                    if re.fullmatch(r'-?\d+(?:\.\d+)?', text):
                        return float(text) if '.' in text else int(text)
                nested = self._extract_numeric_from_json(value)
                if nested is not None:
                    return nested
            for value in payload.values():
                nested = self._extract_numeric_from_json(value)
                if nested is not None:
                    return nested
        elif isinstance(payload, list):
            for item in payload:
                nested = self._extract_numeric_from_json(item)
                if nested is not None:
                    return nested
        return None

    def _parse_number_like(self, value):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            text = value.strip()
            if re.fullmatch(r'-?\d+(?:\.\d+)?', text):
                return float(text) if "." in text else int(text)
            return text
        return value

    def _iter_json_objects_from_text(self, text):
        decoder = json.JSONDecoder()
        raw = self._strip_ansi_sequences(text)
        for match in re.finditer(r'\{', raw):
            try:
                payload, _end = decoder.raw_decode(raw[match.start():])
            except Exception:
                continue
            yield payload

    def _try_json_loads(self, value):
        if not isinstance(value, str):
            return None
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            pass
        try:
            return json.loads(text.encode("utf-8").decode("unicode_escape"))
        except Exception:
            return None

    def _collect_sigval_payloads(self, payload, depth=0):
        if depth > 8:
            return []
        found = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                if str(key).lower() == "sigval":
                    found.append(value)
                found.extend(self._collect_sigval_payloads(value, depth + 1))
        elif isinstance(payload, list):
            for item in payload:
                found.extend(self._collect_sigval_payloads(item, depth + 1))
        elif isinstance(payload, str):
            nested = self._try_json_loads(payload)
            if nested is not None:
                found.extend(self._collect_sigval_payloads(nested, depth + 1))
                if isinstance(nested, dict):
                    found.append(nested)
        return found

    def _collect_json_field_values(self, payload, field_name, depth=0):
        if depth > 8:
            return []
        values = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                if str(key).lower() == field_name.lower():
                    values.append(value)
                values.extend(
                    self._collect_json_field_values(value, field_name, depth + 1)
                )
        elif isinstance(payload, list):
            for item in payload:
                values.extend(
                    self._collect_json_field_values(item, field_name, depth + 1)
                )
        elif isinstance(payload, str):
            nested = self._try_json_loads(payload)
            if nested is not None:
                values.extend(
                    self._collect_json_field_values(nested, field_name, depth + 1)
                )
        return values

    def _extract_fields_from_payload(self, payload, fields):
        if not isinstance(payload, dict):
            nested = self._try_json_loads(payload)
            if isinstance(nested, dict):
                payload = nested
            else:
                return {}
        result = {}
        for field in fields:
            if field in payload:
                result[field] = self._parse_number_like(payload.get(field))
        return result

    def _parse_sigval_json_fields(self, output, fields):
        fields = [str(field).strip() for field in (fields or []) if str(field).strip()]
        if not fields:
            return None

        candidates = []
        for payload in self._iter_json_objects_from_text(output):
            candidates.append(payload)
            candidates.extend(self._collect_sigval_payloads(payload))

        for candidate in candidates:
            values = self._extract_fields_from_payload(candidate, fields)
            if all(field in values for field in fields):
                return {field: values[field] for field in fields}

        text = self._strip_ansi_sequences(output)
        unescaped = text.replace(r'\"', '"').replace(r'\n', '\n')
        values = {}
        for field in fields:
            match = re.search(
                rf'["\\]*{re.escape(field)}["\\]*\s*:\s*["\']?(-?\d+(?:\.\d+)?)',
                unescaped
            )
            if match:
                values[field] = self._parse_number_like(match.group(1))
        if all(field in values for field in fields):
            return {field: values[field] for field in fields}
        return None

    def run_adb_sigval_json_fields_cmd(self, cmd, config=None):
        config = config or {}
        timeout = float(config.get("read_timeout", 10))
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = "\n".join(
                part.strip()
                for part in (result.stdout, result.stderr)
                if part and part.strip()
            )
            if result.returncode != 0:
                print(f"命令失败: {cmd}\n返回码: {result.returncode}\n输出: {output}")
                return None
            values = self._parse_sigval_json_fields(output, config.get("sigval_fields"))
            if values:
                return values
            print(f"⚠️  无法解析 sigVal JSON 字段: {output}")
            return None
        except Exception as e:
            print(f"命令失败: {cmd}\n错误: {e}")
            return None

    def _result_cmd_parts(self, item):
        """兼容 tuple 和 ITMS 风格 dict 的 result_cmd 配置。"""
        if isinstance(item, dict):
            return str(item.get("label") or "").strip(), str(item.get("command") or "").strip()
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            return str(item[0]).strip(), str(item[1]).strip()
        return "", ""

    def _normalize_process_output(self, text):
        if text is None:
            return ""
        if isinstance(text, bytes):
            for encoding in ("utf-8", "gbk", "latin-1"):
                try:
                    return text.decode(encoding, errors="replace")
                except Exception:
                    continue
            return text.decode(errors="replace")
        return str(text)

    def _strip_ansi_sequences(self, text):
        return re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', self._normalize_process_output(text))

    def _key_sort_value(self, value):
        return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', str(value or ''))]

    def _command_value_labels(self, config):
        if not isinstance(config, dict):
            return []
        labels = [
            str(item).strip()
            for item in config.get("value_labels", [])
            if str(item).strip()
        ]
        if labels:
            return labels
        return []

    def _command_value_key_prefixes(self, config):
        if not isinstance(config, dict):
            return []
        raw = config.get("value_key_prefixes")
        if raw is None:
            raw = config.get("value_key_prefix")
        if isinstance(raw, str):
            values = [raw]
        elif isinstance(raw, list):
            values = raw
        else:
            return []
        return [str(item).strip() for item in values if str(item).strip()]

    def _split_js_value_comment(self, value):
        text = str(value if value is not None else "").strip()
        while text.endswith(";"):
            text = text[:-1].strip()
        if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
            text = text[1:-1].strip()

        search_from = 0
        while True:
            comment_index = text.find("//", search_from)
            if comment_index < 0:
                return text, ""
            if comment_index > 0 and text[comment_index - 1] == ":":
                search_from = comment_index + 2
                continue
            comment = text[comment_index + 2:].strip()
            while comment.startswith("/"):
                comment = comment[1:].strip()
            return text[:comment_index].strip(), comment

    def _normalize_voice_setting_value(self, value):
        text, _comment = self._split_js_value_comment(value)

        switch_match = re.search(r'/Switch[^/]*/(ON|OFF)(?:/|$)', text, flags=re.I)
        if switch_match:
            return switch_match.group(1).upper()
        if text.upper() in ("ON", "OFF"):
            return text.upper()
        if re.fullmatch(r'#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', text):
            return text.upper()
        if text.lower().startswith("page://"):
            return re.sub(r'(/caf_images/)[^/]+/', r'\1{theme}/', text, flags=re.I)
        return text

    _JS_DISPLAY_THEME_COLOR_MAP = {
        "#FCFCFFDB": "TEXT_SELECTED",
        "#01091ADB": "TEXT_SELECTED",
        "#FCFCFF99": "TEXT_UNSELECTED",
        "#01091A99": "TEXT_UNSELECTED",
        "#83634EFF": "CARD_SELECTED",
        "#FCFCFFFF": "CARD_SELECTED",
        "#FFE9DC14": "CARD_UNSELECTED",
        "#383A4C14": "CARD_UNSELECTED",
    }

    def _normalize_display_setting_value(self, value, key=None):
        normalized = self._normalize_voice_setting_value(value)
        if isinstance(normalized, str):
            return self._JS_DISPLAY_THEME_COLOR_MAP.get(normalized.upper(), normalized)
        return normalized

    def _normalize_speech_setting_value(self, value, key=None):
        normalized = self._normalize_voice_setting_value(value)
        if isinstance(normalized, str):
            upper = normalized.upper()
            value_key = str(key or "").strip()
            if value_key in {"voice6", "voice7", "voice8", "voice9"}:
                if upper in {"#83634EFF", "#FCFCFFFF"}:
                    return "CARD_SELECTED"
                if upper in {"#FFE9DC14", "#383A4C14"}:
                    return "CARD_UNSELECTED"
            if value_key in {"voice10", "voice11", "voice12", "voice13", "voice14", "voice15", "voice16", "voice17"}:
                if upper in {"#FCFCFFDB", "#01091ADB"}:
                    return "TEXT_SELECTED"
                if upper in {"#FCFCFF99", "#01091A99"}:
                    return "TEXT_UNSELECTED"
            return normalized
        return normalized

    def _normalize_pilot_setting_value(self, value, key=None):
        normalized = self._normalize_voice_setting_value(value)
        if isinstance(normalized, str):
            upper = normalized.upper()
            if str(key or "").strip() in {"Plt1", "Plt2", "Plt3"}:
                if upper in {"#FCFCFFDB", "#01091ADB"}:
                    return "TEXT_SELECTED"
                if upper in {"#FCFCFF99", "#01091A99"}:
                    return "TEXT_UNSELECTED"
            return normalized
        return normalized

    def _normalize_connection_setting_value(self, value, key=None):
        normalized = self._normalize_voice_setting_value(value)
        if isinstance(normalized, str):
            upper = normalized.upper()
            if str(key or "").strip() in {"Con4", "Con5"}:
                if upper in {"#FCFCFFDB", "#01091ADB"}:
                    return "TEXT_SELECTED"
                if upper in {"#FCFCFF99", "#01091A99"}:
                    return "TEXT_UNSELECTED"
            return normalized
        return normalized

    def _normalize_sound_setting_value(self, value, key=None):
        normalized = self._normalize_voice_setting_value(value)
        if isinstance(normalized, str):
            rectangle_match = re.fullmatch(
                r'Rectangle\(\s*(-?\d+)\s*,\s*(-?\d+)\s*-\s*(-?\d+)\s*,\s*(-?\d+)\s*\)',
                normalized,
                flags=re.I,
            )
            if rectangle_match:
                return f"RECT_X:{rectangle_match.group(1)}-{rectangle_match.group(3)}"
            upper = normalized.upper()
            value_key = str(key or "").strip()
            if value_key in {"Snd23", "Snd24"}:
                if upper in {"#01091ADB", "#FCFCFFDB"}:
                    return "TEXT_SELECTED"
                if upper in {"#01091A99", "#FCFCFF99"}:
                    return "TEXT_UNSELECTED"
            if value_key in {"Snd7", "Snd8", "Snd9", "Snd10", "Snd11", "Snd12"}:
                if upper in {"#FCFCFFDB", "#FFE9DC14"}:
                    return "SOUND_OPTION_UNSELECTED"
                if upper in {"RGBA(204,132,92,0.86)", "#A46A4199"}:
                    return "SOUND_OPTION_SELECTED"
            return normalized
        return normalized

    def _normalize_js_setting_value(self, value, value_normalizer=None, key=None):
        if value_normalizer == "speech_settings":
            return self._normalize_speech_setting_value(value, key)
        if value_normalizer == "pilot_settings":
            return self._normalize_pilot_setting_value(value, key)
        if value_normalizer == "connection_settings":
            return self._normalize_connection_setting_value(value, key)
        if value_normalizer == "sound_settings":
            return self._normalize_sound_setting_value(value, key)
        if value_normalizer == "display_settings":
            return self._normalize_display_setting_value(value, key)
        if value_normalizer in ("voice_settings", "js_settings"):
            return self._normalize_voice_setting_value(value)
        return value

    def _normalize_key_value(self, value, config, key=None):
        text = str(value if value is not None else "").strip()
        while text.endswith(";"):
            text = text[:-1].strip()
        if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
            text = text[1:-1].strip()
        normalizer = config.get("value_normalizer") if isinstance(config, dict) else None
        if normalizer in (
            "speech_settings",
            "pilot_settings",
            "connection_settings",
            "sound_settings",
            "display_settings",
            "voice_settings",
            "js_settings",
        ):
            normalized = self._normalize_js_setting_value(text, normalizer, key)
            if config.get("keep_value_comment", config.get("parse_key_values", False)):
                _raw_value, comment = self._split_js_value_comment(text)
                if comment:
                    return f"{normalized}//{comment}"
            return normalized
        return text

    def _normalize_compare_value(self, value, value_normalizer=None, key=None):
        return self._normalize_js_setting_value(value, value_normalizer, key)

    def _parse_key_value_output(self, raw, config):
        values = {}
        text = self._strip_ansi_sequences(raw)
        labels = self._command_value_labels(config)
        key_prefixes = self._command_value_key_prefixes(config)

        entries = []
        current = ""
        for raw_line in text.replace('\r\n', '\n').split('\n'):
            line = raw_line.strip()
            if not line or (set(line) <= {'-'} and len(line) >= 8):
                continue
            if re.search(r'^[A-Za-z_][A-Za-z0-9_.-]*\s*=', line):
                if current:
                    entries.append(current)
                current = line
            elif current:
                current += line
            else:
                entries.append(line)
            if current and ";" in current:
                entries.append(current)
                current = ""
        if current:
            entries.append(current)

        for entry in entries:
            for match in re.finditer(r'([A-Za-z_][A-Za-z0-9_.-]*)\s*=\s*([^;]*;?)', entry):
                key = match.group(1).strip()
                if key_prefixes:
                    matched_prefix = next(
                        (prefix for prefix in key_prefixes if key.lower().startswith(prefix.lower())),
                        None
                    )
                    if not matched_prefix:
                        continue
                    key = matched_prefix + key[len(matched_prefix):]
                if labels and key not in labels:
                    continue
                if key in values:
                    del values[key]
                values[key] = self._normalize_key_value(match.group(2), config, key)

        if labels:
            ordered_values = {label: values[label] for label in labels if label in values}
            missing = [label for label in labels if label not in values]
            expected = labels
        else:
            ordered_keys = sorted(values.keys(), key=self._key_sort_value)
            ordered_values = {key: values[key] for key in ordered_keys}
            missing = []
            expected = ordered_keys

        return {
            "values": ordered_values,
            "missing": missing,
            "expected": expected,
            "ok": bool(ordered_values) and not missing
        }

    def _run_capture_command(self, capture_cmd, timeout):
        proc = None
        popen_kwargs = {}
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            popen_kwargs["startupinfo"] = startupinfo
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            use_shell = isinstance(capture_cmd, str)
            proc = subprocess.Popen(
                capture_cmd,
                shell=use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **popen_kwargs
            )
            stdout, stderr = proc.communicate(timeout=timeout)
            output = "\n".join(
                part.strip()
                for part in (self._normalize_process_output(stdout), self._normalize_process_output(stderr))
                if part and part.strip()
            )
            return proc.returncode, output
        except subprocess.TimeoutExpired as e:
            if proc is not None and proc.poll() is None:
                try:
                    if os.name == "nt" and isinstance(capture_cmd, str):
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                            capture_output=True,
                            timeout=3,
                            **popen_kwargs
                        )
                    else:
                        proc.kill()
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            try:
                stdout, stderr = proc.communicate(timeout=3) if proc is not None else ("", "")
            except Exception:
                stdout, stderr = (
                    getattr(e, "stdout", None) or getattr(e, "output", None),
                    getattr(e, "stderr", None)
                )
            output = "\n".join(
                part.strip()
                for part in (self._normalize_process_output(stdout), self._normalize_process_output(stderr))
                if part and part.strip()
            )
            return -1, output
        except Exception as e:
            return -1, str(e)

    def _terminate_process(self, proc, popen_kwargs=None):
        if proc is None or proc.poll() is not None:
            return
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    timeout=3,
                    **(popen_kwargs or {})
                )
            except Exception:
                pass
            try:
                proc.wait(timeout=1)
            except Exception:
                pass
        if proc.poll() is not None:
            return
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            pass
        if proc.poll() is not None:
            return
        try:
            proc.kill()
            proc.wait(timeout=1)
        except Exception:
            pass

    def _cleanup_remote_node_script(self, cmd):
        text = str(cmd or "")
        match = re.search(r'node\s+--output-console\s+([^\s;&|]+\.js)', text)
        if not match:
            return
        script_path = match.group(1).strip().strip('"\'')
        if not script_path.startswith("/"):
            return
        script_path = script_path.replace("'", "'\\''")
        cleanup_cmd = f'adb -host shell "pkill -f \'{script_path}\' >/dev/null 2>&1 || true"'
        try:
            subprocess.run(cleanup_cmd, shell=True, capture_output=True, text=True, timeout=5)
        except Exception:
            pass

    def _key_value_script_error_detected(self, output):
        text = self._strip_ansi_sequences(output)
        if "UiObjectNotFoundException" in text:
            return True
        return bool(re.search(
            r'(^|\n)\s*(?:Error|TypeError|ReferenceError|SyntaxError|RangeError|EvalError|URIError):',
            text
        ))

    def _run_key_value_capture_command(self, capture_cmd, config, timeout):
        import queue
        import threading

        proc = None
        popen_kwargs = {}
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            popen_kwargs["startupinfo"] = startupinfo
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        output_queue = queue.Queue()

        def reader(pipe):
            try:
                while True:
                    chunk = os.read(pipe.fileno(), 4096)
                    if not chunk:
                        break
                    output_queue.put(self._normalize_process_output(chunk))
            except Exception:
                pass

        try:
            use_shell = isinstance(capture_cmd, str)
            proc = subprocess.Popen(
                capture_cmd,
                shell=use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **popen_kwargs
            )

            for pipe in (proc.stdout, proc.stderr):
                thread = threading.Thread(target=reader, args=(pipe,), daemon=True)
                thread.start()

            labels = self._command_value_labels(config)
            try:
                quiet_seconds = float(config.get("key_value_quiet_seconds", 0.8))
            except Exception:
                quiet_seconds = 0.8
            try:
                max_collect_seconds = float(config.get("key_value_max_collect_seconds", 2.5))
            except Exception:
                max_collect_seconds = 2.5

            deadline = time.time() + max(1.0, float(timeout or 35))
            first_match_time = None
            last_match_time = None
            output_parts = []
            final_values = None
            final_missing = []

            while True:
                if self.should_stop():
                    self._terminate_process(proc, popen_kwargs)
                    return -1, "".join(output_parts), None, ["测试已停止"]

                chunk = None
                try:
                    chunk = output_queue.get(timeout=0.1)
                except queue.Empty:
                    pass

                if chunk:
                    output_parts.append(chunk)
                    current_output = "".join(output_parts)
                    if self._key_value_script_error_detected(current_output):
                        self._terminate_process(proc, popen_kwargs)
                        return -1, current_output, None, ["JS脚本报错"]
                    parsed = self._parse_key_value_output(current_output, config)
                    values = parsed.get("values") or {}
                    missing = parsed.get("missing") or []
                    if values:
                        final_values = values
                        final_missing = missing
                        now = time.time()
                        if first_match_time is None:
                            first_match_time = now
                        last_match_time = now
                        if labels and not missing:
                            self._terminate_process(proc, popen_kwargs)
                            break

                now = time.time()
                if final_values and not labels:
                    quiet_enough = last_match_time is not None and now - last_match_time >= quiet_seconds
                    collected_enough = first_match_time is not None and now - first_match_time >= max_collect_seconds
                    if quiet_enough or collected_enough:
                        self._terminate_process(proc, popen_kwargs)
                        break

                if proc.poll() is not None:
                    break

                if now >= deadline:
                    self._terminate_process(proc, popen_kwargs)
                    break

            try:
                proc.wait(timeout=3)
            except Exception:
                self._terminate_process(proc, popen_kwargs)

            drain_deadline = time.time() + 0.3
            while time.time() < drain_deadline:
                try:
                    output_parts.append(output_queue.get_nowait())
                except queue.Empty:
                    break

            output = "".join(output_parts)
            if self._key_value_script_error_detected(output):
                return proc.returncode if proc.returncode is not None else -1, output, None, ["JS脚本报错"]
            parsed = self._parse_key_value_output(output, config)
            values = parsed.get("values") or final_values
            missing = parsed.get("missing") if parsed.get("values") else final_missing
            return proc.returncode if proc.returncode is not None else -1, output, values, missing or []
        except Exception as e:
            return -1, str(e), None, []

    def _run_exit_code_capture_command(self, capture_cmd, config, timeout):
        import queue
        import threading

        proc = None
        popen_kwargs = {}
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            popen_kwargs["startupinfo"] = startupinfo
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        output_queue = queue.Queue()

        def reader(pipe):
            try:
                while True:
                    chunk = os.read(pipe.fileno(), 4096)
                    if not chunk:
                        break
                    output_queue.put(self._normalize_process_output(chunk))
            except Exception:
                pass

        try:
            use_shell = isinstance(capture_cmd, str)
            proc = subprocess.Popen(
                capture_cmd,
                shell=use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **popen_kwargs
            )

            for pipe in (proc.stdout, proc.stderr):
                thread = threading.Thread(target=reader, args=(pipe,), daemon=True)
                thread.start()

            deadline = time.time() + max(1.0, float(timeout or 300))
            output_parts = []

            while True:
                if self.should_stop():
                    self._terminate_process(proc, popen_kwargs)
                    return False, "测试已停止", "".join(output_parts)

                chunk = None
                try:
                    chunk = output_queue.get(timeout=0.1)
                except queue.Empty:
                    pass

                if chunk:
                    output_parts.append(chunk)
                    current_output = "".join(output_parts)
                    if self._key_value_script_error_detected(current_output):
                        self._terminate_process(proc, popen_kwargs)
                        return False, "JS脚本报错", current_output

                now = time.time()
                if proc.poll() is not None:
                    break

                if now >= deadline:
                    self._terminate_process(proc, popen_kwargs)
                    return False, f"执行超时({timeout:g}s)", "".join(output_parts)

            try:
                proc.wait(timeout=3)
            except Exception:
                self._terminate_process(proc, popen_kwargs)

            drain_deadline = time.time() + 0.3
            while time.time() < drain_deadline:
                try:
                    output_parts.append(output_queue.get_nowait())
                except queue.Empty:
                    break

            output = "".join(output_parts)
            if self._key_value_script_error_detected(output):
                return False, "JS脚本报错", output

            returncode = proc.returncode if proc.returncode is not None else -1
            if returncode != 0:
                return False, f"返回码={returncode}", output
            return True, "执行成功", output
        except Exception as e:
            return False, str(e), "".join(output_parts) if "output_parts" in locals() else ""

    def _adb_console_capture_cmds(self, cmd, timeout=35):
        adb_prefix = "adb -host shell "
        text = str(cmd or "").strip()
        if text.startswith(adb_prefix):
            remote_cmd = text[len(adb_prefix):].strip()
            return [
                (["adb", "-host", "shell"] + remote_cmd.split(), timeout)
            ]
        return [(text, timeout)]

    def run_adb_electric_steering_wheel_position_cmd(self, cmd, config=None):
        """Read the 8295/8797 electric steering-wheel tilt and telescope positions."""
        raw_output = self.run_adb_raw_cmd(cmd)
        if raw_output is None:
            return None

        text = self._strip_ansi_sequences(raw_output)
        tilt_match = re.search(
            r"Tilt\(up-down\)\s*=\s*(-?\d+(?:\.\d+)?)",
            text,
            flags=re.IGNORECASE,
        )
        tele_match = re.search(
            r"Tele\(front-back\)\s*=\s*(-?\d+(?:\.\d+)?)",
            text,
            flags=re.IGNORECASE,
        )
        values = {}
        if tilt_match:
            values["\u7535\u52a8\u65b9\u5411\u76d8\u4e0a\u4e0b\u4f4d\u7f6e"] = (
                self._parse_number_like(tilt_match.group(1))
            )
        if tele_match:
            values["\u7535\u52a8\u65b9\u5411\u76d8\u524d\u540e\u4f4d\u7f6e"] = (
                self._parse_number_like(tele_match.group(1))
            )
        if len(values) != 2:
            print(f"\u7535\u52a8\u65b9\u5411\u76d8\u4f4d\u7f6e\u89e3\u6790\u5931\u8d25: {text}")
            return None
        return values

    def run_adb_mirror_position_cmd(self, cmd, config=None):
        """Read four mirror position bytes from the tcpdump row at offset 0x0030."""
        try:
            result = subprocess.run(
                [
                    "adb", "-host", "shell", "su", "-c",
                    f'"{self.MIRROR_POSITION_TCPDUMP_COMMAND_8295}"',
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"\u540e\u89c6\u955c\u4f4d\u7f6e\u8bfb\u53d6\u5931\u8d25: {exc}")
            return None
        raw_output = result.stdout
        if result.returncode != 0:
            print(f"\u540e\u89c6\u955c\u4f4d\u7f6e\u8bfb\u53d6\u5931\u8d25: {result.stderr or raw_output}")
            return None
        match = re.search(
            r"(?m)^\s*0x0030:\s+([0-9A-Fa-f]{4})\s+([0-9A-Fa-f]{4})(?![0-9A-Fa-f])",
            self._strip_ansi_sequences(raw_output),
        )
        if not match:
            print(f"\u540e\u89c6\u955c\u4f4d\u7f6e\u89e3\u6790\u5931\u8d25: {raw_output}")
            return None
        positions = bytes.fromhex(match.group(1) + match.group(2))
        return dict(zip(self.MIRROR_POSITION_FIELDS_8295, positions))

    def run_adb_key_values_cmd(self, cmd, config=None):
        """执行 JS/console adb 命令，提取最后出现的 key=value; 结果。"""
        config = config or {}
        try:
            timeout = float(config.get("read_timeout", 35))
        except Exception:
            timeout = 35

        last_output = ""
        last_returncode = 0
        partial_values = None
        partial_missing = []
        for capture_cmd, capture_timeout in self._adb_console_capture_cmds(cmd, timeout):
            last_returncode, last_output, values, missing = self._run_key_value_capture_command(
                capture_cmd, config, capture_timeout
            )
            values = values or {}
            missing = missing or []
            if values and not missing:
                self._cleanup_remote_node_script(cmd)
                return values
            if values:
                partial_values = values
                partial_missing = missing

        if partial_values:
            for label in partial_missing:
                partial_values[label] = None
            print(f"JS键值输出缺失字段: {partial_missing}")
            self._cleanup_remote_node_script(cmd)
            return partial_values

        output_text = last_output.strip()
        if last_returncode != 0:
            print(f"JS键值命令失败: {cmd}\n返回码: {last_returncode}\n输出: {output_text}")
        elif not output_text:
            print(f"JS键值命令无输出: {cmd}")
        else:
            print(f"JS键值命令未找到 key=value 输出: {output_text}")
        self._cleanup_remote_node_script(cmd)
        return None

    def run_exit_code_cmd(self, cmd, config=None):
        config = config or {}
        try:
            timeout = float(config.get("read_timeout", 300))
        except Exception:
            timeout = 300

        last_message = ""
        last_output = ""
        for capture_cmd, capture_timeout in self._adb_console_capture_cmds(cmd, timeout):
            ok, message, output = self._run_exit_code_capture_command(capture_cmd, config, capture_timeout)
            last_message = message
            last_output = output or ""
            self._cleanup_remote_node_script(cmd)
            if ok:
                if last_output.strip() and not config.get("suppress_output"):
                    print(last_output.strip())
                return True, message, last_output

        output_text = last_output.strip()
        if output_text:
            print(f"执行命令失败: {cmd}\n原因: {last_message}\n输出: {output_text}")
        else:
            print(f"执行命令失败: {cmd}\n原因: {last_message}")
        return False, last_message or "执行失败", last_output

    def run_adb_raw_cmd(self, cmd):
        """执行 adb 命令，返回原始文本输出（用于账号等非数值信息）"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                err = (result.stderr or result.stdout or "").strip()
                print(f"命令失败: {cmd}\n错误: {err}")
                return None
            return result.stdout.strip()
        except Exception as e:
            print(f"命令失败: {cmd}\n错误: {e}")
            return None

    def run_adb_connected_camera_status_cmd(self, cmd):
        """解析 busctl 返回的 JSON 字符串，读取首个已连接摄像头的 status。"""
        output = self.run_adb_raw_cmd(cmd)
        if not output:
            return None
        try:
            payload = output.strip()
            if payload.startswith("s "):
                payload = payload[2:].strip()
            payload = json.loads(payload)
            if isinstance(payload, str):
                payload = json.loads(payload)
            if not isinstance(payload, dict) or payload.get("code") != 200:
                return None
            cameras = payload.get("data")
            if not isinstance(cameras, list) or not cameras:
                return None
            status = cameras[0].get("status")
            if isinstance(status, bool) or not isinstance(status, int):
                return None
            return status
        except (ValueError, TypeError, AttributeError):
            print(f"摄像头连接状态解析失败: {output}")
            return None

    def run_adb_sigval_cmd(self, cmd, config=None):
        """执行 vapisend -get 命令并提取嵌套返回中的 sigVal 字段。"""
        config = config or {}
        try:
            timeout = float(config.get("read_timeout", 10))
        except (TypeError, ValueError):
            timeout = 10

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            output = "\n".join(
                part.strip()
                for part in (result.stdout, result.stderr)
                if part and part.strip()
            )
            if result.returncode != 0:
                print(f"命令失败: {cmd}\n返回码: {result.returncode}\n输出: {output}")
                return None

            sig_values = []
            for payload in self._iter_json_objects_from_text(output):
                sig_values.extend(self._collect_sigval_payloads(payload))
            scalar_values = [
                value for value in sig_values
                if not isinstance(value, (dict, list))
            ]
            if scalar_values:
                return self._parse_number_like(scalar_values[-1])

            # 兼容非完整 JSON 输出。
            text = self._strip_ansi_sequences(output).replace(r'\"', '"')
            match = re.search(r'"?sigVal"?\s*:\s*"([^"]*)"', text, re.IGNORECASE)
            if match:
                return self._parse_number_like(match.group(1))

            print(f"⚠️ 无法解析 sigVal: {output}")
            return None
        except Exception as e:
            print(f"命令失败: {cmd}\n错误: {e}")
            return None

    def run_adb_sigval_detailed_cmd(self, cmd, config=None):
        """严格读取 sigVal，同时保留原始返回供只读状态诊断。"""
        config = config or {}
        try:
            timeout = float(config.get("read_timeout", 10))
        except (TypeError, ValueError):
            timeout = 10

        output = ""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            output = "\n".join(
                part.strip()
                for part in (result.stdout, result.stderr)
                if part and part.strip()
            )
            if result.returncode != 0:
                return None, None, output, f"命令返回码为 {result.returncode}"
            if not output:
                return None, None, output, "返回内容为空"

            plain_text = self._strip_ansi_sequences(output).replace(r'\"', '"')
            if re.search(r"No\s+rx\s+signal", plain_text, re.IGNORECASE):
                return None, None, output, "No rx signal"
            if re.search(
                r'''["']?ret["']?\s*[:=]\s*["']?NG(?:["'\s,}\]]|$)''',
                plain_text,
                re.IGNORECASE,
            ):
                return None, None, output, "ret=NG"

            sig_values = []
            for payload in self._iter_json_objects_from_text(output):
                sig_values.extend(self._collect_sigval_payloads(payload))
            scalar_values = [
                value for value in sig_values
                if not isinstance(value, (dict, list))
            ]
            raw_sigval = scalar_values[-1] if scalar_values else None

            if raw_sigval is None:
                match = re.search(
                    r'''["']?sigVal["']?\s*:\s*(?:["'](?P<quoted>[^"']*)["']|(?P<plain>[^,\s}\]]+))''',
                    plain_text,
                    re.IGNORECASE,
                )
                if match:
                    raw_sigval = (
                        match.group("quoted")
                        if match.group("quoted") is not None
                        else match.group("plain")
                    )

            if raw_sigval is None:
                return None, None, output, "未找到 sigVal"
            if isinstance(raw_sigval, str):
                raw_sigval = raw_sigval.strip()
                if not raw_sigval or raw_sigval.lower() in ("null", "none"):
                    return None, None, output, "sigVal 为空"

            return self._parse_number_like(raw_sigval), raw_sigval, output, None
        except Exception as e:
            return None, None, output, f"读取异常: {e}"

    def execute_step_board_status(self, config):
        """只读采集左右电动踏板的状态与位置。"""
        results = {}
        failures = []
        raw_outputs = []

        print(">>> 只读查询: 电动踏板状态")
        for label, command, value_type in self.STEP_BOARD_RESULT_COMMANDS_8797:
            value, raw_sigval, raw_output, error = self.run_adb_sigval_detailed_cmd(
                command, config
            )
            raw_outputs.append(
                f"[{label}]\n{raw_output if raw_output else '(无返回内容)'}"
            )

            side = "左侧" if label.startswith("左侧") else "右侧"
            if error:
                results[label] = None
                if value_type == "status":
                    results[f"{side}踏板原始状态 sigVal"] = None
                    results[f"{side}踏板中文状态"] = "读取失败"
                else:
                    results[f"{side}踏板原始位置 sigVal"] = None
                failures.append(f"{label}: {error}")
                continue

            if value_type == "status":
                status_value = str(value).strip().upper()
                chinese_status = self.STEP_BOARD_STATUS_VALUES_8797.get(status_value)
                results[f"{side}踏板原始状态 sigVal"] = raw_sigval
                if chinese_status is None:
                    results[label] = None
                    results[f"{side}踏板中文状态"] = "解析失败"
                    failures.append(f"{label}: 无法识别状态值 {raw_sigval}")
                else:
                    results[label] = status_value
                    results[f"{side}踏板中文状态"] = chinese_status
            else:
                results[f"{side}踏板原始位置 sigVal"] = raw_sigval
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    results[label] = None
                    failures.append(f"{label}: 位置不是有效数字 {raw_sigval}")
                elif not 0 <= value <= 100:
                    results[label] = None
                    failures.append(f"{label}: 位置超出 0~100 范围 ({value})")
                else:
                    results[label] = value

        results["原始 vapisend 返回内容"] = "\n\n".join(raw_outputs)
        if failures:
            error_text = "；".join(failures)
            print(f"❌ 电动踏板状态读取失败: {error_text}")
            return (
                results,
                config.get("tolerance", 3),
                f"电动踏板状态读取失败: {error_text}\n"
                f"原始 vapisend 返回内容:\n{results['原始 vapisend 返回内容']}",
            )

        return results, config.get("tolerance", 3), None

    def run_adb_rear_screen_power_cmd(self, cmd, config=None):
        """解析后排屏电源返回体中 PARAM 内部 JSON 的 power 字段。"""
        config = config or {}
        try:
            timeout = float(config.get("read_timeout", 10))
        except (TypeError, ValueError):
            timeout = 10

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            output = "\n".join(
                part.strip()
                for part in (result.stdout, result.stderr)
                if part and part.strip()
            )
            if result.returncode != 0:
                print(f"命令失败: {cmd}\n返回码: {result.returncode}\n输出: {output}")
                return None

            power_values = []
            for payload in self._iter_json_objects_from_text(output):
                power_values.extend(
                    self._collect_json_field_values(payload, "power")
                )
            for value in reversed(power_values):
                parsed = self._parse_number_like(value)
                if isinstance(parsed, (int, float)):
                    return parsed

            text = self._strip_ansi_sequences(output).replace(r'\"', '"')
            match = re.search(
                r'"?power"?\s*:\s*"?(?P<value>-?\d+(?:\.\d+)?)',
                text,
                re.IGNORECASE,
            )
            if match:
                return self._parse_number_like(match.group("value"))

            print(f"⚠️ 无法解析后排屏 power: {output}")
            return None
        except Exception as e:
            print(f"命令失败: {cmd}\n错误: {e}")
            return None

    def run_adb_voice1_cmd(self, cmd):
        """执行 adb 命令并提取 voice1 打印行，返回稳定的 voice1 =...; 文本。"""
        def normalize_output(text):
            if text is None:
                return ""
            if isinstance(text, bytes):
                for encoding in ("utf-8", "gbk", "latin-1"):
                    try:
                        return text.decode(encoding, errors="replace")
                    except Exception:
                        continue
                return text.decode(errors="replace")
            return str(text)

        def parse_voice1(output):
            output = normalize_output(output)
            if not output:
                return None

            output = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', output)
            on_path = "page://systemres.yunos.com/assets/caf_images/hdt_light/SwitchLA/ON/Normal.png"
            off_path = "page://systemres.yunos.com/assets/caf_images/hdt_light/SwitchLA/OFF/Normal.png"
            if on_path in output:
                return f"voice1 ={on_path};"
            if off_path in output:
                return f"voice1 ={off_path};"

            match = re.search(
                r'voice1\s*=\s*["\']?([^;"\'\r\n]*SwitchLA/(?:ON|OFF)/Normal\.png)["\']?\s*;?',
                output,
                re.IGNORECASE
            )
            if match:
                return f"voice1 ={match.group(1).strip()};"

            return None

        def run_capture(capture_cmd, timeout):
            proc = None
            popen_kwargs = {}
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                popen_kwargs["startupinfo"] = startupinfo
                popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            try:
                use_shell = isinstance(capture_cmd, str)
                proc = subprocess.Popen(
                    capture_cmd,
                    shell=use_shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    **popen_kwargs
                )
                stdout, stderr = proc.communicate(timeout=timeout)
                output = "\n".join(
                    part.strip()
                    for part in (normalize_output(stdout), normalize_output(stderr))
                    if part and part.strip()
                )
                return proc.returncode, output
            except subprocess.TimeoutExpired as e:
                if proc is not None and proc.poll() is None:
                    try:
                        if os.name == "nt" and isinstance(capture_cmd, str):
                            subprocess.run(
                                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                                capture_output=True,
                                timeout=3,
                                **popen_kwargs
                            )
                        else:
                            proc.kill()
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                try:
                    stdout, stderr = proc.communicate(timeout=3) if proc is not None else ("", "")
                except Exception:
                    stdout, stderr = (
                        getattr(e, "stdout", None) or getattr(e, "output", None),
                        getattr(e, "stderr", None)
                    )
                output = "\n".join(
                    part.strip()
                    for part in (normalize_output(stdout), normalize_output(stderr))
                    if part and part.strip()
                )
                return -1, output
            except Exception as e:
                return -1, str(e)

        adb_prefix = "adb -host shell "
        capture_cmds = []
        if cmd.strip().startswith(adb_prefix):
            remote_cmd = cmd.strip()[len(adb_prefix):].strip()
            capture_cmds.append((["adb", "-host", "shell"] + remote_cmd.split(), 35))
            capture_cmds.append(
                (["adb", "-host", "shell", f"{remote_cmd} & pid=$!; sleep 20; kill $pid >/dev/null 2>&1"], 28)
            )
        else:
            capture_cmds.append((cmd, 35))

        last_output = ""
        last_returncode = 0
        for capture_cmd, timeout in capture_cmds:
            last_returncode, last_output = run_capture(capture_cmd, timeout)
            value = parse_voice1(last_output)
            if value is not None:
                return value

        if last_returncode != 0:
            print(f"语音服务开关状态命令失败: {cmd}\n返回码: {last_returncode}\n输出: {last_output.strip()}")
            return None

        if not last_output.strip():
            print(f"语音服务开关状态命令无输出: {cmd}")
            return None

        print(f"语音服务开关状态未找到 voice1 输出: {last_output.strip()}")
        return None

    def execute_diagnostic_action(self, action_name, config):
        """执行综合测试内置诊断动作"""
        if action_name == "vehicle_reset":
            return self._execute_vehicle_reset(config)
        if action_name == "lhzcu_left_front_door_e_release":
            return self._execute_lhzcu_left_front_door_e_release(config)
        if action_name == "lhzcu_left_rear_door_e_release":
            return self._execute_lhzcu_left_rear_door_e_release(config)
        if action_name == "rhzcu_right_front_door_e_release":
            return self._execute_rhzcu_right_front_door_e_release(config)
        if action_name == "rhzcu_right_rear_door_e_release":
            return self._execute_rhzcu_right_rear_door_e_release(config)
        return False, f"未知诊断动作: {action_name}"

    def _execute_lhzcu_left_front_door_e_release(self, config):
        return self._execute_zone_door_e_release(
            config=config,
            ecu_name="LHZCU",
            target_addr=0x15B0,
            security_algo=0x1010,
            label="左前门",
            io_control_data=bytes.fromhex("02 00 00 00"),
        )

    def _execute_lhzcu_left_rear_door_e_release(self, config):
        return self._execute_zone_door_e_release(
            config=config,
            ecu_name="LHZCU",
            target_addr=0x15B0,
            security_algo=0x1010,
            label="左后门",
            io_control_data=bytes.fromhex("00 08 00 00"),
        )

    def _execute_rhzcu_right_front_door_e_release(self, config):
        from Subpy.rhzcu_doip_config import RHZCU_PHYSICAL_ADDR, RHZCU_SECURITY_ALGO

        return self._execute_zone_door_e_release(
            config=config,
            ecu_name="RHZCU",
            target_addr=RHZCU_PHYSICAL_ADDR,
            security_algo=RHZCU_SECURITY_ALGO,
            label="右前门",
            io_control_data=bytes.fromhex("02 00 00 00"),
        )

    def _execute_rhzcu_right_rear_door_e_release(self, config):
        from Subpy.rhzcu_doip_config import RHZCU_PHYSICAL_ADDR, RHZCU_SECURITY_ALGO

        return self._execute_zone_door_e_release(
            config=config,
            ecu_name="RHZCU",
            target_addr=RHZCU_PHYSICAL_ADDR,
            security_algo=RHZCU_SECURITY_ALGO,
            label="右后门",
            io_control_data=bytes.fromhex("00 08 00 00"),
        )

    def _execute_vehicle_reset(self, config):
        """整车广播 Reset：10 03 -> 重连 -> 11 01。"""
        client = None
        results = {}
        try:
            from Subpy.doip_client import DoIPClient
            from Subpy.broadcast_doip_config import (
                BROADCAST_DOIP_IP,
                BROADCAST_DOIP_PORT,
                BROADCAST_ROUTING_TA,
                BROADCAST_PHYSICAL_ADDR,
            )

            doip_timeout = float(config.get("doip_timeout", 5))
            session_timeout = float(config.get("session_response_timeout", 4))
            reset_timeout = float(config.get("reset_response_timeout", 4))
            reconnect_delay = float(config.get("reset_reconnect_delay", 0.5))

            print(
                f"[诊断] 整车Reset连接 ICB: {BROADCAST_DOIP_IP}:{BROADCAST_DOIP_PORT}, "
                f"routing_ta=0x{BROADCAST_ROUTING_TA:04X}"
            )
            client = DoIPClient(
                BROADCAST_DOIP_IP,
                BROADCAST_DOIP_PORT,
                routing_ta=BROADCAST_ROUTING_TA,
                timeout=doip_timeout,
            )
            client.connect()
            client.routing_activate()

            print(f"[诊断] tx 0x{BROADCAST_PHYSICAL_ADDR:04X} 10 03")
            session_responses = client.send_diagnostic_multi(
                bytes.fromhex("1003"),
                target_addr=BROADCAST_PHYSICAL_ADDR,
                timeout=session_timeout,
                broadcast_mode=True,
            )
            session_summary = self._summarize_broadcast_responses(
                session_responses,
                positive_sid=0x50,
                expected_subfunction=0x03,
                request_sid=0x10,
            )
            self._print_broadcast_summary("扩展会话", session_summary)

            client.disconnect()
            client = None
            if reconnect_delay > 0:
                print(f"[诊断] 整车Reset前重连等待 {reconnect_delay:g} 秒...")
                if not self.interruptible_sleep(reconnect_delay):
                    return False, "测试已停止", results

            print("[诊断] 重新连接 ICB 用于 11 01 Reset")
            client = DoIPClient(
                BROADCAST_DOIP_IP,
                BROADCAST_DOIP_PORT,
                routing_ta=BROADCAST_ROUTING_TA,
                timeout=doip_timeout,
            )
            client.connect()
            client.routing_activate()

            print(f"[诊断] tx 0x{BROADCAST_PHYSICAL_ADDR:04X} 11 01")
            reset_responses = client.send_diagnostic_multi(
                bytes.fromhex("1101"),
                target_addr=BROADCAST_PHYSICAL_ADDR,
                timeout=reset_timeout,
                broadcast_mode=True,
            )
            reset_summary = self._summarize_broadcast_responses(
                reset_responses,
                positive_sid=0x51,
                expected_subfunction=0x01,
                request_sid=0x11,
            )
            self._print_broadcast_summary("Reset", reset_summary)

            results = {
                "扩展会话响应数": session_summary["positive_count"],
                "扩展会话总响应数": session_summary["total_count"],
                "Reset响应数": reset_summary["positive_count"],
                "Reset总响应数": reset_summary["total_count"],
                "Reset NRC数": reset_summary["nrc_count"],
            }

            min_session = int(config.get("min_session_responses", 0))
            min_reset = int(config.get("min_reset_responses", 0))
            min_reset_total = int(config.get("min_reset_total_responses", 1))
            if session_summary["positive_count"] < min_session:
                return False, f"整车Reset失败: 扩展会话响应数 {session_summary['positive_count']} 小于 {min_session}", results
            if reset_summary["positive_count"] < min_reset:
                return False, f"整车Reset失败: Reset响应数 {reset_summary['positive_count']} 小于 {min_reset}", results
            if reset_summary["total_count"] < min_reset_total:
                return False, f"整车Reset失败: Reset总响应数 {reset_summary['total_count']} 小于 {min_reset_total}", results

            message = (
                "整车Reset诊断执行成功: "
                f"扩展会话 {session_summary['positive_count']}/{session_summary['total_count']}, "
                f"Reset {reset_summary['positive_count']}/{reset_summary['total_count']}"
            )
            return True, message, results
        except Exception as e:
            return False, f"整车Reset诊断异常: {e}", results
        finally:
            if client is not None:
                try:
                    client.disconnect()
                except Exception:
                    pass

    def _summarize_broadcast_responses(self, responses, positive_sid, expected_subfunction, request_sid):
        summary = {
            "total_count": 0,
            "positive_count": 0,
            "pending_count": 0,
            "nrc_count": 0,
            "other_count": 0,
            "items": [],
        }

        for item in responses or []:
            source_addr = item.get("source_addr")
            uds = item.get("uds") or b""
            if not uds:
                continue

            summary["total_count"] += 1
            positive_pattern = bytes([positive_sid, expected_subfunction])
            positive = self._find_bytes(uds, positive_pattern) >= 0
            nrc_code = self._find_nrc_code(uds, request_sid)

            if positive:
                status = "positive"
                summary["positive_count"] += 1
            elif nrc_code == 0x78:
                status = "pending"
                summary["pending_count"] += 1
            elif nrc_code is not None:
                status = f"NRC 0x{nrc_code:02X}"
                summary["nrc_count"] += 1
            else:
                status = "other"
                summary["other_count"] += 1

            summary["items"].append({
                "source_addr": source_addr,
                "status": status,
                "uds": uds,
            })

        return summary

    def _find_bytes(self, data, pattern):
        if not data or not pattern or len(data) < len(pattern):
            return -1
        return bytes(data).find(pattern)

    def _find_nrc_code(self, uds, request_sid):
        data = bytes(uds)
        for idx in range(0, max(0, len(data) - 2)):
            if data[idx] == 0x7F and data[idx + 1] == request_sid:
                return data[idx + 2]
        return None

    def _format_uds(self, data, max_len=24):
        shown = bytes(data[:max_len])
        text = " ".join(f"{b:02X}" for b in shown)
        if len(data) > max_len:
            text += " ..."
        return text

    def _print_broadcast_summary(self, stage, summary):
        print(
            f"[诊断] {stage}响应: positive={summary['positive_count']}, "
            f"pending={summary['pending_count']}, nrc={summary['nrc_count']}, "
            f"other={summary['other_count']}, total={summary['total_count']}"
        )
        for item in summary["items"][:20]:
            source_addr = item.get("source_addr")
            addr_text = f"0x{source_addr:04X}" if source_addr is not None else "unknown"
            print(f"[诊断]   {addr_text}: {item['status']} {self._format_uds(item['uds'])}")
        if len(summary["items"]) > 20:
            print(f"[诊断]   ... 省略 {len(summary['items']) - 20} 条响应")

    def _execute_zone_door_e_release(self, config, ecu_name, target_addr, security_algo, label, io_control_data):
        """区域控制器门电释放：10 03 -> 27 01/02 -> 2F D1 80 03 + IO控制数据"""
        diag = None
        try:
            from Subpy.lhzcu_diagnostics import LHZCUDiagnostics

            diag = LHZCUDiagnostics(
                target_addr=target_addr,
                security_algo=security_algo,
                timeout=5.0,
            )
            print(f"[诊断] {ecu_name} 连接并路由激活...")
            diag.connect()

            print(f"[诊断] tx 0x{target_addr:04X} 10 03")
            session_result = diag.extended_session()
            print(f"[诊断] 扩展会话: {session_result}")

            print(f"[诊断] tx 0x{target_addr:04X} 27 01")
            security_result = diag.security_level1()
            print(
                "[诊断] 安全访问成功: "
                f"seed={security_result.get('seed')}, key={security_result.get('key')}"
            )

            io_hex = " ".join(f"{b:02X}" for b in io_control_data)
            print(f"[诊断] tx 0x{target_addr:04X} 2F D1 80 03 {io_hex}")
            result = diag.io_control("D180", "03", io_control_data)
            if not result.get("success"):
                return False, f"{ecu_name} IO控制失败: {result.get('error', result)}"

            wait_seconds = float(config.get("diagnostic_wait_seconds", 0))
            if wait_seconds > 0:
                print(f"[诊断] IO控制完成，等待 {wait_seconds:g} 秒...")
                if not self.interruptible_sleep(wait_seconds):
                    return False, "测试已停止"

            return True, f"{ecu_name} {label}电释放诊断执行成功"
        except Exception as e:
            return False, f"{ecu_name} {label}电释放诊断异常: {e}"
        finally:
            if diag is not None:
                try:
                    diag.disconnect()
                except Exception:
                    pass
    
    def load_all_baselines(self):
        """加载所有基准（从单个文件，带异常保护）"""
        if not os.path.exists(self.baseline_file):
            return {}
        try:
            with open(self.baseline_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, OSError) as e:
            print(f"⚠️ all_baselines.json 损坏({e})，自动重置")
            try:
                backup_path = self.baseline_file + ".bak"
                if os.path.exists(self.baseline_file):
                    os.rename(self.baseline_file, backup_path)
                self.save_all_baselines({})
                print(f"✅ 已备份损坏文件为 {backup_path}，创建新的空基准文件")
            except OSError:
                pass
            return {}
    
    def save_all_baselines(self, baselines):
        """保存所有基准到单个文件"""
        with open(self.baseline_file, "w", encoding="utf-8") as f:
            json.dump(baselines, f, ensure_ascii=False, indent=2)
    
    def has_baseline(self, instruction_name):
        """检查指定指令是否有基准"""
        return bool(self.get_baseline(instruction_name))
    
    def save_baseline(self, instruction_name, results):
        config = self._get_instruction_config(instruction_name)
        required_fields = tuple(config.get("baseline_fields", ()))
        missing_fields = [
            field
            for field in required_fields
            if not isinstance(results, dict)
            or field not in results
            or results.get(field) is None
        ]
        if missing_fields:
            print(f"基准值缺少必需字段，不保存: {missing_fields}")
            return False
        results_to_save = results
        if config.get("save_baseline_fields_only") and required_fields:
            results_to_save = {
                field: results.get(field)
                for field in required_fields
            }
        """保存单个指令的基准"""
        instruction_name = self._baseline_instruction_name(instruction_name)
        # 检查是否有无效值
        has_none = any(v is None for v in results_to_save.values())
        if has_none:
            print(f"❌ 基准值包含 None，不保存: {results_to_save}")
            return False
        
        baselines = self.load_all_baselines()
        
        # 综合测试基准，加上前缀区分
        if (
            self.vehicle_platform == "8797"
            and instruction_name in {
                "C屏下电",
                "账号",
                "\u9884\u7ea6\u5145\u7535\u5f00\u5173\u72b6\u6001",
                "\u9884\u7ea6\u5145\u7535\u5f00\u59cb\u65f6\u95f4",
                "\u9884\u7ea6\u5145\u7535\u7ed3\u675f\u65f6\u95f4",
            }
        ):
            baseline_name = f"综合_8797_{instruction_name}"
        else:
            baseline_name = f"综合_{instruction_name}"
        baselines[baseline_name] = {
            "type": "general_test",
            "instruction": instruction_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": results_to_save
        }
        self.save_all_baselines(baselines)
        print(f"✅ :通过/基准已保存 {baseline_name}")
        return True
    
    def get_baseline(self, instruction_name):
        """获取指定指令的基准"""
        baselines = self.load_all_baselines()
        config = self._get_instruction_config(instruction_name)
        for baseline_key in self._baseline_key_candidates(instruction_name):
            if baseline_key in baselines:
                results = baselines.get(baseline_key, {}).get("results", {})
                if self._baseline_results_compatible(config, results):
                    return results
        return {}

    def _baseline_results_compatible(self, config, results):
        if not isinstance(results, dict):
            return False
        required_fields = tuple(config.get("baseline_fields", ()))
        if required_fields:
            return all(
                field in results and results.get(field) is not None
                for field in required_fields
            )
        if config.get("result_parser") == "sigval_json_fields":
            fields = [str(field).strip() for field in config.get("sigval_fields", []) if str(field).strip()]
            return bool(results) and any(field in results for field in fields)
        if not config.get("parse_key_values"):
            return True
        if not results:
            return False

        labels = self._command_value_labels(config)
        if labels:
            return any(label in results for label in labels)

        prefixes = self._command_value_key_prefixes(config)
        if prefixes:
            return any(
                str(key).lower().startswith(prefix.lower())
                for key in results.keys()
                for prefix in prefixes
            )
        return True
    
    def delete_baseline(self, instruction_name):
        """删除指定指令的基准"""
        baselines = self.load_all_baselines()
        deleted = False
        for baseline_key in self._baseline_key_candidates(instruction_name):
            if baseline_key in baselines:
                del baselines[baseline_key]
                deleted = True
        
        if deleted:
            self.save_all_baselines(baselines)
        
        return deleted
    
    def execute_and_collect(self, instruction_name, extra_wait=0):
        """执行指令 + 等待 + 收集结果
        extra_wait: 额外等待时间（从界面输入框读取），会加上配置里的基础等待时间
        """
        instruction_name = self._canonical_instruction_name(instruction_name)
        if instruction_name not in self.instructions:
            return None, 0, f"未找到指令: {instruction_name}"
        
        config = self._get_instruction_config(instruction_name)
        allowed_platforms = config.get("platforms") if isinstance(config, dict) else None
        if allowed_platforms and self.vehicle_platform not in allowed_platforms:
            return None, config.get("tolerance", 0), (
                f"指令 {instruction_name} 不支持 {self.vehicle_platform} 平台"
            )
        if self.should_stop():
            return None, config.get("tolerance", 0), "测试已停止"
        
        # 🎯 特殊指令：音频探测
        if config.get("special_type") == "audio_detection":
            # 🎯 从self的属性中读取（综合测试对话框传递过来的）
            duration = getattr(self, "_audio_duration", 10)
            threshold = getattr(self, "_audio_threshold", 5)
            save_folder = getattr(self, "_save_folder", "")
            
            try:
                duration = float(duration)
            except:
                duration = 10
            try:
                threshold = float(threshold)
            except:
                threshold = 5
            
            # 调用音频探测函数
            results, tolerance, error = self.execute_audio_detection(
                save_folder=save_folder,
                duration_seconds=duration,
                threshold_percent=threshold
            )
            
            return results, tolerance, error

        if config.get("special_type") == "lastmode_cache":
            current_cycle = getattr(self, "_lastmode_current_cycle", 0)
            save_folder = getattr(self, "_save_folder", "")
            return self.execute_lastmode_cache(
                save_folder=save_folder,
                current_cycle=current_cycle,
                tolerance=config.get("tolerance", 0),
            )

        if config.get("special_type") == "step_board_status":
            return self.execute_step_board_status(config)
        
        # 1. 执行控制指令（区分继电器指令、ADB指令、纯读取指令、纯视觉指令、等待指令、截图指令）
        print(f">>> 执行: {instruction_name}")
        
        has_execute = "execute_cmd" in config  # 是否有执行命令
        is_relay = config.get("is_relay", False)  # 是否是继电器指令
        is_visual_only = config.get("is_visual_only", False)  # 是否是纯视觉检测指令
        is_wait_only = config.get("is_wait_only", False)  # 是否是纯等待指令
        is_screenshot = config.get("is_screenshot", False)  # 是否是截图指令
        diagnostic_action = config.get("diagnostic_action", "")  # 是否是诊断动作指令
        
        if is_wait_only:
            # 纯等待指令：等待时间 = 休眠唤醒延迟时间
            total_wait = self.sleep_wake_delay
            print(f"[等待] 休眠唤醒延迟: {self.sleep_wake_delay}s, 递增时间: {self.increment_time}s, 总等待: {total_wait}s")
            
            if total_wait > 0:
                # 分段显示等待进度
                interval = min(1.0, total_wait)
                elapsed = 0
                while elapsed < total_wait:
                    if not self.interruptible_sleep(interval):
                        return None, config["tolerance"], "测试已停止"
                    elapsed += interval
                    remaining = max(0, total_wait - elapsed)
                    if remaining > 0:
                        print(f"[等待] 剩余 {remaining:.1f} 秒...")
            
            print(f"[等待] 等待完成")
            return {}, config["tolerance"], None
            
        elif is_visual_only:
            # 纯视觉检测指令
            from Subpy.visual_detector import get_visual_detector
            detector = get_visual_detector()
            
            wait_time = config.get("wait_seconds", 3)
            total_wait = wait_time + extra_wait
            print(f"[视觉] 等待 {total_wait} 秒后执行检测...")
            if not self.interruptible_sleep(total_wait):
                return None, config["tolerance"], "测试已停止"
            
            # 🎯 确保摄像头一定打开（自动打开，无需手动去设置里打开）
            if detector.cap is None or not detector.cap.isOpened():
                print(f"[视觉] 正在自动打开摄像头 {detector.camera_port}...")
                detector.open_camera(detector.camera_port)
                if not self.interruptible_sleep(0.5):  # 等摄像头稳定
                    return None, config["tolerance"], "测试已停止"
            
            # 🎯 等待亮度稳定策略
            print(f"[视觉] 开始等待亮度稳定（最多5秒）...")
            max_wait = 5.0  # 最多等待5秒
            check_interval = 0.2  # 每0.2秒检测一次
            stable_time = 0.5  # 需要稳定保持0.5秒
            stable_start = None
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # 抓取一帧
                ret, frame = detector.cap.read()
                if ret:
                    detector.current_frame = frame
                
                # 检测亮度
                if len(detector.roi_list) > 0 and detector.current_frame is not None:
                    all_ok = True
                    brightness_results = {}
                    for i, roi in enumerate(detector.roi_list):
                        brightness = detector.calculate_brightness(detector.current_frame, roi)
                        brightness_results[f"区域{i+1}_亮度"] = round(brightness, 1)
                        if brightness < detector.brightness_threshold:
                            all_ok = False
                    
                    # 检查是否稳定
                    if all_ok:
                        if stable_start is None:
                            stable_start = time.time()
                            print(f"[视觉] 亮度达标，开始计时稳定...")
                        elif time.time() - stable_start >= stable_time:
                            print(f"[视觉] 亮度已稳定！各区域亮度: {brightness_results}")
                            return brightness_results, config["tolerance"], None
                    else:
                        stable_start = None
                        print(f"[视觉] 亮度未达标: {brightness_results}")
                
                if not self.interruptible_sleep(check_interval):
                    return None, config["tolerance"], "测试已停止"
            
            # 🎯 超时了，按最后一帧判断
            print(f"[视觉] 等待超时，按最后一帧判断...")
            if len(detector.roi_list) > 0 and detector.current_frame is not None:
                brightness_results = {}
                for i, roi in enumerate(detector.roi_list):
                    brightness = detector.calculate_brightness(detector.current_frame, roi)
                    brightness_results[f"区域{i+1}_亮度"] = round(brightness, 1)
                print(f"[视觉] 最后一帧各区域亮度: {brightness_results}")
                return brightness_results, config["tolerance"], None
            else:
                print(f"[视觉] ROI数量: {len(detector.roi_list)}, 摄像头状态: {'打开' if detector.cap and detector.cap.isOpened() else '关闭'}")
                
        elif is_relay:
            # 继电器控制指令：优先使用动态传入的通道映射，其次使用配置中的默认值
            channel = self.relay_channel_map.get(instruction_name, config.get("relay_channel", 1))
            duration = config.get("press_duration", 2.0)
            print(f"[继电器] {instruction_name}: 串口={self.relay_port}, 通道={channel}, 持续={duration}秒")
            if not self.press_relay(channel, duration):
                return None, config["tolerance"], "继电器执行失败或测试已停止"
            
            # 等待动作完成
            wait_time = config.get("wait_seconds", 0)
            total_wait = wait_time + extra_wait
            print(f"[调试] wait_seconds={wait_time}s, extra_wait={extra_wait}s, total_wait={total_wait}s")
            print(f"等待 {total_wait} 秒...")
            if not self.interruptible_sleep(total_wait):
                return None, config["tolerance"], "测试已停止"
            
        elif "robot_command" in config:
            # 机器人控制指令：通过TCP/IP发送
            robot_cmd = config["robot_command"]
            robot_ip = config.get("robot_ip", self.robot_ip)
            robot_port = config.get("robot_port", self.robot_port)
            robot_timeout = config.get("robot_timeout", self.robot_timeout)
            print(f"[机器人] {instruction_name}: 发送指令={robot_cmd}, 目标={robot_ip}:{robot_port}")
            success = self.send_robot_command(robot_cmd, robot_ip, robot_port, robot_timeout)
            
            if not success:
                print(f"[机器人] 指令发送失败: {instruction_name}")
                return None, config["tolerance"], "机器人指令发送失败"
            
            # 等待动作完成
            wait_time = config.get("wait_seconds", 0)
            total_wait = wait_time + extra_wait
            print(f"[调试] wait_seconds={wait_time}s, extra_wait={extra_wait}s, total_wait={total_wait}s")
            print(f"等待 {total_wait} 秒...")
            if not self.interruptible_sleep(total_wait):
                return None, config["tolerance"], "测试已停止"

        elif diagnostic_action:
            print(f"[诊断] {instruction_name}: {diagnostic_action}")
            action_result = self.execute_diagnostic_action(diagnostic_action, config)
            if len(action_result) == 3:
                success, message, diagnostic_results = action_result
            else:
                success, message = action_result
                diagnostic_results = None
            print(f"[诊断] {message}")
            if not success:
                return diagnostic_results, config["tolerance"], message

            wait_time = config.get("wait_seconds", 0)
            total_wait = wait_time + extra_wait
            if total_wait > 0:
                print(f"[诊断] 额外等待 {total_wait} 秒...")
                if not self.interruptible_sleep(total_wait):
                    return None, config["tolerance"], "测试已停止"

            if diagnostic_results is not None:
                return diagnostic_results, config["tolerance"], None
        
        elif is_screenshot:
            # 截图指令：uiautomator_screencap → adb pull → 删除车机文件
            # 三个步骤全部成功才算 pass，无需基准对比
            # save_folder 由 execute_and_compare 通过 self._screenshot_save_folder 注入
            save_folder = getattr(self, "_screenshot_save_folder", "")
            current_cycle = getattr(self, "_screenshot_current_cycle", 0)
            
            if self.vehicle_platform == "8797":
                ok, info = self._do_screenshot_8797(current_cycle, save_folder)
            else:
                ok, info = self._do_screenshot(current_cycle, save_folder)
            
            # 等待
            wait_time = config.get("wait_seconds", 0)
            total_wait = wait_time + extra_wait
            if total_wait > 0:
                if not self.interruptible_sleep(total_wait):
                    return None, config["tolerance"], "测试已停止"
            
            # 通过 results 传递结果给 execute_and_compare
            return {"_screenshot_ok": ok, "_screenshot_info": info}, config["tolerance"], None
            
        elif has_execute:
            # 普通ADB执行指令
            if config.get("success_by_exit_code") or config.get("exit_code_success"):
                ok, message, _output = self.run_exit_code_cmd(config["execute_cmd"], config)
                if not ok:
                    return None, config["tolerance"], message
            else:
                self.run_adb_cmd(config["execute_cmd"])
            
            # 等待动作完成
            wait_time = config.get("wait_seconds", 0)
            total_wait = wait_time + extra_wait
            print(f"等待 {total_wait} 秒...")
            if not self.interruptible_sleep(total_wait):
                return None, config["tolerance"], "测试已停止"
            
        else:
            # 纯读取指令（只读取状态不执行任何动作）
            print(f"[读取] 纯状态读取指令")
            wait_time = config.get("wait_seconds", 0)
            total_wait = 0 if config.get("skip_read_wait") else wait_time + extra_wait
            if total_wait > 0:
                print(f"[读取] wait_seconds={wait_time}s, extra_wait={extra_wait}s, total_wait={total_wait}s")
                print(f"等待 {total_wait} 秒...")
                if not self.interruptible_sleep(total_wait):
                    return None, config["tolerance"], "测试已停止"
        
        # 3. 读取所有返回值（纯视觉指令、等待指令、截图指令已经在上面处理了）
        results = {}
        if not is_visual_only and not is_wait_only and not is_screenshot:
            for item in config["result_cmds"]:
                name, cmd = self._result_cmd_parts(item)
                print(f"[读取] 开始读取: {name}, 命令: {cmd}")
                value = None
                read_retries = max(1, int(config.get("read_retries", 1)))
                retry_interval = float(config.get("read_retry_interval", 0.5))
                parse_key_values = bool(config.get("parse_key_values") or config.get("parser") == "key_value")
                parse_sigval_json_fields = config.get("result_parser") == "sigval_json_fields"
                for attempt in range(1, read_retries + 1):
                    if config.get("result_parser") == "connected_camera_status":
                        value = self.run_adb_connected_camera_status_cmd(cmd)
                    elif config.get("result_parser") == "electric_steering_wheel_position":
                        value = self.run_adb_electric_steering_wheel_position_cmd(cmd, config)
                    elif config.get("result_parser") == "mirror_position_8295":
                        value = self.run_adb_mirror_position_cmd(cmd, config)
                    elif parse_key_values:
                        value = self.run_adb_key_values_cmd(cmd, config)
                    elif parse_sigval_json_fields:
                        value = self.run_adb_sigval_json_fields_cmd(cmd, config)
                    elif config.get("result_parser") == "voice1":
                        value = self.run_adb_voice1_cmd(cmd)
                    elif config.get("result_parser") == "rear_screen_power":
                        value = self.run_adb_rear_screen_power_cmd(cmd, config)
                    elif config.get("result_parser") == "sigval_value":
                        value = self.run_adb_sigval_cmd(cmd, config)
                    elif config.get("raw_output", False):
                        value = self.run_adb_raw_cmd(cmd)
                    else:
                        value = self.run_adb_cmd(cmd)
                    if ((parse_key_values or parse_sigval_json_fields) and value) or (
                        not parse_key_values and not parse_sigval_json_fields and value is not None
                    ):
                        break
                    if attempt < read_retries:
                        print(f"[读取] {name} 第 {attempt}/{read_retries} 次未获取到，{retry_interval:g}s 后重试")
                        if not self.interruptible_sleep(retry_interval):
                            return None, config["tolerance"], "测试已停止"
                if parse_key_values or parse_sigval_json_fields:
                    if isinstance(value, dict) and value:
                        print(f"[读取] {name} 的键值结果: {value}")
                        for key, val in value.items():
                            results[key] = val
                            print(f"  {key}: {val}")
                    else:
                        print(f"[读取] {name} 未获取到键值结果")
                        results[name] = None
                        print(f"  {name}: None")
                    continue
                active_value = config.get("enum_switch_active_value")
                if value is not None and active_value is not None:
                    value = (
                        "开启"
                        if str(value).strip().upper()
                        == str(active_value).strip().upper()
                        else "关闭"
                    )
                print(f"[读取] {name} 的结果: {value}")
                results[name] = value
                print(f"  {name}: {value}")
        
        return results, config["tolerance"], None
    
    def _do_screenshot(self, current_cycle, save_folder):
        """
        执行截图三连：uiautomator_screencap → adb pull → 删除
        :param current_cycle: 当前循环次数（0表示基准测试）
        :param save_folder: 截图保存目录（空字符串表示拉到执行程序目录）
        :return: (是否成功, 详情字符串)
        """
        import subprocess
        import datetime
        
        # 1) 生成图片名称
        timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        if current_cycle and current_cycle > 0:
            img_name = f"cycle{current_cycle}_{timestamp}.png"
        else:
            img_name = f"{timestamp}.png"
        
        device_path = f"/tmp/{img_name}"
        
        # 2) 决定本地保存路径
        if save_folder:
            local_dir = os.path.join(os.path.normpath(save_folder), "截图")
        else:
            # 基准测试：拉到执行程序目录
            local_dir = os.getcwd()
        
        try:
            os.makedirs(local_dir, exist_ok=True)
        except Exception as e:
            return False, f"创建目录失败: {e}"
        
        local_path = os.path.join(local_dir, img_name)
        
        # 3) 顺序执行三条 adb 命令（用 Popen 以便 stop 时 kill）
        cmds = [
            ("截屏", f'adb -host shell "uiautomator_screencap {device_path}"'),
            ("拉取", f'adb -host pull {device_path} "{local_path}"'),
            ("删除", f'adb -host shell "rm -f {device_path}"'),
        ]
        
        details = []
        for step_name, cmd in cmds:
            print(f"[截图] {step_name}: {cmd}")
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=15
                )
                if result.returncode != 0:
                    err = (result.stderr or result.stdout or "").strip()
                    details.append(f"{step_name}失败({err[:60]})")
                    return False, " | ".join(details)
                details.append(f"{step_name}OK")
            except subprocess.TimeoutExpired:
                details.append(f"{step_name}超时")
                return False, " | ".join(details)
            except Exception as e:
                details.append(f"{step_name}异常({e})")
                return False, " | ".join(details)
            finally:
                self._screenshot_process = None
        
        # 4) 校验文件确实拉下来了
        if not os.path.exists(local_path):
            return False, " | ".join(details) + f" | 本地文件不存在: {local_path}"
        
        details.append(f"保存→{local_path}")
        return True, " | ".join(details)

    def _do_screenshot_8797(self, current_cycle, save_folder):
        """8797 截图：生成四张临时图，逐张重命名、拉取，最后删除车机文件。"""
        from datetime import datetime as datetime_class

        timestamp = datetime_class.now().strftime("%Y%m%d%H%M%S")
        cycle_text = str(current_cycle if current_cycle and current_cycle > 0 else 0)
        local_dir = os.path.join(
            os.path.normpath(save_folder) if save_folder else os.getcwd(),
            "截图",
        )
        try:
            os.makedirs(local_dir, exist_ok=True)
        except Exception as exc:
            return False, f"创建目录失败: {exc}"

        def run_command(cmd, timeout=30):
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                output = "\n".join(
                    part.strip()
                    for part in (result.stdout, result.stderr)
                    if part and part.strip()
                )
                return result.returncode == 0, output
            except Exception as exc:
                return False, str(exc)

        capture_cmd = 'adb shell "screencap -a -p /tmp/"'
        print(f"[8797截图] 生成截图: {capture_cmd}")
        captured, capture_output = run_command(capture_cmd, timeout=30)
        if not captured:
            return False, f"生成截图失败: {capture_output or '命令执行失败'}"

        remote_targets = []
        pulled_files = []
        failures = []
        try:
            for index in range(4):
                target_name = f"{index}+{cycle_text}+{timestamp}.png"
                remote_target = f"/tmp/{target_name}"
                local_path = os.path.join(local_dir, target_name)
                remote_targets.append(remote_target)

                rename_cmd = (
                    f'adb shell "if [ -f /tmp/_{index}.png ]; then '
                    f'mv /tmp/_{index}.png {remote_target}; '
                    f'elif [ -f /tmp/_{index} ]; then '
                    f'mv /tmp/_{index} {remote_target}; '
                    f'else exit 1; fi"'
                )
                renamed, rename_output = run_command(rename_cmd, timeout=15)
                if not renamed:
                    failures.append(f"_{index}重命名失败: {rename_output or '文件不存在'}")
                    continue

                pull_cmd = f'adb pull "{remote_target}" "{local_path}"'
                print(f"[8797截图] 拉取第 {index} 张: {pull_cmd}")
                pulled, pull_output = run_command(pull_cmd, timeout=30)
                if pulled and os.path.exists(local_path):
                    pulled_files.append(local_path)
                else:
                    failures.append(f"_{index}拉取失败: {pull_output or '文件不存在'}")
        finally:
            cleanup_paths = remote_targets + [
                f"/tmp/_{index}" for index in range(4)
            ] + [
                f"/tmp/_{index}.png" for index in range(4)
            ]
            cleanup_cmd = 'adb shell "rm -f ' + " ".join(cleanup_paths) + '"'
            cleaned, cleanup_output = run_command(cleanup_cmd, timeout=15)
            if not cleaned:
                failures.append(f"删除车机截图失败: {cleanup_output or '命令执行失败'}")

        if failures:
            return False, f"已拉取 {len(pulled_files)}/4 张；" + "；".join(failures)
        return True, f"已保存 4 张截图: {os.path.abspath(local_dir)}"
    
    def compare_results(self, baseline, actual, tolerance, exact_compare_fields=None, value_normalizer=None):
        """带容差的结果对比"""
        all_pass = True
        details = {}
        exact_compare_fields = set(exact_compare_fields or [])
        exact_compare_all = "*" in exact_compare_fields
        switch_state_fields = {"语音服务开关状态", "千万大模型开关状态"}
        compressor_state_fields = {"压缩机状态"}
        
        for name, baseline_val in baseline.items():
            actual_val = actual.get(name)
            
            # 检查基准值是否有效
            if baseline_val is None:
                details[name] = {"status": "error", "msg": "基准值无效，请重新采集基准"}
                all_pass = False
                continue
            
            # 检查实际值是否有效
            if actual_val is None:
                details[name] = {"status": "error", "msg": "读取失败"}
                all_pass = False
                continue

            # 压缩机状态只判断开/关（0/非0），不要求非零状态与基准数值完全相等。
            # 这样可以兼容不同车型或时刻返回的具体转速/状态码。
            if name in compressor_state_fields:
                try:
                    baseline_num = float(baseline_val)
                    actual_num = float(actual_val)
                    baseline_on = baseline_num != 0
                    actual_on = actual_num != 0
                    is_pass = baseline_on == actual_on
                    details[name] = {
                        "status": "pass" if is_pass else "fail",
                        "baseline": baseline_val,
                        "actual": actual_val,
                        "msg": (
                            "压缩机状态零/非零一致"
                            if is_pass
                            else "压缩机状态不一致：基准为零时实际必须为零，基准非零时实际必须非零"
                        ),
                    }
                    if not is_pass:
                        all_pass = False
                    continue
                except (TypeError, ValueError):
                    # 非数字返回值沿用原有文本比较逻辑。
                    pass
            
            # 数值字段按容差对比；指定字段的字符串按精确文本对比，其他非数值字段沿用仅记录逻辑。
            if not (isinstance(baseline_val, (int, float)) and isinstance(actual_val, (int, float))):
                if exact_compare_all or name in exact_compare_fields:
                    baseline_text = str(self._normalize_compare_value(baseline_val, value_normalizer, name)).strip()
                    actual_text = str(self._normalize_compare_value(actual_val, value_normalizer, name)).strip()
                    baseline_display = self._format_exact_compare_value(name, baseline_text)
                    actual_display = self._format_exact_compare_value(name, actual_text)
                    if name in switch_state_fields and baseline_display in ("开", "关") and actual_display in ("开", "关"):
                        is_pass = actual_display == baseline_display
                    else:
                        is_pass = actual_text == baseline_text
                    details[name] = {
                        "status": "pass" if is_pass else "fail",
                        "baseline": baseline_val,
                        "actual": actual_val,
                        "msg": "状态一致" if is_pass and name in switch_state_fields else ("文本一致" if is_pass else self._format_exact_compare_msg(name, baseline_text, actual_text)),
                        "display_actual": actual_display
                    }
                    if not is_pass:
                        all_pass = False
                    continue

                details[name] = {
                    "status": "pass",
                    "baseline": baseline_val,
                    "actual": actual_val,
                    "msg": "非数值字段，仅记录"
                }
                continue
            
            diff = abs(actual_val - baseline_val)
            is_pass = diff <= tolerance
            
            details[name] = {
                "status": "pass" if is_pass else "fail",
                "baseline": baseline_val,
                "actual": actual_val,
                "diff": diff
            }
            
            if not is_pass:
                all_pass = False
        
        return {"all_pass": all_pass, "details": details}

    def compare_step_board_status(self, baseline, actual, tolerance=3):
        """按左右两侧分别校验踏板状态和位置。"""
        all_pass = True
        details = {}
        summary_items = []

        for side in ("左侧", "右侧"):
            status_field = f"{side}踏板状态"
            position_field = f"{side}踏板位置"
            actual_status = actual.get(status_field)
            target_status = baseline.get(status_field)
            actual_position = actual.get(position_field)
            target_position = baseline.get(position_field)

            status_pass = (
                actual_status in self.STEP_BOARD_STATUS_VALUES_8797
                and target_status in self.STEP_BOARD_STATUS_VALUES_8797
                and actual_status == target_status
            )
            position_diff = None
            position_pass = False
            if (
                not isinstance(actual_position, bool)
                and not isinstance(target_position, bool)
                and isinstance(actual_position, (int, float))
                and isinstance(target_position, (int, float))
            ):
                position_diff = abs(actual_position - target_position)
                position_pass = position_diff <= tolerance

            details[status_field] = {
                "status": "pass" if status_pass else "fail",
                "baseline": target_status,
                "actual": actual_status,
                "msg": (
                    "状态一致"
                    if status_pass
                    else f"状态不一致：目标={target_status}, 实际={actual_status}"
                ),
            }
            details[position_field] = {
                "status": "pass" if position_pass else "fail",
                "baseline": target_position,
                "actual": actual_position,
                "diff": position_diff,
                "msg": (
                    f"位置偏差 {position_diff}，允许偏差 ±{tolerance}"
                    if position_diff is not None
                    else "位置值无效"
                ),
            }

            side_pass = status_pass and position_pass
            all_pass = all_pass and side_pass
            side_result = "通过"
            if not side_pass:
                reasons = []
                if not status_pass:
                    reasons.append(
                        f"状态不一致(目标={target_status},实际={actual_status})"
                    )
                if not position_pass:
                    reasons.append(
                        f"位置偏差超限(偏差={position_diff},允许±{tolerance})"
                        if position_diff is not None
                        else "位置读取无效"
                    )
                side_result = f"失败（{'；'.join(reasons)}）"

            actual[f"{side}踏板目标位置"] = target_position
            actual[f"{side}踏板位置偏差"] = position_diff
            actual[f"{side}踏板校验结果"] = side_result
            details[f"{side}踏板校验结果"] = {
                "status": "pass" if side_pass else "fail",
                "msg": side_result,
            }

            summary_items.extend([
                f"{side}踏板原始状态 sigVal={actual.get(f'{side}踏板原始状态 sigVal')}",
                f"{side}踏板中文状态={actual.get(f'{side}踏板中文状态')}",
                f"{side}踏板原始位置 sigVal={actual.get(f'{side}踏板原始位置 sigVal')}",
                f"{side}踏板目标位置={target_position}",
                f"{side}踏板位置偏差={position_diff}",
                f"{side}踏板校验结果={side_result}",
            ])

        raw_output = actual.get("原始 vapisend 返回内容", "")
        summary = "；".join(summary_items)
        if raw_output:
            summary += f"\n原始 vapisend 返回内容:\n{raw_output}"
        return {
            "all_pass": all_pass,
            "details": details,
            "summary": summary,
        }

    def _format_exact_compare_value(self, name, value):
        if name == "语音服务开关状态":
            if "/ON/" in value:
                return "开"
            if "/OFF/" in value:
                return "关"
        if name == "千万大模型开关状态":
            normalized = str(value).strip().lower()
            if normalized in ("1", "true", "on", "enable", "enabled"):
                return "开"
            if normalized in ("0", "false", "off", "disable", "disabled"):
                return "关"
        return value

    def _format_exact_compare_msg(self, name, baseline_value, actual_value):
        if name in ("语音服务开关状态", "千万大模型开关状态"):
            baseline_display = self._format_exact_compare_value(name, baseline_value)
            actual_display = self._format_exact_compare_value(name, actual_value)
            return f"基准={baseline_display},实际={actual_display}"
        return "基准值与实际值不一致"
    
    def execute_and_compare(self, instruction_name, extra_wait=0, current_cycle=1, save_folder="", is_baseline_test=False):
        """
        🎯 Play按钮调用：完整执行单条测试指令
        执行 → 采集 → 判断 → 截图（失败时）→ 返回结果
        :param is_baseline_test: 是否是基准测试
        """
        baseline_instruction_name = self._baseline_instruction_name(instruction_name)
        instruction_name = self._canonical_instruction_name(instruction_name)
        config = self._get_instruction_config(instruction_name)
        self.last_execution_detail = {
            "instruction": baseline_instruction_name,
            "cycle": current_cycle,
            "actual": None,
            "baseline": None,
            "details": None,
            "tolerance": None,
            "error": None,
        }
        is_visual_only = config.get("is_visual_only", False)
        is_wait_only = config.get("is_wait_only", False)
        is_screenshot = config.get("is_screenshot", False)
        is_audio_detection = config.get("special_type", "") == "audio_detection"
        
        # 🎯 截图指令：把保存路径和循环次数注入实例属性，供 execute_and_collect 使用
        if is_screenshot:
            self._screenshot_save_folder = save_folder
            self._screenshot_current_cycle = current_cycle
        
        # 🎯 音频探测指令：设置保存路径和循环次数
        if is_audio_detection:
            self._save_folder = save_folder
            self._audio_current_cycle = current_cycle

        if config.get("special_type") == "lastmode_cache":
            self._save_folder = save_folder
            self._lastmode_current_cycle = current_cycle
        
        # 1. 执行并采集结果
        actual_results, tolerance, error = self.execute_and_collect(instruction_name, extra_wait)
        self.last_execution_detail.update({
            "actual": actual_results,
            "tolerance": tolerance,
            "error": error,
        })
        
        if error:
            return f"❌执行失败: {error}"
        
        # 🎯 音频探测指令：只跟音量阈值对比，不跟基准对比
        if is_audio_detection:
            avg_volume = actual_results.get("平均音量", 0)
            threshold = actual_results.get("音量阈值", 30)
            
            # 对比平均音量和阈值
            if avg_volume < threshold:
                # 失败
                self.last_execution_detail["details"] = {"平均音量": avg_volume, "音量阈值": threshold}
                return f"❌失败|平均音量={avg_volume},阈值={threshold}"
            else:
                # 成功
                self.last_execution_detail["details"] = {"平均音量": avg_volume, "音量阈值": threshold}
                return f"✅成功|平均音量={avg_volume},阈值={threshold}"
        
        # 🎯 截图指令：三个 adb 全部成功就 pass，无需基准
        if is_screenshot:
            ok = actual_results.get("_screenshot_ok", False)
            info = actual_results.get("_screenshot_info", "")
            self.last_execution_detail["details"] = {"截图结果": ok, "截图信息": info}
            if ok:
                return f"✅截图成功|{info}"
            else:
                return f"❌截图失败|{info}"
        
        # 🎯 纯等待指令：基准测试显示空结果，循环测试直接成功
        if is_wait_only:
            total_wait = self.sleep_wake_delay
            # 检查是否有基准（基准测试保存空结果）
            baseline = self.get_baseline(baseline_instruction_name)
            if is_baseline_test:
                # 基准测试：首次执行自动保存空基准
                if not baseline:
                    self.save_baseline(baseline_instruction_name, {})
                return f"✅基准已保存|第{current_cycle}次循环,等待{total_wait}s"
            else:
                # 循环测试：等待完成，直接成功
                return f"✅执行成功|第{current_cycle}次循环,等待{total_wait}s"

        # 🎯 诊断类动作可声明不做基准对比，仅记录执行结果
        if config.get("skip_baseline_compare", False):
            result_text = " ".join([f"{k}:{v}" for k, v in (actual_results or {}).items()])
            self.last_execution_detail["details"] = {"skip_baseline_compare": True}
            if result_text:
                return f"✅执行成功|{result_text}"
            return "✅执行成功"
        
        # 🎯 没有result_cmds的指令：执行成功就通过，无需基准对比
        # 注意：排除视觉检测指令（is_visual_only）和音频探测指令，它们有单独的判断逻辑
        result_cmds = config.get("result_cmds", [])
        if (
            not result_cmds
            and not is_visual_only
            and not is_audio_detection
            and config.get("special_type") != "lastmode_cache"
        ):
            # 直接返回执行成功，不管是不是基准测试
            # (基准测试会在上层逻辑中保存基准)
            self.last_execution_detail["details"] = {"no_result_cmds": True}
            return f"✅执行成功"
        
        # 🎯 纯视觉检测指令：亮度判断 + 图像对比，任一失败都截图
        if is_visual_only:
            from Subpy.visual_detector import get_visual_detector
            import os
            
            detector = get_visual_detector()
            threshold = detector.brightness_threshold
            
            print(f"[视觉检测] 阈值={threshold}, 结果={actual_results}")
            
            # 🎯 确保摄像头一定打开并抓取新帧
            if detector.cap is None or not detector.cap.isOpened():
                print(f"[视觉检测] 自动打开摄像头 {detector.camera_port}...")
                detector.open_camera(detector.camera_port)
                if not self.interruptible_sleep(0.3):
                    return "❌执行失败: 测试已停止"
            
            # 确保有图像
            if detector.current_frame is None:
                ret, frame = detector.cap.read()
                if ret:
                    detector.current_frame = frame
            
            # 1) 亮度判断（重新计算，不依赖 execute_and_collect）
            brightness_pass = True
            detail_items = []
            
            if len(detector.roi_list) > 0 and detector.current_frame is not None:
                for i, roi in enumerate(detector.roi_list):
                    brightness = detector.calculate_brightness(detector.current_frame, roi)
                    name = f"区域{i+1}_亮度"
                    if brightness >= threshold:
                        detail_items.append(f"{name}:✓({brightness})")
                    else:
                        detail_items.append(f"{name}:×({brightness})")
                        brightness_pass = False
            
            # 2) 图像对比（与基准帧）
            image_diff_pass = True
            diff_info = ""
            current_frame = detector.current_frame
            if (detector.reference_frame is not None 
                and current_frame is not None 
                and len(detector.roi_list) > 0):
                diff_list = []
                all_same = True
                for roi in detector.roi_list:
                    is_same, diff = detector.compare_images(
                        detector.reference_frame, current_frame, roi,
                        threshold=detector.image_diff_threshold
                    )
                    diff_list.append(round(diff, 1))
                    if not is_same:
                        all_same = False
                image_diff_pass = all_same
                diff_info = f" | 图像差异{diff_list}"
            
            result_text = " ".join(detail_items) + diff_info
            
            # 3) 截图触发条件：亮度不够 或 图像变化（任一不满足都截图）
            need_screenshot = (not brightness_pass) or (not image_diff_pass)
            if need_screenshot:
                print(f"[视觉检测] 触发截图：亮度={brightness_pass}, 图像={image_diff_pass}")
                
                if save_folder:
                    save_folder = os.path.normpath(save_folder)
                    detector.save_folder = os.path.join(save_folder, "快照记录")
                
                if detector.current_frame is None and detector.cap:
                    ret, frame = detector.cap.read()
                    if ret:
                        detector.current_frame = frame
                
                if detector.current_frame is not None:
                    # 截图前缀（描述触发原因）
                    if not brightness_pass and not image_diff_pass:
                        prefix = "黑屏且画面变化"
                    elif not brightness_pass:
                        prefix = "黑屏异常"
                    else:
                        prefix = "画面变化"
                    detector.save_screenshot(current_cycle, prefix=prefix)
            
            # 4) 结果判断：仅看亮度（图像变化只触发截图，不影响结果）
            if not brightness_pass:
                return f"❌黑屏异常|{result_text}"
            else:
                return f"✅亮屏正常|{result_text}"
        
        # 2. 读取基准
        baseline = self.get_baseline(baseline_instruction_name)
        self.last_execution_detail["baseline"] = baseline
        if not baseline:
            # 没有基准，只显示结果
            result_text = " ".join([f"{k}:{v}" for k, v in actual_results.items()])
            self.last_execution_detail["details"] = {"message": "无基准"}
            return f"⚠️无基准|{result_text}"

        if config.get("special_type") == "step_board_status":
            compare_result = self.compare_step_board_status(
                baseline, actual_results, tolerance
            )
            all_pass = compare_result["all_pass"]
            self.last_execution_detail.update({
                "actual": actual_results,
                "details": compare_result["details"],
                "all_pass": all_pass,
            })
            prefix = "✅通过" if all_pass else "❌失败"
            return f"{prefix}|{compare_result['summary']}"
        
        # 3. 和基准对比
        compare_result = self.compare_results(
            baseline,
            actual_results,
            tolerance,
            config.get("exact_compare_fields", []),
            config.get("value_normalizer")
        )
        all_pass = compare_result["all_pass"]
        details = compare_result["details"]
        self.last_execution_detail.update({
            "details": details,
            "all_pass": all_pass,
        })
        
        # 4. 拼接结果文本（给表格显示）
        detail_items = []
        for name, d in details.items():
            if d["status"] == "pass":
                if d.get("display_actual"):
                    detail_items.append(f"{name}:✓({d['display_actual']})")
                else:
                    detail_items.append(f"{name}:✓")
            elif d["status"] == "fail":
                if "diff" in d:
                    detail_items.append(f"{name}:×(差{d['diff']})")
                elif d.get("msg"):
                    detail_items.append(f"{name}:×({d['msg']})")
                else:
                    detail_items.append(f"{name}:×")
            else:
                detail_items.append(f"{name}:{d.get('msg', '错误')}")
        
        result_text = " ".join(detail_items)
        if all_pass:
            return f"✅通过|{result_text}"
        else:
            return f"❌失败|{result_text}"
    
    def run_test(self, instruction_name, extra_wait=0):
        """测试入口
        extra_wait: 额外等待时间（从界面输入）
        """
        baseline_instruction_name = self._baseline_instruction_name(instruction_name)
        instruction_name = self._canonical_instruction_name(instruction_name)
        config = self._get_instruction_config(instruction_name)
        is_screenshot = config.get("is_screenshot", False)
        
        # 🎯 截图指令：基准测试时拉到执行程序目录（save_folder=""）
        if is_screenshot:
            self._screenshot_save_folder = ""   # 空 → 拉到当前工作目录
            self._screenshot_current_cycle = 0  # 0 → 文件名只用时间戳
        
        # 执行并采集
        actual_results, tolerance, error = self.execute_and_collect(instruction_name, extra_wait)
        if error:
            return {
                "status": "error",
                "message": error
            }
        
        # 🎯 截图指令：三个 adb 全部成功就 pass，并把空结果当作基准保存
        if is_screenshot:
            ok = actual_results.get("_screenshot_ok", False)
            info = actual_results.get("_screenshot_info", "")
            if not self.has_baseline(baseline_instruction_name):
                self.save_baseline(baseline_instruction_name, {})  # 空基准
            if ok:
                return {
                    "status": "pass",
                    "message": f"截图成功: {info}",
                    "results": {}
                }
            else:
                return {
                    "status": "error",
                    "message": f"截图失败: {info}",
                    "results": {}
                }

        if config.get("skip_baseline_compare", False):
            result_text = " ".join([f"{k}:{v}" for k, v in (actual_results or {}).items()])
            return {
                "status": "pass",
                "message": f"执行成功: {result_text}" if result_text else "执行成功",
                "results": actual_results or {}
            }
        
        # 第一次执行 → 存基准
        if not self.has_baseline(baseline_instruction_name):
            save_ok = self.save_baseline(baseline_instruction_name, actual_results)
            if save_ok:
                return {
                    "status": "baseline_created",
                    "message": f"首次执行，已创建基准",
                    "results": actual_results
                }
            else:
                return {
                    "status": "error",
                    "message": f"读取结果包含无效值，无法创建基准",
                    "results": actual_results
                }
        
        # 非第一次 → 对比
        baseline = self.get_baseline(baseline_instruction_name)
        if config.get("special_type") == "step_board_status":
            compare_result = self.compare_step_board_status(
                baseline, actual_results, tolerance
            )
        else:
            compare_result = self.compare_results(
                baseline,
                actual_results,
                tolerance,
                config.get("exact_compare_fields", []),
                config.get("value_normalizer")
            )
        
        return {
            "status": "pass" if compare_result["all_pass"] else "fail",
            "message": compare_result.get(
                "summary",
                "测试通过" if compare_result["all_pass"] else "存在偏差",
            ),
            "baseline": baseline,
            "actual": actual_results,
            "details": compare_result["details"],
            "tolerance": tolerance
        }
    
    def reset_baseline(self, instruction_name, extra_wait=0):
        """重新采集指定指令的基准"""
        baseline_instruction_name = self._baseline_instruction_name(instruction_name)
        instruction_name = self._canonical_instruction_name(instruction_name)
        actual_results, _, error = self.execute_and_collect(instruction_name, extra_wait)
        if error:
            return False, error
        self.save_baseline(baseline_instruction_name, actual_results)
        return True, "基准已更新"
    
    def get_all_instruction_names(self, vehicle_platform="8295"):
        """获取指定车型平台可用的指令名称列表。"""
        platform = str(vehicle_platform or "8295").strip()
        platform_names = self.PLATFORM_INSTRUCTION_NAMES.get(platform)
        if not platform_names:
            return [
                name
                for name, config in self.instructions.items()
                if not isinstance(config, dict)
                or not config.get("platforms")
                or platform in config.get("platforms", ())
            ]

        # 按白名单顺序返回，同时忽略尚未配置到执行器中的名称。
        return [
            name for name in platform_names
            if name in self.instructions
        ]
    
    # ==================== 继电器控制相关方法 ====================
    def set_relay_config(self, port=None, baudrate=None, channel_map=None):
        """设置继电器配置"""
        if port:
            self.relay_port = port
        if baudrate:
            self.relay_baudrate = baudrate
        if channel_map:
            self.relay_channel_map.update(channel_map)
        print(f"[继电器] 配置已更新:")
        print(f"  串口: {self.relay_port}")
        print(f"  通道映射: {self.relay_channel_map}")
    
    def control_relay(self, channel, action='on'):
        """
        控制继电器通道
        :param channel: 通道号 (1-8)
        :param action: 'on' 或 'off'
        """
        try:
            if isinstance(channel, str):
                channel = int(channel)
        except ValueError:
            print(f"无效的通道号: {channel}")
            return False
        
        # 构造指令
        if action == 'on':
            # 打开指令: A0 XX 01 YY
            checksum = 0xA0 + channel + 0x01
            cmd = bytes([0xA0, channel, 0x01, checksum])
        else:
            # 关闭指令: A0 XX 00 YY
            checksum = 0xA0 + channel + 0x00
            cmd = bytes([0xA0, channel, 0x00, checksum])
        
        try:
            ser = serial.Serial(self.relay_port, self.relay_baudrate, timeout=1)
            print(f"[继电器] 发送指令: {' '.join(f'{b:02X}' for b in cmd)}")
            ser.write(cmd)
            self.interruptible_sleep(0.1)
            ser.close()
            return True
        except Exception as e:
            print(f"[继电器] 控制失败: {e}")
            return False
    
    def press_relay(self, channel, duration=2.0):
        """
        模拟按下动作：打开 -> 等待 -> 关闭
        :param channel: 通道号
        :param duration: 按下持续时间（秒）
        """
        print(f"[继电器] 按下通道 {channel}，持续 {duration} 秒")
        if not self.control_relay(channel, 'on'):
            return False
        try:
            if not self.interruptible_sleep(duration):
                print(f"[继电器] 收到停止请求，提前释放通道 {channel}")
                return False
        finally:
            if not self.control_relay(channel, 'off'):
                return False
        print(f"[继电器] 通道 {channel} 已释放")
        return True
    
    def execute_relay_command(self, command_name, duration=2.0):
        """
        执行继电器控制指令
        :param command_name: 指令名称（如"踩刹车"）
        :param duration: 按下持续时间
        """
        if command_name not in self.relay_channel_map:
            print(f"[继电器] 未找到指令: {command_name}")
            return False
        
        channel = self.relay_channel_map[command_name]
        print(f"[继电器] 执行指令: {command_name} -> 通道 {channel}")
        return self.press_relay(channel, duration)
    
    def send_robot_command(self, command, robot_ip=None, robot_port=None, robot_timeout=None):
        """
        通过TCP/IP发送机器人控制指令
        :param command: 机器人指令（如"lock"、"unlockopen"、"closedoor"）
        :return: 是否发送成功
        """
        robot_ip = robot_ip or self.robot_ip
        robot_port = int(robot_port or self.robot_port)
        robot_timeout = float(robot_timeout or self.robot_timeout)
        try:
            print(f"[机器人] 发送指令: '{command}' -> {robot_ip}:{robot_port}")
            
            # 创建TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(robot_timeout)
            
            print(f"[机器人] 正在连接...")
            sock.connect((robot_ip, robot_port))
            print(f"[机器人] 连接成功!")
            
            # 发送指令（格式：run(指令.jspf)，不带换行符）
            full_command = f'run({command}.jspf)'
            send_data = full_command.encode('utf-8')
            print(f"[机器人] 发送数据: {send_data} (长度: {len(send_data)}字节)")
            sock.sendall(send_data)
            print(f"[机器人] 发送完成!")
            
            # 短暂等待后关闭连接
            self.interruptible_sleep(0.1)
            sock.close()
            
            print(f"[机器人] 指令发送成功: {command}")
            return True
            
        except socket.timeout:
            print(f"[机器人] 连接超时: {robot_ip}:{robot_port}")
            return False
        except ConnectionRefusedError:
            print(f"[机器人] 连接被拒绝: {robot_ip}:{robot_port}")
            print(f"[机器人] 请检查机器人是否开机、IP是否正确、端口是否正确")
            return False
        except Exception as e:
            print(f"[机器人] 发送失败: {e}")
            import traceback
            print(f"[机器人] 错误详情: {traceback.format_exc()}")
            return False
    
    def set_wait_params(self, sleep_wake_delay=0.0, increment_time=0.0):
        """
        设置等待指令的参数（由综合测试面板传入）
        :param sleep_wake_delay: 休眠唤醒延迟时间（秒）
        :param increment_time: 递增时间（秒）
        """
        try:
            self.sleep_wake_delay = float(sleep_wake_delay) if sleep_wake_delay else 0.0
        except:
            self.sleep_wake_delay = 0.0
        self.initial_sleep_wake_delay = self.sleep_wake_delay
        
        try:
            self.increment_time = float(increment_time) if increment_time else 0.0
        except:
            self.increment_time = 0.0
        
        print(f"[等待] 参数已更新: 休眠唤醒延迟={self.sleep_wake_delay}s, 递增时间={self.increment_time}s, 总等待={self.sleep_wake_delay + self.increment_time}s")

    def set_current_wait_for_cycle(self, cycle):
        """按循环号计算当前等待，避免把运行时累计值写回配置。"""
        try:
            cycle = int(cycle)
        except (TypeError, ValueError):
            cycle = 1
        cycle = max(1, cycle)
        current_wait = self.initial_sleep_wake_delay + self.increment_time * (cycle - 1)
        self.current_cycle_count = cycle
        self.sleep_wake_delay = max(0.0, current_wait)
        print(f"[等待] 第{cycle}次循环, 当前等待时间={self.sleep_wake_delay}s")
        return self.sleep_wake_delay
    
    def reset_cycle_count(self):
        """重置循环计数（开始新测试时调用）"""
        self.current_cycle_count = 0
        print(f"[等待] 循环计数已重置")
    
    def increment_cycle(self):
        """递增循环计数（每次循环开始时调用）"""
        self.current_cycle_count += 1
        current_wait = self.get_current_wait_time()
        print(f"[等待] 第{self.current_cycle_count}次循环, 等待时间={current_wait}s")
    
    def reset_cycle_count(self):
        """重置循环计数为0"""
        self.current_cycle_count = 0
        print(f"[等待] 循环计数已重置")
    
    def get_current_wait_time(self):
        """
        获取当前循环的等待时间
        第1次：休眠唤醒延迟时间
        第2次：休眠唤醒延迟时间 + 递增时间
        第3次：休眠唤醒延迟时间 + 递增时间 × 2
        ...
        """
        if self.current_cycle_count <= 1:
            return self.initial_sleep_wake_delay
        else:
            return self.initial_sleep_wake_delay + self.increment_time * (self.current_cycle_count - 1)
    
    def execute_audio_detection(self, save_folder="", duration_seconds=10, threshold_percent=30):
        """
        执行音频探测（特殊指令）
        :param save_folder: 保存文件夹
        :param duration_seconds: 采集时长（秒）
        :param threshold_percent: 音量下限（百分比）
        :return: (results, tolerance, error)
        """
        try:
            print(f"[音频探测] 开始执行，时长={duration_seconds}s，阈值={threshold_percent}%")
            
            # 获取当前循环次数
            current_cycle = getattr(self, "_audio_current_cycle", 0)
            
            # 导入音频探测模块
            from Subpy.audio_detection import AudioDetector
            
            # 创建日志回调函数
            def log_callback(msg):
                print(f"[音频探测] {msg}")
            
            # 执行音频探测
            detector = AudioDetector(log_callback)
            # 传入循环次数，用于文件名
            result = detector.detect(duration_seconds, save_folder, threshold_percent, current_cycle)
            
            if result["success"]:
                # 成功：返回完整结果用于显示
                results = {
                    "平均音量": round(result["avg_volume"], 2),
                    "是否静音": "是" if result["is_silent"] else "否",
                    "音量阈值": threshold_percent,
                    "采集时长": duration_seconds,
                    "音频文件": result.get("audio_file", "")
                }
                print(f"[音频探测] 执行成功，结果={results}")
                # 容差设置为5.0（百分比）
                return results, 5.0, None
            else:
                # 失败
                return {}, 5.0, result.get("error", "音频探测失败")
                
        except ImportError as e:
            print(f"[音频探测] 模块导入失败: {e}")
            return {}, 0, f"音频探测模块导入失败: {e}"
        except Exception as e:
            print(f"[音频探测] 执行失败: {e}")
            import traceback
            print(f"[音频探测] 错误详情: {traceback.format_exc()}")
            return {}, 0, f"音频探测执行失败: {e}"

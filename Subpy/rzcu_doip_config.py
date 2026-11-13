#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RZCU (Right Zone Control Unit) DoIP 配置
===============================================
RZCU 右区域控制器 - 通过 ICB 网关转发访问

物理地址：0x17E3 (用户确认)
"""

# DoIP 网关配置 (通过 ICB 转发)
RZCU_DOIP_IP = "172.31.6.11"    # ICB 网关 IP (8295_QNX)
RZCU_DOIP_PORT = 13400          # ICB DoIP 端口

# 网关逻辑地址
RZCU_LOGICAL_ADDR = 0x1000      # ICB 逻辑地址

# RZCU 诊断地址
RZCU_PHYSICAL_ADDR = 0x17E3     # RZCU 逻辑地址 (用户确认)
RZCU_RESPONSE_ADDR = 0x1863     # RZCU 响应地址 (0x17E3 + 0x80)

# 路由激活目标地址 (与 ICB 相同)
RZCU_ROUTING_TA = 0x0010

# Tester 逻辑地址
TESTER_LOGICAL_ADDR = 0x0E80

# 安全访问算法号 (用户确认)
RZCU_SECURITY_ALGO = 0x105A     # ✅ 用户确认算法号

# ── 诊断配置 ──
RZCU_DIAG_CONFIG = {
    "name": "RZCU",
    "description": "Right Zone Control Unit (右区域控制器)",
    "supplier": "待确认",
    "version": "待确认",

    "supported_services": {
        "10": "DiagnosticSessionControl",
        "11": "ECUReset",
        "14": "ClearDiagnosticInformation",
        "19": "ReadDTCInformation",
        "22": "ReadDataByIdentifier",
        "27": "SecurityAccess",
        "28": "CommunicationControl",
        "2E": "WriteDataByIdentifier",
        "2F": "InputOutputControlByIdentifier",
        "31": "RoutineControl",
        "3E": "TesterPresent",
        "85": "ControlDTCSetting",
    },
    "sessions": {
        "01": "Default Session",
        "02": "Programming Session",
        "03": "Extended Diagnostic Session",
    },
    "reset_types": {
        "01": "Hard Reset",
        "02": "Key Off Reset",
        "03": "Soft Reset",
    },
    "security_levels": {
        "01/02": "Level 1 (Default/Extended)",
        "03/04": "Level 2 (Extended)",
        "05/06": "Level 3 (Extended/Programming)",
        "09/0A": "Level 4 (Programming)",
        "61/62": "Level 5 (Development)",
    },
    "security_algo": f"{RZCU_SECURITY_ALGO:08X}",  # 000011E9
}

__all__ = [
    "RZCU_DOIP_IP",
    "RZCU_DOIP_PORT",
    "RZCU_LOGICAL_ADDR",
    "RZCU_PHYSICAL_ADDR",
    "RZCU_RESPONSE_ADDR",
    "RZCU_ROUTING_TA",
    "TESTER_LOGICAL_ADDR",
    "RZCU_SECURITY_ALGO",
    "RZCU_DIAG_CONFIG",
]

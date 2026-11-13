#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RHZCU (Right Head Zone Control Unit) DoIP 配置
===============================================
RHZCU 右域控制器 (UAES) - 通过 ICB 网关转发访问

Part4: 3.0-PPV-RHZCU-ZONE Part4-V2.3-20241114
物理地址: 0x15B1 (DoCAN: 0x5B1 / 0x5B9)
供应商: 联合汽车电子 (UAES)
安全算法: 0x1010 (与 LHZCU 共用)
"""

# DoIP 网关配置 (通过 ICB 转发)
RHZCU_DOIP_IP = "172.31.6.11"    # ICB 网关 IP (8295_QNX)
RHZCU_DOIP_PORT = 13400          # ICB DoIP 端口

# 网关逻辑地址
RHZCU_LOGICAL_ADDR = 0x1000      # ICB 逻辑地址

# RHZCU 诊断地址
RHZCU_PHYSICAL_ADDR = 0x15B1     # RHZCU 逻辑地址 (Part4 Cover 表)
RHZCU_RESPONSE_ADDR = 0x1631     # RHZCU 响应地址 (0x15B1 + 0x80)

# 路由激活目标地址 (与 ICB 相同)
RHZCU_ROUTING_TA = 0x0010

# Tester 逻辑地址
TESTER_LOGICAL_ADDR = 0x0E80

# 安全访问算法号 (与 LHZCU 共用)
RHZCU_SECURITY_ALGO = 0x1010

# ── 诊断配置 ──
RHZCU_DIAG_CONFIG = {
    "name": "RHZCU",
    "description": "Right Head Zone Control Unit (右域控制器)",
    "supplier": "UAES",
    "version": "V2.3 20241114",

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
    "security_algo": f"{RHZCU_SECURITY_ALGO:08X}",
}

__all__ = [
    "RHZCU_DOIP_IP",
    "RHZCU_DOIP_PORT",
    "RHZCU_LOGICAL_ADDR",
    "RHZCU_PHYSICAL_ADDR",
    "RHZCU_RESPONSE_ADDR",
    "RHZCU_ROUTING_TA",
    "TESTER_LOGICAL_ADDR",
    "RHZCU_SECURITY_ALGO",
    "RHZCU_DIAG_CONFIG",
]
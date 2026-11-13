#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LHZCU (Left Head Zone Control Unit) DoIP 配置
===============================================
LHZCU 左域控制器 (UAES) - 通过 ICB 网关转发访问

Part4: 3.0-SOP-LHZCU-ZONE Part4-V4.1-UAES_20250416
物理地址: 0x15B0 (DoCAN: 0x5B0 / 0x5B8)
供应商: 联合汽车电子 (UAES)
"""

# DoIP 网关配置 (通过 ICB 转发)
LHZCU_DOIP_IP = "172.31.6.11"    # ICB 网关 IP (8295_QNX)
LHZCU_DOIP_PORT = 13400          # ICB DoIP 端口

# 网关逻辑地址
LHZCU_LOGICAL_ADDR = 0x1000      # ICB 逻辑地址

# LHZCU 诊断地址
LHZCU_PHYSICAL_ADDR = 0x15B0     # LHZCU 逻辑地址 (Part4 Cover 表)
LHZCU_RESPONSE_ADDR = 0x1630     # LHZCU 响应地址 (0x15B0 + 0x80)

# 路由激活目标地址 (与 ICB 相同)
LHZCU_ROUTING_TA = 0x0010

# Tester 逻辑地址
TESTER_LOGICAL_ADDR = 0x0E80

# 安全访问算法号
LHZCU_SECURITY_ALGO = 0x1010     # 已验证: LHZCU & RHZCU 共用

# ── 诊断配置 ──
LHZCU_DIAG_CONFIG = {
    "name": "LHZCU",
    "description": "Left Head Zone Control Unit (左域控制器)",
    "supplier": "UAES",
    "version": "V4.1 20250416",

    # 支持的诊断服务 (基于 Part4 DiagnosticServices 表)
    "supported_services": {
        "10": "DiagnosticSessionControl",     # 诊断会话控制
        "11": "ECUReset",                      # ECU 复位
        "14": "ClearDiagnosticInformation",    # 清除 DTC
        "19": "ReadDTCInformation",            # 读取 DTC 信息
        "22": "ReadDataByIdentifier",          # 读取 DID
        "27": "SecurityAccess",                # 安全访问
        "28": "CommunicationControl",          # 通信控制
        "2E": "WriteDataByIdentifier",         # 写入 DID
        "2F": "InputOutputControlByIdentifier",# IO 控制
        "31": "RoutineControl",                # 例程控制
        "3E": "TesterPresent",                 # 存在测试
        "85": "ControlDTCSetting",             # DTC 设置控制
    },

    # 诊断会话
    "sessions": {
        "01": "Default Session",
        "02": "Programming Session",
        "03": "Extended Diagnostic Session",
    },

    # ECU 复位类型
    "reset_types": {
        "01": "Hard Reset",
        "02": "Key Off Reset",
        "03": "Soft Reset",
    },

    # 安全访问级别
    "security_levels": {
        "01/02": "Level 1 (Default/Extended)",
        "03/04": "Level 2 (Extended)",
        "05/06": "Level 3 (Extended/Programming)",
        "09/0A": "Level 4 (Programming)",
        "61/62": "Level 5 (Development)",
    },

    # 安全访问算法号
    "security_algo": f"{LHZCU_SECURITY_ALGO:08X}",  # 00001010

    # 常用 DID
    "common_dids": {
        "F100": {"name": "SVIF", "size": None, "desc": "Software Version Identification"},
        "F186": {"name": "Active Diagnostic Session", "size": 1, "desc": "当前诊断会话"},
        "F187": {"name": "Vehicle Manufacturer Spare Data", "size": None, "desc": "整车厂备用数据"},
        "F190": {"name": "Application Software Identification", "size": None, "desc": "应用软件版本"},
        "F191": {"name": "Application Data Identification", "size": None, "desc": "应用数据版本"},
        "E101": {"name": "Odometer reading", "size": 3, "desc": "里程表读数", "unit": "km"},
        "010B": {"name": "Date&time", "size": 6, "desc": "日期时间"},
        "E010": {"name": "Vehicle Speed", "size": 2, "desc": "车速", "factor": 0.015625},
        "D002": {"name": "Vehicle State", "size": 1, "desc": "车辆状态"},
        "D001": {"name": "Power Mode", "size": 1, "desc": "电源模式"},
    },
}

# ── 导出 ──
__all__ = [
    "LHZCU_DOIP_IP",
    "LHZCU_DOIP_PORT",
    "LHZCU_LOGICAL_ADDR",
    "LHZCU_PHYSICAL_ADDR",
    "LHZCU_RESPONSE_ADDR",
    "LHZCU_ROUTING_TA",
    "TESTER_LOGICAL_ADDR",
    "LHZCU_SECURITY_ALGO",
    "LHZCU_DIAG_CONFIG",
]
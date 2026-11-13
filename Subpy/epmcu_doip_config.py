#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPMCU (Electric Power Management Control Unit) DoIP 配置
=========================================================
EPMCU 电动功率管理控制器的 DoIP 诊断配置

EPMCU 网络参数:
  DoIP 地址：172.31.6.11:13400  (通过 ICB 转发)
  路由激活 TA: 0x0010 (与 ICB 相同)
  诊断目标地址：0x0775 (物理地址)
  Tester 逻辑地址：0x0E80
"""

# EPMCU DoIP 网络配置
EPMCU_DOIP_IP = "172.31.6.11"      # EPMCU 的 DoIP 地址 (与 ICB 同 IP)
EPMCU_DOIP_PORT = 13400            # DoIP 端口
EPMCU_ROUTING_TA = 0x0010          # 路由激活目标地址 (与 ICB 相同)
EPMCU_DIAG_TA = 0x0775             # 诊断消息目标地址 (物理地址 0x775)
EPMCU_PHYSICAL_ADDR = EPMCU_DIAG_TA  # 别名 (物理地址)
TESTER_LOGICAL_ADDR = 0x0E80       # Tester 逻辑地址 (与 ICB 相同)

# EPMCU 诊断配置 (基于 Part4 规范)
EPMCU_DIAG_CONFIG = {
    "name": "EPMCU",
    "description": "电动功率管理控制器",
    
    # 支持的诊断服务 (基于 Part4 DiagnosticServices 表)
    "supported_services": {
        "10": "DiagnosticSessionControl",  # 诊断会话控制
        "11": "ECUReset",                   # ECU 复位
        "14": "ClearDiagnosticInformation", # 清除 DTC
        "19": "ReadDTCInformation",         # 读取 DTC 信息
        "22": "ReadDataByIdentifier",       # 读取 DID
        "27": "SecurityAccess",             # 安全访问
        "2E": "WriteDataByIdentifier",      # 写入 DID
        "31": "RoutineControl",             # 例程控制
        "3E": "TesterPresent",              # 存在测试
        "85": "ControlDTCSetting",          # DTC 设置控制
    },
    
    # 常用 DID (基于 Part4 DIDs 表)
    "common_dids": {
        "F190": {"name": "Application Software Identification", "desc": "应用软件版本"},
        "F191": {"name": "Application Data Identification", "desc": "应用数据版本"},
        "F194": {"name": "System Supplier ECU Hardware Number", "desc": "系统供应商 ECU 硬件号"},
        "F195": {"name": "System Supplier ECU Software Number", "desc": "系统供应商 ECU 软件号"},
        "F19A": {"name": "ECU Serial Number", "desc": "ECU 序列号"},
        "F1A0": {"name": "Vehicle Manufacturer ECU Hardware Number", "desc": "整车厂 ECU 硬件号"},
        "F1A1": {"name": "Vehicle Manufacturer ECU Software Number", "desc": "整车厂 ECU 软件号"},
        "0200": {"name": "Power Supply Voltage", "desc": "电源电压", "unit": "V"},
        "0201": {"name": "Battery Current", "desc": "电池电流", "unit": "A"},
        "0202": {"name": "Battery Temperature", "desc": "电池温度", "unit": "°C"},
        "0203": {"name": "DCDC Status", "desc": "DCDC 状态"},
        "0204": {"name": "OBC Status", "desc": "OBC 状态"},
        "0205": {"name": "Junction Box Status", "desc": "配电盒状态"},
    },
    
    # ECU Reset 类型 (基于 Part4)
    "reset_types": {
        "01": "Hard Reset",
        "02": "Key Off Reset",
        "03": "Soft Reset",
    },
    
    # 安全访问级别 (基于 Part4)
    "security_levels": {
        "01/02": "Level 1 (Default)",
        "03/04": "Level 2 (Extended)",
        "05/06": "Level 3 (Programming)",
    },
    
    # 安全访问算法号
    "security_algo": "00001044",  # EPMCU 专用算法号
}

# 导出配置
__all__ = [
    "EPMCU_DOIP_IP",
    "EPMCU_DOIP_PORT",
    "EPMCU_ROUTING_TA",
    "EPMCU_DIAG_TA",
    "EPMCU_PHYSICAL_ADDR",
    "TESTER_LOGICAL_ADDR",
    "EPMCU_DIAG_CONFIG",
]

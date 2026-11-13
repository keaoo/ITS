#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBS (Intelligent Battery Sensor) DoIP 配置
========================================
IBS 智能电池传感器的 DoIP 诊断配置

IBS 网络参数:
  DoIP 地址：172.31.6.11:13400  (通过 ICB 转发)
  路由激活 TA: 0x0010 (与 ICB 相同)
  诊断目标地址：0x0726 (物理地址)
  Tester 逻辑地址：0x0E80
"""

# IBS DoIP 网络配置
IBS_DOIP_IP = "172.31.6.11"      # IBS 的 DoIP 地址 (与 ICB 同 IP)
IBS_DOIP_PORT = 13400            # DoIP 端口
IBS_ROUTING_TA = 0x0010          # 路由激活目标地址 (与 ICB 相同)
IBS_DIAG_TA = 0x0726             # 诊断消息目标地址 (物理地址 0x726)
IBS_PHYSICAL_ADDR = IBS_DIAG_TA  # 别名 (物理地址)
IBS_RESPONSE_ADDR = 0x07A6       # 物理响应地址 (0x726 + 0x80)
TESTER_LOGICAL_ADDR = 0x0E80     # Tester 逻辑地址 (与 ICB 相同)

# IBS 诊断配置 (基于 Part4 规范)
IBS_DIAG_CONFIG = {
    "name": "IBS",
    "description": "智能电池传感器",
    
    # 支持的诊断服务
    "supported_services": {
        "10": "DiagnosticSessionControl",
        "11": "ECUReset",
        "14": "ClearDiagnosticInformation",
        "19": "ReadDTCInformation",
        "22": "ReadDataByIdentifier",
        "27": "SecurityAccess",
        "2E": "WriteDataByIdentifier",
        "31": "RoutineControl",
        "3E": "TesterPresent",
        "85": "ControlDTCSetting",
    },
    
    # 常用 DID
    "common_dids": {
        "F190": {"name": "Application Software Identification", "desc": "应用软件版本"},
        "F191": {"name": "Application Data Identification", "desc": "应用数据版本"},
        "F194": {"name": "System Supplier ECU Hardware Number", "desc": "系统供应商零件号"},
        "F195": {"name": "System Supplier ECU Software Number", "desc": "系统供应商软件号"},
        "F19A": {"name": "ECU Serial Number", "desc": "ECU 序列号"},
    },
    
    # ECU Reset 类型
    "reset_types": {
        "01": "Hard Reset",
        "02": "Key Off Reset",
        "03": "Soft Reset",
    },
    
    # 安全访问级别
    "security_levels": {
        "01/02": "Level 1 (Default)",
        "03/04": "Level 2 (Extended)",
        "05/06": "Level 3 (Programming)",
    },
    
    # 安全访问算法号
    "security_algo": "00001016",  # IBS 专用算法
}

# 导出配置
__all__ = [
    "IBS_DOIP_IP",
    "IBS_DOIP_PORT",
    "IBS_ROUTING_TA",
    "IBS_DIAG_TA",
    "IBS_PHYSICAL_ADDR",
    "TESTER_LOGICAL_ADDR",
    "IBS_DIAG_CONFIG",
]

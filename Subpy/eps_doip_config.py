#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPS (Electric Power Steering) DoIP 配置
========================================
EPS 电动助力转向控制器的 DoIP 诊断配置

EPS 网络参数:
  DoIP 地址：172.31.6.11:13400  (通过 ICB 转发)
  路由激活 TA: 0x0010 (与 ICB 相同)
  诊断目标地址：0x0721 (物理地址)
  Tester 逻辑地址：0x0E80
"""

# EPS DoIP 网络配置
EPS_DOIP_IP = "172.31.6.11"      # EPS 的 DoIP 地址 (与 ICB 同 IP)
EPS_DOIP_PORT = 13400            # DoIP 端口
EPS_ROUTING_TA = 0x0010          # 路由激活目标地址 (与 ICB 相同)
EPS_DIAG_TA = 0x0721             # 诊断消息目标地址 (物理地址 0x721)
EPS_PHYSICAL_ADDR = EPS_DIAG_TA  # 别名 (物理地址)
TESTER_LOGICAL_ADDR = 0x0E80     # Tester 逻辑地址 (与 ICB 相同)

# EPS 诊断配置 (基于 Part4 规范)
EPS_DIAG_CONFIG = {
    "name": "EPS",
    "description": "电动助力转向控制器",
    
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
        "0200": {"name": "Supply Voltage", "desc": "电源电压", "unit": "V"},
        "0201": {"name": "Motor Current", "desc": "电机电流", "unit": "A"},
        "0202": {"name": "Steering Angle", "desc": "转向角", "unit": "deg"},
        "0203": {"name": "Motor Temperature", "desc": "电机温度", "unit": "°C"},
        "0204": {"name": "ECU Temperature", "desc": "ECU 温度", "unit": "°C"},
        "0205": {"name": "Torque Sensor", "desc": "扭矩传感器", "unit": "Nm"},
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
    "security_algo": "00001035",  # EPS 专用算法号
}

# 导出配置
__all__ = [
    "EPS_DOIP_IP",
    "EPS_DOIP_PORT",
    "EPS_ROUTING_TA",
    "EPS_DIAG_TA",
    "EPS_PHYSICAL_ADDR",
    "TESTER_LOGICAL_ADDR",
    "EPS_DIAG_CONFIG",
]

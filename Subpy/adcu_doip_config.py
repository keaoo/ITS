#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADCU (Advanced Driver Assistance Control Unit) DoIP 配置
=========================================================
智能驾驶辅助控制器的 DoIP 诊断配置

ADCU 网络参数 (通过 ICB 转发):
  DoIP 地址：172.31.6.11:13400  (与 ICB 相同)
  路由激活 TA: 0x0010  (与 ICB 相同)
  诊断目标地址：0x05A3  (物理地址)
  Tester 逻辑地址：0x0E80
"""

# ADCU DoIP 网络配置
ADCU_DOIP_IP = "172.31.6.11"      # ADCU 的 DoIP 地址 (通过 ICB)
ADCU_DOIP_PORT = 13400            # DoIP 端口
ADCU_ROUTING_TA = 0x0010          # 路由激活目标地址 (与 ICB 相同)
ADCU_DIAG_TA = 0x0785             # 诊断消息目标地址 (物理地址 0x785)
ADCU_LOGICAL_ADDR = ADCU_DIAG_TA  # 别名 (向后兼容)
ADCU_PHYSICAL_ADDR = 0x0785       # 物理地址
TESTER_LOGICAL_ADDR = 0x0E80      # Tester 逻辑地址 (与 ICB 相同)

# ADCU 诊断配置 (基于 Part4 规范)
ADCU_DIAG_CONFIG = {
    "name": "ADCU",
    "description": "智能驾驶辅助控制器",
    
    # 支持的诊断服务 (基于 Part4 DiagnosticServices)
    "supported_services": {
        "10": "DiagnosticSessionControl",  # 诊断会话控制
        "11": "ECUReset",                   # ECU 复位
        "14": "ClearDiagnosticInformation", # 清除 DTC
        "19": "ReadDTCInformation",         # 读取 DTC 信息
        "22": "ReadDataByIdentifier",       # 读取 DID
        "23": "ReadMemoryByAddress",        # 按地址读取内存
        "27": "SecurityAccess",             # 安全访问
        "2E": "WriteDataByIdentifier",      # 写入 DID
        "2F": "InputOutputControlByIdentifier", # IO 控制
        "31": "RoutineControl",             # 例程控制
        "34": "RequestDownload",            # 请求下载
        "36": "TransferData",               # 数据传输
        "37": "RequestTransferExit",        # 请求传输退出
        "3E": "TesterPresent",              # 存在测试
        "85": "ControlDTCSetting",          # DTC 设置控制
    },
    
    # 常用 DID (基于 Part4 DIDs)
    "common_dids": {
        "0112": {"name": "Supply voltage", "size": 1, "unit": "V", "factor": 0.1},
        "E101": {"name": "Odometer reading", "size": 3, "unit": "km"},
        "010B": {"name": "Date&time", "size": 6},
        "E010": {"name": "Vehicle Speed", "size": 2, "unit": "km/s", "factor": 0.015625},
        "D002": {"name": "Vehicle State", "size": 1},
        "D001": {"name": "Power Mode", "size": 1},
        "F186": {"name": "Active Diagnostic Session", "size": 1},
        "F190": {"name": "Vehicle Information", "size": 20},
        "F18A": {"name": "ECU Serial Number", "size": 10},
        "F191": {"name": "ECU Hardware Version", "size": 5},
        "F192": {"name": "ECU Software Version", "size": 10},
    },
    
    # ECU Reset 类型 (基于 Part4)
    "reset_types": {
        "01": "Hard Reset",
        "02": "Key Off Reset",
        "03": "Soft Reset",
        "04": "Enable Rapid Power Shutoff Mode",
        "05": "Disable Rapid Power Shutoff Mode",
    },
    
    # 安全访问级别 (基于 Part4)
    "security_levels": {
        "01/02": "Level 1 (Default/Extended)",
        "03/04": "Level 2 (Extended)",
        "05/06": "Level 3 (Extended/Programming)",
        "09/0A": "Level 4 (Programming)",
        "61/62": "Level 5 (Development)",
    },
}

# 导出配置
__all__ = [
    "ADCU_DOIP_IP",
    "ADCU_DOIP_PORT",
    "ADCU_ROUTING_TA",
    "ADCU_DIAG_TA",
    "ADCU_LOGICAL_ADDR",
    "ADCU_PHYSICAL_ADDR",
    "TESTER_LOGICAL_ADDR",
    "ADCU_DIAG_CONFIG",
]

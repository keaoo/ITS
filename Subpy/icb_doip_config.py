#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ICB DoIP 配置 - 大 F 车型
========================
大 F (智己 L7 大 F 配置) 的 ICB 参数
"""

# ICB DoIP 配置参数
ICB_DOIP_IP = "172.31.6.11"       # ICB DoIP 地址
ICB_DOIP_PORT = 13400             # DoIP 端口
ICB_ROUTING_TA = 0x0010           # 路由激活目标地址
ICB_DIAG_TA = 0x1000              # 诊断消息目标地址 (逻辑地址)
ICB_LOGICAL_ADDR = ICB_DIAG_TA    # 简化：使用逻辑地址
TESTER_LOGICAL_ADDR = 0x0E80      # Tester 逻辑地址

# 大 F ICB 安全访问算法号
# 小 F: 0x1042
# 大 F: 待确认 (可能是 0x1010, 0x1011, 0x1044 等)
ICB_SECURITY_ALGO = 0x1042  # TODO: 大 F 需要验证

# IPD 配置 (通过 ICB 转发)
IPD_LOGICAL_ADDR = 0x0735       # IPD 逻辑地址
IPD_SECURITY_ALGO = 0x1043      # ✅ 已确认 IPD 算法号

# 配置导出
__all__ = [
    "ICB_DOIP_IP",
    "ICB_DOIP_PORT",
    "ICB_ROUTING_TA",
    "ICB_DIAG_TA",
    "ICB_LOGICAL_ADDR",
    "TESTER_LOGICAL_ADDR",
    "ICB_SECURITY_ALGO",
    "IPD_LOGICAL_ADDR",
    "IPD_SECURITY_ALGO",
]

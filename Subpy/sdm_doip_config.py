# -*- coding: utf-8 -*-
"""
SDM DoIP 配置
SDM (安全域模块) 通过 ICB 网关转发访问
"""

# ICB DoIP 网关 (SDM 通过 ICB 转发)
SDM_DOIP_IP = "172.31.6.11"  # ICB 网关 IP (8295_QNX)
SDM_DOIP_PORT = 13400        # ICB DoIP 端口

# 路由激活目标地址
SDM_ROUTING_TA = 0x0010      # 路由激活目标地址 (ICB 实际值)

# SDM 物理地址
SDM_PHYSICAL_ADDR = 0x730    # SDM 物理请求地址
SDM_RESPONSE_ADDR = 0x7B0    # SDM 物理响应地址 (0x730 + 0x80)

# 安全访问算法号
SDM_SECURITY_ALGO = 0x1019   # SDM 安全算法
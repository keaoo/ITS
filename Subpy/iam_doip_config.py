# -*- coding: utf-8 -*-
"""
IAM DoIP 配置
IAM (智能进入控制器) 通过 ICB 网关转发访问
"""

# ICB DoIP 网关 (IAM 通过 ICB 转发)
IAM_DOIP_IP = "172.31.6.11"  # ICB 网关 IP (8295_QNX)
IAM_DOIP_PORT = 13400       # ICB DoIP 端口

# 逻辑地址 (ICB 网关)
IAM_LOGICAL_ADDR = 0x1000   # ICB 逻辑地址

# IAM 物理地址
IAM_PHYSICAL_ADDR = 0x711   # IAM 物理请求地址
IAM_RESPONSE_ADDR = 0x791   # IAM 物理响应地址 (0x711 + 0x80)

# 路由激活目标地址
IAM_ROUTING_TA = 0x0010     # 路由激活目标地址 (ICB 实际值)

# 安全访问算法号
IAM_SECURITY_ALGO = 0x1011  # IAM 安全算法

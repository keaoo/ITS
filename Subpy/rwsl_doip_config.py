# -*- coding: utf-8 -*-
"""
RWSL DoIP 配置
RWSL (后轮转向锁控制器) 通过 ICB 网关转发访问
"""

# ICB DoIP 网关 (RWSL 通过 ICB 转发)
RWSL_DOIP_IP = "172.31.6.11"  # ICB 网关 IP (8295_QNX)
RWSL_DOIP_PORT = 13400        # ICB DoIP 端口

# 路由激活目标地址
RWSL_ROUTING_TA = 0x0010      # 路由激活目标地址 (ICB 实际值)

# RWSL 物理地址
RWSL_PHYSICAL_ADDR = 0x5D3    # RWSL 物理请求地址
RWSL_RESPONSE_ADDR = 0x653    # RWSL 物理响应地址 (0x5D3 + 0x80)

# 安全访问算法号
RWSL_SECURITY_ALGO = 0x104A   # RWSL 安全算法
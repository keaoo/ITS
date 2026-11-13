# -*- coding: utf-8 -*-
"""
SCM DoIP 配置
SCM (座椅控制模块) 通过 ICB 网关转发访问
"""

# ICB DoIP 网关 (SCM 通过 ICB 转发)
SCM_DOIP_IP = "172.31.6.11"  # ICB 网关 IP (8295_QNX)
SCM_DOIP_PORT = 13400        # ICB DoIP 端口

# 路由激活目标地址
SCM_ROUTING_TA = 0x0010      # 路由激活目标地址 (ICB 实际值)

# SCM 物理地址
SCM_PHYSICAL_ADDR = 0x727    # SCM 物理请求地址
SCM_RESPONSE_ADDR = 0x7A7    # SCM 物理响应地址 (0x727 + 0x80)

# 安全访问算法号
SCM_SECURITY_ALGO = 0x1049   # SCM 安全算法
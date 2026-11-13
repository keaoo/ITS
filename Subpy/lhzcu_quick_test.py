#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LHZCU 快速诊断测试脚本
=======================
验证 LHZCU 的基本诊断功能 (通过 ICB DoIP 网关)

用法:
    python lhzcu_quick_test.py
"""
import sys
import os

# 确保可以在项目根目录或 Subpy 目录下运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Subpy.lhzcu_diagnostics import LHZCUDiagnostics
from Subpy.lhzcu_doip_config import LHZCU_DIAG_CONFIG


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run_lhzcu_test():
    """LHZCU 快速诊断测试"""
    
    print(f"╔{'═'*58}╗")
    print(f"║  LHZCU 快速诊断测试                                  ║")
    print(f"║  算法: 0x{LHZCU_DIAG_CONFIG['security_algo']:>8s}                              ║")
    print(f"║  地址: 0x{LHZCU_DIAG_CONFIG['security_algo']:>8s}                              ║")
    print(f"╚{'═'*58}╝")
    
    diag = LHZCUDiagnostics()
    
    try:
        # ── Step 1: 连接 ──
        print_separator("Step 1: DoIP 连接")
        print("连接 LHZCU (172.31.6.11:13400 → 0x15B0) ...")
        diag.connect()
        print("✓ DoIP 连接 + 路由激活成功")
        
        # ── Step 2: 扩展会话 ──
        print_separator("Step 2: 扩展诊断会话 ($10 03)")
        result = diag.extended_session()
        print(f"✓ 会话切换成功: {result['session']}")
        
        # ── Step 3: TesterPresent ──
        print_separator("Step 3: TesterPresent ($3E 00)")
        result = diag.tester_present()
        print(f"{'✓ TesterPresent 成功' if result['success'] else '❌ 失败'}")
        
        # ── Step 4: 读取基本信息 ──
        print_separator("Step 4: 读取 DID 信息 ($22)")
        
        # 读取当前会话
        result = diag.read_did("F186")
        if result['success']:
            print(f"  F186 (Active Session): {result['decoded']}")
        else:
            print(f"  F186: ❌ {result.get('error', '失败')}")
        
        # 读取软件版本
        result = diag.read_did("F190")
        if result['success']:
            print(f"  F190 (App SW Version): {result['decoded']}")
        else:
            print(f"  F190: ❌ {result.get('error', '失败')}")
        
        # 读取数据版本
        result = diag.read_did("F191")
        if result['success']:
            print(f"  F191 (App Data Version): {result['decoded']}")
        else:
            print(f"  F191: ❌ {result.get('error', '失败')}")
        
        # 读取日期时间
        result = diag.read_did("010B")
        if result['success']:
            print(f"  010B (Date&time): {result['decoded']}")
        else:
            print(f"  010B: ❌ {result.get('error', '失败')}")
        
        # ── Step 5: 安全访问 ──
        print_separator("Step 5: 安全访问 ($27 01/02, 算法 0x1010)")
        result = diag.security_level1()
        if result['success']:
            print(f"✓ 安全访问成功")
            print(f"  Seed: {result['seed']}")
            print(f"  Key : {result['key']}")
        else:
            print(f"❌ 安全访问失败: {result}")
        
        # ── Step 6: 读取 DTC ──
        print_separator("Step 6: DTC 信息 ($19)")
        
        count = diag.read_dtc_count()
        print(f"  DTC 数量: {count}")
        
        if count > 0:
            dtcs = diag.read_dtc()
            for dtc in dtcs[:10]:
                print(f"  0x{dtc.code:06X} (Status: 0x{dtc.status:02X})")
        
        # ── Step 7: TesterPresent ──
        print_separator("Step 7: 保持连接 ($3E 00)")
        result = diag.tester_present()
        print(f"{'✓ TesterPresent' if result['success'] else '❌ 失败'}")
        
        print(f"\n{'='*60}")
        print("  ✅ LHZCU 诊断测试完成!")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        diag.disconnect()
        print("\n✓ 连接已断开")


if __name__ == '__main__':
    run_lhzcu_test()
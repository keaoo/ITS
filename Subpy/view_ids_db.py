"""
IDS DTC 数据库查看器
用法: python view_ids_db.py [dtc码] [ECU名]
示例:
  python view_ids_db.py                     # 显示摘要统计
  python view_ids_db.py P17BA_8B            # 查单个 DTC
  python view_ids_db.py P17BA_8B LHZCU      # 查单个 DTC + 过滤 ECU
  python view_ids_db.py --ecu LHZCU          # 列出该 ECU 的所有 DTC
  python view_ids_db.py --search 刹车        # 搜索描述中包含"刹车"的 DTC
  python view_ids_db.py --export dtc_all.json  # 导出为 JSON
"""

import sys
import os
import pickle
import json

CONFIG_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config"))
DTC_PATH = os.path.join(CONFIG_DIR, "dtc")

def load_db():
    if not os.path.exists(DTC_PATH):
        # Fallback to Subpy/../config (relative to this script's parent)
        alt = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config"))
        alt_path = os.path.join(alt, "dtc")
        if os.path.exists(alt_path):
            return pickle.load(open(alt_path, "rb"))
        print(f"❌ 找不到 dtc 文件")
        print(f"   尝试路径: {DTC_PATH}")
        print(f"   尝试路径: {alt_path}")
        sys.exit(1)
    return pickle.load(open(DTC_PATH, "rb"))


def show_help():
    print("用法: python view_ids_db.py [选项]")
    print()
    print("选项:")
    print("  <DTC码>           查询单个 DTC，如 P17BA_8B")
    print("  <DTC码> <ECU名>   查询单个 DTC 并过滤指定 ECU")
    print("  --ecu <ECU名>     列出该 ECU 的所有 DTC")
    print("  --search <关键词>  搜索描述中包含关键词的 DTC")
    print("  --export <文件>   导出全部 DTC 为 JSON")
    print("  --stats           显示数据库统计")


def main():
    db = load_db()
    
    # Collect all ECU names
    ecus = set()
    for v in db.values():
        ecus.update(v.keys())
    
    # No args = show stats
    if len(sys.argv) <= 1:
        print("=" * 60)
        print("IDS DTC 数据库")
        print("=" * 60)
        print(f"  DTC 总数: {len(db)}")
        print(f"  ECU 总数: {len(ecus)}")
        
        # Count per ECU
        ecu_count = {e: 0 for e in sorted(ecus)}
        for k, v in db.items():
            for e in v:
                if e in ecu_count:
                    ecu_count[e] += 1
        
        print(f"\n  ECU 分布 (前 20):")
        for e, cnt in sorted(ecu_count.items(), key=lambda x: -x[1])[:20]:
            print(f"    {e:12s}: {cnt:5d} DTCs")
        print(f"\n  提示: python view_ids_db.py --help 查看更多用法")
        return
    
    if sys.argv[1] in ('--help', '-h'):
        show_help()
        return
    
    if sys.argv[1] == '--stats':
        print("=" * 60)
        print("IDS DTC 数据库统计")
        print("=" * 60)
        print(f"  DTC 总数: {len(db)}")
        print(f"  ECU 总数: {len(ecus)}")
        ecu_count = {e: 0 for e in sorted(ecus)}
        for k, v in db.items():
            for e in v:
                if e in ecu_count:
                    ecu_count[e] += 1
        for e, cnt in sorted(ecu_count.items(), key=lambda x: -x[1]):
            print(f"    {e:12s}: {cnt:5d}")
        return
    
    if sys.argv[1] == '--ecu':
        if len(sys.argv) < 3:
            print("需指定 ECU 名，如: --ecu LHZCU")
            return
        target = sys.argv[2]
        print(f"ECU {target} 的 DTC 列表:")
        count = 0
        for k in sorted(db.keys()):
            if target in db[k]:
                desc = db[k][target]
                print(f"  {k:12s}  {desc}")
                count += 1
        print(f"  共 {count} 条")
        return
    
    if sys.argv[1] == '--search':
        if len(sys.argv) < 3:
            print("需指定关键词，如: --search 刹车")
            return
        keyword = sys.argv[2]
        print(f"搜索描述中包含 '{keyword}' 的 DTC:")
        count = 0
        for k in sorted(db.keys()):
            for ecu, desc in db[k].items():
                if keyword in desc:
                    print(f"  {k:12s}  [{ecu:10s}] {desc}")
                    count += 1
        print(f"  共 {count} 条")
        return
    
    if sys.argv[1] == '--export':
        if len(sys.argv) < 3:
            print("需指定导出文件名，如: --export dtc_all.json")
            return
        out_file = sys.argv[2]
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"已导出 {len(db)} 条 DTC 到 {out_file}")
        return
    
    # Query by DTC code
    dtc_code = sys.argv[1].upper()
    ecu_filter = sys.argv[2].upper() if len(sys.argv) > 2 else None
    
    entry = db.get(dtc_code)
    if not entry:
        print(f"❌ 未找到 DTC: {dtc_code}")
        return
    
    print(f"\nDTC {dtc_code}:")
    print("-" * 60)
    for ecu, desc in sorted(entry.items()):
        if ecu_filter and ecu_filter != ecu.upper():
            continue
        print(f"  [{ecu:10s}] {desc}")
    print(f"  ({len(entry)} 个 ECU 有此 DTC)")


if __name__ == "__main__":
    main()
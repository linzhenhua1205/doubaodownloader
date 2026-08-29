#!/usr/bin/env python3
"""
竞品分析数据采集与质量管理工具

功能:
1. 验证采集数据的完整性和一致性
2. 生成结构化的维度对比表数据文件
3. 支持多竞品批量处理

用法:
  python3 comparison-data-collector.py \
    --competitors "我们自己,Dell XE9680,HPE Cray XD670,Supermicro AS-8125GS" \
    --output /tmp/competitor-data.txt
"""
import argparse
import csv
import sys
import os
from datetime import datetime


REQUIRED_DIMENSIONS = [
    # 硬件层
    ("硬件", "CPU型号"),
    ("硬件", "GPU型号"),
    ("硬件", "GPU互联带宽"),
    ("硬件", "GPU互联拓扑"),
    ("硬件", "内存容量/类型"),
    ("硬件", "存储配置"),
    ("硬件", "PCIe版本"),
    ("硬件", "PSU规格"),
    ("硬件", "散热方案"),
    ("硬件", "物理尺寸(U)"),
    ("硬件", "估算功耗(W)"),
    # 软件层
    ("软件", "AI框架支持"),
    ("软件", "管理软件"),
    ("软件", "通信库"),
    ("软件", "集群调度"),
    ("软件", "监控系统"),
    ("软件", "开发者体验评分(1-5)"),
    # 固件层
    ("固件", "BIOS版本"),
    ("固件", "BMC版本"),
    ("固件", "POST时间(s)"),
    ("固件", "BIOS可配置项数"),
    ("固件", "BiOS默认值策略"),
    ("固件", "Redfish覆盖率(%)"),
    ("固件", "安全等级"),
    ("固件", "固件更新机制"),
    # 商业
    ("商业", "估算BOM成本($)"),
    ("商业", "售价($)"),
    ("商业", "目标客户群"),
    ("商业", "市场定位"),
]


def generate_template(competitors):
    """生成维度对比表数据文件模板"""
    names = [c.strip() for c in competitors.split(",")]
    
    lines = []
    # 表头
    header = "领域|维度"
    for n in names:
        header += f"|{n}"
    header += "|分析结论"
    lines.append(header)
    
    # 分隔线
    sep = ":---|:---"
    for _ in names:
        sep += "|:---"
    sep += "|:---"
    lines.append(sep)
    
    for category, dimension in REQUIRED_DIMENSIONS:
        row = f"{category}|{dimension}"
        for _ in names:
            row += "|"
        row += "|"
        lines.append(row)
    
    return "\n".join(lines)


def validate_data(data_file):
    """验证数据填写完整性"""
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return False
    
    with open(data_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    if len(lines) < 2:
        print("❌ 数据文件为空或只有表头")
        return False
    
    # 解析表头
    header = lines[0].split('|')
    num_cols = len(header)
    competitor_names = header[1:-1]  # 去掉第一列(维度)和最后一列(结论)
    
    print(f"=== 数据验证报告 ===")
    print(f"竞品数: {len(competitor_names)} ({', '.join(competitor_names)})")
    print(f"维度数: {len(lines) - 1} (含表头)")
    
    # 统计各竞品的空值
    empty_count = [0] * len(competitor_names)
    total_rows = 0
    
    for line in lines[1:]:  # 跳过表头
        cols = line.split('|')
        if len(cols) != num_cols:
            continue
        total_rows += 1
        for i in range(1, len(competitor_names) + 1):
            if i < len(cols) and (cols[i].strip() == '' or cols[i].strip() == '-'):
                empty_count[i-1] += 1
    
    print("\n--- 填充率统计 ---")
    for i, name in enumerate(competitor_names):
        filled = total_rows - empty_count[i]
        rate = (filled / total_rows * 100) if total_rows > 0 else 0
        status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
        print(f"  {status} {name}: {filled}/{total_rows} ({rate:.0f}%)")
    
    # 完整性判断
    all_ok = all(rate >= 50 for rate in 
                 [(total_rows - empty_count[i]) / total_rows * 100 
                  for i in range(len(competitor_names))] 
                 if total_rows > 0)
    
    print(f"\n总体判断: {'✅ 数据可用于分析' if all_ok else '❌ 数据不完整，需补充采集'}")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description='竞品数据采集与质量管理')
    parser.add_argument('--competitors', type=str,
                        help='竞品列表，逗号分隔 (如 "我们自己,竞品A,竞品B,竞品C")')
    parser.add_argument('--output', type=str, default='comparison-data.txt',
                        help='输出文件路径')
    parser.add_argument('--validate', type=str,
                        help='验证已有数据文件的完整性')
    
    args = parser.parse_args()
    
    if args.validate:
        validate_data(args.validate)
        return
    
    if args.competitors and args.output:
        template = generate_template(args.competitors)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(template)
        names = args.competitors.split(",")
        print(f"✅ 模板已生成: {args.output}")
        print(f"   竞品: {', '.join(n.strip() for n in names)}")
        print(f"   维度: {len(REQUIRED_DIMENSIONS)} 个")
        print(f"\n请在 '{args.output}' 中填充数据，然后运行:")
        print(f"  python3 {__file__} --validate {args.output}")
        return
    
    parser.print_help()


if __name__ == '__main__':
    main()

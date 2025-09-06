#!/usr/bin/env python3
"""
按频率分组汇总低频组合数据
"""

import csv
from collections import defaultdict

def main():
    # 读取低频数据
    freq_groups = defaultdict(list)
    
    with open('low_frequency_combinations.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            freq = int(row['frequency'])
            freq_groups[freq].append(row)
    
    # 按频率输出汇总
    print("=== 低频source组合汇总 ===")
    for freq in sorted(freq_groups.keys()):
        items = freq_groups[freq]
        print(f"\n频率 {freq} ({len(items)} 个实体):")
        
        # 按组合签名分组
        by_signature = defaultdict(list)
        for item in items:
            by_signature[item['combination_signature']].append(item)
        
        for signature, sig_items in by_signature.items():
            print(f"  组合: {signature}")
            for item in sig_items:
                path = item['absolute_url_path']
                fragment = f"#{item['fragment']}" if item['fragment'] else ""
                print(f"    - {path}{fragment}")
    
    print(f"\n总计: {sum(len(items) for items in freq_groups.values())} 个低频实体")
    print(f"频率分布: {dict((freq, len(items)) for freq, items in freq_groups.items())}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
提取低频source组合的具体数据，生成肉眼可查看的表格
"""

import json
import csv
from collections import defaultdict

def main():
    # 读取source组合统计
    with open('source_combinations.json', 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    # 找出频率小于10的组合
    low_freq_combinations = []
    for combo_data in stats['combinations']:
        if combo_data['frequency'] < 10:
            low_freq_combinations.append(combo_data['combination'])
    
    # 读取最终路径数据
    with open('paths_final.json', 'r', encoding='utf-8') as f:
        paths = json.load(f)
    
    # 为每个实体生成source组合签名
    def get_combination_signature(sources):
        """根据sources列表生成组合签名"""
        combo = defaultdict(int)
        for source in sources:
            source_name = source['source']
            # 从label推断角色
            if source_name == 'langalphMap.json':
                if '_using_' in source['label']:
                    role = 'language'
                else:
                    role = 'writing_system'
            elif source_name == 'language.csv':
                role = 'language'
            elif source_name in ['writing.csv', 'langalphSingle.csv']:
                role = 'writing_system'
            else:
                role = 'unknown'
            
            key = f"{source_name}:{role}"
            combo[key] += 1
        
        return dict(combo)
    
    # 提取匹配低频组合的数据
    low_freq_data = []
    for item in paths:
        combo_sig = get_combination_signature(item['sources'])
        
        # 检查是否匹配任何低频组合
        for target_combo in low_freq_combinations:
            if combo_sig == target_combo:
                # 提取关键信息
                source_labels = []
                for source in item['sources']:
                    source_labels.append(f"{source['source']}:{source['label']}")
                
                low_freq_data.append({
                    'absolute_url_path': item['absolute_url_path'],
                    'fragment': item.get('fragment', ''),
                    'combination_signature': str(combo_sig),
                    'sources': ' | '.join(source_labels),
                    'frequency': next(c['frequency'] for c in stats['combinations'] if c['combination'] == target_combo)
                })
                break
    
    # 按频率和路径排序
    low_freq_data.sort(key=lambda x: (x['frequency'], x['absolute_url_path']))
    
    # 保存为CSV
    with open('low_frequency_combinations.csv', 'w', encoding='utf-8', newline='') as f:
        if low_freq_data:
            fieldnames = ['frequency', 'absolute_url_path', 'fragment', 'combination_signature', 'sources']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(low_freq_data)
    
    print(f"提取了 {len(low_freq_data)} 个低频组合实体")
    print(f"涉及 {len(low_freq_combinations)} 种不同的低频组合")

if __name__ == "__main__":
    main()

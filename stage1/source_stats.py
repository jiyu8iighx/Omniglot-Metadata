#!/usr/bin/env python3
"""
从paths_final.json生成source组合统计
"""

import json
from collections import Counter, defaultdict

def generate_source_stats(paths_file='paths_final.json', output_file='source_combinations.json'):
    """生成source组合统计"""
    
    with open(paths_file, 'r', encoding='utf-8') as f:
        paths = json.load(f)
    
    # 收集source角色组合
    role_combinations = []
    
    for path_entry in paths:
        roles = []
        role_counts = defaultdict(int)
        
        for source in path_entry['sources']:
            src = source['source']
            label = source['label']
            
            # 区分langalph中的角色
            if src == 'langalphMap.json':
                if '_using_' in label:
                    role = 'langalphMap.json:language'
                else:
                    role = 'langalphMap.json:writing_system'
            elif src == 'language.csv':
                role = 'language.csv:language'
            elif src == 'writing.csv':
                role = 'writing.csv:writing_system'
            elif src == 'langalphSingle.csv':
                role = 'langalphSingle.csv:writing_system'
            
            roles.append(role)
            role_counts[role] += 1
        
        # 保存组合（保留重数）
        combo = {}
        for role in set(roles):
            combo[role] = role_counts[role]
        
        role_combinations.append(combo)
    
    # 统计组合频次
    combo_counter = Counter()
    for combo in role_combinations:
        # 创建可哈希的组合key
        combo_key = tuple(sorted((role, count) for role, count in combo.items()))
        combo_counter[combo_key] += 1
    
    # 转换为最终格式
    combinations = []
    for combo_key, freq in combo_counter.items():
        combo_dict = dict(combo_key)
        combinations.append({
            'combination': combo_dict,
            'frequency': freq
        })
    
    # 按频次排序
    combinations.sort(key=lambda x: x['frequency'], reverse=True)
    
    # 统计各角色总计
    role_totals = defaultdict(int)
    for combo in role_combinations:
        for role, count in combo.items():
            role_totals[role] += count
    
    # 生成最终统计
    stats = {
        'total_entities': len(paths),
        'unique_combinations': len(combinations),
        'combinations': combinations,
        'role_totals': dict(role_totals)
    }
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    return stats

def main():
    generate_source_stats()

if __name__ == "__main__":
    main()

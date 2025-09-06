#!/usr/bin/env python3
"""
分析路径收集过程中的重复情况
"""

import json
import csv
from collections import defaultdict
from pathlib import Path

def load_csv_paths(file_path, source_name):
    """加载CSV文件中的路径"""
    paths = []
    if Path(file_path).exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    paths.append({
                        'path': row[0].strip(),
                        'label': row[1].strip(),
                        'source': source_name
                    })
    return paths

def load_langalph_map_paths():
    """加载langalphMap.json中的路径"""
    paths = []
    json_file = Path("langalphMap.json")
    
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for entry in data:
            writing_info = entry['writing']
            languages = entry['language']
            
            # 书写系统路径
            paths.append({
                'path': writing_info['Link'],
                'label': writing_info['Label'],
                'source': 'langalphMap.json(writing)'
            })
            
            # 语言路径
            for lang_entry in languages:
                paths.append({
                    'path': lang_entry[0],
                    'label': lang_entry[1],
                    'source': 'langalphMap.json(language)'
                })
    return paths

def normalize_to_absolute(path):
    """将路径标准化为绝对路径"""
    base_path = path.split('#')[0] if '#' in path else path
    
    if base_path.startswith('/'):
        return base_path
    elif base_path.startswith('../'):
        if base_path.startswith('../chinese/'):
            return '/chinese/' + base_path[11:]
        elif base_path.startswith('../language/articles/'):
            return '/language/articles/' + base_path[21:]
        else:
            return '/writing/' + base_path[3:]
    else:
        return '/writing/' + base_path

def main():
    print("=== 路径重复分析 ===\n")
    
    # 收集所有路径
    all_paths = []
    all_paths.extend(load_csv_paths("language.csv", "language.csv"))
    all_paths.extend(load_csv_paths("writing.csv", "writing.csv"))
    all_paths.extend(load_csv_paths("langalphSingle.csv", "langalphSingle.csv"))
    all_paths.extend(load_langalph_map_paths())
    
    print(f"总收集路径条目: {len(all_paths)}")
    
    # 按原始路径分组
    by_original = defaultdict(list)
    for item in all_paths:
        by_original[item['path']].append(item)
    
    # 按绝对路径分组
    by_absolute = defaultdict(list)
    for item in all_paths:
        abs_path = normalize_to_absolute(item['path'])
        item['absolute_path'] = abs_path
        by_absolute[abs_path].append(item)
    
    print(f"原始路径去重后: {len(by_original)}")
    print(f"绝对路径去重后: {len(by_absolute)}")
    print(f"可去除的重复条目: {len(all_paths) - len(by_absolute)}")
    
    # 分析重复的绝对路径
    duplicates = {k: v for k, v in by_absolute.items() if len(v) > 1}
    print(f"\n重复的绝对路径数量: {len(duplicates)}")
    
    # 显示重复示例
    print("\n=== 重复路径示例 ===")
    for abs_path, items in list(duplicates.items())[:10]:
        print(f"\n{abs_path}:")
        for item in items:
            print(f"  - 原路径: {item['path']}")
            print(f"    标签: {item['label']}")
            print(f"    来源: {item['source']}")
    
    # 统计来源交叉情况
    print("\n=== 来源交叉分析 ===")
    cross_source_count = 0
    for abs_path, items in duplicates.items():
        sources = set(item['source'] for item in items)
        if len(sources) > 1:
            cross_source_count += 1
    
    print(f"跨来源重复的路径: {cross_source_count}/{len(duplicates)}")
    
    # 保存详细分析结果
    with open('duplicate_analysis.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_entries': len(all_paths),
                'unique_original_paths': len(by_original),
                'unique_absolute_paths': len(by_absolute),
                'duplicate_absolute_paths': len(duplicates),
                'cross_source_duplicates': cross_source_count
            },
            'duplicates': {abs_path: [{'path': item['path'], 'label': item['label'], 'source': item['source']} 
                                     for item in items] 
                          for abs_path, items in duplicates.items()}
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细分析结果已保存到: duplicate_analysis.json")

if __name__ == "__main__":
    main()

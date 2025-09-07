#!/usr/bin/env python3
"""
根据source组合模式对实体进行分类
将不同类别的JSON对象输出到class/目录
"""

import json
from pathlib import Path
from collections import defaultdict

def classify_entity_by_sources(sources):
    """根据source组合分类实体"""
    
    # 统计各角色
    source_counts = {}
    for source in sources:
        role_key = f"{source['source']}:{get_role(source)}"
        source_counts[role_key] = source_counts.get(role_key, 0) + 1
    
    # 简化为single/multiple
    pattern = {}
    for role, count in source_counts.items():
        pattern[role] = "single" if count == 1 else "multiple"
    
    return classify_pattern(pattern)

def get_role(source):
    """从source对象获取角色"""
    src = source['source']
    label = source['label']
    
    if src == 'langalphMap.json':
        if '_using_' in label:
            return 'language'
        else:
            return 'writing_system'
    elif src == 'language.csv':
        return 'language'
    elif src == 'writing.csv':
        return 'writing_system'
    elif src == 'langalphSingle.csv':
        return 'writing_system'
    
    return 'unknown'

def classify_pattern(pattern):
    """根据简化的source模式分类实体
    
    命名规则: [Xw][Yl][Zml][Zmw] (为0的项略去)
    - w: 书写系统源 (writing.csv + langalphSingle.csv)
    - l: 语言源 (language.csv) 
    - ml: Map-Language 映射中的语言 (langalphMap.json:language)
    - mw: Map-Writing 映射中的书写系统 (langalphMap.json:writing_system)
    - 1表示single，2表示multiple (>=2)
    """
    
    has_lang_csv = 'language.csv:language' in pattern
    has_writing_csv = 'writing.csv:writing_system' in pattern  
    has_langalph_lang = 'langalphMap.json:language' in pattern
    has_langalph_writing = 'langalphMap.json:writing_system' in pattern
    has_single_writing = 'langalphSingle.csv:writing_system' in pattern
    
    # 统计各类型源的数量 (1=single, 2=multiple)
    writing_count = 0
    if has_writing_csv:
        writing_count = 1 if pattern.get('writing.csv:writing_system') == 'single' else 2
    if has_single_writing:
        single_count = 1 if pattern.get('langalphSingle.csv:writing_system') == 'single' else 2
        if writing_count == 0:
            writing_count = single_count
        else:
            # 合并计数：如果已有writing.csv，则变为multiple
            writing_count = 2
        
    lang_count = 0
    if has_lang_csv:
        lang_count = 1 if pattern.get('language.csv:language') == 'single' else 2
        
    map_lang_count = 0
    if has_langalph_lang:
        map_lang_count = 1 if pattern.get('langalphMap.json:language') == 'single' else 2
    
    map_writing_count = 0
    if has_langalph_writing:
        map_writing_count = 1 if pattern.get('langalphMap.json:writing_system') == 'single' else 2
    
    # 构建代码（为0的项略去）
    code_parts = []
    
    if writing_count > 0:
        code_parts.append(f"{writing_count}w")
    if lang_count > 0:
        code_parts.append(f"{lang_count}l")
    if map_lang_count > 0:
        code_parts.append(f"{map_lang_count}ml")
    if map_writing_count > 0:
        code_parts.append(f"{map_writing_count}mw")
    
    if not code_parts:
        return "empty"
    
    return "-".join(code_parts)

def classify_all_entities(paths_file='paths_final.json', output_dir='class'):
    """对所有实体进行分类并输出到对应目录"""
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 读取数据
    with open(paths_file, 'r', encoding='utf-8') as f:
        entities = json.load(f)
    
    # 分类统计
    categories = defaultdict(list)
    
    for entity in entities:
        category = classify_entity_by_sources(entity['sources'])
        categories[category].append(entity)
    
    # 输出各类别文件
    summary = {}
    for category, items in categories.items():
        # 保存分类数据
        category_file = output_path / f"{category}.json"
        with open(category_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        summary[category] = {
            'count': len(items),
            'file': str(category_file)
        }
        
        print(f"{category}: {len(items)} 个实体 -> {category_file}")
    
    # 生成分类汇总
    summary_file = output_path / "classification_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n分类汇总已保存到: {summary_file}")
    print(f"总计: {len(entities)} 个实体分为 {len(categories)} 个类别")
    
    return summary

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="根据source组合对实体进行分类")
    parser.add_argument('--input', default='paths_final.json', help='输入JSON文件')
    parser.add_argument('--output', default='class', help='输出目录')
    
    args = parser.parse_args()
    
    summary = classify_all_entities(args.input, args.output)
    
    # 显示统计
    print("\n=== 分类统计 ===")
    for category, info in sorted(summary.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"{category:25s}: {info['count']:4d} 个")

if __name__ == "__main__":
    main()

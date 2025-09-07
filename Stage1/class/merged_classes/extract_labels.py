#!/usr/bin/env python3
"""
从分类文件中提取标签，每个实体一行，实体内多个标签用逗号分隔
"""

import json

def clean_label(label):
    """清理标签，移除_using_部分"""
    return label.split('_using_')[0] if '_using_' in label else label

def extract_entity_labels(entity):
    """提取单个实体的所有标签"""
    labels = []
    for source in entity['sources']:
        cleaned = clean_label(source['label'])
        if cleaned not in labels:
            labels.append(cleaned)
    return labels

def merge_and_extract(input_files, output_prefix):
    """合并文件并提取标签"""
    all_entities = []
    
    for file_path in input_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_entities.extend(json.load(f))
    
    # 输出合并的JSON
    with open(f"{output_prefix}.json", 'w', encoding='utf-8') as f:
        json.dump(all_entities, f, ensure_ascii=False, indent=2)
    
    # 输出标签列表（每个实体一行）
    with open(f"{output_prefix}_labels.txt", 'w', encoding='utf-8') as f:
        for entity in all_entities:
            labels = extract_entity_labels(entity)
            f.write(', '.join(labels) + '\n')
    
    return len(all_entities)

if __name__ == "__main__":
    # 语言实体文件
    language_files = [
        '../1l-1ml.json',
        '../1l-2ml.json', 
        '../1l.json',
        '../1ml.json'
    ]
    
    count = merge_and_extract(language_files, 'languages')
    print(f"处理完成: {count} 个语言实体")

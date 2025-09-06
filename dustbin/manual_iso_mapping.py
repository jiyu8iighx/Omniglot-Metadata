#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实用的ISO映射脚本 - 生成具体的映射结果
支持多核并行处理
"""

import json
import csv
import re
from difflib import SequenceMatcher
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from functools import partial
import time

def normalize_name(name):
    """标准化名称用于匹配"""
    name = re.sub(r'\([^)]*\)', '', name)  # 移除括号
    name = re.sub(r'[,\-\']', ' ', name)   # 替换标点
    name = re.sub(r'\s+', ' ', name).strip().lower()
    return name

def similarity_score(str1, str2):
    """计算相似度"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def load_data():
    """加载所有数据"""
    # 加载实体数据
    with open('entity_analysis_report.json', 'r', encoding='utf-8') as f:
        entities = json.load(f)['entities']
    
    # 加载ISO 639-3
    iso639 = {}
    with open('iso-639-3_Name_Index.tab', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            iso639[row['Id']] = {
                'print_name': row['Print_Name'],
                'inverted_name': row['Inverted_Name']
            }
    
    # 加载ISO 15924
    iso15924 = {}
    with open('iso15924-codes.tsv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            iso15924[row['Code']] = {
                'english_name': row['English Name'],
                'alias': row['Alias'] if row['Alias'] else None
            }
    
    return entities, iso639, iso15924

def resolve_conflicts(entities):
    """解决类型冲突"""
    resolved = {}
    conflicts = []
    
    for entity_id, entity_data in entities.items():
        if entity_data['is_fragment']:
            continue
            
        type_hints = set(entity_data['type_hints'])
        sources = set(entity_data['sources'])
        
        # 检查是否有真实冲突
        is_conflict = (len(type_hints) > 1 and not (
            type_hints <= {'language', 'multi_lang_writing'} or 
            type_hints <= {'writing_system', 'single_lang_writing', 'multi_lang_writing'}
        ))
        
        if is_conflict:
            conflicts.append(entity_id)
            # 解决冲突的规则
            if 'langalph_single_csv' in sources:
                resolved_type = 'writing_system'
            elif 'multi_lang_writing' in type_hints:
                resolved_type = 'writing_system'
            elif 'writing_csv' in sources and 'language_csv' not in sources:
                resolved_type = 'writing_system'
            else:
                # 检查标签中的关键词
                labels = ' '.join(entity_data['labels']).lower()
                if any(kw in labels for kw in ['script', 'alphabet', 'writing', 'cuneiform']):
                    resolved_type = 'writing_system'
                else:
                    resolved_type = 'language'
            resolved[entity_id] = resolved_type
        else:
            resolved[entity_id] = entity_data['primary_type']
    
    return resolved, conflicts

def find_best_matches(entity_labels, iso_data, threshold=0.8):
    """找到最佳匹配"""
    best_matches = []
    
    for label in entity_labels:
        normalized_label = normalize_name(label)
        
        for iso_code, iso_info in iso_data.items():
            # 对于ISO 639-3
            if 'print_name' in iso_info:
                scores = [
                    similarity_score(normalized_label, normalize_name(iso_info['print_name'])),
                    similarity_score(normalized_label, normalize_name(iso_info['inverted_name']))
                ]
                max_score = max(scores)
                if max_score >= threshold:
                    best_matches.append({
                        'iso_code': iso_code,
                        'score': max_score,
                        'omniglot_label': label,
                        'iso_name': iso_info['print_name']
                    })
            
            # 对于ISO 15924
            elif 'english_name' in iso_info:
                scores = [similarity_score(normalized_label, normalize_name(iso_info['english_name']))]
                if iso_info['alias']:
                    scores.append(similarity_score(normalized_label, normalize_name(iso_info['alias'])))
                max_score = max(scores)
                if max_score >= threshold:
                    best_matches.append({
                        'iso_code': iso_code,
                        'score': max_score,
                        'omniglot_label': label,
                        'iso_name': iso_info['english_name']
                    })
    
    # 返回分数最高的匹配
    if best_matches:
        return sorted(best_matches, key=lambda x: x['score'], reverse=True)[0]
    return None

def process_entity_batch(entity_batch, iso639, iso15924, resolved_types):
    """并行处理一批实体"""
    batch_results = {
        'language_mappings': {},
        'writing_mappings': {},
        'unmapped_languages': [],
        'unmapped_writings': []
    }
    
    for entity_id, entity_data in entity_batch:
        if entity_data['is_fragment']:
            continue
        
        entity_type = resolved_types[entity_id]
        labels = entity_data['labels']
        
        if entity_type == 'language':
            match = find_best_matches(labels, iso639)
            if match:
                batch_results['language_mappings'][entity_id] = match
            else:
                batch_results['unmapped_languages'].append({'entity_id': entity_id, 'labels': labels})
        
        elif entity_type == 'writing_system':
            match = find_best_matches(labels, iso15924)
            if match:
                batch_results['writing_mappings'][entity_id] = match
            else:
                batch_results['unmapped_writings'].append({'entity_id': entity_id, 'labels': labels})
    
    return batch_results

def chunk_dict(data, chunk_size):
    """将字典分块"""
    items = list(data.items())
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

def main():
    print("开始ISO映射...")
    
    # 加载数据
    entities, iso639, iso15924 = load_data()
    print(f"加载完成: {len(entities)} 实体, {len(iso639)} ISO639, {len(iso15924)} ISO15924")
    
    # 解决冲突
    resolved_types, conflicts = resolve_conflicts(entities)
    print(f"解决了 {len(conflicts)} 个类型冲突")
    
    # 准备多核并行处理
    num_cores = cpu_count()
    print(f"使用 {num_cores} 个CPU核心进行并行处理")
    
    # 过滤掉fragment实体
    non_fragment_entities = {k: v for k, v in entities.items() if not v['is_fragment']}
    total_entities = len(non_fragment_entities)
    
    # 将实体分块
    chunk_size = max(1, total_entities // (num_cores * 4))  # 每核心4个任务
    entity_chunks = list(chunk_dict(non_fragment_entities, chunk_size))
    
    print(f"将 {total_entities} 个实体分为 {len(entity_chunks)} 个批次处理")
    
    # 创建并行处理函数
    process_batch = partial(process_entity_batch, 
                           iso639=iso639, 
                           iso15924=iso15924, 
                           resolved_types=resolved_types)
    
    # 执行并行映射
    start_time = time.time()
    with Pool(num_cores) as pool:
        batch_results = pool.map(process_batch, entity_chunks)
    
    # 合并结果
    language_mappings = {}
    writing_mappings = {}
    unmapped = {'languages': [], 'writing_systems': []}
    
    for batch_result in batch_results:
        language_mappings.update(batch_result['language_mappings'])
        writing_mappings.update(batch_result['writing_mappings'])
        unmapped['languages'].extend(batch_result['unmapped_languages'])
        unmapped['writing_systems'].extend(batch_result['unmapped_writings'])
    
    processing_time = time.time() - start_time
    print(f"并行处理完成，耗时 {processing_time:.2f} 秒")
    
    # 保存结果
    results = {
        'statistics': {
            'total_processed': total_entities,
            'conflicts_resolved': len(conflicts),
            'languages_mapped': len(language_mappings),
            'writing_systems_mapped': len(writing_mappings),
            'languages_unmapped': len(unmapped['languages']),
            'writing_systems_unmapped': len(unmapped['writing_systems']),
            'processing_time_seconds': processing_time,
            'cpu_cores_used': num_cores
        },
        'mappings': {
            'languages': language_mappings,
            'writing_systems': writing_mappings
        },
        'unmapped': unmapped,
        'conflicts_resolved': [{'entity_id': eid, 'resolved_as': resolved_types[eid]} for eid in conflicts]
    }
    
    with open('iso_mapping_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 输出统计
    print(f"\n=== 映射完成 ===")
    print(f"处理实体总数: {total_entities}")
    print(f"解决类型冲突: {len(conflicts)}")
    print(f"语言映射成功: {len(language_mappings)}")
    print(f"书写系统映射成功: {len(writing_mappings)}")
    print(f"未映射语言: {len(unmapped['languages'])}")
    print(f"未映射书写系统: {len(unmapped['writing_systems'])}")
    print(f"处理时间: {processing_time:.2f} 秒")
    print(f"使用CPU核心: {num_cores}")
    print(f"\n结果已保存到: iso_mapping_results.json")

if __name__ == "__main__":
    main()
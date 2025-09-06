#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体标准化脚本 - 基于if-else规则的类型推断
实现支持双重角色的实体分类系统
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

class EntityStandardizer:
    def __init__(self):
        self.entities = {}
        self.evidence_rules = {
            'langalph_single_csv': {'type': 'single_lang_writing', 'confidence': 'high'},
            'langalph_map_json': {'type': 'multi_lang_writing', 'confidence': 'high'},
            'writing_csv': {'type': 'writing_system', 'confidence': 'medium'},
            'language_csv': {'type': 'language', 'confidence': 'medium'}
        }
    
    def load_data(self):
        """加载所有源数据"""
        print("正在加载源数据...")
        
        # 加载language.csv
        language_entities = {}
        with open('language.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    path, label = row[0], row[1]
                    entity_id = self.normalize_path(path)
                    if entity_id not in language_entities:
                        language_entities[entity_id] = {'paths': [], 'labels': []}
                    language_entities[entity_id]['paths'].append(path)
                    language_entities[entity_id]['labels'].append(label)
        
        # 加载writing.csv
        writing_entities = {}
        with open('writing.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    path, label = row[0], row[1]
                    entity_id = self.normalize_path(path)
                    if entity_id not in writing_entities:
                        writing_entities[entity_id] = {'paths': [], 'labels': []}
                    writing_entities[entity_id]['paths'].append(path)
                    writing_entities[entity_id]['labels'].append(label)
        
        # 加载langalphSingle.csv
        single_writing_entities = {}
        with open('langalphSingle.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    path, label = row[0], row[1]
                    entity_id = self.normalize_path(path)
                    if entity_id not in single_writing_entities:
                        single_writing_entities[entity_id] = {'paths': [], 'labels': []}
                    single_writing_entities[entity_id]['paths'].append(path)
                    single_writing_entities[entity_id]['labels'].append(label)
        
        # 加载langalphMap.json
        map_entities = {}
        with open('langalphMap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                writing_info = item['writing']
                entity_id = self.normalize_path(writing_info['Link'])
                if entity_id not in map_entities:
                    map_entities[entity_id] = {'paths': [], 'labels': []}
                map_entities[entity_id]['paths'].append(writing_info['Link'])
                map_entities[entity_id]['labels'].append(writing_info['Label'])
        
        # 合并所有实体
        all_entity_ids = set(language_entities.keys()) | set(writing_entities.keys()) | \
                        set(single_writing_entities.keys()) | set(map_entities.keys())
        
        for entity_id in all_entity_ids:
            self.entities[entity_id] = {
                'id': entity_id,
                'paths': [],
                'labels': [],
                'evidence': [],
                'fragments': []
            }
            
            # 合并数据
            for source, entities_dict in [
                ('language_csv', language_entities),
                ('writing_csv', writing_entities), 
                ('langalph_single_csv', single_writing_entities),
                ('langalph_map_json', map_entities)
            ]:
                if entity_id in entities_dict:
                    entity_data = entities_dict[entity_id]
                    self.entities[entity_id]['paths'].extend(entity_data['paths'])
                    self.entities[entity_id]['labels'].extend(entity_data['labels'])
                    
                    # 添加证据
                    rule = self.evidence_rules[source]
                    self.entities[entity_id]['evidence'].append({
                        'source': source,
                        'type': rule['type'],
                        'confidence': rule['confidence']
                    })
            
            # 去重
            self.entities[entity_id]['paths'] = list(set(self.entities[entity_id]['paths']))
            self.entities[entity_id]['labels'] = list(set(self.entities[entity_id]['labels']))
        
        print(f"加载完成：{len(self.entities)} 个实体")
    
    def normalize_path(self, path):
        """标准化路径"""
        # 移除路径前缀
        if path.startswith('/writing/'):
            path = path[9:]
        elif path.startswith('../language/articles/'):
            path = path[21:]
        
        # 处理PHP后缀
        if path.endswith('.php'):
            path = path[:-4] + '.htm'
        
        # 移除fragment（用于实体ID）
        if '#' in path:
            path = path.split('#')[0]
        
        return path
    
    def infer_entity_type(self, entity):
        """使用if-else规则推断实体类型"""
        evidence = entity['evidence']
        labels = entity['labels']
        
        # 规则1：明确的单语言书写系统
        if self.has_evidence(evidence, 'langalph_single_csv', 'single_lang_writing'):
            return {
                'primary_type': 'writing_system',
                'secondary_type': None,
                'confidence': 'high',
                'reason': 'langalph_single_csv evidence'
            }
        
        # 规则2：明确的多语言书写系统
        if self.has_evidence(evidence, 'langalph_map_json', 'multi_lang_writing'):
            return {
                'primary_type': 'writing_system', 
                'secondary_type': None,
                'confidence': 'high',
                'reason': 'langalph_map_json evidence'
            }
        
        # 规则3：纯书写系统来源
        if self.only_has_sources(evidence, ['writing_csv']):
            return {
                'primary_type': 'writing_system',
                'secondary_type': None, 
                'confidence': 'medium',
                'reason': 'writing_csv only'
            }
        
        # 规则4：纯语言来源
        if self.only_has_sources(evidence, ['language_csv']):
            return {
                'primary_type': 'language',
                'secondary_type': None,
                'confidence': 'medium', 
                'reason': 'language_csv only'
            }
        
        # 规则5：内容启发式 - 书写系统关键词
        if self.contains_keywords(labels, ['script', 'alphabet', 'syllabary', 'writing', 'cuneiform', 'hieroglyph']):
            return {
                'primary_type': 'writing_system',
                'secondary_type': None,
                'confidence': 'low',
                'reason': 'writing system keywords'
            }
        
        # 规则6：混合证据 - 可能是双重角色
        if self.has_mixed_evidence(evidence):
            return {
                'primary_type': 'language',  # 默认主要类型
                'secondary_type': 'writing_system',  # 可能的次要类型
                'confidence': 'low',
                'reason': 'mixed evidence - possible dual role',
                'requires_review': True
            }
        
        # 默认：语言
        return {
            'primary_type': 'language',
            'secondary_type': None,
            'confidence': 'low',
            'reason': 'default to language'
        }
    
    def has_evidence(self, evidence, source, type_hint):
        """检查是否有特定证据"""
        return any(e['source'] == source and e['type'] == type_hint for e in evidence)
    
    def only_has_sources(self, evidence, sources):
        """检查是否只有特定来源"""
        evidence_sources = set(e['source'] for e in evidence)
        return evidence_sources.issubset(set(sources))
    
    def contains_keywords(self, labels, keywords):
        """检查标签是否包含关键词"""
        for label in labels:
            label_lower = label.lower()
            if any(keyword in label_lower for keyword in keywords):
                return True
        return False
    
    def has_mixed_evidence(self, evidence):
        """检查是否有混合证据"""
        types = set(e['type'] for e in evidence)
        sources = set(e['source'] for e in evidence)
        
        # 有不同类型的证据
        has_type_mix = len(types) > 1
        
        # 有不同来源的证据
        has_source_mix = len(sources) > 1
        
        return has_type_mix or has_source_mix
    
    def analyze_all_entities(self):
        """分析所有实体"""
        print("正在分析实体类型...")
        
        results = {
            'entities': {},
            'statistics': {
                'total': len(self.entities),
                'by_primary_type': defaultdict(int),
                'by_confidence': defaultdict(int),
                'dual_role': 0,
                'requires_review': 0
            }
        }
        
        for entity_id, entity in self.entities.items():
            type_result = self.infer_entity_type(entity)
            
            entity_result = {
                'id': entity_id,
                'paths': entity['paths'],
                'labels': entity['labels'],
                'evidence': entity['evidence'],
                'type_inference': type_result
            }
            
            results['entities'][entity_id] = entity_result
            
            # 统计
            results['statistics']['by_primary_type'][type_result['primary_type']] += 1
            results['statistics']['by_confidence'][type_result['confidence']] += 1
            
            if type_result.get('secondary_type'):
                results['statistics']['dual_role'] += 1
            
            if type_result.get('requires_review'):
                results['statistics']['requires_review'] += 1
        
        return results
    
    def save_results(self, results):
        """保存结果"""
        with open('entity_standardization_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 实体标准化结果 ===")
        print(f"总实体数: {results['statistics']['total']}")
        print(f"主要类型分布:")
        for type_name, count in results['statistics']['by_primary_type'].items():
            print(f"  {type_name}: {count}")
        print(f"置信度分布:")
        for conf, count in results['statistics']['by_confidence'].items():
            print(f"  {conf}: {count}")
        print(f"双重角色: {results['statistics']['dual_role']}")
        print(f"需要审查: {results['statistics']['requires_review']}")
        print(f"\n结果已保存到: entity_standardization_results.json")

def main():
    standardizer = EntityStandardizer()
    standardizer.load_data()
    results = standardizer.analyze_all_entities()
    standardizer.save_results(results)

if __name__ == "__main__":
    main()

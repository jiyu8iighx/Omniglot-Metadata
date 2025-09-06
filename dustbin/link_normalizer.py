#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
链接标准化和实体识别脚本
处理Omniglot项目中的各种链接格式，创建统一的实体标识符系统
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

class LinkNormalizer:
    def __init__(self):
        self.entity_map = defaultdict(lambda: {
            'paths': set(),
            'labels': set(), 
            'type_evidence': []  # [(source, type_hint), ...]
        })
        
    def normalize_path(self, path):
        """标准化链接路径"""
        # 移除开头的路径前缀
        if path.startswith('/writing/'):
            path = path[9:]
        elif path.startswith('../language/articles/'):
            path = path[21:]
            
        # 处理PHP后缀 - 根据用户说明，PHP文件实际上是HTML
        if path.endswith('.php'):
            base_path = path[:-4]
            return f"{base_path}.htm", path  # 返回标准化路径和原路径
        
        return path, path
        
    def extract_fragment_info(self, path):
        """提取Fragment信息"""
        if '#' in path:
            base_path, fragment = path.split('#', 1)
            return base_path, fragment
        return path, None
        
    def add_entity(self, path, label, source, type_hint=None):
        """添加实体信息"""
        normalized_path, original_path = self.normalize_path(path)
        base_path, fragment = self.extract_fragment_info(normalized_path)
        
        # 使用基础路径作为实体ID（不包含fragment）
        entity_id = base_path
        
        entity = self.entity_map[entity_id]
        entity['paths'].add(original_path)
        entity['labels'].add(label)
        
        if type_hint:
            entity['type_evidence'].append((source, type_hint))
            
        # 如果有fragment，记录为子实体
        if fragment:
            fragment_id = f"{entity_id}#{fragment}"
            fragment_entity = self.entity_map[fragment_id]
            fragment_entity['paths'].add(original_path)
            fragment_entity['labels'].add(label)
            fragment_entity['parent_entity'] = entity_id
            if type_hint:
                fragment_entity['type_evidence'].append((f"{source}_fragment", type_hint))
    
    def load_language_csv(self):
        """加载language.csv数据"""
        with open('language.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    self.add_entity(row[0], row[1], 'language_csv', 'language')
    
    def load_writing_csv(self):
        """加载writing.csv数据"""
        with open('writing.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    self.add_entity(row[0], row[1], 'writing_csv', 'writing_system')
    
    def load_langalph_single_csv(self):
        """加载langalphSingle.csv数据"""
        with open('langalphSingle.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    self.add_entity(row[0], row[1], 'langalph_single_csv', 'single_lang_writing')
    
    def load_langalph_map_json(self):
        """加载langalphMap.json数据"""
        with open('langalphMap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            writing_info = item['writing']
            # 书写系统实体
            self.add_entity(
                writing_info['Link'], 
                writing_info['Label'], 
                'langalph_map_json', 
                'multi_lang_writing'
            )
            
            # 关联的语言实体
            for lang_path, lang_label in item['language']:
                self.add_entity(lang_path, lang_label, 'langalph_map_json', 'language')
    
    def analyze_entity_types(self):
        """分析实体类型"""
        type_conflicts = []
        
        for entity_id, entity_data in self.entity_map.items():
            type_evidence = entity_data['type_evidence']
            type_hints = set(evidence[1] for evidence in type_evidence)
            
            # 检查类型冲突
            if len(type_hints) > 1:
                # 排除兼容的类型组合
                if not (type_hints <= {'language', 'multi_lang_writing'} or 
                       type_hints <= {'writing_system', 'single_lang_writing', 'multi_lang_writing'}):
                    type_conflicts.append({
                        'entity_id': entity_id,
                        'type_evidence': type_evidence,
                        'labels': list(entity_data['labels'])
                    })
        
        return type_conflicts
    
    def generate_entity_report(self):
        """生成实体报告"""
        report = {
            'total_entities': len(self.entity_map),
            'entities': {},
            'statistics': {
                'by_type': defaultdict(int),
                'by_source': defaultdict(int),
                'fragments': 0,
                'type_conflicts': 0
            }
        }
        
        for entity_id, entity_data in self.entity_map.items():
            # 判断是否为fragment实体
            is_fragment = '#' in entity_id
            if is_fragment:
                report['statistics']['fragments'] += 1
            
            # 统计类型
            primary_type = self.determine_primary_type(entity_data['type_evidence'])
            report['statistics']['by_type'][primary_type] += 1
            
            # 统计来源
            for source, _ in entity_data['type_evidence']:
                report['statistics']['by_source'][source] += 1
            
            # 转换set为list以便JSON序列化
            entity_info = {
                'paths': list(entity_data['paths']),
                'labels': list(entity_data['labels']),
                'type_evidence': entity_data['type_evidence'],
                'primary_type': primary_type,
                'is_fragment': is_fragment,
                'confidence_score': self.calculate_confidence(entity_data['type_evidence'])
            }
            
            if 'parent_entity' in entity_data:
                entity_info['parent_entity'] = entity_data['parent_entity']
                
            report['entities'][entity_id] = entity_info
        
        return report
    
    def determine_primary_type(self, type_evidence):
        """基于证据强度确定实体的主要类型"""
        if not type_evidence:
            return 'unknown'
        
        # 来源权重定义
        source_weights = {
            'langalph_single_csv': 3,      # 最可靠：明确的单语言书写系统
            'langalph_map_json': 3,        # 最可靠：明确的多语言书写系统映射
            'writing_csv': 2,              # 较可靠：来自书写系统索引页
            'language_csv': 2,             # 较可靠：来自语言索引页
            'langalph_map_json_fragment': 1, # 一般：fragment来源
            'writing_csv_fragment': 1,     # 一般：fragment来源
            'language_csv_fragment': 1     # 一般：fragment来源
        }
        
        # 类型权重累积
        type_scores = defaultdict(float)
        
        for source, type_hint in type_evidence:
            weight = source_weights.get(source, 1)
            
            # 将具体类型映射到主类型
            if type_hint in ['single_lang_writing', 'multi_lang_writing', 'writing_system']:
                type_scores['writing_system'] += weight
            elif type_hint == 'language':
                type_scores['language'] += weight
        
        if not type_scores:
            return 'unknown'
        
        # 返回得分最高的类型
        return max(type_scores.items(), key=lambda x: x[1])[0]
    
    def calculate_confidence(self, type_evidence):
        """计算类型判断的置信度"""
        if not type_evidence:
            return 0.0
        
        source_weights = {
            'langalph_single_csv': 3,
            'langalph_map_json': 3,
            'writing_csv': 2,
            'language_csv': 2,
            'langalph_map_json_fragment': 1,
            'writing_csv_fragment': 1,
            'language_csv_fragment': 1
        }
        
        total_weight = sum(source_weights.get(source, 1) for source, _ in type_evidence)
        max_possible = len(type_evidence) * 3
        
        return total_weight / max_possible if max_possible > 0 else 0.0

def main():
    """主处理函数"""
    normalizer = LinkNormalizer()
    
    print("正在加载数据文件...")
    normalizer.load_language_csv()
    normalizer.load_writing_csv() 
    normalizer.load_langalph_single_csv()
    normalizer.load_langalph_map_json()
    
    print("正在分析实体类型...")
    type_conflicts = normalizer.analyze_entity_types()
    
    print("正在生成报告...")
    report = normalizer.generate_entity_report()
    
    # 保存完整报告
    with open('entity_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 输出摘要
    print(f"\n=== 实体标准化分析报告 ===")
    print(f"总实体数量: {report['total_entities']}")
    print(f"Fragment实体数量: {report['statistics']['fragments']}")
    print(f"\n按类型分布:")
    for type_name, count in report['statistics']['by_type'].items():
        print(f"  {type_name}: {count}")
    print(f"\n按来源分布:")
    for source, count in report['statistics']['by_source'].items():
        print(f"  {source}: {count}")
    
    if type_conflicts:
        print(f"\n发现 {len(type_conflicts)} 个类型冲突:")
        for conflict in type_conflicts[:5]:  # 只显示前5个
            print(f"  {conflict['entity_id']}: {conflict['type_hints']} - {conflict['labels']}")
    
    print(f"\n完整报告已保存到: entity_analysis_report.json")

if __name__ == "__main__":
    main() 
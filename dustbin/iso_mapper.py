#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO代码映射脚本
处理实体类型冲突，建立Omniglot实体与ISO标准代码的映射关系
"""

import csv
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher

class ISOMapper:
    def __init__(self):
        self.entities = {}
        self.iso639_codes = {}
        self.iso15924_codes = {}
        self.conflicts = []
        self.mappings = {
            'languages': {},  # entity_id -> iso639_code
            'writing_systems': {},  # entity_id -> iso15924_code
            'unmapped': {
                'languages': [],
                'writing_systems': []
            }
        }
    
    def load_entity_data(self):
        """加载实体分析数据"""
        with open('entity_analysis_report.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.entities = data['entities']
        
        # 识别类型冲突
        for entity_id, entity_data in self.entities.items():
            type_hints = set(entity_data['type_hints'])
            # 真实的类型冲突（不是兼容的组合）
            if len(type_hints) > 1 and not (
                type_hints <= {'language', 'multi_lang_writing'} or 
                type_hints <= {'writing_system', 'single_lang_writing', 'multi_lang_writing'}
            ):
                self.conflicts.append(entity_id)
        
        print(f"加载了 {len(self.entities)} 个实体，发现 {len(self.conflicts)} 个类型冲突")
    
    def load_iso_standards(self):
        """加载ISO标准数据"""
        # 加载ISO 639-3语言代码
        with open('iso-639-3_Name_Index.tab', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                self.iso639_codes[row['Id']] = {
                    'print_name': row['Print_Name'],
                    'inverted_name': row['Inverted_Name']
                }
        
        # 加载ISO 15924书写系统代码
        with open('iso15924-codes.tsv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                self.iso15924_codes[row['Code']] = {
                    'number': row['N°'],
                    'english_name': row['English Name'],
                    'alias': row['Alias'] if row['Alias'] else None
                }
        
        print(f"加载了 {len(self.iso639_codes)} 个ISO 639-3语言代码")
        print(f"加载了 {len(self.iso15924_codes)} 个ISO 15924书写系统代码")
    
    def similarity_score(self, str1, str2):
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def normalize_name_for_matching(self, name):
        """标准化名称用于匹配"""
        # 移除括号内容
        name = re.sub(r'\([^)]*\)', '', name)
        # 移除常见的标点和修饰词
        name = re.sub(r'[,\-\']', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name.lower()
    
    def find_language_matches(self, entity_id, labels):
        """为语言实体寻找ISO 639-3匹配"""
        best_matches = []
        
        for label in labels:
            normalized_label = self.normalize_name_for_matching(label)
            
            for iso_code, iso_data in self.iso639_codes.items():
                # 检查Print_Name匹配
                print_name_norm = self.normalize_name_for_matching(iso_data['print_name'])
                score1 = self.similarity_score(normalized_label, print_name_norm)
                
                # 检查Inverted_Name匹配
                inverted_name_norm = self.normalize_name_for_matching(iso_data['inverted_name'])
                score2 = self.similarity_score(normalized_label, inverted_name_norm)
                
                max_score = max(score1, score2)
                
                if max_score >= 0.85:  # 高置信度匹配
                    best_matches.append({
                        'iso_code': iso_code,
                        'score': max_score,
                        'matched_field': 'print_name' if score1 >= score2 else 'inverted_name',
                        'omniglot_label': label,
                        'iso_name': iso_data['print_name']
                    })
        
        # 按分数排序并去重
        best_matches.sort(key=lambda x: x['score'], reverse=True)
        seen_codes = set()
        unique_matches = []
        for match in best_matches:
            if match['iso_code'] not in seen_codes:
                unique_matches.append(match)
                seen_codes.add(match['iso_code'])
        
        return unique_matches[:3]  # 返回前3个最佳匹配
    
    def find_writing_system_matches(self, entity_id, labels):
        """为书写系统实体寻找ISO 15924匹配"""
        best_matches = []
        
        for label in labels:
            normalized_label = self.normalize_name_for_matching(label)
            
            for iso_code, iso_data in self.iso15924_codes.items():
                # 检查English Name匹配
                english_name_norm = self.normalize_name_for_matching(iso_data['english_name'])
                score1 = self.similarity_score(normalized_label, english_name_norm)
                
                # 检查Alias匹配（如果存在）
                score2 = 0
                if iso_data['alias']:
                    alias_norm = self.normalize_name_for_matching(iso_data['alias'])
                    score2 = self.similarity_score(normalized_label, alias_norm)
                
                max_score = max(score1, score2)
                
                if max_score >= 0.85:  # 高置信度匹配
                    best_matches.append({
                        'iso_code': iso_code,
                        'score': max_score,
                        'matched_field': 'english_name' if score1 >= score2 else 'alias',
                        'omniglot_label': label,
                        'iso_name': iso_data['english_name']
                    })
        
        # 按分数排序并去重
        best_matches.sort(key=lambda x: x['score'], reverse=True)
        seen_codes = set()
        unique_matches = []
        for match in best_matches:
            if match['iso_code'] not in seen_codes:
                unique_matches.append(match)
                seen_codes.add(match['iso_code'])
        
        return unique_matches[:3]  # 返回前3个最佳匹配
    
    def resolve_entity_type(self, entity_id, entity_data):
        """解决实体类型冲突"""
        type_hints = set(entity_data['type_hints'])
        sources = entity_data['sources']
        
        # 基于来源的优先级判断
        if 'langalph_single_csv' in sources or 'multi_lang_writing' in type_hints:
            return 'writing_system'
        elif 'writing_csv' in sources and 'language_csv' not in sources:
            return 'writing_system'
        elif 'language_csv' in sources and 'writing_csv' not in sources:
            return 'language'
        else:
            # 基于标签内容的启发式判断
            labels = entity_data['labels']
            writing_keywords = ['script', 'alphabet', 'syllabary', 'writing', 'cuneiform', 'hieroglyph']
            
            for label in labels:
                label_lower = label.lower()
                if any(keyword in label_lower for keyword in writing_keywords):
                    return 'writing_system'
            
            # 默认返回语言（因为大多数冲突实体实际上是语言）
            return 'language'
    
    def create_mappings(self):
        """创建实体到ISO代码的映射"""
        mapped_languages = 0
        mapped_writing_systems = 0
        
        for entity_id, entity_data in self.entities.items():
            # 跳过fragment实体
            if entity_data['is_fragment']:
                continue
            
            # 确定实体类型
            if entity_id in self.conflicts:
                resolved_type = self.resolve_entity_type(entity_id, entity_data)
            else:
                resolved_type = entity_data['primary_type']
            
            labels = entity_data['labels']
            
            if resolved_type == 'language':
                matches = self.find_language_matches(entity_id, labels)
                if matches:
                    self.mappings['languages'][entity_id] = {
                        'best_match': matches[0],
                        'all_matches': matches,
                        'labels': list(labels)
                    }
                    mapped_languages += 1
                else:
                    self.mappings['unmapped']['languages'].append({
                        'entity_id': entity_id,
                        'labels': list(labels)
                    })
            
            elif resolved_type == 'writing_system':
                matches = self.find_writing_system_matches(entity_id, labels)
                if matches:
                    self.mappings['writing_systems'][entity_id] = {
                        'best_match': matches[0],
                        'all_matches': matches,
                        'labels': list(labels)
                    }
                    mapped_writing_systems += 1
                else:
                    self.mappings['unmapped']['writing_systems'].append({
                        'entity_id': entity_id,
                        'labels': list(labels)
                    })
        
        print(f"\n=== 映射结果统计 ===")
        print(f"成功映射的语言: {mapped_languages}")
        print(f"成功映射的书写系统: {mapped_writing_systems}")
        print(f"未映射的语言: {len(self.mappings['unmapped']['languages'])}")
        print(f"未映射的书写系统: {len(self.mappings['unmapped']['writing_systems'])}")
    
    def save_mappings(self):
        """保存映射结果"""
        with open('iso_mappings.json', 'w', encoding='utf-8') as f:
            json.dump(self.mappings, f, ensure_ascii=False, indent=2)
        
        # 创建冲突解决报告
        conflict_report = []
        for entity_id in self.conflicts:
            entity_data = self.entities[entity_id]
            resolved_type = self.resolve_entity_type(entity_id, entity_data)
            conflict_report.append({
                'entity_id': entity_id,
                'original_type_hints': list(entity_data['type_hints']),
                'resolved_type': resolved_type,
                'labels': list(entity_data['labels']),
                'sources': list(entity_data['sources'])
            })
        
        with open('conflict_resolution.json', 'w', encoding='utf-8') as f:
            json.dump(conflict_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n映射结果已保存到: iso_mappings.json")
        print(f"冲突解决报告已保存到: conflict_resolution.json")

def main():
    """主处理函数"""
    mapper = ISOMapper()
    
    print("正在加载实体数据...")
    mapper.load_entity_data()
    
    print("正在加载ISO标准数据...")
    mapper.load_iso_standards()
    
    print("正在创建映射...")
    mapper.create_mappings()
    
    print("正在保存结果...")
    mapper.save_mappings()

if __name__ == "__main__":
    main()

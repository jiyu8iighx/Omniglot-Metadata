#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径收集与验证器
收集所有源文件中的路径，处理Fragment，检查文件存在性
"""

import csv
import json
import os
from typing import List, Dict, Optional
from pathlib import Path
from urllib.parse import urljoin

class PathCollector:
    def __init__(self, base_dir: str = ".", input_dir: str = None):
        self.base_dir = Path(base_dir)
        self.input_dir = Path(input_dir) if input_dir else self.base_dir
        self.language_dir = self.base_dir / "language"
        self.writing_dir = self.base_dir / "writing"
        
    def parse_path(self, path: str) -> tuple:
        """解析路径，分离基础路径和Fragment"""
        if '#' in path:
            base_path, fragment = path.split('#', 1)
            return base_path, fragment
        return path, None
    
    def get_absolute_url_path(self, path: str) -> str:
        """将路径转换为相对于站点根目录的绝对路径"""
        base_path, fragment = self.parse_path(path)
        
        # 使用标准URL解析处理相对路径
        # 假设当前基础路径为 /writing/
        base_url = "/writing/"
        absolute_url = urljoin(base_url, base_path)
        
        # urljoin返回的是完整路径，我们只要路径部分
        return absolute_url
    
    def check_file_exists(self, base_path: str) -> bool:
        """检查文件是否存在"""
        # 获取绝对URL路径
        absolute_url = self.get_absolute_url_path(base_path)
        
        # 将绝对URL路径转换为本地文件路径
        # 去除开头的 '/' 并直接映射到input_dir下的相应目录结构
        if absolute_url.startswith('/'):
            relative_path = absolute_url[1:]  # 去除开头的 '/'
        else:
            relative_path = absolute_url
            
        # 构建完整的本地文件路径
        local_file_path = self.input_dir / relative_path
        
        return local_file_path.exists()
    
    def collect_from_language_csv(self) -> List[Dict]:
        """从language.csv收集路径"""
        paths = []
        csv_file = self.input_dir / "language.csv"
        
        if not csv_file.exists():
            print(f"警告: {csv_file} 不存在")
            return paths
            
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    path = row[0].strip()
                    label = row[1].strip()
                    
                    base_path, fragment = self.parse_path(path)
                    file_exists = self.check_file_exists(base_path)
                    absolute_url_path = self.get_absolute_url_path(path)
                    
                    paths.append({
                        'path': path,
                        'base_path': base_path,
                        'fragment': fragment,
                        'absolute_url_path': absolute_url_path,
                        'sources': [{'source': 'language.csv', 'label': label}],
                        'file_exists': file_exists
                    })
        
        return paths
    
    def collect_from_writing_csv(self) -> List[Dict]:
        """从writing.csv收集路径"""
        paths = []
        csv_file = self.input_dir / "writing.csv"
        
        if not csv_file.exists():
            print(f"警告: {csv_file} 不存在")
            return paths
            
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    path = row[0].strip()
                    label = row[1].strip()
                    
                    base_path, fragment = self.parse_path(path)
                    file_exists = self.check_file_exists(base_path)
                    absolute_url_path = self.get_absolute_url_path(path)
                    
                    paths.append({
                        'path': path,
                        'base_path': base_path,
                        'fragment': fragment,
                        'absolute_url_path': absolute_url_path,
                        'sources': [{'source': 'writing.csv', 'label': label}],
                        'file_exists': file_exists
                    })
        
        return paths
    
    def collect_from_langalph_single_csv(self) -> List[Dict]:
        """从langalphSingle.csv收集路径"""
        paths = []
        csv_file = self.input_dir / "langalphSingle.csv"
        
        if not csv_file.exists():
            print(f"警告: {csv_file} 不存在")
            return paths
            
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    path = row[0].strip()
                    label = row[1].strip()
                    
                    base_path, fragment = self.parse_path(path)
                    file_exists = self.check_file_exists(base_path)
                    absolute_url_path = self.get_absolute_url_path(path)
                    
                    paths.append({
                        'path': path,
                        'base_path': base_path,
                        'fragment': fragment,
                        'absolute_url_path': absolute_url_path,
                        'sources': [{'source': 'langalphSingle.csv', 'label': label}],
                        'file_exists': file_exists
                    })
        
        return paths
    
    def collect_from_langalph_map_json(self) -> List[Dict]:
        """从langalphMap.json收集路径"""
        paths = []
        json_file = self.input_dir / "langalphMap.json"
        
        if not json_file.exists():
            print(f"警告: {json_file} 不存在")
            return paths
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for entry in data:
            writing_info = entry['writing']
            languages = entry['language']
            
            # 书写系统路径
            writing_path = writing_info['Link']
            writing_label = writing_info['Label']
            
            base_path, fragment = self.parse_path(writing_path)
            file_exists = self.check_file_exists(base_path)
            absolute_url_path = self.get_absolute_url_path(writing_path)
            
            paths.append({
                'path': writing_path,
                'base_path': base_path,
                'fragment': fragment,
                'absolute_url_path': absolute_url_path,
                'sources': [{'source': 'langalphMap.json', 'label': f'{writing_label}_for_{len(languages)}_languages'}],
                'file_exists': file_exists
            })
            
            # 语言路径
            for lang_entry in languages:
                lang_path = lang_entry[0]  # 路径
                lang_label = lang_entry[1]  # 标签
                
                base_path, fragment = self.parse_path(lang_path)
                file_exists = self.check_file_exists(base_path)
                absolute_url_path = self.get_absolute_url_path(lang_path)
                
                paths.append({
                    'path': lang_path,
                    'base_path': base_path,
                    'fragment': fragment,
                    'absolute_url_path': absolute_url_path,
                    'sources': [{'source': 'langalphMap.json', 'label': f'{lang_label}_using_{writing_label}'}],
                    'file_exists': file_exists
                })
        
        return paths
    
    def merge_duplicate_paths(self, all_paths: List[Dict]) -> List[Dict]:
        """按绝对路径+Fragment合并重复条目，保留所有来源信息"""
        path_dict = {}
        
        for entry in all_paths:
            # 使用绝对路径+Fragment作为唯一键
            absolute_path = entry['absolute_url_path']
            fragment = entry['fragment'] or ''  # None转为空字符串
            unique_key = f"{absolute_path}#{fragment}"
            
            if unique_key in path_dict:
                # 合并来源信息
                path_dict[unique_key]['sources'].extend(entry['sources'])
            else:
                path_dict[unique_key] = entry
        
        return list(path_dict.values())
    
    def collect_all_paths(self) -> List[Dict]:
        """收集所有路径"""
        all_paths = []
        all_paths.extend(self.collect_from_language_csv())
        all_paths.extend(self.collect_from_writing_csv())
        all_paths.extend(self.collect_from_langalph_single_csv())
        all_paths.extend(self.collect_from_langalph_map_json())
        
        # 合并重复路径
        merged_paths = self.merge_duplicate_paths(all_paths)
        
        return merged_paths
    
    def generate_analysis_report(self, paths: List[Dict]) -> Dict:
        """生成分析报告"""
        total_paths = len(paths)
        existing_files = sum(1 for p in paths if p['file_exists'])
        missing_files = total_paths - existing_files
        
        fragment_paths = [p for p in paths if p['fragment'] is not None]
        php_paths = [p for p in paths if p['base_path'].endswith('.php')]
        
        # 统计来源分布
        source_counts = {}
        for path in paths:
            for source_info in path['sources']:
                source = source_info['source']
                source_counts[source] = source_counts.get(source, 0) + 1
        
        # 统计Fragment类型
        fragment_analysis = {}
        for path in fragment_paths:
            fragment = path['fragment']
            if fragment not in fragment_analysis:
                fragment_analysis[fragment] = {
                    'count': 0,
                    'examples': []
                }
            fragment_analysis[fragment]['count'] += 1
            if len(fragment_analysis[fragment]['examples']) < 3:
                fragment_analysis[fragment]['examples'].append({
                    'path': path['path'],
                    'sources': path['sources']
                })
        
        report = {
            'summary': {
                'total_paths': total_paths,
                'existing_files': existing_files,
                'missing_files': missing_files,
                'fragment_paths': len(fragment_paths),
                'php_paths': len(php_paths)
            },
            'source_distribution': source_counts,
            'fragment_analysis': fragment_analysis,
            'missing_files_sample': [
                {
                    'path': p['path'],
                    'base_path': p['base_path'],
                    'sources': p['sources']
                }
                for p in paths if not p['file_exists']
            ][:10]  # 只显示前10个缺失文件示例
        }
        
        return report
    
    def save_results(self, paths: List[Dict], report: Dict):
        """保存结果"""
        # 保存路径收集结果
        output_file = self.base_dir / "paths_raw.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(paths, f, ensure_ascii=False, indent=2)
        print(f"路径收集结果已保存到: {output_file}")
        
        # 保存分析报告
        report_file = self.base_dir / "path_analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"分析报告已保存到: {report_file}")
    
    def run(self):
        """执行完整的路径收集流程"""
        paths = self.collect_all_paths()
        report = self.generate_analysis_report(paths)
        self.save_results(paths, report)

if __name__ == "__main__":
    # 输入从Stage0读取，输出到当前目录(stage1)
    collector = PathCollector(".", "../Stage0")
    collector.run()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON到CSV转换工具
处理嵌套字典和列表展开，便于检视数据
"""

import json
import csv
import os
from typing import Dict, List, Any, Set
from pathlib import Path

class JsonToCsvConverter:
    def __init__(self):
        self.all_columns = set()
    
    def flatten_dict(self, data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """将嵌套字典扁平化"""
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self.flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # 对于列表，我们先不在这里处理，留给expand_lists处理
                items.append((new_key, value))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def expand_lists(self, flattened_data: List[Dict]) -> List[Dict]:
        """展开列表，每个列表元素创建一行"""
        expanded_rows = []
        
        for row in flattened_data:
            # 找出所有包含列表的字段
            list_fields = {}
            scalar_fields = {}
            
            for key, value in row.items():
                if isinstance(value, list):
                    list_fields[key] = value
                else:
                    scalar_fields[key] = value
            
            if not list_fields:
                # 没有列表字段，直接添加
                expanded_rows.append(row)
            else:
                # 有列表字段，需要展开
                # 找出最大列表长度
                max_length = max(len(lst) for lst in list_fields.values()) if list_fields else 1
                
                for i in range(max_length):
                    new_row = scalar_fields.copy()
                    
                    for list_key, list_value in list_fields.items():
                        if i < len(list_value):
                            item = list_value[i]
                            if isinstance(item, dict):
                                # 如果列表元素是字典，进一步扁平化
                                flattened_item = self.flatten_dict(item, f"{list_key}")
                                new_row.update(flattened_item)
                            else:
                                new_row[list_key] = item
                        else:
                            # 列表已结束，填充空值
                            if isinstance(list_value[0], dict) if list_value else False:
                                # 需要为字典的所有可能键创建空值
                                sample_keys = set()
                                for sample_item in list_value:
                                    if isinstance(sample_item, dict):
                                        sample_keys.update(self.flatten_dict(sample_item, f"{list_key}").keys())
                                for empty_key in sample_keys:
                                    new_row[empty_key] = None
                            else:
                                new_row[list_key] = None
                    
                    expanded_rows.append(new_row)
        
        return expanded_rows
    
    def collect_all_columns(self, data: List[Dict]) -> List[str]:
        """收集所有可能的列名"""
        all_columns = set()
        
        for row in data:
            all_columns.update(row.keys())
        
        # 排序列名，让相关的列靠近
        sorted_columns = sorted(all_columns)
        return sorted_columns
    
    def convert_json_to_csv(self, json_file: str, csv_file: str = None):
        """转换JSON文件到CSV"""
        json_path = Path(json_file)
        if not json_path.exists():
            print(f"错误：文件 {json_file} 不存在")
            return
        
        # 生成CSV文件名
        if csv_file is None:
            csv_file = json_path.with_suffix('.csv')
        
        print(f"正在转换: {json_file} -> {csv_file}")
        
        # 读取JSON数据
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("错误：JSON文件必须包含一个对象数组")
            return
        
        if not data:
            print("警告：JSON文件为空")
            return
        
        # 第一步：扁平化所有字典
        flattened_data = []
        for item in data:
            flattened_item = self.flatten_dict(item)
            flattened_data.append(flattened_item)
        
        # 第二步：展开列表
        expanded_data = self.expand_lists(flattened_data)
        
        # 第三步：收集所有列名
        all_columns = self.collect_all_columns(expanded_data)
        
        # 第四步：写入CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            writer.writeheader()
            
            for row in expanded_data:
                # 确保所有列都有值（空值用None表示）
                complete_row = {}
                for col in all_columns:
                    complete_row[col] = row.get(col, None)
                writer.writerow(complete_row)
        
        print(f"转换完成！生成了 {len(expanded_data)} 行，{len(all_columns)} 列")
        print(f"列名示例: {all_columns[:10]}...")
    
    def convert_analysis_report(self, report_file: str):
        """专门转换分析报告的特殊处理"""
        print(f"正在转换分析报告: {report_file}")
        
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 分别处理不同部分
        base_name = Path(report_file).stem
        
        # 1. 基本摘要
        if 'summary' in data:
            summary_data = [data['summary']]
            summary_csv = f"{base_name}_summary.csv"
            self._write_simple_csv(summary_data, summary_csv)
            print(f"生成摘要表: {summary_csv}")
        
        # 2. 来源分布
        if 'source_distribution' in data:
            source_data = [{'source': k, 'count': v} for k, v in data['source_distribution'].items()]
            source_csv = f"{base_name}_source_distribution.csv"
            self._write_simple_csv(source_data, source_csv)
            print(f"生成来源分布表: {source_csv}")
        
        # 3. Fragment分析
        if 'fragment_analysis' in data:
            fragment_data = []
            for fragment, info in data['fragment_analysis'].items():
                base_row = {'fragment': fragment, 'count': info['count']}
                for i, example in enumerate(info['examples']):
                    row = base_row.copy()
                    row['example_index'] = i
                    row['example_path'] = example['path']
                    # 展开sources
                    for j, source in enumerate(example['sources']):
                        row[f'source_{j}_name'] = source['source']
                        row[f'source_{j}_label'] = source['label']
                    fragment_data.append(row)
            
            fragment_csv = f"{base_name}_fragment_analysis.csv"
            self._write_simple_csv(fragment_data, fragment_csv)
            print(f"生成Fragment分析表: {fragment_csv}")
        
        # 4. 缺失文件示例
        if 'missing_files_sample' in data:
            missing_csv = f"{base_name}_missing_files.csv"
            self.convert_json_data_to_csv(data['missing_files_sample'], missing_csv)
            print(f"生成缺失文件表: {missing_csv}")
    
    def convert_json_data_to_csv(self, data: List[Dict], csv_file: str):
        """直接转换JSON数据到CSV（不从文件读取）"""
        if not data:
            print("警告：数据为空")
            return
        
        # 扁平化和展开
        flattened_data = [self.flatten_dict(item) for item in data]
        expanded_data = self.expand_lists(flattened_data)
        all_columns = self.collect_all_columns(expanded_data)
        
        # 写入CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            writer.writeheader()
            
            for row in expanded_data:
                complete_row = {col: row.get(col, None) for col in all_columns}
                writer.writerow(complete_row)
    
    def _write_simple_csv(self, data: List[Dict], csv_file: str):
        """写入简单的CSV（不需要复杂处理）"""
        if not data:
            return
        
        all_columns = set()
        for row in data:
            all_columns.update(row.keys())
        all_columns = sorted(all_columns)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            writer.writeheader()
            writer.writerows(data)

def main():
    converter = JsonToCsvConverter()
    
    # 检查当前目录下的JSON文件
    json_files = list(Path('.').glob('*.json'))
    
    if not json_files:
        print("当前目录下没有找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件:")
    for i, file in enumerate(json_files, 1):
        print(f"  {i}. {file.name}")
    
    print("\n开始转换...")
    
    for json_file in json_files:
        try:
            if json_file.name == 'path_analysis_report.json':
                # 分析报告需要特殊处理
                converter.convert_analysis_report(str(json_file))
            else:
                # 普通JSON文件
                converter.convert_json_to_csv(str(json_file))
        except Exception as e:
            print(f"转换 {json_file.name} 时出错: {e}")
    
    print("\n所有转换完成！")

if __name__ == "__main__":
    main()

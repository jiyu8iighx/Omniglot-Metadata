#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于结构声明的JSON到CSV转换器
支持定长列表（tuple类型）和键匿名字典的声明式处理
"""

import json
import csv
from typing import Dict, List, Any, Union, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class ListType(Enum):
    """列表处理类型"""
    EXPAND = "expand"        # 展开为多行（默认）
    TUPLE = "tuple"          # 定长元组，写入单个单元格
    INDEXED_DICT = "indexed_dict"  # 键匿名字典，用索引作为键

@dataclass
class FieldSpec:
    """字段规范"""
    path: str                           # 字段路径，如 "sources"
    list_type: ListType = ListType.EXPAND  # 列表处理方式
    tuple_length: Optional[int] = None     # 如果是tuple，指定长度
    separator: str = " | "                 # tuple类型的分隔符

class StructuredConverter:
    def __init__(self, field_specs: Dict[str, FieldSpec] = None):
        """
        初始化转换器
        
        Args:
            field_specs: 字段规范字典，键为字段路径，值为FieldSpec
        """
        self.field_specs = field_specs or {}
        self.all_columns = set()
    
    def get_field_spec(self, path: str) -> FieldSpec:
        """获取字段规范，如果未指定则使用默认值"""
        return self.field_specs.get(path, FieldSpec(path))
    
    def flatten_dict(self, data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """扁平化字典，考虑字段规范"""
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self.flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                spec = self.get_field_spec(new_key)
                
                if spec.list_type == ListType.TUPLE:
                    # 处理为元组，写入单个单元格
                    if all(self._is_primitive(item) for item in value):
                        # 所有元素都是基本类型
                        items.append((new_key, spec.separator.join(str(item) for item in value)))
                    else:
                        # 包含复杂类型，按索引展开
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                items.extend(self.flatten_dict(item, f"{new_key}.{i}", sep=sep).items())
                            else:
                                items.append((f"{new_key}.{i}", item))
                
                elif spec.list_type == ListType.INDEXED_DICT:
                    # 处理为键匿名字典
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.extend(self.flatten_dict(item, f"{new_key}.{i}", sep=sep).items())
                        else:
                            items.append((f"{new_key}.{i}", item))
                
                else:  # ListType.EXPAND
                    # 保持原样，留给后续处理
                    items.append((new_key, value))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def _is_primitive(self, value: Any) -> bool:
        """判断是否为基本类型"""
        return isinstance(value, (str, int, float, bool, type(None)))
    
    def expand_lists(self, flattened_data: List[Dict]) -> List[Dict]:
        """展开需要展开的列表"""
        expanded_rows = []
        
        for row in flattened_data:
            # 找出需要展开的列表字段
            expand_fields = {}
            other_fields = {}
            
            for key, value in row.items():
                if isinstance(value, list):
                    spec = self.get_field_spec(key)
                    if spec.list_type == ListType.EXPAND:
                        expand_fields[key] = value
                    else:
                        other_fields[key] = value
                else:
                    other_fields[key] = value
            
            if not expand_fields:
                # 没有需要展开的列表
                expanded_rows.append(row)
            else:
                # 展开列表
                max_length = max(len(lst) for lst in expand_fields.values()) if expand_fields else 1
                
                for i in range(max_length):
                    new_row = other_fields.copy()
                    
                    for list_key, list_value in expand_fields.items():
                        if i < len(list_value):
                            item = list_value[i]
                            if isinstance(item, dict):
                                # 字典元素扁平化
                                flattened_item = self.flatten_dict(item, f"{list_key}")
                                new_row.update(flattened_item)
                            elif isinstance(item, list) and len(item) == 2:
                                # 处理二元组 ["path", "label"]
                                new_row[f"{list_key}.path"] = item[0]
                                new_row[f"{list_key}.label"] = item[1]
                            else:
                                new_row[list_key] = item
                        else:
                            # 填充空值
                            if list_value and isinstance(list_value[0], dict):
                                # 为字典的所有可能键创建空值
                                sample_keys = set()
                                for sample_item in list_value:
                                    if isinstance(sample_item, dict):
                                        sample_keys.update(self.flatten_dict(sample_item, f"{list_key}").keys())
                                for empty_key in sample_keys:
                                    new_row[empty_key] = None
                            elif list_value and isinstance(list_value[0], list) and len(list_value[0]) == 2:
                                # 为二元组创建空值
                                new_row[f"{list_key}.path"] = None
                                new_row[f"{list_key}.label"] = None
                            else:
                                new_row[list_key] = None
                    
                    expanded_rows.append(new_row)
        
        return expanded_rows
    
    def collect_all_columns(self, data: List[Dict]) -> List[str]:
        """收集所有列名并排序"""
        all_columns = set()
        for row in data:
            all_columns.update(row.keys())
        return sorted(all_columns)
    
    def convert_data(self, data: List[Dict]) -> tuple[List[Dict], List[str]]:
        """转换数据"""
        if not data:
            return [], []
        
        # 扁平化
        flattened_data = [self.flatten_dict(item) for item in data]
        
        # 展开列表
        expanded_data = self.expand_lists(flattened_data)
        
        # 收集列名
        all_columns = self.collect_all_columns(expanded_data)
        
        return expanded_data, all_columns
    
    def convert_json_to_csv(self, json_file: str, csv_file: str = None):
        """转换JSON文件到CSV"""
        json_path = Path(json_file)
        if not json_path.exists():
            print(f"错误：文件 {json_file} 不存在")
            return
        
        if csv_file is None:
            csv_file = json_path.with_suffix('.csv')
        
        print(f"正在转换: {json_file} -> {csv_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("错误：JSON文件必须包含一个对象数组")
            return
        
        expanded_data, all_columns = self.convert_data(data)
        
        # 写入CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            writer.writeheader()
            
            for row in expanded_data:
                complete_row = {col: row.get(col, None) for col in all_columns}
                writer.writerow(complete_row)
        
        print(f"转换完成！生成了 {len(expanded_data)} 行，{len(all_columns)} 列")

# 预定义的结构规范
PATH_COLLECTION_SPECS = {
    "sources": FieldSpec("sources", ListType.EXPAND)  # sources需要展开
}

# paths_final.json的展开规则（新的最终路径结构）
PATHS_FINAL_SPECS = {
    "sources": FieldSpec("sources", ListType.EXPAND)  # sources需要展开
}

LANGALPH_MAP_SPECS = {
    "language": FieldSpec("language", ListType.EXPAND)  # language数组需要展开
}

# 示例：如果某个数据有定长元组
EXAMPLE_TUPLE_SPECS = {
    "coordinates": FieldSpec("coordinates", ListType.TUPLE, tuple_length=2, separator=", "),  # [lat, lng] -> "lat, lng"
    "rgb_color": FieldSpec("rgb_color", ListType.TUPLE, tuple_length=3, separator="|"),       # [r, g, b] -> "r|g|b"
    "metadata.tags": FieldSpec("metadata.tags", ListType.TUPLE, separator=" | "),           # 标签列表 -> "tag1 | tag2 | tag3"
}

def main():
    """主函数，演示不同规范的使用"""
    
    # 1. 转换path_collection.json（sources需要展开）
    if Path('path_collection.json').exists():
        print("=== 转换 path_collection.json ===")
        converter = StructuredConverter(PATH_COLLECTION_SPECS)
        converter.convert_json_to_csv('path_collection.json', 'path_collection_structured.csv')
    
    # 2. 转换langalphMap.json（language需要展开）
    if Path('langalphMap.json').exists():
        print("\n=== 转换 langalphMap.json ===")
        converter = StructuredConverter(LANGALPH_MAP_SPECS)
        converter.convert_json_to_csv('langalphMap.json', 'langalphMap_structured.csv')
    
    # 3. 演示tuple类型处理（如果有相应数据）
    print("\n=== 演示tuple类型处理 ===")
    
    # 创建示例数据
    example_data = [
        {
            "name": "Point A",
            "coordinates": [40.7128, -74.0060],  # 这将被处理为 "40.7128, -74.0060"
            "rgb_color": [255, 128, 64],         # 这将被处理为 "255|128|64"
            "metadata": {
                "tags": ["location", "landmark", "NYC"]  # 这将被处理为 "location | landmark | NYC"
            },
            "properties": {
                "elevation": 10,
                "population": 8000000
            }
        },
        {
            "name": "Point B", 
            "coordinates": [34.0522, -118.2437],
            "rgb_color": [128, 255, 128],
            "metadata": {
                "tags": ["city", "west-coast"]
            },
            "properties": {
                "elevation": 71,
                "population": 4000000
            }
        }
    ]
    
    # 使用tuple规范转换
    converter = StructuredConverter(EXAMPLE_TUPLE_SPECS)
    expanded_data, columns = converter.convert_data(example_data)
    
    print("示例数据转换结果:")
    print(f"列名: {columns}")
    for i, row in enumerate(expanded_data):
        print(f"行 {i}: {row}")

if __name__ == "__main__":
    main()

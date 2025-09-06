#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON到CSV命令行转换工具
基于结构化转换器，支持预定义规范和自定义配置
"""

import argparse
import json
import sys
from pathlib import Path
from structured_json_to_csv import (
    StructuredConverter, 
    FieldSpec, 
    ListType,
    PATH_COLLECTION_SPECS,
    PATHS_FINAL_SPECS,
    LANGALPH_MAP_SPECS,
    EXAMPLE_TUPLE_SPECS
)

# 预定义规范配置
PRESET_SPECS = {
    'path_collection': PATH_COLLECTION_SPECS,
    'paths_final': PATHS_FINAL_SPECS,
    'langalph_map': LANGALPH_MAP_SPECS,
    'example_tuple': EXAMPLE_TUPLE_SPECS,
    'default': {}  # 默认规范（全部展开）
}

def load_custom_specs(spec_file: str) -> dict:
    """从JSON文件加载自定义规范"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec_data = json.load(f)
        
        specs = {}
        for path, config in spec_data.items():
            list_type = ListType(config.get('list_type', 'expand'))
            tuple_length = config.get('tuple_length')
            separator = config.get('separator', ' | ')
            
            specs[path] = FieldSpec(
                path=path,
                list_type=list_type,
                tuple_length=tuple_length,
                separator=separator
            )
        
        return specs
    except Exception as e:
        print(f"错误：无法加载规范文件 {spec_file}: {e}")
        sys.exit(1)

def create_example_spec_file(output_file: str):
    """创建示例规范文件"""
    example_specs = {
        "sources": {
            "list_type": "expand",
            "description": "展开sources数组，每个元素一行"
        },
        "coordinates": {
            "list_type": "tuple",
            "tuple_length": 2,
            "separator": ", ",
            "description": "坐标[lat,lng]处理为单个字符串"
        },
        "metadata.tags": {
            "list_type": "tuple",
            "separator": " | ",
            "description": "标签数组连接为单个字符串"
        },
        "items": {
            "list_type": "indexed_dict",
            "description": "用索引作为键展开：items.0.field, items.1.field"
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(example_specs, f, ensure_ascii=False, indent=2)
    
    print(f"示例规范文件已创建: {output_file}")
    print("编辑此文件后可用 --custom-specs 参数使用")

def list_presets():
    """列出所有预设规范"""
    print("可用的预设规范:")
    print("  default        - 默认规范（所有列表都展开）")
    print("  path_collection - 适用于path_collection.json")
    print("  langalph_map   - 适用于langalphMap.json")
    print("  example_tuple  - 演示tuple类型处理")
    print("\n使用方法: json2csv.py --preset <name> input.json")

def main():
    parser = argparse.ArgumentParser(
        description='JSON到CSV转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用默认规范
  json2csv.py data.json

  # 使用预设规范
  json2csv.py --preset langalph_map langalphMap.json

  # 指定输出文件
  json2csv.py --output result.csv data.json

  # 使用自定义规范
  json2csv.py --custom-specs my_specs.json data.json

  # 创建示例规范文件
  json2csv.py --create-example-specs example_specs.json

  # 列出所有预设
  json2csv.py --list-presets
        """
    )
    
    parser.add_argument('input_file', nargs='?', 
                       help='输入的JSON文件')
    
    parser.add_argument('-o', '--output', 
                       help='输出CSV文件路径（默认为输入文件名.csv）')
    
    parser.add_argument('-p', '--preset', 
                       choices=list(PRESET_SPECS.keys()),
                       default='default',
                       help='使用预设规范 (默认: default)')
    
    parser.add_argument('-c', '--custom-specs',
                       help='自定义规范JSON文件路径')
    
    parser.add_argument('--create-example-specs',
                       help='创建示例规范文件')
    
    parser.add_argument('--list-presets', action='store_true',
                       help='列出所有预设规范')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 处理特殊命令
    if args.list_presets:
        list_presets()
        return
    
    if args.create_example_specs:
        create_example_spec_file(args.create_example_specs)
        return
    
    # 检查必需参数
    if not args.input_file:
        print("错误：必须指定输入文件")
        parser.print_help()
        sys.exit(1)
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误：输入文件不存在: {args.input_file}")
        sys.exit(1)
    
    # 确定输出文件
    if args.output:
        output_file = args.output
    else:
        output_file = input_path.with_suffix('.csv')
    
    # 确定使用的规范
    if args.custom_specs:
        if args.verbose:
            print(f"加载自定义规范: {args.custom_specs}")
        field_specs = load_custom_specs(args.custom_specs)
    else:
        if args.verbose:
            print(f"使用预设规范: {args.preset}")
        field_specs = PRESET_SPECS[args.preset]
    
    # 执行转换
    if args.verbose:
        print(f"输入文件: {args.input_file}")
        print(f"输出文件: {output_file}")
        print(f"字段规范数量: {len(field_specs)}")
    
    try:
        converter = StructuredConverter(field_specs)
        converter.convert_json_to_csv(str(input_path), str(output_file))
        
        if args.verbose:
            print("转换完成!")
        
    except Exception as e:
        print(f"转换失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
从path_collection.json生成缺失文件的路径列表
用于重定向检查
"""

import json
import sys

def main():
    # 支持命令行参数指定输入文件
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'paths_raw.json'
    
    # 读取路径集合
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            paths = json.load(f)
    except FileNotFoundError:
        print(f"错误: {input_file} 不存在", file=sys.stderr)
        sys.exit(1)
    
    # 提取file_exists为false的绝对路径
    missing_paths = []
    for item in paths:
        if not item.get('file_exists', True):  # 默认为True以防字段缺失
            abs_path = item.get('absolute_url_path')
            if abs_path:
                missing_paths.append(abs_path)
    
    # 去重并排序
    unique_missing = sorted(set(missing_paths))
    
    # 输出到标准输出
    for path in unique_missing:
        print(path)
    
    # 输出统计信息到stderr
    print(f"# 总共找到 {len(unique_missing)} 个缺失文件路径", file=sys.stderr)

if __name__ == "__main__":
    main()

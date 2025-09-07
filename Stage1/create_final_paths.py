#!/usr/bin/env python3
"""
创建最终路径集合
完成：字段清理 + 重复合并（基于sources字段合并）
"""

import json
import sys
from pathlib import Path

def create_final_paths(input_file='paths_raw.json', corrections_file=None, output_file='paths_final.json'):
    """处理路径字段清理和sources合并"""
    
    # 读取原始路径集合
    with open(input_file, 'r', encoding='utf-8') as f:
        paths = json.load(f)
    
    print(f"原始条目数: {len(paths)}")
    
    # 读取路径修正规则（如果有）
    path_corrections = {}
    if corrections_file and Path(corrections_file).exists():
        with open(corrections_file, 'r', encoding='utf-8') as f:
            path_corrections = json.load(f)
        print(f"加载路径修正规则: {len(path_corrections)} 个")
    
    final_paths = {}  # 使用字典直接去重
    corrections_applied = 0
    
    for path_entry in paths:
        # 第1步：获取原始绝对路径
        original_abs_path = path_entry['absolute_url_path']
        
        # 第2步：应用路径修正（如果有）
        corrected_abs_path = path_corrections.get(original_abs_path, original_abs_path)
        if corrected_abs_path != original_abs_path:
            corrections_applied += 1
        
        # 第3步：构建最终条目（只保留必要字段，移除file_exists）
        fragment = path_entry.get('fragment')
        unique_key = f"{corrected_abs_path}#{fragment or ''}"
        
        final_entry = {
            'absolute_url_path': corrected_abs_path,
            'base_path': corrected_abs_path.split('#')[0],
            'fragment': fragment,
            'sources': path_entry['sources'].copy()
        }
        
        # 第4步：合并重复条目
        if unique_key in final_paths:
            # 合并sources，避免重复
            existing_sources = final_paths[unique_key]['sources']
            for source in final_entry['sources']:
                if source not in existing_sources:
                    existing_sources.append(source)
        else:
            final_paths[unique_key] = final_entry
    
    # 转换为列表并排序
    result = list(final_paths.values())
    result.sort(key=lambda x: x['absolute_url_path'])
    
    # 保存最终结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"最终条目数: {len(result)}")
    print(f"应用修正: {corrections_applied} 个")
    print(f"结果已保存到: {output_file}")
    
    return result

def main():
    """主函数"""
    corrections_file = sys.argv[1] if len(sys.argv) > 1 else None
    create_final_paths(corrections_file=corrections_file)

if __name__ == "__main__":
    main()

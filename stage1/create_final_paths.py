#!/usr/bin/env python3
"""
创建最终路径集合
一次性完成：路径修正 + 重定向应用 + 字段清理 + 重复合并
"""

import json
import sys

def create_final_paths(input_file='paths_raw.json', redirects_file='redirects.csv', output_file='paths_final.json'):
    """一次性处理所有路径标准化任务"""
    
    # 读取原始路径集合
    with open(input_file, 'r', encoding='utf-8') as f:
        paths = json.load(f)
    
    print(f"原始条目数: {len(paths)}")
    
    # 读取重定向信息（如果存在）
    redirects = {}
    try:
        import csv
        with open(redirects_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row['source_path'].strip()
                target = row['target_path'].strip()
                if target and target != source:
                    redirects[source] = target
        print(f"加载重定向规则: {len(redirects)} 个")
    except FileNotFoundError:
        print("未找到重定向文件，跳过重定向处理")
    
    # 绝对路径修正规则（来自勘误表）
    path_corrections = {
        '/writing/mbugu.php': '/writing/mbugu.htm',
        '/writing/belanadaviri.htm': '/writing/belandaviri.htm'
    }
    
    final_paths = {}  # 使用字典直接去重
    corrections_applied = 0
    redirects_applied = 0
    
    for path_entry in paths:
        # 第1步：获取原始绝对路径
        original_abs_path = path_entry['absolute_url_path']
        
        # 第2步：应用路径修正
        corrected_abs_path = path_corrections.get(original_abs_path, original_abs_path)
        if corrected_abs_path != original_abs_path:
            corrections_applied += 1
        
        # 第3步：应用重定向（如果有）
        final_abs_path = redirects.get(corrected_abs_path, corrected_abs_path)
        if final_abs_path != corrected_abs_path:
            redirects_applied += 1
        
        # 第4步：构建最终条目（只保留必要字段）
        fragment = path_entry.get('fragment')
        unique_key = f"{final_abs_path}#{fragment or ''}"
        
        final_entry = {
            'absolute_url_path': final_abs_path,
            'base_path': final_abs_path.split('#')[0],
            'fragment': fragment,
            'sources': path_entry['sources'].copy()
        }
        
        # 第5步：合并重复条目
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
    
    return result

def main():
    """主函数"""
    redirects_file = sys.argv[1] if len(sys.argv) > 1 else 'redirects.csv'
    create_final_paths(redirects_file=redirects_file)

if __name__ == "__main__":
    main()

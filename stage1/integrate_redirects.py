#!/usr/bin/env python3
"""
将重定向检查结果集成到路径集合中
生成带有redirect_target字段的新版本路径集合
"""

import json
import re
from pathlib import Path

def parse_redirect_results(redirect_file):
    """解析重定向检查结果"""
    redirects = {}
    
    with open(redirect_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # 解析格式: /path/source.htm -> /path/target.htm (status)
            match = re.match(r'^(.+?) -> (.+?) \((\d+)\)$', line)
            if match:
                source_path = match.group(1)
                target_path = match.group(2)
                status_code = int(match.group(3))
                
                redirects[source_path] = {
                    'target_path': target_path,
                    'status_code': status_code,
                    'is_redirect': source_path != target_path,
                    'is_available': status_code == 200
                }
            else:
                print(f"警告: 无法解析行: {line}")
    
    return redirects

def integrate_redirect_info(path_collection_file, redirect_results, output_file):
    """将重定向信息集成到路径集合中"""
    
    # 加载路径集合
    with open(path_collection_file, 'r', encoding='utf-8') as f:
        path_data = json.load(f)
    
    # 统计信息
    stats = {
        'total_paths': len(path_data),
        'checked_paths': 0,
        'redirected_paths': 0,
        'unavailable_paths': 0,
        'updated_file_exists': 0
    }
    
    # 为每个路径条目添加重定向信息
    for item in path_data:
        absolute_path = item['absolute_url_path']
        
        # 查找重定向信息
        if absolute_path in redirect_results:
            redirect_info = redirect_results[absolute_path]
            stats['checked_paths'] += 1
            
            # 添加重定向字段
            item['redirect_checked'] = True
            item['redirect_target'] = redirect_info['target_path'] if redirect_info['is_redirect'] else None
            item['redirect_status'] = redirect_info['status_code']
            item['is_redirect'] = redirect_info['is_redirect']
            
            # 统计重定向
            if redirect_info['is_redirect']:
                stats['redirected_paths'] += 1
                print(f"重定向: {absolute_path} -> {redirect_info['target_path']}")
            
            # 更新file_exists状态（基于重定向检查结果）
            if item['file_exists'] != redirect_info['is_available']:
                item['file_exists'] = redirect_info['is_available']
                stats['updated_file_exists'] += 1
                if not redirect_info['is_available']:
                    stats['unavailable_paths'] += 1
            
        else:
            # 未检查的路径
            item['redirect_checked'] = False
            item['redirect_target'] = None
            item['redirect_status'] = None
            item['is_redirect'] = False
    
    # 保存集成后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(path_data, f, ensure_ascii=False, indent=2)
    
    return stats

def main():
    print("=== 重定向信息集成 ===\n")
    
    # 文件路径
    redirect_file = "redirects_check.txt"
    input_file = "path_collection.json"
    output_file = "path_collection_with_redirects.json"
    
    # 检查输入文件
    if not Path(redirect_file).exists():
        print(f"错误: 重定向结果文件不存在: {redirect_file}")
        return
    
    if not Path(input_file).exists():
        print(f"错误: 路径集合文件不存在: {input_file}")
        return
    
    # 解析重定向结果
    print("解析重定向检查结果...")
    redirect_results = parse_redirect_results(redirect_file)
    print(f"解析到 {len(redirect_results)} 个重定向检查结果")
    
    # 分析重定向情况
    redirected = sum(1 for r in redirect_results.values() if r['is_redirect'])
    unavailable = sum(1 for r in redirect_results.values() if not r['is_available'])
    
    print(f"其中实际重定向: {redirected}")
    print(f"不可访问: {unavailable}")
    print()
    
    # 集成到路径集合
    print("集成重定向信息到路径集合...")
    stats = integrate_redirect_info(input_file, redirect_results, output_file)
    
    # 输出统计信息
    print(f"\n=== 集成统计 ===")
    print(f"总路径数: {stats['total_paths']}")
    print(f"已检查路径: {stats['checked_paths']}")
    print(f"重定向路径: {stats['redirected_paths']}")
    print(f"不可访问路径: {stats['unavailable_paths']}")
    print(f"更新file_exists状态: {stats['updated_file_exists']}")
    
    print(f"\n结果已保存到: {output_file}")
    
    # 生成重定向映射报告
    redirect_mapping_file = "redirect_mappings.json"
    with open(redirect_mapping_file, 'w', encoding='utf-8') as f:
        redirect_mappings = {k: v for k, v in redirect_results.items() if v['is_redirect']}
        json.dump(redirect_mappings, f, ensure_ascii=False, indent=2)
    
    print(f"重定向映射已保存到: {redirect_mapping_file}")

if __name__ == "__main__":
    main()

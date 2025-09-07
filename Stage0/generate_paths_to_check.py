#!/usr/bin/env python3
"""
Stage0 重定向检查脚本 - 路径收集器
收集所有需要检查重定向的路径，输出为文本文件供外部工具使用
"""

import csv
import json
from pathlib import Path
from urllib.parse import urljoin
from typing import List

class PathCollector:
    def __init__(self):
        pass
    
    def normalize_to_absolute_path(self, path: str, base_path: str = "/writing/") -> str:
        """将路径标准化为绝对路径"""
        # 移除fragment
        clean_path = path.split('#')[0]
        
        # 如果移除fragment后为空，说明原路径是纯fragment，应该跳过
        if not clean_path:
            return None
        
        # 使用标准URL解析处理相对路径
        absolute_url = urljoin(base_path, clean_path)
        
        return absolute_url
    
    def collect_all_paths(self) -> List[str]:
        """收集所有需要检查的路径"""
        paths = set()
        
        # 从各个CSV文件收集路径
        csv_files = [
            ('language.csv', 0),  # href列在第0列
            ('writing.csv', 0),
            ('langalphSingle.csv', 0)
        ]
        
        for csv_file, href_col in csv_files:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > href_col and row[href_col]:
                        abs_path = self.normalize_to_absolute_path(row[href_col])
                        if abs_path:  # 跳过None（纯fragment路径）
                            paths.add(abs_path)
        
        # 从langalphMap.json收集路径
        with open('langalphMap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data:
                # 书写系统链接
                if 'Link' in entry and entry['Link']:
                    abs_path = self.normalize_to_absolute_path(entry['Link'])
                    if abs_path:  # 跳过None（纯fragment路径）
                        paths.add(abs_path)
                # 语言链接
                if 'Languages' in entry:
                    for lang in entry['Languages']:
                        if isinstance(lang, dict) and 'href' in lang:
                            abs_path = self.normalize_to_absolute_path(lang['href'])
                            if abs_path:  # 跳过None（纯fragment路径）
                                paths.add(abs_path)
        
        return sorted(list(paths))
    
    def collect_charts_paths(self) -> List[str]:
        """收集charts路径（用于单独处理）"""
        paths = set()
        
        with open('charts.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 0 and row[0]:
                    abs_path = self.normalize_to_absolute_path(row[0], "/charts/")
                    if abs_path:  # 跳过None（纯fragment路径）
                        paths.add(abs_path)
        
        return sorted(list(paths))
    
    def save_paths_to_file(self, output_file="paths_to_check.txt"):
        """将收集的路径保存到文件"""
        paths = self.collect_all_paths()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for path in paths:
                f.write(f"{path}\n")
        
        print(f"收集到 {len(paths)} 个唯一路径，已保存到: {output_file}")
        return len(paths)
    
    def save_charts_paths_to_file(self, output_file="charts_paths_to_check.txt"):
        """将charts路径保存到文件"""
        paths = self.collect_charts_paths()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for path in paths:
                f.write(f"{path}\n")
        
        print(f"收集到 {len(paths)} 个charts路径，已保存到: {output_file}")
        return len(paths)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="收集需要重定向检查的路径")
    parser.add_argument('--output', help='输出文件名')
    parser.add_argument('--charts', action='store_true', help='收集charts路径而非常规路径')
    parser.add_argument('--dry-run', action='store_true', help='仅显示路径，不保存文件')
    
    args = parser.parse_args()
    
    collector = PathCollector()
    
    if args.charts:
        if args.dry_run:
            paths = collector.collect_charts_paths()
            print(f"收集到 {len(paths)} 个charts路径:")
            for path in paths[:10]:  # 显示前10个作为示例
                print(f"  {path}")
            if len(paths) > 10:
                print(f"  ... 还有 {len(paths) - 10} 个路径")
        else:
            output_file = args.output or "charts_paths_to_check.txt"
            collector.save_charts_paths_to_file(output_file)
    else:
        if args.dry_run:
            paths = collector.collect_all_paths()
            print(f"收集到 {len(paths)} 个唯一路径:")
            for path in paths[:10]:  # 显示前10个作为示例
                print(f"  {path}")
            if len(paths) > 10:
                print(f"  ... 还有 {len(paths) - 10} 个路径")
        else:
            output_file = args.output or "paths_to_check.txt"
            collector.save_paths_to_file(output_file)

if __name__ == "__main__":
    main()

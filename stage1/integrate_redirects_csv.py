#!/usr/bin/env python3
"""
从CSV重定向结果集成到路径集合
"""

import json
import csv

def main():
    # 读取重定向CSV（格式：source_path,target_path,status_code）
    # 只使用前两个字段，忽略status_code
    redirects = {}
    with open('redirects.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row['source_path'].strip()
            target = row['target_path'].strip()
            
            # 跳过空行
            if not source:
                continue
            
            # 只有当目标路径不同时才记录重定向
            if target and target != source:
                redirects[source] = target
    
    # 读取路径集合
    with open('paths_raw.json', 'r') as f:
        paths = json.load(f)
    
    # 集成重定向信息
    updated = 0
    for item in paths:
        abs_path = item['absolute_url_path']
        item['redirect_target'] = redirects.get(abs_path, None)
        if abs_path in redirects:
            updated += 1
    
    # 保存结果
    with open('paths_with_redirects.json', 'w') as f:
        json.dump(paths, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

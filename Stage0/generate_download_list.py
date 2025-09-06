#!/usr/bin/env python3
"""
从解析后的CSV/JSON文件生成aria2c兼容的下载列表
处理去重、fragment移除和路径绝对化
"""

import csv
import json
import os
from urllib.parse import urlparse, urljoin
from pathlib import Path

def remove_fragment(url):
    """移除URL中的fragment部分（#后面的内容）"""
    if '#' in url:
        return url.split('#')[0]
    return url

def normalize_path(link, base_path="/writing/"):
    """
    使用urllib.parse正确处理URL路径
    - 移除fragment
    - 将相对路径转换为绝对路径
    """
    # 先移除fragment
    link = remove_fragment(link)
    
    # 使用urljoin正确处理相对路径和绝对路径
    # base_path作为基准URL，link作为相对URL
    normalized = urljoin(base_path, link)
    
    # 确保返回的是路径部分（去掉可能的scheme等）
    parsed = urlparse(normalized)
    return parsed.path

def collect_links_from_csv(csv_file, base_path):
    """从CSV文件收集链接"""
    links = set()
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 1:
                    link = normalize_path(row[0], base_path)
                    links.add(link)
    return links

def collect_all_links():
    """从所有源文件收集链接"""
    all_links = set()
    
    # 定义所有要处理的文件
    sources = [
        ('language.csv', '/writing/', '语言页面'),
        ('writing.csv', '/writing/', '书写系统页面'),
        ('charts.csv', '/charts/', '表格文件')
    ]
    
    # 统一处理CSV文件
    for csv_file, base_path, description in sources:
        print(f"收集{description}链接...")
        links = collect_links_from_csv(csv_file, base_path)
        all_links.update(links)
        category_count = len([l for l in all_links if l.startswith(base_path)])
        print(f"{description}: {category_count} 个{'（累计）' if len(all_links) > len(links) else ''}")
    
    # 从langalphMap.json收集语言页面链接
    print("收集langalphMap中的语言页面链接...")
    if os.path.exists('langalphMap.json'):
        with open('langalphMap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for mapping in data:
                # 书写系统链接
                if 'writing' in mapping and 'Link' in mapping['writing']:
                    link = normalize_path(mapping['writing']['Link'], "/writing/")
                    all_links.add(link)
                
                # 语言链接
                if 'language' in mapping:
                    for lang_entry in mapping['language']:
                        if len(lang_entry) >= 1:
                            link = normalize_path(lang_entry[0], "/writing/")
                            all_links.add(link)
        print(f"所有页面: {len([l for l in all_links if l.startswith('/writing/')])} 个（累计）")
    
    return sorted(all_links)

def generate_aria2c_list(links, output_file):
    """生成aria2c兼容的下载列表"""
    base_url = "https://www.omniglot.com"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Stage0 详细页面下载列表 - aria2c兼容格式\n")
        f.write("# 使用方法: aria2c -i stage0_detailed_download_list.txt -j 5 --retry-wait=2\n")
        f.write("# 已去重并移除fragment\n\n")
        
        # 分类输出
        writing_links = [l for l in links if l.startswith('/writing/')]
        chart_links = [l for l in links if l.startswith('/charts/')]
        other_links = [l for l in links if not l.startswith('/writing/') and not l.startswith('/charts/')]
        
        if writing_links:
            f.write("# 语言和书写系统页面 (/writing/)\n")
            for link in writing_links:
                full_url = base_url + link
                # 输出文件名为URL的最后部分
                filename = link.split('/')[-1]
                f.write(f"{full_url}\n")
                f.write(f"  dir=writing\n")
                f.write(f"  out={filename}\n\n")
        
        if other_links:
            f.write("# 其他页面 (非/writing/和/charts/)\n")
            for link in other_links:
                full_url = base_url + link
                # 输出文件名为URL的最后部分，保持目录结构
                filename = link.split('/')[-1]
                # 使用相对路径作为输出目录
                dir_path = '/'.join(link.split('/')[1:-1])  # 去掉开头的/和最后的文件名
                f.write(f"{full_url}\n")
                if dir_path:
                    f.write(f"  dir={dir_path}\n")
                f.write(f"  out={filename}\n\n")
        
        if chart_links:
            f.write("# 表格文件 (/charts/)\n")
            for link in chart_links:
                full_url = base_url + link
                # 输出文件名为URL的最后部分
                filename = link.split('/')[-1]
                f.write(f"{full_url}\n")
                f.write(f"  dir=charts\n")
                f.write(f"  out={filename}\n\n")
    
    return len(writing_links), len(chart_links), len(other_links)

def main():
    print("开始生成下载列表...")
    
    # 收集所有链接
    all_links = collect_all_links()
    
    print(f"\n去重后总计: {len(all_links)} 个唯一链接")
    
    # 统计分类
    writing_count = len([l for l in all_links if l.startswith('/writing/')])
    chart_count = len([l for l in all_links if l.startswith('/charts/')])
    other_count = len([l for l in all_links if not l.startswith('/writing/') and not l.startswith('/charts/')])
    
    print(f"- /writing/ 页面: {writing_count} 个")
    print(f"- /charts/ 文件: {chart_count} 个")
    print(f"- 其他路径: {other_count} 个")
    
    # 生成aria2c下载列表
    output_file = "stage0_detailed_download_list.txt"
    writing_out, chart_out, other_out = generate_aria2c_list(all_links, output_file)
    
    print(f"\n下载列表已生成: {output_file}")
    print(f"- 语言/书写系统页面: {writing_out} 个")
    print(f"- 表格文件: {chart_out} 个")
    print(f"- 其他页面: {other_out} 个")
    
    # 显示一些示例fragment移除的情况
    fragments_removed = []
    if os.path.exists('writing.csv'):
        with open('writing.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 1 and '#' in row[0]:
                    original = row[0]
                    cleaned = remove_fragment(original)
                    fragments_removed.append((original, cleaned))
    
    if fragments_removed:
        print(f"\n示例fragment移除 ({len(fragments_removed)}个):")
        for original, cleaned in fragments_removed[:5]:
            print(f"  {original} → {cleaned}")
        if len(fragments_removed) > 5:
            print(f"  ... 还有 {len(fragments_removed) - 5} 个")

if __name__ == "__main__":
    main()

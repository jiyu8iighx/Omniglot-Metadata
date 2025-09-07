#!/usr/bin/env python3
"""
解析langalph.htm页面，提取书写系统与语言的对应关系
"""

import os
import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup
import argparse

def parse_langalph_page(html_file):
    """
    解析langalph.htm页面
    
    参数:
        html_file: HTML文件路径
    """
    print(f"解析文件: {html_file}")
    
    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找所有p元素
    p_elements = soup.find_all('p')
    print(f"找到 {len(p_elements)} 个p元素")
    
    # 筛选包含多个a标签的p元素
    target_p_elements = []
    
    for p in p_elements:
        a_elements = p.find_all('a')
        if len(a_elements) >= 5:
            # 检查p元素的内容是否主要由a标签和分隔符组成
            text_content = p.get_text().strip()
            # 简单的启发式检查：如果a标签数量足够多，可能是目标元素
            target_p_elements.append((p, len(a_elements)))
            print(f"找到候选p元素，包含 {len(a_elements)} 个a标签")
    
    print(f"找到 {len(target_p_elements)} 个候选p元素")
    
    # 断言: 根据指示，理应有两个符合条件的p元素
    if len(target_p_elements) < 2:
        print(f"错误: 只找到{len(target_p_elements)}个候选p元素，预期至少2个")
        return
    
    # 提取前两个最有可能的p元素中的链接
    single_language_links = []
    multi_language_links = []
    
    if len(target_p_elements) >= 2:
        # 按HTML中的原始顺序处理（不排序）
        
        for i, (p, count) in enumerate(target_p_elements[:2]):
            print(f"处理第 {i+1} 个p元素（{count}个a标签）")
            
            links = []
            a_elements = p.find_all('a')
            
            for a in a_elements:
                href = a.get('href')
                if href:
                    try:
                        link_text = a.string if a.string else a.get_text()
                        link_text = link_text.strip()
                        links.append((href, link_text))
                    except Exception as e:
                        print(f"处理链接时出错: {href}, 错误: {str(e)}")
            
            if i == 0:
                # 第一个p元素（按HTML顺序）
                multi_language_links = links
                print(f"第一个p元素（多语言书写系统）: {len(links)} 个链接")
            else:
                # 第二个p元素（按HTML顺序）
                single_language_links = links
                print(f"第二个p元素（单语言书写系统）: {len(links)} 个链接")
    
    # 保存单语言书写系统链接
    if single_language_links:
        with open('langalphSingle.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for href, text in single_language_links:
                writer.writerow([href, text])
        print(f"单语言书写系统链接已保存到 langalphSingle.csv ({len(single_language_links)} 个)")
    
    # 查找table元素（用于langalphMap）
    table_elements = soup.find_all('table')
    print(f"找到 {len(table_elements)} 个table元素")
    
    if table_elements:
        # 找到最大的table（可能包含最详细的数据）
        largest_table = max(table_elements, key=lambda t: len(t.find_all(['tr', 'td'])))
        row_count = len(largest_table.find_all('tr'))
        cell_count = len(largest_table.find_all('td'))
        print(f"最大的table包含 {row_count} 行，{cell_count} 个单元格")
        print("table元素已找到，等待后续解析指令")
    
    return {
        'single_language_count': len(single_language_links),
        'multi_language_count': len(multi_language_links),
        'table_found': len(table_elements) > 0,
        'table_size': len(largest_table.find_all(['tr', 'td'])) if table_elements else 0
    }

def main():
    parser = argparse.ArgumentParser(description='解析langalph.htm页面')
    parser.add_argument('--input', default='langalph.htm', help='输入HTML文件路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误: 文件 {args.input} 不存在")
        return
    
    result = parse_langalph_page(args.input)
    
    print("\n解析结果:")
    print(f"- 单语言书写系统: {result['single_language_count']} 个")
    print(f"- 多语言书写系统: {result['multi_language_count']} 个")
    print(f"- 找到table元素: {'是' if result['table_found'] else '否'}")
    if result['table_found']:
        print(f"- table大小: {result['table_size']} 个元素")

if __name__ == "__main__":
    main()

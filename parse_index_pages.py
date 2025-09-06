#!/usr/bin/env python3
"""
解析Omniglot索引页面，提取链接和标签
目前支持languages.htm和index.htm页面
"""

import os
import csv
from pathlib import Path
from bs4 import BeautifulSoup
import argparse

def parse_index_page(html_file, output_csv):
    """
    解析languages.htm和index.htm页面，提取链接和标签
    
    参数:
        html_file: HTML文件路径
        output_csv: 输出CSV文件路径
    """
    print(f"解析文件: {html_file}")
    
    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到第一个ol元素
    ol_element = soup.find('ol')
    if not ol_element:
        print(f"错误: 在{html_file}中未找到ol元素")
        return
    
    # 提取所有li元素
    links = []
    errors = []
    
    # 检查是否有子元素需要先处理
    target_elements = [ol_element]
    child_elements = ol_element.find_all(['ol'], recursive=False)
    if child_elements:
        # 如果有子ol元素，将它们添加到目标元素列表
        target_elements = child_elements
    
    # 从所有目标元素中提取链接
    for element in target_elements:
        li_elements = element.find_all('li')
        for li in li_elements:
            a_elements = li.find_all('a')
            for a in a_elements:
                href = a.get('href')
                if href:
                    # 提取链接标签
                    try:
                        link_text = str(a.string) if a.string else str(a.get_text())
                        # 清理链接文本
                        link_text = link_text.strip()
                        
                        # 提取链接目标
                        # 如果是相对路径，只保留文件名部分
                        if '/' in href:
                            href = href.split('/')[-1]
                        
                        # 添加到链接列表
                        links.append((href, link_text))
                    except Exception as e:
                        errors.append(f"处理链接时出错: {href}, 错误: {str(e)}")
    
    # 输出结果到CSV文件
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for href, text in links:
            writer.writerow([f'"{href}"', f'"{text}"'])
    
    print(f"已提取 {len(links)} 个链接，保存到 {output_csv}")
    
    # 输出错误信息
    if errors:
        print("\n发现以下错误:")
        for error in errors:
            print(f"- {error}")

def main():
    parser = argparse.ArgumentParser(description='解析Omniglot索引页面')
    parser.add_argument('--languages', action='store_true', help='解析languages.htm页面')
    parser.add_argument('--index', action='store_true', help='解析index.htm页面')
    parser.add_argument('--all', action='store_true', help='解析所有索引页面')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs('Stage0', exist_ok=True)
    
    # 设置输入和输出路径
    input_dir = 'Stage0'
    output_dir = 'Stage0'
    
    if args.all or args.languages:
        input_file = os.path.join(input_dir, 'languages.htm')
        output_file = os.path.join(output_dir, 'language.csv')
        parse_index_page(input_file, output_file)
    
    if args.all or args.index:
        input_file = os.path.join(input_dir, 'index.htm')
        output_file = os.path.join(output_dir, 'writing.csv')
        parse_index_page(input_file, output_file)
    
    if not (args.all or args.languages or args.index):
        print("请指定要解析的页面: --languages, --index, 或 --all")

if __name__ == "__main__":
    main()

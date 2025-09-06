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
    
    # 找到所有ol元素
    ol_elements = soup.find_all('ol')
    if not ol_elements:
        print(f"错误: 在{html_file}中未找到ol元素")
        return
    
    # 断言: 应该只有一个ol元素作为主要数据容器
    if len(ol_elements) != 1:
        print(f"警告: 发现{len(ol_elements)}个ol元素，预期只有1个")
    
    # 使用第一个ol元素
    ol_element = ol_elements[0]
    
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
                        # 直接获取a标签的文本内容
                        link_text = a.string if a.string else a.get_text()
                        # 清理链接文本
                        link_text = link_text.strip()
                        
                        # 添加到链接列表（保持原始href）
                        links.append((href, link_text))
                    except Exception as e:
                        errors.append(f"处理链接时出错: {href}, 错误: {str(e)}")
    
    # 输出结果到CSV文件
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for href, text in links:
            writer.writerow([href, text])
    
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
    parser.add_argument('--charts', action='store_true', help='解析charts.html页面')
    parser.add_argument('--all', action='store_true', help='解析所有索引页面')
    parser.add_argument('--input', help='指定输入文件')
    parser.add_argument('--output', help='指定输出文件')
    
    args = parser.parse_args()
    
    # 如果指定了输入输出文件，直接解析
    if args.input and args.output:
        if not os.path.exists(args.input):
            print(f"错误: 输入文件 {args.input} 不存在")
            return
        parse_index_page(args.input, args.output)
        return
    
    # 确保输出目录存在
    os.makedirs('Stage0', exist_ok=True)
    
    # 设置输入和输出路径
    # 当前已在Stage0目录下，直接使用相对路径
    
    if args.all or args.languages:
        input_file = 'languages.htm'
        output_file = 'language.csv'
        parse_index_page(input_file, output_file)
    
    if args.all or args.index:
        input_file = 'index.htm'
        output_file = 'writing.csv'
        parse_index_page(input_file, output_file)
    
    if args.all or args.charts:
        input_file = 'charts.html'
        output_file = 'charts.csv'
        parse_index_page(input_file, output_file)
    
    if not (args.all or args.languages or args.index or args.charts or (args.input and args.output)):
        print("请指定要解析的页面: --languages, --index, --charts, --all, 或使用 --input 和 --output 指定文件")

if __name__ == "__main__":
    main()

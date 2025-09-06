#!/usr/bin/env python3
"""
解析langalph.htm页面中的table元素，生成langalphMap.json
"""

import os
import json
from bs4 import BeautifulSoup

def parse_langalph_table(html_file, output_json):
    """
    解析langalph.htm中的table元素，生成书写系统与语言的映射关系
    
    参数:
        html_file: HTML文件路径
        output_json: 输出JSON文件路径
    """
    print(f"解析文件: {html_file}")
    
    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到table元素
    table = soup.find('table')
    if not table:
        print("错误: 未找到table元素")
        return
    
    print("找到table元素，开始解析...")
    
    # 获取所有tr元素
    tr_elements = table.find_all('tr')
    print(f"找到 {len(tr_elements)} 个tr元素")
    
    # 断言: 验证table包含足够的行
    if len(tr_elements) < 10:
        print(f"错误: table只包含{len(tr_elements)}行，不符合预期")
        return
    
    mapping_data = []
    errors = []
    
    for i, tr in enumerate(tr_elements):
        try:
            td_elements = tr.find_all('td')
            td_count = len(td_elements)
            
            if td_count == 2:
                # 情况2: 书写系统在左列，语言列表在右列
                result = parse_two_column_row(td_elements, i)
                if result:
                    mapping_data.append(result)
                    
            elif td_count == 1:
                # 情况1: 书写系统和语言在同一个td中
                result = parse_single_column_row(td_elements[0], i)
                if result:
                    mapping_data.append(result)
                    
            else:
                if td_count > 0:  # 忽略空行
                    # 断言: 根据指示，tr宽度应该只有1或2两种情况
                    errors.append(f"行 {i+1}: td数量{td_count}不符合预期（应为1或2）")
                    
        except Exception as e:
            errors.append(f"行 {i+1}: 解析错误 - {str(e)}")
    
    # 输出结果
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent="\t")
    
    print(f"解析完成，共生成 {len(mapping_data)} 个映射关系")
    print(f"结果已保存到 {output_json}")
    
    if errors:
        print(f"\n发现 {len(errors)} 个错误:")
        for error in errors[:10]:  # 只显示前10个错误
            print(f"- {error}")
        if len(errors) > 10:
            print(f"... 还有 {len(errors) - 10} 个错误")
    
    return len(mapping_data), len(errors)

def parse_two_column_row(td_elements, row_index):
    """
    解析两列的tr元素
    td[0]: 书写系统信息
    td[1]: 语言列表
    """
    try:
        left_td = td_elements[0]
        right_td = td_elements[1]
        
        # 提取书写系统信息
        writing_info = {}
        
        # 查找有href属性的a元素
        href_a = left_td.find('a', href=True)
        if href_a:
            writing_info['Link'] = href_a.get('href')
            # 提取标签文本
            label_text = href_a.string if href_a.string else href_a.get_text()
            writing_info['Label'] = label_text.strip()
        else:
            writing_info['Link'] = ""
            writing_info['Label'] = ""
        
        # 查找有id属性的a元素
        id_a = left_td.find('a', id=True)
        if id_a:
            writing_info['AnchorID'] = id_a.get('id')
        else:
            writing_info['AnchorID'] = ""
        
        # 提取语言列表
        language_list = []
        right_a_elements = right_td.find_all('a', href=True)
        
        for a in right_a_elements:
            href = a.get('href')
            label = a.string if a.string else a.get_text()
            if href and label:
                language_list.append([href, label.strip()])
        
        return {
            "writing": writing_info,
            "language": language_list
        }
        
    except Exception as e:
        print(f"解析两列行 {row_index+1} 时出错: {str(e)}")
        return None

def parse_single_column_row(td_element, row_index):
    """
    解析单列的tr元素
    td中包含: a(id), div(包含a href), a(语言链接), a(语言链接), ...
    """
    try:
        # 获取td中的所有直接子元素
        children = list(td_element.children)
        
        # 过滤掉纯文本节点（空白符等）
        element_children = [child for child in children if hasattr(child, 'name') and child.name]
        
        # 断言: 验证单列行的基本结构
        if len(element_children) < 3:
            print(f"警告: 单列行 {row_index+1} 元素数量不足: {len(element_children)}")
            return None
        
        # 断言: 验证第一个元素是a标签
        if element_children[0].name != 'a':
            print(f"警告: 单列行 {row_index+1} 第一个元素不是a标签: {element_children[0].name}")
            return None
        
        # 断言: 验证第二个元素是div标签
        if element_children[1].name != 'div':
            print(f"警告: 单列行 {row_index+1} 第二个元素不是div标签: {element_children[1].name}")
            return None
        
        writing_info = {}
        
        # 第一个元素应该是提供id的a元素
        first_a = element_children[0]
        if first_a.name == 'a' and first_a.get('id'):
            writing_info['AnchorID'] = first_a.get('id')
        else:
            writing_info['AnchorID'] = ""
        
        # 第二个元素应该是包含书写系统链接的div
        second_element = element_children[1]
        if second_element.name == 'div':
            div_a = second_element.find('a', href=True)
            if div_a:
                writing_info['Link'] = div_a.get('href')
                label_text = div_a.string if div_a.string else div_a.get_text()
                writing_info['Label'] = label_text.strip()
            else:
                writing_info['Link'] = ""
                writing_info['Label'] = ""
        else:
            writing_info['Link'] = ""
            writing_info['Label'] = ""
        
        # 其余元素应该是语言链接
        language_list = []
        for elem in element_children[2:]:
            if elem.name == 'a' and elem.get('href'):
                href = elem.get('href')
                label = elem.string if elem.string else elem.get_text()
                if href and label:
                    language_list.append([href, label.strip()])
        
        return {
            "writing": writing_info,
            "language": language_list
        }
        
    except Exception as e:
        print(f"解析单列行 {row_index+1} 时出错: {str(e)}")
        return None

def main():
    input_file = 'langalph.htm'
    output_file = 'langalphMap.json'
    
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        return
    
    result_count, error_count = parse_langalph_table(input_file, output_file)
    
    print(f"\n最终结果:")
    print(f"- 成功解析: {result_count} 个映射关系")
    print(f"- 解析错误: {error_count} 个")

if __name__ == "__main__":
    main()

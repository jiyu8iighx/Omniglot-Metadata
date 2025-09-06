#!/usr/bin/env python3
"""
ISO 639-3语言代码清洗工具

根据用户要求处理ISO 639-3数据：
1. 移除已弃用(Deprecated/Retired)代码条目
2. 移除不代表实际语言实体的Special代码(Scope=S, Type=S)
3. 区分语言族(Macrolanguage)与个体语言(Individual)
"""

import pandas as pd
import os
from pathlib import Path

def load_iso_data():
    """加载所有相关的ISO数据文件"""
    iso_dir = Path("ISO")
    
    # 主要代码表
    main_codes = pd.read_csv(iso_dir / "iso-639-3.tsv", sep='\t', dtype=str, na_values=[''])
    print(f"原始代码总数: {len(main_codes)}")
    
    # 已弃用代码表
    try:
        retired_codes = pd.read_csv(iso_dir / "iso-639-3_Retirements.tsv", sep='\t', dtype=str)
        retired_ids = set(retired_codes['Id'].tolist())
        print(f"已弃用代码数: {len(retired_ids)}")
    except Exception as e:
        print(f"加载已弃用代码失败: {e}")
        retired_ids = set()
    
    # 宏语言映射表
    try:
        macro_mappings = pd.read_csv(iso_dir / "iso-639-3-macrolanguages.tsv", sep='\t', dtype=str)
        print(f"宏语言映射条目数: {len(macro_mappings)}")
    except Exception as e:
        print(f"加载宏语言映射失败: {e}")
        macro_mappings = pd.DataFrame()
    
    return main_codes, retired_ids, macro_mappings

def analyze_data_categories(df):
    """分析数据分类情况"""
    print("\n=== 数据分类分析 ===")
    
    # Scope分析
    scope_counts = df['Scope'].value_counts()
    print(f"\nScope分布:")
    for scope, count in scope_counts.items():
        scope_desc = {
            'I': 'Individual(个体语言)',
            'M': 'Macrolanguage(宏语言)',
            'S': 'Special(特殊代码)'
        }.get(scope, '未知')
        print(f"  {scope}: {count} ({scope_desc})")
    
    # Language_Type分析
    type_counts = df['Language_Type'].value_counts()
    print(f"\nLanguage_Type分布:")
    for ltype, count in type_counts.items():
        type_desc = {
            'L': 'Living(现存语言)',
            'E': 'Extinct(已灭绝语言)',
            'A': 'Ancient(古代语言)',
            'H': 'Historical(历史语言)',
            'C': 'Constructed(人造语言)',
            'S': 'Special(特殊用途)'
        }.get(ltype, '未知')
        print(f"  {ltype}: {count} ({type_desc})")
    
    # 组合分析
    print(f"\nScope + Type组合:")
    combo_counts = df.groupby(['Scope', 'Language_Type']).size()
    for (scope, ltype), count in combo_counts.items():
        print(f"  {scope}+{ltype}: {count}")
    
    return scope_counts, type_counts

def identify_codes_to_remove(df, retired_ids):
    """识别需要移除的代码"""
    print("\n=== 识别需要移除的代码 ===")
    
    # 1. 已弃用代码
    retired_in_main = df[df['Id'].isin(retired_ids)]
    print(f"主表中的已弃用代码: {len(retired_in_main)}")
    if len(retired_in_main) > 0:
        print("示例:", retired_in_main[['Id', 'Ref_Name']].head().values.tolist())
    
    # 2. Special代码 (Scope=S, Type=S)
    special_codes = df[(df['Scope'] == 'S') & (df['Language_Type'] == 'S')]
    print(f"特殊代码(S+S): {len(special_codes)}")
    print("特殊代码列表:")
    for _, row in special_codes.iterrows():
        print(f"  {row['Id']}: {row['Ref_Name']}")
    
    # 总计需要移除的代码
    codes_to_remove = set(retired_ids) | set(special_codes['Id'].tolist())
    print(f"\n总计需要移除: {len(codes_to_remove)}")
    
    return codes_to_remove, special_codes

def classify_remaining_codes(df, codes_to_remove):
    """对剩余代码进行分类"""
    print("\n=== 分类剩余代码 ===")
    
    # 移除不需要的代码
    clean_df = df[~df['Id'].isin(codes_to_remove)].copy()
    print(f"清洗后代码总数: {len(clean_df)}")
    
    # 按Scope分类
    individual_langs = clean_df[clean_df['Scope'] == 'I']
    macro_langs = clean_df[clean_df['Scope'] == 'M']
    
    print(f"\n个体语言(I): {len(individual_langs)}")
    print(f"宏语言(M): {len(macro_langs)}")
    
    # 进一步按Language_Type分类个体语言
    print(f"\n个体语言按类型分布:")
    ind_type_counts = individual_langs['Language_Type'].value_counts()
    for ltype, count in ind_type_counts.items():
        type_desc = {
            'L': 'Living(现存语言)',
            'E': 'Extinct(已灭绝语言)', 
            'A': 'Ancient(古代语言)',
            'H': 'Historical(历史语言)',
            'C': 'Constructed(人造语言)'
        }.get(ltype, '未知')
        print(f"  {ltype}: {count} ({type_desc})")
    
    # 宏语言详情
    print(f"\n宏语言详情:")
    for _, row in macro_langs.iterrows():
        print(f"  {row['Id']}: {row['Ref_Name']} (Type: {row['Language_Type']})")
    
    return clean_df, individual_langs, macro_langs

def create_output_files(clean_df, individual_langs, macro_langs, special_codes):
    """创建输出文件"""
    print("\n=== 生成输出文件 ===")
    
    output_dir = Path("ISO")
    
    # 1. 完整清洗后数据
    clean_output = output_dir / "iso-639-3-cleaned.tsv"
    clean_df.to_csv(clean_output, sep='\t', index=False)
    print(f"✅ 完整清洗数据: {clean_output} ({len(clean_df)}条)")
    
    # 2. 仅个体语言
    individual_output = output_dir / "iso-639-3-individual.tsv"
    individual_langs.to_csv(individual_output, sep='\t', index=False)
    print(f"✅ 个体语言数据: {individual_output} ({len(individual_langs)}条)")
    
    # 3. 仅宏语言
    macro_output = output_dir / "iso-639-3-macrolanguage.tsv"
    macro_langs.to_csv(macro_output, sep='\t', index=False)
    print(f"✅ 宏语言数据: {macro_output} ({len(macro_langs)}条)")
    
    # 4. 创建简化版（仅ID和名称）
    simple_fields = ['Id', 'Scope', 'Language_Type', 'Ref_Name']
    
    clean_simple = clean_df[simple_fields]
    simple_output = output_dir / "iso-639-3-cleaned-simple.tsv"
    clean_simple.to_csv(simple_output, sep='\t', index=False)
    print(f"✅ 简化清洗数据: {simple_output}")
    
    # 5. 被移除代码的记录
    removed_info = []
    
    # 添加Special代码信息
    for _, row in special_codes.iterrows():
        removed_info.append({
            'Id': row['Id'],
            'Ref_Name': row['Ref_Name'],
            'Reason': 'Special code (S+S)',
            'Description': 'Not representing actual language entity'
        })
    
    if removed_info:
        removed_df = pd.DataFrame(removed_info)
        removed_output = output_dir / "iso-639-3-removed-codes.tsv" 
        removed_df.to_csv(removed_output, sep='\t', index=False)
        print(f"✅ 移除代码记录: {removed_output} ({len(removed_info)}条)")

def create_language_hierarchy_info(clean_df, macro_mappings):
    """创建语言层次关系信息"""
    print("\n=== 创建语言层次关系 ===")
    
    if macro_mappings.empty:
        print("⚠️  未找到宏语言映射数据，跳过层次关系生成")
        return
    
    # 分析宏语言和成员语言的关系
    hierarchy_info = []
    
    for _, mapping in macro_mappings.iterrows():
        macro_id = mapping['M_Id']
        individual_id = mapping['I_Id']
        status = mapping['I_Status']
        
        # 获取宏语言信息
        macro_info = clean_df[clean_df['Id'] == macro_id]
        if len(macro_info) == 0:
            continue
        macro_name = macro_info.iloc[0]['Ref_Name']
        
        # 获取个体语言信息
        ind_info = clean_df[clean_df['Id'] == individual_id]
        if len(ind_info) == 0:
            # 可能是被清理掉的代码，跳过
            continue
        ind_name = ind_info.iloc[0]['Ref_Name']
        
        hierarchy_info.append({
            'Macro_Id': macro_id,
            'Macro_Name': macro_name,
            'Individual_Id': individual_id,
            'Individual_Name': ind_name,
            'Status': status
        })
    
    if hierarchy_info:
        hierarchy_df = pd.DataFrame(hierarchy_info)
        output_file = Path("ISO") / "iso-639-3-language-hierarchy.tsv"
        hierarchy_df.to_csv(output_file, sep='\t', index=False)
        print(f"✅ 语言层次关系: {output_file} ({len(hierarchy_info)}条)")
        
        # 统计信息
        active_mappings = hierarchy_df[hierarchy_df['Status'] == 'A']
        print(f"  活跃映射: {len(active_mappings)}")
        print(f"  总映射数: {len(hierarchy_df)}")

def main():
    """主函数"""
    print("=== ISO 639-3 语言代码清洗工具 ===")
    
    # 1. 加载数据
    main_codes, retired_ids, macro_mappings = load_iso_data()
    
    # 2. 分析数据分类
    analyze_data_categories(main_codes)
    
    # 3. 识别需要移除的代码
    codes_to_remove, special_codes = identify_codes_to_remove(main_codes, retired_ids)
    
    # 4. 分类剩余代码
    clean_df, individual_langs, macro_langs = classify_remaining_codes(main_codes, codes_to_remove)
    
    # 5. 创建输出文件
    create_output_files(clean_df, individual_langs, macro_langs, special_codes)
    
    # 6. 创建语言层次关系信息
    create_language_hierarchy_info(clean_df, macro_mappings)
    
    print(f"\n=== 处理完成 ===")
    print(f"原始代码: {len(main_codes)}")
    print(f"移除代码: {len(codes_to_remove)}")
    print(f"清洗后代码: {len(clean_df)}")
    print(f"  - 个体语言: {len(individual_langs)}")
    print(f"  - 宏语言: {len(macro_langs)}")

if __name__ == "__main__":
    main()

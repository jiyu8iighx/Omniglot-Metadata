# Omniglot数据处理设计文档

## 0. Stage0: 源数据重建

### HTML结构解析方法
**标准列表页面**（languages.htm/index.htm/charts.html）：
- 结构：`<ol><li><p><a href>标签</a>, ...</p></li></ol>`
- 断言：应有唯一的ol元素
- 解析：提取所有li元素中的a标签的href和文本

**langalph.htm页面**：
- p元素：包含两个p元素（各含5+个a标签），分别对应多语言和单语言书写系统
- table元素：行宽度只能是1或2
  - 宽度2：左列书写系统，右列语言列表
  - 宽度1：`a(id), div(a href), a(语言), a(语言), ...`结构

### 数据更新状态
经Stage0重建后的数据状态（相比重建前）：
- `language.csv`: 2241个链接（+9个）
- `writing.csv`: 369个链接（相同）  
- `charts.csv`: 1991个链接（新增）
- `langalphSingle.csv`: 50个链接（相同）
- `langalphMap.json`: 51个映射关系（+1个）

### 重定向检查工具
Stage0提供重定向检查工具，用于生成供Stage1使用的重定向映射数据：

**路径收集**：
```bash
# 收集常规路径（language/writing/langalphMap）
python3 generate_paths_to_check.py > paths_to_check.txt

# 收集charts路径（使用/charts/基路径）
python3 generate_paths_to_check.py --charts > charts_paths_to_check.txt

# 查看收集的路径（不保存文件）
python3 generate_paths_to_check.py --dry-run
python3 generate_paths_to_check.py --charts --dry-run
```

**重定向检查**：
```bash
# 检查常规路径重定向
cat paths_to_check.txt | ./check_redirects.sh > redirects.csv

# 检查charts路径重定向  
cat charts_paths_to_check.txt | ./check_redirects.sh > charts_redirects.csv

# 管道组合（一步完成路径收集和检查）
python3 generate_paths_to_check.py | ./check_redirects.sh > redirects.csv
```

**输出格式**：
- CSV格式：`source_path,target_path,status_code,is_redirect,is_available`
- 支持20个并发curl任务进行高效检查
- 错误处理：连接失败标记为`CURL_ERROR`

## 1. 数据流程架构

### 数据演变过程
```
源数据(CSV/JSON) → 原始路径收集 → 路径标准化 → 最终路径集合 → 实体标准化 → ISO映射 → 输出
```

### 数据文件演变链
```
language.csv, writing.csv, langalphSingle.csv, langalphMap.json
    ↓ [path_collector.py]
paths_raw.json (原始路径，包含file_exists字段)
    ↓ [create_final_paths.py + path_corrections.json可选]
paths_final.json (字段清理，移除file_exists，sources合并)
    ↓ [entity_builder.py - 待实现]
entities.json (实体标准化)
    ↓ [iso_mapper.py - 待实现]  
entities_with_iso.json (ISO代码映射)
```

### 处理层次
1. **路径收集层**: 提取原始路径，检查文件存在性，保留完整信息
2. **路径标准化层**: 移除file_exists字段，应用可选修正，合并sources
3. **实体标准化层**: 基于路径生成实体，处理去重和分类
4. **ISO映射层**: 将实体映射到ISO 639-3/15924标准
5. **输出层**: 生成结构化数据集

## 2. 核心数据结构

### PathEntryRaw (原始路径收集 - paths_raw.json)
```python
PathEntryRaw = {
    'path': str,                    # 原始路径（相对路径）
    'base_path': str,               # 去除fragment的基础路径
    'fragment': str | None,         # HTML锚点
    'absolute_url_path': str,       # 标准化绝对路径
    'sources': List[Source],        # 来源信息
    'file_exists': bool             # 本地文件存在性
}
```

### PathEntryFinal (最终路径集合 - paths_final.json) 
```python
PathEntryFinal = {
    'absolute_url_path': str,       # 标准化路径（应用可选修正）
    'base_path': str,               # 去除fragment的基础路径
    'fragment': str | None,         # HTML锚点
    'sources': List[Source]         # 合并的来源信息（去重后）
}
```

## 3. 备忘：未来实现设计
<!-- 以下为Stage2和后续阶段的设计构想，暂未实现 -->

<details>
<summary>实体数据结构设计草案</summary>

```python
Entity = {
    'id': str,                      # 基于绝对路径的唯一标识
    'paths': List[str],             # 所有相关路径
    'labels': List[str],            # 所有显示标签
    'type_hints': List[TypeHint],   # 类型推断证据
    'fragments': List[Fragment]     # 子实体信息
}
```

</details>

<details>
<summary>类型推断策略构想</summary>

推断规则（if-else链）：
```python
if has_language_evidence and has_writing_evidence:
    return DUAL_ROLE
elif has_strong_language_evidence:
    return LANGUAGE
elif has_strong_writing_evidence:
    return WRITING_SYSTEM
elif has_weak_language_evidence:
    return LANGUAGE
else:
    return UNCERTAIN
```

证据来源分类：
- **强证据**: 直接来源分类、ISO代码匹配
- **弱证据**: 文件名模式、目录位置

</details>

## 4. 通用工具程序

### json2csv.py
- **功能**: 结构化JSON到CSV转换
- **预设**: `paths_final`, `langalph_map`, `path_collection`
- **特性**: 支持嵌套对象、列表展开
- **用法**: `python json2csv.py --preset paths_final stage1/paths_final.json`

## 5. Stage1: 路径标准化层 (已完成)

### 功能概述
- ✅ 路径收集和标准化
- ✅ Fragment处理逻辑
- ✅ 重定向检查机制
- ✅ Source组合统计分析
- ✅ 低频组合数据提取

### 路径处理逻辑

#### 路径标准化规则
使用Python标准库`urllib.parse.urljoin`进行URL解析，基础路径为`/writing/`：

```python
from urllib.parse import urljoin
absolute_url = urljoin("/writing/", base_path)
```

**处理结果**：
- **简单文件名** (`xxx.htm`) → `/writing/xxx.htm`
- **相对路径** (`../chinese/xxx.htm`) → `/chinese/xxx.htm`  
- **绝对路径** (`/writing/xxx.htm`) → `/writing/xxx.htm`
- **任意相对路径** (`../any/path.htm`) → `/any/path.htm`

#### Fragment处理
- **去重标准**: `absolute_url_path + "#" + fragment`
- **重定向检查**: 移除fragment进行HTTP请求
- **实体识别**: fragment表示页面内不同语言/书写系统

### Stage1数据处理流程

#### 当前实际流程
```bash
# 1. 收集所有路径并检查文件存在性
cd Stage1
python3 path_collector.py

# 2. 生成最终路径集合（移除file_exists，合并sources）
python3 create_final_paths.py [path_corrections.json]

# 3. 生成source组合统计
python3 source_stats.py
```

#### 数据处理说明
- **path_collector.py**: 从Stage0读取CSV/JSON，检查文件存在性，生成paths_raw.json
- **create_final_paths.py**: 移除file_exists字段，应用可选修正，合并重复条目的sources
- **source_stats.py**: 分析source角色组合，生成统计报告

### 脚本文件 (`Stage1/`)
- `path_collector.py`: 主要路径收集脚本，从Stage0读取数据，生成`paths_raw.json`
- `create_final_paths.py`: 字段清理和sources合并，生成`paths_final.json`  
- `source_stats.py`: 生成source组合统计`source_combinations.json`
- `extract_low_frequency_data.py`: 提取低频组合数据（可选）
- `summarize_low_frequency.py`: 低频组合汇总分析（可选）

### 数据文件 (`Stage1/`)
- `paths_raw.json`: 原始路径收集结果 (2535个实体，包含file_exists字段)
- `paths_final.json`: 最终标准化路径 (2535个实体，已移除file_exists字段)
- `path_analysis_report.json`: 路径分析报告
- `source_combinations.json`: source组合统计 (30种唯一组合)

### 核心成果
1. **路径标准化**: 所有相对路径转换为绝对URL路径
2. **Fragment处理**: 正确处理HTML锚点作为实体标识符  
3. **文件存在性检查**: 在Stage0已完成，Stage1移除该字段
4. **Sources合并**: 正确处理重复条目的来源信息合并
5. **Source统计**: 识别出30种不同的source组合模式

## 6. 下一阶段规划

### Stage2: 实体标准化层 (待实现)
- 🔄 实体去重和标准化
- 🔄 类型推断实现
- 🔄 ISO代码映射
- 🔄 最终数据集生成

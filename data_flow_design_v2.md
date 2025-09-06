# Omniglot数据处理设计文档

## 1. 数据流程架构

### 数据演变过程
```
源数据(CSV/JSON) → 原始路径收集 → 路径标准化 → 最终路径集合 → 实体标准化 → ISO映射 → 输出
```

### 数据文件演变链
```
language.csv, writing.csv, langalphSingle.csv, langalphMap.json
    ↓ [path_collector.py]
paths_raw.json (原始路径，包含复杂相对路径)
    ↓ [create_final_paths.py + redirects.csv]
paths_final.json (标准化绝对路径，字段清理)
    ↓ [entity_builder.py - 待实现]
entities.json (实体标准化)
    ↓ [iso_mapper.py - 待实现]  
entities_with_iso.json (ISO代码映射)
```

### 处理层次
1. **路径收集层**: 提取原始路径，保留完整信息用于调试
2. **路径标准化层**: 应用修正+重定向，输出清洁的最终路径
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
    'absolute_url_path': str,       # 最终标准化路径（应用修正+重定向）
    'base_path': str,               # 去除fragment的基础路径
    'fragment': str | None,         # HTML锚点
    'sources': List[Source]         # 合并的来源信息
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

### 重定向处理

#### 检查流程
```bash
# 1. 收集所有路径
python stage1/path_collector.py

# 2. 生成缺失文件列表
python stage1/generate_missing_paths.py > missing_paths.txt

# 3. 执行重定向检查（用户手动执行）
stage1/check_redirects_csv.sh < missing_paths.txt > redirects.csv

# 4. 集成重定向信息
python stage1/integrate_redirects_csv.py
```

#### 数据格式
- **输入**: `source_path,target_path`
- **逻辑**: 仅当target ≠ source时记录重定向
- **输出**: 所有PathEntry都有`redirect_target`字段（null或目标路径）

### 脚本文件 (`stage1/`)
- `path_collector.py`: 主要路径收集脚本，生成`paths_raw.json`
- `generate_missing_paths.py`: 提取缺失文件路径列表
- `check_redirects_csv.sh`: HTTP重定向检查脚本（用户执行）
- `integrate_redirects_csv.py`: 集成重定向信息到路径数据
- `create_final_paths.py`: 生成最终标准化路径`paths_final.json`
- `source_stats.py`: 生成source组合统计`source_combinations.json`
- `extract_low_frequency_data.py`: 提取低频组合数据
- `summarize_low_frequency.py`: 低频组合汇总分析

### 数据文件 (`stage1/`)
- `paths_raw.json`: 原始路径收集结果 (2488个实体)
- `paths_final.json`: 最终标准化路径 (2488个实体)
- `path_analysis_report.json`: 路径分析报告
- `source_combinations.json`: Source组合统计 (40种组合)
- `low_frequency_combinations.csv`: 低频组合数据表格 (56个实体)

### 核心成果
1. **路径标准化**: 所有相对路径转换为绝对URL路径
2. **Fragment处理**: 正确处理HTML锚点作为实体标识符
3. **重定向处理**: 集成HTTP重定向信息，解决文件不存在问题
4. **Source统计**: 识别出40种不同的source组合模式
5. **异常识别**: 提取56个低频组合实体供人工检视

## 6. 下一阶段规划

### Stage2: 实体标准化层 (待实现)
- 🔄 实体去重和标准化
- 🔄 类型推断实现
- 🔄 ISO代码映射
- 🔄 最终数据集生成

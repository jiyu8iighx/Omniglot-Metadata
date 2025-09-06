# Omniglot数据清洗流程设计

## 整体数据流程

### 1. 源数据层
```
原始HTML页面 + XLS/XLSX表格
├── language/ 目录：语言页面HTML
├── writing/ 目录：书写系统页面HTML  
├── chart/ 目录：原始表格文件
└── 索引页面：languages.htm, index.htm, langalph.htm, charts.html
```

### 2. 预处理层（用户已完成）
```
CSV提取 + JSON解析
├── language.csv：语言链接列表
├── writing.csv：书写系统链接列表
├── langalphSingle.csv：单语言书写系统
├── langalphMap.json：多语言书写系统映射
└── csv/ 目录：转换后的表格数据
```

### 3. 实体标准化层（已完成）
```
链接标准化 + 实体识别
├── 路径标准化：保持原始路径，仅用于实体ID生成
├── 实体去重：同一实体多个链接路径
├── 类型推断：基于if-else规则，支持双重角色
└── 冲突识别：50个双重角色实体需要进一步分析
```

### 4. ISO映射层（部分完成）
```
标准代码匹配
├── 语言 → ISO 639-3（已生成映射结果）
├── 书写系统 → ISO 15924（已生成映射结果）
├── 层次关系：主系统-变体（已识别latin.htm等错误）
└── 质量修正：需要基于新实体分类重新映射
```

### 5. 最终输出层
```
结构化数据集
├── 实体元数据：ID、标签、类型、ISO代码
├── 关联关系：语言-书写系统映射
├── 表格数据：IPA、字母表等语言学信息
└── 质量报告：未映射、冲突、错误
```

## 数据结构设计

### 第一阶段：路径收集数据结构
```python
PathEntry = {
    'path': str,                    # 完整原始路径（包含Fragment）
    'base_path': str,              # 基础路径（不含Fragment）  
    'fragment': str or None,       # Fragment部分（如果有）
    'absolute_url_path': str,      # 标准化绝对路径（用于去重）
    'sources': List[dict],         # 来源信息 [{'source': 'language.csv', 'label': 'Arabic'}]
    'file_exists': bool,           # 基础文件是否存在
    # 重定向信息（集成后添加）
    'redirect_checked': bool,      # 是否已检查重定向
    'redirect_target': str or None, # 重定向目标路径
    'redirect_status': int or None, # HTTP状态码
    'is_redirect': bool            # 是否为重定向
}
```

**重要变更**：
- **添加了`absolute_url_path`字段**：将不同格式的路径标准化为绝对路径
- **基于绝对路径+Fragment去重**：确保同一页面的不同Fragment实体保持独立
- **去重效果**：从5121个原始条目去重为2493个唯一条目（减少2628个重复）
- **Fragment实体保护**：31个Fragment条目独立保存，避免错误合并
- **来源合并**：相同路径+Fragment的来源信息自动合并到一个条目中
- **重定向信息集成**：新增重定向检查结果，发现4个重定向映射

**路径标准化逻辑**：
- `/writing/xxx.htm` → 保持不变
- `../chinese/xxx.htm` → `/chinese/xxx.htm`  
- `../language/articles/xxx.htm` → `/language/articles/xxx.htm`
- `xxx.htm` → `/writing/xxx.htm`（假设在writing目录下）

**Fragment处理逻辑**：
- **去重时**: 使用`绝对路径+Fragment`作为唯一键，确保不同Fragment实体独立
- **重定向检查时**: 移除Fragment进行HTTP请求（因为Fragment是客户端处理）
- **实体识别**: Fragment用于区分同一页面内的不同语言/书写系统变体
- **ISO映射**: Fragment实体可能对应独立ISO代码或作为主实体的变体处理

**关键修正**：
- 避免了将`elamite.htm#old`和`elamite.htm#proto`错误合并到`elamite.htm`
- 保持了31个Fragment实体的独立性，防止数据丢失

**重定向处理流程**：
1. **检查阶段**: 使用`check_redirects_csv.sh`输出简化CSV格式
   ```bash
   ./check_redirects_csv.sh < missing_paths.txt > redirects.csv
   ```
2. **集成阶段**: 使用`integrate_redirects_csv.py`解析CSV并集成到路径集合
3. **CSV格式**: `source_path,target_path`（只保留必要信息）
4. **重定向逻辑**: 仅当target_path != source_path时记录重定向目标
5. **发现重定向**: 4个路径有实际重定向，需要更新实体引用
   - `wandamen.htm` → `wamesa.htm`
   - `ojibwa.htm` → `ojibwe.htm`  
   - `sylheti.htm` → `syloti.htm`
   - `tuareg.htm` → `tayarttamajeq.htm`

### 后续阶段：实体数据结构
```python
Entity = {
    'id': str,                    # 标准化路径（不含fragment）
    'paths': List[str],           # 所有链接路径
    'labels': List[str],          # 所有显示标签
    'evidence': List[Evidence],   # 类型推断证据
    'fragments': List[Fragment],  # 子实体（如果有）
    'iso_codes': {                # ISO标准代码
        'language': str,          # ISO 639-3
        'writing_system': str     # ISO 15924
    }

}

Evidence = {
    'source': str,                # 数据源（language_csv等）
    'type': str,                  # 推断类型（language/writing_system）
    'confidence': str             # 置信度（high/medium/low）
}

Fragment = {
    'id': str,                    # 完整ID（含fragment）
    'fragment_name': str,         # 锚点名称
    'parent_entity': str,         # 父实体ID
    'labels': List[str],          # 标签
    'evidence': List[Evidence]    # 证据
}
```

### 类型推断策略（if-else规则）
```python
def infer_entity_type(evidence_list):
    # 规则1：明确的单语言书写系统
    if has_evidence(evidence_list, 'langalph_single_csv', 'single_lang_writing'):
        return 'writing_system'
    
    # 规则2：明确的多语言书写系统
    if has_evidence(evidence_list, 'langalph_map_json', 'multi_lang_writing'):
        return 'writing_system'
    
    # 规则3：纯书写系统来源
    if only_has_sources(evidence_list, ['writing_csv']):
        return 'writing_system'
    
    # 规则4：纯语言来源
    if only_has_sources(evidence_list, ['language_csv']):
        return 'language'
    
    # 规则5：内容启发式
    if contains_keywords(labels, ['script', 'alphabet', 'syllabary']):
        return 'writing_system'
    
    # 规则6：混合情况 - 标记为需要人工审查
    if has_mixed_evidence(evidence_list):
        return 'mixed'  # 需要人工审查
    
    # 默认：语言
    return 'language'
```

### 冲突处理策略
```python
def handle_type_conflicts(entity):
    evidence = entity['evidence']
    
    # 情况1：同一实体在不同上下文中确实有不同角色
    # 例如：Arabic既是语言也是书写系统
    if is_legitimate_dual_role(entity):
        return {
            'primary_type': 'language',      # 主要类型
            'secondary_type': 'writing_system', # 次要类型
            'context': 'dual_role'
        }
    
    # 情况2：数据源不一致
    if has_source_conflicts(evidence):
        return {
            'primary_type': 'unknown',
            'context': 'source_conflict',
            'requires_review': True
        }
    
    # 情况3：Fragment子类型
    if is_fragment_variant(entity):
        return {
            'primary_type': infer_from_parent(entity),
            'context': 'fragment_variant'
        }
```

## 实现程序概述

### 1. 链接标准化器 (LinkNormalizer)
```python
class LinkNormalizer:
    def normalize_paths(self):      # PHP→HTM，路径清理
    def extract_fragments(self):    # 锚点提取
    def deduplicate_entities(self): # 实体去重
    def collect_evidence(self):     # 证据收集
```

### 2. 类型推断器 (TypeInferencer)  
```python
class TypeInferencer:
    def apply_rules(self):          # 应用if-else规则
    def detect_conflicts(self):     # 冲突检测
    def handle_dual_roles(self):    # 双重角色处理
```

### 3. ISO映射器 (ISOMapper)
```python
class ISOMapper:
    def match_languages(self):      # 语言→ISO 639-3
    def match_writing_systems(self): # 书写系统→ISO 15924
    def resolve_hierarchies(self):  # 层次关系处理
    def validate_mappings(self):    # 映射验证
```

### 4. 质量控制器 (QualityController)
```python
class QualityController:
    def detect_errors(self):        # 错误检测
    def generate_reports(self):     # 质量报告
    def create_patches(self):       # 补丁生成
```

## 关键设计原则

1. **保持原始数据不变**：所有处理都是增量的，不覆盖原始文件
2. **证据驱动**：每个推断都有明确的证据来源
3. **规则明确**：使用if-else而非模糊的权重
4. **支持双重角色**：同一实体可以既是语言也是书写系统
5. **人工审查标记**：无法自动处理的标记为需要审查
6. **补丁式修正**：错误修正通过补丁文件实现

## JSON到CSV转换工具

### 命令行工具：json2csv.py

为了支持灵活的数据结构设计和表格化输出，我们实现了一个结构化的JSON到CSV转换工具。

#### 基本用法
```bash
# 使用默认规范（所有列表都展开）
python json2csv.py data.json

# 使用预设规范
python json2csv.py --preset langalph_map langalphMap.json

# 指定输出文件
python json2csv.py --output result.csv data.json

# 详细输出模式
python json2csv.py -v --preset path_collection path_collection.json
```

#### 预设规范
- `default` - 默认规范（所有列表都展开）
- `path_collection` - 适用于path_collection.json
- `langalph_map` - 适用于langalphMap.json  
- `example_tuple` - 演示tuple类型处理

#### 自定义规范设计

当设计新的数据结构时，可以通过JSON规范文件声明字段的表格化方法：

```bash
# 创建示例规范文件
python json2csv.py --create-example-specs my_specs.json
```

**规范文件格式**：
```json
{
  "sources": {
    "list_type": "expand",
    "description": "展开sources数组，每个元素一行"
  },
  "coordinates": {
    "list_type": "tuple",
    "tuple_length": 2,
    "separator": ", ",
    "description": "坐标[lat,lng]处理为单个字符串"
  },
  "metadata.tags": {
    "list_type": "tuple",
    "separator": " | ",
    "description": "标签数组连接为单个字符串"
  },
  "items": {
    "list_type": "indexed_dict",
    "description": "用索引作为键展开：items.0.field, items.1.field"
  }
}
```

**字段类型说明**：
- `expand`: 列表展开，每个元素生成一行（适用于一对多关系）
- `tuple`: 列表连接为单个字符串（适用于固定长度数组）
- `indexed_dict`: 用索引展开为多列（适用于结构化列表）

**使用自定义规范**：
```bash
python json2csv.py --custom-specs my_specs.json data.json
```

#### 工具功能
```bash
# 列出所有预设规范
python json2csv.py --list-presets

# 查看帮助
python json2csv.py --help
```

### 数据结构设计指导

在设计新的数据结构时，考虑以下表格化策略：

1. **一对多关系**：使用`expand`类型，生成多行记录
2. **坐标/元组数据**：使用`tuple`类型，合并为单个字段
3. **嵌套对象数组**：使用`indexed_dict`类型，展开为多列
4. **标签/分类列表**：使用`tuple`类型，用分隔符连接

## 当前状态和下一步

### 已完成
- ✅ 基础链接标准化（保持原始路径）
- ✅ 实体去重和标识（2,443个实体）
- ✅ 类型推断：if-else规则，支持双重角色
- ✅ 初步ISO映射（需要基于新分类重新映射）
- ✅ 结构化JSON到CSV转换工具（支持复杂数据结构表格化）

### 当前状态
- **实体统计**：2,443个实体（2,116语言，327书写系统）
- **双重角色**：50个实体需要进一步分析
- **映射错误**：已识别latin.htm等层次关系错误
- **数据质量**：高置信度169个，中等置信度2,224个，低置信度50个
- **转换工具**：支持预设和自定义规范的命令行工具

### 下一步计划
1. 重新设计整体架构
2. 基于新实体分类重新进行ISO映射
3. 完善双重角色实体处理
4. 生成最终结构化数据集


# 实体分类文档

本目录包含根据源组合模式分类的实体JSON文件。

## 命名规则

文件名格式：`[Xw][Yl][Zml][Zmw].json`

### 标识符含义
- **`w`** = 书写系统源 (writing.csv + langalphSingle.csv)
- **`l`** = 语言源 (language.csv)
- **`ml`** = 映射语言 (langalphMap.json:language)
- **`mw`** = 映射书写系统 (langalphMap.json:writing_system)

### 数字含义
- **`1`** = single (单个)
- **`2`** = multiple (多个，≥2)
- **为0的项略去**

## 分类统计

### 无冲突 + 单一名称
- **`1l-1ml.json`** (1837个) - 标准语言：1个language.csv + 1个映射语言
- **`1l-2ml.json`** (192个) - 多书写系统语言：1个language.csv + 多个映射语言  
- **`1l.json`** (49个) - 孤立语言：仅1个language.csv
- **`1w.json`** (173个) - 纯书写系统：仅1个书写系统源
- **`1ml.json`** (21个) - 纯映射语言
- **`1mw.json`** (1个) - 纯映射书写系统

### 无冲突 + 多名称
- **`2w.json`** (42个) - 多个书写系统源（同一类型多个名称）

### 有冲突 + 单一名称
- **`1w-1l.json`** (33个) - 既是书写系统又是语言
- **`1w-1l-1ml.json`** (21个) - 书写系统 + 语言 + 映射语言
- **`1w-1mw.json`** (20个) - 书写系统源 + 映射书写系统
- **`1w-1l-1ml-1mw.json`** (16个) - 书写系统 + 语言 + 映射语言 + 映射书写系统
- **`1w-1ml.json`** (8个) - 书写系统源 + 映射语言
- **`1w-1l-2ml.json`** (6个) - 书写系统 + 语言 + 多个映射语言
- **`1w-1l-2ml-1mw.json`** (7个) - 书写系统 + 语言 + 多个映射语言 + 映射书写系统
- **`1w-1ml-1mw.json`** (4个) - 书写系统源 + 映射语言 + 映射书写系统

### 有冲突 + 多名称
- **`2w-1l.json`** (36个) - 多个书写系统名称 + 语言名称
- **`2w-1l-1ml.json`** (17个) - 多个书写系统 + 语言 + 映射语言
- **`2l-1ml.json`** (6个) - 多个语言源 + 映射语言
- **`1w-2l-1ml-1mw.json`** (2个) - 书写系统 + 多个语言源 + 映射语言 + 映射书写系统
- **`2w-1ml.json`** (2个) - 多个书写系统源 + 映射语言
- **`2w-2l.json`** (2个) - 多个书写系统 + 多个语言源
- **`2w-1l-2ml.json`** (1个) - 多个书写系统 + 语言 + 多个映射语言
- **`2w-1l-2ml-1mw.json`** (1个) - 多个书写系统 + 语言 + 多个映射语言 + 映射书写系统
- **`1w-2l.json`** (1个) - 书写系统 + 多个语言源

## 典型示例

### 标准语言 (1l-1ml)
```json
{
  "absolute_url_path": "/chinese/cantonese.htm",
  "sources": [
    {"source": "language.csv", "label": "Chinese (Cantonese)"},
    {"source": "langalphMap.json", "label": "Cantonese (honji)_using_Chinese"}
  ]
}
```

### 多书写系统语言 (1l-2ml)
```json
{
  "absolute_url_path": "/writing/aari.htm",
  "sources": [
    {"source": "language.csv", "label": "Aari"},
    {"source": "langalphMap.json", "label": "Aari_using_Ge'ez (Ethiopic)"},
    {"source": "langalphMap.json", "label": "Aari_using_Latin / Roman"}
  ]
}
```

### 纯书写系统 (1w)
```json
{
  "absolute_url_path": "/writing/linear_b.htm",
  "sources": [
    {"source": "writing.csv", "label": "Linear B"}
  ]
}
```

## 数据质量说明

### 四象限分析框架
基于两个二值属性的交叉组合：

#### 1. 无冲突 + 单一名称 - **优先处理**
- 数据质量最高，可直接进行ISO标准匹配
- 语言实体 → ISO 639-3语言代码  
- 书写系统实体 → ISO 15924书写系统代码

#### 2. 无冲突 + 多名称 - **合并同义词**
- 同一实体的多个名称变体
- 需要选择标准名称，建立同义词映射

#### 3. 有冲突 + 单一名称 - **类型消歧**
- 实体类型归属不明确
- 需要人工判断或上下文分析确定主要类型

#### 4. 有冲突 + 多名称 - **复杂处理**
- 既有类型冲突又有多名称问题
- 需要先消歧类型，再合并同义词
- 处理优先级最低，可能需要专门分析

总计分为 **24个类别**

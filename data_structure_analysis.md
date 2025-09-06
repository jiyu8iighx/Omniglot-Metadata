# Omniglot 数据结构分析文档

本文档详细记录了项目中各类数据文件的结构和格式，为后续数据清洗工作提供参考。

## 1. 基础统计数据

| 数据类型 | Omniglot数量 | ISO标准数量 | 备注 |
|---------|-------------|------------|-----|
| 语言条目 | 2,232 | 8,311 (ISO 639-3) | Omniglot覆盖约27%的ISO语言 |
| 书写系统条目 | 369 | 226 (ISO 15924) | Omniglot包含更多非标准书写系统 |
| 单语言书写系统 | 129 | - | 仅用于一种语言的书写系统 |
| 多语言书写系统 | 50 | - | 用于多种语言的书写系统 |
| 重叠页面 | 126 | - | 同时包含语言和书写系统信息 |
| 表格数据文件 | 2,828 | - | 转换后的CSV格式 |

## 2. 文件结构详解

### 2.1 language.csv
**格式**: CSV，2列，2,232行
**结构**: 
```
"链接目标","链接标签"
"aari.htm","Aari"
"abaza.htm","Abaza"
...
```
**特点**:
- 第一列：文件名（主要是.htm，也有94个.php文件）
- 第二列：语言显示名称
- 包含6个HTML Fragment链接（使用#锚点）

### 2.2 writing.csv  
**格式**: CSV，2列，369行
**结构**:
```
"链接目标","链接标签"
"achiktokbirim.htm","A-chik Tokbirim"
"adaizan.htm","Adaizan"
...
```
**特点**:
- 第一列：文件名（.htm/.php，包含12个HTML Fragment）
- 第二列：书写系统显示名称
- 与language.csv有126个重叠的链接目标

### 2.3 langalphSingle.csv
**格式**: CSV，2列，129行
**结构**:
```
"链接目标","链接标签"  
"adlam.htm","Adlam"
"afaka.htm","Afaka"
...
```
**特点**:
- 记录仅用于单一语言的书写系统
- 包含11个HTML Fragment链接
- 5个PHP文件链接

### 2.4 langalphMap.json
**格式**: JSON数组，50个对象
**结构**:
```json
[
  {
    "writing": {
      "AnchorID": "arabic",
      "Link": "arabic.htm", 
      "Label": "Arabic"
    },
    "language": [
      ["/writing/adamaua.htm", "Adamaua Fulfulde"],
      ["/writing/afrikaans.htm", "Afrikaans"],
      ...
    ]
  },
  ...
]
```
**特点**:
- 每个对象代表一个多语言书写系统
- `writing`字段：书写系统信息（AnchorID, Link, Label）
- `language`字段：使用该书写系统的语言列表
- 语言数量分布：最少0个，最多1,771个，平均46.8个
- 语言链接路径以`/writing/`开头

### 2.5 ISO标准文件详解

#### 2.5.1 iso-639-3_Name_Index.tab
**格式**: TSV，3列，8,312行（含标题）
**结构**:
```
Id	Print_Name	Inverted_Name
aaa	Ghotuo	Ghotuo
aar	Afar	Afar
aae	Arbëreshë Albanian	Albanian, Arbëreshë
...
```
**字段说明**:
- `Id`: 三字母语言代码（ISO 639-3主键）
- `Print_Name`: 标准显示名称（用于匹配Omniglot标签）
- `Inverted_Name`: 倒序名称（主要用于字典排序）

**匹配特点**:
- 某些条目包含地理或方言信息，如"Arabic, Algerian Saharan"
- 某些使用逗号分隔的倒序格式，如"Albanian, Arbëreshë"
- 需要考虑名称变体和别名匹配

#### 2.5.2 iso15924-codes.tsv  
**格式**: TSV，4列，227行（含标题）
**结构**:
```
Code	N°	English Name	Alias
Adlm	166	Adlam	Adlam
Arab	160	Arabic	Arabic
Aran	161	Arabic (Nastaliq variant)	
...
```
**字段说明**:
- `Code`: 四字母书写系统代码（ISO 15924主键）
- `N°`: 三位数字代码
- `English Name`: 英文标准名称（用于匹配Omniglot标签）
- `Alias`: 别名（可能为空，用于额外匹配）

**匹配特点**:
- 某些条目包含变体信息，如"Arabic (Nastaliq variant)"
- 别名字段提供额外的匹配可能性
- 某些历史文字可能在Omniglot中有更详细的分类

### 2.6 CSV表格数据
**格式**: CSV，2,828个文件
**命名规则**: `{语言名}.{书写系统/类型}.csv`

#### 2.6.1 文件类型分布（前20名）
| 类型标识 | 文件数量 | 说明 |
|---------|---------|------|
| Latin.csv | 100 | 拉丁字母系统 |
| Pronunciation.csv | 50 | 发音指南 |
| Alphabet.csv | 50 | 字母表 |
| Cyrillic.csv | 47 | 西里尔字母系统 |
| Devanagari.csv | 46 | 天城文字母系统 |
| Arabic.csv | 46 | 阿拉伯文字母系统 |
| Latin alphabet.csv | 45 | 拉丁字母表 |
| Numbers.csv | 40 | 数字系统 |
| No. of speakers.csv | 26 | 使用人数统计 |
| Consonants.csv | 26 | 辅音系统 |
| Vowels.csv | 24 | 元音系统 |
| Numerals.csv | 23 | 数词系统 |
| Sheet1.csv | 18 | 默认工作表 |
| Sample.csv | 17 | 文本样本 |
| Bengali.csv | 13 | 孟加拉文字母系统 |

#### 2.6.2 内容结构示例

**字母表类型**（akan.Alphabet.csv）:
```
"A a","B b","D d","E e","Ɛ ɛ","F f","G g","H h",,akan
a,be,ce,de,e,ef,ge,ha,,Akan  
[ɑ],[b],[c],[d],[ɛ],[f],[g],[h],,
```
- 第1行：字母形式
- 第2行：字母名称  
- 第3行：IPA音标
- 最后列：语言名称

**数字系统类型**（amharic.Numbers.csv）:
```
1,2,3,4,5,6,7,8,9,፲
አንዶ,ሁለት,ሶስት,አራት,አምስት,ስዶዶስት,ሰባት,ስምንት,ዘጠኝ,አስር
and,hulätt,sost,aratt,amməst,səddəst,säbatt,səmmənt,zäṭäňň,assər
```
- 包含数字符号、本地语言表示、转写等多层信息
- 通常还包含序数词、大数等扩展内容

**音系类型**（abaza.Cyrillic.csv）:
```
"А а","Б б","В в","Г г","Гв гв","Гъ гъ",,абаза бызшва
а,бы,вы,гы,гвы,гъы,,"Abaza Bızšva"  
a,b,v,g,gv,g'',,Abaza
[a],[b],[v],[ɡ],[ɡʷ],[ɣ],,
```
- 第1行：字母形式
- 第2行：音节名称
- 第3行：转写
- 第4行：IPA音标

**特点**:
- 格式高度依赖原始Excel文件的布局
- 多数包含语言名称的本地化表示
- IPA音标是重要的标准化参考点

## 3. 数据质量问题分析

### 3.1 链接完整性问题
- **PHP文件**: 94个链接指向PHP文件，需要验证是否存在对应的HTM版本
- **Fragment链接**: 29个包含HTML锚点的链接，用于区分同一页面的不同部分
- **缺失文件**: erratum.md中列出了多个不存在或链接错误的文件

### 3.2 命名一致性问题  
- **字符编码**: 混用不同的撇号字符（U+2019 vs U+02BC）
- **拼写变体**: 如Saami/Sámi、capizon/capiznon等
- **标签差异**: 同一实体在不同上下文中可能有不同的显示名称

### 3.3 结构性问题
- **重叠实体**: 126个页面同时包含语言和书写系统信息
- **分类边界**: 某些条目的语言/书写系统分类可能不够明确
- **关联关系**: 语言与书写系统的多对多关系需要标准化

## 4. HTML Fragment详细分析

### 4.1 Fragment完整列表和分类

#### 语言类Fragment (6个)
| 链接 | 标签 | 分类 | 说明 |
|-----|------|------|------|
| `kanga.htm#kufa` | Kufa | 地理变体 | Kufa地区的Kanga语 |
| `mari.htm#hm` | Mari (Hill) | 地理变体 | 山地马里语 |
| `mari.htm#mm` | Mari (Meadow) | 地理变体 | 草原马里语 |
| `mari.htm#nwm` | Mari (Northwestern) | 地理变体 | 西北马里语 |
| `sorbian.htm#ls` | Sorbian (Lower) | 地理变体 | 下索布语 |
| `sorbian.htm#us` | Sorbian (Upper) | 地理变体 | 上索布语 |

#### 书写系统类Fragment (12个)
| 链接 | 标签 | 分类 | 说明 |
|-----|------|------|------|
| `latin.htm#archaic` | Archaic Latin | 历史变体 | 古拉丁文 |
| `runic.htm#elder` | Elder Futhark | 历史变体 | 老福萨克文 |
| `runic.htm#medieval` | Medieval (Latinised) Futhark | 历史变体 | 中世纪福萨克文 |
| `runic.htm#yngrfuthark` | Younger Futhark | 历史变体 | 新福萨克文 |
| `elamite.htm#old` | Old Elamite | 历史变体 | 古埃兰文 |
| `elamite.htm#proto` | Proto-Elamite | 历史变体 | 原始埃兰文 |
| `oldenglish.htm#oe` | Old English | 历史变体 | 古英语书写 |
| `irish.htm#irishunc` | Irish (Uncial) | 书写风格 | 爱尔兰安色尔体 |
| `german.htm#suetterlin` | Sütterlin | 书写风格 | 德语苏特林体 |
| `palawano.htm#ibalnan` | Ibalnan | 地理变体 | Ibalnan地区变体 |
| `yonaguni.htm#kaida` | Kaida | 未知分类 | 需进一步调查 |

#### 单语言书写系统Fragment (11个)
主要集中在`olditalic.htm`（古意大利文字）和`somali.htm`（索马里文字）：
- `olditalic.htm`: 包含7个古意大利文字变体
- `somali.htm`: 包含2个索马里文字系统（Borama, Osmanya）
- `uyghur.htm#uighurvert`: 古维吾尔文

### 4.2 Fragment处理策略
1. **保留完整标识**: Fragment应作为实体的完整标识符保留
2. **层次化分类**: 建立主类型-子类型的层次结构
3. **ISO映射考虑**: 某些Fragment可能对应独立的ISO代码，某些可能需要合并

## 5. 关键数据关系分析

### 5.1 实体类型重叠情况
```
总页面数：约2,600+ (language/ + writing/ 目录)
├── 纯语言页面：约2,106 (2,232 - 126)
├── 纯书写系统页面：约243 (369 - 126) 
└── 混合页面：126 (需要内容分析确定主分类)
```

### 5.2 书写系统-语言关联模式
```
书写系统总数：369 + 50 = 419
├── 单语言书写系统：129 (langalphSingle.csv)
├── 多语言书写系统：50 (langalphMap.json，平均46.8语言/系统)
└── 其他书写系统：240 (writing.csv中的其余部分)
```

### 5.3 数据源优先级
1. **ISO标准**: 权威参考，用于最终标准化
2. **langalphMap.json**: 明确的书写系统-语言关联关系
3. **langalphSingle.csv**: 单语言书写系统的可靠来源
4. **language.csv/writing.csv**: 基础分类，但可能有重叠
5. **CSV表格数据**: 详细的语言学信息，用于验证和补充

## 6. 推荐的下一步工作流程

### 6.1 第一阶段：基础清洗和标准化 (优先级：高)
1. **创建实体标识符标准化脚本**
   - 处理PHP vs HTM文件扩展名
   - 标准化Fragment链接格式
   - 建立统一的实体ID系统

2. **建立初步ISO映射表**
   - 语言名称到ISO 639-3代码的模糊匹配
   - 书写系统名称到ISO 15924代码的模糊匹配
   - 记录无法匹配的条目供人工审查

3. **错误修正系统**
   - 基于erratum.md创建已知错误的补丁文件
   - 实现可选的错误修正应用机制

### 6.2 第二阶段：深度分析和验证 (优先级：中)
1. **重叠页面内容分析**
   - 分析126个重叠页面确定主要分类
   - 提取页面中的语言vs书写系统信息
   - 建立页面内容的结构化元数据

2. **表格数据质量评估**
   - 分析2,828个CSV文件的内容模式
   - 识别IPA音标的一致性
   - 验证语言名称的本地化表示

### 6.3 第三阶段：最终整合和输出 (优先级：中低)
1. **生成最终数据集**
   - 创建标准化的语言-书写系统关联表
   - 包含ISO代码的完整元数据
   - 数据质量评估报告

2. **为其他LLM准备数据**
   - 创建适合LLM处理的数据格式
   - 提供必要的上下文和元数据
   - 建立验证和反馈机制

### 6.4 建议的技术实现
- **语言**: Python（便于CSV/JSON处理和字符串匹配）
- **匹配算法**: 使用fuzzywuzzy或类似库进行名称匹配
- **输出格式**: JSON或SQLite数据库，便于后续查询和更新
- **错误处理**: 补丁式修正，保持原始数据不变

---
*文档最后更新: 基于完整数据结构分析*
*下一步: 等待用户确认优先级和具体实施方向* 
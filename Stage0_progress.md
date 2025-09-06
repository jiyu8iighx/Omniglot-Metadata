# Stage0 重建进展报告

## 概述
Stage0为Omniglot网站源数据的重新下载和解析阶段，旨在获取网站维护者根据勘误更新后的最新数据。

## 完成进展

### 1. 文件迁移 ✅
- 创建`Stage0-old/`目录
- 移动旧的源文件：`languages.htm`, `index.htm`, `langalph.htm`, `charts.html`
- 移动旧的衍生文件：`language.csv`, `writing.csv`, `langalphSingle.csv`, `langalphMap.csv`, `langalphMap.json`
- 移动旧的页面内容目录：`language/`, `writing/`, `chart/`, `csv/`

### 2. 索引页面解析 ✅

#### 基础页面解析
- **languages.htm** → **language.csv**: 2241个语言链接（比旧版本+9个）
- **index.htm** → **writing.csv**: 369个书写系统链接（与旧版本相同）
- **charts.html** → **charts.csv**: 1991个表格文件链接

#### langalph.htm页面解析
- **langalphSingle.csv**: 50个单语言书写系统（与旧版本相同）
- **langalphMap.json**: 51个书写系统-语言映射关系（比旧版本+1个）

## HTML结构特征与解析方法

### 1. 标准列表页面（languages.htm, index.htm, charts.html）

**HTML结构特征:**
```html
<div id="list2">
<ol>
 <li><p><a id="a"></a>
 <a href="aari.htm">Aari</a>,
 <a href="abaza.htm">Abaza</a>,
 ...
 </p></li>
 ...
</ol>
</div>
```

**解析方法:**
1. 查找第一个`<ol>`元素
2. 提取所有`<li>`元素中的`<a>`标签
3. 从`<a>`标签提取`href`属性和文本内容
4. 断言验证：`ol`元素至少包含10个`li`元素

**输出格式:** CSV文件，每行包含`链接目标,链接标签`

### 2. langalph.htm页面

#### 2.1 单/多语言书写系统列表

**HTML结构特征:**
```html
<p>
<a href="链接1">标签1</a>,
<a href="链接2">标签2</a>,
... (50+个a标签)
</p>
```

**解析方法:**
1. 查找包含5个以上`<a>`标签的`<p>`元素
2. 按`<a>`标签数量排序，取前两个（130个和50个）
3. 提取所有`<a>`标签的`href`和文本内容

#### 2.2 书写系统-语言映射表

**HTML结构特征:**
```html
<table>
<tr><th>Writing system</th><th>Used to write</th></tr>
<!-- 两列格式 -->
<tr>
 <td><a id="arabic"></a><a href="arabic.htm">Arabic</a></td>
 <td><a href="/writing/lang1.htm">Language1</a>, ...</td>
</tr>
<!-- 单列格式 -->
<tr>
 <td><a id="latin"></a><div><a href="latin.htm">Latin</a></div><a href="/writing/lang1.htm">Language1</a>...</td>
</tr>
</table>
```

**解析方法:**
1. 查找`<table>`元素
2. 遍历所有`<tr>`元素，根据`<td>`数量判断格式：
   - **两列格式（td_count=2）**: 左列书写系统，右列语言列表
   - **单列格式（td_count=1）**: `a(id), div(a href), a(语言), a(语言), ...`
3. 提取书写系统信息：`AnchorID`, `Link`, `Label`
4. 提取语言列表：`[href, label]`数组
5. 断言验证：table至少包含10行

**输出格式:** JSON文件，结构如下：
```json
[
  {
    "writing": {
      "AnchorID": "arabic",
      "Link": "arabic.htm", 
      "Label": "Arabic"
    },
    "language": [
      ["/writing/lang1.htm", "Language1"],
      ["/writing/lang2.htm", "Language2"]
    ]
  }
]
```

## 脚本文件

### parse_index_pages.py
- 解析标准列表页面（languages.htm, index.htm, charts.html）
- 支持多种调用方式：`--languages`, `--index`, `--charts`, `--all`, `--input --output`
- 包含结构验证断言

### parse_langalph.py  
- 解析langalph.htm中的p元素列表
- 生成langalphSingle.csv
- 识别table元素位置

### parse_langalph_table.py
- 解析langalph.htm中的table元素
- 支持两种行格式的自动识别
- 生成langalphMap.json
- 包含详细的结构验证断言

## 数据变化分析

### 新增内容
1. **language.csv**: +9个语言链接
2. **langalphMap.json**: +1个书写系统映射关系

这些变化可能反映了：
- 网站维护者采纳的勘误修正
- 新增的语言或书写系统条目
- 数据质量的提升

## 下一步计划
1. 生成详细页面下载列表
2. 下载所有语言页面、书写系统页面和表格文件
3. 验证解析结果的准确性
4. 进入Stage1数据处理阶段

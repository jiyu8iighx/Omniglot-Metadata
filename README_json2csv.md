# JSON到CSV转换工具使用说明

## 概述

`json2csv.py` 是一个灵活的JSON到CSV转换工具，支持复杂嵌套结构的表格化输出。通过声明式的字段规范，可以控制如何处理数组、对象和嵌套数据。

## 快速开始

### 基本用法
```bash
# 最简单的用法（使用默认规范）
python json2csv.py data.json

# 指定输出文件
python json2csv.py data.json --output result.csv
```

### 使用预设规范
```bash
# 列出所有预设
python json2csv.py --list-presets

# 使用预设规范
python json2csv.py --preset langalph_map langalphMap.json
python json2csv.py --preset path_collection path_collection.json
```

## 字段规范系统

### 字段类型

| 类型 | 用途 | 示例输入 | 输出效果 |
|------|------|----------|----------|
| `expand` | 一对多关系 | `[{"name":"A"}, {"name":"B"}]` | 生成多行，每行一个元素 |
| `tuple` | 固定长度数组 | `[12.34, 56.78]` | 单个字符串："12.34, 56.78" |
| `indexed_dict` | 结构化列表 | `[{"x":1}, {"x":2}]` | 多列：field.0.x, field.1.x |

### 自定义规范

创建规范文件：
```bash
python json2csv.py --create-example-specs my_specs.json
```

编辑规范文件：
```json
{
  "sources": {
    "list_type": "expand",
    "description": "展开sources数组，每个元素一行"
  },
  "coordinates": {
    "list_type": "tuple",
    "separator": ", ",
    "description": "坐标处理为单个字符串"
  },
  "items": {
    "list_type": "indexed_dict",
    "description": "用索引展开为多列"
  }
}
```

使用自定义规范：
```bash
python json2csv.py --custom-specs my_specs.json data.json
```

## 预设规范详解

### 1. `default`
- 所有数组都使用`expand`类型
- 适用于简单的JSON结构

### 2. `langalph_map`
- 专为`langalphMap.json`设计
- 将`language`字段展开为`language.path`和`language.label`列

### 3. `path_collection`
- 专为`path_collection.json`设计
- 将`sources`数组展开，每个来源信息一行

### 4. `example_tuple`
- 演示`tuple`类型处理
- 展示如何将坐标等固定长度数组合并为单个字段

## 命令行选项

```bash
Usage: json2csv.py [OPTIONS] INPUT_FILE

Options:
  -o, --output OUTPUT           输出CSV文件路径
  -p, --preset PRESET          使用预设规范
  -c, --custom-specs FILE       自定义规范JSON文件
  --create-example-specs FILE   创建示例规范文件
  --list-presets               列出所有预设规范
  -v, --verbose                详细输出
  -h, --help                   显示帮助信息
```

## 设计指导

在设计新数据结构时，考虑表格化需求：

### 1. 一对多关系 → `expand`
适用于主实体有多个相关记录的情况：
```json
{
  "entity": "Chinese",
  "writing_systems": ["Traditional", "Simplified", "Pinyin"]
}
```
使用`expand`会生成3行，每行包含一个书写系统。

### 2. 固定格式数据 → `tuple`
适用于坐标、版本号等固定格式：
```json
{
  "location": [39.9042, 116.4074],
  "version": [2, 1, 0]
}
```
使用`tuple`会合并为"39.9042, 116.4074"和"2.1.0"。

### 3. 结构化列表 → `indexed_dict`
适用于需要保持顺序的复杂对象：
```json
{
  "variants": [
    {"name": "Modern", "year": 2000},
    {"name": "Classical", "year": 1800}
  ]
}
```
使用`indexed_dict`会生成`variants.0.name`, `variants.1.name`等列。

## 错误处理

工具会检查：
- 输入文件是否存在
- JSON格式是否有效
- 自定义规范文件是否正确
- 转换过程中的异常

所有错误都会显示清晰的错误信息。

## 示例

更多使用示例请参考：
- `test_outputs/` 目录中的测试文件
- `data_flow_design.md` 中的详细文档


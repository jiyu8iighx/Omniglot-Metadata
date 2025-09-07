# Source组合模式分析（简化版）

## 正常模式（按重要性排序）

### 1. 标准语言条目
- **模式**: `langalphMap.json:language=single + language.csv:language=single`
- **频次**: 1837次
- **含义**: 标准语言，在language.csv中列出，在langalphMap中被1个书写系统引用
- **处理**: 标准语言实体

### 2. 多书写系统语言
- **模式**: `langalphMap.json:language=multiple + language.csv:language=single`  
- **频次**: 151+38+2+2+1次（不同的multiple数量）
- **含义**: 正常，一个语言可以用多种书写系统书写（如梵语用5种书写系统）
- **处理**: 多书写系统语言实体

### 3. 独立书写系统
- **模式**: `writing.csv:writing_system=single`
- **频次**: 160次
- **含义**: 仅在writing.csv中的书写系统，没有对应语言信息
- **处理**: 纯书写系统实体

### 4. 单语言书写系统（一致性好）
- **模式**: `langalphSingle.csv:writing_system=single + writing.csv:writing_system=single`
- **频次**: 40次
- **含义**: 数据一致性好，同一书写系统在两个来源都出现
- **处理**: 验证过的单语言书写系统

### 5. 孤立语言
- **模式**: `language.csv:language=single`
- **频次**: 49次
- **含义**: 仅在language.csv中的语言，没有书写系统信息
- **处理**: 缺少书写系统信息的语言

## 复合模式（语言+书写系统混合）

### 6. 复合页面（标准）
- **模式**: `language.csv:language=single + writing.csv:writing_system=single`
- **频次**: 28次
- **含义**: 页面同时包含语言和书写系统信息
- **处理**: 需要拆分为独立实体

### 7. 复合页面（多语言映射）
- **模式**: `langalphMap.json:language=single + language.csv:language=single + writing.csv:writing_system=single`
- **频次**: 14次
- **含义**: 复合页面，有书写系统映射
- **处理**: 需要拆分，保留映射关系

### 8. 复合页面（复杂）
- **模式**: 各种包含multiple的复合组合
- **频次**: 多个小频次组合
- **含义**: 复杂的复合页面，可能有重复数据
- **处理**: 需要仔细拆分和去重

## 异常模式（需要审查）

### 9. 重复语言条目
- **模式**: `language.csv:language=multiple`（不管其他维度）
- **含义**: 同一语言在language.csv中多次出现
- **处理**: 检查是否为真重复或合理的多链接

### 10. 重复书写系统条目  
- **模式**: `writing.csv:writing_system=multiple`（不管其他维度）
- **含义**: 同一书写系统多次出现
- **处理**: 检查是否为fragment问题或真重复

### 11. 孤立的书写系统映射
- **模式**: `langalphMap.json:writing_system=single`（无其他维度）
- **频次**: 1次
- **含义**: 仅在langalphMap中出现的书写系统
- **处理**: 检查是否缺少对应的writing.csv条目

## 处理策略建议

```python
def classify_entity_pattern(sources):
    """根据简化的source模式分类实体"""
    
    has_lang_csv = 'language.csv:language' in sources
    has_writing_csv = 'writing.csv:writing_system' in sources  
    has_langalph_lang = 'langalphMap.json:language' in sources
    has_langalph_writing = 'langalphMap.json:writing_system' in sources
    has_single_writing = 'langalphSingle.csv:writing_system' in sources
    
    # 检查是否有multiple
    has_multiple = any('multiple' in str(v) for v in sources.values())
    
    if has_multiple:
        if has_lang_csv and has_writing_csv:
            return "COMPLEX_COMPOSITE_PAGE"
        elif has_langalph_lang:
            return "MULTI_SCRIPT_LANGUAGE"  # 正常
        else:
            return "DUPLICATE_DATA"  # 需要审查
    
    # 单一来源模式
    if has_lang_csv and has_langalph_lang and not has_writing_csv:
        return "STANDARD_LANGUAGE"
    
    if has_writing_csv and not has_lang_csv:
        return "PURE_WRITING_SYSTEM"
        
    if has_lang_csv and has_writing_csv:
        return "COMPOSITE_PAGE"
        
    if only_one_source(sources):
        return "ISOLATED_ENTRY"
        
    return "REVIEW_NEEDED"
```

## 关键洞察

1. **多书写系统语言是正常的**：如梵语被多种书写系统书写
2. **重数不重要**：只需要区分single vs multiple
3. **复合页面很常见**：28+个页面同时包含语言和书写系统
4. **数据一致性良好**：langalphSingle和writing.csv有40个重叠
5. **真正异常的是重复条目**：same entity appearing multiple times in same source

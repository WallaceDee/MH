# 爬虫编码问题修复说明

## 问题描述

在Windows环境下运行爬虫时，出现了以下编码错误：

```
'gbk' codec can't encode character '\u26a0' in position 0: illegal multibyte sequence
```

## 问题原因

1. **Windows默认编码**: Windows系统默认使用GBK编码
2. **Unicode字符**: 日志中包含了Unicode字符（如⚠️、🎉等）
3. **控制台输出**: 控制台处理器没有指定UTF-8编码

## 解决方案

### 1. 编码修复工具 (`src/spider/encoding_fix.py`)

创建了专门的编码修复工具，包含以下功能：

```python
def fix_encoding():
    """修复编码问题"""
    # 设置环境变量强制使用UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 重新配置标准输出和错误输出
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
```

### 2. 安全打印函数

提供了安全的打印函数，自动处理编码问题：

```python
def safe_print(*args, **kwargs):
    """安全的打印函数，处理编码问题"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 替换Unicode字符为ASCII等价字符
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_arg = arg.replace('🎉', '[SUCCESS]')
                safe_arg = safe_arg.replace('⚠️', '[WARNING]')
                # ... 更多替换
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)
```

### 3. 爬虫初始化修复

在装备爬虫和召唤兽爬虫的初始化方法中添加了编码修复：

```python
def __init__(self):
    # 修复编码问题
    from src.spider.encoding_fix import fix_encoding
    fix_encoding()
    
    # ... 其他初始化代码
```

### 4. 日志处理器修复

修改了日志处理器的控制台输出编码：

```python
# 创建控制台处理器 - 设置UTF-8编码避免GBK编码错误
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# 设置控制台输出编码为UTF-8
if hasattr(console_handler.stream, 'reconfigure'):
    try:
        console_handler.stream.reconfigure(encoding='utf-8')
    except Exception:
        pass  # 如果设置失败，继续使用默认编码
```

## 修复的文件

1. **`src/spider/encoding_fix.py`** - 编码修复工具
2. **`src/spider/equip.py`** - 装备爬虫编码修复
3. **`src/spider/pet.py`** - 召唤兽爬虫编码修复

## 测试验证

运行测试脚本验证修复效果：

```bash
python tests/test_encoding_fix.py
```

测试包括：
1. 编码修复功能测试
2. Unicode字符输出测试
3. 爬虫初始化测试

## 修复效果

### 修复前
- 出现GBK编码错误
- 无法输出Unicode字符
- 爬虫初始化失败

### 修复后
- 自动设置UTF-8编码
- 支持Unicode字符输出
- 爬虫正常初始化
- 提供安全的备用方案

## 注意事项

1. **环境变量**: 设置了`PYTHONIOENCODING=utf-8`
2. **兼容性**: 在Python 3.7+版本中工作
3. **备用方案**: 如果编码设置失败，会使用安全打印函数
4. **日志文件**: 日志文件仍然使用UTF-8编码保存

## 总结

通过多层次的编码修复方案，解决了Windows环境下爬虫的Unicode字符输出问题，确保爬虫能够正常运行并输出包含Unicode字符的日志信息。

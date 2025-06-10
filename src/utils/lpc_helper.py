#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LPC解析助手工具类
负责处理梦幻西游CBG中的LPC格式数据解析和转换
"""

import re
import json
import logging
import ast


class LPCHelper:
    """LPC格式解析助手工具类"""
    
    def __init__(self, logger=None):
        """初始化LPC解析器"""
        self.logger = logger or logging.getLogger(__name__)
    
    def js_eval(self, js_str):
        """Python版本的js_eval函数，安全地解析JavaScript格式的数据
        
        对应JavaScript中的js_eval函数
        """
        try:
            if not js_str or not isinstance(js_str, str):
                return {}
            
            # 去除外层括号（如果有的话）
            js_str = js_str.strip()
            if js_str.startswith('(') and js_str.endswith(')'):
                js_str = js_str[1:-1]
            
            # 尝试JSON解析
            return json.loads(js_str)
            
        except json.JSONDecodeError:
            try:
                # 如果JSON解析失败，尝试使用ast.literal_eval（更安全的eval）
                return ast.literal_eval(js_str)
            except (ValueError, SyntaxError):
                self.logger.warning("js_eval解析失败")
                self.logger.warning(js_str)
                return {}
    
    def improved_lpc_parser(self, lpc_str):
        """
        复杂LPC解析器，支持深度嵌套结构和特殊字符处理
        
        特点：
        - 使用递归解析，支持复杂嵌套结构
        - 保留原始转义字符
        - 将LPC数组转换为字符串格式
        - 适用于复杂的角色数据解析（如large_equip_desc）
        
        Returns:
            dict: 解析后的Python字典对象
        """
        try:
            if not lpc_str or not isinstance(lpc_str, str):
                return {}
            
            # 清理数据
            data = lpc_str.strip()
            
            # 移除外层括号 ([ ... ])
            if data.startswith('([') and data.endswith('])'):
                data = data[2:-2]
            elif data.startswith('({') and data.endswith('})'):
                data = data[2:-2]
            
            # 递归处理嵌套的LPC结构
            def process_lpc_value(value_str):
                value_str = value_str.strip()
                
                # 处理数组 ([...])
                if value_str.startswith('([') and value_str.endswith('])'):
                    inner = value_str[2:-2]
                    return parse_lpc_mapping(inner)
                
                # 处理映射 ({...})
                elif value_str.startswith('({') and value_str.endswith('})'):
                    inner = value_str[2:-2]
                    return parse_lpc_array(inner)
                
                # 处理字符串
                elif value_str.startswith('"') and value_str.endswith('"'):
                    return value_str[1:-1]
                
                # 处理数字
                elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
                    return int(value_str)
                
                # 处理浮点数
                elif '.' in value_str:
                    try:
                        return float(value_str)
                    except ValueError:
                        return value_str
                
                return value_str
            
            def parse_lpc_mapping(data_str):
                """解析LPC映射格式 key:value,key:value"""
                result = {}
                if not data_str.strip():
                    return result
                
                # 手动分割，考虑嵌套结构
                parts = []
                current = ""
                bracket_count = 0
                in_quotes = False
                
                for char in data_str:
                    if char == '"' and (not current or current[-1] != '\\'):
                        in_quotes = not in_quotes
                    elif not in_quotes:
                        if char in '([{':
                            bracket_count += 1
                        elif char in ')]}':
                            bracket_count -= 1
                        elif char == ',' and bracket_count == 0:
                            if current.strip():
                                parts.append(current.strip())
                            current = ""
                            continue
                    current += char
                
                if current.strip():
                    parts.append(current.strip())
                
                for part in parts:
                    if ':' in part:
                        # 找到第一个冒号的位置（不在引号内）
                        colon_pos = -1
                        in_quotes = False
                        for i, char in enumerate(part):
                            if char == '"' and (i == 0 or part[i-1] != '\\'):
                                in_quotes = not in_quotes
                            elif char == ':' and not in_quotes:
                                colon_pos = i
                                break
                        
                        if colon_pos > 0:
                            key = part[:colon_pos].strip()
                            value = part[colon_pos+1:].strip()
                            
                            # 处理键名（去除引号）
                            if key.startswith('"') and key.endswith('"'):
                                key = key[1:-1]
                            
                            # 处理值
                            processed_value = process_lpc_value(value)
                            result[key] = processed_value
                
                return result
            
            def parse_lpc_array(data_str):
                """解析LPC数组格式"""
                # 简化处理，返回字符串表示
                return f"[{data_str}]"
            
            # 解析主数据
            result = parse_lpc_mapping(data)
            self.logger.debug(f"复杂LPC解析成功，解析了 {len(result)} 个字段")
            return result
            
        except Exception as e:
            self.logger.error(f"复杂LPC解析失败: {e}")
            return {}
    
    def lpc_to_js(self, lpc_str, return_dict=False):
        """
        增强版LPC转换器，支持深层递归解析
        
        特点：
        - 递归处理嵌套的LPC结构
        - 正确转换所有层级的数据
        - 处理数字键和字符串键
        - 支持数组和映射的嵌套
        
        Args:
            lpc_str: LPC格式字符串
            return_dict: 如果为True，返回Python字典对象；否则返回JSON字符串
        
        Returns:
            JSON字符串或Python字典对象，取决于return_dict参数
        """
        try:
            def parse_lpc_structure(text):
                """递归解析LPC结构，返回Python对象"""
                text = text.strip()
                
                # 处理映射：([key:value,key:value]) -> {key:value,key:value}
                if text.startswith('([') and text.endswith('])'):
                    inner_content = text[2:-2].strip()
                    return parse_lpc_mapping(inner_content)
                
                # 处理数组：({item,item,item}) -> [item,item,item]
                elif text.startswith('({') and text.endswith('})'):
                    inner_content = text[2:-2].strip()
                    return parse_lpc_array(inner_content)
                
                # 处理字符串
                elif text.startswith('"') and text.endswith('"'):
                    return text[1:-1]
                
                # 处理数字
                elif text.isdigit() or (text.startswith('-') and text[1:].isdigit()):
                    return int(text)
                
                # 处理浮点数
                elif re.match(r'^-?\d+\.\d+$', text):
                    return float(text)
                
                # 默认返回字符串
                return text
            
            def parse_lpc_mapping(content):
                """解析LPC映射内容"""
                if not content.strip():
                    return {}
                
                result = {}
                items = split_lpc_items(content)
                
                for item in items:
                    item = item.strip()
                    if not item:
                        continue
                    
                    # 找到键值分隔符 ':'
                    colon_pos = find_key_value_separator(item)
                    if colon_pos == -1:
                        continue
                    
                    key_part = item[:colon_pos].strip()
                    value_part = item[colon_pos + 1:].strip()
                    
                    # 处理键名（移除引号）
                    if key_part.startswith('"') and key_part.endswith('"'):
                        key = key_part[1:-1]
                    else:
                        key = key_part
                    
                    # 递归处理值
                    value = parse_lpc_structure(value_part)
                    result[key] = value
                
                return result
            
            def parse_lpc_array(content):
                """解析LPC数组内容"""
                if not content.strip():
                    return []
                
                result = []
                items = split_lpc_items(content)
                
                for item in items:
                    item = item.strip()
                    if not item:
                        continue
                    
                    # 递归处理每个数组元素
                    value = parse_lpc_structure(item)
                    result.append(value)
                
                return result
            
            def split_lpc_items(content):
                """智能分割LPC项目，考虑嵌套结构"""
                items = []
                current_item = ""
                bracket_depth = 0
                in_quotes = False
                escape_next = False
                
                for char in content:
                    if escape_next:
                        current_item += char
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        current_item += char
                        continue
                    
                    if char == '"' and not escape_next:
                        in_quotes = not in_quotes
                        current_item += char
                        continue
                    
                    if not in_quotes:
                        if char in '([{':
                            bracket_depth += 1
                        elif char in ')]}':
                            bracket_depth -= 1
                        elif char == ',' and bracket_depth == 0:
                            # 找到分隔符，添加当前项
                            if current_item.strip():
                                items.append(current_item.strip())
                            current_item = ""
                            continue
                    
                    current_item += char
                
                # 添加最后一项
                if current_item.strip():
                    items.append(current_item.strip())
                
                return items
            
            def find_key_value_separator(item):
                """找到键值分隔符':'的位置，考虑嵌套和引号"""
                bracket_depth = 0
                in_quotes = False
                escape_next = False
                
                for i, char in enumerate(item):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"':
                        in_quotes = not in_quotes
                        continue
                    
                    if not in_quotes:
                        if char in '([{':
                            bracket_depth += 1
                        elif char in ')]}':
                            bracket_depth -= 1
                        elif char == ':' and bracket_depth == 0:
                            return i
                
                return -1
            
            # 开始解析
            result_obj = parse_lpc_structure(lpc_str)
            
            # 如果请求返回字典对象
            if return_dict:
                return result_obj
            
            # 否则返回JSON字符串
            json_str = json.dumps(result_obj, ensure_ascii=False, separators=(',', ':'))
            self.logger.debug(f"深层LPC解析成功，结果长度: {len(json_str)}")
            return json_str
            
        except Exception as e:
            self.logger.warning(f"深层LPC解析失败: {e}")
            # 降级到简单模式
            return self.simple_lpc_to_js(lpc_str, return_dict)
    
    def simple_lpc_to_js(self, lpc_str, return_dict=False):
        """
        简化版LPC转换器（作为后备方案）
        """
        try:
            # 简化的LPC到JSON转换，特别处理数字键
            result = lpc_str.strip()
            
            # 移除最外层的 ([ ]) 
            if result.startswith('([') and result.endswith('])'):
                result = result[2:-2]
                # 包装成JSON对象
                result = '{' + result + '}'
            elif result.startswith('({') and result.endswith('})'):
                result = result[2:-2]
                # 包装成JSON数组
                result = '[' + result + ']'
            
            # 处理嵌套的LPC结构，使用更精确的替换
            # 从内到外逐步替换
            depth = 0
            max_depth = 20  # 防止无限循环
            
            while ('([' in result or '({' in result) and depth < max_depth:
                depth += 1
                # 处理mapping: ([...]) -> {...}
                result = result.replace('([', '{')
                result = result.replace('])', '}')
                
                # 处理array: ({...}) -> [...]
                result = result.replace('({', '[')
                result = result.replace('})', ']')
            
            # 修复：使用更精确的正则表达式，只处理真正的键值对
            # 处理数字键：匹配 数字: 且前面是 { 或 , 或开头，且不在引号内
            # 使用负向后向断言和前向断言确保不匹配字符串内部的内容
            def quote_keys(match_obj):
                """处理键的引号添加，确保不在字符串内部"""
                full_match = match_obj.group(0)
                prefix = match_obj.group(1) if match_obj.group(1) else ''
                key = match_obj.group(2)
                suffix = match_obj.group(3)
                return f'{prefix}"{key}"{suffix}'
            
            # 匹配数字键，确保前面是分隔符（{, 或开头），且不在字符串内
            # 模式解释：(^|[{,]\s*) 捕获开头或分隔符，(\d+) 捕获数字，(\s*:) 捕获冒号
            result = re.sub(r'(^|[{,]\s*)(\d+)(\s*:)', quote_keys, result)
            
            # 处理字符串键：确保键名有引号（同样避免处理字符串内部）
            result = re.sub(r'(^|[{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', quote_keys, result)
            
            # 清理多余的逗号
            result = re.sub(r',\s*}', '}', result)
            result = re.sub(r',\s*]', ']', result)
            
            # 处理可能的空结构
            result = result.replace('{}', '{}')
            result = result.replace('[]', '[]')
            
            self.logger.debug(f"简单LPC转换结果前200字符: {result[:200]}")
            
            # 如果请求返回字典对象
            if return_dict:
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {}
            
            # 尝试解析以验证正确性
            try:
                json.loads(result)
                return result
            except json.JSONDecodeError as e:
                self.logger.debug(f"JSON验证失败: {e}")
                return result  # 即使验证失败也返回，让上层处理
            
        except Exception as e:
            self.logger.warning(f"简单LPC转换失败: {e}")
            if return_dict:
                return {}
            return lpc_str 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁召唤兽信息解析模块
Python版本的召唤兽信息解析函数，对应JavaScript版本的实现
"""

import json
import base64
import re
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import unquote
import sys
import os
import math
from datetime import datetime

# 添加src目录到路径以便导入LPCHelper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.lpc_helper import LPCHelper

logger = logging.getLogger(__name__)


class PetDescDecoder:
    """召唤兽描述信息解码器"""
    
    def __init__(self):
        # 字符串数组，对应JavaScript版本中的混淆数组
        self.string_array = ['substring', 'atob', 'charCodeAt', 'push', 'test']
        
        # 重排字符串数组（对应JavaScript中的混淆逻辑）
        self._shuffle_string_array()
    
    def _shuffle_string_array(self):
        """重排字符串数组，模拟JavaScript版本的混淆逻辑"""
        # 对应JavaScript中的重排逻辑
        count = 339  # 0x153
        for _ in range(count):
            self.string_array.append(self.string_array.pop(0))
    
    def _get_string(self, index: int) -> str:
        """获取字符串数组中的元素"""
        index = index - 0x0
        return self.string_array[index]
    
    def decode_desc(self, encoded_string: str, cookie_key: str = '') -> str:
        """
        解码加密的召唤兽描述信息
        对应JavaScript版本的decode_desc函数
        
        Args:
            encoded_string: 加密的字符串
            cookie_key: 从cookie中提取的_k参数
            
        Returns:
            解码后的字符串
        """
        try:
            # 去除首尾空格
            encoded_string = encoded_string.strip()
            
            # 检查是否被@符号包围
            if not re.match(r'^@[\s\S]*@$', encoded_string):
                return encoded_string
            
            # 去除@符号
            encoded_string = re.sub(r'^@|@$', '', encoded_string)
            
            # 检查是否包含@分隔符来提取密钥
            if '@' in encoded_string:
                at_index = encoded_string.find('@')
                cookie_key = encoded_string[:at_index]
                encoded_string = encoded_string[at_index + 1:]
            
            # Base64解码
            try:
                decoded_bytes = base64.b64decode(encoded_string)
                decoded_str = decoded_bytes.decode('utf-8')
            except Exception as e:
                logger.warning(f"Base64解码失败: {e}")
                return encoded_string
            
            # 尝试使用eval解析（对应JavaScript版本的eval逻辑）
            try:
                # 尝试JSON解析
                decoded_data = json.loads(decoded_str)
            except json.JSONDecodeError:
                # 如果JSON解析失败，直接使用字符串
                decoded_data = decoded_str
            
            # 如果解码结果有d属性，则使用d属性（对应JavaScript逻辑）
            if isinstance(decoded_data, dict) and 'd' in decoded_data:
                decoded_data = decoded_data['d']
            
            # 如果有密钥且decoded_data是字符串，进行XOR解密
            if cookie_key and isinstance(decoded_data, str):
                decrypted = self._xor_decrypt(decoded_data, cookie_key)
                # XOR解密后，尝试JSON解析，如果成功则返回JSON字符串
                try:
                    json.loads(decrypted)  # 验证是否为有效JSON
                    return decrypted  # 返回JSON字符串
                except json.JSONDecodeError:
                    return decrypted  # 如果不是JSON，返回原字符串
            
            # 如果decoded_data是字典，返回JSON字符串
            if isinstance(decoded_data, dict):
                return json.dumps(decoded_data)
            
            return str(decoded_data)
            
        except Exception as e:
            logger.error(f"解码失败: {e}")
            return encoded_string
    
    def _xor_decrypt(self, data: str, key: str) -> str:
        """
        使用XOR算法解密数据
        对应JavaScript版本的XOR解密逻辑
        
        Args:
            data: 要解密的数据
            key: 解密密钥
            
        Returns:
            解密后的字符串
        """
        if not key:
            return data
        
        try:
            result = []
            key_index = 0
            
            for char_index in range(len(data)):
                char_code = ord(data[char_index])
                key_char = ord(key[key_index % len(key)])
                key_index += 1
                
                # XOR运算
                char_code = char_code ^ key_char
                # 转换为二进制字符串，对应JavaScript版本的toString(2)
                result.append(format(char_code, 'b'))  # 转换为二进制字符串
            
            # 将二进制字符串转换为字符，对应JavaScript版本的逻辑
            chars = []
            for binary_str in result:
                try:
                    char_code = int(binary_str, 2)
                    chars.append(chr(char_code))
                except (ValueError, OverflowError):
                    continue
            
            return ''.join(chars)
            
        except Exception as e:
            logger.error(f"XOR解密失败: {e}")
            return data


class PetInfoParser:
    """召唤兽信息解析器"""
    
    def __init__(self):
        self.decoder = PetDescDecoder()
        self.lpc_helper = LPCHelper()
    
    def parse_desc_info(self, desc_info: str) -> str:
        """
        解析召唤兽描述信息
        对应JavaScript版本的parse_desc_info函数
        
        Args:
            desc_info: 召唤兽描述信息
            
        Returns:
            解析后的描述信息
        """
        try:
            decoded_info = self.decoder.decode_desc(desc_info)
            # 解码后的数据是分号分隔的字符串，直接返回
            return decoded_info
        except Exception as e:
            logger.warning(f"解析描述信息失败: {e}")
            return desc_info
    
    def parse_fashang_fafang(self, desc_info: str) -> Dict[str, Optional[int]]:
        """
        解析法伤和法防信息
        对应JavaScript版本的parse_fashang_fafang函数
        
        Args:
            desc_info: 召唤兽描述信息
            
        Returns:
            包含法伤和法防的字典
        """
        try:
            # 完全按照JavaScript逻辑：JSON.parse(window.decode_desc(desc_info))
            decoded_data = self.decoder.decode_desc(desc_info)
            data = json.loads(decoded_data)
            return {
                'fashang': data.get('fashang'),
                'fafang': data.get('fafang')
            }
        except Exception as e:
            return {'fashang': None, 'fafang': None}
    
    def get_pet_attrs_info(self, pet_desc: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取召唤兽属性信息
        对应JavaScript版本的get_pet_attrs_info函数
        
        Args:
            pet_desc: 召唤兽描述字符串
            options: 解析选项
            
        Returns:
            召唤兽属性信息字典
        """
        if options is None:
            options = {}
        
        # 修正召唤兽描述格式
        pet_desc = self._correct_pet_desc(pet_desc)
        
        # 分割属性
        attrs = pet_desc.split(';')
        
        # 获取选项参数
        fashang = options.get('fashang')
        fafang = options.get('fafang')
        only_basic_attr = options.get('only_basic_attr', False)
        
        # 解析基础属性
        attrs_info = self._parse_basic_attrs(attrs)
        
        # 解析技能信息
        attrs_info = self._parse_skills(attrs_info)
        
        # 解析其他属性
        if attrs_info.get('other'):
            attrs_info = self._parse_other_attrs(attrs_info, fashang, fafang)
        
        # 如果只需要基础属性，直接返回
        if only_basic_attr:
            return attrs_info
        
        # 解析额外信息
        attrs_info = self._parse_extra_info(attrs_info, attrs)
        
        return attrs_info
    
    def _get_pet_ext_zz(self, data: Dict[str, Any], options: Dict[str, Any]) -> None:
        """
        处理召唤兽额外资质
        对应JavaScript版本的get_pet_ext_zz函数
        
        Args:
            data: 召唤兽属性信息字典
            options: 选项参数
        """
        try:
            # 神兽类型列表
            SHENSHOU_ITYPES = [102005, 102008, 102016, 102018, 102019, 102020, 102021, 102031, 102032, 102035, 102049, 102050, 102051, 102060, 102100, 102101, 102108, 102109, 102110, 102131, 102132, 102249, 102250, 102255, 102256, 102257, 102258, 102259, 102260, 102261, 102262, 102263, 102264, 102265, 102266, 102267, 102268, 102269, 102270, 102271, 102272, 102273, 102274, 102275, 102276, 102277, 102311, 102312, 102313, 102314, 102315, 102316, 102317, 102318, 102825, 102826, 102827, 102828, 102487, 102459, 102497, 102488, 102490, 102498, 112000, 112002, 112027, 112016, 112034, 112028, 112017, 112035]
            
            # 完整的召唤兽战斗等级类型配置
            PET_BATTLE_LEVEL_TYPES = [[2559, 0], [2047, 0], [2046, 0], [2045, 0], [2044, 0], [2555, 0], [2554, 0], [2042, 0], [2553, 0], [2041, 0], [2552, 0], [2040, 0], [2039, 0], [2038, 0], [2037, 0], [2036, 0], [2548, 0], [2547, 0], [2034, 0], [2546, 0], [2033, 0], [2545, 0], [2544, 0], [2030, 0], [2542, 0], [2029, 0], [2541, 0], [2028, 0], [2540, 0], [2539, 0], [2538, 0], [2537, 0], [2024, 0], [2536, 0], [2023, 0], [2534, 0], [2022, 0], [2533, 0], [2530, 0], [2529, 0], [2017, 0], [2528, 0], [2015, 0], [2012, 0], [2524, 0], [2523, 0], [2011, 0], [2010, 0], [2522, 0], [2009, 0], [2007, 0], [2006, 0], [2517, 0], [2004, 0], [2003, 0], [2515, 0], [2002, 0], [2001, 0], [2512, 0], [2511, 0], [2510, 0], [2509, 0], [2507, 0], [2506, 0], [2504, 0], [2502, 0], [2501, 0], [2324, 2], [2323, 2], [2322, 2], [2321, 2], [2320, 2], [2319, 2], [2824, 2], [2823, 2], [2310, 0], [2822, 2], [2309, 0], [2821, 2], [2308, 0], [2820, 2], [2307, 0], [2819, 2], [2306, 0], [2305, 0], [2304, 0], [2303, 0], [2300, 0], [2810, 0], [2809, 0], [2808, 0], [2807, 0], [2806, 0], [2805, 0], [2804, 0], [2803, 0], [2283, 0], [2783, 0], [2247, 2], [2246, 2], [2245, 2], [2244, 2], [2243, 2], [2242, 2], [2241, 1], [2240, 1], [2239, 1], [2238, 0], [2237, 0], [2236, 0], [2235, 0], [2747, 2], [2234, 0], [2746, 2], [2233, 0], [2745, 2], [2232, 1], [2744, 2], [2231, 1], [2743, 2], [2230, 1], [2742, 2], [2229, 0], [2741, 1], [2228, 0], [2740, 1], [2227, 0], [2739, 1], [2226, 0], [2738, 0], [2225, 0], [2737, 0], [2224, 0], [2736, 0], [2735, 0], [2223, 0], [2222, 0], [2734, 0], [2221, 0], [2733, 0], [2220, 0], [2732, 1], [2219, 0], [2731, 1], [2218, 0], [2730, 1], [2217, 0], [2729, 0], [2216, 0], [2728, 0], [2215, 0], [2727, 0], [2214, 0], [2726, 0], [2213, 0], [2725, 0], [2212, 0], [2724, 0], [2723, 0], [2211, 0], [2722, 0], [2210, 0], [2209, 0], [2721, 0], [2208, 0], [2720, 0], [2207, 0], [2719, 0], [2206, 0], [2718, 0], [2205, 0], [2717, 0], [2204, 0], [2716, 0], [2715, 0], [2203, 0], [2714, 0], [2202, 0], [2713, 0], [2201, 0], [2712, 0], [2200, 0], [2711, 0], [2199, 0], [2198, 0], [2710, 0], [2197, 0], [2709, 0], [2708, 0], [2196, 0], [2707, 0], [2195, 0], [2706, 0], [2194, 0], [2705, 0], [2193, 0], [2704, 0], [2192, 0], [2703, 0], [2191, 0], [2702, 0], [2190, 0], [2701, 0], [2189, 0], [2188, 0], [2700, 0], [2187, 0], [2699, 0], [2698, 0], [2186, 0], [2185, 0], [2697, 0], [2184, 0], [2696, 0], [2183, 0], [2695, 0], [2694, 0], [2182, 0], [2693, 0], [2181, 0], [2692, 0], [2180, 0], [2691, 0], [2179, 0], [2690, 0], [2178, 0], [2689, 0], [2688, 0], [2687, 0], [2686, 0], [2685, 0], [2684, 0], [2683, 0], [2682, 0], [2681, 0], [2680, 0], [2679, 0], [2678, 0], [2164, 0], [2163, 1], [2162, 0], [2161, 1], [2160, 1], [2159, 0], [2153, 0], [2664, 0], [2152, 0], [2663, 1], [2151, 0], [2662, 0], [2150, 0], [2661, 1], [2660, 1], [2659, 0], [2144, 0], [2143, 0], [2142, 0], [2141, 0], [2653, 0], [2140, 0], [2652, 0], [2139, 0], [2651, 0], [2138, 0], [2650, 0], [2137, 0], [2136, 0], [2135, 0], [2134, 0], [2133, 0], [2130, 1], [2129, 0], [2128, 1], [2127, 0], [2126, 1], [2125, 0], [2124, 0], [2123, 0], [2122, 0], [2121, 0], [2120, 0], [2119, 0], [2630, 1], [2118, 0], [2629, 0], [2117, 0], [2628, 1], [2116, 0], [2627, 0], [2115, 0], [2626, 1], [2114, 0], [2625, 0], [2113, 0], [2624, 0], [2112, 0], [2623, 0], [2111, 0], [2622, 0], [2621, 0], [2620, 0], [2619, 0], [2107, 0], [2618, 0], [2106, 0], [2617, 0], [2105, 0], [2616, 0], [2104, 0], [2615, 0], [2103, 0], [2614, 0], [2102, 0], [2613, 0], [2612, 0], [2099, 0], [2611, 0], [2098, 0], [2097, 0], [2096, 0], [2607, 0], [2095, 0], [2606, 0], [2094, 0], [2605, 0], [2093, 0], [2604, 0], [2603, 0], [2602, 0], [2599, 0], [2087, 0], [2598, 0], [2086, 0], [2597, 0], [2085, 0], [2596, 0], [2595, 0], [2594, 0], [2593, 0], [2078, 0], [2077, 0], [2076, 0], [2587, 0], [2586, 0], [2074, 0], [2585, 0], [2073, 0], [2072, 0], [2071, 0], [2070, 0], [2068, 0], [2067, 0], [2578, 0], [2066, 0], [2577, 0], [2065, 0], [2576, 0], [2064, 0], [2063, 0], [2574, 0], [2062, 0], [2061, 0], [2573, 0], [2572, 0], [2571, 0], [2059, 0], [2570, 0], [2568, 0], [2567, 0], [2055, 0], [2054, 0], [2566, 0], [2053, 0], [2565, 0], [2052, 0], [2564, 0], [2563, 0], [2562, 0], [2561, 0], [2048, 0], [2411, 2], [2413, 0], [2414, 0], [2415, 0], [2416, 0], [2417, 0], [2418, 0], [2419, 0], [2420, 0], [2421, 0], [2422, 0], [2423, 0], [2424, 0], [2425, 0], [2426, 0], [2427, 0], [2428, 0], [2429, 0], [2430, 0], [2431, 0], [2432, 0], [2433, 0], [2434, 0], [2435, 0], [2436, 0], [2437, 0], [2438, 0], [2439, 0], [2440, 0], [2441, 0], [2442, 0], [2443, 0], [2445, 0], [2447, 0], [2451, 0], [2449, 0], [2450, 0], [2452, 0], [2458, 0], [2453, 0], [2454, 0], [2455, 0], [2456, 0], [2448, 0], [2446, 0], [2444, 0], [2475, 0], [2473, 0], [2471, 1], [2477, 0], [2481, 0], [2479, 2]]
            
            def is_shenshou_pet(pet_id: str, is_super_sum: Optional[int]) -> bool:
                """判断是否为神兽"""
                if is_super_sum is not None:
                    return bool(is_super_sum)
                
                try:
                    pet_id_int = int(pet_id)
                    if pet_id_int < 100000:
                        pet_id_int += 100000
                    return pet_id_int in SHENSHOU_ITYPES
                except (ValueError, TypeError):
                    return False
            
            def get_pet_battle_level(pet_id: str) -> int:
                """获取召唤兽战斗等级类型"""
                try:
                    pet_id_int = int(pet_id)
                    for pet_info in PET_BATTLE_LEVEL_TYPES:
                        id_to_check = pet_info[0] + 100000
                        if pet_id_int == id_to_check:
                            return pet_info[1]
                    return -1
                except (ValueError, TypeError):
                    return -1
            
            # 默认选项
            default_options = {
                'attrs': 'attack_ext,defence_ext,speed_ext,avoid_ext,physical_ext,magic_ext',
                'total_attrs': 'attack_aptitude,defence_aptitude,speed_aptitude,avoid_aptitude,physical_aptitude,magic_aptitude',
                'csavezz': '',
                'carrygradezz': -1,
                'pet_id': -1,
                'lastchecksubzz': 0
            }
            
            # 合并选项
            opts = {**default_options, **options}
            
            # 如果是神兽，直接返回
            if is_shenshou_pet(str(opts['pet_id']), opts.get('is_super_sum')):
                return
            
            attrs = opts['attrs'].split(',')
            total_attrs = opts['total_attrs'].split(',')
            csavezz = opts.get('csavezz', '')
            carrygradezz = opts.get('carrygradezz', -1)
            lastchecksubzz = opts.get('lastchecksubzz', 0)
            
            # 获取当前日期
            current_date = datetime.now()
            
            if not csavezz:
                return
            
            csavezz_list = csavezz.split('|')
            
            if carrygradezz < 0:
                carrygradezz = get_pet_battle_level(str(opts['pet_id']))
            
            if carrygradezz < 0:
                return
            
            # 资质上限配置 [攻击, 防御, 速度, 躲避, 体力, 法力]
            max_zz = [
                [1550, 1550, 1550, 1800, 5500, 3050],  # 等级0
                [1600, 1600, 1600, 2000, 6500, 3500],  # 等级1
                [1650, 1650, 1650, 2000, 7000, 3600]   # 等级2
            ]
            
            if carrygradezz >= len(max_zz):
                carrygradezz = 0
            
            zz = max_zz[carrygradezz]
            
            # 特殊召唤兽处理
            if data.get('pet_name', '').startswith('泡泡灵仙'):
                zz = [1770, 1900, 1650, 2000, 9700, 4800]
            
            # 处理每个资质
            for i, z in enumerate(zz):
                if i >= len(attrs) or i >= len(total_attrs):
                    continue
                
                ext_key = attrs[i]
                total_key = total_attrs[i]
                
                if total_key in data:
                    try:
                        total_value = int(data[total_key])
                        csave_value = int(csavezz_list[i]) if i < len(csavezz_list) and csavezz_list[i] else 0
                        
                        value = total_value - max(z, csave_value)
                        ext = int(max(value, 0))  # 确保ext是整数类型
                      
                        data[ext_key] = ext
                        
                        org_zz = total_value - ext
                        data[total_key] = org_zz
                        
                        # 如果有额外资质，处理衰减
                        if ext > 0:
                            year = lastchecksubzz or 2017
                            current_year = current_date.year
                            current_total_zz = org_zz + ext
                            
                            # 修复：使用与JavaScript端一致的循环逻辑
                            for y in range(current_year - year, 0, -1):
                                decay = int(math.floor(ext / 2))  # 确保decay是整数类型
                                current_total_zz = max(current_total_zz - decay, org_zz)
                                ext = int(current_total_zz - org_zz)  # 确保ext是整数类型

                                if ext <= 0:
                                    break
                            
                            down_ext_zz = data[ext_key] - ext
                            data[ext_key] = ext
                            
                            if down_ext_zz > 0:
                                self._fix_pet_decay_attr(data, i, down_ext_zz)
                    
                    except (ValueError, TypeError, IndexError):
                        continue
                        
        except Exception as e:
            logger.warning(f"处理召唤兽额外资质失败: {e}")
    
    def _fix_pet_decay_attr(self, pet: Dict[str, Any], attr_type: int, down_zz: int) -> None:
        """
        修复召唤兽衰减属性
        对应JavaScript版本的fix_pet_decay_attr函数
        """
        try:
            grade = int(pet.get('pet_grade', 0))
            # 修复growth字段处理，支持cheng_zhang字段
            growth = float(pet.get('growth') or pet.get('cheng_zhang', 0)) * 1000
            
            if math.isnan(grade) or math.isnan(growth) or grade <= 0 or growth <= 0:
                return
            
            def try_decay(keys, val):
                """尝试衰减属性"""
                if isinstance(keys, str):
                    keys = [keys]
                for key in keys:
                    if key in pet:
                        try:
                            current_val = int(pet[key])
                            new_val = max(current_val - val, 0) or 0  # 对应JavaScript的|| 0
                            pet[key] = new_val

                        except (ValueError, TypeError):
                            continue
            
            def fix_max(key, max_keys):
                """修正最大值"""
                if key in pet:
                    for mk in max_keys:
                        if mk in pet:
                            try:
                                pet[key] = min(int(pet[key]), int(pet[mk]))
                                return
                            except (ValueError, TypeError):
                                continue
            
            # 根据属性类型处理衰减
            if attr_type == 0:  # 攻击
                # 调试：打印attack衰减的详细计算过程
                decay_calc = down_zz * grade * 2 / 1000 * (700 + growth / 2) / 1000 * 4 / 3
                decay = math.ceil(decay_calc)

                try_decay('attack', decay)
            elif attr_type == 1:  # 防御
                decay = math.ceil(down_zz * grade * 7 / 4000 * (700 + growth / 2) / 1000)
                try_decay('defence', decay)
            elif attr_type == 2:  # 速度
                speed = pet.get('smartness') or pet.get('min_jie')
                if speed is not None:
                    try:
                        decay = math.ceil(down_zz * int(speed) / 1000)
                        try_decay('speed', decay)
                    except (ValueError, TypeError):
                        pass
            elif attr_type == 4:  # 体力
                decay = math.ceil(down_zz * grade / 1000)
                keys = ['max_blood', 'blood_max']
                try_decay(keys, decay)
                fix_max('blood', keys)
            elif attr_type == 5:  # 法力
                decay_mp = math.ceil(down_zz * grade / 500)
                mp_keys = ['max_magic', 'magic_max']
                try_decay(mp_keys, decay_mp)
                fix_max('magic', mp_keys)
                
                decay_lingli = math.ceil(down_zz * 3 / 10 * grade / 1000)
                try_decay(['wakan', 'ling_li'], decay_lingli)
                
        except Exception as e:
            logger.warning(f"修复召唤兽衰减属性失败: {e}")
    
    def _correct_pet_desc(self, pet_desc: str) -> str:
        """
        修正召唤兽描述格式
        对应JavaScript版本的correct_pet_desc函数
        """
        import re
        
        num_re = re.compile(r'^[0-9]*$')
        PET_ATTR_NUM = 33
        OLD_ATTR_NUM = 30
        OLDEST_ATTR_NUM = 29
        
        attr_num = len(pet_desc.split(';'))
        
        # 如果属性数量符合要求，直接返回
        if attr_num >= PET_ATTR_NUM or attr_num == OLD_ATTR_NUM or attr_num == OLDEST_ATTR_NUM:
            return pet_desc
        
        # 从末尾开始查找数字、分号和竖线
        new_desc = ""
        for i in range(len(pet_desc) - 1, 0, -1):
            ch = pet_desc[i]
            if ch not in [';', '|'] and not num_re.match(ch):
                break
            else:
                new_desc = ch + new_desc
        
        # 确保开头有分号
        if not new_desc.startswith(';'):
            new_desc = ';' + new_desc
        
        return '-' + new_desc
    
    def _parse_basic_attrs(self, attrs: List[str]) -> Dict[str, Any]:
        """解析基础属性"""
        def get_baobao_info(is_baobao: str) -> str:
            if is_baobao is None or is_baobao == '':
                return "未知"
            return "是" if int(is_baobao) else "否"
        
        # 确保attrs列表有足够的元素
        while len(attrs) < 35:
            attrs.append('')
        
        attrs_info = {
            'pet_name': attrs[0] if len(attrs) > 0 else '',
            'type_id': attrs[1] if len(attrs) > 1 else '',
            'pet_grade': attrs[2] if len(attrs) > 2 else '',
            'blood': attrs[3] if len(attrs) > 3 else '',
            'magic': attrs[4] if len(attrs) > 4 else '',
            'attack': int(attrs[5]) if len(attrs) > 5 and attrs[5] and attrs[5].isdigit() else 0,
            'defence': attrs[6] if len(attrs) > 6 else '',
            'speed': attrs[7] if len(attrs) > 7 else '',
            'soma': attrs[9] if len(attrs) > 9 else '',
            'magic_powner': attrs[10] if len(attrs) > 10 else '',
            'strength': attrs[11] if len(attrs) > 11 else '',
            'endurance': attrs[12] if len(attrs) > 12 else '',
            'smartness': attrs[13] if len(attrs) > 13 else '',
            'potential': attrs[14] if len(attrs) > 14 else '',
            'wakan': attrs[15] if len(attrs) > 15 else '',
            'max_blood': attrs[16] if len(attrs) > 16 else '',
            'max_magic': attrs[17] if len(attrs) > 17 else '',
            'lifetime': "永生" if len(attrs) <= 18 or not attrs[18] or not attrs[18].isdigit() or int(attrs[18]) >= 65432 else attrs[18],
            'five_aptitude': attrs[19] if len(attrs) > 19 else '',
            'attack_aptitude': attrs[20] if len(attrs) > 20 else '',
            'defence_aptitude': attrs[21] if len(attrs) > 21 else '',
            'physical_aptitude': attrs[22] if len(attrs) > 22 else '',
            'magic_aptitude': attrs[23] if len(attrs) > 23 else '',
            'speed_aptitude': attrs[24] if len(attrs) > 24 else '',
            'avoid_aptitude': attrs[25] if len(attrs) > 25 else '',
            'growth': float(attrs[26]) / 1000 if len(attrs) > 26 and attrs[26] and attrs[26].replace('.', '').isdigit() else 0,
            'all_skill': attrs[27] if len(attrs) > 27 else '',
            'sp_skill': attrs[28] if len(attrs) > 28 else '',
            'is_baobao': get_baobao_info(attrs[29] if len(attrs) > 29 else ''),
            'used_qianjinlu': attrs[32] if len(attrs) > 32 else '',
            'other': attrs[34] if len(attrs) > 34 else '',
        }
        
        return attrs_info
    
    def _parse_skills(self, attrs_info: Dict[str, Any]) -> Dict[str, Any]:
        """解析技能信息"""
        all_skills = attrs_info.get('all_skill', '').split('|') if attrs_info.get('all_skill') else []
        attrs_info['all_skill'] = '|'.join(all_skills)
        
        sp_skill_id = str(attrs_info.get('sp_skill', '0')).strip()
        if sp_skill_id != '0' and sp_skill_id not in all_skills:
            all_skills.append(sp_skill_id)
        
        attrs_info['sp_skill_id'] = sp_skill_id
        attrs_info['all_skills'] = all_skills
        
        return attrs_info
    
    def _parse_other_attrs(self, attrs_info: Dict[str, Any], fashang: Optional[int], fafang: Optional[int]) -> Dict[str, Any]:
        """解析其他属性，参考pet.js中的逻辑"""
        try:
            if attrs_info.get('other'):
                # 检查other是否已经是字典格式
                if isinstance(attrs_info['other'], dict):
                    other_attr = attrs_info['other']
                else:
                    # 尝试直接JSON解析（用于简单的JSON格式）
                    other_str = attrs_info['other']
                    if other_str.startswith('(') and other_str.endswith(')'):
                        try:
                            import json
                            json_str = other_str[1:-1]  # 去掉括号
                            other_attr = json.loads(json_str)
                        except json.JSONDecodeError:
                            # 如果JSON解析失败，尝试LPC解析
                            js_format = self.lpc_helper.lpc_to_js(attrs_info['other'], return_dict=False)
                            if js_format:
                                other_attr = self.lpc_helper.js_eval(js_format)
                            else:
                                other_attr = {}
                    else:
                        # 使用LPCHelper解析LPC格式的other数据
                        js_format = self.lpc_helper.lpc_to_js(attrs_info['other'], return_dict=False)
                        if js_format:
                            other_attr = self.lpc_helper.js_eval(js_format)
                        else:
                            other_attr = {}
                
                attrs_info['other'] = other_attr
                    
                # 处理进阶额外加点 - 参考pet.js第131-143行的逻辑
                jj_extra_add = other_attr.get("jj_extra_add")
                if jj_extra_add:
                    attrs_info["ti_zhi_add"] = jj_extra_add.get("iCor", 0)
                    attrs_info["fa_li_add"] = jj_extra_add.get("iMag", 0)
                    attrs_info["li_liang_add"] = jj_extra_add.get("iStr", 0)
                    attrs_info["nai_li_add"] = jj_extra_add.get("iRes", 0)
                    attrs_info["min_jie_add"] = jj_extra_add.get("iSpe", 0)
                    
                    # 从基础属性中减去进阶加点，获得真实的基础属性
                    try:
                        attrs_info['soma'] = int(attrs_info.get('soma', 0)) - attrs_info["ti_zhi_add"]
                        attrs_info['magic_powner'] = int(attrs_info.get('magic_powner', 0)) - attrs_info["fa_li_add"]
                        attrs_info['strength'] = int(attrs_info.get('strength', 0)) - attrs_info["li_liang_add"]
                        attrs_info['endurance'] = int(attrs_info.get('endurance', 0)) - attrs_info["nai_li_add"]
                        attrs_info['smartness'] = int(attrs_info.get('smartness', 0)) - attrs_info["min_jie_add"]
                    except (ValueError, TypeError) as e:
                        logger.warning(f"处理进阶加点时转换数值失败: {e}")
                else:
                    # 如果没有进阶加点，设置为0
                    attrs_info["ti_zhi_add"] = 0
                    attrs_info["fa_li_add"] = 0
                    attrs_info["li_liang_add"] = 0
                    attrs_info["nai_li_add"] = 0
                    attrs_info["min_jie_add"] = 0
                
                # 解析进阶信息 - 对应pet.js第196-208行的逻辑
                jinjie_info = other_attr.get("jinjie", {})
                attrs_info['jinjie'] = jinjie_info
                attrs_info["lx"] = jinjie_info.get("lx", 0)
                attrs_info["jinjie_cnt"] = jinjie_info.get("cnt", "0")
                attrs_info["texing"] = jinjie_info.get("core", {})
                
                # 处理召唤兽锦衣列表 - 参考pet.js第142-163行的逻辑
                if other_attr.get('avt_list') and isinstance(other_attr['avt_list'], list):
                    avt_list_result = self._parse_avt_list(other_attr)
                    other_attr['avt_list_format'] = avt_list_result.get('avt_list_format', [])
                    other_attr['current_on_avt'] = avt_list_result.get('current_on_avt')

                if "core_close" in other_attr:
                    attrs_info["core_close"] = "已开启" if other_attr["core_close"] == 0 else "已关闭"
                
                # 处理召唤兽额外资质 - 参考pet.js第171-181行的逻辑
                if other_attr.get('csavezz'):
                    self._get_pet_ext_zz(attrs_info, {
                        'attrs': 'attack_ext,defence_ext,speed_ext,avoid_ext,physical_ext,magic_ext',
                        'total_attrs': 'attack_aptitude,defence_aptitude,speed_aptitude,avoid_aptitude,physical_aptitude,magic_aptitude',
                        'csavezz': other_attr.get('csavezz'),
                        'carrygradezz': other_attr.get('carrygradezz'),
                        'lastchecksubzz': other_attr.get('lastchecksubzz'),
                        'pet_id': attrs_info.get('type_id', ''),
                        'is_super_sum': other_attr.get('is_super_sum')
                    })
                else:
                    # 如果没有csavezz，设置默认的扩展属性值
                    attrs_info['attack_ext'] = 0
                    attrs_info['defence_ext'] = 0
                    attrs_info['speed_ext'] = 0
                    attrs_info['avoid_ext'] = 0
                    attrs_info['physical_ext'] = 0
                    attrs_info['magic_ext'] = 0

       
                
                # 解析内丹信息
                attrs_info['neidan'] = self._parse_neidan(other_attr)
                
                # 解析装备信息
                attrs_info['equip_list'] = self._parse_pet_equips(other_attr)
                
                # 解析进化技能
                attrs_info['evol_skill_list'] = self._parse_evol_skill_list(other_attr, attrs_info)
                
                # 解析颜色信息
                attrs_info['color'] = other_attr.get('iColor')
                attrs_info['summon_color'] = other_attr.get('summon_color')

                 # 解析法伤法防 - 参考pet.js第200-206行的逻辑
                attrs_info['iMagDam'] = other_attr.get('iMagDam')
                attrs_info['iMagDef'] = other_attr.get('iMagDef')
                
                # 如果法伤法防为None且传入了fashang和fafang参数
                if (attrs_info['iMagDam'] is None and attrs_info['iMagDef'] is None and 
                    fashang and fafang and isinstance(fashang, (int, float)) and isinstance(fafang, (int, float))):
                    attrs_info['iMagDam'] = fashang
                    attrs_info['iMagDef'] = fafang
                
                # 解析神机阁使用情况 - 对应pet.js第208行的逻辑
                attrs_info["used_sjg"] = self._get_sjg(other_attr.get("sjg", "0"))
                
        except Exception as e:
            logger.warning(f"解析其他属性失败: {e}")
            attrs_info['neidan'] = []
            # 设置默认值
            attrs_info['evol_skill_list'] = []
            attrs_info['evol_skills'] = []
            attrs_info['equip_list'] = [None, None, None, None]
            attrs_info['used_sjg'] = '0'
            attrs_info['attack_ext'] = 0
            attrs_info['defence_ext'] = 0
            attrs_info['speed_ext'] = 0
            attrs_info['avoid_ext'] = 0
            attrs_info['physical_ext'] = 0
            attrs_info['magic_ext'] = 0
        
        return attrs_info
    
    def _parse_neidan(self, other_attr: Dict) -> List[Dict]:
        """解析内丹信息，完全按照JS版本的逻辑"""
        neidan_list = []
        try:
            # 从summon_core字段获取内丹数据，对应JS版本的pet.summon_core
            neidan_data = other_attr.get('summon_core')
            
            if neidan_data and isinstance(neidan_data, dict):
                # 按照内丹ID的数字顺序排序，确保与JS版本一致
                sorted_neidan_ids = sorted(neidan_data.keys(), key=lambda x: int(x) if x.isdigit() else 0)
                
                # 遍历内丹数据，对应JS版本的for (var p in neidan_data)
                for neidan_id in sorted_neidan_ids:
                    neidan_info = neidan_data[neidan_id]
                    if isinstance(neidan_info, list) and len(neidan_info) >= 1:
                        level = neidan_info[0] if isinstance(neidan_info[0], (int, float)) else 0
                        
                        # 获取内丹名称，对应JS版本的PetNeidanInfo[p]
                        neidan_name = self._get_neidan_name(neidan_id)
                        
                        # 获取内丹描述，对应JS版本的CBG_GAME_CONFIG.neidan_desc[p]
                        desc = self._get_neidan_desc(neidan_id)
                        
                        neidan_list.append({
                            'name': neidan_name,
                            'icon': f"https://cbg-xyq.res.netease.com/images/neidan/{neidan_id}.jpg",
                            'level': int(level),
                            'desc': desc,
                            'isNeiDan': True
                        })
            
            # 如果没有summon_core字段，尝试从neidan字段获取（兼容性处理）
            elif 'neidan' in other_attr and isinstance(other_attr['neidan'], list):
                for neidan in other_attr['neidan']:
                    if isinstance(neidan, dict):
                        neidan_list.append({
                            'name': neidan.get('name', ''),
                            'level': neidan.get('level', 0),
                            'desc': neidan.get('desc', ''),
                            'icon': neidan.get('icon', ''),
                            'isNeiDan': neidan.get('isNeiDan', True)
                        })
                        
        except Exception as e:
            logger.warning(f"解析内丹失败: {e}")
        
        return neidan_list
    
    def _get_neidan_name(self, neidan_id: str) -> str:
        """获取内丹名称，对应JS版本的PetNeidanInfo[p]"""
        try:
            from parser.config_loader import get_config_loader
            config_loader = get_config_loader()
            pet_neidan_config = config_loader.get_pet_neidan_config()
            
            neidan_info = pet_neidan_config.get(str(neidan_id), {})
            if isinstance(neidan_info, dict):
                return neidan_info.get('name', f'内丹{neidan_id}')
            elif isinstance(neidan_info, str):
                return neidan_info
            else:
                return f'内丹{neidan_id}'
        except Exception as e:
            logger.warning(f"获取内丹名称失败: {e}")
            return f'内丹{neidan_id}'
    
    def _get_neidan_desc(self, neidan_id: str) -> str:
        """获取内丹描述，对应JS版本的CBG_GAME_CONFIG.neidan_desc[p]"""
        try:
            from parser.config_loader import get_config_loader
            config_loader = get_config_loader()
            full_config = config_loader._load_full_config()
            
            neidan_desc_config = full_config.get('neidan_desc', {})
            skill_config = neidan_desc_config.get(str(neidan_id), {})
            
            if isinstance(skill_config, dict):
                return skill_config.get('desc', '')
            else:
                return ''
        except Exception as e:
            logger.warning(f"获取内丹描述失败: {e}")
            return ''
    
    def _parse_pet_equips(self, other_attr: Dict) -> List[Dict]:
        """解析召唤兽装备信息，确保与JS版本一致"""
        equip_list = []
        
        try:
            # 前3个装备位置：从 summon_equip1, summon_equip2, summon_equip3 获取
            max_equip_num = 3
            img_dir = "https://cbg-xyq.res.netease.com/images/equip/small/"
            
            for i in range(max_equip_num):
                equip_key = f"summon_equip{i + 1}"
                item = other_attr.get(equip_key)
                
                if item and isinstance(item, dict):
                    equip_type = item.get("iType")
                    equip_desc = item.get("cDesc", "")
                    
                    # 获取装备名称和静态描述
                    equip_name_info = self._get_equip_info(equip_type)
                    equip_name = equip_name_info.get("name", f"装备{equip_type}")
                    static_desc = equip_name_info.get("desc", "").replace("#R", "<br />")
                    
                    equip_list.append({
                        "name": equip_name,
                        "icon": f"{img_dir}{equip_type}.gif",
                        "type": equip_type,
                        "desc": equip_desc,
                        "static_desc": static_desc
                    })
                else:
                    equip_list.append(None)
            
            # 第4个装备位置：召唤兽饰品，从 summon_equip4_type 获取
            # 只有当 summon_equip4_type 存在时才添加第4个装备
            if other_attr.get('summon_equip4_type'):
                equip_type = other_attr['summon_equip4_type']
                equip_desc = other_attr.get('summon_equip4_desc', '')
                
                # 获取召唤兽饰品名称
                equip_name = self._get_pet_shipin_info(equip_type)
                
                # 无论饰品名称是否存在，都添加第4个装备，与JavaScript版本保持一致
                equip_list.append({
                    "name": equip_name,  # 如果配置中不存在，equip_name为None
                    "icon": f"https://cbg-xyq.res.netease.com/images/pet_shipin/small/{equip_type}.png",
                    "type": equip_type,
                    "desc": equip_desc,
                    "static_desc": ''
                })
                
        except Exception as e:
            logger.warning(f"解析召唤兽装备失败: {e}")
            # 返回3个None
            equip_list = [None, None, None]
            
        return equip_list
    
    def _get_equip_info(self, equip_type: int) -> Dict[str, str]:
        """获取装备信息，对应JS版本的RoleNameInfo.get_equip_info"""
        try:
            from parser.config_loader import get_config_loader
            config_loader = get_config_loader()
            full_config = config_loader._load_full_config()
            
            # 直接从完整配置中获取equip_info
            equip_info = full_config.get('equip_info', {}).get(str(equip_type), {})
            
            if isinstance(equip_info, dict):
                name = equip_info.get("name", f"装备{equip_type}")
                desc = equip_info.get("desc", "")
                # 替换#R为<br />
                desc = desc.replace("#R", "<br />")
            else:
                name = str(equip_info) if equip_info else f"装备{equip_type}"
                desc = ""
            
            return {
                "name": name,
                "desc": desc
            }
        except Exception as e:
            logger.warning(f"获取装备信息失败: {e}")
            return {
                "name": f"装备{equip_type}",
                "desc": ""
            }
    
    def _get_pet_shipin_info(self, equip_type: int) -> str:
        """获取召唤兽饰品信息，对应JS版本的RoleNameInfo.pet_shipin_info"""
        try:
            from parser.config_loader import get_config_loader
            config_loader = get_config_loader()
            pet_shipin_config = config_loader.get_pet_shipin_config()
            
            # 如果配置中不存在该ID，返回None，表示不添加该装备
            return pet_shipin_config.get(str(equip_type))
        except Exception as e:
            logger.warning(f"获取召唤兽饰品信息失败: {e}")
            return None
    
    def _parse_evol_skill_list(self, other_attr: Dict, attrs_info: Dict) -> List[Dict]:
        """解析进化技能列表，确保与JS版本完全一致"""
        evol_skill_list = []
        try:
            if 'EvolSkill' in other_attr:
                # 加载技能映射配置
                try:
                    from parser.config_loader import get_config_loader
                    config_loader = get_config_loader()
                    full_config = config_loader._load_full_config()
                    skill_desc_config = full_config.get('pet_skill_desc', {})
                    skill_mapping_config = full_config.get('pet_skill_high_to_other_level_mapping', {})
                except Exception as e:
                    logger.warning(f"获取技能配置失败: {e}")
                    skill_desc_config = {}
                    skill_mapping_config = {}
                
                # 获取进化技能ID列表并排序，确保与JS版本一致
                evol_skill_ids = [int(s) for s in other_attr['EvolSkill'].split('|') if s.strip()]
                evol_skill_ids.sort()  # 按数字排序，对应JS版本的排序逻辑
                
                all_skills = [str(s) for s in attrs_info.get('all_skills', [])]
                
                for orig_id in evol_skill_ids:
                    orig_id_str = str(orig_id)
                    evol_skill_hash = skill_mapping_config.get(orig_id_str, {})
                    
                    # 获取映射的技能ID
                    low_skill = str(evol_skill_hash.get('low_skill', ''))
                    high_skill = str(evol_skill_hash.get('high_skill', ''))
                    super_skill = str(evol_skill_hash.get('super_skill', ''))
                    
                    # 确定排序ID和图标ID，对应JS版本的逻辑
                    sort_id = low_skill or high_skill or orig_id_str
                    icon_id = orig_id_str  # 使用原始ID作为图标ID
                    evol_type = orig_id_str  # 使用原始ID作为evol_type
                    
                    # 初始化字段
                    name = ''
                    desc = ''
                    cifuIcon = ''
                    heightCifuIcon = ''
                    hlightLight = False
                    
                    # 首先设置基础名称和描述（对应JS版本的初始设置）
                    if skill_desc_config.get(orig_id_str):
                        skill_config = skill_desc_config[orig_id_str]
                        if isinstance(skill_config, dict):
                            name = skill_config.get('name', '')
                            desc = skill_config.get('desc', '')
                    
                    # 检查技能是否已拥有
                    is_high_skill = high_skill and high_skill in all_skills
                    is_low_skill = low_skill and low_skill in all_skills
                    
                    # 描述和图标逻辑
                    if is_high_skill or is_low_skill:
                        hlightLight = True
                        
                        if not is_high_skill and low_skill:
                            icon_id = low_skill
                            evol_type = low_skill
                        
                        if is_high_skill:
                            # 高级技能：使用evol_skill_hash.name + （进化后获得）
                            name = (evol_skill_hash.get('name', '') or '') + '（进化后获得）'
                            # 使用super_skill的描述
                            if super_skill and skill_desc_config.get(super_skill):
                                super_skill_config = skill_desc_config[super_skill]
                                if isinstance(super_skill_config, dict):
                                    desc = super_skill_config.get('desc', '')
                            # 设置super_skill的图标
                            if super_skill:
                                cifuIcon = f"https://cbg-xyq.res.netease.com/images/skill/{super_skill.zfill(5)}.gif"
                        else:
                            # 低级技能：在原有名称后添加（进化后获得）
                            name += '（进化后获得）'
                            # 设置high_skill的图标
                            if high_skill:
                                heightCifuIcon = f"https://cbg-xyq.res.netease.com/images/skill/{high_skill.zfill(4)}.gif"
                    else:
                        # 既没有高级技能也没有低级技能
                        # 使用evol_skill_hash.name + （进化后获得）
                        name = (evol_skill_hash.get('name', '') or '') + '（进化后获得）'
                        # 使用super_skill的描述
                        if super_skill and skill_desc_config.get(super_skill):
                            super_skill_config = skill_desc_config[super_skill]
                            if isinstance(super_skill_config, dict):
                                desc = super_skill_config.get('desc', '')
                        # 设置super_skill的图标
                        if super_skill:
                            cifuIcon = f"https://cbg-xyq.res.netease.com/images/skill/{super_skill.zfill(5)}.gif"
                        hlightLight = False
                    
                    # 构建技能对象
                    icon = f"https://cbg-xyq.res.netease.com/images/skill/{str(icon_id).zfill(4)}.gif"
                    skill_obj = {
                        'skill_type': orig_id_str,
                        'level': 1,
                        'icon': icon,
                        'evol_type': evol_type,
                        'name': name,
                        'desc': desc,
                        'cifuIcon': cifuIcon,
                        'hlightLight': hlightLight
                    }
                    
                    if heightCifuIcon:
                        skill_obj['heightCifuIcon'] = heightCifuIcon
                    
                    evol_skill_list.append(skill_obj)
                
                # evol_skills 顺序与 evol_skill_list 保持一致
                attrs_info['evol_skills'] = [item['skill_type'] for item in evol_skill_list]
                
        except Exception as e:
            logger.warning(f"解析进化技能失败: {e}")
        
        return evol_skill_list
    
    def _parse_evol_skills(self, other_attr: Dict) -> List[str]:
        """解析进化技能ID列表"""
        evol_skills = []
        try:
            if 'EvolSkill' in other_attr:
                evol_skills = other_attr['EvolSkill'].split('|')
        except Exception as e:
            logger.warning(f"解析进化技能ID失败: {e}")
        return evol_skills
    
    def _parse_avt_list(self, other_attr: Dict) -> Dict[str, Any]:
        """
        解析召唤兽锦衣列表
        对应JavaScript版本第142-163行的逻辑
        
        Args:
            other_attr: 其他属性字典
            
        Returns:
            包含锦衣列表信息的字典
        """
        try:
            if not other_attr.get('avt_list') or not isinstance(other_attr['avt_list'], list):
                return {
                    'avt_list_format': [],
                    'current_on_avt': None
                }
            
            avt_list = other_attr['avt_list']
            avt_list_format = []
            
            # 获取游戏配置
            pet_jinyi_config = self._get_pet_jinyi_config()
            sumavt_propsk_config = self._get_sumavt_propsk_config()
            
            # 获取当前装备的锦衣索引
            current_on_avt_index = other_attr.get('current_on_avt')
            if current_on_avt_index is not None:
                try:
                    current_on_avt_index = int(current_on_avt_index)
                except (ValueError, TypeError):
                    current_on_avt_index = None
            
            for i, item in enumerate(avt_list):
                if isinstance(item, dict):
                    # 直接修改原始项目（模拟JavaScript行为）
                    item_type = str(item.get('type'))
                    
                    # 给所有锦衣添加名称（如果没有的话）
                    if item_type and not item.get('name'):
                        if pet_jinyi_config.get(item_type):
                            jinyi_config = pet_jinyi_config[item_type]
                            if isinstance(jinyi_config, dict) and jinyi_config.get('name'):
                                item['name'] = jinyi_config['name']
                            else:
                                # 如果配置格式不正确，设置默认名称
                                item['name'] = f"锦衣_{item_type}"
                        else:
                            # 如果配置中没有这个类型，设置默认名称
                            item['name'] = f"未知锦衣_{item_type}"
                    
                    # 判断是否为当前装备的锦衣
                    # 检查两种情况：1) current_on_avt索引匹配，2) 已有in_use字段
                    is_current_by_index = (current_on_avt_index is not None and i == current_on_avt_index)
                    is_current_by_flag = item.get('in_use')
                    
                    if is_current_by_index or is_current_by_flag:
                        item['in_use'] = True
                        
                        # 处理属性技能信息（只对当前装备的锦衣处理，匹配JavaScript逻辑）
                        # JavaScript版本：item.sumavt_propsk = other_attr['sumavt_propsk']
                        global_sumavt_propsk = other_attr.get('sumavt_propsk')
                        
                        # 优先使用全局的sumavt_propsk，如果没有则使用item自己的
                        source_sumavt_propsk = global_sumavt_propsk if global_sumavt_propsk is not None else item.get('sumavt_propsk')
                        
                        if source_sumavt_propsk is not None:
                            # 转换为字符串以便统一处理
                            sumavt_propsk_str = str(source_sumavt_propsk)
                            
                            # 如果已经是中文标签，则保持不变
                            if sumavt_propsk_str in ['体质', '力量', '法力', '耐力', '敏捷']:
                                item['sumavt_propsk'] = sumavt_propsk_str
                            else:
                                # 数字到英文键的映射
                                propsk_mapping = {
                                    '3': 'iCor_Avt_Inc',  # 体质
                                    '1': 'iStr_Avt_Inc',  # 力量
                                    '2': 'iMag_Avt_Inc',  # 法力
                                    '4': 'iRes_Avt_Inc',  # 耐力
                                    '5': 'iSpe_Avt_Inc',  # 敏捷
                                }
                                
                                # 先尝试映射到英文键，然后查找配置
                                english_key = propsk_mapping.get(sumavt_propsk_str, sumavt_propsk_str)
                                if sumavt_propsk_config.get(english_key):
                                    item['sumavt_propsk'] = sumavt_propsk_config[english_key].get('label', source_sumavt_propsk)
                                else:
                                    # 如果没有找到配置，设置为空字符串（匹配JavaScript逻辑）
                                    item['sumavt_propsk'] = ''
                        else:
                            # 如果没有sumavt_propsk信息，设置为空字符串（匹配JavaScript逻辑）
                            item['sumavt_propsk'] = ''
                    
                    avt_list_format.append(item)
            
            # 找到当前正在使用的锦衣
            current_on_avt = None
            for item in avt_list_format:
                if item.get('in_use'):
                    current_on_avt = item
                    break
            
            return {
                'avt_list_format': avt_list_format,
                'current_on_avt': current_on_avt
            }
            
        except Exception as e:
            logger.warning(f"解析召唤兽锦衣列表失败: {e}")
            return {
                'avt_list_format': [],
                'current_on_avt': None
            }
    
    def _get_pet_jinyi_config(self) -> Dict[str, Any]:
        """
        获取召唤兽锦衣配置
        对应JavaScript中的window.CBG_GAME_CONFIG.pet_jinyi
        
        Returns:
            召唤兽锦衣配置字典
        """
        try:
            from parser.config_loader import get_config_loader
            config_loader = get_config_loader()
            full_config = config_loader._load_full_config()
            pet_jinyi_config = full_config.get('pet_jinyi', {})
            
            # 确保配置正确加载
            if not pet_jinyi_config:
                # 如果配置为空，记录警告但不影响程序运行
                pass
                
            return pet_jinyi_config if isinstance(pet_jinyi_config, dict) else {}
        except Exception as e:
            # 静默处理配置加载异常，返回空配置
            # 这样不会影响程序运行，只是锦衣名称会使用默认值
            try:
                logger.warning(f"获取召唤兽锦衣配置失败: {e}")
            except:
                # 如果logger也有问题，静默处理
                pass
            return {}
    
    def _get_sumavt_propsk_config(self) -> Dict[str, Any]:
        """
        获取锦衣属性技能配置
        对应JavaScript中的window.CBG_GAME_CONFIG.sumavt_propsk
        
        Returns:
            锦衣属性技能配置字典
        """
        try:
            # 使用config_loader加载配置
            from parser.config_loader import get_config_loader
            config_loader = get_config_loader()
            
            # 获取完整配置
            full_config = config_loader._load_full_config()
            
            # 从配置中获取锦衣属性技能配置
            sumavt_propsk_config = full_config.get('sumavt_propsk', {})
            
            # 如果没有找到配置，尝试其他可能的配置键
            if not sumavt_propsk_config:
                # 尝试其他可能的配置键名
                possible_keys = ['pet_avt_propsk', 'avt_propsk', 'pet_clothes_propsk']
                for key in possible_keys:
                    if key in full_config:
                        sumavt_propsk_config = full_config[key]
                        break
            
            # 确保返回的配置格式正确
            if isinstance(sumavt_propsk_config, dict):
                # 转换为label格式
                formatted_config = {}
                for prop_id, prop_data in sumavt_propsk_config.items():
                    if isinstance(prop_data, dict):
                        formatted_config[str(prop_id)] = {
                            'label': prop_data.get('label', prop_data.get('name', '')),
                            'desc': prop_data.get('desc', '')
                        }
                    elif isinstance(prop_data, str):
                        formatted_config[str(prop_id)] = {
                            'label': prop_data,
                            'desc': ''
                        }
                return formatted_config
            
            return {}
            
        except Exception as e:
            logger.warning(f"获取锦衣属性技能配置失败: {e}")
            return {}
    
    def _parse_extra_info(self, attrs_info: Dict[str, Any], attrs: List[str]) -> Dict[str, Any]:
        """解析额外信息"""
        # 解析元宵使用情况
        attrs_info['used_yuanxiao'] = self._get_yuanxiao(attrs[30] if len(attrs) > 30 else '')
        
        # 解析炼兽珍经使用情况
        attrs_info['used_lianshou'] = self._get_lianshou(attrs[33] if len(attrs) > 33 else '')
        
        return attrs_info
    
    def _get_yuanxiao(self, input_value: str) -> int:
        """获取元宵使用情况，对应JS版本的get_yuanxiao函数"""
        try:
            if not input_value or input_value == '0':
                return 0
            
            # JS版本使用EquipRequestTime和ServerCurrentTime进行时间判断
            # 由于我们没有这些变量，返回0以匹配JS版本的行为
            return 0
        except (ValueError, TypeError):
            return 0
    
    def _get_lianshou(self, input_value: str) -> int:
        """获取炼兽珍经使用情况，对应JS版本的get_lianshou函数"""
        try:
            if not input_value or input_value == '0':
                return 0
            
            # JS版本使用EquipRequestTime和ServerCurrentTime进行时间判断
            # 由于我们没有这些变量，返回0以匹配JS版本的行为
            return 0
        except (ValueError, TypeError):
            return 0

    def _get_sjg(self, input_value: str) -> int:
        """获取神机阁使用情况，对应JS版本的get_sjg函数（与get_yuanxiao相同）"""
        try:
            if not input_value or input_value == '0':
                return 0
            
            # JS版本使用EquipRequestTime和ServerCurrentTime进行时间判断
            # 由于我们没有这些变量，返回0以匹配JS版本的行为
            return 0
        except (ValueError, TypeError):
            return 0


def parse_pet_info(desc: str) -> Dict[str, Any]:
    """
    解析召唤兽信息的统一接口
    对应JavaScript版本的parsePetInfo函数
    
    Args:
        desc: 召唤兽描述信息
        
    Returns:
        解析后的召唤兽属性信息
    """
    parser = PetInfoParser()
    
    # 解析描述信息
    pet_desc = parser.parse_desc_info(desc)
    
    # 解析法伤法防
    linli_data = parser.parse_fashang_fafang(desc)
    
    # 获取召唤兽属性信息
    pet_attrs = parser.get_pet_attrs_info(pet_desc, {
        'only_basic_attr': False,
        'fashang': linli_data.get('fashang'),
        'fafang': linli_data.get('fafang')
    })
    
    return pet_attrs
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统API蓝图
"""

from flask import Blueprint, send_file, request, jsonify, Response, current_app
from ....controllers.system_controller import SystemController
from ....utils.response import success_response, error_response
import os
import json
import logging
import time

# 添加src目录到Python路径
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # 向上三级到src目录
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from src.utils.project_path import get_relative_path, get_config_path
except ImportError:
    # 如果无法导入，直接使用相对路径计算
    def get_relative_path(path):
        return os.path.join(src_path, path)
    
    def get_config_path():
        return os.path.join(src_path, 'config')

# 获取logger
logger = logging.getLogger(__name__)

system_bp = Blueprint('system', __name__)
controller = SystemController()


@system_bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        info = controller.get_system_info()
        return success_response(data=info)
    except Exception as e:
        return error_response(f"获取系统信息失败: {str(e)}")


@system_bp.route('/files', methods=['GET'])
def list_files():
    """列出输出文件"""
    try:
        files = controller.list_output_files()
        return success_response(data=files)
    except Exception as e:
        return error_response(f"获取文件列表失败: {str(e)}")


@system_bp.route('/files/<filename>/download', methods=['GET'])
def download_file(filename):
    """下载文件"""
    try:
        file_path = controller.get_file_path(filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return error_response("文件不存在", code=404, http_code=404)
    except Exception as e:
        return error_response(f"下载失败: {str(e)}", http_code=500)


@system_bp.route('/config-file/<filename>', methods=['GET'])
def get_config_file(filename):
    """获取配置文件内容"""
    try:
        # 使用项目路径工具获取配置文件路径
        config_path = get_relative_path(f'src/constant/{filename}')
        
        if not os.path.exists(config_path):
            return "配置文件不存在", 404
        
        with open(config_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        # 将jsonc需要去除注释
        # 简单处理JSONC注释（移除//注释）
        lines = js_content.split('\n')
        cleaned_lines = []
        for line in lines:
            # 移除行内注释
            if '//' in line:
                line = line[:line.index('//')]
            cleaned_lines.append(line)
        
        js_content = '\n'.join(cleaned_lines)
        # 直接返回文件内容
        return Response(js_content, mimetype='text/plain')
        
    except Exception as e:
        return f"获取配置失败: {str(e)}", 500


@system_bp.route('/config/search-params', methods=['GET'])
def get_search_params():
    """
    获取搜索参数配置
    
    Returns:
        JSON: 包含所有搜索参数配置的响应
    """
    try:
        config_dir = get_config_path()
        
        # 定义需要读取的配置文件
        config_files = {
            'equip_params_normal': 'equip_params_normal.json',
            'equip_params_lingshi': 'equip_params_lingshi.json',
            'equip_params_pet': 'equip_params_pet.json',
            'equip_params_pet_equip': 'equip_params_pet_equip.json'
        }
        
        result = {}
        
        for key, filename in config_files.items():
            file_path = os.path.join(config_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        result[key] = content
                except json.JSONDecodeError as e:
                    logger.error(f"解析配置文件 {filename} 失败: {e}")
                    result[key] = {"error": f"JSON解析失败: {str(e)}"}
                except Exception as e:
                    logger.error(f"读取配置文件 {filename} 失败: {e}")
                    result[key] = {"error": f"文件读取失败: {str(e)}"}
            else:
                logger.warning(f"配置文件不存在: {filename}")
                result[key] = {"error": "文件不存在"}
        
        # 处理角色搜索参数（从search_params目录读取）
        role_params = {}
        if os.path.exists(config_dir):
            try:
                # 读取109等级的配置作为默认角色配置
                role_file = os.path.join(config_dir, '109.json')
                if os.path.exists(role_file):
                    with open(role_file, 'r', encoding='utf-8') as f:
                        role_params = json.load(f)
                else:
                    # 如果没有109.json，读取第一个可用的文件
                    for filename in os.listdir(config_dir):
                        if filename.endswith('.json'):
                            role_file = os.path.join(config_dir, filename)
                            with open(role_file, 'r', encoding='utf-8') as f:
                                role_params = json.load(f)
                            break
            except Exception as e:
                logger.error(f"读取角色搜索参数失败: {e}")
        
        # 处理召唤兽搜索参数（使用equip_params_pet作为基础）
        pet_params = result.get('equip_params_pet', {})
        
        # 构建前端需要的格式
        frontend_params = {
            "role": role_params,
            "equip_normal": result.get('equip_params_normal', {}),
            "equip_lingshi": result.get('equip_params_lingshi', {}),
            "equip_pet": result.get('equip_params_pet', {}),
            "equip_pet_equip": result.get('equip_params_pet_equip', {}),
            "pet": pet_params
        }
        
        return success_response(data=frontend_params, message="获取搜索参数配置成功")
        
    except Exception as e:
        logger.error(f"获取搜索参数配置失败: {e}")
        return error_response(f"获取搜索参数配置失败: {str(e)}")


@system_bp.route('/config/search-params/<param_type>', methods=['GET'])
def get_search_param_by_type(param_type: str):
    """
    根据类型获取特定的搜索参数配置
    
    Args:
        param_type: 参数类型 (role, equip_normal, equip_lingshi, equip_pet, equip_pet_equip, pet)
    
    Returns:
        JSON: 包含特定搜索参数配置的响应
    """
    try:
        config_dir = get_config_path()
        
        # 参数类型到文件名的映射
        type_to_file = {
            'equip_normal': 'equip_params_normal.json',
            'equip_lingshi': 'equip_params_lingshi.json',
            'equip_pet': 'equip_params_pet.json',
            'equip_pet_equip': 'equip_params_pet_equip.json'
        }
        
        # 特殊处理角色和召唤兽参数
        if param_type == 'role':
            if os.path.exists(config_dir):
                try:
                    # 读取109等级的配置作为默认角色配置
                    role_file = os.path.join(config_dir, '109.json')
                    if os.path.exists(role_file):
                        with open(role_file, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            return success_response(data=content, message=f"获取{param_type}参数配置成功")
                    else:
                        return error_response("角色配置文件不存在")
                except Exception as e:
                    logger.error(f"读取角色配置文件失败: {e}")
                    return error_response(f"文件读取失败: {str(e)}")
            else:
                return error_response("角色配置目录不存在")
        elif param_type == 'pet':
            # 召唤兽参数使用equip_params_pet
            filename = 'equip_params_pet.json'
            file_path = os.path.join(config_dir, filename)
        elif param_type not in type_to_file:
            return error_response(f"不支持的参数类型: {param_type}")
        else:
            filename = type_to_file[param_type]
            file_path = os.path.join(config_dir, filename)
        
        if not os.path.exists(file_path):
            return error_response(f"配置文件不存在: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return success_response(data=content, message=f"获取{param_type}参数配置成功")
        except json.JSONDecodeError as e:
            logger.error(f"解析配置文件 {filename} 失败: {e}")
            return error_response(f"JSON解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"读取配置文件 {filename} 失败: {e}")
            return error_response(f"文件读取失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"获取{param_type}参数配置失败: {e}")
        return error_response(f"获取{param_type}参数配置失败: {str(e)}")


@system_bp.route('/config/search-params/<param_type>', methods=['POST'])
def update_search_param(param_type: str):
    """
    更新特定类型的搜索参数配置
    
    Args:
        param_type: 参数类型
    
    Returns:
        JSON: 更新结果
    """
    try:
        config_dir = get_config_path()
        
        # 参数类型到文件名的映射
        type_to_file = {
            'equip_normal': 'equip_params_normal.json',
            'equip_lingshi': 'equip_params_lingshi.json',
            'equip_pet': 'equip_params_pet.json',
            'equip_pet_equip': 'equip_params_pet_equip.json'
        }
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return error_response("请提供要更新的参数数据")
        
        # 特殊处理角色和召唤兽参数
        if param_type == 'role':
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            filename = '109.json'
            file_path = os.path.join(config_dir, filename)
        elif param_type == 'pet':
            # 召唤兽参数使用equip_params_pet
            filename = 'equip_params_pet.json'
            file_path = os.path.join(config_dir, filename)
        elif param_type not in type_to_file:
            return error_response(f"不支持的参数类型: {param_type}")
        else:
            filename = type_to_file[param_type]
            file_path = os.path.join(config_dir, filename)
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 写入文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功更新{param_type}参数配置")
            return success_response(message=f"更新{param_type}参数配置成功")
            
        except Exception as e:
            logger.error(f"写入配置文件 {filename} 失败: {e}")
            return error_response(f"文件写入失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"更新{param_type}参数配置失败: {e}")
        return error_response(f"更新{param_type}参数配置失败: {str(e)}") 
    
@system_bp.route('/market-data/status', methods=['GET'])
def get_market_data_status():
    """获取市场数据状态"""
    try:
        from src.evaluator.market_data_collector import MarketDataCollector
        
        # 获取市场数据收集器实例
        collector = MarketDataCollector()
        
        # 获取MySQL数据总数
        mysql_count = collector._get_empty_roles_count()
        
        # 获取基本状态信息
        status_info = {
            "data_loaded": collector._data_loaded,
            "last_refresh_time": collector._last_refresh_time.isoformat() if collector._last_refresh_time else None,
            "cache_expiry_hours": collector._cache_expiry_hours,
            "data_count": len(collector.market_data) if not collector.market_data.empty else 0,
            "data_columns": list(collector.market_data.columns) if not collector.market_data.empty else [],
            "memory_usage_mb": collector.market_data.memory_usage(deep=True).sum() / 1024 / 1024 if not collector.market_data.empty else 0,
            "mysql_data_count": mysql_count
        }
        
        # 添加刷新进度信息
        refresh_status = collector.get_refresh_status()
        status_info.update({
            "refresh_status": refresh_status["status"],
            "refresh_progress": refresh_status["progress"],
            "refresh_message": refresh_status["message"],
            "refresh_processed_records": refresh_status["processed_records"],
            "refresh_total_records": refresh_status["total_records"],
            "refresh_current_batch": refresh_status["current_batch"],
            "refresh_total_batches": refresh_status["total_batches"],
            "refresh_start_time": refresh_status["start_time"],
            "refresh_elapsed_seconds": refresh_status["elapsed_seconds"]
        })
        
        # 如果有数据，添加数据统计信息
        if not collector.market_data.empty:
            try:
                # 价格统计
                price_stats = {
                    "min_price": float(collector.market_data['price'].min()),
                    "max_price": float(collector.market_data['price'].max()),
                    "avg_price": float(collector.market_data['price'].mean()),
                    "median_price": float(collector.market_data['price'].median())
                }
                status_info["price_statistics"] = price_stats
                
                # 角色类型分布
                if 'role_type' in collector.market_data.columns:
                    role_type_counts = collector.market_data['role_type'].value_counts().to_dict()
                    status_info["role_type_distribution"] = role_type_counts
                
                # 等级分布（如果存在level字段）
                level_fields = [col for col in collector.market_data.columns if 'level' in col.lower()]
                if level_fields:
                    level_field = level_fields[0]  # 使用第一个找到的等级字段
                    level_stats = {
                        "min_level": int(collector.market_data[level_field].min()),
                        "max_level": int(collector.market_data[level_field].max()),
                        "avg_level": float(collector.market_data[level_field].mean())
                    }
                    status_info["level_statistics"] = level_stats
                    
            except Exception as e:
                logger.warning(f"获取数据统计信息时出错: {e}")
                status_info["statistics_error"] = str(e)
        
        # 计算缓存是否过期
        if collector._last_refresh_time:
            from datetime import datetime, timedelta
            cache_expiry_time = collector._last_refresh_time + timedelta(hours=collector._cache_expiry_hours)
            status_info["cache_expired"] = datetime.now() > cache_expiry_time
            status_info["cache_expiry_time"] = cache_expiry_time.isoformat()
        else:
            status_info["cache_expired"] = True
            status_info["cache_expiry_time"] = None
        
        # 添加Flask缓存信息
        try:
            cache_info = collector.get_cache_info()
            status_info["flask_cache"] = cache_info
        except Exception as e:
            logger.warning(f"获取Flask缓存信息失败: {e}")
            status_info["flask_cache"] = {"available": False, "error": str(e)}
        
        return success_response(data=status_info, message="获取市场数据状态成功")
        
    except Exception as e:
        logger.error(f"获取市场数据状态失败: {e}")
        return error_response(f"获取市场数据状态失败: {str(e)}")


@system_bp.route('/market-data/cache-status', methods=['GET'])
def get_cache_status():
    """获取缓存状态"""
    try:
        from src.evaluator.market_data_collector import MarketDataCollector
        
        # 获取市场数据收集器实例
        collector = MarketDataCollector()
        
        # 获取缓存状态
        cache_status = collector.get_cache_status()
        
        return success_response(data=cache_status, message="获取缓存状态成功")
        
    except Exception as e:
        logger.error(f"获取缓存状态失败: {e}")
        return error_response(f"获取缓存状态失败: {str(e)}")


@system_bp.route('/market-data/equipment/cache-status', methods=['GET'])
def get_equipment_cache_status():
    """获取装备缓存状态"""
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 使用类方法获取单例实例的缓存状态
        cache_status = EquipMarketDataCollector.get_cache_status_static()
        
        return success_response(data=cache_status, message="获取装备缓存状态成功")
        
    except Exception as e:
        logger.error(f"获取装备缓存状态失败: {e}")
        return error_response(f"获取装备缓存状态失败: {str(e)}")


@system_bp.route('/market-data/equipment/refresh', methods=['POST'])
def refresh_equipment_data():
    """启动装备数据刷新"""
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        import threading
        
        # 获取请求参数
        data = request.get_json() or {}
        
        # 获取装备数据采集器实例（使用单例模式）
        collector = EquipMarketDataCollector.get_instance()
        
        # 检查是否正在刷新
        if collector._refresh_status == "running":
            return error_response("装备数据刷新正在进行中，请等待完成后再试")
        
        # 设置刷新参数
        use_cache = data.get('use_cache', True)
        force_refresh = data.get('force_refresh', False)
        
        # 在后台线程中执行刷新
        def background_refresh():
            try:
                if force_refresh:
                    # 强制刷新，完全重新加载
                    collector.refresh_full_cache()
                else:
                    # 使用缓存，如果缓存不存在则加载
                    collector._load_full_data_to_redis(force_refresh=False)
            except Exception as e:
                logger.error(f"后台刷新装备数据失败: {e}")
                collector._refresh_status = "error"
                collector._refresh_message = f"刷新失败: {str(e)}"
        
        # 启动后台线程
        refresh_thread = threading.Thread(target=background_refresh)
        refresh_thread.daemon = True
        refresh_thread.start()
        
        # 立即返回启动成功的响应
        return success_response(data={
            "refresh_started": True,
            "message": "装备数据刷新已启动，请使用状态接口查询进度",
            "force_refresh": force_refresh,
            "use_cache": use_cache
        }, message="装备数据刷新已启动")
        
    except Exception as e:
        logger.error(f"启动装备数据刷新失败: {e}")
        return error_response(f"启动装备数据刷新失败: {str(e)}")

 
@system_bp.route('/market-data/equipment/status', methods=['GET'])
def get_equipment_market_data_status():
    """获取装备市场数据状态"""
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        import time
        
        # 获取装备数据采集器实例（使用单例模式）
        start_time = time.time()
        collector = EquipMarketDataCollector.get_instance()
        instance_time = (time.time() - start_time) * 1000
        
        # 添加调试信息
        print(f"🔍 装备市场数据状态 - 实例ID: {id(collector)} (耗时: {instance_time:.2f}ms)")
        print(f"🔍 内存缓存状态: {collector._full_data_cache is not None and not collector._full_data_cache.empty if collector._full_data_cache is not None else False}")
        print(f"🔍 刷新状态: {collector._refresh_status}")
        
        # 获取MySQL装备数据总数
        mysql_start = time.time()
        mysql_count = collector._get_mysql_equipments_count()
        mysql_time = (time.time() - mysql_start) * 1000
        print(f"🔍 MySQL查询耗时: {mysql_time:.2f}ms")
        
        # 获取Redis数据总数（从Hash元数据获取，不加载实际数据）
        redis_count = 0
        redis_start = time.time()
        try:
            if collector.redis_cache and collector.redis_cache.is_available():
                # 从Hash结构元数据获取数据总数
                meta_key = f"{collector._full_cache_key}:meta"
                print(f"🔍 尝试获取Redis元数据键: {meta_key}")
                
                # 先检查键是否存在
                full_meta_key = collector.redis_cache._make_key(meta_key)
                print(f"🔍 完整元数据键: {full_meta_key}")
                
                # 检查键是否存在
                key_exists = collector.redis_cache.client.exists(full_meta_key)
                print(f"🔍 元数据键是否存在: {key_exists}")
                
                if key_exists:
                    # 元数据是作为普通字符串存储的，需要反序列化
                    import pickle
                    try:
                        metadata_bytes = collector.redis_cache.client.get(full_meta_key)
                        if metadata_bytes:
                            hash_metadata = pickle.loads(metadata_bytes)
                            print(f"🔍 Redis元数据内容: {hash_metadata}")
                            if hash_metadata and 'total_count' in hash_metadata:
                                redis_count = hash_metadata.get('total_count', 0)
                                print(f"🔍 Redis缓存数据量: {redis_count} 条")
                            else:
                                print("🔍 Redis元数据缺少total_count字段")
                        else:
                            print("🔍 Redis元数据为空")
                    except Exception as e:
                        print(f"🔍 反序列化Redis元数据失败: {e}")
                        # 尝试作为Hash结构获取（向后兼容）
                        hash_metadata = collector.redis_cache.get(meta_key)
                        print(f"🔍 Redis元数据内容(Hash): {hash_metadata}")
                        if hash_metadata and 'total_count' in hash_metadata:
                            redis_count = hash_metadata.get('total_count', 0)
                            print(f"🔍 Redis缓存数据量: {redis_count} 条")
                        else:
                            print("🔍 Redis Hash元数据缺少total_count字段")
                else:
                    print("🔍 Redis Hash元数据键不存在")
                    
                    # 避免调用hlen()，因为这会触发Redis扫描，影响性能
                    # 如果元数据不存在，说明可能没有数据或者数据正在加载中
                    print("🔍 元数据不存在，跳过Redis数据量查询以避免性能影响")
                    redis_count = 0
            else:
                print("🔍 Redis不可用")
        except Exception as e:
            print(f"🔍 获取Redis数据总数失败: {e}")
        finally:
            redis_time = (time.time() - redis_start) * 1000
            print(f"🔍 Redis查询耗时: {redis_time:.2f}ms")
        
        # 获取基本状态信息
        status_info = {
            "data_loaded": collector._full_data_cache is not None and not collector._full_data_cache.empty,
            "last_refresh_time": collector._refresh_start_time.isoformat() if collector._refresh_start_time else None,
            "cache_ttl_hours": collector._cache_ttl_hours,
            "data_count": len(collector._full_data_cache) if collector._full_data_cache is not None and not collector._full_data_cache.empty else 0,
            "data_columns": list(collector._full_data_cache.columns) if collector._full_data_cache is not None and not collector._full_data_cache.empty else [],
            "memory_usage_mb": collector._full_data_cache.memory_usage(deep=True).sum() / 1024 / 1024 if collector._full_data_cache is not None and not collector._full_data_cache.empty else 0,
            "mysql_data_count": mysql_count,
            "redis_data_count": redis_count
        }
        
        # 添加刷新进度信息
        refresh_status = collector.get_refresh_status()
        status_info.update({
            "refresh_status": refresh_status["status"],
            "refresh_progress": refresh_status["progress"],
            "refresh_message": refresh_status["message"],
            "refresh_processed_records": refresh_status["processed_records"],
            "refresh_total_records": refresh_status["total_records"],
            "refresh_current_batch": refresh_status["current_batch"],
            "refresh_total_batches": refresh_status["total_batches"],
            "refresh_start_time": refresh_status["start_time"],
            "refresh_elapsed_seconds": refresh_status["elapsed_seconds"]
        })
        
        # 如果有数据，添加数据统计信息
        if collector._full_data_cache is not None and not collector._full_data_cache.empty:
            try:
                # 价格统计
                if 'price' in collector._full_data_cache.columns:
                    price_stats = {
                        "min_price": float(collector._full_data_cache['price'].min()),
                        "max_price": float(collector._full_data_cache['price'].max()),
                        "avg_price": float(collector._full_data_cache['price'].mean()),
                        "median_price": float(collector._full_data_cache['price'].median())
                    }
                    status_info["price_statistics"] = price_stats
                
                # 装备类型分布
                if 'kindid' in collector._full_data_cache.columns:
                    kindid_counts = collector._full_data_cache['kindid'].value_counts().to_dict()
                    status_info["kindid_distribution"] = kindid_counts
                
                # 等级分布
                if 'equip_level' in collector._full_data_cache.columns:
                    level_stats = {
                        "min_level": int(collector._full_data_cache['equip_level'].min()),
                        "max_level": int(collector._full_data_cache['equip_level'].max()),
                        "avg_level": float(collector._full_data_cache['equip_level'].mean())
                    }
                    status_info["level_statistics"] = level_stats
                    
            except Exception as e:
                logger.warning(f"获取装备数据统计信息时出错: {e}")
                status_info["statistics_error"] = str(e)
        
        # 计算缓存是否过期
        if collector._refresh_start_time:
            from datetime import datetime, timedelta
            if collector._cache_ttl_hours == -1:
                status_info["cache_expired"] = False
                status_info["cache_expiry_time"] = None
            else:
                cache_expiry_time = collector._refresh_start_time + timedelta(hours=collector._cache_ttl_hours)
                status_info["cache_expired"] = datetime.now() > cache_expiry_time
                status_info["cache_expiry_time"] = cache_expiry_time.isoformat()
        else:
            status_info["cache_expired"] = True
            status_info["cache_expiry_time"] = None
        
        # 添加Redis全量缓存状态信息
        try:
            redis_cache_status = collector.get_cache_status()
            status_info["redis_full_cache"] = redis_cache_status
        except Exception as e:
            logger.warning(f"获取Redis全量缓存状态失败: {e}")
            status_info["redis_full_cache"] = {"available": False, "error": str(e)}
        
        return success_response(data=status_info, message="获取装备市场数据状态成功")
        
    except Exception as e:
        logger.error(f"获取装备市场数据状态失败: {e}")
        return error_response(f"获取装备市场数据状态失败: {str(e)}")


@system_bp.route('/market-data/pet/status', methods=['GET'])
def get_pet_market_data_status():
    """获取召唤兽市场数据状态"""
    try:
        from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
        
        # 获取召唤兽数据采集器实例
        collector = PetMarketDataCollector()
        
        # 添加调试信息
        print(f"🔍 召唤兽市场数据状态 - 实例ID: {id(collector)}")
        print(f"🔍 内存缓存状态: {collector._full_data_cache is not None and not collector._full_data_cache.empty if collector._full_data_cache is not None else False}")
        print(f"🔍 刷新状态: {collector._refresh_status}")
        
        # 获取MySQL召唤兽数据总数
        mysql_count = collector._get_mysql_pets_count()
        
        # 获取基本状态信息
        status_info = {
            "data_loaded": collector._full_data_cache is not None and not collector._full_data_cache.empty,
            "last_refresh_time": collector._refresh_start_time.isoformat() if collector._refresh_start_time else None,
            "cache_ttl_hours": collector._cache_ttl_hours,
            "data_count": len(collector._full_data_cache) if collector._full_data_cache is not None and not collector._full_data_cache.empty else 0,
            "data_columns": list(collector._full_data_cache.columns) if collector._full_data_cache is not None and not collector._full_data_cache.empty else [],
            "memory_usage_mb": collector._full_data_cache.memory_usage(deep=True).sum() / 1024 / 1024 if collector._full_data_cache is not None and not collector._full_data_cache.empty else 0,
            "mysql_data_count": mysql_count
        }
        
        # 添加刷新进度信息
        refresh_status = collector.get_refresh_status()
        status_info.update({
            "refresh_status": refresh_status["status"],
            "refresh_progress": refresh_status["progress"],
            "refresh_message": refresh_status["message"],
            "refresh_processed_records": refresh_status["processed_records"],
            "refresh_total_records": refresh_status["total_records"],
            "refresh_current_batch": refresh_status["current_batch"],
            "refresh_total_batches": refresh_status["total_batches"],
            "refresh_start_time": refresh_status["start_time"],
            "refresh_elapsed_seconds": refresh_status["elapsed_seconds"]
        })
        
        # 如果有数据，添加数据统计信息
        if collector._full_data_cache is not None and not collector._full_data_cache.empty:
            try:
                df = collector._full_data_cache
                
                # 价格统计
                if 'price' in df.columns:
                    price_stats = {
                        "min_price": float(df['price'].min()),
                        "max_price": float(df['price'].max()),
                        "avg_price": float(df['price'].mean()),
                        "median_price": float(df['price'].median())
                    }
                    status_info["price_statistics"] = price_stats
                
                # 等级统计
                if 'equip_level' in df.columns:
                    level_stats = {
                        "min_level": int(df['equip_level'].min()),
                        "max_level": int(df['equip_level'].max())
                    }
                    status_info["level_statistics"] = level_stats
                
                # 携带等级统计
                if 'role_grade_limit' in df.columns:
                    role_grade_limit_stats = {
                        "min_role_grade_limit": int(df['role_grade_limit'].min()),
                        "max_role_grade_limit": int(df['role_grade_limit'].max())
                    }
                    status_info["role_grade_limit_statistics"] = role_grade_limit_stats
                
                # 技能分布统计
                if 'all_skill' in df.columns:
                    # 统计所有技能的出现次数
                    all_skills = []
                    for skills_str in df['all_skill'].dropna():
                        if skills_str and str(skills_str).strip():
                            skills = str(skills_str).split('|')
                            all_skills.extend([s.strip() for s in skills if s.strip()])
                    
                    from collections import Counter
                    skill_counts = Counter(all_skills)
                    status_info["skill_distribution"] = dict(skill_counts.most_common(20))  # 取前20个最常见的技能
                
            except Exception as e:
                logger.warning(f"计算召唤兽数据统计信息失败: {e}")
                status_info["statistics_error"] = str(e)
        
        # 计算缓存是否过期
        if collector._refresh_start_time:
            from datetime import datetime, timedelta
            if collector._cache_ttl_hours == -1:
                status_info["cache_expired"] = False
                status_info["cache_expiry_time"] = None
            else:
                cache_expiry_time = collector._refresh_start_time + timedelta(hours=collector._cache_ttl_hours)
                status_info["cache_expired"] = datetime.now() > cache_expiry_time
                status_info["cache_expiry_time"] = cache_expiry_time.isoformat()
        else:
            status_info["cache_expired"] = True
            status_info["cache_expiry_time"] = None
        
        # 添加Redis全量缓存状态信息
        try:
            redis_cache_status = collector.get_cache_status()
            status_info["redis_full_cache"] = redis_cache_status
        except Exception as e:
            logger.warning(f"获取Redis全量缓存状态失败: {e}")
            status_info["redis_full_cache"] = {"available": False, "error": str(e)}
        
        return success_response(data=status_info, message="获取召唤兽市场数据状态成功")
        
    except Exception as e:
        logger.error(f"获取召唤兽市场数据状态失败: {e}")
        return error_response(f"获取召唤兽市场数据状态失败: {str(e)}")


@system_bp.route('/market-data/pet/refresh', methods=['POST'])
def refresh_pet_data():
    """刷新召唤兽数据"""
    try:
        from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
        
        # 获取召唤兽数据采集器实例
        collector = PetMarketDataCollector()
        
        # 启动后台数据刷新
        import threading
        
        def refresh_task():
            try:
                # 加载召唤兽数据到Redis缓存
                collector._load_full_data_to_redis()
            except Exception as e:
                logger.error(f"召唤兽数据刷新任务失败: {e}")
        
        # 在后台线程中执行刷新任务
        thread = threading.Thread(target=refresh_task)
        thread.daemon = True
        thread.start()
        
        return success_response(message="召唤兽数据刷新已启动，正在后台处理...")
        
    except Exception as e:
        logger.error(f"启动召唤兽数据刷新失败: {e}")
        return error_response(f"启动召唤兽数据刷新失败: {str(e)}")


@system_bp.route('/market-data/pet/refresh-full-cache', methods=['POST'])
def refresh_pet_full_cache():
    """刷新召唤兽全量缓存"""
    try:
        from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
        
        # 获取召唤兽数据采集器实例
        collector = PetMarketDataCollector()
        
        # 启动后台全量缓存刷新
        import threading
        
        def refresh_task():
            try:
                # 强制刷新全量缓存
                collector.refresh_full_cache()
            except Exception as e:
                logger.error(f"召唤兽全量缓存刷新任务失败: {e}")
        
        # 在后台线程中执行刷新任务
        thread = threading.Thread(target=refresh_task)
        thread.daemon = True
        thread.start()
        
        return success_response(message="召唤兽全量缓存刷新已启动，正在后台处理...")
        
    except Exception as e:
        logger.error(f"启动召唤兽全量缓存刷新失败: {e}")
        return error_response(f"启动召唤兽全量缓存刷新失败: {str(e)}")


@system_bp.route('/market-data/pet/refresh-status', methods=['GET'])
def get_pet_refresh_status():
    """获取召唤兽数据刷新状态"""
    try:
        from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
        
        # 获取召唤兽数据采集器实例
        collector = PetMarketDataCollector()
        
        # 获取刷新状态
        refresh_status = collector.get_refresh_status()
        
        return success_response(data=refresh_status, message="获取召唤兽刷新状态成功")
        
    except Exception as e:
        logger.error(f"获取召唤兽刷新状态失败: {e}")
        return error_response(f"获取召唤兽刷新状态失败: {str(e)}")


@system_bp.route('/redis/status', methods=['GET'])
def get_redis_status():
    """获取Redis状态信息"""
    try:
        from src.utils.redis_cache import get_redis_cache
        
        redis_cache = get_redis_cache()
        if not redis_cache:
            return error_response("Redis缓存未初始化")
        
        # 基本连接信息
        status_info = {
            "available": redis_cache.is_available(),
            "host": redis_cache.host,
            "port": redis_cache.port,
            "db": redis_cache.db,
            "connection_pool_size": redis_cache.pool.max_connections if hasattr(redis_cache, 'pool') else 0
        }
        
        if not status_info["available"]:
            status_info["error"] = "Redis连接不可用"
            return success_response(data=status_info, message="Redis状态获取成功")
        
        try:
            # 获取Redis服务器信息
            redis_info = redis_cache.get_redis_info()
            if redis_info:
                status_info.update({
                    "redis_version": redis_info.get('redis_version'),
                    "used_memory_human": redis_info.get('used_memory_human'),
                    "used_memory_peak_human": redis_info.get('used_memory_peak_human'),
                    "connected_clients": redis_info.get('connected_clients'),
                    "total_commands_processed": redis_info.get('total_commands_processed'),
                    "keyspace_hits": redis_info.get('keyspace_hits'),
                    "keyspace_misses": redis_info.get('keyspace_misses'),
                    "uptime_in_seconds": redis_info.get('uptime_in_seconds'),
                    "cache_keys_count": redis_info.get('db0', {}).get('keys', 0)
                })
                
                # 计算命中率
                hits = redis_info.get('keyspace_hits', 0)
                misses = redis_info.get('keyspace_misses', 0)
                total = hits + misses
                if total > 0:
                    status_info["hit_rate"] = round((hits / total) * 100, 2)
                else:
                    status_info["hit_rate"] = 0
        except Exception as e:
            logger.warning(f"获取Redis详细信息失败: {e}")
            status_info["info_error"] = str(e)
        
        # 获取缓存类型统计
        try:
            cache_types = redis_cache.get_cache_types()
            if cache_types:
                status_info["cache_types"] = cache_types
        except Exception as e:
            logger.warning(f"获取缓存类型统计失败: {e}")
            status_info["cache_types_error"] = str(e)
        
        return success_response(data=status_info, message="Redis状态获取成功")
        
    except Exception as e:
        logger.error(f"获取Redis状态失败: {e}")
        return error_response(f"获取Redis状态失败: {str(e)}")


@system_bp.route('/market-data/equipment/refresh-status', methods=['GET'])
def get_equipment_refresh_status():
    """获取装备数据刷新进度状态"""
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 使用类方法获取单例实例的刷新状态
        refresh_status = EquipMarketDataCollector.get_refresh_status_static()
        
        return success_response(data=refresh_status, message="获取装备刷新状态成功")
        
    except Exception as e:
        logger.error(f"获取装备刷新状态失败: {e}")
        return error_response(f"获取装备刷新状态失败: {str(e)}")


@system_bp.route('/market-data/analysis', methods=['GET'])
def get_market_data_analysis():
    """获取市场数据详细分析"""
    try:
        from src.evaluator.market_data_collector import MarketDataCollector
        import pandas as pd
        import numpy as np
        
        # 获取市场数据收集器实例
        collector = MarketDataCollector()
        
        if collector.market_data.empty:
            return error_response("暂无市场数据，请先刷新数据")
        
        df = collector.market_data.copy()
        
        analysis_data = {}
        
        # 1. 等级分布分析
        if 'level' in df.columns:
            level_bins = [109, 120, 130, 140, 150, 160, 175]
            level_labels = ['109-119', '120-129', '130-139', '140-149', '150-159', '160-175']
            df['level_range'] = pd.cut(df['level'], bins=level_bins, labels=level_labels, include_lowest=True)
            level_dist = df['level_range'].value_counts().sort_index()
            
            analysis_data['level_distribution'] = {
                'categories': level_dist.index.tolist(),
                'values': level_dist.values.tolist()
            }
        
        # 2. 价格分布分析
        if 'price' in df.columns:
            price_bins = [0, 1000, 5000, 10000, 20000, 50000, float('inf')]
            price_labels = ['<1000', '1000-5000', '5000-10000', '10000-20000', '20000-50000', '>50000']
            df['price_range'] = pd.cut(df['price'], bins=price_bins, labels=price_labels, include_lowest=True)
            price_dist = df['price_range'].value_counts().sort_index()
            
            analysis_data['price_distribution'] = {
                'categories': price_dist.index.tolist(),
                'values': price_dist.values.tolist()
            }
        
        # 3. 等级与价格关系（散点数据）
        if 'level' in df.columns and 'price' in df.columns:
            # 采样数据，避免返回过多点
            sample_size = min(500, len(df))
            sample_df = df.sample(n=sample_size)
            scatter_data = sample_df[['level', 'price']].values.tolist()
            
            analysis_data['level_price_relation'] = {
                'data': scatter_data
            }
            
            # 计算等级价格趋势
            level_groups = df.groupby(pd.cut(df['level'], bins=8))['price'].agg(['mean', 'count']).reset_index()
            level_groups['level_mid'] = level_groups['level'].apply(lambda x: x.mid)
            
            analysis_data['price_trend'] = {
                'levels': level_groups['level_mid'].round().astype(int).tolist(),
                'avg_prices': level_groups['mean'].round().tolist(),
                'counts': level_groups['count'].tolist()
            }
        
        # 4. 门派分布分析

        if 'school' in df.columns:
            school_dist = df['school'].value_counts()
            school_data = []
            for school_id, count in school_dist.items():
                school_data.append({'name': school_id, 'value': int(count)})
            
            analysis_data['school_distribution'] = school_data
        
        # 5. 服务器分布分析（TOP 10）
        if 'serverid' in df.columns:
            server_dist = df['serverid'].value_counts().head(10)
            analysis_data['server_distribution'] = {
                'server_ids': server_dist.index.tolist(),
                'counts': server_dist.values.tolist()
            }
        
        # 6. 基础统计信息
        analysis_data['basic_stats'] = {
            'total_count': len(df),
            'avg_price': float(df['price'].mean()) if 'price' in df.columns else 0,
            'median_price': float(df['price'].median()) if 'price' in df.columns else 0,
            'price_std': float(df['price'].std()) if 'price' in df.columns else 0,
            'avg_level': float(df['level'].mean()) if 'level' in df.columns else 0,
            'level_std': float(df['level'].std()) if 'level' in df.columns else 0
        }
        
        return success_response(data=analysis_data, message="获取市场数据分析成功")
        
    except Exception as e:
        logger.error(f"获取市场数据分析失败: {e}")
        return error_response(f"获取市场数据分析失败: {str(e)}")


@system_bp.route('/market-data/refresh', methods=['POST'])
def refresh_market_data():
    """启动分批刷新市场数据"""
    try:
        from src.evaluator.market_data_collector import MarketDataCollector
        import threading
        
        # 获取请求参数
        data = request.get_json() or {}
        
        # 获取市场数据收集器实例
        collector = MarketDataCollector()
        
        # 检查是否正在刷新
        if collector._refresh_status == "running":
            return error_response("数据刷新正在进行中，请等待完成后再试")
        
        # 设置刷新参数
        filters = data.get('filters', None)
        use_cache = data.get('use_cache', True)
        force_refresh = data.get('force_refresh', False)
        # 在后台线程中执行刷新
        def background_refresh():
            try:
                collector.refresh_market_data(
                    filters=filters,
                    use_cache=use_cache,
                    force_refresh=force_refresh,
                )
            except Exception as e:
                logger.error(f"后台刷新失败: {e}")
                collector._refresh_status = "error"
                collector._refresh_message = f"刷新失败: {str(e)}"
        
        # 启动后台线程
        refresh_thread = threading.Thread(target=background_refresh)
        refresh_thread.daemon = True
        refresh_thread.start()
        
        # 立即返回启动成功的响应
        return success_response(data={
            "refresh_started": True,
            "message": "数据刷新已启动，请使用状态接口查询进度",
            "filters_applied": filters
        }, message="数据刷新已启动")
        
    except Exception as e:
        logger.error(f"启动刷新失败: {e}")
        return error_response(f"启动刷新失败: {str(e)}")


@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "healthy"}, message="角色API服务正常运行")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统API蓝图
"""

from flask import Blueprint, send_file, request, jsonify, Response
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
        
        # 获取基本状态信息
        status_info = {
            "data_loaded": collector._data_loaded,
            "last_refresh_time": collector._last_refresh_time.isoformat() if collector._last_refresh_time else None,
            "cache_expiry_hours": collector._cache_expiry_hours,
            "data_count": len(collector.market_data) if not collector.market_data.empty else 0,
            "data_columns": list(collector.market_data.columns) if not collector.market_data.empty else [],
            "memory_usage_mb": collector.market_data.memory_usage(deep=True).sum() / 1024 / 1024 if not collector.market_data.empty else 0
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
        
        return success_response(data=status_info, message="获取市场数据状态成功")
        
    except Exception as e:
        logger.error(f"获取市场数据状态失败: {e}")
        return error_response(f"获取市场数据状态失败: {str(e)}")


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
        max_records = data.get('max_records', 999)
        batch_size = data.get('batch_size', 200)
        
        logger.info(f"启动分批刷新市场数据，参数: filters={filters}, max_records={max_records}, batch_size={batch_size}")
        
        # 在后台线程中执行刷新
        def background_refresh():
            try:
                collector.refresh_market_data_batch(
                    filters=filters,
                    max_records=max_records,
                    batch_size=batch_size
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
            "filters_applied": filters,
            "max_records": max_records,
            "batch_size": batch_size
        }, message="数据刷新已启动")
        
    except Exception as e:
        logger.error(f"启动刷新失败: {e}")
        return error_response(f"启动刷新失败: {str(e)}")


@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "healthy"}, message="角色API服务正常运行")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理API蓝图
提供配置文件读取和管理功能
"""

import os
import json
import logging
from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional
from src.utils.project_path import get_project_root, get_config_path

# 获取logger
logger = logging.getLogger(__name__)

# 创建蓝图
config_bp = Blueprint('config', __name__, url_prefix='/api/v1/config')

def success_response(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """成功响应格式"""
    return {
        "code": 200,
        "data": data,
        "message": message,
        "timestamp": int(__import__('time').time())
    }

def error_response(message: str, code: int = 400) -> Dict[str, Any]:
    """错误响应格式"""
    return {
        "code": code,
        "data": None,
        "message": message,
        "timestamp": int(__import__('time').time())
    }

@config_bp.route('/search-params', methods=['GET'])
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
        search_params_dir = os.path.join(config_dir, 'search_params')
        if os.path.exists(search_params_dir):
            try:
                # 读取109等级的配置作为默认角色配置
                role_file = os.path.join(search_params_dir, '109.json')
                if os.path.exists(role_file):
                    with open(role_file, 'r', encoding='utf-8') as f:
                        role_params = json.load(f)
                else:
                    # 如果没有109.json，读取第一个可用的文件
                    for filename in os.listdir(search_params_dir):
                        if filename.endswith('.json'):
                            role_file = os.path.join(search_params_dir, filename)
                            with open(role_file, 'r', encoding='utf-8') as f:
                                role_params = json.load(f)
                            break
            except Exception as e:
                logger.error(f"读取角色搜索参数失败: {e}")
        
        # 处理宠物搜索参数（使用equip_params_pet作为基础）
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
        
        return jsonify(success_response(data=frontend_params, message="获取搜索参数配置成功"))
        
    except Exception as e:
        logger.error(f"获取搜索参数配置失败: {e}")
        return jsonify(error_response(f"获取搜索参数配置失败: {str(e)}"))

@config_bp.route('/search-params/<param_type>', methods=['GET'])
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
        
        # 特殊处理角色和宠物参数
        if param_type == 'role':
            search_params_dir = os.path.join(config_dir, 'search_params')
            if os.path.exists(search_params_dir):
                try:
                    # 读取109等级的配置作为默认角色配置
                    role_file = os.path.join(search_params_dir, '109.json')
                    if os.path.exists(role_file):
                        with open(role_file, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            return jsonify(success_response(data=content, message=f"获取{param_type}参数配置成功"))
                    else:
                        return jsonify(error_response("角色配置文件不存在"))
                except Exception as e:
                    logger.error(f"读取角色配置文件失败: {e}")
                    return jsonify(error_response(f"文件读取失败: {str(e)}"))
            else:
                return jsonify(error_response("角色配置目录不存在"))
        elif param_type == 'pet':
            # 宠物参数使用equip_params_pet
            filename = 'equip_params_pet.json'
            file_path = os.path.join(config_dir, filename)
        elif param_type not in type_to_file:
            return jsonify(error_response(f"不支持的参数类型: {param_type}"))
        else:
            filename = type_to_file[param_type]
            file_path = os.path.join(config_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify(error_response(f"配置文件不存在: {filename}"))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return jsonify(success_response(data=content, message=f"获取{param_type}参数配置成功"))
        except json.JSONDecodeError as e:
            logger.error(f"解析配置文件 {filename} 失败: {e}")
            return jsonify(error_response(f"JSON解析失败: {str(e)}"))
        except Exception as e:
            logger.error(f"读取配置文件 {filename} 失败: {e}")
            return jsonify(error_response(f"文件读取失败: {str(e)}"))
        
    except Exception as e:
        logger.error(f"获取{param_type}参数配置失败: {e}")
        return jsonify(error_response(f"获取{param_type}参数配置失败: {str(e)}"))

@config_bp.route('/search-params/<param_type>', methods=['POST'])
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
            return jsonify(error_response("请提供要更新的参数数据"))
        
        # 特殊处理角色和宠物参数
        if param_type == 'role':
            search_params_dir = os.path.join(config_dir, 'search_params')
            if not os.path.exists(search_params_dir):
                os.makedirs(search_params_dir, exist_ok=True)
            filename = '109.json'
            file_path = os.path.join(search_params_dir, filename)
        elif param_type == 'pet':
            # 宠物参数使用equip_params_pet
            filename = 'equip_params_pet.json'
            file_path = os.path.join(config_dir, filename)
        elif param_type not in type_to_file:
            return jsonify(error_response(f"不支持的参数类型: {param_type}"))
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
            return jsonify(success_response(message=f"更新{param_type}参数配置成功"))
            
        except Exception as e:
            logger.error(f"写入配置文件 {filename} 失败: {e}")
            return jsonify(error_response(f"文件写入失败: {str(e)}"))
        
    except Exception as e:
        logger.error(f"更新{param_type}参数配置失败: {e}")
        return jsonify(error_response(f"更新{param_type}参数配置失败: {str(e)}"))

@config_bp.route('/files', methods=['GET'])
def list_config_files():
    """
    列出config目录下的所有配置文件
    
    Returns:
        JSON: 配置文件列表
    """
    try:
        config_dir = get_config_path()
        
        if not os.path.exists(config_dir):
            return jsonify(success_response(data=[], message="config目录不存在"))
        
        files = []
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(config_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime,
                    'path': file_path
                })
        
        return jsonify(success_response(data=files, message="获取配置文件列表成功"))
        
    except Exception as e:
        logger.error(f"获取配置文件列表失败: {e}")
        return jsonify(error_response(f"获取配置文件列表失败: {str(e)}")) 
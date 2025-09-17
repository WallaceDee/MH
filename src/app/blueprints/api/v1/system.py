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
    
@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "healthy"}, message="角色API服务正常运行")
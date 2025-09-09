#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫API蓝图
基于run.py的功能提供完整的爬虫API服务

API端点列表:
1. GET  /api/v1/spider/status         - 获取任务状态
2. GET  /api/v1/spider/config         - 获取爬虫配置信息
3. POST /api/v1/spider/basic/start    - 启动基础爬虫（通用）
4. POST /api/v1/spider/role/start     - 启动角色爬虫
5. POST /api/v1/spider/equip/start    - 启动装备爬虫
6. POST /api/v1/spider/pet/start      - 启动召唤兽爬虫
7. POST /api/v1/spider/proxy/start    - 启动代理爬虫
8. POST /api/v1/spider/proxy/manage   - 管理代理IP
9. POST /api/v1/spider/test/run       - 运行测试
10.POST /api/v1/spider/task/stop      - 停止当前任务

参数说明:
- spider_type: 爬虫类型 (role/equip/pet)
- equip_type: 装备类型 (normal/lingshi/pet) - 仅装备爬虫需要
- max_pages: 爬取页数 (默认5)
- delay_min: 最小延迟秒数 (默认5.0)
- delay_max: 最大延迟秒数 (默认8.0)

响应格式:
{
    "code": 200,
    "data": {...},
    "message": "操作描述",
    "timestamp": 1234567890
}
"""

from flask import Blueprint, request
from ....controllers.spider_controller import SpiderController
from ....utils.response import success_response, error_response

spider_bp = Blueprint('spider', __name__)
controller = SpiderController()


@spider_bp.route('/status', methods=['GET'])
def get_status():
    """获取当前任务状态"""
    try:
        status = controller.get_task_status()
        return success_response(data=status, message="获取状态成功")
    except Exception as e:
        return error_response(f"获取状态失败: {str(e)}")


@spider_bp.route('/config', methods=['GET'])
def get_config():
    """获取爬虫配置信息"""
    try:
        config = controller.get_spider_config()
        return success_response(data=config, message="获取配置成功")
    except Exception as e:
        return error_response(f"获取配置失败: {str(e)}")


@spider_bp.route('/basic/start', methods=['POST'])
def start_basic_spider():
    """启动基础爬虫（支持角色、装备、召唤兽）"""
    try:
        data = request.json or {}
        
        # 参数验证
        spider_type = data.get('spider_type', 'role')
        if spider_type not in ['role', 'equip', 'pet']:
            return error_response("spider_type必须是role、equip或pet之一")
        
        equip_type = data.get('equip_type', 'normal')
        if spider_type == 'equip' and equip_type not in ['normal', 'lingshi', 'pet']:
            return error_response("equip_type必须是normal、lingshi或pet之一")
        
        max_pages = data.get('max_pages', 5)
        if not isinstance(max_pages, int) or max_pages <= 0:
            return error_response("max_pages必须是大于0的整数")
        
        delay_min = data.get('delay_min', 5.0)
        delay_max = data.get('delay_max', 8.0)
        
        if delay_min < 0 or delay_max < 0 or delay_min > delay_max:
            return error_response("延迟参数无效")
        
        result = controller.start_basic_spider(
            spider_type=spider_type,
            equip_type=equip_type,
            max_pages=max_pages,
            delay_min=delay_min,
            delay_max=delay_max
        )
        
        return success_response(data=result, message="爬虫已启动")
    except Exception as e:
        return error_response(f"启动爬虫失败: {str(e)}")


@spider_bp.route('/role/start', methods=['POST'])
def start_role_spider():
    """启动角色爬虫"""
    try:
        data = request.json or {}
        result = controller.start_role_spider(
            max_pages=data.get('max_pages', 5),
            delay_min=data.get('delay_min', 5.0),
            delay_max=data.get('delay_max', 8.0),
            cached_params=data.get('cached_params')
        )
        return success_response(data=result, message="角色爬虫已启动")
    except Exception as e:
        return error_response(f"启动角色爬虫失败: {str(e)}")


@spider_bp.route('/equip/start', methods=['POST'])
def start_equip_spider():
    """启动装备爬虫"""
    try:
        data = request.json or {}
        
        equip_type = data.get('equip_type', 'normal')
        # 是否多服务器
        multi = data.get('multi', False)
        # 目标服务器列表
        # [
        #   {
        #     "server_id": 459,
        #     "areaid": 3,
        #     "server_name": "2008"
        #   },
        #   {
        #     "server_id": 527,
        #     "areaid": 3,
        #     "server_name": "生日快乐"
        #   },
        #   {
        #     "server_id": 625,
        #     "areaid": 39,
        #     "server_name": "钓鱼岛"
        #   },
        #   {
        #     "server_id": 554,
        #     "areaid": 58,
        #     "server_name": "兰亭序"
        #   },
        #   {
        #     "server_id": 443,
        #     "areaid": 28,
        #     "server_name": "沂水雪山"
        #   },
        #   {
        #     "server_id": 9,
        #     "areaid": 3,
        #     "server_name": "紫禁城"
        #   },
        #   {
        #     "server_id": 976,
        #     "areaid": 58,
        #     "server_name": "梦幻西游"
        #   }
        # ]
        # 如果multi为True，则根据列表把服务器参数合并到cached_params中，然后依次执行任务

        target_server_list = data.get('target_server_list', [])
        if equip_type not in ['normal', 'lingshi', 'pet']:
            return error_response("equip_type必须是normal、lingshi或pet之一")
        
        # 验证target_server_list格式
        if target_server_list and isinstance(target_server_list, list):
            for server in target_server_list:
                if not isinstance(server, dict) or 'server_id' not in server or 'server_name' not in server:
                    return error_response("target_server_list格式错误，每个服务器必须包含server_id和server_name")
        
        result = controller.start_equip_spider(
            equip_type=equip_type,
            max_pages=data.get('max_pages', 5),
            delay_min=data.get('delay_min', 5.0),
            delay_max=data.get('delay_max', 8.0),
            cached_params=data.get('cached_params'),
            target_server_list=target_server_list,
            multi=multi
        )
        return success_response(data=result, message="装备爬虫已启动")
    except Exception as e:
        return error_response(f"启动装备爬虫失败: {str(e)}")


@spider_bp.route('/pet/start', methods=['POST'])
def start_pet_spider():
    """启动召唤兽爬虫"""
    try:
        data = request.json or {}
        target_server_list = data.get('target_server_list', [])
        multi = data.get('multi', False)
        
        # 验证target_server_list格式
        if target_server_list and isinstance(target_server_list, list):
            for server in target_server_list:
                if not isinstance(server, dict) or 'server_id' not in server or 'server_name' not in server:
                    return error_response("target_server_list格式错误，每个服务器必须包含server_id和server_name")
        
        result = controller.start_pet_spider(
            max_pages=data.get('max_pages', 5),
            delay_min=data.get('delay_min', 5.0),
            delay_max=data.get('delay_max', 8.0),
            cached_params=data.get('cached_params'),
            target_server_list=target_server_list,
            multi=multi
        )
        return success_response(data=result, message="召唤兽爬虫已启动")
    except Exception as e:
        return error_response(f"启动召唤兽爬虫失败: {str(e)}")


@spider_bp.route('/proxy/start', methods=['POST'])
def start_proxy_spider():
    """启动代理爬虫"""
    try:
        data = request.json or {}
        result = controller.start_proxy_spider(
            max_pages=data.get('max_pages', 5)
        )
        return success_response(data=result, message="代理爬虫已启动")
    except Exception as e:
        return error_response(f"启动代理爬虫失败: {str(e)}")


@spider_bp.route('/proxy/manage', methods=['POST'])
def manage_proxies():
    """管理代理IP"""
    try:
        result = controller.manage_proxies()
        return success_response(data=result, message="代理管理器已启动")
    except Exception as e:
        return error_response(f"代理管理失败: {str(e)}")


@spider_bp.route('/task/stop', methods=['POST'])
def stop_task():
    """停止当前任务"""
    try:
        result = controller.stop_current_task()
        return success_response(data=result, message=result.get("message", "停止任务请求已发送"))
    except Exception as e:
        return error_response(f"停止任务失败: {str(e)}")


@spider_bp.route('/playwright/start', methods=['POST'])
def start_playwright():
    """启动Playwright收集器"""
    try:
        data = request.json or {}
        
        headless = data.get('headless', False)
        target_url = data.get('target_url')
        
        if not isinstance(headless, bool):
            return error_response("headless必须是布尔值")
        
        result = controller.start_playwright_collector(
            headless=headless,
            target_url=target_url
        )
        return success_response(data=result, message="Playwright收集器已启动")
    except Exception as e:
        return error_response(f"启动Playwright收集器失败: {str(e)}")


@spider_bp.route('/cookie/check', methods=['GET'])
def check_cookie():
    """检查Cookie状态"""
    try:
        result = controller.check_cookie_status()
        return success_response(data=result, message="Cookie状态检查完成")
    except Exception as e:
        return error_response(f"检查Cookie状态失败: {str(e)}")


@spider_bp.route('/cookie/update', methods=['POST'])
def update_cookie():
    """更新Cookie"""
    try:
        result = controller.update_cookies()
        return success_response(data=result, message="Cookie更新程序已启动")
    except Exception as e:
        return error_response(f"启动Cookie更新程序失败: {str(e)}")


@spider_bp.route('/task/reset', methods=['POST'])
def reset_task():
    """重置任务状态"""
    try:
        result = controller.reset_task_status()
        return success_response(data=result, message=result.get("message", "任务状态已重置"))
    except Exception as e:
        return error_response(f"重置任务状态失败: {str(e)}")


@spider_bp.route('/logs', methods=['GET'])
def get_logs():
    """获取爬虫日志"""
    try:
        data = request.args or {}
        lines = data.get('lines', 100)  # 默认返回最近100行
        log_type = data.get('type', 'current')  # current: 当前任务, recent: 最近日志
        spider_type = data.get('spider_type')  # 爬虫类型 (role, equip, pet, proxy)
        filename = data.get('filename')  # 指定的日志文件名
        
        logs = controller.get_task_logs(
            lines=int(lines), 
            log_type=log_type, 
            spider_type=spider_type,
            filename=filename
        )
        return success_response(data=logs, message="获取日志成功")
    except Exception as e:
        return error_response(f"获取日志失败: {str(e)}")


@spider_bp.route('/logs/files', methods=['GET'])
def get_log_files():
    """获取日志文件列表"""
    try:
        from ....controllers.system_controller import SystemController
        system_controller = SystemController()
        files = system_controller.list_output_files()
        
        # 过滤出日志文件
        log_files = [file for file in files if file['name'].endswith('.log')]
        
        # 按修改时间排序，最新的在前面
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return success_response(data={"items": log_files}, message="获取日志文件列表成功")
    except Exception as e:
        return error_response(f"获取日志文件列表失败: {str(e)}")





@spider_bp.route('/logs/stream', methods=['GET'])
def stream_logs():
    """流式获取实时日志（Server-Sent Events）"""
    from flask import Response, stream_with_context
    import time
    import os
    
    def generate():
        """生成日志流"""
        last_position = 0
        last_file = None
        completed_wait_count = 0  # 任务完成后的等待计数
        max_completed_wait = 10   # 任务完成后最多再等待10次（10秒）
        
        try:
            while True:
                # 获取最新日志文件
                # 首先尝试获取当前任务状态，确定爬虫类型
                task_status = controller.get_task_status()
                spider_type = None
                is_task_completed = task_status.get('status') == 'completed'
                
                # 如果任务正在运行，尝试从任务状态中获取爬虫类型
                if task_status.get('status') == 'running':
                    # 从任务ID中提取爬虫类型
                    task_id = task_status.get('details', {}).get('task_id', '')
                    if task_id and '_' in task_id:
                        # 处理多服务器任务ID格式：multi_equip_xxx 或单服务器：equip_xxx
                        parts = task_id.split('_')
                        if parts[0] == 'multi' and len(parts) > 1:
                            spider_type = parts[1]  # 多服务器：取第二部分
                        else:
                            spider_type = parts[0]  # 单服务器：取第一部分
                        # print(f"DEBUG: 从task_id提取spider_type - task_id: {task_id}, spider_type: {spider_type}")
                    else:
                        # print(f"DEBUG: task_id格式不正确 - task_id: {task_id}")
                        pass
                elif is_task_completed:
                    # 任务已完成，但我们继续监控一段时间以确保所有日志都被读取
                    task_id = task_status.get('details', {}).get('task_id', '')
                    if task_id and '_' in task_id:
                        # 处理多服务器任务ID格式：multi_equip_xxx 或单服务器：equip_xxx
                        parts = task_id.split('_')
                        if parts[0] == 'multi' and len(parts) > 1:
                            spider_type = parts[1]  # 多服务器：取第二部分
                        else:
                            spider_type = parts[0]  # 单服务器：取第一部分
                    
                    completed_wait_count += 1
                    if completed_wait_count > max_completed_wait:
                        yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 任务已完成，日志监控结束\n\n"
                        break
                else:
                    # 任务不在运行状态，直接返回，避免不必要的处理
                    yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 任务未运行，等待中...\n\n"
                    time.sleep(5)  # 增加等待时间，减少检查频率
                    continue
                
                # 使用controller.get_task_logs()获取日志文件信息
                logs = controller.get_task_logs(lines=1, log_type='current', spider_type=spider_type)
                
                if not logs or not logs.get('log_file'):
                    # 没有日志文件时，发送心跳
                    if not is_task_completed:
                        print(f"DEBUG: 没有找到日志文件 - spider_type: {spider_type}")
                        yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 等待日志文件...\n\n"
                    time.sleep(2)
                    continue
                
                # 使用controller中的service获取正确的项目根目录
                log_dir = os.path.join(controller.service.project_root, 'output')
                
                # 根据controller返回的日志文件名查找完整路径
                import glob
                log_pattern = os.path.join(log_dir, '*', logs.get('log_file'))
                log_files = glob.glob(log_pattern)
                if log_files:
                    log_file = log_files[0]  # 使用第一个匹配的文件
                else:
                    log_file = None
                    if not is_task_completed:
                        print(f"DEBUG: 没有找到匹配的日志文件")
                
                if not log_file or not os.path.exists(log_file):
                    # 没有日志文件时，发送心跳
                    if not is_task_completed:
                        print(f"DEBUG: 日志文件不存在 - spider_type: {spider_type}, log_file: {log_file}")
                        yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 等待日志文件...\n\n"
                    time.sleep(2)
                    continue
                
                # 检查文件是否发生变化
                current_size = os.path.getsize(log_file)
                
                if last_file != log_file:
                    # 新文件，从头开始读取
                    last_position = 0
                    last_file = log_file
                    yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 开始监控日志文件: {os.path.basename(log_file)}\n\n"
                
                if current_size > last_position:
                    # 文件有新内容，读取新增部分
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            f.seek(last_position)
                            new_lines = f.readlines()
                            
                            for line in new_lines:
                                line = line.strip()
                                if line:
                                    yield f"data: {line}\n\n"
                            
                            last_position = f.tell()
                            
                            # 如果读取到了新内容且任务已完成，重置等待计数
                            if new_lines and is_task_completed:
                                completed_wait_count = 0
                                
                    except Exception as e:
                        yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 读取日志文件错误: {str(e)}\n\n"
                
                # 添加多服务器任务间的等待日志
                if task_status.get('multi', False) and task_status.get('status') == 'running':
                    # 检查是否在等待下一个服务器
                    current_server = task_status.get('details', {}).get('current_server', {})
                    completed_servers = task_status.get('details', {}).get('completed_servers', 0)
                    total_servers = task_status.get('details', {}).get('total_servers', 0)
                    
                    # 如果当前没有服务器在运行，说明正在等待
                    if current_server and completed_servers > 0 and completed_servers < total_servers:
                        # 计算等待时间（基于延迟参数）
                        delay_min = 5.0  # 默认最小延迟
                        delay_max = 8.0  # 默认最大延迟
                        avg_delay = (delay_min + delay_max) / 2
                        
                        # 发送等待日志
                        yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - [系统] 服务器 {current_server.get('server_name', '未知')} 爬取完成，等待 {avg_delay:.1f} 秒后继续下一个服务器...\n\n"
                        
                        # 等待一段时间，避免重复发送等待日志
                        time.sleep(avg_delay)
                        continue
                
                time.sleep(1)  # 每1秒检查一次
                
        except Exception as e:
            yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S')} - 流式日志错误: {str(e)}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )


@spider_bp.route('/files', methods=['GET'])
def list_files():
    """列出输出文件"""
    try:
        from ....controllers.system_controller import SystemController
        system_controller = SystemController()
        files = system_controller.list_output_files()
        return success_response(data={"items": files})
    except Exception as e:
        return error_response(f"获取文件列表失败: {str(e)}")


@spider_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载文件"""
    try:
        from ....controllers.system_controller import SystemController
        from flask import send_file
        system_controller = SystemController()
        file_path = system_controller.get_file_path(filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return error_response("文件不存在", code=404, http_code=500)
    except Exception as e:
        return error_response(f"下载失败: {str(e)}", http_code=500)


# 兼容性端点（保持旧版本API兼容）
@spider_bp.route('/proxies/manage', methods=['POST'])
def manage_proxies_legacy():
    """管理代理IP（兼容性端点）"""
    return manage_proxies()


@spider_bp.route('/parse/response', methods=['POST'])
def parse_response_data():
    """解析响应数据"""
    try:
        data = request.json or {}
        
        # 参数验证
        url = data.get('url')
        response_text = data.get('response_text')
        
        if not url:
            return error_response("url参数不能为空")
        
        if not response_text:
            return error_response("response_text参数不能为空")
        
        if not isinstance(url, str):
            return error_response("url必须是字符串")
        
        if not isinstance(response_text, str):
            return error_response("response_text必须是字符串")
        
        # 调用控制器方法
        result = controller.parse_response_data(url, response_text)
        
        if result.get('success'):
            return success_response(data=result, message=result.get('message', '解析成功'))
        else:
            return error_response(result.get('message', '解析失败'))
            
    except Exception as e:
        return error_response(f"解析响应数据失败: {str(e)}") 
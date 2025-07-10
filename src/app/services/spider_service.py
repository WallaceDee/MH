#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫服务层
基于run.py的功能提供完整的爬虫服务
"""

import logging
import sys
import os
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 全局任务状态
task_status = {
    "status": "idle", 
    "message": "", 
    "details": {
        "task_id": None,
        "start_time": None,
        "duration": None
    }
}

# 全局进程引用
current_process = None

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))


class SpiderService:
    """爬虫服务"""
    
    def __init__(self):
        self.project_root = project_root
        self.run_script = os.path.join(self.project_root, 'run.py')
    
    def get_task_status(self):
        """获取任务状态"""
        return task_status
    
    def update_progress(self, current_page: int, total_pages: int, message: str = None):
        """更新进度"""
        global task_status
        if task_status["status"] == "running" and message:
            task_status["message"] = message
    
    def is_task_running(self):
        """检查是否有任务在运行"""
        return task_status["status"] == "running"
    
    def stop_current_task(self):
        """停止当前任务"""
        global current_process, task_status
        
        try:
            if current_process and current_process.poll() is None:
                # 进程还在运行，尝试终止
                logger.info("正在终止爬虫进程...")
                current_process.terminate()
                
                # 等待进程结束，最多等待5秒
                import time
                for _ in range(10):
                    if current_process.poll() is not None:
                        break
                    time.sleep(0.5)
                
                # 如果进程还在运行，强制杀死
                if current_process.poll() is None:
                    logger.warning("进程未响应terminate，强制杀死...")
                    current_process.kill()
                    current_process.wait()
                
                # 更新状态
                task_status = {
                    "status": "stopped",
                    "message": "任务已被手动停止",
                    "details": {
                        **task_status.get("details", {}),
                        "duration": "手动停止"
                    }
                }
                
                current_process = None
                return {"message": "任务已成功停止"}
            else:
                # 检查状态是否为running但进程不存在
                if task_status["status"] == "running":
                    # 任务状态显示运行中但进程不存在，可能是意外中断
                    task_status = {
                        "status": "error",
                        "message": "任务意外中断",
                        "details": {
                            **task_status.get("details", {}),
                            "duration": "意外中断"
                        }
                    }
                    current_process = None
                    return {"message": "检测到任务意外中断，状态已重置"}
                else:
                    return {"message": "没有正在运行的任务"}
                    
        except Exception as e:
            logger.error(f"停止任务失败: {e}")
            return {"message": f"停止任务失败: {str(e)}"}
    
    def reset_task_status(self):
        """重置任务状态（用于清理意外中断的任务）"""
        global task_status, current_process
        
        task_status = {
            "status": "idle", 
            "message": "状态已重置", 
            "details": {
                "task_id": None,
                "start_time": None,
                "duration": None
            }
        }
        
        if current_process:
            try:
                if current_process.poll() is None:
                    current_process.terminate()
                    current_process.wait(timeout=5)
            except:
                pass
            current_process = None
        
        return {"message": "任务状态已重置"}
    
    def run_basic_spider(self, 
                        spider_type: str = 'role',
                        equip_type: str = 'normal',
                        max_pages: int = 5,
                        use_browser: bool = True,
                        delay_min: float = 5.0,
                        delay_max: float = 8.0,
                        cached_params: dict = None):
        """
        运行基础爬虫
        
        Args:
            spider_type: 爬虫类型 (role, equip, pet)
            equip_type: 装备类型 (normal, lingshi, pet) - 仅当spider_type='equip'时有效
            max_pages: 爬取页数
            use_browser: 是否使用浏览器
            delay_min: 最小延迟
            delay_max: 最大延迟
            cached_params: 缓存的搜索参数
        """
        global task_status
        try:
            import time
            task_status = {
                "status": "running", 
                "message": "初始化爬虫...", 
                "details": {
                    "task_id": f"{spider_type}_{int(time.time())}",
                    "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": None
                }
            }
            
            # 构建命令参数
            cmd = [
                sys.executable, self.run_script,
                'basic',
                '--type', spider_type,
                '--pages', str(max_pages),
                '--delay-min', str(delay_min),
                '--delay-max', str(delay_max)
            ]
            
            # 装备类型参数
            if spider_type == 'equip':
                cmd.extend(['--equip-type', equip_type])
            
            # 浏览器参数
            if use_browser:
                cmd.append('--use-browser')
            else:
                cmd.append('--no-browser')
            
            # 缓存参数
            if cached_params and not use_browser:
                import json
                import tempfile
                # 创建临时文件保存缓存参数
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(cached_params, f)
                    cached_params_file = f.name
                cmd.extend(['--cached-params', cached_params_file])
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            task_status["message"] = f"开始爬取{self._get_spider_type_name(spider_type, equip_type)}数据..."
            
            # 执行爬虫（使用实时输出）
            import threading
            import time
            
            global current_process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                cwd=self.project_root,
                bufsize=1,
                universal_newlines=True
            )
            current_process = process
            

            
            # 等待进程完成
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                task_status = {
                    "status": "completed",
                    "message": f"{self._get_spider_type_name(spider_type, equip_type)}爬虫完成！",
                    "details": {
                        **task_status["details"],
                        "duration": f"{int(time.time() - float(task_status['details']['task_id'].split('_')[1]))}秒"
                    },
                    "results": {
                        "spider_type": spider_type,
                        "equip_type": equip_type if spider_type == 'equip' else None,
                        "stdout": stdout,
                        "stderr": stderr
                    }
                }
                logger.info(f"{spider_type}爬虫完成")
            else:
                raise Exception(f"爬虫执行失败: {stderr}")
                
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}"}
            logger.error(f"基础爬虫出错: {e}")
            raise
    
    def run_proxy_spider(self, max_pages: int = 5):
        """运行代理爬虫"""
        global task_status
        try:
            import time
            task_status = {
                "status": "running", 
                "message": "初始化代理爬虫...", 
                "details": {
                    "task_id": f"proxy_{int(time.time())}",
                    "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": None
                }
            }
            
            cmd = [
                sys.executable, self.run_script,
                'proxy',
                '--pages', str(max_pages)
            ]
            
            logger.info(f"执行代理爬虫命令: {' '.join(cmd)}")
            
            task_status["message"] = "开始代理爬取数据..."
            
            global current_process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                cwd=self.project_root
            )
            current_process = process
            
            # 等待进程完成
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                task_status = {
                    "status": "completed",
                    "message": "代理爬虫完成！",
                    "results": {
                        "stdout": stdout,
                        "stderr": stderr
                    }
                }
                logger.info("代理爬虫完成")
            else:
                raise Exception(f"代理爬虫执行失败: {stderr}")
                
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}"}
            logger.error(f"代理爬虫出错: {e}")
            raise
    
    def manage_proxies(self):
        """管理代理IP"""
        global task_status
        try:
            task_status = {"status": "running", "message": "获取代理IP..."}
            
            cmd = [sys.executable, self.run_script, 'proxy-manager']
            
            logger.info(f"执行代理管理命令: {' '.join(cmd)}")
            
            global current_process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                cwd=self.project_root
            )
            current_process = process
            
            # 等待进程完成
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                task_status = {
                    "status": "completed",
                    "message": "代理管理完成！",
                    "results": {
                        "stdout": stdout,
                        "stderr": stderr
                    }
                }
                logger.info("代理管理完成")
            else:
                raise Exception(f"代理管理执行失败: {stderr}")
                
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}"}
            logger.error(f"代理管理出错: {e}")
            raise
    
    def run_tests(self):
        """运行测试"""
        global task_status
        try:
            task_status = {"status": "running", "message": "运行测试..."}
            
            cmd = [sys.executable, self.run_script, 'test']
            
            logger.info(f"执行测试命令: {' '.join(cmd)}")
            
            global current_process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                cwd=self.project_root
            )
            current_process = process
            
            # 等待进程完成
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                task_status = {
                    "status": "completed",
                    "message": "测试完成！",
                    "results": {
                        "stdout": stdout,
                        "stderr": stderr
                    }
                }
                logger.info("测试完成")
            else:
                raise Exception(f"测试执行失败: {stderr}")
                
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}"}
            logger.error(f"测试出错: {e}")
            raise
    
    def get_spider_config(self):
        """获取爬虫配置信息"""
        return {
            "spider_types": [
                {"value": "role", "label": "角色数据", "description": "爬取角色交易数据"},
                {"value": "equip", "label": "装备数据", "description": "爬取装备交易数据"},
                {"value": "pet", "label": "召唤兽数据", "description": "爬取召唤兽交易数据"}
            ],
            "equip_types": [
                {"value": "normal", "label": "普通装备", "description": "武器、防具等普通装备"},
                {"value": "lingshi", "label": "灵饰", "description": "灵饰装备"},
                {"value": "pet", "label": "召唤兽装备", "description": "宠物装备"}
            ],
            "default_config": {
                "pages": 5,
                "delay_min": 5.0,
                "delay_max": 8.0,
                "use_browser": True
            }
        }
    
    def _get_spider_type_name(self, spider_type: str, equip_type: str = None) -> str:
        """获取爬虫类型的中文名称"""
        type_names = {
            "role": "角色",
            "equip": "装备",
            "pet": "召唤兽"
        }
        
        equip_type_names = {
            "normal": "普通装备",
            "lingshi": "灵饰",
            "pet": "召唤兽装备"
        }
        
        if spider_type == "equip" and equip_type:
            return equip_type_names.get(equip_type, equip_type)
        
        return type_names.get(spider_type, spider_type)
    
    def get_task_logs(self, lines: int = 100, log_type: str = 'current', spider_type: str = None, filename: str = None):
        """
        获取任务日志
        
        Args:
            lines: 返回的日志行数
            log_type: 日志类型 (current: 当前任务, recent: 最近日志, filename: 指定文件名)
            spider_type: 爬虫类型 (role, equip, pet, proxy) - 用于查找特定类型的日志
            filename: 指定的日志文件名
        
        Returns:
            Dict: 包含日志信息的字典
        """
        import os
        import glob
        from datetime import datetime
        
        try:
            # 获取日志文件路径
            log_dir = os.path.join(self.project_root, 'output')
            if not os.path.exists(log_dir):
                return {
                    "logs": [],
                    "log_file": None,
                    "total_lines": 0,
                    "message": "日志目录不存在"
                }
            
            # 如果指定了文件名，直接使用该文件
            if filename and filename != 'current':
                # 在output目录的子目录中查找文件
                log_pattern = os.path.join(log_dir, '*', filename)
                log_files = glob.glob(log_pattern)
                
                if not log_files:
                    return {
                        "logs": [],
                        "log_file": filename,
                        "total_lines": 0,
                        "message": f"指定的日志文件 {filename} 不存在"
                    }
                
                log_file = log_files[0]
            else:
                # 根据日志类型和爬虫类型选择文件
                if spider_type:
                    # 根据爬虫类型查找对应的日志文件
                    spider_prefix = {
                        'role': 'cbg_spider_role',
                        'equip': 'cbg_equip_spider', 
                        'pet': 'cbg_pet_spider',
                        'proxy': 'proxy',
                        'test': 'test'
                    }.get(spider_type, 'cbg_spider')
                    
                    # 查找特定类型的日志文件
                    log_pattern = os.path.join(log_dir, '*', f'{spider_prefix}_*.log')
                    log_files = glob.glob(log_pattern)
                    
                    if not log_files:
                        return {
                            "logs": [],
                            "log_file": None,
                            "total_lines": 0,
                            "message": f"没有找到{spider_type}类型的日志文件"
                        }
                    
                    # 按修改时间排序，获取最新的日志文件
                    log_files.sort(key=os.path.getmtime, reverse=True)
                    log_file = log_files[0]
                else:
                    # 获取所有日志文件中的最新文件
                    log_pattern = os.path.join(log_dir, '*', '*.log')
                    log_files = glob.glob(log_pattern)
                    if not log_files:
                        return {
                            "logs": [],
                            "log_file": None,
                            "total_lines": 0,
                            "message": "没有找到日志文件"
                        }
                    
                    # 按修改时间排序，获取最新的日志文件
                    log_files.sort(key=os.path.getmtime, reverse=True)
                    log_file = log_files[0]
            
            # 读取日志文件
            if not os.path.exists(log_file):
                return {
                    "logs": [],
                    "log_file": os.path.basename(log_file),
                    "total_lines": 0,
                    "message": "日志文件不存在"
                }
            
            # 读取指定行数的日志
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            
            # 获取最后N行
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # 处理日志行，移除空行和格式化
            logs = []
            for line in recent_lines:
                line = line.strip()
                if line:
                    logs.append(line)
            
            result = {
                "logs": logs,
                "log_file": os.path.basename(log_file),
                "total_lines": len(all_lines),
                "recent_lines": len(logs),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
            }
            return result
            
        except Exception as e:
            logger.error(f"获取日志失败: {e}")
            return {
                "logs": [],
                "log_file": None,
                "total_lines": 0,
                "message": f"获取日志失败: {str(e)}"
            }
    
 
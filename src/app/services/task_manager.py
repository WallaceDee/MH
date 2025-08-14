import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FileTaskManager:
    """基于文件存储的任务管理器"""
    
    def __init__(self, file_path: str = "data/tasks.json"):
        self.file_path = file_path
        self.lock = threading.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保任务文件存在"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_tasks(self) -> Dict:
        """加载任务数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载任务文件失败: {e}")
            return {}
    
    def _save_tasks(self, tasks: Dict):
        """保存任务数据"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务文件失败: {e}")
    
    def create_task(self, task_id: str, task_type: str, year: int, month: int) -> Dict:
        """创建任务"""
        with self.lock:
            tasks = self._load_tasks()
            task_data = {
                'task_id': task_id,
                'task_type': task_type,
                'year': year,
                'month': month,
                'status': 'pending',
                'total_count': 0,
                'processed_count': 0,
                'updated_count': 0,
                'current_batch': 0,
                'total_batches': 0,
                'error_message': None,
                'start_time': None,
                'end_time': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tasks[task_id] = task_data
            self._save_tasks(tasks)
            return task_data
    
    def update_task(self, task_id: str, updates: Dict) -> bool:
        """更新任务状态"""
        with self.lock:
            tasks = self._load_tasks()
            if task_id not in tasks:
                return False
            
            tasks[task_id].update(updates)
            tasks[task_id]['updated_at'] = datetime.now().isoformat()
            self._save_tasks(tasks)
            return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务"""
        tasks = self._load_tasks()
        return tasks.get(task_id)
    
    def get_active_tasks(self) -> List[Dict]:
        """获取活跃任务"""
        tasks = self._load_tasks()
        active_tasks = []
        for task in tasks.values():
            if task['status'] in ['pending', 'running']:
                active_tasks.append(task)
        return active_tasks
    
    def remove_task(self, task_id: str) -> bool:
        """删除任务"""
        with self.lock:
            tasks = self._load_tasks()
            if task_id in tasks:
                del tasks[task_id]
                self._save_tasks(tasks)
                return True
            return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        with self.lock:
            tasks = self._load_tasks()
            current_time = datetime.now()
            tasks_to_remove = []
            
            for task_id, task in tasks.items():
                if task['status'] in ['completed', 'failed', 'cancelled']:
                    # 检查任务完成时间
                    if task.get('end_time'):
                        end_time = datetime.fromisoformat(task['end_time'])
                        if (current_time - end_time).total_seconds() > max_age_hours * 3600:
                            tasks_to_remove.append(task_id)
            
            # 删除旧任务
            for task_id in tasks_to_remove:
                del tasks[task_id]
            
            if tasks_to_remove:
                self._save_tasks(tasks)
                logger.info(f"清理了 {len(tasks_to_remove)} 个旧任务")

# 全局任务管理器实例
task_manager = FileTaskManager() 
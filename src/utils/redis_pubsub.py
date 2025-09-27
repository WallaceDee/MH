#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis发布/订阅工具类
用于解决跨进程数据同步问题
"""

import json
import redis
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import threading
import time
import pandas as pd


class RedisPubSub:
    """Redis发布/订阅工具类"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        初始化Redis发布/订阅
        
        Args:
            redis_client: Redis客户端实例，如果为None则创建新实例
        """
        self.redis_client = redis_client or self._create_redis_client()
        self.pubsub = self.redis_client.pubsub()
        self.subscribers = {}  # 存储订阅者回调函数
        self.subscribe_thread = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    def _create_redis_client(self) -> redis.Redis:
        """创建Redis客户端"""
        try:
            # 使用与redis_cache.py相同的远程Redis配置
            return redis.Redis(
                host='47.86.33.98',
                port=6379,
                db=0,
                password='447363121',
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=30,
                retry_on_timeout=True
            )
        except Exception as e:
            self.logger.error(f"创建Redis客户端失败: {e}")
            raise
    
    def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        发布消息到指定频道
        
        Args:
            channel: 频道名称
            message: 消息内容
            
        Returns:
            bool: 是否发布成功
        """
        try:
            # 添加时间戳
            message['timestamp'] = datetime.now().isoformat()
            message['publisher'] = 'spider'
            
            # 序列化消息
            message_str = json.dumps(message, ensure_ascii=False)
            
            # 发布消息
            result = self.redis_client.publish(channel, message_str)
            
            self.logger.info(f"📢 发布消息到频道 {channel}: {message.get('type', 'unknown')}")
            return result > 0
            
        except Exception as e:
            self.logger.error(f"发布消息失败: {e}")
            return False
    
    def publish_with_dataframe(self, channel: str, message: Dict[str, Any], dataframe: pd.DataFrame) -> bool:
        """
        发布包含DataFrame数据的消息到指定频道
        
        Args:
            channel: 频道名称
            message: 消息内容
            dataframe: 要发送的DataFrame数据
            
        Returns:
            bool: 是否发布成功
        """
        try:
            import pickle
            import base64
            
            # 添加时间戳
            message['timestamp'] = datetime.now().isoformat()
            message['publisher'] = 'spider'
            message['has_dataframe'] = True
            
            # 序列化DataFrame
            dataframe_bytes = pickle.dumps(dataframe)
            dataframe_b64 = base64.b64encode(dataframe_bytes).decode('utf-8')
            message['dataframe_data'] = dataframe_b64
            message['dataframe_shape'] = dataframe.shape
            message['dataframe_columns'] = dataframe.columns.tolist()
            
            # 序列化消息
            message_str = json.dumps(message, ensure_ascii=False)
            
            # 发布消息
            result = self.redis_client.publish(channel, message_str)
            
            self.logger.info(f"📢 发布DataFrame消息到频道 {channel}: {message.get('type', 'unknown')}, 数据量: {len(dataframe)} 条")
            return result > 0
            
        except Exception as e:
            self.logger.error(f"发布DataFrame消息失败: {e}")
            return False
    
    def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        订阅指定频道
        
        Args:
            channel: 频道名称
            callback: 消息处理回调函数
            
        Returns:
            bool: 是否订阅成功
        """
        try:
            self.subscribers[channel] = callback
            self.pubsub.subscribe(channel)
            
            self.logger.info(f"📡 订阅频道: {channel}")
            
            # 启动订阅线程
            if not self.running:
                self._start_subscribe_thread()
            
            return True
            
        except Exception as e:
            self.logger.error(f"订阅频道失败: {e}")
            return False
    
    def unsubscribe(self, channel: str) -> bool:
        """
        取消订阅指定频道
        
        Args:
            channel: 频道名称
            
        Returns:
            bool: 是否取消订阅成功
        """
        try:
            if channel in self.subscribers:
                del self.subscribers[channel]
                self.pubsub.unsubscribe(channel)
                self.logger.info(f"📡 取消订阅频道: {channel}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"取消订阅频道失败: {e}")
            return False
    
    def _start_subscribe_thread(self):
        """启动订阅线程"""
        if self.subscribe_thread and self.subscribe_thread.is_alive():
            return
        
        self.running = True
        self.subscribe_thread = threading.Thread(target=self._subscribe_loop, daemon=True)
        self.subscribe_thread.start()
        self.logger.info("📡 启动Redis订阅线程")
    
    def _subscribe_loop(self):
        """订阅循环"""
        while self.running:
            try:
                # 获取消息，超时1秒
                message = self.pubsub.get_message(timeout=1.0)
                
                if message and message['type'] == 'message':
                    self._handle_message(message)
                    
            except Exception as e:
                self.logger.error(f"订阅循环错误: {e}")
                time.sleep(1)
    
    def _handle_message(self, message):
        """处理接收到的消息"""
        try:
            channel = message['channel']
            data = message['data']
            
            # 解析消息
            message_data = json.loads(data)
            
            # 如果消息包含DataFrame数据，进行反序列化
            if message_data.get('has_dataframe', False):
                try:
                    import pickle
                    import base64
                    
                    dataframe_b64 = message_data.get('dataframe_data')
                    if dataframe_b64:
                        dataframe_bytes = base64.b64decode(dataframe_b64)
                        dataframe = pickle.loads(dataframe_bytes)
                        message_data['dataframe'] = dataframe
                        
                        self.logger.info(f"📨 成功反序列化DataFrame: {dataframe.shape}")
                        
                except Exception as e:
                    self.logger.error(f"反序列化DataFrame失败: {e}")
                    message_data['dataframe'] = None
            
            # 调用对应的回调函数
            if channel in self.subscribers:
                callback = self.subscribers[channel]
                callback(message_data)
                
        except Exception as e:
            self.logger.error(f"处理消息失败: {e}")
    
    def stop(self):
        """停止订阅"""
        self.running = False
        if self.subscribe_thread:
            self.subscribe_thread.join(timeout=2)
        self.pubsub.close()
        self.logger.info("📡 停止Redis订阅")


# 全局实例
_redis_pubsub_instance = None


def get_redis_pubsub() -> RedisPubSub:
    """获取全局Redis发布/订阅实例"""
    global _redis_pubsub_instance
    if _redis_pubsub_instance is None:
        _redis_pubsub_instance = RedisPubSub()
    return _redis_pubsub_instance


# 消息类型常量
class MessageType:
    """消息类型常量"""
    EQUIPMENT_DATA_SAVED = "equipment_data_saved"
    EQUIPMENT_CACHE_UPDATED = "equipment_cache_updated"
    EQUIPMENT_CACHE_REFRESHED = "equipment_cache_refreshed"


# 频道名称常量
class Channel:
    """频道名称常量"""
    EQUIPMENT_UPDATES = "equipment_updates"
    CACHE_UPDATES = "cache_updates"

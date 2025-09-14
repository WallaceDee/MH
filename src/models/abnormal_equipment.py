#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异常装备数据模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from .base import Base

class AbnormalEquipment(Base):
    """异常装备表"""
    __tablename__ = 'abnormal_equipment'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    equip_sn = Column(String(255), unique=True, nullable=False, comment='装备序列号')
    equipment_data = Column(Text, nullable=False, comment='装备数据')
    mark_reason = Column(String(255), default='标记异常', comment='标记原因')
    mark_time = Column(DateTime, default=datetime.utcnow, comment='标记时间')
    status = Column(String(50), default='pending', comment='状态')
    notes = Column(Text, comment='备注')

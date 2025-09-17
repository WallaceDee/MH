#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异常装备模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from src.models.base import Base

class AbnormalEquipment(Base):
    """异常装备表模型"""
    __tablename__ = 'abnormal_equipment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    equip_sn = Column(String(191), nullable=False, unique=True, comment='装备序列号')
    equipment_data = Column(Text, nullable=False, comment='装备数据JSON')
    mark_reason = Column(String(191), nullable=False, default='标记异常', comment='标记原因')
    mark_time = Column(DateTime, nullable=False, default=func.now(), comment='标记时间')
    status = Column(String(50), nullable=False, default='pending', comment='状态')
    notes = Column(Text, comment='备注')
    
    def __repr__(self):
        return f"<AbnormalEquipment(equip_sn='{self.equip_sn}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'equip_sn': self.equip_sn,
            'equipment_data': self.equipment_data,
            'mark_reason': self.mark_reason,
            'mark_time': self.mark_time.isoformat() if self.mark_time else None,
            'status': self.status,
            'notes': self.notes
        }
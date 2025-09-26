#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备服务
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from src.utils.project_path import get_project_root, get_data_path
from src.database_config import db_config
from src.database import db
from src.models.equipment import Equipment
from src.models.pet import Pet
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import sessionmaker
from src.evaluator.market_anchor.equip.index import EquipAnchorEvaluator
from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
from src.evaluator.feature_extractor.unified_feature_extractor import UnifiedFeatureExtractor
from src.evaluator.constants.equipment_types import LINGSHI_KINDIDS, PET_EQUIP_KINDID, is_lingshi, is_pet_equip

logger = logging.getLogger(__name__)

class EquipmentService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = get_project_root()
        self.data_dir = get_data_path()
        
        # 初始化数据库连接
        self.db_config = db_config
        
        # 初始化特征提取器
        self.equip_feature_extractor = None
        self.lingshi_feature_extractor = None
        self.pet_equip_feature_extractor = None
        
        if EquipFeatureExtractor:
            try:
                self.equip_feature_extractor = EquipFeatureExtractor()
                logger.info("装备特征提取器初始化成功")
            except Exception as e:
                logger.error(f"装备特征提取器初始化失败: {e}")
        
        if LingshiFeatureExtractor:
            try:
                self.lingshi_feature_extractor = LingshiFeatureExtractor()
                logger.info("灵饰特征提取器初始化成功")
            except Exception as e:
                logger.error(f"灵饰特征提取器初始化失败: {e}")
        
        if PetEquipFeatureExtractor:
            try:
                self.pet_equip_feature_extractor = PetEquipFeatureExtractor()
                logger.info("宠物装备特征提取器初始化成功")
            except Exception as e:
                logger.error(f"宠物装备特征提取器初始化失败: {e}")

        # 初始化装备锚点估价器
        self.evaluator = None
        if EquipAnchorEvaluator:
            try:
                self.evaluator = EquipAnchorEvaluator()
                logger.info("装备锚点估价器初始化成功")
            except Exception as e:
                logger.error(f"装备锚点估价器初始化失败: {e}")
        
        # 初始化统一特征提取器
        self.unified_extractor = None
        if UnifiedFeatureExtractor:
            try:
                self.unified_extractor = UnifiedFeatureExtractor()
                logger.info("统一特征提取器初始化成功")
            except Exception as e:
                logger.error(f"统一特征提取器初始化失败: {e}")
        
        # MySQL模式下不需要初始化SQLite数据库
    

    
    
    def mark_equipment_as_abnormal(self, equipment_data: Dict, reason: str = "标记异常", notes: str = None) -> Dict:
        """标记装备为异常"""
        try:
            if not equipment_data:
                return {"error": "装备数据不能为空"}
            
            equip_sn = equipment_data.get('equip_sn')
            
            if not equip_sn:
                return {"error": "装备序列号不能为空"}
            
            # 使用SQLAlchemy ORM
            from src.models.abnormal_equipment import AbnormalEquipment
            
            # 检查是否已存在
            existing = db.session.query(AbnormalEquipment).filter_by(equip_sn=equip_sn).first()
            
            if existing:
                # 更新现有记录
                existing.equipment_data = json.dumps(equipment_data, ensure_ascii=False)
                existing.mark_reason = reason
                existing.notes = notes
                existing.mark_time = datetime.utcnow()
                existing.status = 'pending'
                message = "异常装备记录已更新"
            else:
                # 插入新记录
                abnormal_equipment = AbnormalEquipment(
                    equip_sn=equip_sn,
                    equipment_data=json.dumps(equipment_data, ensure_ascii=False),
                    mark_reason=reason,
                    notes=notes,
                    status='pending'
                )
                db.session.add(abnormal_equipment)
                message = "装备已标记为异常"
            
            db.session.commit()
            
            return {
                "success": True,
                "message": message,
                "equip_sn": equip_sn
            }
                
        except Exception as e:
            logger.error(f"标记装备异常失败: {e}")
            return {"error": f"标记装备异常失败: {str(e)}"}
    
    def get_abnormal_equipment_list(self, page: int = 1, page_size: int = 20, status: str = None) -> Dict:
        """获取异常装备列表"""
        try:
            # 使用SQLAlchemy ORM
            from src.models.abnormal_equipment import AbnormalEquipment
            
            # 构建查询
            query = db.session.query(AbnormalEquipment)
            
            if status:
                query = query.filter(AbnormalEquipment.status == status)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            offset = (page - 1) * page_size
            abnormal_equipments = query.order_by(AbnormalEquipment.mark_time.desc()).offset(offset).limit(page_size).all()
            
            items = []
            for abnormal_equipment in abnormal_equipments:
                try:
                    equipment_data = json.loads(abnormal_equipment.equipment_data) if abnormal_equipment.equipment_data else {}
                    items.append({
                        "id": abnormal_equipment.id,
                        "equip_sn": abnormal_equipment.equip_sn,
                        "equipment_data": equipment_data,
                        "mark_reason": abnormal_equipment.mark_reason,
                        "mark_time": abnormal_equipment.mark_time.isoformat() if abnormal_equipment.mark_time else None,
                        "status": abnormal_equipment.status,
                        "notes": abnormal_equipment.notes
                    })
                except json.JSONDecodeError:
                    logger.warning(f"解析装备数据失败: {abnormal_equipment.equipment_data}")
                    continue
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
                
        except Exception as e:
            logger.error(f"获取异常装备列表失败: {e}")
            return {"error": f"获取异常装备列表失败: {str(e)}"}
    
    def update_abnormal_equipment_status(self, equip_sn: str, status: str, notes: str = None) -> Dict:
        """更新异常装备状态"""
        try:
            # 使用SQLAlchemy ORM
            from src.models.abnormal_equipment import AbnormalEquipment
            
            abnormal_equipment = db.session.query(AbnormalEquipment).filter_by(equip_sn=equip_sn).first()
            
            if abnormal_equipment:
                abnormal_equipment.status = status
                abnormal_equipment.notes = notes
                abnormal_equipment.mark_time = datetime.utcnow()
                db.session.commit()
                
                return {
                    "success": True,
                    "message": "异常装备状态更新成功"
                }
            else:
                return {"error": "未找到指定的异常装备记录"}
                    
        except Exception as e:
            logger.error(f"更新异常装备状态失败: {e}")
            return {"error": f"更新异常装备状态失败: {str(e)}"}
    
    def delete_abnormal_equipment(self, equip_sn: str) -> Dict:
        """删除异常装备记录"""
        try:
            # 使用SQLAlchemy ORM
            from src.models.abnormal_equipment import AbnormalEquipment
            
            abnormal_equipment = db.session.query(AbnormalEquipment).filter_by(equip_sn=equip_sn).first()
            
            if abnormal_equipment:
                db.session.delete(abnormal_equipment)
                db.session.commit()
                
                return {
                    "success": True,
                    "message": "异常装备记录删除成功"
                }
            else:
                return {"error": "未找到指定的异常装备记录"}
                    
        except Exception as e:
            logger.error(f"删除异常装备记录失败: {e}")
            return {"error": f"删除异常装备记录失败: {str(e)}"}
    
    def _get_feature_extractor(self, kindid: int):
        """根据装备类型获取对应的特征提取器"""
        # 使用常量判断装备类型
        if is_lingshi(kindid):
            return self.lingshi_feature_extractor
        elif is_pet_equip(kindid):
            return self.pet_equip_feature_extractor
        else:
            # 普通装备
            return self.equip_feature_extractor
    
    def _get_kindid_from_itype(self, kindid: int, i_type: int) -> int:
        """
        根据kindid和iType获取对应的kindid
        如果kindid已存在且有效，直接返回；否则根据iType转换
        
        Args:
            kindid: 现有的kindid值
            i_type: iType值
            
        Returns:
            int: 有效的kindid值
        """
        # 如果kindid已存在且有效，直接返回
        if kindid > 0:
            return kindid
            
        # 如果iType无效，返回0
        if not i_type or i_type <= 0:
            return 0
            
        # 根据iType转换kindid
        from src.evaluator.constants.i_type_kindid_map import KINDID_ITYPE_RANGE
        
        try:
            i_type = int(i_type)
        except (ValueError, TypeError):
            return 0

        for kindid, ranges in KINDID_ITYPE_RANGE.items():
            for range_tuple in ranges:
                if len(range_tuple) == 2:
                    start, end = range_tuple
                    if int(start) <= i_type <= int(end):
                        return kindid

        return 0
    

    
    def _validate_date_range(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """验证日期范围参数
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            验证后的日期范围元组
        """
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"无效的开始日期格式: {start_date}，请使用YYYY-MM-DD格式")
                
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"无效的结束日期格式: {end_date}，请使用YYYY-MM-DD格式")
                
        return start_date, end_date
    
    
    def get_equipments(self, page: int = 1, page_size: int = 10, 
                      start_date: Optional[str] = None, end_date: Optional[str] = None,
                      equip_sn: Optional[str] = None,
                      level_min: Optional[int] = None, level_max: Optional[int] = None,
                      price_min: Optional[int] = None, price_max: Optional[int] = None,
                      kindid: Optional[List[str]] = None, 
                      equip_type: Optional[List[int]] = None,  # 宠物装备类型（多选）
                      equip_special_skills: Optional[List[str]] = None,
                      equip_special_effect: Optional[List[str]] = None,
                      suit_effect: Optional[str] = None,
                      suit_added_status: Optional[str] = None,
                      suit_transform_skills: Optional[str] = None, 
                      suit_transform_charms: Optional[str] = None,
                      gem_value: Optional[str] = None,
                      gem_level: Optional[int] = None,
                      equip_sn_list: Optional[List[str]] = None,  # 装备序列号列表，如果提供则只查询指定的装备
                      sort_by: Optional[str] = '', sort_order: Optional[str] = '') -> Dict:
        """获取分页的装备列表
        
        Args:
            page: 页码
            page_size: 每页数量
            start_date: 开始日期
            end_date: 结束日期
            equip_sn: 单个装备序列号
            level_min: 等级下限
            level_max: 等级上限
            price_min: 价格下限
            price_max: 价格上限
            kindid: 装备类型列表
            equip_type: 宠物装备类型列表
            equip_special_skills: 特技列表
            equip_special_effect: 特效列表
            suit_effect: 套装效果
            suit_added_status: 套装附加状态
            suit_transform_skills: 套装变身术
            suit_transform_charms: 套装变化咒
            gem_value: 宝石值
            gem_level: 宝石等级
            equip_sn_list: 装备序列号列表，如果提供则只查询指定的装备
            sort_by: 排序字段
            sort_order: 排序顺序
            
        Returns:
            包含装备列表和分页信息的字典
            
        ### 基础信息字段
        1. `eid` - 装备ID（用于操作链接和相似装备功能）
        2. `server_name` - 服务器名称
        3. `price` - 价格
        4. `equip_level` - 装备等级

        ### 🎨 显示和样式字段
        5. `highlight` - 亮点信息
        6. `dynamic_tags` - 动态标签

        ### 💎 宝石和强化字段
        7. `gem_level` - 宝石等级
        8. `jinglian_level` - 精炼等级
        9. `xiang_qian_level` - 镶嵌等级

        ### ⚔️ 特技和特效字段
        10. `special_effect` - 特效
        11. `special_skill` - 特技

        ### ️ 套装和属性字段
        12. `suit_effect` - 套装效果
        13. `agg_added_attrs` - 附加属性

        ###  伤害和属性字段
        14. `all_damage` - 总伤害
        15. `init_damage` - 初始伤害
        16. `damage` - 伤害（备用字段）
        17. `shanghai` - 伤害（备用字段）

        ###  法术相关字段
        18. `init_wakan` - 初始灵力
        19. `magic_damage` - 法术伤害
        20. `init_defense` - 初始防御
        21. `defense` - 防御（备用字段）
        22. `fangyu` - 防御（备用字段）
        23. `magic_defense` - 法术防御

        ### ❤️ 生命和速度字段
        24. `init_hp` - 初始气血
        25. `qixue` - 气血（备用字段）
        26. `init_dex` - 初始敏捷
        27. `speed` - 速度（备用字段）

        ###  功能操作字段
        28. `equip_sn` - 装备序列号（用于删除操作）

        29. `equip_type_desc` - 装备类型描述
        30. `equip_name` - 装备名称
        31. `large_equip_desc` - 装备描述
        """
        try:
            start_date, end_date = self._validate_date_range(start_date, end_date)
            
            # 装备序列号列表参数处理 - 过滤空值
            if equip_sn_list is not None:
                equip_sn_list = [item.strip() for item in equip_sn_list if item and item.strip()]
                if not equip_sn_list:
                    equip_sn_list = None
                logger.info(f"处理后的equip_sn_list: {equip_sn_list}, 长度: {len(equip_sn_list) if equip_sn_list else 0}")
            
            # 使用SQLAlchemy ORM
            query = db.session.query(Equipment)
            
            # 添加调试日志
            logger.info(f"开始处理筛选条件，参数: level_min={level_min}, level_max={level_max}, price_min={price_min}, price_max={price_max}")
            logger.info(f"多选参数: kindid={kindid}, equip_special_skills={equip_special_skills}, equip_special_effect={equip_special_effect}")
            
            # 构建查询条件
            if equip_sn:
                query = query.filter(Equipment.equip_sn == equip_sn)
            
            # 装备序列号列表筛选 - 如果提供了equip_sn_list，只查询指定的装备
            if equip_sn_list is not None and len(equip_sn_list) > 0:
                query = query.filter(Equipment.equip_sn.in_(equip_sn_list))
                logger.info(f"添加装备序列号列表筛选: equip_sn IN {equip_sn_list}")
            else:
                # 时间范围筛选
                if start_date:
                    query = query.filter(func.date(Equipment.selling_time) >= start_date)
                    logger.info(f"添加开始日期筛选: selling_time >= {start_date}")
                if end_date:
                    query = query.filter(func.date(Equipment.selling_time) <= end_date)
                    logger.info(f"添加结束日期筛选: selling_time <= {end_date}")
                    
                # 基础筛选条件
                if level_min is not None:
                    query = query.filter(or_(Equipment.level >= level_min, Equipment.equip_level >= level_min))
                if level_max is not None:
                    query = query.filter(or_(Equipment.level <= level_max, Equipment.equip_level <= level_max))
                if price_min is not None:
                    query = query.filter(Equipment.price >= price_min * 100)  # 前端传元，后端存分
                if price_max is not None:
                    query = query.filter(Equipment.price <= price_max * 100)
                
                # 装备类型筛选（多选）
                if kindid and len(kindid) > 0:
                    query = query.filter(Equipment.kindid.in_(kindid))
                    logger.info(f"添加装备类型筛选: kindid IN {kindid}")
                
                # 宠物装备类型筛选（多选）
                if equip_type and len(equip_type) > 0:
                    query = query.filter(Equipment.equip_type.in_(equip_type))
                    logger.info(f"添加宠物装备类型筛选: equip_type IN {equip_type}")
                
                # 特技筛选（多选）
                if equip_special_skills and len(equip_special_skills) > 0:
                    query = query.filter(Equipment.special_skill.in_(equip_special_skills))
                    logger.info(f"添加特技筛选: special_skill IN {equip_special_skills}")
                
                # 特效筛选（多选，JSON数组格式）
                if equip_special_effect and len(equip_special_effect) > 0:
                    effect_conditions = []
                    for effect in equip_special_effect:
                        effect_conditions.append(
                            or_(
                                Equipment.special_effect.like(f'[{effect}]'),
                                Equipment.special_effect.like(f'[{effect},%'),
                                Equipment.special_effect.like(f'%,{effect},%'),
                                Equipment.special_effect.like(f'%,{effect}]')
                            )
                        )
                    query = query.filter(or_(*effect_conditions))
                    logger.info(f"添加特效筛选: {equip_special_effect}")
                
                # 套装筛选
                if suit_effect:
                    query = query.filter(Equipment.suit_effect == suit_effect)
                    logger.info(f"添加套装筛选: suit_effect = {suit_effect}")
                    
                if suit_added_status:
                    query = query.filter(Equipment.suit_effect == suit_added_status)
                    logger.info(f"添加套装附加状态筛选: suit_effect = {suit_added_status}")
                    
                if suit_transform_skills:
                    query = query.filter(Equipment.suit_effect == suit_transform_skills)
                    logger.info(f"添加套装变身术筛选: suit_effect = {suit_transform_skills}")
                    
                if suit_transform_charms:
                    query = query.filter(Equipment.suit_effect == suit_transform_charms)
                    logger.info(f"添加套装变化咒筛选: suit_effect = {suit_transform_charms}")
                
                # 宝石筛选
                if gem_value:
                    gem_conditions = or_(
                        Equipment.gem_value.like(f'[{gem_value}]'),
                        Equipment.gem_value.like(f'[{gem_value},%'),
                        Equipment.gem_value.like(f'%,{gem_value},%'),
                        Equipment.gem_value.like(f'%,{gem_value}]')
                    )
                    query = query.filter(gem_conditions)
                    logger.info(f"添加宝石筛选: gem_value = {gem_value}")
                    
                if gem_level is not None:
                    query = query.filter(Equipment.gem_level >= gem_level)
                    logger.info(f"添加宝石等级筛选: gem_level >= {gem_level}")

            # 获取总数
            total = query.count()
            logger.info(f"查询到的总数: {total}")
            
            # 排序
            order_by = Equipment.update_time.desc()  # 默认按更新时间倒序
            if sort_by and sort_order:
                allowed_sort_by = [
                    'price', 'highlight', 'dynamic_tags', 'gem_level', 'jinglian_level', 'xiang_qian_level',
                    'special_effect', 'suit_effect', 'agg_added_attrs', 'equip_level', 'all_damage', 
                    'init_damage', 'init_wakan', 'init_defense', 'init_hp', 'init_dex', 'create_time_equip', 
                    'selling_time', 'special_skill', 'server_name', 'equip_name', 'seller_nickname', 'zongshang'
                ]
                if sort_by in allowed_sort_by and sort_order.lower() in ['asc', 'desc']:
                    sort_column = getattr(Equipment, sort_by)
                    order_by = sort_column.asc() if sort_order.lower() == 'asc' else sort_column.desc()

            # 分页查询 - 当使用equip_sn_list时，限制返回数量
            if equip_sn_list is not None and len(equip_sn_list) > 0:
                # 使用equip_sn_list时，直接返回所有匹配的装备，但限制在page_size内
                equipments = query.order_by(order_by).limit(page_size).all()
                logger.info(f"equip_sn_list模式：查询到的装备数量: {len(equipments)}")
            else:
                # 正常分页查询
                offset = (page - 1) * page_size
                equipments = query.order_by(order_by).offset(offset).limit(page_size).all()
                logger.info(f"正常分页模式：查询到的装备数量: {len(equipments)}")
            
            total_pages = (total + page_size - 1) // page_size
            
            # 转换为字典格式
            equipment_list = []
            for equipment in equipments:
                equipment_dict = {}
                for column in equipment.__table__.columns:
                    value = getattr(equipment, column.name)
                    if isinstance(value, datetime):
                        equipment_dict[column.name] = value.isoformat()
                    else:
                        equipment_dict[column.name] = value
                equipment_list.append(equipment_dict)
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "data": equipment_list,
                "start_date": start_date,
                "end_date": end_date,
            }

        except Exception as e:
            logger.error(f"获取装备列表时出错: {e}")
            return {"error": str(e)}

    def get_equipment_details(self, equip_sn: str) -> Optional[Dict]:
        """获取单个装备的详细信息"""
        try:
            
            # 使用SQLAlchemy ORM
            equipment = db.session.query(Equipment).filter_by(equip_sn=equip_sn).first()
            
            if equipment:
                equipment_dict = {}
                for column in equipment.__table__.columns:
                    value = getattr(equipment, column.name)
                    if isinstance(value, datetime):
                        equipment_dict[column.name] = value.isoformat()
                    else:
                        equipment_dict[column.name] = value
                return equipment_dict
            return None

        except Exception as e:
            logger.error(f"获取装备详情时出错: {e}")
            return None

    def _get_equipment_by_eid(self, eid: str) -> Optional[Dict]:
        """通过eid查询完整的装备信息"""
        try:
            # 使用SQLAlchemy ORM
            equipment = db.session.query(Equipment).filter_by(eid=eid).first()
            
            if equipment:
                equipment_dict = {}
                for column in equipment.__table__.columns:
                    value = getattr(equipment, column.name)
                    if isinstance(value, datetime):
                        equipment_dict[column.name] = value.isoformat()
                    else:
                        equipment_dict[column.name] = value
                return equipment_dict
            return None
            
        except Exception as e:
            logger.error(f"通过eid获取装备信息时出错: {e}")
            return None

    def _get_equipment_by_equip_sn(self, equip_sn: str) -> Optional[Dict]:
        """通过equip_sn查询完整的装备信息"""
        try:
            # 使用SQLAlchemy ORM
            equipment = db.session.query(Equipment).filter_by(equip_sn=equip_sn).first()
            
            if equipment:
                equipment_dict = {}
                for column in equipment.__table__.columns:
                    value = getattr(equipment, column.name)
                    if isinstance(value, datetime):
                        equipment_dict[column.name] = value.isoformat()
                    else:
                        equipment_dict[column.name] = value
                return equipment_dict
            return None
            
        except Exception as e:
            logger.error(f"通过equip_sn获取装备信息时出错: {e}")
            return None

    def find_equipment_anchors(self, equipment_data: Dict, 
                              similarity_threshold: float = 0.7,
                              max_anchors: int = 30) -> Dict:
        """寻找装备市场锚点"""
        try:
            if not self.evaluator:
                return {
                    "error": "装备锚点估价器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 根据kindid获取对应的特征提取器
            kindid = equipment_data.get('kindid', 0)
            if kindid == 0:
                i_type = equipment_data.get('iType', 0)
                if i_type > 0:
                    kindid = self._get_kindid_from_itype(kindid, i_type)

            feature_extractor = self._get_feature_extractor(kindid)
            
            if not feature_extractor:
                extractor_type = "灵饰" if is_lingshi(kindid) else "宠物装备" if is_pet_equip(kindid) else "装备"
                return {
                    "error": f"{extractor_type}特征提取器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 使用特征提取器提取特征
            try:
                equipment_features = feature_extractor.extract_features(equipment_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in equipment_data:
                equipment_features['equip_sn'] = equipment_data['equip_sn']
            
            # 验证必要的特征字段
            required_fields = ['equip_level', 'kindid']
            missing_fields = [field for field in required_fields if field not in equipment_features]
            if missing_fields:
                return {
                    "error": f"提取的特征缺少必要字段: {', '.join(missing_fields)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 验证参数范围
            if not 0.0 <= similarity_threshold <= 1.0:
                return {
                    "error": "相似度阈值必须在0.0-1.0之间",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            if not 1 <= max_anchors <= 100:
                return {
                    "error": "最大锚点数量必须在1-100之间",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 调用锚点查找方法
            anchors = self.evaluator.find_market_anchors(
                target_features=equipment_features,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            # 格式化返回结果
            result = {
                "anchor_count": len(anchors),
                "similarity_threshold": similarity_threshold,
                "anchors": []
            }
            
            # 处理锚点数据
            for anchor in anchors:
                anchor_equip_sn = anchor.get("equip_sn")
                
                # 通过equip_sn查询完整的装备信息
                full_equipment_info = None
                if anchor_equip_sn:
                    full_equipment_info = self._get_equipment_by_equip_sn(anchor_equip_sn)
                
                # 组合锚点信息和完整装备信息
                if full_equipment_info:
                    anchor_info = {
                        **full_equipment_info,
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                    }
                else:
                    # 如果无法获取完整信息，使用基础信息
                    anchor_info = {
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                        "price": float(anchor.get("price", 0)),
                        "equip_name": "未知装备",
                        "server_name": "未知服务器",
                        "equip_level": 0,
                        "special_skill": 0,
                        "suit_effect": 0,
                    }
                result["anchors"].append(anchor_info)
            
            # 添加统计信息
            if anchors:
                prices = [float(anchor["price"]) for anchor in anchors]
                similarities = [float(anchor["similarity"]) for anchor in anchors]
                
                result["statistics"] = {
                    "price_range": {
                        "min": float(min(prices)),
                        "max": float(max(prices))
                    },
                    "similarity_range": {
                        "min": round(float(min(similarities)), 3),
                        "max": round(float(max(similarities)), 3),
                        "avg": round(float(sum(similarities) / len(similarities)), 3)
                    }
                }
            else:
                result["statistics"] = {
                    "price_range": {"min": 0, "max": 0},
                    "similarity_range": {"min": 0, "max": 0, "avg": 0}
                }
                result["message"] = "未找到符合条件的市场锚点，建议降低相似度阈值"
            
            return result
            
        except Exception as e:
            logger.error(f"查找锚点时发生错误: {e}")
            return {
                "error": f"查找锚点时发生错误: {str(e)}",
                "anchors": [],
                "anchor_count": 0
            }

    def get_equipment_valuation(self, equipment_data: Dict,
                               strategy: str = 'fair_value',
                               similarity_threshold: float = 0.7,
                               max_anchors: int = 30) -> Dict:
        """获取装备估价"""
        try:
            if not self.evaluator:
                return {
                    "error": "装备锚点估价器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 根据kindid获取对应的特征提取器
            kindid = equipment_data.get('kindid', 0)
            if kindid == 0:
                i_type = equipment_data.get('iType', 0)
                if i_type > 0:
                    kindid = self._get_kindid_from_itype(kindid, i_type)

            feature_extractor = self._get_feature_extractor(kindid)
            
            if not feature_extractor:
                extractor_type = "灵饰" if is_lingshi(kindid) else "宠物装备" if is_pet_equip(kindid) else "装备"
                return {
                    "error": f"{extractor_type}特征提取器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 使用特征提取器提取特征
            try:
                equipment_features = feature_extractor.extract_features(equipment_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in equipment_data:
                equipment_features['equip_sn'] = equipment_data['equip_sn']
            
            # 验证策略参数
            valid_strategies = ['fair_value', 'competitive', 'premium']
            if strategy not in valid_strategies:
                return {
                    "error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 验证相似度阈值和最大锚点数量
            if not 0.0 <= similarity_threshold <= 1.0:
                return {
                    "error": "相似度阈值必须在0.0-1.0之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            if not 1 <= max_anchors <= 100:
                return {
                    "error": "最大锚点数量必须在1-100之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 调用估价方法
            result = self.evaluator.calculate_value(
                target_features=equipment_features,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            # 格式化返回结果
            if "error" in result:
                # 估价失败时，仍然返回包含feature等信息的完整结构，但标记为失败
                return {
                    "error": result.get("error", "估价失败"),  # 保留错误信息
                    "anchor_count": 0,
                    "anchors": [],
                    "confidence": 0.0,
                    "equip_sn": equipment_features.get("equip_sn", ""),
                    "estimated_price": 0,
                    "estimated_price_yuan": 0,
                    "feature": equipment_features,
                    "invalid_item": False,
                    "max_anchors": max_anchors,
                    "price_range": {
                        "max": 0,
                        "mean": 0,
                        "median": 0,
                        "min": 0
                    },
                    "similarity_threshold": similarity_threshold,
                    "skip_reason": result.get("error", "估价失败"),
                    "strategy": strategy
                }
            
            estimated_price = result.get("estimated_price", 0)
            anchor_count = result.get("anchor_count", 0)
            
            return {
                "estimated_price": estimated_price,
                "estimated_price_yuan": round(estimated_price / 100, 2),
                "strategy": strategy,
                "anchor_count": anchor_count,
                "anchors": result.get('anchors', []),
                "confidence": result.get("confidence", 0),
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "price_range": result.get("price_range", {}),
                "skip_reason": result.get("skip_reason", ""),
                "invalid_item": result.get("invalid_item", False),
                "feature": equipment_features,
                "equip_sn": result.get("equip_sn", "")  # 添加装备序列号
            }
            
        except Exception as e:
            logger.error(f"估价时发生错误: {e}")
            return {
                "error": f"估价时发生错误: {str(e)}",
                "anchor_count": 0,
                "confidence": 0.0,
                "equip_sn": equipment_data.get("equip_sn", "") if 'equipment_data' in locals() else "",
                "estimated_price": 0,
                "estimated_price_yuan": 0,
                "feature": equipment_features if 'equipment_features' in locals() else {},
                "invalid_item": False,
                "max_anchors": max_anchors,
                "price_range": {
                    "max": 0,
                    "mean": 0,
                    "median": 0,
                    "min": 0
                },
                "similarity_threshold": similarity_threshold,
                "skip_reason": f"估价时发生错误: {str(e)}",
                "strategy": strategy
            }

    def batch_equipment_valuation(self, equipment_list: List[Dict], 
                                 strategy: str = 'fair_value',
                                 similarity_threshold: float = 0.7,
                                 max_anchors: int = 30,
                                 verbose: bool = False) -> Dict:
        """批量装备估价"""
        try:
            logger.info(f"开始批量装备估价，装备数量: {len(equipment_list)}，策略: {strategy}，详细日志: {verbose}")
            
            if not equipment_list:
                return {
                    "error": "装备列表为空",
                    "results": []
                }
            
            # 提取装备特征
            equip_features_list = []
            
            for i, equipment_data in enumerate(equipment_list):
                try:
                    # 获取kindid和iType，使用统一方法处理
                    kindid = equipment_data.get('kindid', 0)
                    i_type = equipment_data.get('iType', 0)
                    
                    # 统一处理kindid获取逻辑
                    kindid = self._get_kindid_from_itype(kindid, i_type)
                    if kindid > 0:
                        equipment_data['kindid'] = kindid
                        logger.debug(f"第{i+1}个装备获取到kindid: {kindid}")
                    
                    feature_extractor = self._get_feature_extractor(kindid)
                    
                    if not feature_extractor:
                        extractor_type = "灵饰" if is_lingshi(kindid) else "宠物装备" if is_pet_equip(kindid) else "装备"
                        logger.warning(f"第{i+1}个装备的{extractor_type}特征提取器未初始化")
                        continue
                    
                    # 使用特征提取器提取特征
                    if kindid==PET_EQUIP_KINDID:
                        equipment_data = {
                            'kindid':kindid,
                            'desc':equipment_data.get('cDesc',equipment_data.get('desc','')),
                        }
                    equipment_features = feature_extractor.extract_features(equipment_data)
                    
                    # 确保equip_sn信息被正确传递
                    if 'equip_sn' in equipment_data:
                        equipment_features['equip_sn'] = equipment_data['equip_sn']
                    
                    # 添加原始装备数据用于后续处理
                    equipment_features['index'] = i
                    
                    equip_features_list.append(equipment_features)
                    
                except Exception as e:
                    logger.error(f"第{i+1}个装备特征提取失败: {e}")
                    continue
            
            if not equip_features_list:
                return {
                    "error": "所有装备特征提取失败",
                    "results": []
                }
            # 调用装备估价器的批量估价方法，传递 verbose 参数
            batch_results = self.evaluator.batch_valuation(
                equip_features_list, 
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors,
                verbose=verbose
            )
            
            # 处理批量估价结果
            processed_results = []
            for result in batch_results:
                if "error" in result:
                    # 处理错误情况，按照统一格式返回，包含feature等字段
                    processed_result = {
                        "index": result.get("equip_index", 0),
                        "anchor_count": 0,
                        "anchors": [],
                        "confidence": 0.0,
                        "equip_sn": result.get("equip_sn", ""),
                        "estimated_price": 0,
                        "estimated_price_yuan": 0,
                        "feature": result.get("feature", {}),
                        "invalid_item": False,
                        "max_anchors": max_anchors,
                        "price_range": {
                            "max": 0,
                            "mean": 0,
                            "median": 0,
                            "min": 0
                        },
                        "similarity_threshold": similarity_threshold,
                        "error": result.get("error", "估价失败"),
                        "strategy": strategy,
                        "kindid": result.get("kindid", "")
                    }
                else:
                    # 处理成功情况，按照统一格式返回
                    estimated_price = result.get("estimated_price", 0)
                    processed_result = {
                        "index": result.get("equip_index", 0),
                        "anchor_count": result.get("anchor_count", 0),
                        "anchors": result.get("anchors", []),
                        "confidence": result.get("confidence", 0),
                        "equip_sn": result.get("equip_sn", ""),
                        "estimated_price": estimated_price,
                        "estimated_price_yuan": round(estimated_price / 100, 2),
                        "feature": result.get("feature", {}),
                        "invalid_item": result.get("invalid_item", False),
                        "max_anchors": max_anchors,
                        "price_range": result.get("price_range", {}),
                        "similarity_threshold": similarity_threshold,
                        "skip_reason": result.get("skip_reason", ""),
                        "strategy": strategy,
                        "kindid": result.get("kindid", "")
                    }
                
                processed_results.append(processed_result)
            
            # 按原始索引排序
            processed_results.sort(key=lambda x: x["index"])
            
            return {
                "success": True,
                "total_count": len(equipment_list),
                "success_count": len([r for r in processed_results if "error" not in r]),
                "strategy": strategy,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "verbose": verbose,
                "results": processed_results
            }
            
        except Exception as e:
            logger.error(f"批量装备估价失败: {e}")
            return {
                "error": f"批量装备估价失败: {str(e)}",
                "results": []
            }
    
    def extract_features(self, equipment_data: Dict, data_type: str = 'equipment') -> Dict:
        """提取装备特征"""
        try:
            if not self.unified_extractor:
                return {
                    "error": "统一特征提取器未初始化",
                    "features": {}
                }
            
            # 使用统一特征提取器提取特征
            features,kindid,extractor_type = self.unified_extractor.extract_features(equipment_data, data_type)
            
            return {
                "features": features,
                "data_type": data_type,
                "kindid": kindid,
                "extractor_type": extractor_type
            }
            
        except Exception as e:
            logger.error(f"提取装备特征时发生错误: {e}")
            return {
                "error": f"提取装备特征时发生错误: {str(e)}",
                "features": {}
            }
    
    def extract_features_batch(self, equipment_list: List[Dict], data_type: str = 'equipment') -> Dict:
        """批量提取装备特征"""
        try:
            if not self.unified_extractor:
                return {
                    "error": "统一特征提取器未初始化",
                    "features_list": []
                }
            
            if not equipment_list:
                return {
                    "error": "装备列表为空",
                    "features_list": []
                }
            
            # 使用统一特征提取器批量提取特征
            features_list = self.unified_extractor.extract_features_batch(equipment_list, data_type)
            
            return {
                "features_list": features_list,
                "data_type": data_type,
                "total_count": len(equipment_list),
                "success_count": len([f for f in features_list if f])
            }
            
        except Exception as e:
            logger.error(f"批量提取装备特征时发生错误: {e}")
            return {
                "error": f"批量提取装备特征时发生错误: {str(e)}",
                "features_list": []
            }
    
    def get_extractor_info(self, kindid: int) -> Dict:
        """获取指定kindid的提取器信息"""
        try:
            if not self.unified_extractor:
                return {
                    "error": "统一特征提取器未初始化"
                }
            
            info = self.unified_extractor.get_extractor_info(kindid)
            return info
            
        except Exception as e:
            logger.error(f"获取提取器信息时发生错误: {e}")
            return {
                "error": f"获取提取器信息时发生错误: {str(e)}"
            }
    
    def get_supported_kindids(self) -> Dict:
        """获取支持的kindid列表"""
        try:
            if not self.unified_extractor:
                return {
                    "error": "统一特征提取器未初始化"
                }
            
            supported_kindids = self.unified_extractor.get_supported_kindids()
            return supported_kindids
            
        except Exception as e:
            logger.error(f"获取支持的kindid列表时发生错误: {e}")
            return {
                "error": f"获取支持的kindid列表时发生错误: {str(e)}"
            }

    def delete_equipment(self, equip_sn: str) -> Dict:
        """删除指定装备"""
        try:
            
            # 使用SQLAlchemy ORM
            equipment = db.session.query(Equipment).filter_by(equip_sn=equip_sn).first()
            
            if not equipment:
                return {
                    "error": f"未找到装备序列号为 {equip_sn} 的装备",
                    "deleted": False
                }
            
            db.session.delete(equipment)
            db.session.commit()
            
            logger.info(f"成功删除装备: {equip_sn}")
            return {
                "deleted": True,
                "equip_sn": equip_sn,
                "message": "装备删除成功"
            }
                    
        except Exception as e:
            logger.error(f"删除装备时发生错误: {e}")
            return {
                "error": f"删除装备时发生错误: {str(e)}",
                "deleted": False
            }

    def get_lingshi_config(self) -> Dict:
        """获取灵饰数据"""
        try:
            from src.evaluator.market_anchor.equip.constant import get_lingshi_config
            
            # 从constant模块获取灵饰数据
            lingshi_data = get_lingshi_config()
            
            return {"data": lingshi_data}
            
        except Exception as e:
            return {"error": f"获取灵饰数据失败: {str(e)}"}

    def get_weapon_config(self) -> Dict:
        """获取武器数据"""
        try:
            from src.evaluator.market_anchor.equip.constant import get_weapon_config
            
            # 从constant模块获取武器数据
            weapon_data = get_weapon_config()
            
            return {"data": weapon_data}
            
        except Exception as e:
            return {"error": f"获取武器数据失败: {str(e)}"}

    def get_pet_equip_config(self) -> Dict:
        """获取宠物装备数据"""
        try:
            from src.evaluator.market_anchor.equip.constant import get_pet_equip_config
            
            # 从constant模块获取宠物装备数据
            pet_equip_data = get_pet_equip_config()
            
            return {"data": pet_equip_data}

        except Exception as e:
            return {"error": f"获取宠物装备数据失败: {str(e)}"}
    
    def get_equip_config(self) -> Dict:
        """获取装备数据"""
        try:
            from src.evaluator.market_anchor.equip.constant import get_config
            
            # 从constant模块获取装备数据
            equip_data = get_config()

            return {"data": equip_data}

        except Exception as e:
            return {"error": f"获取装备数据失败: {str(e)}"}
    
    def incremental_update_cache(self, update_type: str = 'auto', last_update_time: Optional[str] = None) -> Dict:
        """增量更新装备缓存"""
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            from datetime import datetime
            
            # 获取装备市场数据采集器实例
            collector = EquipMarketDataCollector.get_instance()
            
            if update_type == 'auto':
                # 自动检测并更新
                success = collector.auto_incremental_update()
            elif update_type == 'time':
                # 基于时间戳更新
                if last_update_time:
                    try:
                        last_time = datetime.fromisoformat(last_update_time)
                        success = collector.incremental_update(last_time)
                    except ValueError:
                        return {"error": "时间格式错误，请使用ISO格式"}
                else:
                    success = collector.incremental_update()
            else:
                return {"error": f"不支持的更新类型: {update_type}"}
            
            if success:
                # 获取更新后的状态
                status = collector.get_incremental_update_status()
                return {
                    "success": True,
                    "message": "增量更新成功",
                    "status": status
                }
            else:
                return {"error": "增量更新失败"}
            
        except Exception as e:
            logger.error(f"增量更新装备缓存失败: {str(e)}")
            return {"error": f"增量更新装备缓存失败: {str(e)}"}
    
    def get_incremental_update_status(self) -> Dict:
        """获取增量更新状态"""
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            
            # 获取装备市场数据采集器实例
            collector = EquipMarketDataCollector.get_instance()
            
            # 获取增量更新状态
            status = collector.get_incremental_update_status()
            
            return status
            
        except Exception as e:
            logger.error(f"获取增量更新状态失败: {str(e)}")
            return {"error": f"获取增量更新状态失败: {str(e)}"}
    
    def auto_incremental_update(self) -> Dict:
        """自动增量更新"""
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            
            # 获取装备市场数据采集器实例
            collector = EquipMarketDataCollector.get_instance()
            
            # 执行自动增量更新
            success = collector.auto_incremental_update()
            
            if success:
                # 获取更新后的状态
                status = collector.get_incremental_update_status()
                return {
                    "success": True,
                    "message": "自动增量更新成功",
                    "status": status
                }
            else:
                return {"error": "自动增量更新失败"}
            
        except Exception as e:
            logger.error(f"自动增量更新失败: {str(e)}")
            return {"error": f"自动增量更新失败: {str(e)}"}
    
    def force_incremental_update(self) -> Dict:
        """强制增量更新"""
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            
            # 获取装备市场数据采集器实例
            collector = EquipMarketDataCollector.get_instance()
            
            # 执行强制增量更新
            success = collector.force_incremental_update()
            
            if success:
                # 获取更新后的状态
                status = collector.get_incremental_update_status()
                return {
                    "success": True,
                    "message": "强制增量更新成功",
                    "status": status
                }
            else:
                return {"error": "强制增量更新失败"}
            
        except Exception as e:
            logger.error(f"强制增量更新失败: {str(e)}")
            return {"error": f"强制增量更新失败: {str(e)}"}


equipment_service = EquipmentService()
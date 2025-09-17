#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宠物服务
"""

import os
import json
import sys
import uuid
import threading
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging



from src.utils.project_path import get_project_root, get_data_path
from src.database import db
from src.models.pet import Pet
from sqlalchemy import and_, or_, func, text

# 导入任务管理器
from .task_manager import task_manager

logger = logging.getLogger(__name__)

from evaluator.mark_anchor.pet.index import PetMarketAnchorEvaluator
from evaluator.feature_extractor.pet_feature_extractor import PetFeatureExtractor
from evaluator.constants.equipment_types import PET_EQUIP_KINDID

class BatchUpdateTask:
    """批量更新任务状态管理"""

    def __init__(self, task_id: str, year: int, month: int):
        self.task_id = task_id
        self.year = year
        self.month = month
        self.status = 'pending'  # pending, running, completed, failed, cancelled
        self.total_count = 0
        self.processed_count = 0
        self.updated_count = 0
        self.current_batch = 0
        self.total_batches = 0
        self.error_message = ''
        self.start_time = None
        self.end_time = None
        self.batch_size = 5  # 每批处理50条
        self._lock = threading.Lock()
        self._stop_requested = False

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'task_id': self.task_id,
            'year': self.year,
            'month': self.month,
            'status': self.status,
            'total_count': self.total_count,
            'processed_count': self.processed_count,
            'updated_count': self.updated_count,
            'current_batch': self.current_batch,
            'total_batches': self.total_batches,
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'progress_percentage': self.get_progress_percentage()
        }

    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.total_count == 0:
            return 0.0
        return round((self.processed_count / self.total_count) * 100, 2)

    def request_stop(self):
        """请求停止任务"""
        with self._lock:
            self._stop_requested = True

    def is_stop_requested(self) -> bool:
        """检查是否请求停止"""
        with self._lock:
            return self._stop_requested


# 全局任务管理器
_task_manager = {}
_task_lock = threading.Lock()


def get_task_manager():
    """获取任务管理器"""
    global _task_manager
    return _task_manager


def add_task(task: BatchUpdateTask):
    """添加任务"""
    global _task_manager
    with _task_lock:
        _task_manager[task.task_id] = task


def remove_task(task_id: str):
    """移除任务"""
    global _task_manager
    with _task_lock:
        if task_id in _task_manager:
            del _task_manager[task_id]


def get_task(task_id: str) -> Optional[BatchUpdateTask]:
    """获取任务"""
    global _task_manager
    with _task_lock:
        return _task_manager.get(task_id)


class PetService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = get_project_root()

        # 初始化特征提取器
        self.pet_feature_extractor = None

        if PetFeatureExtractor:
            try:
                self.pet_feature_extractor = PetFeatureExtractor()
                logger.info("宠物特征提取器初始化成功")
            except Exception as e:
                logger.error(f"宠物特征提取器初始化失败: {e}")

        # 初始化宠物锚点估价器
        self.evaluator = None
        if PetMarketAnchorEvaluator:
            try:
                self.evaluator = PetMarketAnchorEvaluator()
                logger.info("宠物锚点估价器初始化成功")
            except Exception as e:
                logger.error(f"宠物锚点估价器初始化失败: {e}")

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


    def get_pets(self, page: int = 1, page_size: int = 10, 
                 start_date: Optional[str] = None, end_date: Optional[str] = None,
                 level_min: Optional[int] = None, level_max: Optional[int] = None,
                 price_min: Optional[int] = None, price_max: Optional[int] = None,
                 pet_skills: Optional[List[str]] = None,
                 pet_growth: Optional[str] = None,
                 pet_skill_count: Optional[int] = None,
                 pet_lx: Optional[int] = None,
                 pet_texing: Optional[List[str]] = None,
                 equip_list_amount_warning: Optional[int] = None,
                 equip_sn: Optional[str] = None,
                 warning_rate: Optional[float] = 0.4,
                 sort_by: Optional[str] = 'price', sort_order: Optional[str] = 'asc') -> Dict:
        """获取分页的宠物列表
            🎯 直接使用的字段（从后端API返回的数据）
            基础信息字段：
            eid - 宠物eid
            equip_sn -  宠物序列号
            equip_name -  宠物名称
            equip_face_img - 装备头像图片
            server_name - 服务器名称
            price - 价格
            level - 等级
            role_grade_limit - 参战等级限制
            growth - 成长值
            lx - 灵性值
            equip_list - 宠物装备列表（JSON字符串）
            equip_list_amount - 宠物装备估算金额
            desc - 宠物描述信息（用于解析petData）
            `equip_level` - 装备等级
            `is_baobao` - 是否宝宝
            `sp_skill` - 特殊技能
            `all_skill` - 所有技能（字符串）
            `evol_skill_list` - 进化技能列表（JSON数组）
            `neidan` - 内丹信息（JSON数组）
            `highlight` - 亮点（字符串）
            `dynamic_tags` - 动态（字符串）
            `area_name` - 区域名称
            `server_name` - 服务器名称
            `serverid` - 服务器ID

        """
        try:
            start_date, end_date = self._validate_date_range(start_date, end_date)
            
            # 构建SQLAlchemy查询
            query = db.session.query(Pet)

            # 添加调试日志
            logger.info(
                f"开始处理筛选条件，参数: level_min={level_min}, level_max={level_max}, price_min={price_min}, price_max={price_max}")
            
            # 时间范围筛选
            if start_date:
                query = query.filter(func.date(Pet.selling_time) >= start_date)
                logger.info(f"添加开始日期筛选: selling_time >= {start_date}")
            if end_date:
                query = query.filter(func.date(Pet.selling_time) <= end_date)
                logger.info(f"添加结束日期筛选: selling_time <= {end_date}")

            # 基础筛选条件
            if level_min is not None:
                query = query.filter(Pet.level >= level_min)
            if level_max is not None:
                query = query.filter(Pet.level <= level_max)
            if price_min is not None:
                query = query.filter(Pet.price >= price_min * 100)  # 前端传元，后端存分
            if price_max is not None:
                query = query.filter(Pet.price <= price_max * 100)

            # 宠物技能筛选（多选）
            if pet_skills and len(pet_skills) > 0:
                skill_conditions = []
                for skill in pet_skills:
                    # 使用all_skill字段进行搜索，处理管道符分隔格式 "305|316|304|301"
                    skill_conditions.append(
                        or_(
                            Pet.all_skill == skill,              # 只有这一个技能："305"
                            Pet.all_skill.like(f'{skill}|%'),    # 在开头："305|x|..."
                            Pet.all_skill.like(f'%|{skill}|%'),  # 在中间："|x|305|y|"
                            Pet.all_skill.like(f'%|{skill}')     # 在结尾："|x|y|305"
                        )
                    )
                query = query.filter(and_(*skill_conditions))
                logger.info(f"添加宠物技能筛选: {pet_skills}")

            # 其他筛选条件
            if pet_growth:
                query = query.filter(Pet.growth >= pet_growth)
                logger.info(f"添加成长筛选: growth >= {pet_growth}")
            # 灵性值
            if pet_lx:
                query = query.filter(Pet.lx >= pet_lx)
                logger.info(f"添加灵性筛选: lx >= {pet_lx}")

            # 特性筛选（多选）
            if pet_texing and len(pet_texing) > 0:
                texing_conditions = []
                for texing_id in pet_texing:
                    # 使用texing字段进行搜索，处理JSON格式 {"id": 723, "name": "洞察", ...}
                    texing_conditions.append(Pet.texing.like(f'%"id": {texing_id}%'))
                query = query.filter(or_(*texing_conditions))
                logger.info(f"添加特性筛选: {pet_texing}")

            if pet_skill_count is not None:
                # 根据all_skills字段的长度过滤，计算管道符分隔的技能数量
                query = query.filter(
                    func.length(Pet.all_skill) - func.length(func.replace(Pet.all_skill, '|', '')) + 1 >= pet_skill_count
                )
                logger.info(f"添加技能数量筛选: 技能数量 >= {pet_skill_count}")

            # 估价异常筛选
            if equip_list_amount_warning is not None:
                if equip_list_amount_warning == 1:
                    # 筛选估价异常的宠物：
                    # 1. equip_list_amount_warning = 1 (手动标记的异常)
                    # 2. equip_list_amount > 0 且 equip_list_amount/price > 40% (装备估价占比过高)
                    query = query.filter(
                        or_(
                            Pet.equip_list_amount_warning == 1,
                            and_(
                                Pet.equip_list_amount > 0,
                                Pet.price > 0,
                                func.cast(Pet.equip_list_amount, func.FLOAT) / func.cast(Pet.price, func.FLOAT) > warning_rate
                            )
                        )
                    )
                    logger.info(
                        f"添加估价异常筛选: equip_list_amount_warning = 1 或装备估价占比>{warning_rate*100}%")

            # equip_sn筛选
            if equip_sn:
                query = query.filter(Pet.equip_sn == equip_sn)
                logger.info(f"添加equip_sn筛选: {equip_sn}")

            # 计算总数
            total = query.count()

            # 计算分页
            total_pages = (total + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # 构建排序
            if sort_by == 'skill_count':
                # 按技能数量排序：计算all_skill字段中管道符的数量+1，处理空字符串情况
                skill_count_expr = func.case(
                    (or_(Pet.all_skill == '', Pet.all_skill.is_(None)), 0),
                    else_=func.length(Pet.all_skill) - func.length(func.replace(Pet.all_skill, '|', '')) + 1
                )
                if sort_order.lower() == 'asc':
                    query = query.order_by(skill_count_expr.asc())
                else:
                    query = query.order_by(skill_count_expr.desc())
            elif sort_by and sort_order:
                sort_column = getattr(Pet, sort_by, None)
                if sort_column:
                    if sort_order.lower() == 'asc':
                        query = query.order_by(sort_column.asc())
                    else:
                        query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(Pet.update_time.desc())  # 默认按更新时间倒序

            # 应用分页
            query = query.offset(offset).limit(page_size)

            # 执行查询
            pets = query.all()

            # 转换为字典列表
            pets_data = []
            all_equips = []
            # 检查哪些宠物需要重新计算装备估价
            pets_need_calculation = []
            # (pet_idx, equip_idx) -> all_equips index
            equip_calculation_map = []

            for pet_idx, pet in enumerate(pets):
                # 转换为字典
                pet_dict = {}
                for column in pet.__table__.columns:
                    value = getattr(pet, column.name)
                    if hasattr(value, 'isoformat'):  # datetime对象
                        pet_dict[column.name] = value.isoformat()
                    else:
                        pet_dict[column.name] = value
                
                pets_data.append(pet_dict)

                # 优先使用数据库中的装备估价
                db_equip_amount = pet_dict.get('equip_list_amount', 0)
                if db_equip_amount > 0:
                    # 数据库中有估价，直接使用
                    pet_dict['equip_list_amount'] = db_equip_amount
                    logger.debug(
                        f"使用数据库中的装备估价: {pet_dict['equip_sn']} = {db_equip_amount}分")
                else:
                    # 数据库中无估价，需要重新计算
                    pets_need_calculation.append(pet_idx)

                    # 收集需要估价的装备
                    equip_list_raw = pet_dict.get('equip_list', '[]')
                    try:
                        equip_list = json.loads(equip_list_raw)
                    except Exception:
                        equip_list = []
                    for equip_idx in range(3):
                        equip = equip_list[equip_idx] if equip_idx < len(
                            equip_list) else None
                        if equip:
                            all_equips.append({
                                'kindid': PET_EQUIP_KINDID,
                                'desc': equip.get('desc', ''),
                            })
                            equip_calculation_map.append(
                                (pet_idx, equip_idx))

            # 批量估价需要重新计算的宠物装备
            equip_valuations = []
            if all_equips:
                from src.app.services.equipment_service import equipment_service
                try:
                    # 批量估价写死参数 TODO:
                    result = equipment_service.batch_equipment_valuation(
                        all_equips, 'fair_value', 0.8, 30)
                    if isinstance(result, dict):
                        equip_valuations = result.get('results', [])
                    else:
                        equip_valuations = result
                    logger.info(
                        f"批量装备估价完成，成功估价 {len(equip_valuations)} 个装备")
                except Exception as e:
                    import traceback
                    logger.warning(
                        f"批量装备估价时部分装备失败: {e} (type={type(e)})\n{traceback.format_exc()}")
                    equip_valuations = [{} for _ in all_equips]

            # 计算需要重新计算的宠物装备总价值
            for pet_idx in pets_need_calculation:
                pet = pets_data[pet_idx]
                equip_list_raw = pet.get('equip_list', '[]')
                try:
                    equip_list = json.loads(equip_list_raw)
                except Exception:
                    equip_list = []

                # 计算装备总价值
                equip_list_amount = 0
                equip_list_amount_warning = 0
                for equip_idx in range(3):
                    equip = equip_list[equip_idx] if equip_idx < len(
                        equip_list) else None
                    if equip:
                        try:
                            idx = equip_calculation_map.index(
                                (pet_idx, equip_idx))
                            if 0 <= idx < len(equip_valuations):
                                price_info = equip_valuations[idx]
                                # 累加装备估价
                                estimated_price = price_info.get(
                                    'estimated_price', 0)
                                confidence = price_info.get(
                                    'confidence', 0)
                                if confidence == 0:
                                    equip_list_amount_warning = 1
                                if isinstance(estimated_price, (int, float)):
                                    equip_list_amount += estimated_price
                            else:
                                logger.warning(
                                    f"装备估价索引超界: idx={idx}, len(equip_valuations)={len(equip_valuations)}")
                        except Exception as e:
                            logger.warning(f"装备估价回填异常: {e}")

                # 设置装备总价值字段（单位：分）
                pet['equip_list_amount'] = equip_list_amount

                # 更新数据库中的装备估价
                self.update_pet_equip_amount(
                    pet['equip_sn'], equip_list_amount, equip_list_amount_warning)

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "data": pets_data,  # 已经转换为字典列表，包含equip_list_amount
                "start_date": start_date,
                "end_date": end_date
            }

        except Exception as e:
            import traceback
            logger.error(
                f"获取宠物列表时出错: {e} (type={type(e)})\n{traceback.format_exc()}")
            return {"error": f"获取宠物列表时出错: {str(e)}"}

    def update_pet_equip_amount(self, equip_sn: str, equip_list_amount: int, equip_list_amount_warning: int) -> bool:
        """更新宠物装备总价值到MySQL数据库"""
        try:
            # 查找宠物记录
            pet = db.session.query(Pet).filter_by(equip_sn=equip_sn).first()
            
            if pet:
                # 更新装备总价值
                pet.equip_list_amount = equip_list_amount
                pet.equip_list_amount_warning = equip_list_amount_warning
                pet.update_time = datetime.now()
                
                # 提交事务
                db.session.commit()
                
                logger.debug(f"更新宠物装备估价成功: {equip_sn} = {equip_list_amount}分")
                return True
            else:
                logger.warning(f"未找到宠物记录: {equip_sn}")
                return False

        except Exception as e:
            db.session.rollback()
            logger.error(f"更新宠物装备估价失败: {e}")
            return False

    def get_pet_details(self, equip_sn: str) -> Optional[Dict]:
        """获取宠物详情"""
        try:
            # 查找宠物记录
            pet = db.session.query(Pet).filter_by(equip_sn=equip_sn).first()
            
            if pet:
                # 转换为字典
                pet_dict = {}
                for column in pet.__table__.columns:
                    value = getattr(pet, column.name)
                    if hasattr(value, 'isoformat'):  # datetime对象
                        pet_dict[column.name] = value.isoformat()
                    else:
                        pet_dict[column.name] = value
                return pet_dict
            
            return None

        except Exception as e:
            logger.error(f"获取宠物详情时出错: {e}")
            return None

    def _get_pet_by_equip_sn(self, equip_sn: str) -> Optional[Dict]:
        """根据equip_sn获取宠物信息"""
        try:
            # 查找宠物记录
            pet = db.session.query(Pet).filter_by(equip_sn=equip_sn).first()
            
            if pet:
                # 转换为字典
                pet_dict = {}
                for column in pet.__table__.columns:
                    value = getattr(pet, column.name)
                    if hasattr(value, 'isoformat'):  # datetime对象
                        pet_dict[column.name] = value.isoformat()
                    else:
                        pet_dict[column.name] = value
                
                logger.debug(f"找到宠物: {equip_sn}")
                return pet_dict
            
            logger.debug(f"未找到宠物: {equip_sn}")
            return None

        except Exception as e:
            logger.error(f"根据equip_sn获取宠物信息时出错: {e}")
            return None

    def find_pet_anchors(self, pet_data: Dict, similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """寻找宠物市场锚点"""
        try:
            if not self.evaluator:
                return {"error": "宠物锚点估价器未初始化"}

            if not self.pet_feature_extractor:
                return {"error": "宠物特征提取器未初始化"}

            # 提取宠物特征
            pet_features = self.pet_feature_extractor.extract_features(
                pet_data)
            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in pet_data:
                pet_features['equip_sn'] = pet_data['equip_sn']
            # 查找锚点
            anchors = self.evaluator.find_market_anchors(
                pet_features,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )

            # 处理锚点数据
            processed_anchors = []
            for anchor in anchors:
                anchor_equip_sn = anchor.get("equip_sn")

                # 通过equip_sn查询完整的宠物信息
                full_pet_info = None
                if anchor_equip_sn:
                    full_pet_info = self._get_pet_by_equip_sn(anchor_equip_sn)

                # 组合锚点信息和完整宠物信息
                if full_pet_info:
                    # 使用纯宠物价格（已减去装备估价）
                    pet_price = float(anchor.get("price", 0))
                    total_price = float(anchor.get("total_price", pet_price))
                    equip_list_amount = float(
                        anchor.get("equip_list_amount", 0))

                    anchor_info = {
                        **full_pet_info,
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                        "pet_price": pet_price,  # 纯宠物价格
                        "total_price": total_price,  # 总价格
                        "equip_list_amount": equip_list_amount,  # 装备估价
                    }
                else:
                    # 如果无法获取完整信息，使用基础信息
                    pet_price = float(anchor.get("price", 0))
                    total_price = float(anchor.get("total_price", pet_price))
                    equip_list_amount = float(
                        anchor.get("equip_list_amount", 0))

                    anchor_info = {
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                        "price": pet_price,  # 纯宠物价格
                        "pet_price": pet_price,  # 纯宠物价格
                        "total_price": total_price,  # 总价格
                        "equip_list_amount": equip_list_amount,  # 装备估价
                        "equip_name": "未知宠物",
                        "server_name": "未知服务器",
                        "level": 0,
                        "growth": 0,
                        "all_skill": "",
                        "sp_skill": "0",
                        "is_baobao": "否",
                    }
                processed_anchors.append(anchor_info)

            return {
                "anchors": processed_anchors,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "found_count": len(processed_anchors)
            }

        except Exception as e:
            logger.error(f"查找宠物锚点时出错: {e}")
            return {"error": f"查找宠物锚点时出错: {str(e)}"}

    def get_pet_valuation(self, pet_data: Dict, strategy: str = 'fair_value',
                          similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取宠物估价"""
        try:
            if not self.evaluator:
                return {"error": "宠物锚点估价器未初始化"}
            if not self.pet_feature_extractor:
                return {"error": "宠物特征提取器未初始化"}

            # 策略校验
            valid_strategies = ['fair_value',
                                'market_price', 'weighted_average']
            if strategy not in valid_strategies:
                return {
                    "error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}"
                }
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0-1.0之间"}
            if not 1 <= max_anchors <= 100:
                return {"error": "最大锚点数量必须在1-100之间"}

            # 特征提取
            pet_features = self.pet_feature_extractor.extract_features(
                pet_data)
                
            # 装备单独估价
            equip_list_raw = pet_data.get('equip_list', '[]')
            try:
                equip_list = json.loads(equip_list_raw)
            except Exception:
                equip_list = []
            
            equip_valuations = []
            if len(equip_list) > 0:
                # 过滤有效的装备数据，参考其他地方的处理方式
                valid_equips = []
                for equip in equip_list:
                    if equip and isinstance(equip, dict) and 'desc' in equip:
                        valid_equips.append({
                            'kindid': PET_EQUIP_KINDID,  # 宠物装备类型ID
                            'desc': equip.get('desc', '')
                        })
                
                if valid_equips:
                    from src.app.services.equipment_service import equipment_service
                    try:
                        result = equipment_service.batch_equipment_valuation(
                            valid_equips, 'fair_value', 0.8, 30)
                        if isinstance(result, dict):
                            equip_valuations = result.get('results', [])
                        else:
                            equip_valuations = result
                        logger.info(
                            f"批量装备估价完成，成功估价 {len(equip_valuations)} 个装备")
                    except Exception as e:
                        import traceback
                        logger.warning(f"批量装备估价时部分装备失败: {e}")
                        equip_valuations = [{} for _ in valid_equips]
                else:
                    logger.info("没有有效的装备数据需要估价")
                    equip_valuations = []
            
            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in pet_data:
                pet_features['equip_sn'] = pet_data['equip_sn']

            # 估价
            result = self.evaluator.calculate_value(
                pet_features,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            # 检查是否有错误或无效物品
            if "error" in result:
                return {
                    "error": result["error"],
                    "estimated_price": 0,
                    "estimated_price_yuan": 0,
                    "skip_reason": result.get("skip_reason", "")
                }
            
            # 检查是否是无效物品（被跳过估价）
            if result.get("invalid_item", False):
                skip_reason = result.get("skip_reason", "")
                estimated_price = result.get("estimated_price", 0)
                return {
                    "estimated_price": estimated_price,
                    "estimated_price_yuan": round(estimated_price / 100, 2),
                    "strategy": strategy,
                    "anchor_count": 0,
                    "confidence": result.get("confidence", 0),
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "price_range": {},
                    "equip_valuations": equip_valuations,
                    "equip_estimated_price": sum(equip_val.get("estimated_price", 0) for equip_val in equip_valuations if isinstance(equip_val, dict)),
                    "skip_reason": skip_reason,
                    "invalid_item": True
                }
            
            estimated_price = result.get("estimated_price", 0)

            # 直接使用calculate_value返回的锚点信息，避免重复查找
            anchor_count = result.get("anchor_count", 0)

            return {
                "estimated_price": estimated_price,
                "estimated_price_yuan": round(estimated_price / 100, 2),
                "strategy": strategy,
                "anchor_count": anchor_count,
                "confidence": result.get("confidence", 0),
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "price_range": result.get("price_range", {}),
                "equip_valuations": equip_valuations,
                "equip_estimated_price": sum(equip_val.get("estimated_price", 0) for equip_val in equip_valuations if isinstance(equip_val, dict)),
                "skip_reason": result.get("skip_reason", ""),
                "invalid_item": False
            }
        except Exception as e:
            logger.error(f"获取宠物估价时出错: {e}")
            return {"error": f"获取宠物估价时出错: {str(e)}"}

    def update_pet_equip_valuation(self, equip_sn: str = None) -> Dict:
        """手动更新宠物装备估价

        Args:
            equip_sn: 宠物序列号，如果为None则更新所有宠物

        Returns:
            Dict: 更新结果
        """
        try:
            # 构建查询条件
            query = db.session.query(Pet)
            
            if equip_sn:
                query = query.filter(Pet.equip_sn == equip_sn)
            else:
                query = query.filter(
                    or_(
                        Pet.equip_list_amount == 0,
                        Pet.equip_list_amount.is_(None)
                    )
                )

            pets = query.all()
            if not pets:
                return {"message": "没有需要更新装备估价的宠物", "updated_count": 0}

            # 转换为字典列表
            pets_data = []
            for pet in pets:
                pet_dict = {}
                for column in pet.__table__.columns:
                    value = getattr(pet, column.name)
                    if hasattr(value, 'isoformat'):  # datetime对象
                        pet_dict[column.name] = value.isoformat()
                    else:
                        pet_dict[column.name] = value
                pets_data.append(pet_dict)

            # 收集所有需要估价的装备
            all_equips = []
            # (pet_idx, equip_idx) -> all_equips index
            equip_calculation_map = []

            for pet_idx, pet in enumerate(pets_data):
                equip_list_raw = pet.get('equip_list', '[]')
                try:
                    equip_list = json.loads(equip_list_raw)
                except Exception:
                    equip_list = []
                for equip_idx in range(3):
                    equip = equip_list[equip_idx] if equip_idx < len(
                        equip_list) else None
                    if equip:
                        all_equips.append({
                            'kindid': PET_EQUIP_KINDID,
                            'desc': equip.get('desc', ''),
                        })
                        equip_calculation_map.append((pet_idx, equip_idx))

            # 批量估价
            equip_valuations = []
            if all_equips:
                from src.app.services.equipment_service import equipment_service
                try:
                    result = equipment_service.batch_equipment_valuation(
                        all_equips, 'fair_value', 0.8, 30)
                    if isinstance(result, dict):
                        equip_valuations = result.get('results', [])
                    else:
                        equip_valuations = result
                    logger.info(
                        f"批量装备估价完成，成功估价 {len(equip_valuations)} 个装备")
                except Exception as e:
                    import traceback
                    logger.warning(f"批量装备估价时部分装备失败: {e}")
                    equip_valuations = [{} for _ in all_equips]

            # 计算装备总价值并更新数据库
            updated_count = 0
            for pet_idx, pet in enumerate(pets_data):
                equip_list_raw = pet.get('equip_list', '[]')
                try:
                    equip_list = json.loads(equip_list_raw)
                except Exception:
                    equip_list = []

                # 计算装备总价值
                equip_list_amount = 0
                equip_list_amount_warning = 0
                for equip_idx in range(3):
                    equip = equip_list[equip_idx] if equip_idx < len(
                        equip_list) else None
                    if equip:
                        try:
                            idx = equip_calculation_map.index(
                                (pet_idx, equip_idx))
                            if 0 <= idx < len(equip_valuations):
                                price_info = equip_valuations[idx]
                                estimated_price = price_info.get(
                                    'estimated_price', 0)
                                confidence = price_info.get(
                                    'confidence', 0)
                                if confidence == 0:
                                    equip_list_amount_warning = 1
                                if isinstance(estimated_price, (int, float)):
                                    equip_list_amount += estimated_price
                        except Exception as e:
                            logger.warning(f"装备估价回填异常: {e}")

                # 更新数据库
                if self.update_pet_equip_amount(pet['equip_sn'], equip_list_amount, equip_list_amount_warning):
                    updated_count += 1

            return {
                "message": f"装备估价更新完成",
                "updated_count": updated_count,
                "total_pets": len(pets_data)
            }

        except Exception as e:
            logger.error(f"更新宠物装备估价时出错: {e}")
            return {"error": f"更新宠物装备估价时出错: {str(e)}"}

    def get_unvalued_pets_count(self) -> Dict:
        """获取当前年月携带装备但未估价的召唤兽数量"""
        try:
            # 查询携带装备但未估价的召唤兽数量
            # 条件：equip_list不为空且equip_list_amount为0或NULL
            count = db.session.query(Pet).filter(
                and_(
                    Pet.equip_list.isnot(None),
                    ~Pet.equip_list.like('%[null, null, null, {%'),
                    Pet.equip_list != '[null, null, null]',
                    or_(
                        and_(
                            or_(
                                Pet.equip_list_amount == 0,
                                Pet.equip_list_amount.is_(None)
                            )
                        ),
                        Pet.equip_list_amount_warning > 0
                    )
                )
            ).count()

            logger.info(f"查询到有 {count} 只携带装备但未估价的召唤兽")

            return {
                "count": count,
                "message": f"查询成功"
            }

        except Exception as e:
            logger.error(f"查询未估价召唤兽数量失败: {e}")
            return {
                "count": 0,
                "error": f"查询失败: {str(e)}"
            }

    def batch_update_unvalued_pets_equipment(self) -> Dict:
        """批量更新未估价召唤兽的装备价格（异步任务）"""
        try:
            # 创建任务
            task_id = str(uuid.uuid4())
            task_data = task_manager.create_task(
                task_id, 'batch_update_pets', datetime.now().year, datetime.now().month)

            # 创建任务对象
            task = BatchUpdateTask(task_id, datetime.now().year, datetime.now().month)
            add_task(task)

            # 启动异步任务
            thread = threading.Thread(
                target=self._run_batch_update_task,
                args=(task,),
                daemon=True
            )
            thread.start()

            return {
                "success": True,
                "task_id": task_id,
                "message": "批量更新任务已启动",
                "status": "started"
            }

        except Exception as e:
            logger.error(f"启动批量更新任务失败: {e}")
            return {
                "success": False,
                "message": f"启动批量更新任务失败: {str(e)}",
                "updated_count": 0,
                "total_count": 0
            }

    def _run_batch_update_task(self, task: BatchUpdateTask):
        """运行批量更新任务"""
        try:
            # 更新任务状态到文件存储
            task_manager.update_task(task.task_id, {
                'status': 'running',
                'start_time': datetime.now().isoformat()
            })

            task.status = 'running'
            task.start_time = datetime.now()

            # 查询所有未估价的召唤兽
            pets = db.session.query(Pet).filter(
                and_(
                    Pet.equip_list.isnot(None),
                    ~Pet.equip_list.like('%[null, null, null,%'),
                    Pet.equip_list != '[null, null, null]',
                    or_(
                        and_(
                            or_(
                                Pet.equip_list_amount == 0,
                                Pet.equip_list_amount.is_(None)
                            )
                        ),
                        Pet.equip_list_amount_warning > 0
                    )
                )
            ).all()

            if not pets:
                task.status = 'completed'
                task.end_time = datetime.now()
                task_manager.update_task(task.task_id, {
                    'status': 'completed',
                    'end_time': datetime.now().isoformat()
                })
                return

            # 转换为字典列表
            pets_data = []
            for pet in pets:
                pet_dict = {}
                for column in pet.__table__.columns:
                    value = getattr(pet, column.name)
                    if hasattr(value, 'isoformat'):  # datetime对象
                        pet_dict[column.name] = value.isoformat()
                    else:
                        pet_dict[column.name] = value
                pets_data.append(pet_dict)
            
            task.total_count = len(pets_data)
            task.total_batches = (
                task.total_count + task.batch_size - 1) // task.batch_size

            # 更新任务信息到文件存储
            task_manager.update_task(task.task_id, {
                'total_count': task.total_count,
                'total_batches': task.total_batches
            })

            logger.info(
                f"开始批量更新任务 {task.task_id}，共 {task.total_count} 只召唤兽，分 {task.total_batches} 批处理")

            # 分批处理
            for batch_start in range(0, task.total_count, task.batch_size):
                # 检查内存中的停止请求
                if task.is_stop_requested():
                    task.status = 'cancelled'
                    task.end_time = datetime.now()
                    task_manager.update_task(task.task_id, {
                        'status': 'cancelled',
                        'end_time': datetime.now().isoformat()
                    })
                    logger.info(f"任务 {task.task_id} 被用户取消")
                    return

                # 检查文件存储中的停止状态
                file_task = task_manager.get_task(task.task_id)
                if file_task and file_task.get('status') == 'cancelled':
                    task.status = 'cancelled'
                    task.end_time = datetime.now()
                    logger.info(f"任务 {task.task_id} 在文件存储中被标记为取消")
                    return

                batch_end = min(
                    batch_start + task.batch_size, task.total_count)
                batch_pets = pets_data[batch_start:batch_end]
                task.current_batch += 1

                logger.info(
                    f"处理第 {task.current_batch}/{task.total_batches} 批，共 {len(batch_pets)} 只召唤兽")

                # 处理当前批次
                batch_updated = self._process_batch(
                    batch_pets, task)
                task.updated_count += batch_updated
                task.processed_count += len(batch_pets)

                # 更新进度到文件存储
                task_manager.update_task(task.task_id, {
                    'current_batch': task.current_batch,
                    'processed_count': task.processed_count,
                    'updated_count': task.updated_count
                })

                # 短暂休息，避免过度占用资源
                time.sleep(0.1)

            task.status = 'completed'
            task.end_time = datetime.now()
            task_manager.update_task(task.task_id, {
                'status': 'completed',
                'end_time': datetime.now().isoformat()
            })
            logger.info(
                f"任务 {task.task_id} 完成，成功更新 {task.updated_count}/{task.total_count} 只召唤兽")

        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.end_time = datetime.now()
            task_manager.update_task(task.task_id, {
                'status': 'failed',
                'error_message': str(e),
                'end_time': datetime.now().isoformat()
            })
            logger.error(f"任务 {task.task_id} 失败: {e}")

    def _process_batch(self, batch_pets: List[Dict], task: BatchUpdateTask) -> int:
        """处理一批召唤兽"""
        try:
            # 收集所有需要估价的装备
            all_equips = []
            # (pet_idx, equip_idx) -> all_equips index
            equip_calculation_map = []

            for pet_idx, pet in enumerate(batch_pets):
                equip_list_raw = pet.get('equip_list', '[]')
                try:
                    equip_list = json.loads(equip_list_raw)
                except Exception:
                    equip_list = []

                # 只取前三个装备
                for equip_idx in range(3):
                    equip = equip_list[equip_idx] if equip_idx < len(
                        equip_list) else None
                    if equip and equip.get('desc'):
                        all_equips.append({
                            'kindid': PET_EQUIP_KINDID,
                            'desc': equip.get('desc', ''),
                        })
                        equip_calculation_map.append((pet_idx, equip_idx))

            # 批量估价
            equip_valuations = []
            if all_equips:
                from src.app.services.equipment_service import equipment_service
                try:
                    result = equipment_service.batch_equipment_valuation(
                        all_equips, 'fair_value', 0.8, 30)
                    if isinstance(result, dict):
                        equip_valuations = result.get('results', [])
                    else:
                        equip_valuations = result
                except Exception as e:
                    logger.warning(f"批量装备估价失败: {e}")
                    equip_valuations = [{} for _ in all_equips]

            # 计算装备总价值并更新数据库
            batch_updated = 0
            for pet_idx, pet in enumerate(batch_pets):
                equip_list_raw = pet.get('equip_list', '[]')
                try:
                    equip_list = json.loads(equip_list_raw)
                except Exception:
                    equip_list = []

                # 计算装备总价值
                equip_list_amount = 0
                equip_list_amount_warning = 0
                for equip_idx in range(3):
                    equip = equip_list[equip_idx] if equip_idx < len(
                        equip_list) else None
                    if equip and equip.get('desc'):
                        try:
                            idx = equip_calculation_map.index(
                                (pet_idx, equip_idx))
                            if 0 <= idx < len(equip_valuations):
                                price_info = equip_valuations[idx]
                                estimated_price = price_info.get(
                                    'estimated_price', 0)
                                confidence = price_info.get('confidence', 0)
                                if confidence == 0:
                                    equip_list_amount_warning = 1
                                if isinstance(estimated_price, (int, float)):
                                    equip_list_amount += estimated_price
                        except Exception as e:
                            logger.warning(f"装备估价回填异常: {e}")

                # 更新数据库
                if self.update_pet_equip_amount(pet['equip_sn'], equip_list_amount, equip_list_amount_warning):
                    batch_updated += 1

            return batch_updated

        except Exception as e:
            logger.error(f"处理批次失败: {e}")
            return 0

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        # 优先从文件存储获取
        task_data = task_manager.get_task(task_id)
        if task_data:
            # 添加进度百分比字段
            if task_data.get('total_count', 0) > 0:
                progress_percentage = round(
                    (task_data.get('processed_count', 0) / task_data['total_count']) * 100, 2)
            else:
                progress_percentage = 0.0
            task_data['progress_percentage'] = progress_percentage
            return task_data

        # 兼容旧的内存任务
        task = get_task(task_id)
        if task:
            return task.to_dict()
        return None

    def get_active_tasks(self) -> List[Dict]:
        """获取活跃任务列表"""
        try:
            # 从文件存储获取活跃任务
            active_tasks = task_manager.get_active_tasks()

            # 为每个任务添加进度百分比字段
            for task_data in active_tasks:
                if task_data.get('total_count', 0) > 0:
                    progress_percentage = round(
                        (task_data.get('processed_count', 0) / task_data['total_count']) * 100, 2)
                else:
                    progress_percentage = 0.0
                task_data['progress_percentage'] = progress_percentage

            return active_tasks
        except Exception as e:
            logger.error(f"获取活跃任务失败: {e}")
            return []

    def stop_task(self, task_id: str) -> Dict:
        """停止任务"""
        try:
            # 检查文件存储任务
            task_data = task_manager.get_task(task_id)
            if task_data:
                if task_data['status'] in ['pending', 'running']:
                    # 更新状态为取消
                    task_manager.update_task(task_id, {
                        'status': 'cancelled',
                        'end_time': datetime.now().isoformat()
                    })
                    logger.info(f"已更新文件存储任务 {task_id} 状态为取消")

            # 检查内存任务
            task = get_task(task_id)
            if task:
                if task.status in ['completed', 'failed', 'cancelled']:
                    return {"success": False, "message": "任务已完成或已停止"}

                # 发送停止请求到内存任务
                task.request_stop()
                logger.info(f"已发送停止请求到内存任务 {task_id}")

            # 如果两个系统都没有找到任务
            if not task_data and not task:
                return {"success": False, "message": "任务不存在"}

            return {"success": True, "message": "停止任务请求已发送"}

        except Exception as e:
            logger.error(f"停止任务失败: {e}")
            return {"success": False, "message": f"停止任务失败: {str(e)}"}

    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """清理已完成的任务"""
        current_time = datetime.now()
        tasks_to_remove = []

        for task_id, task in get_task_manager().items():
            if task.status in ['completed', 'failed', 'cancelled']:
                if task.end_time:
                    age = current_time - task.end_time
                    if age.total_seconds() > max_age_hours * 3600:
                        tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            remove_task(task_id)
            logger.info(f"清理过期任务: {task_id}")

    def delete_pet(self, pet_sn: str) -> Dict:
        """删除宠物"""
        try:
            # 先检查宠物是否存在
            pet = db.session.query(Pet).filter_by(equip_sn=pet_sn).first()
            if not pet:
                return {"error": f"未找到宠物: {pet_sn}"}

            # 删除宠物
            db.session.delete(pet)
            db.session.commit()

            logger.info(f"删除宠物成功: {pet_sn}")
            return {"success": True, "message": f"召唤兽 {pet_sn} 删除成功"}

        except Exception as e:
            db.session.rollback()
            logger.error(f"删除宠物失败: {e}")
            return {"error": f"删除宠物失败: {str(e)}"}

    def get_pet_by_equip_sn(self, equip_sn: str) -> Optional[Dict]:
        """通过equip_sn获取召唤兽详情"""
        try:
            # 查找宠物记录
            pet = db.session.query(Pet).filter_by(equip_sn=equip_sn).first()
            
            if pet:
                # 转换为字典
                pet_dict = {}
                for column in pet.__table__.columns:
                    value = getattr(pet, column.name)
                    if hasattr(value, 'isoformat'):  # datetime对象
                        pet_dict[column.name] = value.isoformat()
                    else:
                        pet_dict[column.name] = value
                return pet_dict
            
            return None

        except Exception as e:
            logger.error(f"通过equip_sn获取召唤兽详情失败: {e}")
            return None

    def batch_pet_valuation(self, pet_list: List[Dict], 
                           strategy: str = 'fair_value',
                           similarity_threshold: float = 0.7,
                           max_anchors: int = 30,
                           verbose: bool = False) -> Dict:
        """批量宠物估价"""
        try:
            logger.info(f"开始批量宠物估价，宠物数量: {len(pet_list)}，策略: {strategy}，详细日志: {verbose}")
            
            if not pet_list:
                return {
                    "error": "宠物列表为空",
                    "results": []
                }
            
            # 提取宠物特征
            pet_features_list = []
            
            for i, pet_data in enumerate(pet_list):
                try:
                    # 检查是否有宠物特征提取器
                    if not PetFeatureExtractor:
                        logger.warning(f"第{i+1}个宠物的特征提取器未初始化")
                        continue
                    
                    # 使用特征提取器提取特征
                    feature_extractor = PetFeatureExtractor()
                    pet_features = feature_extractor.extract_features(pet_data)
                    
                    # 添加原始宠物数据用于后续处理
                    pet_features['index'] = i
                    pet_features['original_pet_data'] = pet_data  # 保存原始数据，包含equip_list
                    
                    pet_features_list.append(pet_features)
                    
                except Exception as e:
                    logger.error(f"第{i+1}个宠物特征提取失败: {e}")
                    continue
            
            if not pet_features_list:
                return {
                    "error": "所有宠物特征提取失败",
                    "results": []
                }
            
            # 检查是否有宠物估价器
            if not PetMarketAnchorEvaluator:
                return {
                    "error": "宠物估价器未初始化",
                    "results": []
                }
            
            # 调用宠物估价器的批量估价方法
            evaluator = PetMarketAnchorEvaluator()
            batch_results = evaluator.batch_valuation(
                pet_features_list, 
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors,
                verbose=verbose
            )
            
            # 处理批量估价结果
            processed_results = []
            
            for i, result in enumerate(batch_results):
                if "error" in result:
                    # 处理错误情况
                    processed_result = {
                        "index": i,  # 直接使用循环索引
                        "error": result["error"],
                        "estimated_price": 0,
                        "estimated_price_yuan": 0,
                        "confidence": 0,
                        "anchor_count": 0,
                        "equip_estimated_price": 0,
                        "equip_valuations": [],
                        "skip_reason": result.get("skip_reason", "")
                    }
                else:
                    # 处理成功情况
                    estimated_price = result.get("estimated_price", 0)
                    
                    # 计算装备估价
                    equip_estimated_price = 0
                    equip_valuations = []
                    
                    # 从原始宠物数据中获取装备信息并计算估价
                    pet_index = i  # 直接使用循环索引
                    
                    if pet_index < len(pet_features_list):
                        original_pet_data = pet_features_list[pet_index].get('original_pet_data', {})
                        equip_list_raw = original_pet_data.get('equip_list', '[]')
                        
                        try:
                            equip_list = json.loads(equip_list_raw)
                            if equip_list and len(equip_list) > 0:
                                # 过滤有效的装备数据
                                valid_equips = []
                                for equip in equip_list:
                                    if equip and isinstance(equip, dict) and 'desc' in equip:
                                        valid_equips.append({
                                            'kindid': PET_EQUIP_KINDID,
                                            'desc': equip.get('desc', '')
                                        })
                                
                                if valid_equips:
                                    from src.app.services.equipment_service import equipment_service
                                    try:
                                        equip_result = equipment_service.batch_equipment_valuation(
                                            valid_equips, 'fair_value', 0.8, 30)
                                        if isinstance(equip_result, dict):
                                            equip_valuations = equip_result.get('results', [])
                                        else:
                                            equip_valuations = equip_result
                                        
                                        # 计算装备总估价
                                        equip_estimated_price = sum(
                                            equip_val.get("estimated_price", 0) 
                                            for equip_val in equip_valuations 
                                            if isinstance(equip_val, dict)
                                        )
                                        
                                        logger.info(f"宠物{pet_index}装备估价完成，装备数量: {len(valid_equips)}，总估价: {equip_estimated_price}")
                                        
                                    except Exception as e:
                                        logger.warning(f"宠物{pet_index}装备估价失败: {e}")
                                        equip_valuations = [{} for _ in valid_equips]
                        except Exception as e:
                            logger.warning(f"宠物{pet_index}装备列表解析失败: {e}")
                    
                    processed_result = {
                        "index": i,  # 直接使用循环索引
                        "estimated_price": estimated_price,
                        "estimated_price_yuan": round(estimated_price / 100, 2),
                        "confidence": result.get("confidence", 0),
                        "anchor_count": result.get("anchor_count", 0),
                        "price_range": result.get("price_range", {}),
                        "strategy": strategy,
                        "equip_estimated_price": equip_estimated_price,
                        "equip_valuations": equip_valuations,
                        "skip_reason": result.get("skip_reason", ""),
                        "invalid_item": result.get("invalid_item", False)
                    }
                
                processed_results.append(processed_result)
            
            # 按原始索引排序
            processed_results.sort(key=lambda x: x["index"])
            
            return {
                "success": True,
                "total_count": len(pet_list),
                "success_count": len([r for r in processed_results if "error" not in r]),
                "strategy": strategy,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "verbose": verbose,
                "results": processed_results
            }
            
        except Exception as e:
            logger.error(f"批量宠物估价失败: {e}")
            return {
                "error": f"批量宠物估价失败: {str(e)}",
                "results": []
            }

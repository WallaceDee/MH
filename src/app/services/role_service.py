#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色服务 - 完整迁移版本
使用SQLAlchemy ORM进行数据库操作，包含所有原有功能
"""
import json
import hashlib
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from flask import current_app
from src.database import db
from src.models.role import Role, LargeEquipDescData
from src.evaluator.market_anchor_evaluator import MarketAnchorEvaluator
from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
# 导入Flask-Caching
from flask_caching import Cache


logger = logging.getLogger(__name__)

class RoleService:
    """角色服务完整迁移版本"""
    
    def __init__(self):
        self.db = db
        
        # Flask-Caching将在使用时动态获取
        self._cache_instance = None
        
        # 初始化特征提取器
        self.feature_extractor = None
        if FeatureExtractor:
            try:
                self.feature_extractor = FeatureExtractor()
                logger.info("角色特征提取器初始化成功")
            except Exception as e:
                logger.error(f"角色特征提取器初始化失败: {e}")

        # 初始化市场锚定估价器
        self.market_evaluator = None
        if MarketAnchorEvaluator:
            try:
                self.market_evaluator = MarketAnchorEvaluator()
                logger.info("角色市场锚定估价器初始化成功")
            except Exception as e:
                logger.error(f"角色市场锚定估价器初始化失败: {e}")

    def _ensure_app_context(self):
        """确保在Flask应用上下文中执行数据库操作"""
        try:
            # 尝试访问current_app，如果没有应用上下文会抛出RuntimeError
            app_name = current_app.name
            return True
        except RuntimeError:
            raise RuntimeError("必须在Flask应用上下文中使用数据库操作")

    def _get_cache(self):
        """获取Flask-Caching实例 - 动态获取，支持在Flask上下文中使用"""
        try:
            # 检查是否在应用上下文中
            if not current_app:
                logger.debug("未在Flask应用上下文中，无法获取缓存")
                return None
                
            # 如果已经缓存了实例，直接返回
            if self._cache_instance is not None:
                return self._cache_instance
            
            # 从应用中获取缓存实例
            if hasattr(current_app, 'cache'):
                self._cache_instance = current_app.cache
                logger.debug("从应用属性获取Flask-Caching实例")
                return self._cache_instance
            
            # 从应用扩展中获取缓存实例
            extensions = getattr(current_app, 'extensions', {})
            for ext_name, ext_instance in extensions.items():
                if isinstance(ext_instance, Cache):
                    self._cache_instance = ext_instance
                    logger.debug("从应用扩展获取Flask-Caching实例")
                    return self._cache_instance
            
            logger.debug("未找到Flask-Caching实例")
            return None
                
        except Exception as e:
            logger.debug(f"获取Flask-Caching实例失败: {e}")
            return None

    def _generate_roles_cache_key(self, filters: Dict, page: int, page_size: int, role_type: str) -> str:
        """生成角色列表缓存键"""
        
        # 构建缓存键数据
        cache_data = {
            'filters': filters,
            'page': page,
            'page_size': page_size,
            'role_type': role_type,
            'version': '1.0'  # 版本号，用于缓存失效
        }
        
        # 生成哈希
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        cache_hash = hashlib.md5(cache_str.encode('utf-8')).hexdigest()[:16]
        
        return f"roles_list:{cache_hash}"

    def _clear_roles_cache(self, role_type: str = None):
        """清理角色列表缓存"""
        cache = self._get_cache()
        if not cache:
            logger.debug("Flask-Caching不可用，跳过缓存清理")
            return
        
        try:
            # Flask-Caching通常不支持通配符删除，所以缓存会自然过期
            # 这里只是记录清理意图，实际的缓存会在TTL过期后自动清理
            if role_type:
                logger.info(f"标记清理角色类型 {role_type} 的缓存（将在过期时自动清理）")
            else:
                logger.info("标记清理所有角色列表缓存（将在过期时自动清理）")
                
            # 可选：如果需要立即清理，可以记录所有使用过的缓存键然后逐个删除
            # 但这需要额外的存储机制来跟踪缓存键
                
        except Exception as e:
            logger.warning(f"清理角色列表缓存失败: {e}")


    def update_role_equip_price(self, eid: str, equip_price: float) -> bool:
        """更新角色的装备估价价格
        
        Args:
            eid: 角色唯一标识符
            equip_price: 装备估价价格（分）
            
        Returns:
            bool: 更新是否成功
        """
        try:
            self._ensure_app_context()
            
            # 查找角色
            role = self.db.session.query(Role).filter(Role.eid == eid).first()
            if not role:
                logger.warning(f"未找到角色记录: {eid}")
                return False
            
            # 更新装备估价价格
            role.equip_price = equip_price
            role.update_time = datetime.now()
            
            self.db.session.commit()
            logger.info(f"更新角色装备估价价格成功: {eid} = {equip_price}分")
            
            # 清理相关缓存
            self._clear_roles_cache()
            
            return True
                    
        except Exception as e:
            logger.error(f"更新角色装备估价价格失败: {e}")
            self.db.session.rollback()
            return False

    def update_role_pet_price(self, eid: str, pet_price: float) -> bool:
        """更新角色的宠物估价价格
        
        Args:
            eid: 角色唯一标识符
            pet_price: 宠物估价价格（分）
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 查找角色
            role = self.db.session.query(Role).filter(Role.eid == eid).first()
            if not role:
                logger.warning(f"未找到角色记录: {eid}")
                return False
            
            # 更新宠物估价价格
            role.pet_price = pet_price
            role.update_time = datetime.now()
            
            self.db.session.commit()
            logger.info(f"更新角色宠物估价价格成功: {eid} = {pet_price}分")
            
            # 清理相关缓存
            self._clear_roles_cache()
            
            return True
                    
        except Exception as e:
            logger.error(f"更新角色宠物估价价格失败: {e}")
            self.db.session.rollback()
            return False

    def update_role_base_price(self, eid: str, base_price: float) -> bool:
        """更新角色的总估价价格
        
        Args:
            eid: 角色唯一标识符
            base_price: 总估价价格（分）
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 查找角色
            role = self.db.session.query(Role).filter(Role.eid == eid).first()
            if not role:
                logger.warning(f"未找到角色记录: {eid}")
                return False
            
            # 更新总估价价格
            role.base_price = base_price
            role.update_time = datetime.now()
            
            self.db.session.commit()
            logger.info(f"更新角色总估价价格成功: {eid} = {base_price}分")
            
            # 清理相关缓存
            self._clear_roles_cache()
            
            return True
                    
        except Exception as e:
            logger.error(f"更新角色总估价价格失败: {e}")
            self.db.session.rollback()
            return False

    def get_roles(self, page: int = 1, page_size: int = 15, level_min: Optional[int] = None, 
                  level_max: Optional[int] = None, sort_by: Optional[str] = None, 
                  sort_order: Optional[str] = None, role_type: str = 'normal',
                  equip_num: Optional[int] = None, pet_num: Optional[int] = None, 
                  pet_num_level: Optional[int] = None, accept_bargain: Optional[int] = None,
                  eid_list: Optional[List[str]] = None, use_cache: bool = True) -> Dict:
        """获取角色列表
        
        Args:
            page: 页码
            page_size: 每页数量
            level_min: 最小等级
            level_max: 最大等级
            sort_by: 排序字段
            sort_order: 排序方向
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
            equip_num: 物品数量上限（小于等于）
            pet_num: 召唤兽数量上限（小于等于）
            pet_num_level: 召唤兽等级下限（大于）
            accept_bargain: 是否接受还价，1表示接受还价
            eid_list: 角色eid列表，如果提供则只查询指定的角色
        """
        try:
            start_time = time.time()
            self._ensure_app_context()
            
            # 验证页码和每页数量
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # 构建筛选条件字典
            filters = {
                'level_min': level_min,
                'level_max': level_max,
                'equip_num': equip_num,
                'pet_num': pet_num,
                'pet_num_level': pet_num_level,
                'accept_bargain': accept_bargain,
                'sort_by': sort_by,
                'sort_order': sort_order,
                'eid_list': eid_list
            }
            # 移除None值
            filters = {k: v for k, v in filters.items() if v is not None}
            
            # 尝试从缓存获取数据
            if use_cache:
                cache = self._get_cache()
                if cache:
                    cache_key = self._generate_roles_cache_key(filters, page, page_size, role_type)
                    cached_result = cache.get(cache_key)
                    
                    if cached_result:
                        elapsed_time = time.time() - start_time
                        logger.info(f"从Flask-Caching获取角色列表成功，耗时: {elapsed_time:.3f}秒")
                        return cached_result
                    else:
                        logger.debug(f"Flask-Caching未命中，缓存键: {cache_key}")
                else:
                    logger.debug("Flask-Caching不可用，跳过缓存读取")
                
            logger.info(f"查询角色列表: 角色类型: {role_type}, 页码: {page}, 每页: {page_size}")
            
            # 构建基础查询
            query = self.db.session.query(Role)
            
            # 应用过滤条件
            if level_min is not None:
                query = query.filter(Role.level >= level_min)
            if level_max is not None:
                query = query.filter(Role.level <= level_max)
            if accept_bargain is not None:
                query = query.filter(Role.accept_bargain == accept_bargain)
            
            # 角色类型过滤 - 暂时注释掉，因为数据库字段还未添加
            if role_type:
                query = query.filter(Role.role_type == role_type)
            
            # eid列表过滤 - 如果提供了eid_list，只查询指定的角色
            if eid_list is not None and len(eid_list) > 0:
                query = query.filter(Role.eid.in_(eid_list))
            
            # 对于装备数量和宠物数量的过滤，需要特殊处理
            # 这些字段在LargeEquipDescData表中，需要JOIN查询
            if equip_num is not None or pet_num is not None:
                query = query.join(LargeEquipDescData, Role.eid == LargeEquipDescData.eid, isouter=True)
                
                if equip_num is not None:
                    if equip_num == 0:
                        # 当equip_num为0时,表示没有物品
                        query = query.filter(
                            (LargeEquipDescData.all_equip_json.is_(None)) |
                            (LargeEquipDescData.all_equip_json == '') |
                            (LargeEquipDescData.all_equip_json == '{}')
                        )
                    else:
                        # 当equip_num大于0时，使用MySQL的SQL字符串匹配来统计装备数量
                        # 通过计算JSON中"iType"出现的次数来估算装备数量
                        query = query.filter(
                            LargeEquipDescData.all_equip_json.isnot(None),
                            LargeEquipDescData.all_equip_json != '',
                            LargeEquipDescData.all_equip_json != '{}',
                            db.func.char_length(LargeEquipDescData.all_equip_json) - 
                            db.func.char_length(db.func.replace(LargeEquipDescData.all_equip_json, 'iType', '')) <= 
                            db.func.char_length('iType') * equip_num
                        )

                if pet_num is not None and pet_num_level is not None:
                    if pet_num == 0:
                        # 当pet_num为0时,表示没有召唤兽
                        query = query.filter(
                            (LargeEquipDescData.all_summon_json.is_(None)) |
                            (LargeEquipDescData.all_summon_json == '[]')
                        )
                    else:
                        # 当pet_num大于0时，需要解析JSON统计召唤兽数量
                        # 这里简化处理，实际项目中可能需要更复杂的JSON查询
                        pass  # TODO: 实现召唤兽数量过滤

            # 获取总记录数
            total = query.count()

            # 计算分页
            total_pages = (total + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # 构建排序条件
            order_by = Role.update_time.desc()  # 默认按更新时间倒序
            if sort_by and sort_order:
                # 验证排序字段
                allowed_sort_by = [
                    'highlight', 'dynamic_tags', 'price', 'level', 'collect_num',
                    'create_time', 'update_time', 'accept_bargain', 'history_price'
                ]

                # 解析排序参数
                sort_fields = sort_by.split(',')
                sort_orders = sort_order.split(',')

                # 构建排序条件
                order_conditions = []
                for field, order in zip(sort_fields, sort_orders):
                    if field in allowed_sort_by and order.lower() in ['asc', 'desc']:
                        # 根据字段名确定排序方向
                        column = getattr(Role, field)
                        if order.lower() == 'desc':
                            order_conditions.append(column.desc())
                        else:
                            order_conditions.append(column.asc())

                if order_conditions:
                    order_by = order_conditions[0]  # 使用第一个排序条件

            # 执行查询
            roles = query.order_by(order_by).offset(offset).limit(page_size).all()

            # 转换为字典格式
            roles_data = []
            for role in roles:
                role_dict = {
                    'eid': role.eid,
                    'serverid': role.serverid,
                    'server_name': role.server_name,
                    'seller_nickname': role.seller_nickname,
                    'level': role.level,
                    'school': role.school,
                    'price': role.price,
                    'accept_bargain': role.accept_bargain,
                    # history_price为NULL时候返回'[]'
                    'history_price': role.history_price if role.history_price else '[]',
                    'dynamic_tags': role.dynamic_tags,
                    'highlight': role.highlight,
                    'create_time': role.create_time.isoformat() if hasattr(role.create_time, 'isoformat') else str(role.create_time) if role.create_time else None,
                    'update_time': role.update_time.isoformat() if hasattr(role.update_time, 'isoformat') else str(role.update_time) if role.update_time else None,
                    'collect_num': role.collect_num,
                    'other_info': role.other_info,
                    'base_price': role.base_price,
                    'equip_price': role.equip_price,
                    'pet_price': role.pet_price,
                    'is_split_independent_role': role.is_split_independent_role,
                    'is_split_main_role': role.is_split_main_role,
                    'large_equip_desc': role.large_equip_desc,
                    'split_price_desc': role.split_price_desc
                }
                
                # 添加关联的装备数据
                if role.detail_info:
                    role_dict.update({
                        'all_equip_json': role.detail_info.all_equip_json,
                        'all_summon_json': role.detail_info.all_summon_json,
                        'sum_exp': role.detail_info.sum_exp
                    })
                
                roles_data.append(role_dict)

            # 构建返回结果
            result = {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "data": roles_data,
                "message": "成功获取角色数据"
            }
            
            # 缓存结果到Flask-Caching
            if use_cache:
                cache = self._get_cache()
                if cache:
                    try:
                        cache_key = self._generate_roles_cache_key(filters, page, page_size, role_type)
                        cache_success = cache.set(cache_key, result, timeout=3600)  # 缓存1小时
                        
                        if cache_success:
                            elapsed_time = time.time() - start_time
                            logger.info(f"角色列表已缓存到Flask-Caching，查询+缓存总耗时: {elapsed_time:.3f}秒，缓存键: {cache_key}")
                        else:
                            logger.warning(f"Flask-Caching设置失败，缓存键: {cache_key}")
                        
                    except Exception as e:
                        logger.warning(f"缓存角色列表失败: {e}")
                else:
                    logger.debug("Flask-Caching不可用，跳过缓存设置")
            
            return result

        except ValueError as e:
            logger.error(f"参数验证错误: {e}")
            import traceback
            logger.error(f"参数验证错误堆栈: {traceback.format_exc()}")
            return {
                "error": str(e),
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": []
            }
        except RuntimeError as e:
            # 如果是应用上下文错误，重新抛出
            if "必须在Flask应用上下文中使用数据库操作" in str(e):
                raise e
            logger.error(f"获取角色列表时出错: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"获取角色列表时出错: {e}")
            return {"error": str(e)}

    def get_role_details(self, eid: str) -> Optional[Dict]:
        """获取单个角色的详细信息
        
        Args:
            eid: 角色ID
        """
        try:
            if not eid:
                return None
            
            # 查找角色
            role = self.db.session.query(Role).filter(Role.eid == eid).first()
            if not role:
                return None

            # 构建角色详情字典
            role_dict = {
                'eid': role.eid,
                'serverid': role.serverid,
                'server_name': role.server_name,
                'seller_nickname': role.seller_nickname,
                'level': role.level,
                'school': role.school,
                'price': role.price,
                'accept_bargain': role.accept_bargain,
                'history_price': role.history_price,
                'dynamic_tags': role.dynamic_tags,
                'highlight': role.highlight,
                'create_time': role.create_time.isoformat() if role.create_time else None,
                'update_time': role.update_time.isoformat() if role.update_time else None,
                'collect_num': role.collect_num,
                'other_info': role.other_info,
                'base_price': role.base_price,
                'equip_price': role.equip_price,
                'pet_price': role.pet_price,
                'is_split_independent_role': role.is_split_independent_role,
                'is_split_main_role': role.is_split_main_role,
                'large_equip_desc': role.large_equip_desc,
                'split_price_desc': role.split_price_desc,
                'yushoushu_skill': role.yushoushu_skill,
                'school_skills': role.school_skills,
                'life_skills': role.life_skills,
                'expire_time': role.expire_time.isoformat() if hasattr(role.expire_time, 'isoformat') else str(role.expire_time) if role.expire_time else None
            }
            
            # 添加关联的装备数据
            if role.detail_info:
                role_dict.update({
                    'sum_exp': role.detail_info.sum_exp,
                    'three_fly_lv': role.detail_info.three_fly_lv,
                    'all_new_point': role.detail_info.all_new_point,
                    'jiyuan_amount': role.detail_info.jiyuan_amount,
                    'packet_page': role.detail_info.packet_page,
                    'xianyu_amount': role.detail_info.xianyu_amount,
                    'learn_cash': role.detail_info.learn_cash,
                    'sum_amount': role.detail_info.sum_amount,
                    'role_icon': role.detail_info.role_icon,
                    'expt_ski1': role.detail_info.expt_ski1,
                    'expt_ski2': role.detail_info.expt_ski2,
                    'expt_ski3': role.detail_info.expt_ski3,
                    'expt_ski4': role.detail_info.expt_ski4,
                    'expt_ski5': role.detail_info.expt_ski5,
                    'beast_ski1': role.detail_info.beast_ski1,
                    'beast_ski2': role.detail_info.beast_ski2,
                    'beast_ski3': role.detail_info.beast_ski3,
                    'beast_ski4': role.detail_info.beast_ski4,
                    'changesch_json': role.detail_info.changesch_json,
                    'ex_avt_json': role.detail_info.ex_avt_json,
                    'huge_horse_json': role.detail_info.huge_horse_json,
                    'shenqi_json': role.detail_info.shenqi_json,
                    'all_equip_json': role.detail_info.all_equip_json,
                    'all_summon_json': role.detail_info.all_summon_json,
                    'all_rider_json': role.detail_info.all_rider_json
                })

            return role_dict

        except Exception as e:
            logger.error(f"获取角色详情时出错: {e}")
            return None

    def get_role_feature(self, eid: str) -> Optional[Dict]:
        """获取角色详情并提取特征
        
        Args:
            eid: 角色ID
        """
        try:
            # 先获取角色基础数据
            role_data = self.get_role_details(eid)
            if not role_data:
                return None

            # 导入特征提取器（与原始版本保持一致）
            from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor

            # 创建特征提取器实例
            extractor = FeatureExtractor()

            # 提取特征
            features = extractor.extract_features(role_data)

            # 将原始角色数据和提取的特征合并返回
            result = {
                'role_data': role_data,
                'features': features,
                'eid': eid
            }

            return result

        except Exception as e:
            logger.error(f"获取角色特征时出错: {e}")
            return None

    def delete_role(self, eid: str) -> Dict:
        """删除指定角色
        
        Args:
            eid: 角色ID
            
        Returns:
            Dict: 包含删除结果的字典
        """
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
            # 查找角色
            role = self.db.session.query(Role).filter(Role.eid == eid).first()
            if not role:
                return {"error": "未找到指定的角色"}
            
            # 删除角色相关的装备数据
            equip_deleted = self.db.session.query(LargeEquipDescData).filter(LargeEquipDescData.eid == eid).delete()
            
            # 删除角色数据
            role_deleted = self.db.session.query(Role).filter(Role.eid == eid).delete()
            
            # 提交事务
            self.db.session.commit()
            
            logger.info(f"成功删除角色 {eid}，删除了 {role_deleted} 条角色记录和 {equip_deleted} 条装备记录")
            
            # 清理相关缓存
            self._clear_roles_cache()
            
            return {
                "success": True,
                "eid": eid,
                "role_deleted": role_deleted,
                "equip_deleted": equip_deleted,
                "message": f"成功删除角色 {eid}"
            }

        except Exception as e:
            logger.error(f"删除角色时出错: {e}")
            self.db.session.rollback()
            return {"error": f"删除角色时出错: {str(e)}"}

    def get_role_valuation(self, eid: str, strategy: str = 'fair_value',
                          similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取角色估价 - 使用市场锚定法"""
        try:
            if not self.market_evaluator:
                return {
                    "error": "角色市场锚定估价器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            if not self.feature_extractor:
                return {
                    "error": "角色特征提取器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 先查询角色数据
            role_data = self.get_role_details(eid)
            if not role_data:
                return {
                    "error": f"未找到角色 {eid} 的数据",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 导入特征提取器（与原始版本保持一致）
            from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
            
            # 创建特征提取器实例
            extractor = FeatureExtractor()
            
            # 使用特征提取器提取特征
            try:
                role_features = extractor.extract_features(role_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
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
            
            # 调用市场锚定估价器
            try:
                result = self.market_evaluator.calculate_value(
                    target_features=role_features,
                    strategy=strategy,
                    similarity_threshold=similarity_threshold,
                    max_anchors=max_anchors,
                    verbose=True
                )
                
                # 格式化返回结果
                estimated_price = result.get('estimated_price', 0)
                estimated_price_yuan = estimated_price / 100.0  # 转换为元
                
                # 估价成功后自动更新数据库中的base_price
                if estimated_price > 0:
                    try:
                        update_success = self.update_role_base_price(eid, int(estimated_price))
                        if update_success:
                            logger.info(f"自动更新角色 {eid} 的估价价格: {estimated_price}分")
                        else:
                            logger.warning(f"自动更新角色 {eid} 的估价价格失败")
                    except Exception as update_error:
                        logger.error(f"自动更新角色 {eid} 估价价格时出错: {update_error}")
                        # 不影响估价结果的返回，只记录错误
                
                return {
                    "estimated_price": int(estimated_price),
                    "estimated_price_yuan": round(estimated_price_yuan, 2),
                    "confidence": result.get('confidence', 0.0),
                    "market_value": int(estimated_price),  # 市场锚定估价即为最终价值
                    "anchor_count": result.get('anchor_count', 0),
                    "feature": role_features,
                    "eid": eid,
                    "anchors": result.get('anchors', []),
                    "strategy": strategy,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors
                }
                
            except Exception as e:
                return {
                    "error": f"估价计算失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0,
                    "feature": role_features,
                    "eid": eid
                }
            
        except Exception as e:
            logger.error(f"获取角色估价时出错: {e}")
            return {
                "error": f"获取角色估价时出错: {str(e)}",
                "estimated_price": 0,
                "estimated_price_yuan": 0
            }

    def find_role_anchors(self, eid: str, similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """查找相似角色锚点"""
        try:
            # 先查询角色数据
            role_data = self.get_role_details(eid)
            if not role_data:
                return {
                    "error": f"未找到角色 {eid} 的数据",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 导入特征提取器（与原始版本保持一致）
            from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
            
            # 创建特征提取器实例
            extractor = FeatureExtractor()
            
            # 使用特征提取器提取特征
            try:
                role_features = extractor.extract_features(role_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 获取市场锚定评估器
            if not self.market_evaluator:
                return {
                    "error": "市场锚定评估器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            market_evaluator = self.market_evaluator
            
            # 查找相似角色锚点
            try:
                anchors = market_evaluator.find_market_anchors(
                    target_features=role_features,
                    similarity_threshold=similarity_threshold,
                    max_anchors=max_anchors,
                    verbose=False
                )
                
                if not anchors:
                    return {
                        "anchors": [],
                        "anchor_count": 0,
                        "statistics": None,
                        "message": "未找到相似角色"
                    }
                
                # 格式化锚点数据中的相似度，保留三位小数并获取完整角色信息
                result_anchors = []
                for anchor in anchors:
                    # 从数据库获取完整的角色信息
                    anchor_eid = anchor.get('eid')
                    full_role_info = self.get_role_details(anchor_eid)
                    
                    if full_role_info:
                        # 组合锚点信息和完整角色信息
                        anchor_info = {
                            **full_role_info,  # 包含所有角色基础信息
                            'eid': anchor_eid,
                            'similarity': round(float(anchor.get('similarity', 0)), 3),
                            'price': float(anchor.get('price', 0))
                        }
                    else:
                        # 如果无法获取完整信息，使用基础信息
                        anchor_info = {
                            'eid': anchor_eid,
                            'similarity': round(float(anchor.get('similarity', 0)), 3),
                            'price': float(anchor.get('price', 0)),
                            'nickname': '未知角色',
                            'server_name': '未知服务器',
                            'level': 0,
                            'school': '未知门派'
                        }
                    result_anchors.append(anchor_info)
                
                # 计算统计信息
                prices = [anchor.get('price', 0) for anchor in result_anchors]
                similarities = [anchor.get('similarity', 0) for anchor in result_anchors]
                
                statistics = {
                    "price_range": {
                        "min": min(prices) if prices else 0,
                        "max": max(prices) if prices else 0,
                        "avg": sum(prices) / len(prices) if prices else 0
                    },
                    "similarity_range": {
                        "min": round(min(similarities), 3) if similarities else 0,
                        "max": round(max(similarities), 3) if similarities else 0,
                        "avg": round(sum(similarities) / len(similarities), 3) if similarities else 0
                    }
                }
                
                return {
                    "anchors": result_anchors,
                    "anchor_count": len(result_anchors),
                    "statistics": statistics,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "target_features": role_features
                }
                
            except Exception as e:
                return {
                    "error": f"查找锚点失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
        except Exception as e:
            logger.error(f"查找相似角色锚点时出错: {e}")
            return {
                "error": f"查找相似角色锚点时出错: {str(e)}",
                "anchors": [],
                "anchor_count": 0
            }

    def batch_role_valuation(self, eid_list: List[str], strategy: str = 'fair_value',
                            similarity_threshold: float = 0.7, max_anchors: int = 30, verbose: bool = False) -> Dict:
        """批量角色估价 - 使用市场锚定法"""
        try:
            if not eid_list:
                return {"error": "角色eid列表不能为空"}
            
            if not self.market_evaluator:
                return {"error": "角色市场锚定估价器未初始化"}
            
            # 导入特征提取器（与原始版本保持一致）
            from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
            
            results = []
            total_value = 0
            success_count = 0
            error_count = 0
            
            for i, eid in enumerate(eid_list):
                try:
                    if verbose:
                        logger.info(f"正在估价第 {i+1}/{len(eid_list)} 个角色: {eid}")
                    
                    # 单个角色估价
                    result = self.get_role_valuation(
                        eid=eid,
                        strategy=strategy,
                        similarity_threshold=similarity_threshold,
                        max_anchors=max_anchors
                    )
                    
                    if "error" not in result:
                        success_count += 1
                        total_value += result.get("estimated_price", 0)
                        results.append({
                            "index": i,
                            "eid": eid,
                            "success": True,
                            "data": result
                        })
                    else:
                        error_count += 1
                        results.append({
                            "index": i,
                            "eid": eid,
                            "success": False,
                            "error": result.get("error", "估价失败"),
                            "data": result
                        })
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"第 {i+1} 个角色 {eid} 估价失败: {e}")
                    results.append({
                        "index": i,
                        "eid": eid,
                        "success": False,
                        "error": f"估价异常: {str(e)}",
                        "data": None
                    })
            
            # 构建返回结果
            return {
                "total_roles": len(eid_list),
                "success_count": success_count,
                "error_count": error_count,
                "total_value": total_value,
                "total_value_yuan": round(total_value / 100.0, 2),
                "strategy": strategy,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"批量角色估价失败: {e}")
            return {
                "error": f"批量角色估价失败: {str(e)}",
                "total_roles": len(eid_list) if 'eid_list' in locals() else 0,
                "success_count": 0,
                "error_count": len(eid_list) if 'eid_list' in locals() else 0,
                "total_value": 0,
                "total_value_yuan": 0,
                "results": []
            }

    # 兼容性方法 - 为了保持与原有代码的兼容性
    def create_role(self, role_data: Dict) -> bool:
        """创建角色 - 兼容性方法"""
        try:
            # 创建角色实例
            role = Role(**role_data)
            self.db.session.add(role)
            self.db.session.commit()
            return True
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            self.db.session.rollback()
            return False

    def update_equipment_valuation(self, eid: str, price: float) -> bool:
        """更新装备估价 - 兼容性方法"""
        return self.update_role_equip_price(eid, price)

    def get_role_detail(self, eid: str) -> Optional[Dict]:
        """获取角色详情 - 兼容性方法"""
        return self.get_role_details(eid)

    def switch_role_type(self, eid: str, current_role_type: str, target_role_type: str) -> Dict:
        """切换角色类型（数据迁移）"""
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
            if not current_role_type or not target_role_type:
                return {"error": "当前角色类型和目标角色类型不能为空"}
            
            if current_role_type == target_role_type:
                return {"error": "当前角色类型与目标角色类型相同，无需切换"}
            
            if target_role_type not in ['normal', 'empty']:
                return {"error": "目标角色类型必须是 normal 或 empty"}
            
            # 查找角色
            role = self.db.session.query(Role).filter(Role.eid == eid).first()
            if not role:
                return {"error": "未找到指定的角色"}
            
            # 更新角色类型
            old_role_type = role.role_type
            role.role_type = target_role_type
            
            # 提交事务
            self.db.session.commit()
            
            logger.info(f"成功切换角色 {eid} 的类型: {old_role_type} -> {target_role_type}")
            
            # 清理相关缓存
            self._clear_roles_cache()
            
            return {
                "success": True,
                "eid": eid,
                "old_role_type": old_role_type,
                "new_role_type": target_role_type,
                "message": f"角色类型切换成功: {old_role_type} -> {target_role_type}"
            }
            
        except Exception as e:
            logger.error(f"切换角色类型时出错: {e}")
            self.db.session.rollback()
            return {"error": f"切换角色类型时出错: {str(e)}"}

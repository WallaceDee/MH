#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel导出器模块
负责将CBG角色数据导出为Excel格式
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime
import logging
import json

# 导入CBG链接生成器
try:
    from ..utils.cbg_link_generator import CBGLinkGenerator
except ImportError:
    try:
        from utils.cbg_link_generator import CBGLinkGenerator
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
        from cbg_link_generator import CBGLinkGenerator


class CBGExcelExporter:
    """CBG数据Excel导出器"""
    
    def __init__(self, db_path, output_dir, logger=None):
        """
        初始化Excel导出器
        
        Args:
            db_path (str): 数据库文件路径
            output_dir (str): 输出目录
            logger: 日志对象，如果为None则创建新的logger
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.logger = logger or self._create_logger()
        
        # 使用动态配置加载器
        try:
            from ..parser.config_loader import get_config_loader
        except ImportError:
            from parser.config_loader import get_config_loader
            
        self.config_loader = get_config_loader()
    
    def _create_logger(self):
        """创建默认日志对象"""
        logger = logging.getLogger('CBGExcelExporter')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def get_export_data_sql(self):
        """获取导出数据的SQL查询语句"""
        return '''
            SELECT 
                -- 基本信息（优先使用large_equip_desc_data的数据）
                c.equip_id as _internal_equip_id,  -- 内部使用，不显示
                COALESCE(l.character_name, c.seller_nickname) as 角色名,
                c.area_name || '/' || c.server_name as 服务器,
                COALESCE(l.character_level, c.level) as 等级,
                c.school as 门派,
                c.price_desc as 价格,
                
                -- 修炼信息
                l.sum_exp || '亿' as 总经验,
                ROUND(l.up_exp / 100000000.0, 2) || '亿' as 获得经验,
                l.expt_ski1 || '/' || l.max_expt1 as 攻击修炼,
                l.expt_ski2 || '/' || l.max_expt2 as 防御修炼,
                l.expt_ski3 || '/' || l.max_expt3 as 法术修炼,
                l.expt_ski4 || '/' || l.max_expt4 as 抗法修炼,
                l.expt_ski5 as 猎术修炼,
                
                -- 召唤兽技能
                l.beast_ski1 as 攻击控制力,
                l.beast_ski2 as 防御控制力,
                l.beast_ski3 as 法术控制力,
                l.beast_ski4 as 抗法控制力,
                
                -- 飞升状态（使用更直观的显示）
                c.fly_status as 飞升状态,
                l.nine_fight_level as 生死劫等级,
                
                -- 售卖状态
                c.accept_bargain as 接受还价,
                c.status_desc as 角色售卖状态,
                c.onsale_expire_time_desc as 出售剩余时间,
                c.expire_time as 角色到期时间,
                -- 技能                       
                c.school_skills as 师门技能,
                c.life_skills as 生活技能,
                c.ju_qing_skills as 剧情技能,
                c.yushoushu_skill as 育兽术,
                -- 装备信息
                c.all_equip_json as 装备信息,
                -- 神器信息
                c.all_shenqi_json as 神器信息,
                -- 宝宝信息
                c.all_pets_json as 宝宝信息,
                -- 坐骑信息
                c.all_rider_json as 坐骑信息,
                -- 法宝信息
                c.all_fabao_json as 法宝信息,
                 -- 锦衣信息
                c.ex_avt_json as 锦衣信息,
                
                -- 属性信息
                l.hp_max as 气血,
                l.mp_max as 魔法,
                l.att_all as 命中,
                l.damage_all as 伤害,
                l.mag_dam_all as 法术伤害,
                l.def_all as 防御,
                l.dex_all as 速度,
                l.spe_all as 敏捷,
                l.mag_all as 魔力,
                l.mag_def_all as 法术防御,
                l.dod_all as 躲避,
                l.cor_all as 体质,
                l.str_all as 力量,
                l.res_all as 耐力,
                
            
                -- 点数和潜力
                l.skill_point as 剧情技能剩余技能点,
                
                -- 金钱和道具
                l.cash as 现金,
                l.saving as 存款,
                l.learn_cash as 储备金,
                l.nuts_num as 潜能果数量,
                l.cg_total_amount as 彩果总数,
                l.cg_body_amount as 身上彩果,
                l.cg_box_amount as 仓库彩果,
                l.xianyu_amount as 仙玉数量,
                
                -- 善恶值
                l.badness as 善恶点,
                l.goodness_sav as 储备善恶点,
                
                -- 社交信息
                l.org_name as 帮派名称,
                l.all_new_point as 乾元丹,
                l.org_offer as 帮贡,
                
                -- 成就和评分
                l.achievement_total as 成就总点,
                l.hero_score as 比武积分,
                l.datang_feat as 三界功绩,
                l.sword_score as 剑会积分,
                l.dup_score as 副本评分,
                l.shenqi_score as 神器评分,
                l.qicai_score as 奇才评分,
                l.xianyu_score as 仙玉积分,
                
                -- 房屋信息
                l.rent_level as 房屋等级,
                l.outdoor_level as 庭院等级,
                l.farm_level as 牧场等级,
                
                -- 其他信息
                l.pride as 人气值,
                l.version_code as 版本号,
                
                
                -- 时间信息
                c.create_time as 创建时间,
                c.update_time as 更新时间
                
            FROM characters c
            LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
            ORDER BY c.price DESC
        '''
    
    def prepare_export_data(self):
        """
        准备导出数据：从数据库获取合并后的数据
            
        Returns:
            DataFrame: 合并后的数据
        """
        try:
            conn = sqlite3.connect(self.db_path)
            sql_query = self.get_export_data_sql()
            merged_data_df = pd.read_sql_query(sql_query, conn)
            conn.close()
            
            self.logger.info(f"从数据库获取数据完成，行数: {len(merged_data_df)}")
            return merged_data_df
            
        except Exception as e:
            self.logger.error(f"准备导出数据失败: {e}")
            return pd.DataFrame()  # 返回空DataFrame
    
    def save_to_excel_with_style(self, export_df, excel_path, merged_data_df=None):
        """
        保存数据到Excel并应用样式
        
        Args:
            export_df: 要导出的DataFrame
            excel_path: Excel文件路径
            merged_data_df: 包含内部ID的原始数据(用于超链接)
        """
        try:
            # 创建Excel文件
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # 写入数据到Excel
                export_df.to_excel(writer, sheet_name='角色数据', index=False)
                
                # 获取工作簿和工作表
                workbook = writer.book
                worksheet = writer.sheets['角色数据']
                
                # 如果有原始数据，添加超链接
                if merged_data_df is not None:
                    self.add_hyperlinks_to_worksheet(worksheet, merged_data_df, export_df)
                
                # 调整列宽
                self.adjust_column_widths(worksheet)
            
            self.logger.info(f"Excel文件保存完成: {excel_path}")
            
        except Exception as e:
            self.logger.error(f"保存Excel文件失败: {e}")
            raise

  
    def format_export_data(self, merged_data_df):
        """
        格式化导出数据
        
        Args:
            merged_data_df: 合并后的数据DataFrame
            
        Returns:
            DataFrame: 格式化后的导出数据
        """
        try:
            # 移除内部使用的列
            columns_to_remove = ['_internal_equip_id']
            export_df = merged_data_df.drop(columns=[col for col in columns_to_remove if col in merged_data_df.columns])
            
            self.logger.info(f"数据格式化完成，输出行数: {len(export_df)}")
            return export_df
            
        except Exception as e:
            self.logger.error(f"格式化导出数据失败: {e}")
            raise
    
    
    def add_hyperlinks_to_worksheet(self, worksheet, merged_data_df, export_df):
        """
        为Excel工作表添加超链接
        
        Args:
            worksheet: Excel工作表对象
            merged_data_df: 包含内部ID的原始数据
            export_df: 导出数据
        """
        # 为角色名列添加CBG超链接
        if '角色名' in export_df.columns:
            role_name_col_idx = export_df.columns.get_loc('角色名') + 1  # Excel列索引从1开始
            
            for row_idx, (index, row) in enumerate(merged_data_df.iterrows(), start=2):  # 从第2行开始（跳过标题行）
                eid = row['_internal_equip_id']  # 使用内部ID生成链接
                role_name = row['角色名']
                
                if eid and role_name:
                    cbg_link = CBGLinkGenerator.generate_cbg_link(eid)
                    if cbg_link:
                        # 获取单元格
                        cell = worksheet.cell(row=row_idx, column=role_name_col_idx)
                        cell.hyperlink = cbg_link
                        cell.value = role_name  # 显示角色名
                        
                        # 设置超链接样式
                        from openpyxl.styles import Font
                        cell.font = Font(color="0000FF", underline="single")
    
    def adjust_column_widths(self, worksheet):
        """调整Excel列宽"""
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # 最大宽度50
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def log_export_results(self, filepath, export_df):
        """记录导出结果"""
        self.logger.info(f"数据已导出到: {filepath}")
        self.logger.info(f"角色数据: {len(export_df)} 条")
        self.logger.info(f"已为角色名列添加CBG分享链接超链接")
    
    def export_to_excel(self, filename=None):
        """
        导出数据到Excel文件
        
        Args:
            filename: 文件名，如果为None则自动生成
            
        Returns:
            str: 生成的Excel文件路径，失败时返回None
        """
        try:
            # 1. 准备数据：合并角色基础信息和详细信息  
            merged_data_df = self.prepare_export_data()
            
            if merged_data_df.empty:
                self.logger.warning("没有数据可导出")
                return None
                
            # 2. 格式化数据
            export_df = self.format_export_data(merged_data_df)
            
            # 3. 生成文件名
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'cbg_characters_{timestamp}.xlsx'
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # 4. 完整文件路径
            excel_path = os.path.join(self.output_dir, filename)
            
            # 5. 导出到Excel，应用样式
            self.save_to_excel_with_style(export_df, excel_path, merged_data_df)
            
            self.logger.info(f"Excel导出成功: {excel_path}")
            return excel_path
            
        except Exception as e:
            self.logger.error(f"Excel导出失败: {e}")
            return None
    
    # 工具方法
    def get_rent_level_name(self, level):
        """转换房屋等级数字为中文名称"""
        if level is None:
            return "未知"
        fangwu_mapping = self.config_loader.get_fangwu_level_mapping()
        return fangwu_mapping.get(str(level), f"未知等级({level})")
    
    def get_outdoor_level_name(self, level):
        """转换庭院等级数字为中文名称"""
        if level is None:
            return "未知"
        outdoor_mapping = self.config_loader.get_outdoor_level_mapping()
        return outdoor_mapping.get(str(level), f"未知等级({level})")
    
    def get_farm_level_name(self, level):
        """转换牧场等级数字为中文名称"""
        if level is None:
            return "未知"
        farm_mapping = self.config_loader.get_farm_level_mapping()
        return farm_mapping.get(str(level), f"未知等级({level})")
    
    def get_house_real_owner_name(self, owner_status):
        """转换房屋真实拥有者状态为中文名称"""
        if owner_status is None:
            return "未知"
        # 参考parse_role.js中的get_fangwu_owner_info逻辑
        if owner_status == 1 or owner_status == "1" or owner_status is True:
            return "是"
        elif owner_status == 0 or owner_status == "0" or owner_status is False:
            return "否"
        else:
            return "未知"


# 便利函数
def create_excel_exporter(db_path, output_dir, logger=None):
    """创建Excel导出器实例的便利函数"""
    return CBGExcelExporter(db_path, output_dir, logger)


def export_cbg_data_to_excel(db_path, output_dir, filename=None, 
                           logger=None):
    """
    直接导出CBG数据到Excel的便利函数
    
    Args:
        db_path: 数据库路径
        output_dir: 输出目录
        filename: 文件名
        logger: 日志对象
        
    Returns:
        str: 导出文件路径，失败时返回None
    """
    exporter = CBGExcelExporter(db_path, output_dir, logger)
    return exporter.export_to_excel(filename) 
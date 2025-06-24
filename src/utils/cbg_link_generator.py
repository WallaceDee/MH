#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBG链接生成器工具
用于生成梦幻西游藏宝阁角色分享链接
"""

class CBGLinkGenerator:
    """CBG链接生成器"""
    
    @staticmethod
    def extract_server_id_from_eid(eid):
        """从eid中提取服务器ID"""
        try:
            if eid and '-' in eid:
                parts = eid.split('-')
                if len(parts) >= 2:
                    return parts[1]
        except Exception:
            pass
        return None
    
    @staticmethod
    def generate_cbg_link(eid):
        """生成CBG角色分享链接"""
        if not eid:
            return None
        
        server_id = CBGLinkGenerator.extract_server_id_from_eid(eid)
        if not server_id:
            return None
        
        # 构建基础CBG链接
        base_url = "https://xyq.cbg.163.com/equip"
        params = f"s={server_id}&eid={eid}"
        link = f"{base_url}?{params}"
        
        return link 
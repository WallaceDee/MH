#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API v1 蓝图
"""

from flask import Blueprint
from .spider import spider_bp
from .system import system_bp
from .equipment import equipment_bp
from .character import character_bp

# 创建v1蓝图
api_v1_bp = Blueprint('api_v1', __name__)

# 注册子蓝图
api_v1_bp.register_blueprint(spider_bp, url_prefix='/spider')
api_v1_bp.register_blueprint(system_bp, url_prefix='/system')
api_v1_bp.register_blueprint(equipment_bp, url_prefix='/equipment')
api_v1_bp.register_blueprint(character_bp, url_prefix='/character') 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户模型
"""

from datetime import datetime, timedelta
from src.database import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import hashlib


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=True, comment='邮箱')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    api_token = db.Column(db.String(255), unique=True, nullable=True, comment='API Token')
    token_expires_at = db.Column(db.DateTime, nullable=True, comment='Token过期时间')
    fingerprint = db.Column(db.String(255), nullable=True, comment='Fingerprint值')
    is_active = db.Column(db.Boolean, default=False, nullable=False, comment='是否激活（默认未激活，需管理员启用）')
    is_premium = db.Column(db.Boolean, default=False, nullable=False, comment='是否高级用户')
    is_admin = db.Column(db.Boolean, default=False, nullable=False, comment='是否管理员')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    last_login_at = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    
    def set_password(self, password):
        """设置密码"""
        # 使用pbkdf2:sha256方法，兼容性更好（不依赖scrypt）
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_api_token(self, expires_days=30):
        """生成API Token"""
        # 生成随机token
        token = secrets.token_urlsafe(32)
        self.api_token = hashlib.sha256(token.encode()).hexdigest()
        self.token_expires_at = datetime.utcnow() + timedelta(days=expires_days)
        db.session.commit()
        return token  # 返回原始token（只返回一次）
    
    def is_token_valid(self):
        """检查token是否有效"""
        if not self.api_token or not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at
    
    def refresh_token(self, expires_days=30):
        """刷新token"""
        return self.generate_api_token(expires_days)
    
    def set_fingerprint(self, fingerprint):
        """设置fingerprint"""
        self.fingerprint = fingerprint
        db.session.commit()
    
    def has_fingerprint(self, fingerprint):
        """检查用户是否有指定的fingerprint"""
        return self.fingerprint == fingerprint
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'fingerprint': self.fingerprint,
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


# ORM框架设置指南

本指南将帮助您在CBG爬虫项目中设置和使用SQLAlchemy ORM框架。

## 概述

我们已经为项目添加了SQLAlchemy ORM框架，这样可以更方便地在SQLite和MySQL之间切换，同时提供更好的数据库操作体验。

## 已添加的功能

### 1. 数据库配置管理
- `src/database_config.py` - 统一的数据库配置管理
- 支持SQLite和MySQL数据库切换
- 通过环境变量控制数据库类型

### 2. SQLAlchemy集成
- `src/database.py` - SQLAlchemy数据库初始化
- 支持连接池配置
- 自动处理不同数据库的差异

### 3. 数据模型
- `src/models/role.py` - 角色相关模型
- `src/models/equipment.py` - 装备模型
- `src/models/pet.py` - 召唤兽模型
- `src/models/abnormal_equipment.py` - 异常装备模型

### 4. ORM服务层
- `src/app/services/role_service_orm.py` - 使用ORM的角色服务
- 提供完整的CRUD操作
- 自动处理JSON字段转换

## 使用方法

### 1. 安装依赖

```bash
pip install SQLAlchemy>=1.4.0 Flask-SQLAlchemy>=2.5.0
```

### 2. 配置数据库

#### SQLite模式（默认）
```bash
export DATABASE_TYPE=sqlite
```

#### MySQL模式
```bash
export DATABASE_TYPE=mysql
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=cbg_spider
```

### 3. 在代码中使用

#### 基本查询
```python
from src.database import db
from src.models.role import Role

# 在Flask应用上下文中
with app.app_context():
    # 查询所有角色
    roles = db.session.query(Role).all()
    
    # 条件查询
    high_level_roles = db.session.query(Role).filter(Role.level > 100).all()
    
    # 分页查询
    page_roles = db.session.query(Role).offset(0).limit(10).all()
```

#### 使用服务层
```python
from src.app.services.role_service_orm import RoleServiceORM

# 创建服务实例
role_service = RoleServiceORM()

# 获取角色列表
result = role_service.get_roles_list(page=1, page_size=20)

# 获取角色详情
detail = role_service.get_role_detail('role_eid_123')

# 更新角色
role_service.update_equipment_valuation('role_eid_123', 1000.0)
```

### 4. 数据库迁移

#### 创建表
```python
from src.database import db
from src.models import Role, Equipment, Pet, AbnormalEquipment

# 在Flask应用上下文中
with app.app_context():
    db.create_all()
```

#### 从现有SQLite数据迁移
```python
# 可以编写迁移脚本，将现有SQLite数据导入到ORM模型中
# 这需要根据具体的数据结构来实现
```

## 优势

### 1. 数据库无关性
- 同一套代码可以运行在SQLite和MySQL上
- 通过配置切换数据库类型
- 自动处理不同数据库的语法差异

### 2. 类型安全
- 使用Python类型提示
- 自动验证数据类型
- 减少运行时错误

### 3. 关系映射
- 自动处理表之间的关系
- 支持外键约束
- 简化复杂查询

### 4. 查询优化
- 自动生成优化的SQL语句
- 支持懒加载和预加载
- 内置查询缓存

### 5. 数据验证
- 自动验证数据完整性
- 支持自定义验证规则
- 防止无效数据插入

## 测试

运行测试脚本验证ORM功能：

```bash
python tests/test_orm_functionality.py
```

## 下一步

1. **逐步迁移现有服务** - 将现有的服务类逐步迁移到使用ORM
2. **添加更多模型** - 根据需要添加更多数据模型
3. **优化查询性能** - 添加索引和优化查询
4. **数据迁移工具** - 创建从SQLite到MySQL的迁移工具
5. **API更新** - 更新API接口以使用新的ORM服务

## 注意事项

1. **向后兼容** - 现有的SQLite代码仍然可以正常工作
2. **性能考虑** - ORM可能比原生SQL稍慢，但提供了更好的开发体验
3. **学习曲线** - 团队需要学习SQLAlchemy的使用方法
4. **调试** - 可以通过设置`SQLALCHEMY_ECHO=True`来查看生成的SQL语句

## 故障排除

### 1. 导入错误
确保所有模块路径正确，检查`__init__.py`文件

### 2. 数据库连接失败
检查数据库配置和连接参数

### 3. 表创建失败
确保数据库用户有创建表的权限

### 4. 查询超时
调整连接池配置和查询超时设置

更多帮助请参考SQLAlchemy官方文档或项目README。

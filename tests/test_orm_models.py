#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ORM模型测试
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_model_imports():
    """测试模型导入"""
    print("测试模型导入...")
    
    try:
        from src.models.base import Base
        print(f"✅ Base类导入成功")
        
        from src.models.role import Role, LargeEquipDescData
        print(f"✅ Role模型导入成功")
        print(f"   表名: {Role.__tablename__}")
        print(f"   列数: {len(Role.__table__.columns)}")
        
        from src.models.equipment import Equipment
        print(f"✅ Equipment模型导入成功")
        print(f"   表名: {Equipment.__tablename__}")
        print(f"   列数: {len(Equipment.__table__.columns)}")
        
        from src.models.pet import Pet
        print(f"✅ Pet模型导入成功")
        print(f"   表名: {Pet.__tablename__}")
        print(f"   列数: {len(Pet.__table__.columns)}")
        
        from src.models.abnormal_equipment import AbnormalEquipment
        print(f"✅ AbnormalEquipment模型导入成功")
        print(f"   表名: {AbnormalEquipment.__tablename__}")
        print(f"   列数: {len(AbnormalEquipment.__table__.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_relationships():
    """测试模型关系"""
    print("\n测试模型关系...")
    
    try:
        from src.models.role import Role, LargeEquipDescData
        
        # 检查关系定义
        if hasattr(Role, 'detail_info'):
            print(f"✅ Role.detail_info 关系定义存在")
        else:
            print(f"❌ Role.detail_info 关系定义不存在")
        
        if hasattr(LargeEquipDescData, 'role'):
            print(f"✅ LargeEquipDescData.role 关系定义存在")
        else:
            print(f"❌ LargeEquipDescData.role 关系定义不存在")
        
        # 检查外键
        foreign_keys = [col for col in LargeEquipDescData.__table__.columns if col.foreign_keys]
        if foreign_keys:
            print(f"✅ 找到外键: {[fk.name for fk in foreign_keys]}")
        else:
            print(f"❌ 没有找到外键")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型关系测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_creation():
    """测试模型实例创建"""
    print("\n测试模型实例创建...")
    
    try:
        from src.models.role import Role
        from src.models.equipment import Equipment
        from src.models.pet import Pet
        from src.models.abnormal_equipment import AbnormalEquipment
        
        # 创建Role实例
        role = Role(
            eid='test_001',
            equip_name='测试角色',
            level=175,
            price=1000.0,
            server_name='测试服务器'
        )
        print(f"✅ Role实例创建成功: {role.equip_name}")
        
        # 创建Equipment实例
        equipment = Equipment(
            equip_sn='equip_001',
            equip_name='测试装备',
            level=100,
            price=500.0,
            server_name='测试服务器'
        )
        print(f"✅ Equipment实例创建成功: {equipment.equip_name}")
        
        # 创建Pet实例
        pet = Pet(
            equip_sn='pet_001',
            equip_name='测试召唤兽',
            level=50,
            price=200.0,
            server_name='测试服务器'
        )
        print(f"✅ Pet实例创建成功: {pet.equip_name}")
        
        # 创建AbnormalEquipment实例
        abnormal = AbnormalEquipment(
            equip_sn='abnormal_001',
            equipment_data='{"test": "data"}',
            mark_reason='测试异常'
        )
        print(f"✅ AbnormalEquipment实例创建成功: {abnormal.equip_sn}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型实例创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("ORM模型测试")
    print("=" * 60)
    
    success = True
    
    # 测试模型导入
    if not test_model_imports():
        success = False
    
    # 测试模型关系
    if not test_model_relationships():
        success = False
    
    # 测试模型实例创建
    if not test_model_creation():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有ORM模型测试通过！")
        print("\n下一步:")
        print("1. 配置数据库连接")
        print("2. 创建数据库表")
        print("3. 开始使用ORM进行数据操作")
    else:
        print("❌ 部分测试失败！")
    print("=" * 60)

if __name__ == "__main__":
    main()

import sqlite3
import os
from datetime import datetime

# 获取最新的数据库文件
data_dir = 'data'
now = datetime.now()
db_file = os.path.join(data_dir, f'cbg_equip_{now.year}{now.month:02d}.db')

if os.path.exists(db_file):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        
        # 查询有宝石数据的装备
        cursor.execute("SELECT gem_value, gem_level, equip_name FROM equipments WHERE gem_value IS NOT NULL AND gem_value != '' AND gem_value != '[]' LIMIT 10")
        results = cursor.fetchall()
        
        print('数据库中的宝石数据格式:')
        for gem_value, gem_level, equip_name in results:
            print(f'  装备: {equip_name}')
            print(f'    gem_value: {gem_value}')
            print(f'    gem_level: {gem_level}')
            print()
            
        # 查询总的有宝石装备数量
        cursor.execute("SELECT COUNT(*) FROM equipments WHERE gem_value IS NOT NULL AND gem_value != '' AND gem_value != '[]'")
        total = cursor.fetchone()[0]
        print(f'总共有 {total} 个装备有宝石数据')
        
        # 测试宝石查询
        print('\n测试宝石查询:')
        test_gem_id = '1'  # 太阳石
        cursor.execute("SELECT COUNT(*) FROM equipments WHERE gem_value LIKE ?", (f'%"{test_gem_id}"%',))
        count1 = cursor.fetchone()[0]
        print(f'使用 LIKE %"{test_gem_id}"% 查询到 {count1} 个装备')
        
        cursor.execute("SELECT COUNT(*) FROM equipments WHERE gem_value LIKE ?", (f'%[{test_gem_id}]%',))
        count2 = cursor.fetchone()[0]
        print(f'使用 LIKE %[{test_gem_id}]% 查询到 {count2} 个装备')
        
        cursor.execute("SELECT COUNT(*) FROM equipments WHERE gem_value LIKE ?", (f'%{test_gem_id}%',))
        count3 = cursor.fetchone()[0]
        print(f'使用 LIKE %{test_gem_id}% 查询到 {count3} 个装备')
        
else:
    print(f'数据库文件不存在: {db_file}') 
import sqlite3
import os

def test_database():
    """简单测试数据库连接和数据"""
    db_path = r"C:\Users\Administrator\Desktop\mh\data\202509\cbg_empty_roles_202509.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查roles表中有价格的数据
        cursor.execute("SELECT COUNT(*) FROM roles WHERE price > 0;")
        count = cursor.fetchone()[0]
        print(f"roles表中有价格的记录数: {count}")
        
        # 检查large_equip_desc_data表数据
        cursor.execute("SELECT COUNT(*) FROM large_equip_desc_data;")
        count2 = cursor.fetchone()[0]
        print(f"large_equip_desc_data表记录数: {count2}")
        
        # 检查关联查询
        query = """
        SELECT COUNT(*) FROM large_equip_desc_data l
        INNER JOIN roles r ON l.eid = r.eid
        WHERE r.price > 0
        """
        cursor.execute(query)
        count3 = cursor.fetchone()[0]
        print(f"关联查询有效记录数: {count3}")
        
        # 先查看表结构
        cursor.execute("PRAGMA table_info(large_equip_desc_data);")
        columns = cursor.fetchall()
        print(f"\nlarge_equip_desc_data表字段: {[col[1] for col in columns[:10]]}...")  # 只显示前10个字段
        
        cursor.execute("PRAGMA table_info(roles);")
        columns = cursor.fetchall()
        print(f"roles表字段: {[col[1] for col in columns[:10]]}...")  # 只显示前10个字段
        
        # 获取几个样本看看
        query = """
        SELECT l.eid, r.price, l.role_level, l.role_school
        FROM large_equip_desc_data l
        INNER JOIN roles r ON l.eid = r.eid
        WHERE r.price > 0
        LIMIT 5
        """
        cursor.execute(query)
        samples = cursor.fetchall()
        
        print("\n样本数据:")
        for i, row in enumerate(samples):
            print(f"  {i+1}. eid: {row['eid']}, price: {row['price']}, level: {row['role_level']}, school: {row['role_school']}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_database() 
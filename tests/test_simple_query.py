import sqlite3
import os

def test_simple_query():
    """简单测试查询"""
    db_path = r"C:\Users\Administrator\Desktop\mh\data\202509\cbg_empty_roles_202509.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 测试简单查询
        print("1. 测试roles表的price字段:")
        cursor.execute("SELECT eid, price FROM roles WHERE price > 0 LIMIT 3;")
        samples = cursor.fetchall()
        for row in samples:
            print(f"  eid: {row['eid']}, price: {row['price']}")
        
        print("\n2. 测试关联查询:")
        query = """
        SELECT l.eid, r.price, l.role_level, l.role_school
        FROM large_equip_desc_data l
        INNER JOIN roles r ON l.eid = r.eid
        WHERE r.price > 0
        LIMIT 3
        """
        cursor.execute(query)
        samples = cursor.fetchall()
        for row in samples:
            print(f"  eid: {row['eid']}, price: {row['price']}, level: {row['role_level']}, school: {row['role_school']}")
        
        conn.close()
        
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_simple_query() 
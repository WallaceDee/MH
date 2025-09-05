import sqlite3
import os

def check_roles_table():
    """检查roles表的字段"""
    db_path = r"C:\Users\Administrator\Desktop\mh\data\202509\cbg_empty_roles_202509.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取roles表的字段
        cursor.execute("PRAGMA table_info(roles);")
        columns = cursor.fetchall()
        print("roles表的所有字段:")
        for i, col in enumerate(columns):
            print(f"  {i+1:2d}. {col[1]:<25} {col[2]:<10}")
        
        # 查找包含price的字段
        price_fields = [col[1] for col in columns if 'price' in col[1].lower()]
        print(f"\n包含price的字段: {price_fields}")
        
        # 检查第一条记录
        if price_fields:
            price_field = price_fields[0]
            cursor.execute(f"SELECT eid, {price_field} FROM roles WHERE {price_field} > 0 LIMIT 5;")
            samples = cursor.fetchall()
            print(f"\n{price_field}字段的样本数据:")
            for row in samples:
                print(f"  eid: {row['eid']}, {price_field}: {row[price_field]}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_roles_table() 
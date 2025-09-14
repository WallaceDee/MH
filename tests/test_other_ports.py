#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试其他端口上的MariaDB
"""

import pymysql

def test_port(host, port, user, password):
    """测试指定端口"""
    try:
        print(f"测试端口 {port}...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            connect_timeout=5,
            ssl_disabled=True,
            autocommit=True
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✓ 端口 {port} 连接成功！版本: {version}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ 端口 {port} 连接失败: {e}")
        return False

def main():
    host = '47.86.33.98'
    user = 'root'
    password = '447363121'
    ports = [3306, 3307, 3308, 3309, 3310]
    
    print("测试各个端口上的MariaDB连接...")
    
    success_ports = []
    for port in ports:
        if test_port(host, port, user, password):
            success_ports.append(port)
    
    if success_ports:
        print(f"\n🎉 找到可用的端口: {success_ports}")
        print(f"建议使用端口: {success_ports[0]}")
    else:
        print("\n❌ 所有端口都无法连接")
        print("建议检查服务器上的MariaDB服务状态")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
诊断数据库连接问题
"""

import socket
import time
import pymysql

def test_network_connectivity():
    """测试网络连接"""
    print("=== 网络连接测试 ===")
    
    host = '47.86.33.98'
    port = 3306
    
    try:
        # 测试TCP连接
        print(f"测试TCP连接到 {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✓ TCP连接成功")
            return True
        else:
            print(f"✗ TCP连接失败，错误代码: {result}")
            return False
    except Exception as e:
        print(f"✗ 网络连接测试失败: {e}")
        return False

def test_mariadb_handshake():
    """测试MariaDB握手"""
    print("\n=== MariaDB握手测试 ===")
    
    host = '47.86.33.98'
    port = 3306
    
    try:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # 读取服务器握手包
        data = sock.recv(1024)
        if data:
            print(f"✓ 收到服务器响应，长度: {len(data)} 字节")
            print(f"✓ 服务器版本信息: {data[5:].split(b'\x00')[0].decode('utf-8', errors='ignore')}")
            sock.close()
            return True
        else:
            print("✗ 未收到服务器响应")
            sock.close()
            return False
    except Exception as e:
        print(f"✗ MariaDB握手失败: {e}")
        return False

def test_different_ports():
    """测试不同端口"""
    print("\n=== 端口扫描测试 ===")
    
    host = '47.86.33.98'
    ports = [3306, 3307, 3308, 3309, 3310]
    
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✓ 端口 {port} 开放")
                open_ports.append(port)
            else:
                print(f"✗ 端口 {port} 关闭")
        except Exception as e:
            print(f"✗ 端口 {port} 测试失败: {e}")
    
    return open_ports

def test_mariadb_connection():
    """测试MariaDB连接"""
    print("\n=== MariaDB连接测试 ===")
    
    host = '47.86.33.98'
    port = 3306
    user = 'root'
    password = '447363121'
    
    try:
        print(f"尝试连接 {user}@{host}:{port}")
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
        
        print("✓ MariaDB连接成功！")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✓ 数据库版本: {version}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MariaDB连接失败: {e}")
        return False

def main():
    """主诊断函数"""
    print("开始诊断数据库连接问题...\n")
    
    # 1. 网络连接测试
    network_ok = test_network_connectivity()
    
    # 2. MariaDB握手测试
    if network_ok:
        handshake_ok = test_mariadb_handshake()
    else:
        handshake_ok = False
    
    # 3. 端口扫描
    open_ports = test_different_ports()
    
    # 4. MariaDB连接测试
    if handshake_ok:
        mariadb_ok = test_mariadb_connection()
    else:
        mariadb_ok = False
    
    # 总结
    print("\n=== 诊断结果 ===")
    print(f"网络连接: {'✓' if network_ok else '✗'}")
    print(f"MariaDB握手: {'✓' if handshake_ok else '✗'}")
    print(f"开放端口: {open_ports if open_ports else '无'}")
    print(f"MariaDB连接: {'✓' if mariadb_ok else '✗'}")
    
    if not network_ok:
        print("\n建议: 检查网络连接或服务器是否在线")
    elif not handshake_ok:
        print("\n建议: 检查服务器端口是否正确开放")
    elif not mariadb_ok:
        print("\n建议: 检查用户名密码或数据库配置")
    else:
        print("\n🎉 所有测试通过！")

if __name__ == "__main__":
    main()


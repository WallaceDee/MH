#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫项目启动脚本
提供多种运行模式
"""

import sys
import os
import argparse

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def run_basic_spider(max_pages=5):
    """运行基础爬虫"""
    print("启动基础CBG爬虫...")
    try:
        from cbg_spider import CBGSpider
        print("✅ 成功导入CBGSpider")
    except Exception as e:
        print(f"❌ 导入CBGSpider失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        spider = CBGSpider()
        print("🔧 CBG爬虫初始化完成")
        
        # 爬取数据
        print("开始爬取数据...")
        spider.crawl_all_pages(max_pages=max_pages,delay_range=[1, 3],use_browser=True)
        print("数据爬取完成")
        
        # 导出Excel
        print("\n正在导出Excel...")
        excel_file = spider.export_to_excel()
        if excel_file:
            print(f"Excel文件已生成: {excel_file}")
        else:
            print("❌ Excel导出失败")
        
        # 导出JSON
        print("\n正在导出JSON...")
        json_file = spider.export_to_json(filename=None, pretty=False)
        if json_file:
            print(f"JSON文件已生成: {json_file}")
        else:
            print("❌ JSON导出失败")
        
        print("✅ 基础爬虫完成！")
        
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()

def run_proxy_spider(max_pages=5):
    """运行带代理的爬虫"""
    print("🔄 启动带代理的CBG爬虫...")
    from cbg_crawler_with_proxy import EnhancedCBGCrawler
    
    crawler = EnhancedCBGCrawler()
    crawler.start_crawling(max_pages=max_pages)

def run_proxy_manager():
    """运行代理管理器"""
    print("🔧 启动代理IP管理器...")
    from proxy_source_manager import ProxySourceManager
    
    manager = ProxySourceManager()
    proxies = manager.get_all_proxies()
    manager.save_proxies_to_file(proxies)
    print(f"✅ 获取到 {len(proxies)} 个代理IP")

def run_tests():
    """运行测试"""
    print("🧪 运行项目测试...")
    import subprocess
    
    tests_path = os.path.join(project_root, 'tests', 'test_optimized_spider.py')
    subprocess.run([sys.executable, tests_path])

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CBG爬虫项目启动器')
    parser.add_argument('mode', choices=['basic', 'proxy', 'proxy-manager', 'test'], 
                       help='运行模式')
    parser.add_argument('--pages', type=int, default=5, 
                       help='爬取页数 (默认: 5)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎮 CBG智能爬虫系统 v1.0.0")
    print("=" * 60)
    
    try:
        if args.mode == 'basic':
            run_basic_spider(args.pages)
        elif args.mode == 'proxy':
            run_proxy_spider(args.pages)
        elif args.mode == 'proxy-manager':
            run_proxy_manager()
        elif args.mode == 'test':
            run_tests()
            
        print("\n✅ 任务完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    main() 
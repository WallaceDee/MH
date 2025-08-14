#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫项目启动脚本
提供多种运行模式
"""

import sys
import os
import argparse
from datetime import datetime

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def run_basic_spider(max_pages=5, spider_type='role', equip_type='normal', use_browser=True, delay_range=(5, 8), cached_params_file=None):
    """运行基础爬虫"""
    print("启动基础CBG爬虫...")
    
    # 加载缓存参数
    cached_params = None
    if cached_params_file and os.path.exists(cached_params_file):
        try:
            import json
            with open(cached_params_file, 'r', encoding='utf-8') as f:
                cached_params = json.load(f)
            print(f"已加载缓存参数: {len(cached_params)} 个参数")
            # 删除临时文件
            os.unlink(cached_params_file)
        except Exception as e:
            print(f"加载缓存参数失败: {e}")
            if os.path.exists(cached_params_file):
                os.unlink(cached_params_file)
    
    try:
        from cbg_spider import CBGSpider
        print("成功导入CBGSpider")
    except Exception as e:
        print(f"导入CBGSpider失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        from src.spider.equip import CBGEquipSpider
        print("成功导入CBGEquipSpider")
    except Exception as e:
        print(f"导入CBGEquipSpider失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        from src.spider.pet import CBGPetSpider
        print("成功导入CBGPetSpider")
    except Exception as e:
        print(f"导入CBGPetSpider失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        spider = CBGSpider()
        cbg_equip_spider = CBGEquipSpider()
        cbg_pet_spider = CBGPetSpider()
        print("CBG爬虫初始化完成")
        
        # 爬取数据
        print("开始爬取数据...")
        if spider_type == 'role':
            print(f"爬取角色数据，页数: {max_pages}")
            spider.crawl_all_pages(max_pages=max_pages, delay_range=delay_range, use_browser=use_browser, search_params=cached_params)
        elif spider_type == 'equip':
            equip_type_names = {
                'normal': '普通装备',
                'lingshi': '灵饰',
                'pet': '召唤兽装备'
            }
            equip_name = equip_type_names.get(equip_type, equip_type)
            print(f"爬取{equip_name}数据，页数: {max_pages}")
            if use_browser:
                print("将启动浏览器进行参数设置...")
            cbg_equip_spider.crawl_all_pages(
                max_pages=max_pages, 
                delay_range=delay_range, 
                use_browser=use_browser,
                equip_type=equip_type,
                cached_params=cached_params
            )
        elif spider_type == 'pet':
            print(f"爬取召唤兽数据，页数: {max_pages}")
            if use_browser:
                print("将启动浏览器进行参数设置...")
            cbg_pet_spider.crawl_all_pages(
                max_pages=max_pages, 
                delay_range=delay_range, 
                use_browser=use_browser,
                cached_params=cached_params
            )    
        else:
            print(f"未知的爬虫类型: {spider_type}")
        return
        
    except Exception as e:
        print(f"执行出错: {e}")
        import traceback
        traceback.print_exc()

def run_proxy_spider(max_pages=5):
    """运行带代理的爬虫"""
    print("启动带代理的CBG爬虫...")
    from cbg_crawler_with_proxy import EnhancedCBGCrawler
    
    crawler = EnhancedCBGCrawler()
    crawler.start_crawling(max_pages=max_pages)

def run_proxy_manager():
    """运行代理管理器"""
    print("启动代理IP管理器...")
    from proxy_source_manager import ProxySourceManager
    
    manager = ProxySourceManager()
    proxies = manager.get_all_proxies()
    manager.save_proxies_to_file(proxies)
    print(f"获取到 {len(proxies)} 个代理IP")

def run_playwright_collector(headless=False, target_url=None):
    """运行Playwright半自动数据收集器"""
    print("启动Playwright半自动数据收集器...")
    try:
        import asyncio
        from src.spider.playwright_collector import PlaywrightAutoCollector
        
        # 创建收集器实例
        collector = PlaywrightAutoCollector(headless=headless)
        
        # 使用异步运行
        async def run_collector():
            try:
                # 启动收集器
                if target_url:
                    print(f"目标URL: {target_url}")
                    success = await collector.start_collecting(target_url)
                else:
                    # 使用默认URL
                    default_url = "https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search&recommend_type=1"
                    print(f"使用默认URL: {default_url}")
                    success = await collector.start_collecting(default_url)
                
                if success:
                    print("Playwright收集器已启动，浏览器已打开...")
                    print("请在浏览器中手动操作，所有API请求将被自动捕获")
                    print("关闭浏览器窗口即可自动停止收集服务")
                    
                    # 保持运行直到用户中断或浏览器关闭
                    try:
                        while collector.is_collecting:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        print("\n正在停止收集...")
                    
                    # 停止收集器
                    await collector.stop_collecting()
                    print("数据收集已完成")
                else:
                    print("启动失败")
                    
            except Exception as e:
                print(f"运行Playwright收集器失败: {e}")
                await collector.stop_collecting()
        
        # 运行异步函数
        asyncio.run(run_collector())
            
    except Exception as e:
        print(f"运行Playwright收集器失败: {e}")
        import traceback
        traceback.print_exc()

def run_tests():
    """运行测试"""
    print("运行项目测试...")
    import subprocess
    
    tests_path = os.path.join(project_root, 'tests', 'test_optimized_spider.py')
    subprocess.run([sys.executable, tests_path])

def show_help_examples():
    """显示使用示例"""
    print("\n" + "="*60)
    print("使用示例")
    print("="*60)
    print("1. 爬取角色数据:")
    print("   python run.py basic --type role --pages 10")
    print()
    print("2. 爬取普通装备数据:")
    print("   python run.py basic --type equip --equip-type normal --pages 5")
    print()
    print("3. 爬取灵饰数据（使用浏览器设置参数）:")
    print("   python run.py basic --type equip --equip-type lingshi --use-browser --pages 3")
    print()
    print("4. 爬取召唤兽装备数据:")
    print("   python run.py basic --type equip --equip-type pet --pages 5")
    print()
    print("5. 爬取召唤兽（宠物）数据:")
    print("   python run.py basic --type pet --pages 8")
    print()
    print("6. 爬取召唤兽（宠物）数据 - 使用浏览器设置筛选条件:")
    print("   python run.py basic --type pet --use-browser --pages 5")
    print("   # 可设置: 等级范围、价格范围、宠物类型、技能数量、成长值、资质等")
    print()
    print("7. 爬取召唤兽（宠物）数据 - 使用缓存参数:")
    print("   python run.py basic --type pet --no-browser --pages 10")
    print("   # 使用 config/pet_params.json 中的搜索参数")
    print()
    print("8. 使用代理爬取:")
    print("   python run.py proxy --pages 10")
    print()
    print("9. 管理代理IP:")
    print("   python run.py proxy-manager")
    print()
    print("10. 运行测试:")
    print("    python run.py test")
    print()
    print("11. Playwright半自动数据收集:")
    print("    python run.py playwright")
    print("    python run.py playwright --headless --target-url https://xyq.cbg.163.com/")
    print()
    print("召唤兽爬虫特色功能:")
    print("   - 支持完整的宠物属性: 等级、气血、伤害、防御、速度、法伤、法防等")
    print("   - 支持宠物筛选条件: 宠物类型、技能数量、成长值、资质范围等")
    print("   - 支持浏览器手动设置复杂搜索条件")
    print("   - 数据按月分割存储: cbg_pets_YYYYMM.db")
    print("   - 支持参数缓存，避免重复设置")
    print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='CBG智能爬虫系统 - 支持角色、装备、灵饰、召唤兽装备、召唤兽等多种数据爬取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run.py basic --type role --pages 10                    # 爬取角色数据
  python run.py basic --type equip --equip-type normal          # 爬取普通装备
  python run.py basic --type equip --equip-type lingshi --use-browser  # 爬取灵饰(浏览器设置)
  python run.py basic --type equip --equip-type pet             # 爬取召唤兽装备
  python run.py basic --type pet --pages 8                      # 爬取召唤兽(宠物)
  python run.py basic --type pet --use-browser --pages 5        # 爬取召唤兽(浏览器设置筛选条件)
  python run.py proxy --pages 10                                # 使用代理爬取
  python run.py proxy-manager                                   # 管理代理IP
  python run.py test                                            # 运行测试
  python run.py playwright                                      # Playwright半自动数据收集(交互式)
  python run.py playwright --headless --target-url https://xyq.cbg.163.com/  # Playwright收集(无头模式)

半自动数据收集模式说明:
  - 启动浏览器并监听所有CBG API请求
  - 自动捕获对 recommend.py 的请求并解析参数
  - 根据请求参数自动分类: 角色、装备、灵饰、宠物、宠物装备
  - 数据自动保存到对应的SQLite数据库
  - 支持交互式操作和后台监控
  - 可导出数据为JSON格式

召唤兽爬虫详细说明:
  - 召唤兽数据包含: 基本信息、属性、技能、资质、成长、价格等完整数据
  - 支持浏览器模式手动设置筛选条件: 等级、价格、宠物类型、技能数、成长值、资质等
  - 支持本地参数缓存模式，避免重复设置搜索条件
  - 数据存储到 data/cbg_pets_YYYYMM.db，按月分割便于管理
        """
    )
    
    # 主要模式参数
    parser.add_argument('mode', choices=['basic', 'proxy', 'proxy-manager', 'test', 'playwright', 'help'], 
                       help='运行模式', default='basic')
    
    # 基础爬虫参数
    parser.add_argument('--type', type=str, default='role', choices=['role', 'equip', 'pet'],
                       help='爬虫类型: role(角色)、equip(装备)、pet(召唤兽) (默认: role)')
    
    # 装备爬虫专用参数
    parser.add_argument('--equip-type', type=str, default='normal', 
                       choices=['normal', 'lingshi', 'pet'],
                       help='装备类型: normal(普通装备), lingshi(灵饰), pet(召唤兽装备) (默认: normal)')
    
    # 通用参数
    parser.add_argument('--pages', type=int, default=5, 
                       help='爬取页数 (默认: 5)')
    parser.add_argument('--use-browser', action='store_true', default=True,
                       help='使用浏览器设置搜索参数 (仅对装备和召唤兽爬虫有效，默认启用)')
    parser.add_argument('--no-browser', action='store_true',
                       help='禁用浏览器模式，使用本地或默认参数')
    parser.add_argument('--delay-min', type=float, default=5.0,
                       help='请求延迟最小值(秒) (默认: 5.0)')
    parser.add_argument('--delay-max', type=float, default=8.0,
                       help='请求延迟最大值(秒) (默认: 8.0)')
    parser.add_argument('--cached-params', type=str,
                       help='缓存参数文件路径')
    
    # Playwright收集器参数
    parser.add_argument('--headless', action='store_true',
                       help='无头模式运行浏览器')
    parser.add_argument('--target-url', type=str,
                       help='目标URL (仅对playwright模式有效)')
    
    args = parser.parse_args()
    
    # 处理浏览器参数冲突
    if args.no_browser:
        args.use_browser = False
    
    # 显示帮助示例
    if args.mode == 'help':
        show_help_examples()
        return
    
    print("=" * 60)
    print("CBG智能爬虫系统 v2.0.0")
    print("=" * 60)
    print(f"运行模式: {args.mode}")
    
    if args.mode == 'basic':
        print(f"爬虫类型: {args.type}")
        if args.type == 'equip':
            equip_type_names = {
                'normal': '普通装备',
                'lingshi': '灵饰', 
                'pet': '召唤兽装备'
            }
            print(f"装备类型: {equip_type_names.get(args.equip_type, args.equip_type)}")
        elif args.type == 'pet':
            print(f"召唤兽爬虫: 支持完整宠物数据")
            print(f"数据库: cbg_pets_{datetime.now().strftime('%Y%m')}.db")
        print(f"爬取页数: {args.pages}")
        print(f"延迟范围: {args.delay_min}-{args.delay_max}秒")
        if args.use_browser:
            print("浏览器模式: 启用")
            if args.type == 'pet':
                print("   - 可设置: 等级、价格、宠物类型、技能数、成长值、资质等筛选条件")
    elif args.mode == 'playwright':
        print("Playwright半自动数据收集模式")
        if args.headless:
            print("浏览器模式: 无头模式")
        else:
            print("浏览器模式: 有界面模式")
        if args.target_url:
            print(f"目标URL: {args.target_url}")
        else:
            print("目标URL: 使用默认推荐搜索页面")
    
    print("=" * 60)
    
    try:
        if args.mode == 'basic':
            run_basic_spider(
                max_pages=args.pages,
                spider_type=args.type,
                equip_type=args.equip_type,
                use_browser=args.use_browser,
                delay_range=(args.delay_min, args.delay_max),
                cached_params_file=args.cached_params
            )
        elif args.mode == 'proxy':
            run_proxy_spider(args.pages)
        elif args.mode == 'proxy-manager':
            run_proxy_manager()
        elif args.mode == 'test':
            run_tests()
        elif args.mode == 'playwright':
            run_playwright_collector(headless=args.headless, target_url=args.target_url)
            
        print("\n任务完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    main() 
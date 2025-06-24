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

def run_basic_spider(max_pages=5, spider_type='role', equip_type='normal', use_browser=True, delay_range=(1, 3)):
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
        from src.spider.equip import CBGEquipSpider
        print("✅ 成功导入CBGEquipSpider")
    except Exception as e:
        print(f"❌ 导入CBGEquipSpider失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        from src.spider.pet import CBGPetSpider
        print("✅ 成功导入CBGPetSpider")
    except Exception as e:
        print(f"❌ 导入CBGPetSpider失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        spider = CBGSpider()
        cbg_equip_spider = CBGEquipSpider()
        cbg_pet_spider = CBGPetSpider()
        print("🔧 CBG爬虫初始化完成")
        
        # 爬取数据
        print("开始爬取数据...")
        if spider_type == 'role':
            print(f"🎯 爬取角色数据，页数: {max_pages}")
            spider.crawl_all_pages(max_pages=max_pages, delay_range=delay_range, use_browser=use_browser)
        elif spider_type == 'equip':
            equip_type_names = {
                'normal': '普通装备',
                'lingshi': '灵饰',
                'pet': '召唤兽装备'
            }
            equip_name = equip_type_names.get(equip_type, equip_type)
            print(f"🎯 爬取{equip_name}数据，页数: {max_pages}")
            if use_browser:
                print("🌐 将启动浏览器进行参数设置...")
            cbg_equip_spider.crawl_all_pages(
                max_pages=max_pages, 
                delay_range=delay_range, 
                use_browser=use_browser,
                equip_type=equip_type
            )
        elif spider_type == 'pet':
            print(f"🎯 爬取召唤兽数据，页数: {max_pages}")
            if use_browser:
                print("🌐 将启动浏览器进行参数设置...")
            cbg_pet_spider.crawl_all_pages(
                max_pages=max_pages, 
                delay_range=delay_range, 
                use_browser=use_browser
            )    
        else:
            print(f"❌ 未知的爬虫类型: {spider_type}")
            return
            
        print("✅ 数据爬取完成")
        
        # # 导出Excel
        # print("\n正在导出Excel...")
        # excel_file = spider.export_to_excel()
        # if excel_file:
        #     print(f"Excel文件已生成: {excel_file}")
        # else:
        #     print("❌ Excel导出失败")
        
        # # 导出JSON
        # print("\n正在导出JSON...")
        # json_file = spider.export_to_json(filename=None, pretty=False)
        # if json_file:
        #     print(f"JSON文件已生成: {json_file}")
        # else:
        #     print("❌ JSON导出失败")
        
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

def show_help_examples():
    """显示使用示例"""
    print("\n" + "="*60)
    print("📖 使用示例")
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
    print("💡 召唤兽爬虫特色功能:")
    print("   • 支持完整的宠物属性: 等级、气血、伤害、防御、速度、法伤、法防等")
    print("   • 支持宠物筛选条件: 宠物类型、技能数量、成长值、资质范围等")
    print("   • 支持浏览器手动设置复杂搜索条件")
    print("   • 数据按月分割存储: cbg_pets_YYYYMM.db")
    print("   • 支持参数缓存，避免重复设置")
    print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='🎮 CBG智能爬虫系统 - 支持角色、装备、灵饰、召唤兽装备、召唤兽等多种数据爬取',
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

召唤兽爬虫详细说明:
  • 召唤兽数据包含: 基本信息、属性、技能、资质、成长、价格等完整数据
  • 支持浏览器模式手动设置筛选条件: 等级、价格、宠物类型、技能数、成长值、资质等
  • 支持本地参数缓存模式，避免重复设置搜索条件
  • 数据存储到 data/cbg_pets_YYYYMM.db，按月分割便于管理
        """
    )
    
    # 主要模式参数
    parser.add_argument('mode', choices=['basic', 'proxy', 'proxy-manager', 'test', 'help'], 
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
    parser.add_argument('--delay-min', type=float, default=1.0,
                       help='请求延迟最小值(秒) (默认: 1.0)')
    parser.add_argument('--delay-max', type=float, default=3.0,
                       help='请求延迟最大值(秒) (默认: 3.0)')
    
    args = parser.parse_args()
    
    # 处理浏览器参数冲突
    if args.no_browser:
        args.use_browser = False
    
    # 显示帮助示例
    if args.mode == 'help':
        show_help_examples()
        return
    
    print("=" * 60)
    print("🎮 CBG智能爬虫系统 v2.0.0")
    print("=" * 60)
    print(f"📊 运行模式: {args.mode}")
    
    if args.mode == 'basic':
        print(f"🎯 爬虫类型: {args.type}")
        if args.type == 'equip':
            equip_type_names = {
                'normal': '普通装备',
                'lingshi': '灵饰', 
                'pet': '召唤兽装备'
            }
            print(f"🔧 装备类型: {equip_type_names.get(args.equip_type, args.equip_type)}")
        elif args.type == 'pet':
            print(f"🐾 召唤兽爬虫: 支持完整宠物数据")
            print(f"🔧 数据库: cbg_pets_{datetime.now().strftime('%Y%m')}.db")
        print(f"📄 爬取页数: {args.pages}")
        print(f"⏱️  延迟范围: {args.delay_min}-{args.delay_max}秒")
        if args.use_browser:
            print("🌐 浏览器模式: 启用")
            if args.type == 'pet':
                print("   • 可设置: 等级、价格、宠物类型、技能数、成长值、资质等筛选条件")
    
    print("=" * 60)
    
    try:
        if args.mode == 'basic':
            run_basic_spider(
                max_pages=args.pages,
                spider_type=args.type,
                equip_type=args.equip_type,
                use_browser=args.use_browser,
                delay_range=(args.delay_min, args.delay_max)
            )
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
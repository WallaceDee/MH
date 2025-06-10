#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫Web界面 - API服务器
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import json
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# 全局变量
current_task = None
task_status = {"status": "idle", "message": "", "progress": 0}

@app.route('/')
def index():
    """API根路径"""
    return jsonify({
        "message": "CBG Spider API Server",
        "version": "2.0",
        "frontend": "请访问前端项目: http://localhost:8080"
    })

@app.route('/api/status')
def get_status():
    """获取当前任务状态"""
    return jsonify(task_status)

@app.route('/api/start_basic_spider', methods=['POST'])
def start_basic_spider():
    """启动基础爬虫"""
    global current_task, task_status
    
    if task_status["status"] == "running":
        return jsonify({"error": "已有任务在运行中"})
    
    data = request.json
    max_pages = data.get('pages', 5)
    export_excel = data.get('export_excel', True)
    export_json = data.get('export_json', True)
    
    def run_spider():
        global task_status
        try:
            task_status = {"status": "running", "message": "初始化爬虫...", "progress": 10}
            
            from cbg_spider import CBGSpider
            spider = CBGSpider()
            
            task_status["message"] = "开始爬取数据..."
            task_status["progress"] = 30
            
            spider.crawl_all_pages(max_pages=max_pages)
            
            task_status["message"] = "爬取完成，正在导出..."
            task_status["progress"] = 70
            
            results = {"files": []}
            
            if export_excel:
                excel_file = spider.export_to_excel()
                if excel_file:
                    results["files"].append({"type": "excel", "path": excel_file})
            
            if export_json:
                json_file = spider.export_to_json()
                if json_file:
                    results["files"].append({"type": "json", "path": json_file})
            
            task_status = {
                "status": "completed", 
                "message": f"完成！生成了 {len(results['files'])} 个文件", 
                "progress": 100,
                "results": results
            }
            
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}", "progress": 0}
    
    thread = threading.Thread(target=run_spider)
    thread.start()
    current_task = thread
    
    return jsonify({"message": "爬虫已启动"})

@app.route('/api/start_proxy_spider', methods=['POST'])
def start_proxy_spider():
    """启动代理爬虫"""
    global current_task, task_status
    
    if task_status["status"] == "running":
        return jsonify({"error": "已有任务在运行中"})
    
    data = request.json
    max_pages = data.get('pages', 5)
    
    def run_proxy_spider():
        global task_status
        try:
            task_status = {"status": "running", "message": "初始化代理爬虫...", "progress": 10}
            
            from cbg_crawler_with_proxy import EnhancedCBGCrawler
            
            task_status["message"] = "开始爬取数据..."
            task_status["progress"] = 30
            
            crawler = EnhancedCBGCrawler()
            crawler.start_crawling(max_pages=max_pages)
            
            task_status = {
                "status": "completed", 
                "message": "代理爬虫完成！", 
                "progress": 100
            }
            
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}", "progress": 0}
    
    thread = threading.Thread(target=run_proxy_spider)
    thread.start()
    current_task = thread
    
    return jsonify({"message": "代理爬虫已启动"})

@app.route('/api/manage_proxies', methods=['POST'])
def manage_proxies():
    """管理代理IP"""
    global task_status
    
    if task_status["status"] == "running":
        return jsonify({"error": "已有任务在运行中"})
    
    def get_proxies():
        global task_status
        try:
            task_status = {"status": "running", "message": "获取代理IP...", "progress": 50}
            
            from proxy_source_manager import ProxySourceManager
            manager = ProxySourceManager()
            proxies = manager.get_all_proxies()
            manager.save_proxies_to_file(proxies)
            
            task_status = {
                "status": "completed", 
                "message": f"获取到 {len(proxies)} 个代理IP", 
                "progress": 100,
                "results": {"proxy_count": len(proxies)}
            }
            
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}", "progress": 0}
    
    thread = threading.Thread(target=get_proxies)
    thread.start()
    
    return jsonify({"message": "代理管理器已启动"})

@app.route('/api/files')
def list_files():
    """列出输出文件和文件夹"""
    try:
        output_dir = os.path.join(project_root, 'output')
        if not os.path.exists(output_dir):
            return jsonify({"items": []})
        
        items = []
        for name in os.listdir(output_dir):
            item_path = os.path.join(output_dir, name)
            stat = os.stat(item_path)
            is_dir = os.path.isdir(item_path)
            
            items.append({
                "name": name,
                "size": stat.st_size if not is_dir else 0,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "path": item_path,
                "is_dir": is_dir 
            })
        
        items.sort(key=lambda x: (x['is_dir'], x['modified']), reverse=True)
        return jsonify({"items": items})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载文件"""
    try:
        output_dir = os.path.join(project_root, 'output')
        file_path = os.path.join(output_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "文件不存在"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system_info')
def system_info():
    """获取系统信息"""
    try:
        info = {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "project_root": project_root,
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/characters')
def get_characters():
    """获取角色列表（分页）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        level_min = request.args.get('level_min', type=int)
        level_max = request.args.get('level_max', type=int)
        school_skill_num = request.args.get('school_skill_num', type=int)
        school_skill_level = request.args.get('school_skill_level', type=int)
        
        # 角色修炼参数
        expt_gongji = request.args.get('expt_gongji', type=int)
        expt_fangyu = request.args.get('expt_fangyu', type=int)
        expt_fashu = request.args.get('expt_fashu', type=int)
        expt_kangfa = request.args.get('expt_kangfa', type=int)
        expt_total = request.args.get('expt_total', type=int)
        max_expt_gongji = request.args.get('max_expt_gongji', type=int)
        max_expt_fangyu = request.args.get('max_expt_fangyu', type=int)
        max_expt_fashu = request.args.get('max_expt_fashu', type=int)
        max_expt_kangfa = request.args.get('max_expt_kangfa', type=int)
        expt_lieshu = request.args.get('expt_lieshu', type=int)
        
        # 召唤兽修炼参数
        bb_expt_gongji = request.args.get('bb_expt_gongji', type=int)
        bb_expt_fangyu = request.args.get('bb_expt_fangyu', type=int)
        bb_expt_fashu = request.args.get('bb_expt_fashu', type=int)
        bb_expt_kangfa = request.args.get('bb_expt_kangfa', type=int)
        bb_expt_total = request.args.get('bb_expt_total', type=int)
        skill_drive_pet = request.args.get('skill_drive_pet', type=int)
        
        # 调用API获取数据
        from api.character_api import CharacterAPI
        api = CharacterAPI()
        result = api.get_characters(
            page=page,
            page_size=page_size,
            year=year,
            month=month,
            level_min=level_min,
            level_max=level_max,
            school_skill_num=school_skill_num,
            school_skill_level=school_skill_level,
            # 角色修炼参数
            expt_gongji=expt_gongji,
            expt_fangyu=expt_fangyu,
            expt_fashu=expt_fashu,
            expt_kangfa=expt_kangfa,
            expt_total=expt_total,
            max_expt_gongji=max_expt_gongji,
            max_expt_fangyu=max_expt_fangyu,
            max_expt_fashu=max_expt_fashu,
            max_expt_kangfa=max_expt_kangfa,
            expt_lieshu=expt_lieshu,
            # 召唤兽修炼参数
            bb_expt_gongji=bb_expt_gongji,
            bb_expt_fangyu=bb_expt_fangyu,
            bb_expt_fashu=bb_expt_fashu,
            bb_expt_kangfa=bb_expt_kangfa,
            bb_expt_total=bb_expt_total,
            skill_drive_pet=skill_drive_pet
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "获取角色列表失败"
        }), 500

def main():
    """启动API服务器"""
    print("🌐 CBG爬虫API服务器启动中...")
    print("🔗 API地址: http://localhost:5000")
    print("📱 前端地址: http://localhost:8080 (需要单独启动)")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main() 
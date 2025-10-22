#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Webhook自动部署服务
监听GitHub推送事件，自动触发部署
"""

import os
import json
import hmac
import hashlib
import subprocess
import logging
from flask import Flask, request, jsonify
from datetime import datetime

# 配置
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your-webhook-secret')
REPO_NAME = os.getenv('REPO_NAME', 'WallaceDee/MH')
BRANCH = os.getenv('BRANCH', 'master')
DEPLOY_SCRIPT = '/usr/lingtong/deploy/auto_deploy.sh'
LOG_FILE = '/var/log/webhook_deploy.log'

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def verify_signature(payload, signature):
    """验证GitHub Webhook签名"""
    if not signature:
        return False
    
    # 移除 'sha256=' 前缀
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    # 计算期望的签名
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def execute_deploy():
    """执行部署脚本"""
    try:
        logger.info("开始执行自动部署...")
        
        # 执行部署脚本
        result = subprocess.run(
            [DEPLOY_SCRIPT, 'deploy'],
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            logger.info("部署成功完成")
            return True, result.stdout
        else:
            logger.error(f"部署失败: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error("部署超时")
        return False, "部署超时"
    except Exception as e:
        logger.error(f"部署异常: {str(e)}")
        return False, str(e)

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理GitHub Webhook"""
    try:
        # 获取请求数据
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        event_type = request.headers.get('X-GitHub-Event')
        
        # 验证签名
        if not verify_signature(payload, signature):
            logger.warning("Webhook签名验证失败")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # 解析payload
        data = json.loads(payload)
        repo_name = data.get('repository', {}).get('full_name', '')
        ref = data.get('ref', '')
        
        # 检查是否是目标仓库和分支
        if repo_name != REPO_NAME:
            logger.info(f"忽略非目标仓库: {repo_name}")
            return jsonify({'message': 'Not target repository'}), 200
        
        if not ref.endswith(f'refs/heads/{BRANCH}'):
            logger.info(f"忽略非目标分支: {ref}")
            return jsonify({'message': 'Not target branch'}), 200
        
        # 检查事件类型
        if event_type not in ['push', 'workflow_run']:
            logger.info(f"忽略非部署事件: {event_type}")
            return jsonify({'message': 'Not deployment event'}), 200
        
        # 记录部署信息
        commit_sha = data.get('head_commit', {}).get('id', 'unknown')
        commit_message = data.get('head_commit', {}).get('message', 'No message')
        author = data.get('head_commit', {}).get('author', {}).get('name', 'Unknown')
        
        logger.info(f"触发部署 - 仓库: {repo_name}, 分支: {BRANCH}")
        logger.info(f"提交: {commit_sha[:8]} by {author}")
        logger.info(f"消息: {commit_message}")
        
        # 执行部署
        success, output = execute_deploy()
        
        if success:
            logger.info("Webhook部署成功")
            return jsonify({
                'message': 'Deployment successful',
                'commit': commit_sha,
                'output': output
            }), 200
        else:
            logger.error("Webhook部署失败")
            return jsonify({
                'message': 'Deployment failed',
                'error': output
            }), 500
            
    except json.JSONDecodeError:
        logger.error("无效的JSON payload")
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        logger.error(f"Webhook处理异常: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'webhook-deploy'
    })

@app.route('/status', methods=['GET'])
def status():
    """查看部署状态"""
    try:
        # 检查部署脚本是否存在
        if not os.path.exists(DEPLOY_SCRIPT):
            return jsonify({
                'status': 'error',
                'message': 'Deploy script not found'
            }), 500
        
        # 检查最近的服务状态
        result = subprocess.run(
            [DEPLOY_SCRIPT, 'status'],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'status': 'ok',
            'deploy_script_output': result.stdout,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("GitHub Webhook部署服务启动")
    logger.info(f"监听仓库: {REPO_NAME}")
    logger.info(f"监听分支: {BRANCH}")
    logger.info(f"部署脚本: {DEPLOY_SCRIPT}")
    
    app.run(
        host='0.0.0.0',
        port=9000,
        debug=False
    )

#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

SQUID_CONF = '/etc/squid/squid.conf'
SQUID_CONF_BACKUP = '/etc/squid/squid.conf.backup'

if not os.path.exists(SQUID_CONF):
    logger.error(f"Squid config not found at {SQUID_CONF}")

def run_command(cmd):
    try:
        logger.info(f"Running command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return {'success': result.returncode == 0, 'output': result.stdout, 'error': result.stderr}
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Command timed out'}
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Squid GUI Backend is running'})

@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        if not os.path.exists(SQUID_CONF):
            return jsonify({'error': 'Squid config file not found'}), 404
            
        with open(SQUID_CONF, 'r') as f:
            config = f.read()
        
        result = {
            'http_port': '3128',
            'cache_dir': '/var/spool/squid',
            'cache_mem': '256 MB',
            'visible_hostname': 'squid-proxy',
            'dns_nameservers': '8.8.8.8 8.8.4.4',
            'access_log': '/var/log/squid/access.log',
            'cache_log': '/var/log/squid/cache.log',
            'maximum_object_size': '4096 KB'
        }
        
        patterns = {
            'http_port': r'http_port\s+(\S+)',
            'cache_mem': r'cache_mem\s+(.+)',
            'visible_hostname': r'visible_hostname\s+(\S+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, config, re.MULTILINE)
            if match:
                result[key] = match.group(1).strip()
            
        return jsonify(result)
    except PermissionError:
        return jsonify({'error': 'Permission denied reading Squid config'}), 403
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    try:
        data = request.json
        
        if not os.path.exists(SQUID_CONF):
            return jsonify({'error': 'Squid config file not found'}), 404
        
        subprocess.run(f'cp {SQUID_CONF} {SQUID_CONF_BACKUP}', shell=True)
        
        with open(SQUID_CONF, 'r') as f:
            config = f.read()
        
        for key, value in data.items():
            if key == 'http_port':
                if re.search(r'http_port\s+\S+', config):
                    config = re.sub(r'http_port\s+\S+', f'http_port {value}', config)
            elif key == 'cache_mem':
                if re.search(r'cache_mem\s+.+', config):
                    config = re.sub(r'cache_mem\s+.+', f'cache_mem {value}', config)
            elif key == 'visible_hostname':
                if re.search(r'visible_hostname\s+\S+', config):
                    config = re.sub(r'visible_hostname\s+\S+', f'visible_hostname {value}', config)
        
        with open(SQUID_CONF, 'w') as f:
            f.write(config)
            
        return jsonify({'success': True, 'message': 'Configuration updated'})
    except PermissionError:
        return jsonify({'error': 'Permission denied writing Squid config'}), 403
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reload', methods=['POST'])
def reload_squid():
    result = run_command('systemctl reload squid')
    return jsonify(result)

@app.route('/api/restart', methods=['POST'])
def restart_squid():
    result = run_command('systemctl restart squid')
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def get_status():
    result = run_command('systemctl is-active squid')
    is_running = result['output'].strip() == 'active'
    return jsonify({'running': is_running, 'status': result['output'].strip()})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        lines = request.args.get('lines', 100, type=int)
        log_file = '/var/log/squid/access.log'
        
        if not os.path.exists(log_file):
            return jsonify([])
        
        result = run_command(f'tail -n {lines} {log_file}')
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        logs = []
        for line in result['output'].split('\n'):
            if line.strip():
                logs.append({
                    'timestamp': '2025-10-29 14:00:00',
                    'client': '192.168.1.1',
                    'method': 'GET',
                    'url': 'example.com',
                    'status': '200',
                    'size': '1024'
                })
        
        return jsonify(logs[-10:])
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = {
        'uptime': '5d 12h 34m',
        'requests': '125,847',
        'cacheHitRate': '67.8%',
        'bandwidth': '4.2 GB',
        'activeConnections': '23'
    }
    return jsonify(stats)

if __name__ == '__main__':
    logger.info("Starting Squid GUI Backend on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)

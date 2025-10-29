# Advanced Configuration

### Custom Log Parsing

The log parsing in the backend is currently simplified. To parse actual Squid logs, modify the `/api/logs` endpoint in `app.py`:


```python
@app.route('/api/logs', methods=['GET'])
def get_logs():
    # Parse Squid native log format
    # Format: timestamp elapsed remotehost code/status bytes method URL
    import re
    pattern = r'(\S+)\s+\S+\s+(\S+)\s+\S+/(\d+)\s+(\d+)\s+(\S+)\s+(\S+)'
    
    logs = []
    for line in result['output'].split('\n'):
        match = re.match(pattern, line)
        if match:
            logs.append({
                'timestamp': match.group(1),
                'client': match.group(2),
                'status': match.group(3),
                'size': match.group(4),
                'method': match.group(5),
                'url': match.group(6)
            })
```

### Adding New Configuration Fields

To manage additional Squid directives:

1.  **Add to GET endpoint** in `app.py`:


```python
result = {
    # ... existing fields ...
    'new_directive': 'default_value'
}

patterns = {
    # ... existing patterns ...
    'new_directive': r'new_directive\s+(.+)'
}
```

2.  **Add to POST endpoint** in `app.py`:


```python
for key, value in data.items():
    # ... existing conditions ...
    elif key == 'new_directive':
        if re.search(r'new_directive\s+.+', config):
            config = re.sub(r'new_directive\s+.+', f'new_directive {value}', config)
```

3.  **Update frontend** in `index.html` - no changes needed, it dynamically generates fields.

### Adding Custom API Endpoints

Example: Add cache statistics endpoint:


```python
@app.route('/api/cache-stats', methods=['GET'])
def get_cache_stats():
    result = run_command('squidclient mgr:info')
    # Parse output and return JSON
    return jsonify({'cache_stats': result['output']})
```

import subprocess, json

# Test if pmb MCP server sends instructions in initialize response
proc = subprocess.run(
    ['C:/Azazael/.venvs/py315t/Scripts/python.exe', 'C:/Users/clint/llama-server/unified/pams_server_launcher.py'],
    input='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n',
    capture_output=True, text=True, timeout=15,
    env={**__import__('os').environ, 'AI_MEMORY_DATA_DIR': 'C:/Users/clint/.pams/memory_data'}
)
print('stdout (first 500):', proc.stdout[:500])
# Check if instructions field is present
try:
    resp = json.loads(proc.stdout.strip().split('\n')[0])
    has_instructions = 'instructions' in (resp.get('result', {}) or {})
    print('has instructions field:', has_instructions)
    if has_instructions:
        print('instructions length:', len(resp['result']['instructions']))
except Exception as e:
    print('parse error:', e)
print('stderr (first 200):', proc.stderr[:200])
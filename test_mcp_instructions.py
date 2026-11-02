import subprocess, json, os

# Test if engram MCP server sends instructions in initialize response
proc = subprocess.run(
    ['C:/Users/clint/go/bin/engram.exe', 'mcp', '--tools=agent'],
    input='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n',
    capture_output=True, text=True, timeout=10
)
print('stdout:', proc.stdout[:1000])
print('stderr:', proc.stderr[:300])
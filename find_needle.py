src = open('Project_SHARDEX/ops.py', encoding="utf-8").read()
needle = 'raise OpError("unhandled op'
idx = src.find(needle)
print('found at:', idx)
print(repr(src[idx-100:idx+50]))
import json, subprocess, re, os, shutil
REPO = r'C:\Azazael\azazael'
ELIZA = os.path.join(REPO, 'Project_ELIZA')
APPLY = os.environ.get('APPLY') == '1'
idx = json.load(open(os.path.join(ELIZA, 'shards', 'SHARD_INDEX.json'), encoding='utf-8'))['shards']
wired = json.load(open(os.path.join(ELIZA, 'shards', 'WIRED.json'), encoding='utf-8'))['wired']
bymod = {e['shard_id']: e['path'] for e in idx}
st = subprocess.run(['git', 'status', '--porcelain', 'Project_ELIZA/shards'], cwd=REPO, capture_output=True).stdout.decode('utf-8', 'replace')
deleted = [l[3:].strip().strip('"') for l in st.splitlines() if l[:2].strip() == 'D']
sid_re = re.compile(r'^SHARD_ID\s*=\s*"([^"]+)"', re.M)
delsid = {}
for p in deleted:
    r = subprocess.run(['git', 'show', 'HEAD:' + p], cwd=REPO, capture_output=True)
    if r.returncode:
        continue
    t = r.stdout.decode('utf-8', 'replace')
    m = sid_re.search(t)
    if m and "import_module('adopted." in t:
        delsid[m.group(1)] = (p, t)

plan = []
for sid in wired:
    p = bymod.get(sid)
    if not p:
        continue
    r = subprocess.run(['git', 'cat-file', '-e', 'HEAD:Project_ELIZA/' + p], cwd=REPO, capture_output=True)
    if r.returncode != 0 and sid in delsid:
        plan.append((sid, delsid[sid][0], delsid[sid][1], p))

print('APPLY' if APPLY else 'DRY-RUN', '| planned writes:', len(plan))
written = 0
for sid, old, text, new in plan:
    if not APPLY:
        continue
    target = os.path.join(ELIZA, *new.split('/'))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    if os.path.exists(target):
        shutil.copy2(target, os.path.join(REPO, '.tmp_shardtest', 'newstubs', new.replace('/', '__')))
    with open(target, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    written += 1
print('written:', written)

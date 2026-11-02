import json
from collections import defaultdict

for name, path in [('graph.json','graphify-out/graph.json'),('merged','graphify-out/graph_merged_llama.json')]:
    g = json.load(open(path, encoding='utf-8'))
    nodes = g.get('nodes', [])
    edges = g.get('edges', g.get('links', []))
    adj = defaultdict(set)
    for e in edges:
        s, t = e.get('source'), e.get('target')
        if s and t:
            adj[s].add(t)
            adj[t].add(s)
    connected = sum(1 for n in nodes if adj.get(n.get('id') or n.get('label')))
    print(name + ': nodes=' + str(len(nodes)) + ' edges=' + str(len(edges)) + ' connected=' + str(connected))
    ranked = sorted(nodes, key=lambda n: -len(adj.get(n.get('id') or n.get('label'), ())))
    top5 = [n.get('label', n.get('id', '?')) for n in ranked[:5]]
    degs = [len(adj.get(n.get('id') or n.get('label'), ())) for n in ranked[:5]]
    print('  god_nodes: ' + str(top5))
    print('  degrees: ' + str(degs))
    # communities
    comms = set(n.get('community_name', n.get('community', '?')) for n in nodes)
    print('  communities: ' + str(len(comms)))
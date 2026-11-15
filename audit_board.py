import sqlite3
conn = sqlite3.connect('C:/Users/clint/.azazael/telemetry_store.db')
conn.row_factory = sqlite3.Row

# Check for available/claimed tasks
rows = conn.execute(
    'SELECT board_id, lane, task_id, state, claimed_by, claimed_at, note FROM lane_task_state WHERE state IN ("available", "claimed") ORDER BY board_id DESC LIMIT 50'
).fetchall()
print('=== Available/Claimed tasks ===')
for r in rows:
    print('board_id=' + str(r['board_id']) + ' lane=' + r['lane'] + ' task_id=' + str(r['task_id']) + ' state=' + r['state'] + ' by=' + str(r['claimed_by']) + ' at=' + str(r['claimed_at']) + ' note=' + str(r['note'])[:80])

# Check memorybus_queue for tasks topics
rows = conn.execute(
    'SELECT id, topic, content FROM memorybus_queue WHERE topic LIKE "lane.%.tasks" ORDER BY id DESC LIMIT 30'
).fetchall()
print()
print('=== Task queue (memorybus_queue) ===')
for r in rows:
    print('id=' + str(r['id']) + ' topic=' + r['topic'] + ' content=' + r['content'][:150])
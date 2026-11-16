import sys

sys.path.insert(0, "C:/Azazael/azazael/src")
from CORE.LaneMessageBoard import LaneMessageBoard

b = LaneMessageBoard(lane="freebuff")
msgs = b.poll_tasks("freebuff")
print("count:", len(msgs))
for m in msgs:
    # detail is a STRING on modern rows and a DICT on legacy ones, so
    # m.detail[:100] raised KeyError: slice(None, 100, None) on a dict
    # detail. str() first, then slice.
    detail = str(m.detail or "")[:100].encode("ascii", "ignore").decode()
    print("#", m.task_id, "|", m.action, "|", detail)

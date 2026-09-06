"""AOA EventBus - Cross-Arm pub/sub messaging system."""
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from collections import defaultdict
import threading, uuid


class EventPriority:
    LOW = 0
    NORMAL = 1
    MEDIUM = 1  # alias for NORMAL
    HIGH = 2
    CRITICAL = 3

@dataclass
class AOEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: str = ""
    source_arm: str = ""
    target_arm: str = ""
    payload: dict = field(default_factory=dict)
    priority: int = 1
    correlation_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)
    def to_dict(self) -> dict:
        return {"event_id":self.event_id,"event_type":self.event_type,"source_arm":self.source_arm,"target_arm":self.target_arm,"payload":self.payload,"priority":self.priority,"correlation_id":self.correlation_id,"timestamp":self.timestamp,"metadata":self.metadata}

class AOEventType:
    ARM_INITIALIZED="arm.initialized"; ARM_SHUTDOWN="arm.shutdown"; ARM_ERROR="arm.error"
    LIBRA_DOC_GENERATED="libra.doc.generated"; LIBRA_TEMPLATE_LOADED="libra.template.loaded"; LIBRA_FILING_COMPLETE="libra.filing.complete"
    AZAZAEL_WORM_EXECUTED="azazael.worm.executed"; AZAZAEL_CLUSTER_COMPLETE="azazael.cluster.complete"; AZAZAEL_ANOMALY_DETECTED="azazael.anomaly.detected"
    CODEX_RENDER_STARTED="codex.render.started"; CODEX_RENDER_COMPLETE="codex.render.complete"; CODEX_VIDEO_READY="codex.video.ready"
    EVE_MODEL_SELECTED="eve.model.selected"; EVE_BENCHMARK_COMPLETE="eve.benchmark.complete"; EVE_INFERENCE_COMPLETE="eve.inference.complete"
    WORKFLOW_STARTED="workflow.started"; WORKFLOW_STEP_COMPLETE="workflow.step.complete"; WORKFLOW_COMPLETE="workflow.complete"; WORKFLOW_FAILED="workflow.failed"
    SESSION_MILESTONE="session.milestone"; SESSION_STARTED="session.started"; SESSION_COMPLETED="session.completed"

class EventBus:
    def __init__(self, max_history=1000):
        self._subscribers=defaultdict(list); self._history=[]; self._max_history=max_history; self._lock=threading.Lock()
    def publish(self, event):
        with self._lock:
            self._history.append(event)
            if len(self._history)>self._max_history: self._history=self._history[-self._max_history:]
        for pattern,cbs in self._subscribers.items():
            if self._match_pattern(pattern, event.event_type):
                for cb in cbs:
                    try: cb(event)
                    except: pass
    def subscribe(self, pattern, cb):
        with self._lock: self._subscribers[pattern].append(cb)
    def unsubscribe(self, pattern, cb):
        with self._lock:
            if pattern in self._subscribers: self._subscribers[pattern]=[c for c in self._subscribers[pattern] if c!=cb]
    def get_history(self, event_type=None, source_arm=None, limit=100):
        with self._lock:
            r=self._history
            if event_type: r=[e for e in r if e.event_type==event_type]
            if source_arm: r=[e for e in r if e.source_arm==source_arm]
            return r[-limit:]
    def get_correlated_events(self, cid):
        with self._lock: return [e for e in self._history if e.correlation_id==cid]
    def clear_history(self):
        with self._lock: self._history.clear()
    @staticmethod
    def _match_pattern(pattern, event_type):
        if pattern==event_type or pattern=="*": return True
        if pattern.endswith(".*") and event_type.startswith(pattern[:-2]): return True
        if pattern.startswith("*.") and event_type.endswith(pattern[2:]): return True
        return False
    @property
    def subscriber_count(self):
        with self._lock: return sum(len(cbs) for cbs in self._subscribers.values())
    @property
    def history_count(self):
        with self._lock: return len(self._history)

class EventPipeline:
    def __init__(self, bus, name=""): self.bus=bus; self.name=name; self._steps=[]
    def add_step(self, h): self._steps.append(h)
    def execute(self, initial):
        results=[initial]; current=initial
        for i,step in enumerate(self._steps):
            try:
                nxt=step(current)
                if nxt is None: break
                results.append(nxt); current=nxt
            except Exception as e:
                results.append(AOEvent(event_type=AOEventType.WORKFLOW_FAILED,source_arm="pipeline."+self.name,payload={"step":i,"error":str(e)},correlation_id=initial.correlation_id,priority=3))
                break
        return results

_gb=None
def get_event_bus():
    global _gb
    if _gb is None: _gb=EventBus()
    return _gb

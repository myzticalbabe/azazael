"""
Worker Automation Suite — increases lane usefulness for work.

Implements:
1. Clinical lane independence (separate from kilo)
2. Automated task dispatcher with dependency graph
3. Health/heartbeat monitoring with auto-recovery
4. Model diversity configuration
5. Cross-lane lesson sharing bus
6. Work stealing protocol
7. Local LLM dev task routing
8. Auto code review spawner
9. Test aggregator
10. Metrics collector
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from concurrent.futures import ThreadPoolExecutor

# Add paths
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from CORE.LaneMessageBoard import LaneMessageBoard


# ─── Configuration ─────────────────────────────────────────────────────────────

@dataclass
class LaneConfig:
    name: str
    model: str
    specialty: str
    max_concurrent: int = 5
    health_check_interval: int = 30  # seconds
    work_steal_enabled: bool = True


LANE_CONFIGS = {
    "kilo": LaneConfig("kilo", "nemotron", "architecture, substrate, clinical", max_concurrent=5),
    "freebuff": LaneConfig("freebuff", "muse", "sensory, pacing, timer", max_concurrent=5),
    "opencode": LaneConfig("opencode", "beam", "affect, time, load, companion", max_concurrent=5),
    "clinical": LaneConfig("clinical", "qwen35", "dsm5-tr/icd11 crosswalk", max_concurrent=3),
}

DB_PATH = Path("C:/Users/clint/.azazael/telemetry_store.db")


# ─── Health Monitor ────────────────────────────────────────────────────────────

class HealthMonitor:
    """Monitors lane health via heartbeat in lane.<lane>.status"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.last_heartbeat: dict[str, datetime] = {}
        self.missing_threshold = timedelta(seconds=60)
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _monitor_loop(self):
        while self._running:
            self._check_health()
            time.sleep(10)

    def _check_health(self):
        for lane_name in LANE_CONFIGS:
            hb = self._get_last_heartbeat(lane_name)
            if hb is None:
                print(f"[HEALTH] {lane_name}: NO HEARTBEAT")
                self._trigger_recovery(lane_name)
            elif datetime.now() - hb > self.missing_threshold:
                print(f"[HEALTH] {lane_name}: STALE ({datetime.now() - hb})")
                self._trigger_recovery(lane_name)
            else:
                self.last_heartbeat[lane_name] = hb

    def _get_last_heartbeat(self, lane: str) -> datetime | None:
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp FROM memorybus_queue
                WHERE topic = ? AND content LIKE '%heartbeat%'
                ORDER BY timestamp DESC LIMIT 1
            """, (f"lane.{lane}.status",))
            row = cursor.fetchone()
            conn.close()
            if row:
                return datetime.fromisoformat(row[0].replace('Z', '+00:00'))
        except Exception as e:
            print(f"[HEALTH] Heartbeat query failed for {lane}: {e}")
            return None
        return None

    def _trigger_recovery(self, lane: str):
        print(f"[RECOVERY] Triggering for {lane}")
        # Re-assign claimed tasks back to available
        self._reassign_stuck_tasks(lane)

    def _reassign_stuck_tasks(self, lane: str):
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lane_task_state
                SET state = 'available', claimed_by = NULL, claimed_at = NULL, attempts = attempts + 1
                WHERE lane = ? AND state = 'claimed' AND claimed_by = ?
            """, (lane, lane))
            conn.commit()
            print(f"[RECOVERY] Re-assigned {cursor.rowcount} stuck tasks from {lane}")
            conn.close()
        except Exception as e:
            print(f"[RECOVERY ERROR] {e}")


# ─── Heartbeat Sender ──────────────────────────────────────────────────────────

class HeartbeatSender:
    """Sends periodic heartbeat to lane.<lane>.status"""

    def __init__(self, lane: str, db_path: Path = DB_PATH):
        self.lane = lane
        self.db_path = db_path
        self._running = False
        self._thread: threading.Thread | None = None
        self.interval = 30  # seconds

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        board = LaneMessageBoard(lane=self.lane)
        while self._running:
            try:
                board.announce(f"heartbeat: {self.lane} alive at {datetime.now().isoformat()}")
            except Exception as e:
                print(f"[HEARTBEAT] {self.lane} announce failed: {e}")
            time.sleep(self.interval)


# ─── Automated Dispatcher ──────────────────────────────────────────────────────

@dataclass
class TaskNode:
    task_id: str
    lane: str
    action: str
    detail: str
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, ready, running, done, blocked


class DependencyDispatcher:
    """Automated task dispatch with dependency resolution"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.task_graph: dict[str, TaskNode] = {}
        self._lock = threading.Lock()

    def register_task(self, task: TaskNode):
        with self._lock:
            self.task_graph[task.task_id] = task

    def get_ready_tasks(self, lane: str) -> list[TaskNode]:
        """Get tasks for lane whose dependencies are satisfied"""
        with self._lock:
            ready = []
            for task in self.task_graph.values():
                if task.lane != lane or task.status != "pending":
                    continue
                deps_met = all(
                    self.task_graph[dep].status == "done"
                    for dep in task.depends_on
                    if dep in self.task_graph
                )
                if deps_met:
                    task.status = "ready"
                    ready.append(task)
            return ready

    def mark_running(self, task_id: str):
        with self._lock:
            if task_id in self.task_graph:
                self.task_graph[task_id].status = "running"

    def mark_done(self, task_id: str):
        with self._lock:
            if task_id in self.task_graph:
                self.task_graph[task_id].status = "done"

    def dispatch_loop(self, lane: str, interval: int = 5):
        """Continuously dispatch ready tasks to lane"""
        board = LaneMessageBoard(lane=lane)
        while True:
            ready = self.get_ready_tasks(lane)
            for task in ready:
                self.mark_running(task.task_id)
                try:
                    row = board.push_hook(lane, task.action, task.detail, task.task_id)
                    print(f"[DISPATCH] {lane} <- {task.task_id} ({row})")
                except Exception as e:
                    print(f"[DISPATCH ERROR] {task.task_id}: {e}")
            time.sleep(interval)


# ─── Work Stealing ─────────────────────────────────────────────────────────────

class WorkStealer:
    """Allows idle lanes to steal work from busy lanes"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def steal_work(self, idle_lane: str, max_items: int = 3) -> list[dict]:
        """Steal available work from other lanes"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        # Find lanes with available work
        cursor.execute("""
            SELECT DISTINCT lts.lane, COUNT(*) as cnt
            FROM lane_task_state lts
            LEFT JOIN memorybus_queue mq ON mq.id = lts.board_id
            WHERE lts.state IN ('available', 'open')
            AND mq.topic LIKE 'lane.%.tasks'
            AND lts.lane != ?
            GROUP BY lts.lane
            ORDER BY cnt DESC
        """, (idle_lane,))

        victims = cursor.fetchall()
        stolen = []

        for victim_lane, cnt in victims:
            if cnt == 0:
                continue
            # Claim from victim
            victim_board = LaneMessageBoard(lane=victim_lane)
            tasks = victim_board.claim_tasks(victim_lane, limit=min(max_items, cnt))
            for t in tasks:
                # Re-assign to idle lane
                reassign_board = LaneMessageBoard(lane=idle_lane)
                row = reassign_board.push_hook(
                    idle_lane, t["action"], t["detail"], t["task_id"]
                )
                stolen.append({"from": victim_lane, "task_id": t["task_id"], "row": row})
                print(f"[STEAL] {idle_lane} stole {t['task_id']} from {victim_lane}")

            if len(stolen) >= max_items:
                break

        conn.close()
        return stolen

    def start_stealer(self, idle_lane: str, interval: int = 60):
        """Background thread that steals when idle"""
        def loop():
            while True:
                # Check if lane has no available work
                board = LaneMessageBoard(lane=idle_lane)
                tasks = board.claim_tasks(idle_lane, limit=1)
                if not tasks:  # No work available
                    self.steal_work(idle_lane)
                time.sleep(interval)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()


# ─── Lesson Bus ────────────────────────────────────────────────────────────────

class LessonBus:
    """Cross-lane lesson sharing via lane.all.lessons"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def publish_lesson(self, source_lane: str, lesson: dict):
        """Publish lesson to all lanes"""
        lesson["source_lane"] = source_lane
        lesson["published_at"] = datetime.now().isoformat()
        for dest_lane in LANE_CONFIGS:
            try:
                board = LaneMessageBoard(lane=dest_lane)
                row = board.push_hook(
                    dest_lane, "lesson", json.dumps(lesson),
                    f"lesson_{int(time.time())}_{dest_lane}"
                )
                print(f"[LESSON] {source_lane} -> {dest_lane}: {lesson.get('title', 'untitled')}")
            except Exception as e:
                print(f"[LESSON ERROR] {dest_lane}: {e}")

    def subscribe(self, lane: str, since_id: int = 0) -> list[dict]:
        """Get new lessons for lane"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, content FROM memorybus_queue
            WHERE topic = 'lane.all.lessons' AND id > ?
            ORDER BY id ASC
        """, (since_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "lesson": json.loads(r[1])} for r in rows]


# ─── Local LLM Router ──────────────────────────────────────────────────────────

class LocalLLMRouter:
    """Routes coding tasks to eve_unleashed swarm (16 workers)"""

    def __init__(self):
        from eve_unleashed.swarm_oracle import swarm
        self.swarm = swarm

    def route_coding_task(self, claims: list[str], workers: int = 16) -> dict:
        """Route coding claims to local LLM swarm"""
        print(f"[LLM ROUTER] Routing {len(claims)} tasks to local swarm ({workers} workers)")
        return self.swarm(claims=claims, grievance_id=f"llm_route_{int(time.time())}", live=False, workers=workers)

    def route_dev_tasks(self, tasks: list[dict]) -> dict:
        """Route development tasks (implement, fix, test) to swarm"""
        claims = [f"{t['type']}: {t['detail']}" for t in tasks]
        return self.route_coding_task(claims)


# ─── Auto Code Review ──────────────────────────────────────────────────────────

class AutoCodeReview:
    """Spawns reviewer agents for changes"""

    def __init__(self):
        self.llm = LocalLLMRouter()

    def review_changes(self, files: list[str], diff: str) -> dict:
        """Review code changes via local LLM"""
        claims = [
            f"REVIEW: {f} - {diff[:500]}" for f in files
        ]
        return self.llm.route_coding_task(claims, workers=8)

    def review_pr(self, pr_files: list[str]) -> dict:
        """Review PR files"""
        return self.review_changes(pr_files, "")


# ─── Test Aggregator ───────────────────────────────────────────────────────────

class TestAggregator:
    """Aggregates test results across lanes"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def aggregate_sarah(self) -> dict:
        """Aggregate SARAH test results"""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            cwd="C:/Azazael/azazael", capture_output=True, text=True, timeout=120
        )
        sarah_tests = [l for l in result.stdout.split("\n") if "sarah" in l.lower()]
        return {
            "total_collected": len(sarah_tests),
            "tests": sarah_tests[:20]
        }

    def run_lane_tests(self, lane: str) -> dict:
        """Run tests for specific lane"""
        lane_modules = {
            "kilo": ["test_sarah_profile", "test_sarah_predict", "test_sarah_initiate", "test_sarah_offload", "test_sarah_crosswalk", "test_sarah_pacing"],
            "freebuff": ["test_sarah_mixer", "test_sarah_transitions", "test_sarah_pacing", "test_sarah_timer", "test_sarah_redundancy"],
            "opencode": ["test_sarah_interocept", "test_sarah_affirmation", "test_sarah_timeview", "test_sarah_load", "test_sarah_companion"],
        }
        modules = lane_modules.get(lane, [])
        if not modules:
            return {"error": f"Unknown lane: {lane}"}

        test_paths = " ".join(f"tests/{m}.py" for m in modules)
        result = subprocess.run(
            ["python", "-m", "pytest", test_paths, "-v", "--tb=short"],
            cwd="C:/Azazael/azazael", capture_output=True, text=True, timeout=300
        )
        return {
            "lane": lane,
            "exit_code": result.returncode,
            "passed": result.stdout.count(" PASSED"),
            "failed": result.stdout.count(" FAILED"),
            "output": result.stdout[-2000:]
        }


# ─── Metrics Collector ─────────────────────────────────────────────────────────

class MetricsCollector:
    """Collects lane metrics: throughput, queue depth, error rate, latency"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def collect(self) -> dict:
        """Collect current metrics"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        metrics = {}

        # Queue depths per lane
        for lane in LANE_CONFIGS:
            cursor.execute("""
                SELECT state, COUNT(*) FROM lane_task_state lts
                LEFT JOIN memorybus_queue mq ON mq.id = lts.board_id
                WHERE lts.lane = ? AND mq.topic = ?
                GROUP BY state
            """, (lane, f"lane.{lane}.tasks"))
            metrics[f"{lane}_queue"] = dict(cursor.fetchall())

        # Throughput (done in last hour)
        hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        for lane in LANE_CONFIGS:
            cursor.execute("""
                SELECT COUNT(*) FROM lane_task_state lts
                LEFT JOIN memorybus_queue mq ON mq.id = lts.board_id
                WHERE lts.lane = ? AND lts.state = 'done' AND lts.retired_at > ?
            """, (lane, hour_ago))
            metrics[f"{lane}_throughput_1h"] = cursor.fetchone()[0]

        # Error rate
        for lane in LANE_CONFIGS:
            cursor.execute("""
                SELECT COUNT(*) FROM lane_task_state
                WHERE lane = ? AND state = 'blocked'
            """, (lane,))
            metrics[f"{lane}_blocked"] = cursor.fetchone()[0]

        conn.close()
        return metrics

    def start_collector(self, interval: int = 60):
        """Background metrics collection"""
        def loop():
            while True:
                m = self.collect()
                print(f"[METRICS] {json.dumps(m, indent=2)}")
                time.sleep(interval)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()


# ─── Main Orchestrator ─────────────────────────────────────────────────────────

class WorkerAutomation:
    """Main orchestrator for all worker automation"""

    def __init__(self):
        self.health = HealthMonitor()
        self.dispatcher = DependencyDispatcher()
        self.stealer = WorkStealer()
        self.lesson_bus = LessonBus()
        self.llm_router = LocalLLMRouter()
        self.code_review = AutoCodeReview()
        self.test_agg = TestAggregator()
        self.metrics = MetricsCollector()
        self.heartbeats: dict[str, HeartbeatSender] = {}

    def start(self):
        """Start all automation components"""
        print("[AUTOMATION] Starting worker automation suite...")

        # Start health monitor
        self.health.start()

        # Start heartbeats for each lane
        for lane in LANE_CONFIGS:
            hb = HeartbeatSender(lane)
            hb.start()
            self.heartbeats[lane] = hb

        # Start metrics collector
        self.metrics.start_collector(interval=60)

        # Start work stealers for each lane
        for lane in LANE_CONFIGS:
            if LANE_CONFIGS[lane].work_steal_enabled:
                self.stealer.start_stealer(lane)

        # Register SARAH tasks with dispatcher
        self._register_sarah_tasks()

        print("[AUTOMATION] All components started")

    def _register_sarah_tasks(self):
        """Register SARAH build tasks with dependency graph"""
        tasks = [
            # B1 - Profile (kilo) - no deps
            TaskNode("SARAH-B1", "kilo", "sarah_b1_profile", "B1 profile contract", []),
            # B6 - Predictability (kilo) - depends on B1
            TaskNode("SARAH-M6", "kilo", "sarah_m6_predict", "M6 predictability", ["SARAH-B1"]),
            # B2 - Sensory (freebuff) - depends on B1
            TaskNode("SARAH-B2", "freebuff", "sarah_b2_sensory", "B2 sensory M3/M4", ["SARAH-B1"]),
            # B3 - Affect (opencode) - depends on B1
            TaskNode("SARAH-B3", "opencode", "sarah_b3_affect", "B3 affect M8/M14", ["SARAH-B1"]),
            # B4/B5 - Time/Load/Companion/Affirmation (opencode) - depends on B3
            TaskNode("SARAH-B4", "opencode", "sarah_b4_time", "B4 time scaffolding M9", ["SARAH-B3"]),
            TaskNode("SARAH-B5", "opencode", "sarah_b5_load", "B5 load M12/M13", ["SARAH-B3"]),
            # M10 - Offload (kilo) - depends on B1
            TaskNode("SARAH-M10", "kilo", "sarah_m10_offload", "M10 offload", ["SARAH-B1"]),
            # M11 - Initiation (kilo) - depends on B1
            TaskNode("SARAH-M11", "kilo", "sarah_m11_initiate", "M11 initiation", ["SARAH-B1"]),
            # B6 - Pacing/Timer/Redundancy (freebuff) - depends on B2
            TaskNode("SARAH-B6", "freebuff", "sarah_b6_pacing", "B6 pacing M5/M15", ["SARAH-B2"]),
            # B8 - Clinical (clinical) - depends on B1 + M6
            TaskNode("SARAH-B8", "clinical", "sarah_b8_clinical", "B8 clinical crosswalk", ["SARAH-B1", "SARAH-M6"]),
        ]
        for t in tasks:
            self.dispatcher.register_task(t)

    def stop(self):
        """Stop all components"""
        self.health.stop()
        for hb in self.heartbeats.values():
            hb.stop()


# ─── Demo / Entry Point ────────────────────────────────────────────────────────

def main():
    automation = WorkerAutomation()
    automation.start()

    try:
        # Keep running
        while True:
            time.sleep(10)
            # Print metrics
            m = automation.metrics.collect()
            print(f"[METRICS] {json.dumps(m, indent=2)}")
    except KeyboardInterrupt:
        print("\n[AUTOMATION] Shutting down...")
        automation.stop()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
AZAZAEL CORE Demo - Demonstrates FreeThreadedAgent + MemoryBus + PAMS.

This script:
1. Creates a MemoryBus
2. Creates a PamsBusBridge to persist events to PAMS
3. Creates DemoAgents that communicate via MemoryBus
4. Demonstrates pub/sub lifecycle and PAMS persistence

Usage:
    python demo_core.py

Requires:
    - PAMS server running on localhost:5100 (optional)
"""

import sys
import os
import time
import json

# Ensure CORE is importable
_ft_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _ft_path not in sys.path:
    sys.path.insert(0, _ft_path)

from CORE.MemoryBus import BusMessage, MemoryBus
from CORE.FreeThreadedAgent import FreeThreadedAgent
from CORE.freethreading import FreeThreadPool, is_free_threaded

IS_FREE_THREADED = is_free_threaded()

# Attempt to import PamsBusBridge (will work if PAMS is available)
HAS_PAMS_BRIDGE = False
try:
    from CORE.PamsBusBridge import PamsBusBridge
    HAS_PAMS_BRIDGE = True
except ImportError:
    pass

# Check if PAMS is actually running
PAMS_AVAILABLE = False
try:
    import urllib.request
    r = urllib.request.urlopen("http://localhost:5100/health", timeout=2)
    if r.status == 200:
        PAMS_AVAILABLE = True
        print("  PAMS server: ONLINE")
    else:
        print("  PAMS server: UNEXPECTED STATUS")
except Exception:
    print("  PAMS server: OFFLINE (demo will skip PAMS persistence)")


class DemoAgent(FreeThreadedAgent):
    """A simple demo agent that publishes events to MemoryBus."""

    def __init__(self, name, memory_bus=None, pool=None):
        super().__init__(name=name, memory_bus=memory_bus, pool=pool)
        self.events_published = 0

    def run(self):
        """Main agent loop: publish periodic events to MemoryBus."""
        self.log("info", f"DemoAgent [{self.name}] started")
        counter = 0
        while self.is_running:
            counter += 1
            # Publish an event to MemoryBus
            count = self.memory_bus.publish(
                topic="demo.heartbeat",
                content={
                    "agent": self.name,
                    "counter": counter,
                    "free_threaded": IS_FREE_THREADED,
                    "timestamp": time.time(),
                },
                source=self.name,
            )
            self.events_published += 1
            self.log("info", f"Published heartbeat #{counter} ({count} subscribers)")
            # Sleep between heartbeats
            for _ in range(10):
                if not self.is_running:
                    break
                time.sleep(0.1)

    def get_stats(self):
        base = super().get_stats() if hasattr(super(), "get_stats") else {}
        return {
            **base,
            "events_published": self.events_published,
            "name": self.name,
        }


class DemoSubscriber(FreeThreadedAgent):
    """A demo agent that subscribes to MemoryBus events and logs them."""

    def __init__(self, name, memory_bus=None, pool=None):
        super().__init__(name=name, memory_bus=memory_bus, pool=pool)
        self.received_events = []
        self._subscription = None

    def on_start(self):
        """Subscribe to heartbeat events on start."""
        self._subscription = self.memory_bus.subscribe(
            "demo.heartbeat",
            callback=self._on_heartbeat,
        )
        self.log("info", f"Subscribed to demo.heartbeat")

    def _on_heartbeat(self, message: BusMessage):
        """Handle incoming heartbeat messages."""
        self.received_events.append(message)
        payload = message.content
        self.log("info", f"Received heartbeat #{payload.get("counter")} from {payload.get("agent")}")

    def run(self):
        """Main loop."""
        self.log("info", f"DemoSubscriber [{self.name}] listening...")
        while self.is_running:
            time.sleep(1.0)

    def on_stop(self):
        """Clean up subscription."""
        if self._subscription:
            try:
                self.memory_bus.unsubscribe(self._subscription)
            except Exception:
                pass

    def get_stats(self):
        return {
            "received_count": len(self.received_events),
            "name": self.name,
        }


def main():
    print("=" * 60)
    print("  AZAZAEL CORE Demo")
    print("  Free-threaded Python 3.14t")
    print("=" * 60)
    print(f"  IS_FREE_THREADED: {IS_FREE_THREADED}")
    print()

    # 1. Create shared MemoryBus
    print("  [1/4] Creating MemoryBus...")
    bus = MemoryBus()
    print(f"        MemoryBus created")
    print()

    # 2. Create PamsBusBridge if PAMS is available
    bridge = None
    if PAMS_AVAILABLE and HAS_PAMS_BRIDGE:
        print("  [2/4] Creating PamsBusBridge...")
        bridge = PamsBusBridge(memory_bus=bus, pams_url="http://localhost:5100")
        bridge.subscribe_topic("demo.heartbeat")  # Live demo topic
        bridge.start()
        print(f"        PamsBusBridge started - persisting events to PAMS")
    else:
        print("  [2/4] PamsBusBridge: SKIPPED (PAMS offline)")
    print()

    # 3. Create DemoAgents
    print("  [3/4] Creating agents...")
    pool = FreeThreadPool(max_workers=4, name="DemoPool")
    agent1 = DemoAgent(name="Alpha", memory_bus=bus, pool=pool)
    agent2 = DemoAgent(name="Beta", memory_bus=bus, pool=pool)
    subscriber = DemoSubscriber(name="Logger", memory_bus=bus, pool=pool)
    print(f"        Alpha (DemoAgent) created")
    print(f"        Beta (DemoAgent) created")
    print(f"        Logger (DemoSubscriber) created")
    print()

    # 4. Start all agents
    print("  [4/4] Starting agents...")
    subscriber.start()
    agent1.start()
    time.sleep(0.3)
    agent2.start()
    print()

    # Let them run for a bit
    print("  --- Agents running (collecting events)...")
    time.sleep(2.0)

    # Stop agents
    print("  --- Stopping agents...")
    agent1.stop()
    agent2.stop()
    subscriber.stop()
    if bridge:
        bridge.stop()

    agent1.wait()
    agent2.wait()
    subscriber.wait()
    if bridge:
        bridge.wait()

    print()

    # Results
    print("=" * 60)
    print("  DEMO RESULTS")
    print("=" * 60)
    print(f"  Alpha events published:  {agent1.events_published}")
    print(f"  Beta events published:   {agent2.events_published}")
    print(f"  Logger events received:  {len(subscriber.received_events)}")
    print(f"  MemoryBus history:       {len(bus.history())} messages")
    print(f"  MemoryBus topics:        {bus.topics()}")
    if bridge:
        stats = bridge.bridge_stats()
        print(f"  PAMS persisted:          {stats.get('persisted', 0)}")
        print(f"  PAMS failed:             {stats.get('failed', 0)}")

    # Verify pub/sub worked
    print()
    if len(subscriber.received_events) > 0:
        print("  >>> DEMO PASSED: Pub/sub working correctly <<<")
    else:
        print("  >>> DEMO FAILED: No events received <<<")
    print("=" * 60)


if __name__ == "__main__":
    main()

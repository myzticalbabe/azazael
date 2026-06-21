# coding: utf-8
"""
Azazael Dynamic Logger v1.0 - Real-time persistent logging
"""
import os
import threading
from pathlib import Path
from datetime import datetime
from collections import deque
import queue

class LogLevel:
    DEBUG, INFO, WARN, ERROR, SUCCESS = "DEBUG", "INFO", "WARN", "ERROR", "SUCCESS"

class DynamicLogger:
    _instance, _lock = None, threading.Lock()
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        self._log_queue, self._log_history = queue.Queue(), deque(maxlen=1000)
        self._quiet, self._output_enabled = False, True
        self._start_writer()

    def _start_writer(self):
        threading.Thread(target=self._write_loop, daemon=True).start()

    def _write_loop(self):
        while True:
            try:
                msg = self._log_queue.get(timeout=0.1)
                if msg is None: break
                self._persist(msg)
            except queue.Empty: continue

    def _persist(self, msg):
        try:
            log_dir = Path(__file__).parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            lp = log_dir / "azazael_dynamic.log"
            with open(lp, 'a', encoding='utf-8') as f:
                f.write(f"{msg['ts']} | {msg['lvl']:7} | {msg['msg']}\n")
                f.flush(); os.fsync(f.fileno())
        except Exception: pass

    def log(self, msg, lvl=LogLevel.INFO, tag=""):
        if self._quiet: return
        ts, full = datetime.now().isoformat(), f"{tag} {msg}".strip() if tag else msg
        data = {'ts': ts, 'lvl': lvl, 'msg': full}
        self._log_history.append(data)
        if self._output_enabled:
            syms = {LogLevel.DEBUG: "[?]", LogLevel.INFO: "[+]", LogLevel.WARN: "[!]", LogLevel.ERROR: "[-]", LogLevel.SUCCESS: "[*]"}
            print(f"{syms.get(lvl, '[?]')} {ts[11:19]} {full}", flush=True)
        self._log_queue.put(data)

    def debug(self, m, t=""): self.log(m, LogLevel.DEBUG, t)
    def info(self, m, t=""): self.log(m, LogLevel.INFO, t)
    def warn(self, m, t=""): self.log(m, LogLevel.WARN, t)
    def error(self, m, t=""): self.log(m, LogLevel.ERROR, t)
    def success(self, m, t=""): self.log(m, LogLevel.SUCCESS, t)

logger = DynamicLogger()
log = logger.log; info = logger.info; warn = logger.warn; error = logger.error; success = logger.success

# coding: utf-8
"""
HORUS - Human-Readable Output Unified System

ML Groupings Results Viewer with Visual Popup Display
Machine-Readable Ecosystem Information Export
Live Monitor for Real-Time Ecosystem Tracking

Usage:
    >>> import horus
    >>> horus.display_results()
    >>> horus.watch_for_updates()
    >>> horus.export_ecosystem_info()
    >>> horus.launch_live_monitor()
    >>> horus.launch_monitor()

Configuration:
    - Output format: HTML, JSON, Console
    - Destination: popup, file, browser, all
    - Path: C:/Users/clint/Desktop/HORUS
"""

import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import ttk, scrolledtext


class MLGroup(Enum):
    """ML Platform Groupings."""

    CORE = "Core"
    QLEARNING = "Q-Learning"
    INTEGRATION = "Integration"
    MONITORING = "Monitoring"
    LM_STUDIO = "LM Studio"
    ANALYSIS = "Analysis"
    CONVERSION = "Conversion"
    INSTALLATION = "Installation"
    AUTOLOAD = "Autoload"
    IMPROVEMENTS = "Improvements"


class OutputFormat(Enum):
    """Output format options."""

    HTML = "html"
    JSON = "json"
    CONSOLE = "console"


class OutputDestination(Enum):
    """Output destination options."""

    POPUP = "popup"
    FILE = "file"
    BROWSER = "browser"
    ALL = "all"


@dataclass
class OutputConfig:
    """Configuration for HORUS output."""

    format: OutputFormat = OutputFormat.HTML
    destination: OutputDestination = OutputDestination.ALL
    base_path: str = "C:/Users/clint/Desktop/HORUS"
    auto_open_browser: bool = True
    include_timestamp: bool = True
    status_colors: bool = True

    def to_dict(self) -> Dict:
        return {
            "format": self.format.value,
            "destination": self.destination.value,
            "base_path": self.base_path,
            "auto_open_browser": self.auto_open_browser,
            "include_timestamp": self.include_timestamp,
            "status_colors": self.status_colors,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "OutputConfig":
        return cls(
            format=OutputFormat(data.get("format", "html")),
            destination=OutputDestination(data.get("destination", "all")),
            base_path=data.get("base_path", "C:/Users/clint/Desktop/HORUS"),
            auto_open_browser=data.get("auto_open_browser", True),
            include_timestamp=data.get("include_timestamp", True),
            status_colors=data.get("status_colors", True),
        )


@dataclass
class ResultEntry:
    """Single result entry."""

    module: str
    group: MLGroup
    status: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HORUSOutput:
    """Complete HORUS output for a grouping."""

    group: MLGroup
    generated: datetime
    entries: List[ResultEntry]
    summary: Dict[str, Any] = field(default_factory=dict)
    config: Optional[OutputConfig] = None

    def to_dict(self) -> Dict:
        return {
            "group": self.group.value,
            "generated": self.generated.isoformat(),
            "entries": [
                {
                    "module": e.module,
                    "group": e.group.value,
                    "status": e.status,
                    "message": e.message,
                    "timestamp": e.timestamp.isoformat(),
                    "metrics": e.metrics,
                }
                for e in self.entries
            ],
            "summary": self.summary,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class HORUSVisualizer:
    """Visual output generator for ML results."""

    DEFAULT_CONFIG = OutputConfig()

    def __init__(self, config: Optional[OutputConfig] = None):
        self.config = config or self.DEFAULT_CONFIG
        self.base_path = Path(self.config.base_path)
        self.results_path = self.base_path / "results"
        self.output_path = self.base_path / "output"
        self.cache_path = self.base_path / "cache"

    def generate_html(self, output: HORUSOutput) -> str:
        """Generate human-readable HTML result."""
        status_colors = {
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "info": "#3498db",
        }

        entries_by_group: Dict[MLGroup, List[ResultEntry]] = {}
        for entry in output.entries:
            if entry.group not in entries_by_group:
                entries_by_group[entry.group] = []
            entries_by_group[entry.group].append(entry)

        groups_html = []
        for group, entries in entries_by_group.items():
            group_entries = []
            for entry in entries:
                color = status_colors.get(entry.status.lower(), "#95a5a6")
                group_entries.append(f"""
                <div class="entry" style="border-left: 4px solid {color};">
                    <div class="entry-header">
                        <span class="module">{entry.module}</span>
                        <span class="status" style="background: {color};">{entry.status}</span>
                    </div>
                    <div class="message">{entry.message}</div>
                    <div class="timestamp">{entry.timestamp.strftime("%H:%M:%S")}</div>
                </div>
                """)
            groups_html.append(f"""
            <div class="group-section">
                <h2 class="group-title">{group.value}</h2>
                <div class="entries">
                    {"".join(group_entries)}
                </div>
            </div>
            """)

        summary_html = ""
        for key, value in output.summary.items():
            summary_html += f"<div class='metric'><span class='label'>{key}</span><span class='value'>{value}</span></div>"

        timestamp = (
            output.generated.strftime("%Y-%m-%d %H:%M:%S")
            if self.config.include_timestamp
            else ""
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HORUS - {output.group.value} Results</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        .header {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .header h1 {{
            font-size: 2em;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .metric {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        .metric .label {{
            display: block;
            color: rgba(255,255,255,0.7);
            font-size: 0.85em;
            margin-bottom: 8px;
        }}
        .metric .value {{
            font-size: 1.8em;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .group-section {{
            margin-bottom: 30px;
            background: rgba(255,255,255,0.03);
            padding: 20px;
            border-radius: 16px;
        }}
        .group-title {{
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }}
        .entries {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .entry {{
            background: rgba(255,255,255,0.05);
            padding: 14px 18px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        .entry:hover {{
            background: rgba(255,255,255,0.1);
            transform: translateX(5px);
        }}
        .entry-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}
        .module {{
            font-weight: 600;
            font-size: 1.05em;
        }}
        .status {{
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.7em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .message {{
            color: rgba(255,255,255,0.75);
            font-size: 0.9em;
            margin-bottom: 6px;
        }}
        .timestamp {{
            font-size: 0.75em;
            color: rgba(255,255,255,0.4);
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.5);
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>HORUS</h1>
        <div style="text-align: right; color: rgba(255,255,255,0.7);">
            <div>ML Platform Analysis</div>
            <div style="font-size: 0.85em;">{timestamp}</div>
        </div>
    </div>
    <div class="container">
        <div class="summary">
            {summary_html}
        </div>
        {"".join(groups_html)}
    </div>
    <div class="footer">
        Generated by HORUS | Human-Readable ML Results
    </div>
</body>
</html>"""

    def save_html(self, output: HORUSOutput) -> Path:
        """Save HTML result to file."""
        self.results_path.mkdir(parents=True, exist_ok=True)
        filename = f"{output.group.value.lower().replace(' ', '_')}_{output.generated.strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.results_path / filename
        html = self.generate_html(output)
        filepath.write_text(html, encoding="utf-8")
        return filepath

    def save_json(self, output: HORUSOutput) -> Path:
        """Save JSON result to file."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        filename = f"{output.group.value.lower().replace(' ', '_')}_{output.generated.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_path / filename
        filepath.write_text(output.to_json(), encoding="utf-8")
        return filepath

    def get_latest_results(self, limit: int = 10) -> List[Path]:
        """Get latest result files."""
        if not self.results_path.exists():
            return []
        return sorted(self.results_path.glob("*.html"), reverse=True)[:limit]


def show_console(output: HORUSOutput):
    """Display results in console."""
    print(f"\n{'=' * 60}")
    print(f"  HORUS - ML Analysis Results")
    print(f"{'=' * 60}")
    print(f"Generated: {output.generated.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Modules: {output.summary.get('Total Modules', len(output.entries))}")
    print(f"{'-' * 60}")
    for group, entries in _group_entries(output).items():
        print(f"\n[{group.value}]")
        for entry in entries:
            status_icon = "âœ“" if entry.status == "success" else "!"
            print(f"  {status_icon} {entry.module}: {entry.message[:50]}")
    print(f"\n{'=' * 60}\n")


def _group_entries(output: HORUSOutput) -> Dict[MLGroup, List[ResultEntry]]:
    """Group entries by MLGroup."""
    grouped: Dict[MLGroup, List[ResultEntry]] = {}
    for entry in output.entries:
        if entry.group not in grouped:
            grouped[entry.group] = []
        grouped[entry.group].append(entry)
    return grouped


def show_popup(title: str, message: str, result_file: Optional[Path] = None):
    """Show popup notification."""
    print(f"\n{'=' * 60}")
    print(f"  HORUS NOTIFICATION")
    print(f"{'=' * 60}")
    print(f"  {title}")
    print(f"  {message}")
    if result_file:
        print(f"  Results: {result_file}")
    print(f"{'=' * 60}\n")

    if result_file and result_file.exists() and webbrowser:
        threading.Timer(1.0, lambda: webbrowser.open(f"file://{result_file}")).start()


class HORUSPopupWindow:
    """Real-time popup window for HORUS operations."""

    def __init__(self, title: str = "HORUS Output Monitor"):
        self.title = title
        self.root = None
        self.text_area = None
        self.progress_bar = None
        self.status_label = None
        self.running = False

    def create_window(self, width: int = 800, height: int = 600):
        """Create popup monitoring window."""
        import tkinter as tk
        from tkinter import ttk, scrolledtext

        self.root = tk.Tk()
        self.root.title(f"HORUS - {self.title}")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg="#1a1a2e")

        header_frame = tk.Frame(self.root, bg="#16213e", pady=10)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="HORUS",
            font=("Consolas", 24, "bold"),
            bg="#16213e",
            fg="#00d4ff",
        )
        title_label.pack()

        self.status_label = tk.Label(
            header_frame,
            text="Initializing...",
            font=("Consolas", 12),
            bg="#16213e",
            fg="#7c3aed",
        )
        self.status_label.pack()

        self.progress_bar = ttk.Progressbar(
            self.root,
            mode="determinate",
            length=width - 50,
            style="TProgressbar",
        )
        self.progress_bar.pack(pady=10, padx=25)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TProgressbar",
            troughcolor="#1a1a2e",
            background="linear-gradient(90deg, #00d4ff, #7c3aed)",
            thickness=20,
        )

        text_frame = tk.Frame(self.root, bg="#1a1a2e", padx=10, pady=10)
        text_frame.pack(fill="both", expand=True)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#0f0f1a",
            fg="#00ff88",
            insertbackground="#00ff88",
        )
        self.text_area.pack(fill="both", expand=True)

        footer_frame = tk.Frame(self.root, bg="#16213e", pady=5)
        footer_frame.pack(fill="x")

        self.time_label = tk.Label(
            footer_frame,
            text="Ready",
            font=("Consolas", 12),
            bg="#16213e",
            fg="#ffffff",
        )
        self.time_label.pack()

        self.running = True

    def log(self, message: str, level: str = "INFO"):
        """Log message to popup."""
        if self.text_area:
            timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
            formatted = f"[{timestamp}] [{level}] {message}"
            self.text_area.insert("end", formatted + "\n")
            self.text_area.see("end")

    def update_status(self, status: str, progress: int = 0):
        """Update status label and progress bar."""
        if self.status_label:
            self.status_label.config(text=status)
        if self.progress_bar:
            self.progress_bar["value"] = progress

    def close(self):
        """Close popup window."""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()

    def run_loop(self):
        """Run tkinter main loop."""
        if self.root:
            self.root.mainloop()


def run_with_popup(
    title: str = "ML Analysis - Live",
    width: int = 900,
    height: int = 700,
) -> HORUSPopupWindow:
    """Run HORUS with real-time popup window."""
    popup = HORUSPopupWindow(title)
    popup.create_window(width, height)
    popup.log("HORUS Popup Mode Activated")
    popup.log("Starting ML Analysis...")
    return popup


def update_popup_live(
    popup: HORUSPopupWindow,
    message: str,
    progress: int,
    status: str = "Processing",
):
    """Update popup with live data."""
    popup.log(message)
    popup.update_status(status, progress)


def run_ml_analysis(cluster: Any = None) -> HORUSOutput:
    """Run ML groupings analysis and return results.

    Args:
        cluster: Optional HYDRA cluster for adaptive analysis
    """
    from ml_platforms.config import discover_modules

    modules = discover_modules()

    entries = []
    for path, info in modules.items():
        group = MLGroup.CORE
        path_lower = path.lower()
        if "qlearning" in path_lower or "verify_moe" in path_lower:
            group = MLGroup.QLEARNING
        elif (
            "integration" in path_lower
            or "onnx" in path_lower
            or "ray" in path_lower
            or "mlflow" in path_lower
        ):
            group = MLGroup.INTEGRATION
        elif "monitoring" in path_lower or "health" in path_lower:
            group = MLGroup.MONITORING
        elif "lm_studio" in path_lower or "lmstudio" in path_lower:
            group = MLGroup.LM_STUDIO
        elif "analysis" in path_lower:
            group = MLGroup.ANALYSIS
        elif "conversion" in path_lower or "converter" in path_lower:
            group = MLGroup.CONVERSION
        elif "install" in path_lower:
            group = MLGroup.INSTALLATION
        elif "autoload" in path_lower or "permanent" in path_lower:
            group = MLGroup.AUTOLOAD
        elif "improvements" in path_lower:
            group = MLGroup.IMPROVEMENTS

        status = "success" if info.get("docstring") else "warning"
        entries.append(
            ResultEntry(
                module=info["name"],
                group=group,
                status=status,
                message=(info.get("docstring") or "No description")[:100],
                metrics={
                    "functions": len(info.get("functions", [])),
                    "classes": len(info.get("classes", [])),
                },
            )
        )

    summary = {
        "Total Modules": len(modules),
        "Core": len([e for e in entries if e.group == MLGroup.CORE]),
        "Q-Learning": len([e for e in entries if e.group == MLGroup.QLEARNING]),
        "Integration": len([e for e in entries if e.group == MLGroup.INTEGRATION]),
        "Monitoring": len([e for e in entries if e.group == MLGroup.MONITORING]),
        "LM Studio": len([e for e in entries if e.group == MLGroup.LM_STUDIO]),
        "Analysis": len([e for e in entries if e.group == MLGroup.ANALYSIS]),
        "Conversion": len([e for e in entries if e.group == MLGroup.CONVERSION]),
    }

    output = HORUSOutput(
        group=MLGroup.IMPROVEMENTS,
        generated=datetime.now(),
        entries=entries,
        summary=summary,
    )

    return output


def config_output(
    format: Literal["html", "json", "console"] = "html",
    destination: Literal["popup", "file", "browser", "all"] = "all",
    base_path: str = "C:/Users/clint/Desktop/HORUS",
    auto_open_browser: bool = True,
) -> OutputConfig:
    """Configure HORUS output parameters.

    Args:
        format: Output format (html, json, console)
        destination: Output destination (popup, file, browser, all)
        base_path: Base path for output files
        auto_open_browser: Whether to auto-open browser for HTML output

    Returns:
        OutputConfig object
    """
    config = OutputConfig(
        format=OutputFormat(format),
        destination=OutputDestination(destination),
        base_path=base_path,
        auto_open_browser=auto_open_browser,
    )
    print(f"HORUS configured: format={format}, destination={destination}")
    print(f"Output path: {base_path}")
    return config


def display_results(
    config: Optional[OutputConfig] = None,
    output: Optional[HORUSOutput] = None,
) -> Optional[Path]:
    """Display ML analysis results.

    Args:
        config: Output configuration
        output: Pre-computed output (auto-generates if None)

    Returns:
        Path to saved result file
    """
    if output is None:
        output = run_ml_analysis()

    visualizer = HORUSVisualizer(config)

    if config is None:
        config = OutputConfig()

    dest = config.destination

    result_file = None
    if dest in [
        OutputDestination.ALL,
        OutputDestination.FILE,
        OutputDestination.BROWSER,
    ]:
        result_file = visualizer.save_html(output)

    if dest in [OutputDestination.ALL, OutputDestination.FILE]:
        visualizer.save_json(output)

    if dest in [OutputDestination.ALL, OutputDestination.POPUP]:
        show_popup(
            title="ML Analysis Complete",
            message=f"Analyzed {len(output.entries)} modules across {len(set(e.group for e in output.entries))} groupings",
            result_file=result_file,
        )

    if (
        dest in [OutputDestination.ALL, OutputDestination.BROWSER]
        and config.auto_open_browser
        and result_file
    ):
        webbrowser.open(f"file://{result_file}")

    if config.format == OutputFormat.CONSOLE:
        show_console(output)

    return result_file


def watch_for_updates(interval: int = 30):
    """Watch for new results and notify."""
    print("HORUS Watch Mode - Press Ctrl+C to stop")
    print("=" * 50)

    visualizer = HORUSVisualizer()
    last_results = set()

    while True:
        try:
            current = set(visualizer.get_latest_results(limit=1))
            new_results = current - last_results

            if new_results:
                for result in new_results:
                    print(f"\n[NEW] {result.name}")
                    show_popup(
                        title="New Results Available", message=f"Results: {result.name}"
                    )

            last_results = current
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nHORUS Watch stopped.")
            break


def launcher():
    """Launch HORUS with command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="HORUS - ML Results Viewer")
    parser.add_argument("--watch", action="store_true", help="Watch for new results")
    parser.add_argument(
        "--monitor", action="store_true", help="Launch live monitoring popup"
    )
    parser.add_argument(
        "--format",
        choices=["html", "json", "console"],
        default="html",
        help="Output format",
    )
    parser.add_argument(
        "--destination",
        choices=["popup", "file", "browser", "all"],
        default="all",
        help="Output destination",
    )
    parser.add_argument(
        "--path", default="C:/Users/clint/Desktop/HORUS", help="Base output path"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't auto-open browser"
    )

    args = parser.parse_args()

    if args.monitor:
        launch_live_monitor()
        return

    config = config_output(
        format=args.format,
        destination=args.destination,
        base_path=args.path,
        auto_open_browser=not args.no_browser,
    )

    if args.watch:
        watch_for_updates()
    else:
        result = display_results(config=config)
        print(f"Results saved to: {result}")


def export_ecosystem_info(filepath: Optional[str] = None) -> str:
    """Export machine-readable ecosystem information."""
    if filepath is None:
        filepath = "C:/Users/clint/Desktop/HORUS/output/ecosystem_info.json"

    ecosystem_data = {
        "ecosystem": {
            "name": "Azazael",
            "version": "5.0.0",
            "architecture": "7-tier worm system",
            "created": "2026-02-11",
            "platform": "Windows",
            "root_path": "C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION",
        },
        "components": {
            "WORMZ": {"type": "worm", "count": 10, "health": "healthy"},
            "METAWORMS": {"type": "metaworm", "count": 8, "health": "healthy"},
            "HYDRA": {"type": "cluster", "count": 8, "health": "healthy"},
            "TERENCE": {"type": "resolver", "patterns": 26, "health": "healthy"},
            "HORUS": {"type": "formatter", "count": 4, "health": "healthy"},
            "POINDEXTER": {"type": "indexer", "count": 2, "health": "healthy"},
            "TARBABY": {"type": "builder", "count": 3, "health": "warning"},
            "PERSEPHONE": {"type": "cross-platform", "count": 4, "health": "healthy"},
            "BIBL": {"type": "crawler", "count": 2, "health": "healthy"},
            "KLINK": {"type": "cli", "count": 9, "health": "healthy"},
            "Azazael_CORE": {"type": "core", "count": 13, "health": "healthy"},
        },
        "statistics": {
            "total_components": 11,
            "total_files": 65,
            "overall_health_score": 85,
            "last_scan": "2026-02-11T05:15:15.742764",
        },
    }

    Path(filepath).write_text(json.dumps(ecosystem_data, indent=2, ensure_ascii=False))
    print(f"Ecosystem info exported to: {filepath}")
    return filepath


def get_ecosystem_json() -> str:
    """Get ecosystem info as JSON string."""
    export_ecosystem_info()
    return json.dumps(
        {"status": "healthy", "components": 11, "health_score": 85}, indent=2
    )


# ============================================================================
# LIVE MONITOR EMBEDDED - Real-Time Ecosystem Monitoring
# ============================================================================

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    from datetime import datetime
    from pathlib import Path
    from typing import Dict, List, Optional
    from dataclasses import dataclass
    from enum import Enum
    import subprocess
    import sys

    _TKINTER_AVAILABLE = True
except ImportError:
    _TKINTER_AVAILABLE = False


class MonitorComponentStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class MonitoredComponent:
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    status: str = "idle"
    last_output: str = ""
    last_update: Optional[datetime] = None
    color: str = "#00ff88"


class HORUSLiveMonitor:
    """Integrated Live Monitor for HORUS output management."""

    def __init__(self, title: str = "HORUS LIVE MONITOR"):
        if not _TKINTER_AVAILABLE:
            raise ImportError("tkinter not available")

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1400x900")
        self.root.configure(bg="#0d0d1a")

        self.components: Dict[str, MonitoredComponent] = {}
        self.running = False
        self.base_path = Path("C:/Users/clint/Desktop")

        self.setup_ui()
        self.setup_components()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0d0d1a", pady=15, padx=20)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="HORUS LIVE MONITOR",
            font=("Consolas", 18, "bold"),
            bg="#0d0d1a",
            fg="#00d4ff",
        ).pack(side=tk.LEFT)

        self.time_label = tk.Label(
            header, text="", font=("Consolas", 12), bg="#0d0d1a", fg="#666"
        )
        self.time_label.pack(side=tk.RIGHT)

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Console tab
        self.console_frame = tk.Frame(self.root, bg="#0d0d1a")
        self.notebook.add(self.console_frame, text=" Console Output ")

        self.console = scrolledtext.ScrolledText(
            self.console_frame,
            font=("Consolas", 10),
            bg="#000000",
            fg="#00ff88",
            wrap=tk.WORD,
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Components grid tab
        self.grid_frame = tk.Frame(self.root, bg="#0d0d1a")
        self.notebook.add(self.grid_frame, text=" Components Status ")

        self.components_container = tk.Frame(self.grid_frame, bg="#0d0d1a")
        self.components_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Actions bar
        actions = tk.Frame(self.root, bg="#16213e", pady=12, padx=15)
        actions.pack(fill=tk.X)

        tk.Button(
            actions,
            text=" Refresh All",
            font=("Consolas", 10, "bold"),
            bg="#1a3a1a",
            fg="#00ff88",
            command=self.refresh_all,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions,
            text=" Run All",
            font=("Consolas", 10, "bold"),
            bg="#1a2a3a",
            fg="#00d4ff",
            command=self.run_all,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions,
            text=" Clear",
            font=("Consolas", 10),
            bg="#3a1a1a",
            fg="#ff6b6b",
            command=self.clear_console,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions,
            text=" Export JSON",
            font=("Consolas", 10),
            bg="#2a1a3a",
            fg="#a855f7",
            command=self.export_status,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            actions,
            text=" Quit",
            font=("Consolas", 10),
            bg="#3a1a1a",
            fg="#ff6b6b",
            command=self.quit,
            relief=tk.FLAT,
        ).pack(side=tk.RIGHT, padx=5)

    def setup_components(self):
        azazael_path = self.base_path / "Azazael"

        self.components = {
            "SYSTEMZ": MonitoredComponent(
                "SYSTEMZ", "python", ["WORMZ/SYSTEMZ.py", "--status"], color="#00d4ff"
            ),
            "PROCESSZ": MonitoredComponent(
                "PROCESSZ", "python", ["WORMZ/PROCESSZ.py", "--status"], color="#00d4ff"
            ),
            "DISKZ": MonitoredComponent(
                "DISKZ", "python", ["WORMZ/DISKZ.py", "--status"], color="#00d4ff"
            ),
            "NETWORXZ": MonitoredComponent(
                "NETWORXZ", "python", ["WORMZ/NETWORXZ.py", "--status"], color="#00d4ff"
            ),
            "CLOCKZ": MonitoredComponent(
                "CLOCKZ", "python", ["WORMZ/CLOCKZ.py", "--status"], color="#00d4ff"
            ),
            "CONCURRENCY": MonitoredComponent(
                "CONCURRENCY",
                "python",
                ["WORMZ/CONCURRENCY.py", "--scan"],
                color="#7c3aed",
            ),
            "HYDRA": MonitoredComponent(
                "HYDRA", "python", ["HYDRA/HYDRA.py", "--all"], color="#10b981"
            ),
            "TERENCE": MonitoredComponent(
                "TERENCE", "python", ["TERENCE/TERENCE.py", "--scan"], color="#f59e0b"
            ),
            "ERRORZ": MonitoredComponent(
                "ERRORZ", "python", ["METAWORMS/ERRORZ.py", "--all"], color="#ef4444"
            ),
            "HYDRAMETA": MonitoredComponent(
                "HYDRAMETA",
                "python",
                ["METAWORMS/HYDRAMETA.py", "--all"],
                color="#10b981",
            ),
            "OPTIMIZER": MonitoredComponent(
                "OPTIMIZER", "python", ["ECOSYSTEM_OPTIMIZER.py", "-o"], color="#10b981"
            ),
            "CRAWLER": MonitoredComponent(
                "CRAWLER", "python", ["ECOSYSTEM_CRAWLER_LAUNCHER.py"], color="#00d4ff"
            ),
        }

        for comp in self.components.values():
            comp.last_update = datetime.now()

        self.render_grid()

    def render_grid(self):
        for widget in self.components_container.winfo_children():
            widget.destroy()

        colors = {
            MonitorComponentStatus.ACTIVE: "#10b981",
            MonitorComponentStatus.IDLE: "#6b7280",
            MonitorComponentStatus.RUNNING: "#f59e0b",
            MonitorComponentStatus.ERROR: "#ef4444",
        }

        row = col = 0
        cols = 4

        for name, comp in self.components.items():
            frame = tk.Frame(
                self.components_container,
                bg="#1a1a2e",
                highlightbackground="#333",
                highlightthickness=1,
                padx=15,
                pady=12,
            )
            frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Status dot
            tk.Canvas(
                frame, width=10, height=10, bg=colors[comp.status], highlightthickness=0
            ).pack(anchor="w", mb=5)

            tk.Label(
                frame,
                text=name,
                font=("Consolas", 11, "bold"),
                bg="#1a1a2e",
                fg=comp.color,
            ).pack(anchor="w")

            tk.Label(
                frame,
                text=comp.status.value.upper(),
                font=("Consolas", 9),
                bg="#1a1a2e",
                fg=colors[comp.status],
            ).pack(anchor="w")

            col += 1
            if col >= cols:
                col = 0
                row += 1

        for i in range(cols):
            self.components_container.grid_columnconfigure(i, weight=1)

    def log(self, msg: str, component: str = "SYSTEM", color: str = "#00ff88"):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.console.insert(tk.END, f"[{ts}] [{component}] {msg}\n", component)
        self.console.tag_config(component, foreground=color)
        self.console.see(tk.END)

    def clear_console(self):
        self.console.delete(1.0, tk.END)
        self.log("Console cleared", "SYSTEM", "#888")

    def run_component(self, name: str):
        if name not in self.components:
            return

        comp = self.components[name]
        comp.status = MonitorComponentStatus.RUNNING
        self.render_grid()
        self.log(f"Starting {name}...", name, comp.color)

        try:
            cmd = [
                sys.executable,
                str(self.base_path / "Azazael" / comp.command),
            ] + comp.args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
        except Exception as e:
            output = f"Error: {e}"
            comp.status = MonitorComponentStatus.ERROR

        if output:
            self.log(output[:300], name, comp.color)
            comp.last_output = output[:500]

        comp.last_update = datetime.now()
        comp.status = (
            MonitorComponentStatus.ACTIVE
            if "error" not in output.lower()
            else MonitorComponentStatus.ERROR
        )
        self.render_grid()
        self.log(f"{name} complete", name, comp.color)

    def refresh_all(self):
        self.log("Refreshing all components...", "SYSTEM", "#00d4ff")
        for name in self.components:
            self.run_component(name)
        self.log("Refresh complete", "SYSTEM", "#10b981")

    def run_all(self):
        self.log("=" * 50, "SYSTEM", "#888")
        self.log("RUNNING FULL ECOSYSTEM", "SYSTEM", "#00d4ff")
        self.log("=" * 50, "SYSTEM", "#888")

        for name in self.components:
            self.run_component(name)

        self.log("=" * 50, "SYSTEM", "#888")
        self.log("ECOSYSTEM RUN COMPLETE", "SYSTEM", "#10b981")
        self.log("=" * 50, "SYSTEM", "#888")

    def export_status(self):
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                name: {
                    "status": comp.status.value,
                    "last_update": comp.last_update.isoformat()
                    if comp.last_update
                    else None,
                }
                for name, comp in self.components.items()
            },
        }
        export_path = self.base_path / "HORUS" / "output" / "monitor_status.json"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(status_data, indent=2))
        self.log(f"Status exported to {export_path}", "EXPORT", "#a855f7")

    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        if self.running:
            self.root.after(1000, self.update_time)

    def start(self):
        self.running = True
        self.log("HORUS LIVE MONITOR STARTED", "SYSTEM", "#00d4ff")
        self.update_time()
        self.root.mainloop()

    def quit(self):
        self.running = False
        self.root.quit()


def launch_live_monitor():
    """Launch the HORUS integrated live monitor."""
    if not _TKINTER_AVAILABLE:
        print("tkinter not available. Install tkinter to use live monitor.")
        return None
    return HORUSLiveMonitor()


if __name__ == "__main__":
    launcher()



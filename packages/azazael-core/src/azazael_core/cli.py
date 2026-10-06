#!/usr/bin/env python3
# coding: utf-8
"""
AZAZAEL Core CLI — Standalone command-line entry point for Nuitka .exe build.

Provides:
  paths    → Show project paths and desktop resolution
  registry → List worm registry contents (categories, counts)
  config   → Show current configuration
  version  → Print azazael-core version
  help     → Print this help
"""

import sys
from pathlib import Path


def cmd_paths():
    """Show dynamic paths."""
    from azazael_core import (
        get_project_root, get_desktop_dir, get_g_drive,
        get_src_dir, get_output_dir, get_core_dir, get_worms_dir,
        PATHS_VERSION,
    )

    print("=" * 60)
    print(f"  AZAZAEL Core — Dynamic Paths (v{PATHS_VERSION})")
    print("=" * 60)
    print(f"  Project Root  : {get_project_root()}")
    print(f"  Src Dir       : {get_src_dir()}")
    print(f"  Output Dir    : {get_output_dir()}")
    print(f"  Desktop Dir   : {get_desktop_dir()}")
    print(f"  G: Drive      : {get_g_drive()}")
    print(f"  CORE Dir      : {get_core_dir()}")
    print(f"  WORMS Dir     : {get_worms_dir()}")
    print("=" * 60)


def cmd_registry():
    """Show worm registry summary."""
    import sys
    from azazael_core import discover_worms, get_all_categories, get_worms_by_category

    def _progress(p, t, n):
        print(f"  \r[discover] {p}/{t} - {n}", file=sys.stderr, end="", flush=True)
    discover_worms(progress_callback=_progress)
    print(file=sys.stderr)  # close progress line
    cats = get_all_categories()
    print("=" * 60)
    print("  AZAZAEL Core — Worm Registry")
    print("=" * 60)
    total = 0
    for cat in sorted(cats):
        worms = get_worms_by_category(cat)
        total += len(worms)
        print(f"  [{cat}] ({len(worms)} worms)")
        for w in sorted(worms)[:5]:
            print(f"    - {w}")
        if len(worms) > 5:
            print(f"    ... and {len(worms) - 5} more")
    print(f"  Total: {total} worms across {len(cats)} categories")
    if total == 0:
        print()
        print("  Note: Standalone package does not include WORMS modules.")
        print("  Install the full AZAZAEL project for worm discovery.")
    print("=" * 60)


def cmd_config():
    """Show configuration."""
    from azazael_core import Config

    print("=" * 60)
    print("  AZAZAEL Core — Configuration (Config class)")
    print("=" * 60)
    print(f"  AZAZAEL_ROOT        : {Config.AZAZAEL_ROOT}")
    print(f"  SRC_DIR             : {Config.SRC_DIR}")
    print(f"  CLUSTER_TIMEOUT     : {Config.CLUSTER_TIMEOUT}")
    print(f"  CLUSTER_RETRY_COUNT : {Config.CLUSTER_RETRY_COUNT}")
    print(f"  CLUSTER_PARALLELISM : {Config.CLUSTER_PARALLELISM}")
    print(f"  CIRCUIT_THRESHOLD   : {Config.CIRCUIT_FAILURE_THRESHOLD}")
    print(f"  CIRCUIT_RESET       : {Config.CIRCUIT_RESET_TIMEOUT}")
    print("=" * 60)


def _safe_str(text: str) -> str:
    """Strip characters unsupported by the Windows cp1252 terminal encoding."""
    return text.encode('cp1252', 'replace').decode('cp1252')


def cmd_clusters():
    """Show cluster types, Nature categories, or execute a cluster."""

    # Check for subcommand: azazael-core clusters <subcommand> [args]
    if len(sys.argv) > 2:
        subcmd = sys.argv[2].lower()
        if subcmd == "execute":
            cluster_type = sys.argv[3].lower() if len(sys.argv) > 3 else None
            if not cluster_type:
                print("Usage: azazael-core clusters execute <cluster_type>")
                print()
                print("Available cluster types:")
                from azazael_core.worms.clusters import CLUSTER_REGISTRY
                for name in sorted(CLUSTER_REGISTRY.keys()):
                    print(f"  {name}")
                return
            _cmd_clusters_execute(cluster_type)
            return
        else:
            print(f"Unknown subcommand: {sys.argv[2]}", file=sys.stderr)
            print("Usage: azazael-core clusters [execute <type>]", file=sys.stderr)
            sys.exit(1)

    from azazael_core.worms.clusters import (
        CLUSTER_REGISTRY, NATURE_DEFINITIONS,
        _CLUSTERWORMS_OK, _NATURE_OK, _META_OK,
    )

    def p(text: str):
        """Print safely, stripping characters unsupported by the terminal."""
        print(_safe_str(text))

    p("=" * 60)
    p("  AZAZAEL Core — Cluster System")
    p("=" * 60)
    p(f"  CLUSTERWORMS     : {'OK' if _CLUSTERWORMS_OK else 'UNAVAILABLE'}")
    p(f"  NATURE_CLUSTERS  : removed (D1/U3 taxonomy)")
    p(f"  METACLUSTER      : {'OK' if _META_OK else 'UNAVAILABLE'}")
    p("")

    if CLUSTER_REGISTRY:
        p("  Predefined Clusters:")
        for name, info in sorted(CLUSTER_REGISTRY.items()):
            worms = ", ".join(info.get("worms", [])[:5])
            p(f"    {name:<16} {info.get('description', '')}")
            p(f"    {'':16} Worms: {worms}")
        p("")
        p("  Run 'azazael-core clusters execute <type>' to execute a cluster.")
    else:
        p("  No predefined clusters available.")

    p("")
    if NATURE_DEFINITIONS:
        p(f"  Nature Categories ({len(NATURE_DEFINITIONS)}):")
        for nature, defn in sorted(NATURE_DEFINITIONS.items()):
            icon = _safe_str(defn.get("icon", ""))
            purpose = defn.get("purpose", "")
            feeds = ", ".join(defn.get("feeds_into", [])[:3])
            p(f"    {icon} {nature:<18} {purpose[:50]}")
            if feeds:
                p(f"    {'':20} -> feeds: {feeds}")
    p("=" * 60)


def _cmd_clusters_execute(cluster_type: str):
    """Execute a cluster of the given type."""
    from azazael_core.worms.clusters import (
        ClusterWORMZ, CLUSTER_REGISTRY,
        _CLUSTERWORMS_OK,
    )

    # Use _safe_str for all output (Windows cp1252 terminal safety)
    p = lambda text: print(_safe_str(text))

    if not _CLUSTERWORMS_OK:
        p("Error: CLUSTERWORMS module is unavailable.")
        sys.exit(1)

    # Normalize case for lookup
    cluster_type = cluster_type.lower()
    if cluster_type not in CLUSTER_REGISTRY:
        p(f"Unknown cluster type: {cluster_type}")
        p(f"Available: {', '.join(sorted(CLUSTER_REGISTRY.keys()))}")
        sys.exit(1)

    info = CLUSTER_REGISTRY[cluster_type]
    p("=" * 60)
    p(f"  Executing Cluster: {cluster_type}")
    p(f"  Description: {info.get('description', 'N/A')}")
    p(f"  Worms: {', '.join(info.get('worms', []))}")
    p("=" * 60)
    p("")

    try:
        cluster = ClusterWORMZ(cluster_type)
        status = cluster.get_status()

        p(f"Cluster ID: {status.get('cluster_id', 'N/A')}")
        p(f"Version:    {status.get('version', 'N/A')}")
        p(f"Worm Count: {status['worm_count']}")
        p("")

        # Show loaded worms
        loaded = status.get('loaded_worms', [])
        if loaded:
            p(f"Loaded worms ({len(loaded)}):")
            for w in loaded[:10]:
                p(f"  - {w}")
            if len(loaded) > 10:
                p(f"  ... and {len(loaded) - 10} more")
        else:
            p("No worms resolved for this cluster type.")

        p("")
        p("=" * 60)
        p(f"  Cluster '{cluster_type}' execution complete.")
        p("=" * 60)

    except Exception as e:
        p(f"Error executing cluster: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_version():
    """Print version."""
    print("azazael-core v3.1.0")
    print(f"Python {sys.version}")
    from azazael_core import is_free_threaded, get_thread_info
    info = get_thread_info()
    print(f"Free-threading: {'enabled' if is_free_threaded() else 'disabled'}")
    print(f"CPU count: {info.get('cpu_count', 'N/A')}")
    print(f"Python executable: {info.get('python_executable', 'N/A')}")


COMMANDS = {
    "paths": cmd_paths,
    "registry": cmd_registry,
    "clusters": cmd_clusters,
    "config": cmd_config,
    "version": cmd_version,
}


def print_help():
    print("azazael-core v3.1.0 — AZAZAEL Core CLI")
    print()
    print("Usage: azazael-core <command>")
    print()
    print("Commands:")
    for name, func in sorted(COMMANDS.items()):
        doc = (func.__doc__ or "").strip().split("\n")[0]
        print(f"  {name:<12} {doc}")
    print()
    print("Subcommands:")
    print("  clusters execute <type>   Execute a cluster (system, network, security, ...)")
    print()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print_help()
        return

    cmd = sys.argv[1].lower()
    if cmd in COMMANDS:
        try:
            COMMANDS[cmd]()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

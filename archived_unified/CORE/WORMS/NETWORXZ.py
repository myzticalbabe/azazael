# coding: utf-8
"""
NETWORXZ - Network Management Worm

Network monitoring and management for Azazael ecosystem.

Features:
- Network interface listing
- Connection monitoring
- Bandwidth statistics
- Ping monitoring
- Port checking
- DNS resolution

Usage:
    >>> import networxz
    >>> networxz.get_interfaces()     # List interfaces
    >>> networxz.get_connections()     # List connections
    >>> networxz.get_stats()          # Get bandwidth stats
    >>> networxz.ping("google.com")   # Ping host
"""

import os
import sys
import time
import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import psutil


@dataclass
class NetworkInterface:
    """Network interface information."""

    name: str
    address: str
    netmask: str
    broadcast: str
    is_up: bool
    speed: Optional[int]


class NETWORXZ:
    """Network Management Worm."""

    VERSION = "1.0.0"

    def __init__(self):
        pass

    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interfaces."""
        interfaces = []
        for name, addrs in psutil.net_if_addrs().items():
            info = {
                "name": name,
                "addresses": [],
                "is_up": name in psutil.net_if_stats(),
            }
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    info["addresses"].append(
                        {
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        }
                    )
            if info["addresses"]:
                interfaces.append(info)
        return interfaces

    def get_connections(self, kind: str = "all") -> List[Dict[str, Any]]:
        """Get network connections."""
        conns = []
        for conn in psutil.net_connections(kind=kind):
            conns.append(
                {
                    "fd": conn.fd,
                    "family": conn.family.name
                    if hasattr(conn.family, "name")
                    else str(conn.family),
                    "type": conn.type.name
                    if hasattr(conn.type, "name")
                    else str(conn.type),
                    "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}"
                    if conn.laddr
                    else "",
                    "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}"
                    if conn.raddr
                    else "",
                    "status": conn.status,
                    "pid": conn.pid,
                }
            )
        return conns

    def get_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        counters = psutil.net_io_counters()
        return {
            "bytes_sent_mb": round(counters.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(counters.bytes_recv / (1024**2), 2),
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
            "errin": counters.errin,
            "errout": counters.errout,
            "dropin": counters.dropin,
            "dropout": counters.dropout,
        }

    def ping(self, host: str, count: int = 1, timeout: int = 2) -> Dict[str, Any]:
        """Ping a host."""
        import subprocess

        try:
            result = subprocess.run(
                ["ping", "-n", str(count), "-w", str(timeout * 1000), host],
                capture_output=True,
                text=True,
                timeout=timeout * count + 5,
            )
            return {
                "host": host,
                "success": result.returncode == 0,
                "output": result.stdout[:500],
                "error": result.stderr[:500] if result.stderr else None,
            }
        except Exception as e:
            return {"host": host, "success": False, "error": str(e)}

    def check_port(self, host: str, port: int, timeout: int = 2) -> Dict[str, Any]:
        """Check if port is open."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return {"host": host, "port": port, "open": result == 0}
        except Exception as e:
            return {"host": host, "port": port, "open": False, "error": str(e)}
        finally:
            sock.close()

    def resolve(self, hostname: str) -> Dict[str, Any]:
        """Resolve hostname to IP."""
        try:
            ip = socket.gethostbyname(hostname)
            return {"hostname": hostname, "ip": ip, "success": True}
        except socket.gaierror as e:
            return {"hostname": hostname, "success": False, "error": str(e)}

    def get_summary(self) -> Dict[str, Any]:
        """Get network summary."""
        return {
            "interfaces": self.get_interfaces(),
            "connections_count": len(self.get_connections()),
            "stats": self.get_stats(),
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="NETWORXZ - Network Management Worm")
    parser.add_argument("--interfaces", action="store_true", help="List interfaces")
    parser.add_argument("--connections", action="store_true", help="List connections")
    parser.add_argument("--stats", action="store_true", help="Get bandwidth stats")
    parser.add_argument("--ping", type=str, help="Ping host")
    parser.add_argument("--port", type=int, help="Check port (requires --host)")
    parser.add_argument("--resolve", type=str, help="Resolve hostname")
    parser.add_argument("--summary", action="store_true", help="Summary")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    nz = NETWORXZ()

    if args.json:
        if args.interfaces:
            print(json.dumps(nz.get_interfaces(), indent=2))
        elif args.connections:
            print(json.dumps(nz.get_connections(), indent=2))
        elif args.stats:
            print(json.dumps(nz.get_stats(), indent=2))
        elif args.ping:
            print(json.dumps(nz.ping(args.ping), indent=2))
        elif args.port and args.host:
            print(json.dumps(nz.check_port(args.host, args.port), indent=2))
        elif args.resolve:
            print(json.dumps(nz.resolve(args.resolve), indent=2))
        elif args.summary:
            print(json.dumps(nz.get_summary(), indent=2))
        else:
            print(json.dumps(nz.get_summary(), indent=2))
    else:
        if args.interfaces:
            for iface in nz.get_interfaces():
                print(
                    f"{iface['name']}: {', '.join(a['address'] for a in iface['addresses'])}"
                )
        elif args.connections:
            for c in nz.get_connections()[:20]:
                print(f"{c['local_addr']} -> {c['remote_addr']} [{c['status']}]")
        elif args.stats:
            s = nz.get_stats()
            print(f"Sent: {s['bytes_sent_mb']}MB | Recv: {s['bytes_recv_mb']}MB")
        elif args.ping:
            r = nz.ping(args.ping)
            print(f"{args.ping}: {'OK' if r['success'] else 'FAILED'}")
        elif args.port and args.host:
            r = nz.check_port(args.host, args.port)
            print(f"{args.host}:{args.port}: {'OPEN' if r['open'] else 'CLOSED'}")
        elif args.resolve:
            r = nz.resolve(args.resolve)
            print(f"{args.resolve}: {r.get('ip', r.get('error', 'UNKNOWN'))}")
        else:
            s = nz.get_stats()
            print(
                f"Connections: {s['connections_count']} | Sent: {s['stats']['bytes_sent_mb']}MB"
            )


if __name__ == "__main__":
    main()

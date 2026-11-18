"""
Workspace Baseline Snapshot & Dynamic MCP Tool Registry
Tracks deliverable provenance and automates Model Context Protocol discovery.
"""
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, List

class WorkspaceSnapshot:
    SNAPSHOT_FILE = Path("/tmp/.ple_baseline_snapshot.json")

    @classmethod
    def take_snapshot(cls, workdir: Path) -> Dict[str, Dict[str, Any]]:
        snapshot = {}
        for p in workdir.rglob('*'):
            if p.is_file() and not p.name.startswith('.'):
                try:
                    stat = p.stat()
                    snapshot[str(p.relative_to(workdir))] = {
                        "size": stat.st_size,
                        "mtime_ns": stat.st_mtime_ns
                    }
                except FileNotFoundError:
                    pass
        cls.SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))
        return snapshot

    @classmethod
    def get_created_deliverables(cls, workdir: Path) -> List[Path]:
        if not cls.SNAPSHOT_FILE.exists():
            return [p for p in workdir.rglob('*') if p.is_file() and not p.name.startswith('.')]
        baseline = json.loads(cls.SNAPSHOT_FILE.read_text())
        new_files = []
        for p in workdir.rglob('*'):
            if p.is_file() and not p.name.startswith('.'):
                rel_path = str(p.relative_to(workdir))
                if rel_path not in baseline:
                    new_files.append(p)
                else:
                    # File was modified/rewritten
                    if p.stat().st_size != baseline[rel_path]["size"] or p.stat().st_mtime_ns != baseline[rel_path]["mtime_ns"]:
                        new_files.append(p)
        return new_files

class DynamicMCPRegistry:
    """Discovers and interrogates containerized MCP servers on http://127.0.0.1:8000/mcp/"""
    def __init__(self, mcp_servers_meta: List[Dict[str, str]]):
        self.servers = mcp_servers_meta
        self.registered_tools: List[Dict[str, Any]] = []

    def probe_and_register(self) -> List[Dict[str, Any]]:
        for server in self.servers:
            url = server.get("url", "")
            try:
                # Issue tools/list RPC
                req = urllib.request.Request(
                    f"{url.rstrip('/')}/tools/list",
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        payload = json.loads(response.read().decode('utf-8'))
                        tools = payload.get("tools", [])
                        self.registered_tools.extend(tools)
            except Exception:
                # Graceful fallback if MCP server is starting or idle
                pass
        return self.registered_tools

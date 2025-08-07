from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from mcp.server import Server
from mcp.server.lowlevel import run
from mcp.types import (
    ListToolsResult,
    Tool,
)


DEFAULT_ALLOWED_DIRS_ENV = "MCP_FS_ALLOWED_DIRS"


@dataclass
class AllowedPath:
    path: Path

    def contains(self, other: Path) -> bool:
        try:
            other_resolved = other.resolve()
        except FileNotFoundError:
            # For operations creating new files, validate the parent directory
            other_resolved = other.parent.resolve()

        try:
            other_resolved.relative_to(self.path)
            return True
        except ValueError:
            return False


def load_allowed_dirs() -> List[AllowedPath]:
    raw = os.getenv(DEFAULT_ALLOWED_DIRS_ENV, "")
    candidates = [s.strip() for s in raw.split(os.pathsep) if s.strip()]
    allowed: List[AllowedPath] = []
    for c in candidates:
        p = Path(c).expanduser().resolve()
        if p.exists() and p.is_dir():
            allowed.append(AllowedPath(p))
    return allowed


def assert_allowed(target: Path, allowed: List[AllowedPath]) -> None:
    if not allowed:
        raise PermissionError(
            "No allowed directories configured. Set MCP_FS_ALLOWED_DIRS to a list of absolute paths separated by os.pathsep (':' on macOS/Linux, ';' on Windows)."
        )
    for ap in allowed:
        if ap.contains(target):
            return
    raise PermissionError(f"Path not allowed: {target}")


server = Server("local-filesystem")


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    tools: List[Tool] = [
        Tool(
            name="fs_list",
            description="List directory contents within allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to list"}
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="fs_read_file",
            description="Read a file within allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute file path"}
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="fs_write_file",
            description="Create or overwrite a file within allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        ),
        Tool(
            name="fs_delete",
            description="Delete a file or directory (recursive for directories) within allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="fs_mkdir",
            description="Create a directory (mkdir -p behavior) within allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="fs_move",
            description="Move or rename files/directories within allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "src": {"type": "string"},
                    "dst": {"type": "string"},
                    "overwrite": {"type": "boolean", "default": False},
                },
                "required": ["src", "dst"],
            },
        ),
    ]
    return ListToolsResult(tools=tools)


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    allowed = load_allowed_dirs()
    try:
        if name == "fs_list":
            path = Path(arguments["path"]).expanduser()
            assert_allowed(path, allowed)
            entries = []
            if not path.exists():
                raise FileNotFoundError(str(path))
            for child in sorted(path.iterdir()):
                stat = child.stat()
                entries.append(
                    {
                        "path": str(child),
                        "name": child.name,
                        "is_dir": child.is_dir(),
                        "size": stat.st_size,
                        "modified": int(stat.st_mtime),
                    }
                )
            return {
                "content": [
                    {
                        "type": "json",
                        "content": entries,
                    }
                ]
            }
        if name == "fs_read_file":
            path = Path(arguments["path"]).expanduser()
            assert_allowed(path, allowed)
            if not path.is_file():
                raise FileNotFoundError(str(path))
            data = path.read_text(encoding="utf-8")
            return {"content": [{"type": "text", "text": data}]}
        if name == "fs_write_file":
            path = Path(arguments["path"]).expanduser()
            assert_allowed(path, allowed)
            path.parent.mkdir(parents=True, exist_ok=True)
            content = arguments.get("content", "")
            path.write_text(content, encoding="utf-8")
            return {"content": [{"type": "json", "content": {"ok": True, "path": str(path)}}]}
        if name == "fs_delete":
            import shutil

            path = Path(arguments["path"]).expanduser()
            assert_allowed(path, allowed)
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            return {"content": [{"type": "json", "content": {"ok": True}}]}
        if name == "fs_mkdir":
            path = Path(arguments["path"]).expanduser()
            assert_allowed(path, allowed)
            path.mkdir(parents=True, exist_ok=True)
            return {"content": [{"type": "json", "content": {"ok": True, "path": str(path)}}]}
        if name == "fs_move":
            import shutil

            src = Path(arguments["src"]).expanduser()
            dst = Path(arguments["dst"]).expanduser()
            overwrite = bool(arguments.get("overwrite", False))
            assert_allowed(src, allowed)
            assert_allowed(dst, allowed)
            if dst.exists():
                if overwrite:
                    if dst.is_dir():
                        import shutil as _shutil

                        _shutil.rmtree(dst)
                    else:
                        dst.unlink()
                else:
                    raise FileExistsError(str(dst))
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return {"content": [{"type": "json", "content": {"ok": True}}]}
    except PermissionError as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"PermissionError: {e}",
                }
            ],
        }
    except FileNotFoundError as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"FileNotFoundError: {e}",
                }
            ],
        }
    except FileExistsError as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"FileExistsError: {e}",
                }
            ],
        }
    except Exception as e:  # noqa: BLE001
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {e}",
                }
            ],
        }


async def _run_async() -> None:
    await run(server)


if __name__ == "__main__":
    asyncio.run(_run_async())


def main() -> None:
    """Console-script entrypoint."""
    asyncio.run(_run_async())



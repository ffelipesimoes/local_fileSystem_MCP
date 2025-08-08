from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP


DEFAULT_ALLOWED_DIRS_ENV = "MCP_FS_ALLOWED_DIRS"


@dataclass
class AllowedPath:
    path: Path

    def contains(self, other: Path) -> bool:
        try:
            other_resolved = other.resolve()
        except FileNotFoundError:
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
            "No allowed directories configured. Set MCP_FS_ALLOWED_DIRS with absolute paths."
        )
    for ap in allowed:
        if ap.contains(target):
            return
    raise PermissionError(f"Path not allowed: {target}")


mcp = FastMCP(name="local-filesystem-mcp")


@mcp.tool()
def fs_list(path: str):
    allowed = load_allowed_dirs()
    target = Path(path).expanduser()
    assert_allowed(target, allowed)
    if not target.exists():
        raise FileNotFoundError(str(target))
    items = []
    for child in sorted(target.iterdir()):
        stat = child.stat()
        items.append(
            {
                "path": str(child),
                "name": child.name,
                "is_dir": child.is_dir(),
                "size": stat.st_size,
                "modified": int(stat.st_mtime),
            }
        )
    return items


@mcp.tool()
def fs_read_file(path: str) -> str:
    allowed = load_allowed_dirs()
    target = Path(path).expanduser()
    assert_allowed(target, allowed)
    if not target.is_file():
        raise FileNotFoundError(str(target))
    return target.read_text(encoding="utf-8")


@mcp.tool()
def fs_write_file(path: str, content: str) -> dict:
    allowed = load_allowed_dirs()
    target = Path(path).expanduser()
    assert_allowed(target, allowed)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"ok": True, "path": str(target)}


@mcp.tool()
def fs_delete(path: str) -> dict:
    import shutil

    allowed = load_allowed_dirs()
    target = Path(path).expanduser()
    assert_allowed(target, allowed)
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()
    return {"ok": True}


@mcp.tool()
def fs_mkdir(path: str) -> dict:
    allowed = load_allowed_dirs()
    target = Path(path).expanduser()
    assert_allowed(target, allowed)
    target.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "path": str(target)}


@mcp.tool()
def fs_move(src: str, dst: str, overwrite: bool = False) -> dict:
    import shutil

    allowed = load_allowed_dirs()
    source = Path(src).expanduser()
    dest = Path(dst).expanduser()
    assert_allowed(source, allowed)
    assert_allowed(dest, allowed)
    if dest.exists():
        if overwrite:
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        else:
            raise FileExistsError(str(dest))
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))
    return {"ok": True}


def main() -> None:
    # HTTP is required for Smithery; default to 0.0.0.0:3000
    port = int(os.getenv("PORT", "3000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()



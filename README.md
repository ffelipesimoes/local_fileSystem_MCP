# Local Filesystem MCP Server

A secure MCP server that exposes CRUD tools for the local filesystem, restricted to a whitelist of allowed directories.

## Features

- Whitelisted access: set `MCP_FS_ALLOWED_DIRS` to absolute directories (separated by `:` on macOS/Linux, `;` on Windows)
- Tools: `fs_list`, `fs_read_file`, `fs_write_file`, `fs_delete`, `fs_mkdir`, `fs_move`

## Quickstart (Local)

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Run the server:

   ```bash
   MCP_FS_ALLOWED_DIRS="$HOME" python -m local_filesystem_mcp.server
   ```

## Smithery Manifest

This repo contains an `mcp.json` manifest for Smithery. You can publish it or use directly:

- Ensure `entrypoint` and `env` are correct in `mcp.json`.
- Smithery will run: `python -m local_filesystem_mcp.server`.

## Client Example

The sample `main.py` demonstrates connecting to a remote MCP server. To test this server locally, you can use the MCP CLI:

```bash
mcp dev -c mcp.json
```

## Environment

- `MCP_FS_ALLOWED_DIRS`: absolute directories that the server can access.

## License

MIT

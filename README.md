# Local Filesystem MCP Server

A secure MCP server that exposes CRUD tools for the local filesystem, restricted to a whitelist of allowed directories.

## Features

- Whitelisted access: set `MCP_FS_ALLOWED_DIRS` to absolute directories (separated by `:` on macOS/Linux, `;` on Windows)
- Tools: `fs_list`, `fs_read_file`, `fs_write_file`, `fs_delete`, `fs_mkdir`, `fs_move`

## Como baixar e usar

Requisitos:

- Python 3.13+
- macOS, Linux ou Windows
- Opcional: `uv` (recomendado) ou `pip`

### Opção A) Baixar ZIP

1. Baixe o ZIP deste repositório e extraia em uma pasta local.
2. Instale as dependências e rode (veja abaixo).

### Opção B) Clonar com Git

```bash
git clone <URL_DO_REPOSITORIO>
cd local_fileSystem_MCP
```

### Instalar dependências

- Com `uv` (recomendado):
  ```bash
  uv sync
  ```
- Com `pip`:

  ```bash
  python -m venv .venv
  # macOS/Linux
  source .venv/bin/activate
  # Windows (PowerShell)
  .venv\\Scripts\\Activate.ps1

  pip install -U pip
  pip install -e .
  ```

### Configurar diretórios permitidos (whitelist)

Defina `MCP_FS_ALLOWED_DIRS` com os diretórios absolutos que o servidor poderá acessar.

- macOS/Linux (separador `:`):
  ```bash
  export MCP_FS_ALLOWED_DIRS="$HOME:/tmp"
  ```
- Windows (separador `;`):
  ```powershell
  setx MCP_FS_ALLOWED_DIRS "%USERPROFILE%;C:\\Temp"
  ```

### Executar o servidor

- Via script instalado:
  ```bash
  MCP_FS_ALLOWED_DIRS="$HOME" local-filesystem-mcp
  ```
- Ou via módulo Python:
  ```bash
  MCP_FS_ALLOWED_DIRS="$HOME" python -m local_filesystem_mcp.server
  ```

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

Como usar no Smithery:

- Importe o `mcp.json` ao criar um servidor MCP na plataforma.
- Ajuste a variável `MCP_FS_ALLOWED_DIRS` no ambiente do Smithery.
- Mais detalhes na plataforma [Smithery](https://smithery.ai/).

## Client Example

The sample `main.py` demonstrates connecting to a remote MCP server. To test this server locally, you can use the MCP CLI:

```bash
mcp dev -c mcp.json
```

## Environment

- `MCP_FS_ALLOWED_DIRS`: absolute directories that the server can access.

## License

MIT

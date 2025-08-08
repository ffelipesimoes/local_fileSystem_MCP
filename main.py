import mcp
from mcp.client.streamable_http import streamablehttp_client
import json
import base64
import os
import sys

config = {
  "logLevel": "info"
}
# Encode config in base64
config_b64 = base64.b64encode(json.dumps(config).encode()).decode()
smithery_api_key = os.getenv("SMITHERY_API_KEY")
if not smithery_api_key:
    sys.stderr.write("Missing SMITHERY_API_KEY environment variable. Please set it securely and retry.\n")
    sys.exit(1)

# Create server URL
url = f"https://server.smithery.ai/@cyanheads/filesystem-mcp-server/mcp?config={config_b64}&api_key={smithery_api_key}&profile=straight-gull-b8R60a"

async def main():
    # Connect to the server using HTTP client
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        async with mcp.ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools_result = await session.list_tools()
            print(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
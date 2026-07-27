import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from upstash_redis import Redis

load_dotenv()

redis = Redis.from_env()
mcp = FastMCP("Conversation Summarizer")

@mcp.tool()
def save_conservation_summary(summary, title, tags, ttl_seconds):
    if tags is None: tags = []

    summary_id = f"summary:{uuid.uuid4().hex[:8]}"
    created_at = datetime.now().isoformat()

    payload = {
        "id": summary_id,
        "title": title,
        "summary": summary,
        "tags": tags,
        "timestamp": created_at,
    }

    try:
        redis.set(summary_id, json.dumps(payload))

        if ttl_seconds and ttl_seconds > 0:
            redis.expire(summary_id, ttl_seconds)

        return {
            "status": "success",
            "key": summary_id,
            "message": f"Summary '{title}' successfully pushed to Upstash Redis.",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}





def main():
    print("Hello from claude-mcp-tool!")


if __name__ == "__main__":
   mcp.run() 

import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from upstash_redis import Redis

# Load local .env during local development; ignored gracefully on Horizon
load_dotenv()

# Initialize Upstash Redis client using environment variables
redis = Redis.from_env()

# Create the FastMCP instance
mcp = FastMCP("Conversation Summarizer")


@mcp.tool()
def save_conversation_summary(
    summary: str,
    title: str = "General Chat Summary",
    tags: list[str] = None,
    ttl_seconds: int = None,
) -> dict:
    """Summarizes a conversation and stores it directly into Upstash Redis."""
    if tags is None:
        tags = []

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
        # Store in Upstash Redis
        redis.set(summary_id, json.dumps(payload))

        # Optional TTL setting
        if ttl_seconds and ttl_seconds > 0:
            redis.expire(summary_id, ttl_seconds)

        return {
            "status": "success",
            "key": summary_id,
            "message": f"Summary '{title}' successfully pushed to Upstash Redis.",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    mcp.run()
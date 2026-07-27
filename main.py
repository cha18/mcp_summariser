import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field
from upstash_redis import Redis

# Load local .env during local development; ignored gracefully on Horizon
load_dotenv()

# Initialize Upstash Redis client using environment variables
redis = Redis.from_env()

# Create the FastMCP instance
mcp = FastMCP("Conversation Summarizer")


@mcp.tool()
def save_conversation_summary(
    summary: str = Field(description="A detailed, fact-dense recap of the conversation. Include specific numbers, names, locations, measurements, preferences, tradeoffs discussed, and actionable conclusions. Write in plain paragraphs — enough detail that someone reading this can reconstruct key takeaways without re-reading the chat. Aim for 3-8 sentences."),
    title: str = Field(default="General Chat Summary", description="A concise, descriptive title reflecting the main topic(s)"),
    tags: list[str] = Field(default=None, description="2-6 topic tags, e.g. ['shopping', 'sizing', 'colombo']"),
    ttl_seconds: int = Field(default=None, description="Optional time-to-live in seconds"),
) -> dict:
    """Saves a detailed conversation summary to the knowledge base vault.

    This summary is later processed by a knowledge-base agent that extracts facts,
    creates/edits Obsidian notes, and organizes them into subdirectories by topic.
    Be specific and thorough — generic summaries produce generic vault entries.
    Include concrete details: names, numbers, locations, decisions, comparisons.
    """
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
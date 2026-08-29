"""
Recoup — Webhook Idempotency Layer.

Deduplicates incoming webhooks and guarantees idempotent, safe execution.

Key principles:
1. Idempotency Key: Unique event_id or payment_id.
2. Forward-Only Transitions: A case in a terminal state (recovered/blocked)
   cannot be regressed by out-of-order webhooks.
3. Audit Log: Duplicate webhooks are logged as safe no-ops in the audit trail.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any
import aiosqlite

from app.database import DB_PATH

logger = logging.getLogger(__name__)


async def is_event_processed(idempotency_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if an idempotency key has already been processed.

    Returns:
        Tuple[bool, Optional[dict]]: (is_duplicate, previous_result)
    """
    if not idempotency_key:
        return False, None

    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                "SELECT processed_at, result FROM idempotency_keys WHERE key = ?",
                (idempotency_key,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    processed_at, result_json = row
                    result = json.loads(result_json) if result_json else {}
                    logger.info(f"Duplicate event detected for idempotency key: {idempotency_key}")
                    return True, result
    except Exception as e:
        logger.error(f"Error checking idempotency key: {e}")

    return False, None


async def record_idempotency_key(idempotency_key: str, event_id: str, result: Dict[str, Any]) -> bool:
    """
    Record an idempotency key upon successful processing.
    """
    if not idempotency_key:
        return False

    now = datetime.now(timezone.utc).isoformat()
    result_json = json.dumps(result)

    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO idempotency_keys (key, event_id, processed_at, result)
                VALUES (?, ?, ?, ?)
                """,
                (idempotency_key, event_id, now, result_json),
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to record idempotency key {idempotency_key}: {e}")
        return False

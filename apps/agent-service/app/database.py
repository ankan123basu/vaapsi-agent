"""
Recoup — Database initialization and session management.
Uses SQLite via SQLAlchemy for the audit store.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

DB_PATH = Path("recoup.db")


async def init_db():
    """Initialize the SQLite database with required tables."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        # Recovery cases table — the main state store
        await db.execute("""
            CREATE TABLE IF NOT EXISTS recovery_cases (
                case_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                raw_event TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                customer_email TEXT DEFAULT '',
                customer_phone TEXT DEFAULT '',
                customer_opted_out INTEGER DEFAULT 0,
                amount_at_risk REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'INR',
                decline_reason_raw TEXT DEFAULT '',
                root_cause TEXT DEFAULT '',
                root_cause_confidence REAL DEFAULT 0.0,
                diagnosis_method TEXT DEFAULT '',
                diagnosis_reasoning TEXT DEFAULT '',
                diagnosis_provider TEXT DEFAULT '',
                diagnosis_latency_ms REAL DEFAULT 0.0,
                recovery_channel TEXT DEFAULT '',
                recovery_action TEXT DEFAULT '',
                message_content TEXT DEFAULT '',
                offer_details TEXT DEFAULT '{}',
                scheduled_at TEXT DEFAULT '',
                guardrail_status TEXT DEFAULT '',
                guardrail_violations TEXT DEFAULT '[]',
                execution_status TEXT DEFAULT '',
                execution_result TEXT DEFAULT '{}',
                razorpay_payment_link_id TEXT DEFAULT '',
                recovery_amount REAL DEFAULT 0.0,
                case_status TEXT DEFAULT 'detected',
                retry_count INTEGER DEFAULT 0,
                idempotency_key TEXT UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Audit trail — immutable, append-only log
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                node_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                reasoning TEXT DEFAULT '',
                provider TEXT DEFAULT '',
                latency_ms REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
            )
        """)

        # Idempotency store — for webhook deduplication
        await db.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_keys (
                key TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                result TEXT DEFAULT '{}'
            )
        """)

        # Metrics snapshots — for dashboard
        await db.execute("""
            CREATE TABLE IF NOT EXISTS metrics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_at_risk REAL DEFAULT 0.0,
                total_recovered REAL DEFAULT 0.0,
                total_cases INTEGER DEFAULT 0,
                recovered_cases INTEGER DEFAULT 0,
                failed_cases INTEGER DEFAULT 0,
                blocked_cases INTEGER DEFAULT 0,
                pending_approval INTEGER DEFAULT 0,
                compliance_violations INTEGER DEFAULT 0,
                rule_hit_count INTEGER DEFAULT 0,
                llm_fallback_count INTEGER DEFAULT 0,
                avg_latency_ms REAL DEFAULT 0.0
            )
        """)

        # Create indices
        await db.execute("CREATE INDEX IF NOT EXISTS idx_cases_status ON recovery_cases(case_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_cases_event_id ON recovery_cases(event_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_audit_case_id ON audit_trail(case_id)")

        await db.commit()


async def get_db():
    """Get a database connection."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

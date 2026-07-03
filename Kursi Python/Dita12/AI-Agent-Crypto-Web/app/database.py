from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS watched_tokens (mint_address TEXT PRIMARY KEY, symbol TEXT, name TEXT, category TEXT, notes TEXT, allowed_for_trading INTEGER, blocked INTEGER, risk_level TEXT, reason_for_blocking TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS wallet_snapshots (id INTEGER PRIMARY KEY, public_address TEXT, total_value_usd REAL, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS ai_analyses (id INTEGER PRIMARY KEY, context TEXT, raw_response TEXT, parsed_response TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS trade_proposals (id INTEGER PRIMARY KEY, decision TEXT, payload TEXT, risk_score INTEGER, status TEXT DEFAULT 'PENDING', created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS dry_run_trades (id INTEGER PRIMARY KEY, proposal_id INTEGER, payload TEXT, pnl_usd REAL DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS executed_trades (id INTEGER PRIMARY KEY, proposal_id INTEGER, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS rejected_trades (id INTEGER PRIMARY KEY, proposal_id INTEGER, reason TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS risk_events (id INTEGER PRIMARY KEY, proposal_id INTEGER, severity TEXT, message TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS paper_portfolio (mint_address TEXT PRIMARY KEY, symbol TEXT, quantity REAL, average_cost_usd REAL, realized_pnl_usd REAL DEFAULT 0, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as con:
            con.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def execute(self, sql: str, params: Iterable[Any] = ()) -> int:
        with self.connect() as con:
            cur = con.execute(sql, tuple(params))
            con.commit()
            return int(cur.lastrowid or 0)

    def query(self, sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self.connect() as con:
            return [dict(row) for row in con.execute(sql, tuple(params)).fetchall()]

    def save_snapshot(self, snapshot: dict[str, Any]) -> int:
        return self.execute("INSERT INTO wallet_snapshots(public_address,total_value_usd,payload) VALUES(?,?,?)", (snapshot["public_address"], snapshot.get("total_value_usd", 0), json.dumps(snapshot)))

    def save_analysis(self, context: dict[str, Any], raw: str, parsed: dict[str, Any]) -> int:
        return self.execute("INSERT INTO ai_analyses(context,raw_response,parsed_response) VALUES(?,?,?)", (json.dumps(context), raw, json.dumps(parsed)))

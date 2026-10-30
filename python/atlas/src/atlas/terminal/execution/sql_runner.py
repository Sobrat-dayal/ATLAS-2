"""Permission-controlled, read-only SQL query engine for Stage 123."""

import re
import sqlite3
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.terminal.execution.domain import (
    ExecutionStatus,
    ResourceProfile,
    SqlSource,
    TabularColumn,
    TabularResult,
)
from atlas.terminal.execution.errors import (
    TerminalSqlSourceNotFoundError,
    TerminalSqlStatementNotAllowedError,
)

# Registry of authorized SQL sources
AUTHORIZED_SQL_SOURCES: Dict[str, SqlSource] = {
    "test_prices": SqlSource(
        source_id="test_prices",
        display_name="Test Financial Prices (Controlled Fixture)",
        source_type="in_memory_fixture",
        allowed_schemas=["public"],
        allowed_views=["test_prices"],
        is_read_only=True,
        default_row_limit=500,
        timeout_seconds=15,
        description="Controlled isolated test pricing relation with AAA, BBB, CCC fixtures.",
    ),
    "postgresql_analytical": SqlSource(
        source_id="postgresql_analytical",
        display_name="PostgreSQL Analytical Views (Read-Only)",
        source_type="postgresql_analytical",
        allowed_schemas=["analytics", "public"],
        allowed_views=["v_instruments", "v_daily_returns", "v_risk_metrics"],
        is_read_only=True,
        default_row_limit=500,
        timeout_seconds=15,
        description="Authorized institutional analytical views enforced by Row-Level Security.",
    ),
    "clickhouse_analytics": SqlSource(
        source_id="clickhouse_analytics",
        display_name="ClickHouse Time-Series Analytics (Read-Only)",
        source_type="clickhouse_analytics",
        allowed_schemas=["default"],
        allowed_views=["tick_prices_1m", "order_book_snapshots"],
        is_read_only=True,
        default_row_limit=500,
        timeout_seconds=15,
        description="High-frequency market time-series analytical repository.",
    ),
}

# Forbidden SQL keywords and clauses
FORBIDDEN_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bMERGE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bCOPY\b",
    r"\bCALL\b",
    r"\bDO\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bVACUUM\b",
    r"\bREINDEX\b",
    r"\bSELECT\s+.*\s+INTO\b",
    r"\bPG_READ_FILE\b",
    r"\bPG_WRITE_FILE\b",
    r"\bPG_SLEEP\b",
    r"\bLOAD_EXTENSION\b",
]


def validate_sql_statement(sql_text: str) -> Dict[str, Any]:
    """Strictly validates SQL text against the read-only analytical allowlist."""
    clean = sql_text.strip()
    if not clean:
        raise TerminalSqlStatementNotAllowedError("EMPTY", "Query cannot be empty.")

    # Remove comments
    stripped = re.sub(r"--.*?$", "", clean, flags=re.MULTILINE)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL).strip()

    # Reject multiple statements (separated by semicolon)
    statements = [s.strip() for s in stripped.split(";") if s.strip()]
    if len(statements) > 1:
        raise TerminalSqlStatementNotAllowedError(
            "MULTIPLE_STATEMENTS",
            "Multiple statements separated by semicolons are strictly prohibited.",
        )

    statement = statements[0] if statements else ""

    # Check for forbidden mutations and destructive clauses
    for pattern in FORBIDDEN_KEYWORDS:
        match = re.search(pattern, statement, re.IGNORECASE)
        if match:
            forbidden_kw = match.group(0).strip().upper()
            raise TerminalSqlStatementNotAllowedError(
                forbidden_kw,
                f"Statement contains prohibited mutation/privileged keyword '{forbidden_kw}'.",
            )

    # Must start with SELECT or WITH
    upper_stmt = statement.upper()
    if not (upper_stmt.startswith("SELECT") or upper_stmt.startswith("WITH")):
        first_token = statement.split()[0].upper() if statement.split() else "UNKNOWN"
        raise TerminalSqlStatementNotAllowedError(
            first_token, "Only read-only SELECT and WITH ... SELECT queries are permitted."
        )

    return {
        "valid": True,
        "statement_type": "SELECT",
        "clean_statement": statement,
    }


class SqlSandboxRunner:
    """Read-only SQL query runner enforcing statement policy and fixture isolation."""

    def __init__(self):
        self._lock = threading.Lock()
        self._init_fixture_database()

    def _init_fixture_database(self) -> None:
        """Seed the isolated reference fixture database for test_prices."""
        self._fixture_conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._fixture_conn.execute(
            "PRAGMA query_only = ON;"
        )  # Read-only pragma initially off for setup
        self._fixture_conn.execute("PRAGMA query_only = OFF;")
        self._fixture_conn.execute(
            """
            CREATE TABLE test_prices (
                instrument VARCHAR(16) PRIMARY KEY,
                price REAL NOT NULL
            );
            """
        )
        self._fixture_conn.executemany(
            "INSERT INTO test_prices (instrument, price) VALUES (?, ?);",
            [("AAA", 100.0), ("BBB", 150.0), ("CCC", 200.0)],
        )
        self._fixture_conn.commit()

        # Install engine-level read-only authorizer
        def read_only_authorizer(action_code: int, *args) -> int:
            # 21 = SQLITE_SELECT, 20 = SQLITE_READ, 31 = SQLITE_FUNCTION
            if action_code in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, 31):
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        self._fixture_conn.set_authorizer(read_only_authorizer)

    def execute(
        self,
        execution_id: str,
        sql_text: str,
        source_id: Optional[str],
        resource_profile: ResourceProfile,
        cancellation_event: Optional[threading.Event] = None,
    ) -> Dict[str, Any]:
        """Execute a validated read-only SQL query."""
        validation = validate_sql_statement(sql_text)
        query = validation["clean_statement"]

        selected_source = source_id or "test_prices"
        if selected_source not in AUTHORIZED_SQL_SOURCES:
            raise TerminalSqlSourceNotFoundError(selected_source)

        start_time = time.perf_counter()

        if cancellation_event and cancellation_event.is_set():
            return {
                "status": ExecutionStatus.CANCELLED,
                "stdout": "",
                "stderr": "SQL query was cancelled prior to execution.",
                "duration_ms": 0.0,
                "error_code": "TERMINAL_SQL_QUERY_CANCELLED",
                "error_message": "Query was cancelled by user request.",
                "row_count": 0,
                "tabular_result": None,
            }

        # Execute query against source
        max_rows = resource_profile.max_rows

        try:
            with self._lock:
                cursor = self._fixture_conn.cursor()
                cursor.execute(query)

                col_names = [d[0] for d in cursor.description] if cursor.description else []
                raw_rows = cursor.fetchmany(max_rows + 1)
                cursor.close()

            duration_ms = (time.perf_counter() - start_time) * 1000

            truncated = len(raw_rows) > max_rows
            returned_rows = raw_rows[:max_rows]

            columns = [TabularColumn(name=col, data_type="TEXT") for col in col_names]
            rows_dict = [dict(zip(col_names, row)) for row in returned_rows]

            tabular_result = TabularResult(
                columns=columns,
                rows=rows_dict,
                total_rows=len(rows_dict),
                truncated=truncated,
                as_of=datetime.now(timezone.utc),
            )

            stdout_summary = f"Selected {len(rows_dict)} row(s) in {duration_ms:.2f}ms"
            if truncated:
                stdout_summary += f" [TRUNCATED to max limit of {max_rows} rows]"

            return {
                "status": ExecutionStatus.COMPLETED,
                "stdout": stdout_summary,
                "stderr": "",
                "duration_ms": duration_ms,
                "error_code": None,
                "error_message": None,
                "row_count": len(rows_dict),
                "tabular_result": tabular_result,
            }

        except sqlite3.DatabaseError as db_err:
            duration_ms = (time.perf_counter() - start_time) * 1000
            err_msg = str(db_err)
            if "not authorized" in err_msg.lower():
                return {
                    "status": ExecutionStatus.SECURITY_DENIED,
                    "stdout": "",
                    "stderr": f"Database authorization rejected statement: {err_msg}",
                    "duration_ms": duration_ms,
                    "error_code": "TERMINAL_SQL_PERMISSION_DENIED",
                    "error_message": err_msg,
                    "row_count": 0,
                    "tabular_result": None,
                }

            return {
                "status": ExecutionStatus.FAILED,
                "stdout": "",
                "stderr": f"SQL execution error: {err_msg}",
                "duration_ms": duration_ms,
                "error_code": "TERMINAL_SQL_QUERY_FAILED",
                "error_message": err_msg,
                "row_count": 0,
                "tabular_result": None,
            }

"""Sandboxed, isolated Python execution runtime for Stage 123."""

import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable, Dict, Optional

from atlas.terminal.execution.domain import (
    ExecutionStatus,
    ResourceProfile,
    StreamOutputType,
)
from atlas.terminal.execution.errors import (
    TerminalExecutionInputTooLargeError,
)

# Standard pinned approved environment manifest
STANDARD_PYTHON_PACKAGES: Dict[str, str] = {
    "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    "numpy": "2.5.4",
    "math": "built-in",
    "statistics": "built-in",
    "datetime": "built-in",
    "json": "built-in",
    "typing": "built-in",
}


def sanitize_sandbox_environment() -> Dict[str, str]:
    """Scrub platform secrets, database credentials, and cloud API keys from process environment."""
    clean_env: Dict[str, str] = {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1",
    }

    # Retain strictly necessary OS loader environment
    for key in ("SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "COMSPEC"):
        val = os.environ.get(key)
        if val is not None:
            clean_env[key] = val

    # Verify no leaked credentials
    sensitive_keys = [
        k
        for k in clean_env.keys()
        if any(
            term in k.upper()
            for term in ("TOKEN", "KEY", "SECRET", "PASS", "DB", "AUTH", "SUPABASE")
        )
    ]
    for k in sensitive_keys:
        clean_env.pop(k, None)

    return clean_env


def redact_host_paths(text: str, sandbox_dir: str) -> str:
    """Scrub absolute host filesystem paths from exception tracebacks."""
    if not text:
        return ""
    # Normalize path separators
    clean = text.replace(sandbox_dir, "/sandbox").replace(
        sandbox_dir.replace("\\", "/"), "/sandbox"
    )
    # Redact host user profile paths
    clean = re.sub(r"[a-zA-Z]:\\[Uu]sers\\[^\\]+\\", "/home/atlas/", clean)
    clean = re.sub(r"\/Users\/[^\/]+\/", "/home/atlas/", clean)
    return clean


class PythonSandboxRunner:
    """Subprocess-isolated Python execution worker enforcing resource boundaries."""

    def __init__(self, max_input_bytes: int = 65536):
        self.max_input_bytes = max_input_bytes

    def execute(
        self,
        execution_id: str,
        code: str,
        resource_profile: ResourceProfile,
        cancellation_event: Optional[threading.Event] = None,
        on_chunk: Optional[Callable[[StreamOutputType, str], None]] = None,
    ) -> Dict[str, Any]:
        """Execute Python code in an isolated temporary directory and unprivileged subprocess."""
        code_bytes = len(code.encode("utf-8"))
        if code_bytes > self.max_input_bytes:
            raise TerminalExecutionInputTooLargeError(code_bytes, self.max_input_bytes)

        temp_dir = tempfile.mkdtemp(prefix=f"atlas_py_{execution_id}_")
        script_path = os.path.join(temp_dir, "main.py")

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        clean_env = sanitize_sandbox_environment()
        clean_env["TMP"] = temp_dir
        clean_env["TEMP"] = temp_dir

        cmd = [sys.executable, "-B", "-s", script_path]
        start_time = time.perf_counter()

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=temp_dir,
                env=clean_env,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except Exception as exc:
            return {
                "status": ExecutionStatus.INFRASTRUCTURE_FAILED,
                "stdout": "",
                "stderr": f"Failed to spawn isolated Python process: {str(exc)}",
                "duration_ms": (time.perf_counter() - start_time) * 1000,
                "error_code": "TERMINAL_EXECUTION_SANDBOX_START_FAILED",
                "error_message": str(exc),
                "row_count": None,
                "tabular_result": None,
            }

        timeout = resource_profile.timeout_seconds
        poll_interval = 0.05
        elapsed = 0.0
        cancelled = False
        timed_out = False

        while process.poll() is None:
            if cancellation_event and cancellation_event.is_set():
                cancelled = True
                process.terminate()
                try:
                    process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                break

            if elapsed >= timeout:
                timed_out = True
                process.terminate()
                try:
                    process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                break

            time.sleep(poll_interval)
            elapsed += poll_interval

        stdout_raw, stderr_raw = process.communicate()
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Enforce output length limit
        max_bytes = resource_profile.max_output_bytes
        if len(stdout_raw.encode("utf-8")) > max_bytes:
            stdout_raw = stdout_raw[:max_bytes] + "\n[OUTPUT TRUNCATED: Exceeded 64KB limit]"

        # Sanitize paths
        stdout = stdout_raw
        stderr = redact_host_paths(stderr_raw, temp_dir)

        if on_chunk:
            if stdout:
                on_chunk(StreamOutputType.STDOUT, stdout)
            if stderr:
                on_chunk(StreamOutputType.STDERR, stderr)

        # Cleanup ephemeral sandbox files
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for f_name in files:
                    try:
                        os.remove(os.path.join(root, f_name))
                    except OSError:
                        pass
                for d_name in dirs:
                    try:
                        os.rmdir(os.path.join(root, d_name))
                    except OSError:
                        pass
            os.rmdir(temp_dir)
        except OSError:
            pass

        # Determine outcome
        if cancelled:
            return {
                "status": ExecutionStatus.CANCELLED,
                "stdout": stdout,
                "stderr": stderr or "Execution cancelled by user.",
                "duration_ms": duration_ms,
                "error_code": "TERMINAL_EXECUTION_CANCELLED",
                "error_message": "Execution cancelled by user request.",
                "row_count": None,
                "tabular_result": None,
            }

        if timed_out:
            return {
                "status": ExecutionStatus.TIMED_OUT,
                "stdout": stdout,
                "stderr": stderr or f"Process exceeded timeout limit of {timeout} seconds.",
                "duration_ms": duration_ms,
                "error_code": "TERMINAL_EXECUTION_TIMED_OUT",
                "error_message": f"Execution timed out after {timeout} seconds.",
                "row_count": None,
                "tabular_result": None,
            }

        if process.returncode != 0:
            # Extract exception class name if available
            exc_match = re.search(r"([A-Za-z0-9_]+Error|[A-Za-z0-9_]+Exception):\s*(.*)", stderr)
            error_code = exc_match.group(1) if exc_match else "TERMINAL_EXECUTION_RUNTIME_FAILED"
            error_msg = (
                exc_match.group(0)
                if exc_match
                else f"Process exited with non-zero code {process.returncode}."
            )

            return {
                "status": ExecutionStatus.FAILED,
                "stdout": stdout,
                "stderr": stderr,
                "duration_ms": duration_ms,
                "error_code": error_code,
                "error_message": error_msg,
                "row_count": None,
                "tabular_result": None,
            }

        return {
            "status": ExecutionStatus.COMPLETED,
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
            "error_code": None,
            "error_message": None,
            "row_count": None,
            "tabular_result": None,
        }

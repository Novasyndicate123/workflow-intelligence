from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .meta_execution_intelligence import MetaExecutionIntelligence
from .qwen_job_store import QwenJobStore
from .coding_model_policy import CodingModelPolicy


class QwenRouteRunner:
    """Run the bounded local Qwen worker and feed durable route evidence."""

    def __init__(self, store: QwenJobStore, intelligence: MetaExecutionIntelligence, worker_command: list[str]):
        self.store = store
        self.intelligence = intelligence
        self.worker_command = list(worker_command)
        self.policy = CodingModelPolicy()
        if not self.policy.is_allowed(store.model):
            raise ValueError("REQUIRED_CODING_MODEL_POLICY_VIOLATION")

    def run(self, job_id: str, task_class: str, prompt: str) -> dict:
        started = time.time()
        proc = subprocess.run(
            self.worker_command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=300,
            check=False,
        )
        elapsed = round(time.time() - started, 3)
        try:
            payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except json.JSONDecodeError:
            payload = {"ok": False, "error": "invalid_worker_json"}
        ok = bool(payload.get("ok")) and proc.returncode == 0
        status = "success" if ok else "failure"
        content = payload.get("content", "")
        self.store.record_result(
            job_id=job_id,
            task_class=task_class,
            prompt=prompt,
            status=status,
            elapsed_seconds=elapsed,
            content=content if ok else payload.get("error", "worker_failure"),
        )
        self.intelligence.observe(
            route=self.store.model,
            task_class=task_class,
            status=status,
            duration_ms=elapsed * 1000.0,
            error_class=None if ok else str(payload.get("error", "worker_failure")),
        )
        return {
            "ok": ok,
            "job_id": job_id,
            "model": self.store.model,
            "elapsed_seconds": elapsed,
            "content": content,
        }

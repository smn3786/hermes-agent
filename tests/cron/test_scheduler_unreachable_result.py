"""Agent-returned transport failures must reach cron's bounded re-run ladder."""

from datetime import datetime, timedelta, UTC
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import cron.scheduler as sched
from cron.jobs import create_job, get_job


@pytest.fixture
def run_result(monkeypatch):
    """Keep the real scheduler and job store; replace the model execution boundary."""
    monkeypatch.setitem(sys.modules, "run_agent", SimpleNamespace(AIAgent=MagicMock()))
    monkeypatch.setattr(sched, "_reload_dotenv_and_publish_delivery_target", lambda _job: None)
    monkeypatch.setattr(sched, "_load_cron_job_config", lambda *_args: SimpleNamespace(cfg={}, model="test-model"))
    monkeypatch.setattr(sched, "_resolve_cron_agent_setup", lambda *_args: SimpleNamespace(
        blocked=None, model="test-model", fallback_notice=None))
    monkeypatch.setattr(sched, "_open_cron_session_db", lambda _job: None)
    monkeypatch.setattr(sched, "_FireAudit", MagicMock())
    monkeypatch.setattr(sched, "_teardown_cron_agent", lambda *_args: None)
    monkeypatch.setattr(sched, "finish_execution", lambda *_args, **_kwargs: None)

    def run(result, *, completed_calls=0):
        agent = SimpleNamespace(session_api_calls=completed_calls)
        monkeypatch.setattr(sched, "_construct_cron_agent", lambda *_args, **_kwargs: agent)
        monkeypatch.setattr(sched, "_run_agent_with_watchdog", lambda *_args, **_kwargs: result)
        job = create_job("morning report", "every 24h")
        success, _output, _response, error = sched.run_job(job)
        sched._finish_completed_run(sched._RunDelivery(job=job, success=success, error=error), None, "test-execution")
        return success, error, get_job(job["id"])

    return run


@pytest.mark.parametrize("failure_flag", [{"failed": True}, {"completed": False}])
def test_returned_connection_failure_schedules_bounded_rerun(run_result, failure_flag):
    """Exhausted pre-response connection failures retry minutes later, despite generic error text."""
    success, error, job = run_result({
        **failure_flag, "error": "Connection error.", "final_response": "",
        "failure_reason": "timeout", "failure_retryable": True,
    })

    assert success is False
    assert error == "RuntimeError: Connection error."
    assert job["unreachable_retry"]["attempt"] == 1
    assert timedelta(minutes=4) < datetime.fromisoformat(job["next_run_at"]) - datetime.now(UTC) < timedelta(minutes=6)


@pytest.mark.parametrize("result, completed_calls", [
    ({"failed": True, "failure_reason": "timeout", "failure_retryable": True}, 1),
    ({"failed": True, "failure_reason": "timeout", "failure_retryable": False}, 0),
    ({"failed": True, "failure_reason": "server_error", "failure_retryable": True}, 0),
    ({"failed": True, "failure_reason": "auth", "failure_retryable": False}, 0),
    ({"failed": True}, 0),
    ({"completed": True, "final_response": "report"}, 0),
])
def test_other_results_keep_natural_schedule(run_result, result, completed_calls):
    """A completed model call, other error verdict, or healthy reply must keep the daily cadence."""
    _success, _error, job = run_result(result, completed_calls=completed_calls)

    assert job.get("unreachable_retry") is None
    assert datetime.fromisoformat(job["next_run_at"]) - datetime.now(UTC) > timedelta(hours=23)

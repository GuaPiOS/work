from datetime import datetime

from w2e import daily_scheduler


def test_due_slots_only_weekdays_after_configured_time():
    config = {"daily_digest": {"schedule": {"enabled": True, "weekdays": [1, 2, 3, 4, 5], "times": ["09:30"]}}}
    assert daily_scheduler.due_slots(datetime(2026, 7, 14, 9, 31), config) == ["09:30"]  # Tue
    assert daily_scheduler.due_slots(datetime(2026, 7, 18, 9, 31), config) == []  # Sat
    assert daily_scheduler.due_slots(datetime(2026, 7, 14, 9, 29), config) == []


def test_schedule_can_be_disabled():
    config = {"daily_digest": {"schedule": {"enabled": False, "times": ["09:30"]}}}
    assert daily_scheduler.due_slots(datetime(2026, 7, 14, 10, 0), config) == []


def test_should_run_marks_one_slot_once(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_scheduler, "STATE_FILE", tmp_path / "state.json")
    now = datetime(2026, 7, 14, 12, 31)
    config = {"daily_digest": {"schedule": {"times": ["12:30"]}}}
    run, key = daily_scheduler.should_run(now, config)
    assert run is True
    daily_scheduler.mark_done(key)
    assert daily_scheduler.should_run(now, config) == (False, "")

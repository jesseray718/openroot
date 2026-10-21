import re
import json
from pathlib import Path
import pytest
from unittest.mock import patch
from src.openroot_optimizer import logger
from src.openroot_optimizer.event_models import make_event, now_utc_rfc3339


def test_rfc3339_utc_format(tmp_path):
    events_file = tmp_path / "events.jsonl"

    with patch.object(logger, 'EVENTS', events_file):
        with patch.object(logger, 'DATA_DIR', tmp_path):
            # Create test event
            event = make_event(
                node_id="test_node",
                actor_id="test_actor",
                actor_type="software_agent",
                task_id="task1",
                task_name="test",
                task_category="computational",
                status="completed",
                timestamp_utc=now_utc_rfc3339(),
                timestamp_local="2026-08-26T12:00:00-07:00",
                timezone_offset="-07:00",
                monotonic_start_s=0.0,
                monotonic_end_s=1.0,
                elapsed_monotonic_s=1.0,
                device_id="dev1",
                clock_source="system",
                clock_uncertainty_ms=10.0,
                clock_offset_ms=None,
                timestamp_quality="measured",
                location_id=None,
                latitude_deg=None,
                longitude_deg=None,
                altitude_m=None,
                input_energy_J=100.0,
                useful_output_J=80.0,
                loss_energy_J=20.0,
                stored_energy_delta_J=0.0,
                power_average_W=100.0,
                power_peak_W=120.0,
                human_time_s=0.0,
                computation_runtime_s=1.0,
                machine_runtime_s=1.0,
                idle_time_s=0.0,
                wait_time_s=0.0,
                rework_time_s=0.0,
                evidence_type="calculation",
                evidence_reference="test",
                confidence="modeled",
                notes=""
            )
            logger.append_event(event.to_dict())

    if not events_file.exists():
        pytest.fail(f"Expected events file {events_file} was not created")

    with events_file.open() as f:
        for line in f:
            e = json.loads(line)
            ts = e["timestamp_utc"]
            assert ts.endswith("Z") or re.search(r"[+-]\d{2}:\d{2}$", ts)

def test_elapsed_monotonic_nonnegative(tmp_path):
    events_file = tmp_path / "events.jsonl"

    with patch.object(logger, 'EVENTS', events_file):
        with patch.object(logger, 'DATA_DIR', tmp_path):
            event = make_event(
                node_id="test_node",
                actor_id="test_actor",
                actor_type="software_agent",
                task_id="task1",
                task_name="test",
                task_category="computational",
                status="completed",
                timestamp_utc=now_utc_rfc3339(),
                timestamp_local="2026-08-26T12:00:00-07:00",
                timezone_offset="-07:00",
                monotonic_start_s=0.0,
                monotonic_end_s=1.0,
                elapsed_monotonic_s=1.0,
                device_id="dev1",
                clock_source="system",
                clock_uncertainty_ms=10.0,
                clock_offset_ms=None,
                timestamp_quality="measured",
                location_id=None,
                latitude_deg=None,
                longitude_deg=None,
                altitude_m=None,
                input_energy_J=100.0,
                useful_output_J=80.0,
                loss_energy_J=20.0,
                stored_energy_delta_J=0.0,
                power_average_W=100.0,
                power_peak_W=120.0,
                human_time_s=0.0,
                computation_runtime_s=1.0,
                machine_runtime_s=1.0,
                idle_time_s=0.0,
                wait_time_s=0.0,
                rework_time_s=0.0,
                evidence_type="calculation",
                evidence_reference="test",
                confidence="modeled",
                notes=""
            )
            logger.append_event(event.to_dict())

    if not events_file.exists():
        pytest.fail(f"Expected events file {events_file} was not created")

    with events_file.open() as f:
        for line in f:
            e = json.loads(line)
            assert e["elapsed_monotonic_s"] >= 0

def test_unknown_human_energy_not_forced_zero(tmp_path):
    events_file = tmp_path / "events.jsonl"

    with patch.object(logger, 'EVENTS', events_file):
        with patch.object(logger, 'DATA_DIR', tmp_path):
            event = make_event(
                node_id="test_node",
                actor_id="test_actor",
                actor_type="human",
                task_id="task1",
                task_name="test",
                task_category="physical",
                status="completed",
                timestamp_utc=now_utc_rfc3339(),
                timestamp_local="2026-08-26T12:00:00-07:00",
                timezone_offset="-07:00",
                monotonic_start_s=0.0,
                monotonic_end_s=1.0,
                elapsed_monotonic_s=1.0,
                device_id="dev1",
                clock_source="system",
                clock_uncertainty_ms=10.0,
                clock_offset_ms=None,
                timestamp_quality="measured",
                location_id=None,
                latitude_deg=None,
                longitude_deg=None,
                altitude_m=None,
                input_energy_J=100.0,
                useful_output_J=80.0,
                loss_energy_J=20.0,
                stored_energy_delta_J=0.0,
                power_average_W=100.0,
                power_peak_W=120.0,
                human_time_s=3600.0,
                computation_runtime_s=0.0,
                machine_runtime_s=0.0,
                idle_time_s=0.0,
                wait_time_s=0.0,
                rework_time_s=0.0,
                evidence_type="manual_entry",
                evidence_reference="test",
                confidence="estimated",
                notes=""
            )
            logger.append_event(event.to_dict())

    if not events_file.exists():
        pytest.fail(f"Expected events file {events_file} was not created")

    with events_file.open() as f:
        for line in f:
            e = json.loads(line)
            assert "human_time_s" in e

def test_event_hash_chain_fields_present(tmp_path):
    events_file = tmp_path / "events.jsonl"

    with patch.object(logger, 'EVENTS', events_file):
        with patch.object(logger, 'DATA_DIR', tmp_path):
            event = make_event(
                node_id="test_node",
                actor_id="test_actor",
                actor_type="software_agent",
                task_id="task1",
                task_name="test",
                task_category="computational",
                status="completed",
                timestamp_utc=now_utc_rfc3339(),
                timestamp_local="2026-08-26T12:00:00-07:00",
                timezone_offset="-07:00",
                monotonic_start_s=0.0,
                monotonic_end_s=1.0,
                elapsed_monotonic_s=1.0,
                device_id="dev1",
                clock_source="system",
                clock_uncertainty_ms=10.0,
                clock_offset_ms=None,
                timestamp_quality="measured",
                location_id=None,
                latitude_deg=None,
                longitude_deg=None,
                altitude_m=None,
                input_energy_J=100.0,
                useful_output_J=80.0,
                loss_energy_J=20.0,
                stored_energy_delta_J=0.0,
                power_average_W=100.0,
                power_peak_W=120.0,
                human_time_s=0.0,
                computation_runtime_s=1.0,
                machine_runtime_s=1.0,
                idle_time_s=0.0,
                wait_time_s=0.0,
                rework_time_s=0.0,
                evidence_type="calculation",
                evidence_reference="test",
                confidence="modeled",
                notes=""
            )
            logger.append_event(event.to_dict())

    if not events_file.exists():
        pytest.fail(f"Expected events file {events_file} was not created")

    with events_file.open() as f:
        for line in f:
            e = json.loads(line)
            assert "hash_current_event" in e

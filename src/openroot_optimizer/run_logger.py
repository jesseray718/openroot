import time
from datetime import datetime, timezone
from event_models import make_event
from logger import append_event, read_last_hash, utc_local_info, monotonic_now

def rfc3339_utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def emit_sample_event(status="completed"):
    m0 = monotonic_now()
    time.sleep(0.05)
    m1 = monotonic_now()
    elapsed = max(0.0, m1 - m0)

    ts_local, tz_off = utc_local_info()
    last_hash = read_last_hash()

    # Example measured/estimated placeholders
    input_j = 5.0
    useful_j = 3.0
    loss_j = 2.0
    store_j = 0.0
    pavg = input_j / elapsed if elapsed > 0 else 0.0

    ev = make_event(
        node_id="node.compute.local",
        actor_id="agent.runtime",
        actor_type="software_agent",
        task_id="task.sample",
        task_name="sample logging cycle",
        task_category="computational",
        status=status,

        timestamp_utc=rfc3339_utc(),
        timestamp_local=ts_local,
        timezone_offset=tz_off,
        monotonic_start_s=m0,
        monotonic_end_s=m1,
        elapsed_monotonic_s=elapsed,

        device_id="device.termux",
        clock_source="system",
        clock_uncertainty_ms=50.0,
        clock_offset_ms=None,
        timestamp_quality="estimated",

        location_id=None,
        latitude_deg=None,
        longitude_deg=None,
        altitude_m=None,

        input_energy_J=input_j,
        useful_output_J=useful_j,
        loss_energy_J=loss_j,
        stored_energy_delta_J=store_j,
        power_average_W=pavg,
        power_peak_W=None,

        human_time_s=0.0,
        computation_runtime_s=elapsed,
        machine_runtime_s=0.0,
        idle_time_s=0.0,
        wait_time_s=0.0,
        rework_time_s=0.0,

        evidence_type="calculation",
        evidence_reference="runtime.sample.estimate",
        confidence="estimated",
        notes="sample event for ledger bootstrap",
        hash_previous_event=last_hash
    )
    append_event(ev.to_dict())

if __name__ == "__main__":
    emit_sample_event("started")
    emit_sample_event("completed")
    print("ok: appended sample events")

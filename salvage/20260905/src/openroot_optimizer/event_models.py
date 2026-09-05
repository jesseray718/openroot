from dataclasses import dataclass, asdict
from typing import Optional, Literal, Dict, Any
from datetime import datetime, timezone
import uuid
import hashlib
import json

ActorType = Literal["human", "machine", "sensor", "software_agent", "process"]
TaskCategory = Literal["physical", "thermal", "electrical", "computational", "coordination", "maintenance", "observation"]
StatusType = Literal["started", "paused", "resumed", "completed", "failed", "canceled"]
EvidenceType = Literal["sensor", "meter", "calculation", "manual_entry", "estimate"]
ConfidenceType = Literal["measured", "estimated", "modeled", "unknown"]
TimestampQuality = Literal["measured", "synchronized", "estimated", "manual", "unknown"]

def now_utc_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@dataclass
class Event:
    event_id: str
    parent_event_id: Optional[str]
    correlation_id: str
    node_id: str
    actor_id: str
    actor_type: ActorType
    task_id: str
    task_name: str
    task_category: TaskCategory
    status: StatusType

    timestamp_utc: str
    timestamp_local: str
    timezone_offset: str
    monotonic_start_s: float
    monotonic_end_s: float
    elapsed_monotonic_s: float

    device_id: str
    clock_source: str
    clock_uncertainty_ms: float
    clock_offset_ms: Optional[float]
    timestamp_quality: TimestampQuality

    location_id: Optional[str]
    latitude_deg: Optional[float]
    longitude_deg: Optional[float]
    altitude_m: Optional[float]

    input_energy_J: float
    useful_output_J: float
    loss_energy_J: float
    stored_energy_delta_J: float
    power_average_W: float
    power_peak_W: Optional[float]

    human_time_s: float
    computation_runtime_s: float
    machine_runtime_s: float
    idle_time_s: float
    wait_time_s: float
    rework_time_s: float

    evidence_type: EvidenceType
    evidence_reference: str
    confidence: ConfidenceType
    notes: str
    hash_previous_event: Optional[str]
    hash_current_event: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def make_hash(event_dict_without_hash: Dict[str, Any]) -> str:
    payload = json.dumps(event_dict_without_hash, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def make_event(**kwargs) -> Event:
    base = {
        "event_id": str(uuid.uuid4()),
        "parent_event_id": kwargs.get("parent_event_id"),
        "correlation_id": kwargs.get("correlation_id", str(uuid.uuid4())),
        "hash_previous_event": kwargs.get("hash_previous_event"),
    }
    merged = {**kwargs, **base}
    tmp = dict(merged)
    tmp["hash_current_event"] = ""
    h = make_hash(tmp)
    merged["hash_current_event"] = h
    return Event(**merged)

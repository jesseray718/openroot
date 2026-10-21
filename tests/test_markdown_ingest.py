from pathlib import Path
from openloom.ingest_markdown import ingest_markdown


def test_markdown_ingest(tmp_path):
    source = tmp_path / "note.md"
    source.write_text("# Hello\n\nThis is a test document.")
    pod = tmp_path / "pod"
    result = ingest_markdown(pod, source, "test-batch")
    assert result["chunks"] >= 1
    assert (pod / "pod.db").exists()

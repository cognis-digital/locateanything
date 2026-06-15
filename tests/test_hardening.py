"""Edge-case and error-path tests for the hardening changes."""
from __future__ import annotations

import json

import pytest

from locateanything.cli import main
from locateanything.core import (
    TOOL_NAME,
    _validate_image_path,
    locate,
    reason_locate,
)


# ---------------------------------------------------------------------------
# _validate_image_path
# ---------------------------------------------------------------------------

def test_validate_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        _validate_image_path(str(tmp_path / "ghost.jpg"))


def test_validate_empty_path():
    with pytest.raises(ValueError, match="must not be empty"):
        _validate_image_path("")


def test_validate_directory(tmp_path):
    with pytest.raises(ValueError, match="not a file"):
        _validate_image_path(str(tmp_path))


def test_validate_empty_file(tmp_path):
    p = tmp_path / "empty.jpg"
    p.write_bytes(b"")
    with pytest.raises(ValueError, match="empty"):
        _validate_image_path(str(p))


# ---------------------------------------------------------------------------
# locate() raises on bad input
# ---------------------------------------------------------------------------

def test_locate_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        locate(str(tmp_path / "no_such.jpg"))


def test_locate_empty_file(tmp_path):
    p = tmp_path / "empty.jpg"
    p.write_bytes(b"")
    with pytest.raises(ValueError):
        locate(str(p))


# ---------------------------------------------------------------------------
# locate() with no models available still returns a valid dict
# ---------------------------------------------------------------------------

def test_locate_no_model_returns_valid_structure(tmp_path):
    p = tmp_path / "x.jpg"
    p.write_bytes(b"\xff\xd8\xff\xe0notarealjpeg")
    res = locate(str(p))
    assert res["tool"] == TOOL_NAME
    assert "candidates" in res
    assert isinstance(res["candidates"], list)
    # When models are unreachable a 'note' key is added
    assert "note" in res


# ---------------------------------------------------------------------------
# CLI exit codes
# ---------------------------------------------------------------------------

def test_cli_missing_file_exit_2(tmp_path):
    code = main([str(tmp_path / "nope.jpg")])
    assert code == 2


def test_cli_nonexistent_path_exit_2():
    code = main(["/no/such/image.jpg"])
    assert code == 2


def test_cli_json_format_valid(tmp_path):
    """--format json should emit parseable JSON and return 0 (models may be absent)."""
    p = tmp_path / "x.jpg"
    p.write_bytes(b"\xff\xd8\xff\xe0notarealjpeg")

    from unittest.mock import patch

    captured: list[str] = []

    with patch("builtins.print", side_effect=lambda *a, **kw: captured.append(str(a[0]))):
        code = main([str(p), "--format", "json"])

    assert code == 0
    output = "\n".join(captured)
    data = json.loads(output)
    assert data["tool"] == TOOL_NAME


# ---------------------------------------------------------------------------
# reason_locate: edge cases
# ---------------------------------------------------------------------------

def test_reason_locate_empty_clues():
    """Empty clues string returns a single 'unknown' fallback candidate."""
    candidates = reason_locate("")
    assert len(candidates) == 1
    assert candidates[0].place == "unknown"


def test_candidate_confidence_clamped(monkeypatch):
    """Confidence values outside [0, 1] from the model must be clamped to [0, 1]."""
    import locateanything.core as core_mod

    def fake_chat(endpoint, messages, max_tokens=700):
        return '[{"place": "Testland", "confidence": 1.5, "rationale": "over-confident"}]'

    monkeypatch.setattr(core_mod, "_chat", fake_chat)
    candidates = reason_locate("some clues here")
    assert len(candidates) == 1
    assert candidates[0].confidence <= 1.0


def test_reason_locate_malformed_json(monkeypatch):
    """Malformed JSON from the model returns a fallback candidate, not an exception."""
    import locateanything.core as core_mod

    monkeypatch.setattr(core_mod, "_chat", lambda *a, **kw: "not json at all ][")
    candidates = reason_locate("some clues")
    assert len(candidates) >= 1
    assert candidates[0].place == "see-model-output"

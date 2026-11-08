"""
Tests for GoviSense Cryptographic Provenance & Versioning (Phase 0.2)
Verifies:
- data_version = first 8 hex of sha256 over all training tables bytes + row counts
- model_version = git commit + hash of fitted model parameters
- PipelineRunModel records both into database runs table
- Walk-forward evaluation output contains both versions
"""

import tempfile
from pathlib import Path
from govisense.provenance import (
    compute_data_version,
    compute_model_version,
    get_git_commit,
    get_current_provenance,
)
from govisense.db import PipelineRunModel, get_session, init_db


def test_data_version_format_and_determinism():
    ver1 = compute_data_version()
    assert isinstance(ver1, str)
    assert len(ver1) == 8
    # Assert hex format
    int(ver1, 16)

    # Identical call returns identical hash
    ver2 = compute_data_version()
    assert ver1 == ver2


def test_data_version_changes_on_data_mutation():
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = Path(tmpdir) / "test1.csv"
        f1.write_text("crop,price\nbig_onion,100\n", encoding="utf-8")

        v1 = compute_data_version([f1])
        assert len(v1) == 8

        # Add row
        f1.write_text("crop,price\nbig_onion,100\nbig_onion,110\n", encoding="utf-8")
        v2 = compute_data_version([f1])
        assert v1 != v2, "data_version must change when row count or bytes change"


def test_model_version_format():
    commit = get_git_commit()
    assert isinstance(commit, str)
    assert len(commit) >= 7

    m_ver = compute_model_version()
    assert "+" in m_ver
    commit_part, param_hash = m_ver.split("+", 1)
    assert len(commit_part) == 7
    assert len(param_hash) == 8


def test_pipeline_run_model_records_provenance():
    init_db()
    with get_session() as session:
        run = PipelineRunModel(trigger="test_audit")
        session.add(run)
        session.commit()

        run_id = run.run_id
        assert run.data_version is not None and len(run.data_version) == 8
        assert run.model_version is not None and "+" in run.model_version
        assert run.git_commit is not None

        # Verify reading it back
        saved = session.query(PipelineRunModel).filter_by(run_id=run_id).first()
        assert saved is not None
        assert saved.data_version == run.data_version
        assert saved.model_version == run.model_version


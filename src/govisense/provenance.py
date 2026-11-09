"""
GoviSense Provenance & Audit Versioning Module
Team DARKBITE · ModelX 2.0 Phase 1

Implements strict cryptographic versioning for regulatory traceability:
- data_version: first 8 hex characters of SHA-256 over all training tables bytes + row counts
- model_version: git commit prefix + hash of fitted model parameters
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from govisense.config import PROCESSED_DATA_DIR, DATA_DIR, MODELS_STORE_DIR


def get_git_commit(fallback: str = "unknown") -> str:
    """Retrieve current git commit hash (short or full), with graceful fallback."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        ).strip()
        if commit:
            return commit
    except Exception:
        pass
    return os.environ.get("GIT_COMMIT", fallback)


def compute_data_version(data_files: Optional[List[Union[str, Path]]] = None) -> str:
    """
    Computes data_version = first 8 hex chars of SHA-256 over the bytes of
    all processed training tables plus their exact row counts.
    """
    if data_files is None:
        target_files = []
        if PROCESSED_DATA_DIR.exists():
            for f in sorted(PROCESSED_DATA_DIR.glob("*.csv")):
                target_files.append(f)
            for f in sorted(PROCESSED_DATA_DIR.glob("*.parquet")):
                target_files.append(f)
        req_file = DATA_DIR / "crop_requirements.json"
        if req_file.exists():
            target_files.append(req_file)
    else:
        target_files = [Path(f) for f in data_files]

    if not target_files:
        return "00000000"

    hasher = hashlib.sha256()

    for file_path in sorted(target_files, key=lambda p: p.name):
        if not file_path.exists():
            continue
        try:
            content = file_path.read_bytes()
            file_sha = hashlib.sha256(content).hexdigest()
            row_count = 0
            if file_path.suffix.lower() == ".csv":
                try:
                    df = pd.read_csv(file_path)
                    row_count = len(df)
                except Exception:
                    row_count = content.count(b"\n")
            elif file_path.suffix.lower() == ".json":
                try:
                    data = json.loads(content.decode("utf-8"))
                    row_count = len(data) if isinstance(data, (list, dict)) else 1
                except Exception:
                    row_count = 1
            else:
                row_count = content.count(b"\n")

            entry = f"{file_path.name}:{row_count}:{file_sha}\n".encode("utf-8")
            hasher.update(entry)
        except Exception:
            continue

    return hasher.hexdigest()[:8]


def compute_model_params_hash(models_dir: Optional[Path] = None, extra_params: Optional[Dict[str, Any]] = None) -> str:
    """
    Computes SHA-256 over saved model artifacts and parameters.
    """
    hasher = hashlib.sha256()
    target_dir = models_dir or MODELS_STORE_DIR
    found_artifacts = False

    if target_dir.exists():
        for artifact in sorted(target_dir.rglob("*.pkl")):
            try:
                content = artifact.read_bytes()
                hasher.update(artifact.name.encode("utf-8"))
                hasher.update(hashlib.sha256(content).hexdigest().encode("utf-8"))
                found_artifacts = True
            except Exception:
                continue

    if extra_params:
        hasher.update(json.dumps(extra_params, sort_keys=True).encode("utf-8"))
        found_artifacts = True

    if not found_artifacts:
        # Default baseline model fingerprint
        hasher.update(b"govisense-v2.0-baseline-rules")

    return hasher.hexdigest()[:8]


def compute_model_version(git_commit: Optional[str] = None, params_hash: Optional[str] = None) -> str:
    """
    Computes model_version = git commit plus a hash of the fitted model parameters.
    Example: 680c25e+a1b2c3d4
    """
    commit = (git_commit or get_git_commit())[:7]
    p_hash = params_hash or compute_model_params_hash()
    return f"{commit}+{p_hash}"


def get_current_provenance() -> Dict[str, str]:
    """Convenience getter for all current execution provenance metadata."""
    git_commit = get_git_commit()
    data_version = compute_data_version()
    model_version = compute_model_version(git_commit=git_commit)
    return {
        "git_commit": git_commit,
        "data_version": data_version,
        "model_version": model_version,
    }


def compute_dataset_provenance(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Computes data_quality and is_demo from the source_type of the rows actually used,
    and checks if the database is in fallback SQLite mode.
    """
    try:
        from govisense.db.session import get_active_dialect
        from govisense.config import settings
        is_db_fallback = (get_active_dialect() == "sqlite") and ("postgresql" in str(settings.database_url))
    except Exception:
        is_db_fallback = False

    if df is None or len(df) == 0:
        return {
            "data_quality": "no_data",
            "is_demo": False,
            "db_fallback": is_db_fallback,
        }

    st_col = "source_type" if "source_type" in df.columns else ("source" if "source" in df.columns else None)
    if st_col:
        sources = set(df[st_col].dropna().astype(str).str.lower())
        if "synthetic" in sources:
            return {"data_quality": "synthetic", "is_demo": True, "db_fallback": is_db_fallback}
        if "interpolated" in sources:
            return {"data_quality": "interpolated", "is_demo": False, "db_fallback": is_db_fallback}
        if "real" in sources or "anchor" in sources:
            return {"data_quality": "real", "is_demo": False, "db_fallback": is_db_fallback}

    return {
        "data_quality": "real",
        "is_demo": False,
        "db_fallback": is_db_fallback,
    }


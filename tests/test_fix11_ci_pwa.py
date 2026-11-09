import os
from pathlib import Path
import yaml


def test_ci_workflow_validity_and_contents():
    ci_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"
    assert ci_path.exists(), "ci.yml does not exist"
    content = ci_path.read_text(encoding="utf-8")
    assert len(content) > 100, f"ci.yml is unexpectedly small ({len(content)} bytes)"
    
    # Parse YAML to verify validity
    parsed = yaml.safe_load(content)
    assert "jobs" in parsed, "ci.yml does not define any jobs"
    assert "backend-test" in parsed["jobs"], "ci.yml missing backend-test job"
    assert "frontend-build" in parsed["jobs"], "ci.yml missing frontend-build job"
    
    # Verify backend job has python setup and pytest
    backend_steps = [s.get("name", "") for s in parsed["jobs"]["backend-test"]["steps"]]
    assert any("python" in s.lower() for s in backend_steps), "Missing python setup step in backend job"
    assert any("pytest" in s.lower() for s in backend_steps), "Missing pytest step in backend job"


def test_pwa_service_worker_and_manifest():
    root = Path(__file__).resolve().parent.parent
    sw_path = root / "frontend" / "public" / "sw.js"
    manifest_path = root / "frontend" / "public" / "manifest.json"
    
    assert sw_path.exists(), "frontend/public/sw.js does not exist"
    sw_text = sw_path.read_text(encoding="utf-8")
    assert "CACHE_NAME" in sw_text
    assert "addEventListener(\"install\"" in sw_text or "addEventListener('install'" in sw_text
    assert "addEventListener(\"fetch\"" in sw_text or "addEventListener('fetch'" in sw_text
    assert "offline" in sw_text.lower()
    
    assert manifest_path.exists(), "frontend/public/manifest.json does not exist"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert "GoviSense" in manifest_text
    assert "start_url" in manifest_text


def test_offline_banner_and_sw_registration():
    root = Path(__file__).resolve().parent.parent
    app_path = root / "frontend" / "src" / "App.tsx"
    main_path = root / "frontend" / "src" / "main.tsx"
    
    app_text = app_path.read_text(encoding="utf-8")
    assert "offline-banner" in app_text, "App.tsx missing offline-banner element"
    assert "isOnline" in app_text, "App.tsx missing isOnline state tracking"
    
    main_text = main_path.read_text(encoding="utf-8")
    assert "serviceWorker" in main_text, "main.tsx missing serviceWorker registration"
    assert "/sw.js" in main_text, "main.tsx does not register /sw.js"

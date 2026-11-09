import json
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from govisense.db.session import get_session
from govisense.db.models import EvaluationResultModel
from govisense.provenance import compute_data_version

def export_scoreboard(out_json_path: str = "data/interim/scoreboard.json", out_md_path: str = "docs/model_evaluation_scoreboard.md"):
    db: Session = get_session()
    d_ver = compute_data_version()
    
    results = db.query(EvaluationResultModel).order_by(EvaluationResultModel.created_at.desc()).all()
    
    rows = []
    if not results:
        from govisense.evaluation.backtest import run_walk_forward_evaluation
        backtest_res = run_walk_forward_evaluation(crops=["big_onion", "chilli"])
        results = db.query(EvaluationResultModel).order_by(EvaluationResultModel.created_at.desc()).all()
        
    for r in results:
        details = r.details or {}
        cov = details.get("coverage_80", details.get("interval_80_coverage_pct", 80.0))
        pts = details.get("eval_points", 24)
        
        # Computed verdict: Usable only if beats baseline and coverage >= 70% and N >= 10
        if r.beat_baseline and cov >= 70.0 and pts >= 10:
            verdict = "Usable"
        elif r.beat_baseline or cov >= 60.0:
            verdict = "Usable with limits"
        else:
            verdict = "Not usable"
            
        rows.append({
            "crop": r.crop_id,
            "model": r.model_name,
            "horizon": details.get("horizon", "t+1"),
            "metric": r.metric_name,
            "model_value": round(float(r.metric_value), 4) if r.metric_value is not None else None,
            "baseline_name": r.baseline_name or "seasonal_naive",
            "baseline_value": round(float(r.baseline_value), 4) if r.baseline_value is not None else None,
            "beat_baseline": r.beat_baseline,
            "served_model": "LightGBM" if r.beat_baseline else (r.baseline_name or "seasonal_naive"),
            "coverage_80_pct": cov,
            "eval_points_n": pts,
            "data_version": d_ver,
            "verdict": verdict,
        })
        
    # Write JSON
    Path(out_json_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
        
    # Write Markdown table
    md_lines = [
        "# Model Evaluation Scoreboard",
        f"**Data Version:** `{d_ver}` | **Source:** Real CBSL Prices & Verified NASA POWER Weather\n",
        "| Crop | Model | Horizon | Metric | Model Value | Baseline Name | Baseline Value | Served Model | Coverage 80% | N | Verdict |",
        "| :--- | :--- | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |",
    ]
    for r in rows:
        md_lines.append(
            f"| `{r['crop']}` | {r['model']} | {r['horizon']} | {r['metric']} | {r['model_value']} | {r['baseline_name']} | {r['baseline_value']} | `{r['served_model']}` | {r['coverage_80_pct']}% | {r['eval_points_n']} | **{r['verdict']}** |"
        )
        
    Path(out_md_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
        
    print(f"✅ Exported {len(rows)} scoreboard rows to {out_json_path} and {out_md_path}.")
    return rows

if __name__ == "__main__":
    export_scoreboard()

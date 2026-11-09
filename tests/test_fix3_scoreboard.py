import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from govisense.db.models import Base, EvaluationResultModel
from govisense.api.routes.data import get_evaluation_scoreboard
from unittest.mock import patch


@pytest.fixture
def temp_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_scoreboard_stores_real_results_and_links_every_number(temp_db):
    # Verify table starts empty
    assert temp_db.query(EvaluationResultModel).count() == 0

    # Call endpoint with empty table -> triggers real walk-forward backtest
    res = get_evaluation_scoreboard(db=temp_db)

    # Verify rows were stored in the database
    stored_rows = temp_db.query(EvaluationResultModel).all()
    assert len(stored_rows) > 0
    assert len(res["scoreboard"]) == len(stored_rows)

    # Test that no number in the response exists without a matching stored row
    for item in res["scoreboard"]:
        matching = [
            r for r in stored_rows
            if r.crop_id == item["crop"] and r.model_name == item["module"]
        ]
        assert len(matching) == 1
        stored = matching[0]
        assert stored.metric_value == item["model_wape"]
        assert stored.baseline_value == item["baseline_wape"]
        assert stored.beat_baseline == item["beat_baseline"]
        assert stored.details.get("data_version") == res["data_version"]


def test_scoreboard_returns_no_data_when_backtest_fails(temp_db):
    assert temp_db.query(EvaluationResultModel).count() == 0
    with patch("govisense.evaluation.backtest.run_walk_forward_evaluation", side_effect=Exception("Data missing")):
        res = get_evaluation_scoreboard(db=temp_db)
        assert res["data_quality"] == "no_data"
        assert res["scoreboard"] == []


from engine.risk import assess_risk


def test_low_risk():
    result = assess_risk(
        credit_score=780,
        foir=35
    )

    assert result["risk_level"] == "LOW"
    assert result["risk_points"] == 0
    assert result["risk_factors"] == []


def test_medium_risk():
    result = assess_risk(
        credit_score=748,
        foir=35.76
    )

    assert result["risk_level"] == "MEDIUM"
    assert result["risk_points"] == 1
    assert "Credit score is moderate." in result["risk_factors"]


def test_high_risk():
    result = assess_risk(
        credit_score=672,
        foir=58.85
    )

    assert result["risk_level"] == "HIGH"
    assert result["risk_points"] == 4
    assert "Credit score is below 700." in result["risk_factors"]
    assert "FOIR is above 50%." in result["risk_factors"]
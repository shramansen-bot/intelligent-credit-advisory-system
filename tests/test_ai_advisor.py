from unittest.mock import patch, MagicMock

from engine.ai_advisor import generate_advisory


def test_generate_advisory():
    assessment = {
        "customer_name": "Test Customer",
        "product_name": "Test Loan",
        "requested_amount": 500000,
        "requested_tenure": 60,
        "estimated_emi": 11248.97,
        "foir": 35.76,
        "decision": "ELIGIBLE",
        "reasons": [],
        "risk_level": "MEDIUM",
        "risk_factors": ["Credit score is moderate."]
    }

    mock_response = MagicMock()
    mock_response.text = "Test advisory generated successfully."

    with patch(
        "engine.ai_advisor.client.models.generate_content",
        return_value=mock_response
    ):
        result = generate_advisory(assessment)

    assert result == "Test advisory generated successfully."
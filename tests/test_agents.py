from unittest.mock import MagicMock, patch

from agents.data_retrieval_agent import data_retrieval_agent
from agents.risk_analysis_agent import risk_analysis_agent
from agents.underwriting_agent import underwriting_agent
from agents.supervisor_agent import supervisor_agent


# =========================================================
# DATA RETRIEVAL AGENT TEST
# =========================================================

def test_data_retrieval_agent():
    state = {
        "customer_id": "CUS001",
        "product_id": "PERSONAL_FLEXI",
        "requested_amount": 500000,
        "requested_tenure": 60,
        "audit_trail": []
    }

    result = data_retrieval_agent(state)

    assert result["customer"]["customer_id"] == "CUS001"
    assert result["product"]["product_id"] == "PERSONAL_FLEXI"

    assert len(result["audit_trail"]) == 1

    assert (
        result["audit_trail"][0]["agent"]
        == "Data Retrieval Agent"
    )


# =========================================================
# RISK ANALYSIS AGENT TEST
# =========================================================

def test_risk_analysis_agent():
    initial_state = {
        "customer_id": "CUS001",
        "product_id": "PERSONAL_FLEXI",
        "requested_amount": 500000,
        "requested_tenure": 60,
        "audit_trail": []
    }

    retrieval_result = data_retrieval_agent(
        initial_state
    )

    state = {
        **initial_state,
        **retrieval_result
    }

    result = risk_analysis_agent(state)

    assert result["estimated_emi"] == 11248.97
    assert result["foir"] == 35.76
    assert result["risk_level"] == "MEDIUM"
    assert result["risk_points"] == 1

    assert len(result["audit_trail"]) == 2

    assert (
        result["audit_trail"][1]["agent"]
        == "Risk Analysis Agent"
    )


# =========================================================
# UNDERWRITING AGENT TEST
# =========================================================

def test_underwriting_agent():
    initial_state = {
        "customer_id": "CUS001",
        "product_id": "PERSONAL_FLEXI",
        "requested_amount": 500000,
        "requested_tenure": 60,
        "audit_trail": []
    }

    retrieval_result = data_retrieval_agent(
        initial_state
    )

    risk_state = {
        **initial_state,
        **retrieval_result
    }

    risk_result = risk_analysis_agent(
        risk_state
    )

    underwriting_state = {
        **risk_state,
        **risk_result
    }

    result = underwriting_agent(
        underwriting_state
    )

    assert result["decision"] == "ELIGIBLE"
    assert result["reasons"] == []

    assert len(result["audit_trail"]) == 3

    assert (
        result["audit_trail"][2]["agent"]
        == "Underwriting Decision Agent"
    )


# =========================================================
# SUPERVISOR ROUTING TEST
# =========================================================

def test_supervisor_initial_route():
    state = {
        "customer_id": "CUS001",
        "product_id": "PERSONAL_FLEXI",
        "requested_amount": 500000,
        "requested_tenure": 60,
        "audit_trail": []
    }

    result = supervisor_agent(state)

    assert result["next_agent"] == "data_retrieval"

    assert len(result["audit_trail"]) == 1

    assert (
        result["audit_trail"][0]["agent"]
        == "Supervisor Agent"
    )


# =========================================================
# COMPLETE SUPERVISOR-ROUTED LANGGRAPH TEST
# =========================================================

def test_complete_multi_agent_workflow():
    """
    Test the complete LangGraph workflow without requiring
    a real Gemini API request.

    Policy retrieval and Gemini generation are mocked so the
    workflow remains deterministic and suitable for offline tests.
    """

    mock_policy_results = [
        {
            "text": (
                "Synthetic policy context for "
                "multi-agent workflow testing."
            ),
            "similarity": 0.95
        }
    ]

    mock_response = MagicMock()

    mock_response.text = (
        "Multi-agent advisory generated successfully."
    )

    mock_client = MagicMock()

    mock_client.models.generate_content.return_value = (
        mock_response
    )

    with patch(
        "agents.policy_agent.retrieve_relevant_policy",
        return_value=mock_policy_results
    ), patch(
        "agents.explanation_agent.get_gemini_client",
        return_value=mock_client
    ):

        from agents.workflow import run_loan_advisory

        result = run_loan_advisory(
            customer_id="CUS001",
            product_id="PERSONAL_FLEXI",
            requested_amount=500000,
            requested_tenure=60
        )

    # -----------------------------------------------------
    # CUSTOMER AND PRODUCT
    # -----------------------------------------------------

    assert (
        result["customer"]["customer_id"]
        == "CUS001"
    )

    assert (
        result["product"]["product_id"]
        == "PERSONAL_FLEXI"
    )

    # -----------------------------------------------------
    # AFFORDABILITY AND RISK
    # -----------------------------------------------------

    assert result["estimated_emi"] == 11248.97
    assert result["foir"] == 35.76

    assert result["risk_level"] == "MEDIUM"
    assert result["risk_points"] == 1

    # -----------------------------------------------------
    # UNDERWRITING
    # -----------------------------------------------------

    assert result["decision"] == "ELIGIBLE"
    assert result["reasons"] == []

    # -----------------------------------------------------
    # POLICY / RAG
    # -----------------------------------------------------

    assert result["retrieved_policy"] == (
        mock_policy_results
    )

    # -----------------------------------------------------
    # EXPLANATION
    # -----------------------------------------------------

    assert (
        result["advisory"]
        == "Multi-agent advisory generated successfully."
    )

    # -----------------------------------------------------
    # COMPLETE AUDIT TRAIL
    # -----------------------------------------------------

    assert len(result["audit_trail"]) == 11

    agent_names = [
        entry["agent"]
        for entry in result["audit_trail"]
    ]

    assert agent_names == [
        "Supervisor Agent",
        "Data Retrieval Agent",
        "Supervisor Agent",
        "Risk Analysis Agent",
        "Supervisor Agent",
        "Underwriting Decision Agent",
        "Supervisor Agent",
        "Policy / RAG Agent",
        "Supervisor Agent",
        "Explanation Agent",
        "Supervisor Agent"
    ]

    # -----------------------------------------------------
    # SUPERVISOR ROUTING ORDER
    # -----------------------------------------------------

    supervisor_routes = [
        entry["details"]["next_agent"]
        for entry in result["audit_trail"]
        if entry["agent"] == "Supervisor Agent"
    ]

    assert supervisor_routes == [
        "data_retrieval",
        "risk_analysis",
        "underwriting",
        "policy_rag",
        "explanation",
        "end"
    ]

    # Final supervisor decision must terminate the graph.
    assert result["next_agent"] == "end"

def test_complete_multi_agent_workflow():
    mock_policy_results = [
        {
            "text": (
                "Synthetic policy context for "
                "multi-agent workflow testing."
            ),
            "similarity": 0.95
        }
    ]

    mock_response = MagicMock()
    mock_response.text = (
        "Multi-agent advisory generated successfully."
    )

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = (
        mock_response
    )

    with patch(
        "agents.policy_agent.retrieve_relevant_policy",
        return_value=mock_policy_results
    ), patch(
        "agents.explanation_agent.get_gemini_client",
        return_value=mock_client
    ):
        from agents.workflow import run_loan_advisory

        result = run_loan_advisory(
            customer_id="CUS001",
            product_id="PERSONAL_FLEXI",
            requested_amount=500000,
            requested_tenure=60
        )

    assert result["customer"]["customer_id"] == "CUS001"
    assert result["product"]["product_id"] == "PERSONAL_FLEXI"

    assert result["estimated_emi"] == 11248.97
    assert result["foir"] == 35.76

    assert result["decision"] == "ELIGIBLE"
    assert result["risk_level"] == "MEDIUM"
    assert result["risk_points"] == 1

    assert (
        result["advisory"]
        == "Multi-agent advisory generated successfully."
    )

        # -----------------------------------------------------
    # COMPLETE AUDIT TRAIL
    # -----------------------------------------------------

    assert len(result["audit_trail"]) == 11

    agent_names = [
        entry["agent"]
        for entry in result["audit_trail"]
    ]

    assert agent_names == [
        "Supervisor Agent",
        "Data Retrieval Agent",
        "Supervisor Agent",
        "Risk Analysis Agent",
        "Supervisor Agent",
        "Underwriting Decision Agent",
        "Supervisor Agent",
        "Policy / RAG Agent",
        "Supervisor Agent",
        "Explanation Agent",
        "Supervisor Agent"
    ]

    # -----------------------------------------------------
    # SUPERVISOR ROUTING ORDER
    # -----------------------------------------------------

    supervisor_routes = [
        entry["details"]["next_agent"]
        for entry in result["audit_trail"]
        if entry["agent"] == "Supervisor Agent"
    ]

    assert supervisor_routes == [
        "data_retrieval",
        "risk_analysis",
        "underwriting",
        "policy_rag",
        "explanation",
        "end"
    ]

    # The final Supervisor route terminates the graph.
    assert result["next_agent"] == "end"
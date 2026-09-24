from unittest.mock import MagicMock, patch

from agents.data_retrieval_agent import data_retrieval_agent
from agents.risk_analysis_agent import risk_analysis_agent
from agents.underwriting_agent import underwriting_agent
from agents.supervisor_agent import supervisor_agent


MOCK_CUSTOMER = {
    "customer_id": "CUS001",
    "name": "Arjun Sen",
    "age": 31,
    "employment_type": "Salaried",
    "monthly_net_income": 72000.0,
    "existing_monthly_obligations": 14500.0,
    "monthly_expenses": 26000.0,
    "credit_score": 748,
    "kyc_status": "Verified",
    "income_proof_verified": True,
    "employment_years": 5.0,
    "fraud_flag": False,
}


MOCK_PRODUCT = {
    "product_id": "PERSONAL_FLEXI",
    "product_name": "Personal Flexi Loan",
    "description": (
        "General-purpose unsecured personal loan for eligible "
        "salaried and self-employed applicants."
    ),
    "annual_interest_rate": 12.5,
    "min_loan_amount": 50000.0,
    "max_loan_amount": 1000000.0,
    "min_tenure_months": 12,
    "max_tenure_months": 60,
    "min_credit_score": 700,
    "max_foir_percent": 50.0,
    "min_age": 21,
    "max_age": 60,
    "allowed_employment_types": [
        "Salaried",
        "Self-Employed",
    ],
}


def get_initial_state():
    return {
        "customer_id": "CUS001",
        "product_id": "PERSONAL_FLEXI",
        "requested_amount": 500000,
        "requested_tenure": 60,
        "audit_trail": [],
    }


def run_mocked_data_retrieval(state):
    with patch(
        "agents.data_retrieval_agent.get_customer_by_id",
        return_value=MOCK_CUSTOMER,
    ), patch(
        "agents.data_retrieval_agent.get_loan_product_by_id",
        return_value=MOCK_PRODUCT,
    ):
        return data_retrieval_agent(state)


def test_data_retrieval_agent():
    state = get_initial_state()

    result = run_mocked_data_retrieval(
        state
    )

    assert (
        result["customer"]["customer_id"]
        == "CUS001"
    )

    assert (
        result["customer"]["name"]
        == "Arjun Sen"
    )

    assert (
        result["product"]["product_id"]
        == "PERSONAL_FLEXI"
    )

    assert (
        result["product"]["min_age"]
        == 21
    )

    assert (
        result["product"]["max_age"]
        == 60
    )

    assert (
        result["product"][
            "allowed_employment_types"
        ]
        == [
            "Salaried",
            "Self-Employed",
        ]
    )

    assert len(
        result["audit_trail"]
    ) == 1

    assert (
        result["audit_trail"][0]["agent"]
        == "Data Retrieval Agent"
    )

    assert (
        result["audit_trail"][0]["action"]
        == (
            "Retrieved customer and loan product "
            "data from PostgreSQL."
        )
    )


def test_risk_analysis_agent():
    initial_state = get_initial_state()

    retrieval_result = (
        run_mocked_data_retrieval(
            initial_state
        )
    )

    state = {
        **initial_state,
        **retrieval_result,
    }

    result = risk_analysis_agent(
        state
    )

    assert (
        result["estimated_emi"]
        == 11248.97
    )

    assert result["foir"] == 35.76

    assert (
        result["risk_level"]
        == "MEDIUM"
    )

    assert (
        result["risk_points"]
        == 1
    )

    assert len(
        result["audit_trail"]
    ) == 2

    assert (
        result["audit_trail"][1]["agent"]
        == "Risk Analysis Agent"
    )


def test_underwriting_agent():
    initial_state = get_initial_state()

    retrieval_result = (
        run_mocked_data_retrieval(
            initial_state
        )
    )

    risk_state = {
        **initial_state,
        **retrieval_result,
    }

    risk_result = risk_analysis_agent(
        risk_state
    )

    underwriting_state = {
        **risk_state,
        **risk_result,
    }

    result = underwriting_agent(
        underwriting_state
    )

    assert (
        result["decision"]
        == "ELIGIBLE"
    )

    assert result["reasons"] == []

    assert len(
        result["audit_trail"]
    ) == 3

    assert (
        result["audit_trail"][2]["agent"]
        == "Underwriting Decision Agent"
    )


def test_supervisor_initial_route():
    state = get_initial_state()

    result = supervisor_agent(
        state
    )

    assert (
        result["next_agent"]
        == "data_retrieval"
    )

    assert len(
        result["audit_trail"]
    ) == 1

    assert (
        result["audit_trail"][0]["agent"]
        == "Supervisor Agent"
    )


def test_complete_multi_agent_workflow():
    """
    Test the complete LangGraph workflow without requiring:

    - a live PostgreSQL database for persistence,
    - real policy retrieval,
    - a real Gemini API request.

    External dependencies are mocked so this remains a
    deterministic unit test.

    The Policy / RAG Agent performs two independent searches:
    one for internal lending policy and one for RBI regulatory
    guidance.
    """

    mock_internal_policy_results = [
        {
            "chunk_id": 1,
            "source_name": "lending_policy.txt",
            "source_type": "INTERNAL_POLICY",
            "source_title": (
                "Synthetic Lending Policy"
            ),
            "source_url": None,
            "text": (
                "Synthetic internal policy context "
                "for multi-agent workflow testing."
            ),
            "similarity": 0.95,
        }
    ]

    mock_rbi_policy_results = [
        {
            "chunk_id": 10,
            "source_name": (
                "rbi_key_facts_statement.txt"
            ),
            "source_type": (
                "RBI_REGULATORY_GUIDANCE"
            ),
            "source_title": (
                "RBI Key Facts Statement (KFS) "
                "for Loans and Advances"
            ),
            "source_url": (
                "https://www.rbi.org.in/"
            ),
            "text": (
                "RBI regulatory guidance context "
                "for multi-agent workflow testing."
            ),
            "similarity": 0.90,
        }
    ]

    def mock_policy_retrieval(
        query,
        top_k=2,
        source_type=None,
    ):
        if source_type == "INTERNAL_POLICY":
            return mock_internal_policy_results

        if (
            source_type
            == "RBI_REGULATORY_GUIDANCE"
        ):
            return mock_rbi_policy_results

        return (
            mock_internal_policy_results
            + mock_rbi_policy_results
        )

    mock_response = MagicMock()

    mock_response.text = (
        "Multi-agent advisory generated "
        "successfully."
    )

    mock_client = MagicMock()

    mock_client.models.generate_content.return_value = (
        mock_response
    )

    with patch(
        "agents.data_retrieval_agent.get_customer_by_id",
        return_value=MOCK_CUSTOMER,
    ), patch(
        "agents.data_retrieval_agent.get_loan_product_by_id",
        return_value=MOCK_PRODUCT,
    ), patch(
        "agents.policy_agent.retrieve_relevant_policy",
        side_effect=mock_policy_retrieval,
    ), patch(
        "agents.explanation_agent.get_gemini_client",
        return_value=mock_client,
    ):
        from agents.workflow import (
            run_loan_advisory,
        )

        result = run_loan_advisory(
            customer_id="CUS001",
            product_id="PERSONAL_FLEXI",
            requested_amount=500000,
            requested_tenure=60,
            persist_to_database=False,
        )

    assert (
        result["customer"]["customer_id"]
        == "CUS001"
    )

    assert (
        result["product"]["product_id"]
        == "PERSONAL_FLEXI"
    )

    assert (
        result["product"]["min_age"]
        == 21
    )

    assert (
        result["product"]["max_age"]
        == 60
    )

    assert (
        result["product"][
            "allowed_employment_types"
        ]
        == [
            "Salaried",
            "Self-Employed",
        ]
    )

    assert (
        result["estimated_emi"]
        == 11248.97
    )

    assert result["foir"] == 35.76

    assert (
        result["risk_level"]
        == "MEDIUM"
    )

    assert (
        result["risk_points"]
        == 1
    )

    assert (
        result["risk_factors"]
        == [
            "Credit score is moderate."
        ]
    )

    assert (
        result["decision"]
        == "ELIGIBLE"
    )

    assert result["reasons"] == []

    assert (
        result["retrieved_policy"]
        == (
            mock_internal_policy_results
            + mock_rbi_policy_results
        )
    )

    assert (
        result["retrieved_policy"][0][
            "source_type"
        ]
        == "INTERNAL_POLICY"
    )

    assert (
        result["retrieved_policy"][1][
            "source_type"
        ]
        == "RBI_REGULATORY_GUIDANCE"
    )

    assert (
        result["advisory"]
        == (
            "Multi-agent advisory generated "
            "successfully."
        )
    )

    assert (
        "application_id"
        not in result
    )

    assert len(
        result["audit_trail"]
    ) == 11

    agent_names = [
        entry["agent"]
        for entry in result[
            "audit_trail"
        ]
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
        "Supervisor Agent",
    ]

    policy_audit_entry = next(
        entry
        for entry in result[
            "audit_trail"
        ]
        if (
            entry["agent"]
            == "Policy / RAG Agent"
        )
    )

    assert (
        policy_audit_entry["details"][
            "sections_retrieved"
        ]
        == 2
    )

    assert (
        policy_audit_entry["details"][
            "internal_policy_sections"
        ]
        == 1
    )

    assert (
        policy_audit_entry["details"][
            "rbi_guidance_sections"
        ]
        == 1
    )

    supervisor_routes = [
        entry["details"]["next_agent"]
        for entry in result[
            "audit_trail"
        ]
        if (
            entry["agent"]
            == "Supervisor Agent"
        )
    ]

    assert supervisor_routes == [
        "data_retrieval",
        "risk_analysis",
        "underwriting",
        "policy_rag",
        "explanation",
        "end",
    ]

    assert (
        result["next_agent"]
        == "end"
    )
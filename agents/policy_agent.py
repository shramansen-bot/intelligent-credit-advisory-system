from engine.policy_retriever import retrieve_relevant_policy

from agents.state import LoanAdvisoryState


def build_policy_query(state: LoanAdvisoryState):
    """
    Build a retrieval query from the current loan assessment state.
    """

    query = f"""
Retrieve the lending policies relevant to this loan application.

Loan product: {state["product"]["product_name"]}
Eligibility decision: {state["decision"]}
Eligibility reasons: {state["reasons"]}
FOIR: {state["foir"]}%
Risk level: {state["risk_level"]}
Risk factors: {state["risk_factors"]}
"""

    return query


def policy_agent(state: LoanAdvisoryState):
    """
    Retrieve the most relevant synthetic lending-policy sections
    for the current loan assessment.
    """

    query = build_policy_query(state)

    retrieved_policy = retrieve_relevant_policy(
        query,
        top_k=3
    )

    audit_entry = {
        "agent": "Policy / RAG Agent",
        "action": (
            "Retrieved relevant lending-policy sections "
            "using semantic similarity."
        ),
        "details": {
            "sections_retrieved": len(retrieved_policy),
            "similarity_scores": [
                round(item["similarity"], 4)
                for item in retrieved_policy
            ]
        }
    }

    audit_trail = state.get(
        "audit_trail",
        []
    ) + [audit_entry]

    return {
        "retrieved_policy": retrieved_policy,
        "audit_trail": audit_trail
    }
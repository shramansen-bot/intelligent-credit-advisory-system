from engine.policy_retriever import retrieve_relevant_policy

from agents.state import LoanAdvisoryState


INTERNAL_POLICY_TOP_K = 3
RBI_GUIDANCE_TOP_K = 2


def build_policy_query(state: LoanAdvisoryState):
    """
    Build a retrieval query from the current loan assessment state.
    """

    query = f"""
Retrieve the lending policies and regulatory guidance relevant to
this loan application.

Loan product: {state["product"]["product_name"]}
Eligibility decision: {state["decision"]}
Eligibility reasons: {state["reasons"]}
FOIR: {state["foir"]}%
Risk level: {state["risk_level"]}
Risk factors: {state["risk_factors"]}
"""

    return query


def retrieve_internal_policy(query):
    """
    Retrieve prototype-specific lending rules.

    These rules contain the synthetic underwriting requirements
    used by the Intelligent Credit Advisory System, including
    eligibility, FOIR, credit-score, and risk-classification rules.
    """

    return retrieve_relevant_policy(
        query,
        top_k=INTERNAL_POLICY_TOP_K,
        source_type="INTERNAL_POLICY",
    )


def retrieve_rbi_guidance(query):
    """
    Retrieve external RBI regulatory guidance.

    RBI guidance provides regulatory and borrower-protection context.
    It does not define or override the prototype's internal
    underwriting thresholds.
    """

    return retrieve_relevant_policy(
        query,
        top_k=RBI_GUIDANCE_TOP_K,
        source_type="RBI_REGULATORY_GUIDANCE",
    )


def policy_agent(state: LoanAdvisoryState):
    """
    Retrieve relevant internal lending policy and RBI regulatory
    guidance for the current loan assessment.

    Internal policy determines the prototype's configured lending
    rules. RBI material is retrieved separately as external
    regulatory context.

    The two sources are combined only after retrieval so that
    internal policy cannot crowd RBI guidance out of the RAG
    context, or vice versa.
    """

    query = build_policy_query(state)

    internal_policy = retrieve_internal_policy(
        query
    )

    rbi_guidance = retrieve_rbi_guidance(
        query
    )

    retrieved_policy = (
        internal_policy
        + rbi_guidance
    )

    audit_entry = {
        "agent": "Policy / RAG Agent",
        "action": (
            "Retrieved relevant internal lending policy "
            "and RBI regulatory guidance using "
            "semantic similarity."
        ),
        "details": {
            "sections_retrieved": len(
                retrieved_policy
            ),
            "internal_policy_sections": len(
                internal_policy
            ),
            "rbi_guidance_sections": len(
                rbi_guidance
            ),
            "sources": [
                {
                    "source_type": item[
                        "source_type"
                    ],
                    "source_title": item[
                        "source_title"
                    ],
                    "similarity": round(
                        item["similarity"],
                        4,
                    ),
                }
                for item in retrieved_policy
            ],
        },
    }

    audit_trail = state.get(
        "audit_trail",
        [],
    ) + [audit_entry]

    return {
        "retrieved_policy": retrieved_policy,
        "audit_trail": audit_trail,
    }
from typing import TypedDict


class LoanAdvisoryState(TypedDict, total=False):
    """
    Shared state passed between agents in the LangGraph workflow.

    Each agent reads the information it needs and adds its own
    results back into this shared state.
    """

    # Original user request
    customer_id: str
    product_id: str
    requested_amount: float
    requested_tenure: int

    # Data Retrieval Agent
    customer: dict
    product: dict

    # Risk Analysis Agent
    estimated_emi: float
    foir: float
    risk_level: str
    risk_points: int
    risk_factors: list[str]

    # Underwriting Decision Agent
    decision: str
    reasons: list[str]

    # Policy / RAG Agent
    retrieved_policy: list[dict]

    # Explanation Agent
    advisory: str

    next_agent: str
    audit_trail: list[dict]
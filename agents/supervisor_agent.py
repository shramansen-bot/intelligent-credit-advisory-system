from agents.state import LoanAdvisoryState


def supervisor_agent(state: LoanAdvisoryState):
    """
    Inspect the shared LangGraph state and determine which
    specialized agent should execute next.

    The supervisor uses deterministic routing rather than an LLM.
    This keeps workflow control predictable, testable and auditable.
    """

    # -----------------------------------------------------
    # ROUTE 1: DATA RETRIEVAL
    # -----------------------------------------------------

    if "customer" not in state or "product" not in state:
        next_agent = "data_retrieval"

    # -----------------------------------------------------
    # ROUTE 2: RISK ANALYSIS
    # -----------------------------------------------------

    elif (
        "estimated_emi" not in state
        or "foir" not in state
        or "risk_level" not in state
    ):
        next_agent = "risk_analysis"

    # -----------------------------------------------------
    # ROUTE 3: UNDERWRITING
    # -----------------------------------------------------

    elif "decision" not in state:
        next_agent = "underwriting"

    # -----------------------------------------------------
    # ROUTE 4: POLICY / RAG
    # -----------------------------------------------------

    elif "retrieved_policy" not in state:
        next_agent = "policy_rag"

    # -----------------------------------------------------
    # ROUTE 5: EXPLANATION
    # -----------------------------------------------------

    elif "advisory" not in state:
        next_agent = "explanation"

    # -----------------------------------------------------
    # ROUTE 6: WORKFLOW COMPLETE
    # -----------------------------------------------------

    else:
        next_agent = "end"

    audit_entry = {
        "agent": "Supervisor Agent",
        "action": "Inspected shared workflow state and selected next route.",
        "details": {
            "next_agent": next_agent
        }
    }

    audit_trail = state.get(
        "audit_trail",
        []
    ) + [audit_entry]

    return {
        "next_agent": next_agent,
        "audit_trail": audit_trail
    }
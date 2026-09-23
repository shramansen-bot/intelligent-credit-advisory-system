from langgraph.graph import StateGraph, START, END

from agents.state import LoanAdvisoryState
from agents.supervisor_agent import supervisor_agent
from agents.data_retrieval_agent import data_retrieval_agent
from agents.risk_analysis_agent import risk_analysis_agent
from agents.underwriting_agent import underwriting_agent
from agents.policy_agent import policy_agent
from agents.explanation_agent import explanation_agent


# =========================================================
# SUPERVISOR ROUTING FUNCTION
# =========================================================

def route_from_supervisor(state: LoanAdvisoryState):
    """
    Read the route selected by the Supervisor Agent.

    LangGraph uses the returned string to determine which
    specialized node should execute next.
    """

    return state["next_agent"]


# =========================================================
# BUILD LANGGRAPH WORKFLOW
# =========================================================

def build_loan_advisory_graph():
    """
    Build the supervisor-routed multi-agent loan advisory graph.

    Each specialized agent performs one responsibility and then
    returns control to the Supervisor Agent. The Supervisor
    inspects the shared state and determines the next route.
    """

    workflow = StateGraph(LoanAdvisoryState)

    # -----------------------------------------------------
    # REGISTER AGENTS
    # -----------------------------------------------------

    workflow.add_node(
        "supervisor",
        supervisor_agent
    )

    workflow.add_node(
        "data_retrieval",
        data_retrieval_agent
    )

    workflow.add_node(
        "risk_analysis",
        risk_analysis_agent
    )

    workflow.add_node(
        "underwriting",
        underwriting_agent
    )

    workflow.add_node(
        "policy_rag",
        policy_agent
    )

    workflow.add_node(
        "explanation",
        explanation_agent
    )

    # -----------------------------------------------------
    # ENTRY POINT
    # -----------------------------------------------------

    workflow.add_edge(
        START,
        "supervisor"
    )

    # -----------------------------------------------------
    # CONDITIONAL SUPERVISOR ROUTING
    # -----------------------------------------------------

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "data_retrieval": "data_retrieval",
            "risk_analysis": "risk_analysis",
            "underwriting": "underwriting",
            "policy_rag": "policy_rag",
            "explanation": "explanation",
            "end": END
        }
    )

    # -----------------------------------------------------
    # RETURN CONTROL TO SUPERVISOR
    # -----------------------------------------------------

    workflow.add_edge(
        "data_retrieval",
        "supervisor"
    )

    workflow.add_edge(
        "risk_analysis",
        "supervisor"
    )

    workflow.add_edge(
        "underwriting",
        "supervisor"
    )

    workflow.add_edge(
        "policy_rag",
        "supervisor"
    )

    workflow.add_edge(
        "explanation",
        "supervisor"
    )

    return workflow.compile()


# =========================================================
# COMPILE GRAPH
# =========================================================

loan_advisory_graph = build_loan_advisory_graph()


# =========================================================
# PUBLIC WORKFLOW FUNCTION
# =========================================================

def run_loan_advisory(
    customer_id,
    product_id,
    requested_amount,
    requested_tenure
):
    """
    Execute the complete supervisor-routed multi-agent workflow.
    """

    initial_state = {
        "customer_id": customer_id,
        "product_id": product_id,
        "requested_amount": requested_amount,
        "requested_tenure": requested_tenure,
        "audit_trail": []
    }

    return loan_advisory_graph.invoke(
        initial_state
    )


# =========================================================
# COMMAND-LINE TEST
# =========================================================

if __name__ == "__main__":

    result = run_loan_advisory(
        customer_id="CUS001",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    print(
        "\n=== SUPERVISOR-ROUTED MULTI-AGENT "
        "LOAN ADVISORY ==="
    )

    print(
        "\nCustomer:",
        result["customer"]["name"]
    )

    print(
        "Product:",
        result["product"]["product_name"]
    )

    print(
        "Estimated EMI:",
        result["estimated_emi"]
    )

    print(
        "FOIR:",
        result["foir"]
    )

    print(
        "Decision:",
        result["decision"]
    )

    print(
        "Risk:",
        result["risk_level"]
    )

    print(
        "\n=== AUDIT TRAIL ==="
    )

    for index, entry in enumerate(
        result["audit_trail"],
        start=1
    ):

        print(
            f"\n{index}. {entry['agent']}"
        )

        print(
            entry["action"]
        )

        if entry.get("details"):

            print(
                "Details:",
                entry["details"]
            )

    print(
        "\n=== AI ADVISORY ==="
    )

    print(
        result["advisory"]
    )
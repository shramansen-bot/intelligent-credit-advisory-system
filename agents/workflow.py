from langgraph.graph import END, StateGraph

from agents.state import LoanAdvisoryState
from agents.supervisor_agent import supervisor_agent
from agents.data_retrieval_agent import data_retrieval_agent
from agents.risk_analysis_agent import risk_analysis_agent
from agents.underwriting_agent import underwriting_agent
from agents.policy_agent import policy_agent
from agents.explanation_agent import explanation_agent

from engine.database_repository import (
    create_loan_application,
    update_loan_application_result,
    save_audit_logs,
)


# =========================================================
# SUPERVISOR ROUTING
# =========================================================

def route_from_supervisor(state: LoanAdvisoryState):
    """
    Read the route selected by the Supervisor Agent.
    """
    return state["next_agent"]


# =========================================================
# BUILD LANGGRAPH WORKFLOW
# =========================================================

workflow = StateGraph(LoanAdvisoryState)

workflow.add_node(
    "supervisor",
    supervisor_agent,
)

workflow.add_node(
    "data_retrieval",
    data_retrieval_agent,
)

workflow.add_node(
    "risk_analysis",
    risk_analysis_agent,
)

workflow.add_node(
    "underwriting",
    underwriting_agent,
)

workflow.add_node(
    "policy_rag",
    policy_agent,
)

workflow.add_node(
    "explanation",
    explanation_agent,
)


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

workflow.set_entry_point("supervisor")


# ---------------------------------------------------------
# SUPERVISOR CONDITIONAL ROUTING
# ---------------------------------------------------------

workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "data_retrieval": "data_retrieval",
        "risk_analysis": "risk_analysis",
        "underwriting": "underwriting",
        "policy_rag": "policy_rag",
        "explanation": "explanation",
        "end": END,
    },
)


# ---------------------------------------------------------
# RETURN EACH SPECIALIST AGENT TO SUPERVISOR
# ---------------------------------------------------------

workflow.add_edge(
    "data_retrieval",
    "supervisor",
)

workflow.add_edge(
    "risk_analysis",
    "supervisor",
)

workflow.add_edge(
    "underwriting",
    "supervisor",
)

workflow.add_edge(
    "policy_rag",
    "supervisor",
)

workflow.add_edge(
    "explanation",
    "supervisor",
)


# ---------------------------------------------------------
# COMPILE GRAPH
# ---------------------------------------------------------

loan_advisory_graph = workflow.compile()


# =========================================================
# RUN COMPLETE LOAN ADVISORY WORKFLOW
# =========================================================

def run_loan_advisory(
    customer_id,
    product_id,
    requested_amount,
    requested_tenure,
    persist_to_database=True,
):
    """
    Run the complete multi-agent loan advisory workflow.

    When persist_to_database is True:

    1. Create the application in PostgreSQL.
    2. Run the LangGraph multi-agent workflow.
    3. Update the application with the assessment results.
    4. Persist the complete audit trail.

    Unit tests can set persist_to_database=False so that
    PostgreSQL is not required.
    """

    application_id = None

    # -----------------------------------------------------
    # CREATE PERSISTENT APPLICATION
    # -----------------------------------------------------

    if persist_to_database:
        application_id = create_loan_application(
            customer_id=customer_id,
            product_id=product_id,
            requested_amount=requested_amount,
            requested_tenure=requested_tenure,
        )

    # -----------------------------------------------------
    # INITIAL LANGGRAPH STATE
    # -----------------------------------------------------

    initial_state = {
        "customer_id": customer_id,
        "product_id": product_id,
        "requested_amount": requested_amount,
        "requested_tenure": requested_tenure,
        "audit_trail": [],
    }

    # -----------------------------------------------------
    # RUN MULTI-AGENT WORKFLOW
    # -----------------------------------------------------

    result = loan_advisory_graph.invoke(
        initial_state
    )

    # -----------------------------------------------------
    # PERSIST FINAL RESULTS
    # -----------------------------------------------------

    if persist_to_database:
        update_loan_application_result(
            application_id=application_id,
            estimated_emi=result["estimated_emi"],
            foir=result["foir"],
            risk_level=result["risk_level"],
            risk_points=result["risk_points"],
            decision=result["decision"],
        )

        save_audit_logs(
            application_id=application_id,
            audit_trail=result["audit_trail"],
        )

        # Include the PostgreSQL application ID in the
        # returned result for the UI/API.
        result["application_id"] = application_id

    return result
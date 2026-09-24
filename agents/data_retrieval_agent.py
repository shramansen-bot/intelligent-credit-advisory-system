from engine.database_repository import (
    get_customer_by_id,
    get_loan_product_by_id,
)
from agents.state import LoanAdvisoryState


def data_retrieval_agent(state: LoanAdvisoryState):
    """
    Retrieve customer and loan product information
    from the PostgreSQL system of record.
    """

    customer_id = state["customer_id"]
    product_id = state["product_id"]

    customer = get_customer_by_id(customer_id)
    product = get_loan_product_by_id(product_id)

    if customer is None:
        raise ValueError(
            f"Customer '{customer_id}' was not found in PostgreSQL."
        )

    if product is None:
        raise ValueError(
            f"Loan product '{product_id}' was not found in PostgreSQL."
        )

    audit_entry = {
        "agent": "Data Retrieval Agent",
        "action": (
            "Retrieved customer and loan product data "
            "from PostgreSQL."
        ),
        "details": {
            "customer_id": customer_id,
            "product_id": product_id,
            "kyc_status": customer["kyc_status"],
            "income_proof_verified": (
                customer["income_proof_verified"]
            ),
            "credit_score": customer["credit_score"],
        },
    }

    audit_trail = (
        state.get("audit_trail", [])
        + [audit_entry]
    )

    return {
        "customer": customer,
        "product": product,
        "audit_trail": audit_trail,
    }

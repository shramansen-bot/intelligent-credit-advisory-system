from engine.data_loader import load_customers, load_loan_products

from agents.state import LoanAdvisoryState


def data_retrieval_agent(state: LoanAdvisoryState):
    """
    Retrieve the customer and loan product required for the
    current loan advisory request.
    """

    customers = load_customers()
    products = load_loan_products()

    customer_id = state["customer_id"]
    product_id = state["product_id"]

    customer = next(
        (
            item
            for item in customers
            if item["customer_id"] == customer_id
        ),
        None
    )

    product = next(
        (
            item
            for item in products
            if item["product_id"] == product_id
        ),
        None
    )

    if customer is None:
        raise ValueError(
            f"Customer '{customer_id}' was not found."
        )

    if product is None:
        raise ValueError(
            f"Loan product '{product_id}' was not found."
        )

    audit_entry = {
        "agent": "Data Retrieval Agent",
        "action": "Retrieved customer and loan product data.",
        "details": {
            "customer_id": customer_id,
            "product_id": product_id,
            "kyc_status": customer["kyc_status"],
            "income_proof_verified": customer[
                "income_proof_verified"
            ],
            "credit_score": customer["credit_score"]
        }
    }

    audit_trail = state.get(
        "audit_trail",
        []
    ) + [audit_entry]

    return {
        "customer": customer,
        "product": product,
        "audit_trail": audit_trail
    }

from engine.affordability import calculate_emi, calculate_foir
from engine.risk import assess_risk

from agents.state import LoanAdvisoryState


def risk_analysis_agent(state: LoanAdvisoryState):
    """
    Calculate affordability metrics and determine the prototype
    risk classification for the current loan request.

    Financial calculations remain deterministic and reuse the
    existing tested engine functions.
    """

    customer = state["customer"]
    product = state["product"]

    requested_amount = state["requested_amount"]
    requested_tenure = state["requested_tenure"]

    # Calculate the estimated EMI using the annual interest rate
    # configured for the selected synthetic loan product.
    estimated_emi = calculate_emi(
        principal=requested_amount,
        annual_interest_rate=product["annual_interest_rate"],
        tenure_months=requested_tenure
    )

    # Calculate FOIR using the customer's monthly net income,
    # existing monthly obligations and proposed loan EMI.
    foir = calculate_foir(
        monthly_net_income=customer["monthly_net_income"],
        existing_monthly_obligations=customer["existing_monthly_obligations"],
        proposed_emi=estimated_emi
    )

    # Determine the prototype risk classification using the
    # existing deterministic risk engine.
    risk_result = assess_risk(
        credit_score=customer["credit_score"],
        foir=foir
    )

    # Record this agent's work in the shared audit trail.
    audit_entry = {
        "agent": "Risk Analysis Agent",
        "action": (
            "Calculated EMI, FOIR and prototype risk classification."
        ),
        "details": {
            "estimated_emi": estimated_emi,
            "foir": foir,
            "risk_level": risk_result["risk_level"],
            "risk_points": risk_result["risk_points"],
            "risk_factors": risk_result["risk_factors"]
        }
    }

    audit_trail = state.get(
        "audit_trail",
        []
    ) + [audit_entry]

    return {
        "estimated_emi": estimated_emi,
        "foir": foir,
        "risk_level": risk_result["risk_level"],
        "risk_points": risk_result["risk_points"],
        "risk_factors": risk_result["risk_factors"],
        "audit_trail": audit_trail
    }
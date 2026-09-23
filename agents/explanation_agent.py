from google.genai import errors

from agents.state import LoanAdvisoryState
from engine.ai_advisor import get_gemini_client


def explanation_agent(state: LoanAdvisoryState):
    """
    Generate a grounded natural-language explanation of the
    deterministic loan assessment.

    The Generative AI model explains the result but does not
    calculate or override the underwriting decision.
    """

    policy_context = "\n\n".join(
        item["text"]
        for item in state["retrieved_policy"]
    )

    customer = state["customer"]
    product = state["product"]

    prompt = f"""
You are the Explanation Agent in an educational multi-agent
credit advisory system.

Your responsibility is to explain an already-completed deterministic
loan assessment.

STRICT GROUNDING RULES:

Use only:
1. The loan assessment information supplied below.
2. The retrieved policy context supplied below.

Do not change, override, or independently recalculate:
- the eligibility decision
- EMI
- FOIR
- risk points
- risk level

Do not invent additional lending rules, regulatory requirements,
credit-score standards, FOIR standards, or rejection reasons.

If the supplied information does not support a statement,
do not make that statement.

LOAN ASSESSMENT:

Customer: {customer["name"]}
Loan Product: {product["product_name"]}
Requested Amount: INR {state["requested_amount"]}
Requested Tenure: {state["requested_tenure"]} months
Estimated EMI: INR {state["estimated_emi"]}
FOIR: {state["foir"]}%
Eligibility Decision: {state["decision"]}
Eligibility Reasons: {state["reasons"]}
Risk Level: {state["risk_level"]}
Risk Points: {state["risk_points"]}
Risk Factors: {state["risk_factors"]}

RETRIEVED POLICY CONTEXT:

{policy_context}

RESPONSE REQUIREMENTS:

Provide:
1. Assessment Summary
2. Affordability Explanation
3. Eligibility Explanation
4. Risk Explanation
5. Practical Next Steps

Clearly state that this is an educational prototype assessment
and does not represent a formal lending decision by a real
financial institution.
"""

    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        advisory = response.text

    except errors.ServerError as error:
        if error.code == 503:
            advisory = (
                "AI advisory is temporarily unavailable because "
                "the Gemini service is experiencing high demand. "
                "Please try again later."
            )
        else:
            raise

    audit_entry = {
        "agent": "Explanation Agent",
        "action": (
            "Generated a grounded natural-language explanation "
            "of the deterministic assessment."
        ),
        "details": {
            "model": "gemini-3.8-flash",
            "policy_sections_used": len(
                state["retrieved_policy"]
            )
        }
    }

    audit_trail = state.get(
        "audit_trail",
        []
    ) + [audit_entry]

    return {
        "advisory": advisory,
        "audit_trail": audit_trail
    }
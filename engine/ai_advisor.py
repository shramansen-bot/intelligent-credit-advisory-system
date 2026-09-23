import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from engine.assessment import assess_loan
from engine.policy_retriever import retrieve_relevant_policy


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )


client = genai.Client(api_key=api_key)


def build_retrieval_query(assessment):
    reasons = assessment["reasons"]
    risk_factors = assessment["risk_factors"]

    query = f"""
Explain the lending policies relevant to this loan assessment.

Eligibility decision: {assessment["decision"]}
Eligibility reasons: {reasons}
Risk level: {assessment["risk_level"]}
Risk factors: {risk_factors}
FOIR: {assessment["foir"]}%
"""

    return query


def generate_advisory(assessment):
    retrieval_query = build_retrieval_query(assessment)

    retrieved_results = retrieve_relevant_policy(
        retrieval_query,
        top_k=3
    )

    policy_context = "\n\n".join(
        result["text"]
        for result in retrieved_results
    )

    prompt = f"""
You are an AI credit advisory assistant for an educational prototype.

Explain the loan assessment below in clear, professional and
easy-to-understand language.

STRICT GROUNDING RULES:

Use only:
1. The Loan Assessment provided below.
2. The Retrieved Policy Context provided below.

Do not introduce external banking rules, industry benchmarks,
credit-score ranges, FOIR standards, regulatory requirements,
or lending policies that are not explicitly present in the supplied
information.

Do not change, override, or independently recalculate the eligibility
decision, EMI, FOIR, risk points, or risk level.

Do not invent reasons for the customer's eligibility or risk level.

If the supplied information does not support a statement, do not make
that statement.

LOAN ASSESSMENT:

Customer: {assessment["customer_name"]}
Loan Product: {assessment["product_name"]}
Requested Amount: INR {assessment["requested_amount"]}
Tenure: {assessment["requested_tenure"]} months
Estimated EMI: INR {assessment["estimated_emi"]}
FOIR: {assessment["foir"]}%
Eligibility Decision: {assessment["decision"]}
Eligibility Reasons: {assessment["reasons"]}
Risk Level: {assessment["risk_level"]}
Risk Points: {assessment["risk_points"]}
Risk Factors: {assessment["risk_factors"]}

RETRIEVED POLICY CONTEXT:

{policy_context}

RESPONSE REQUIREMENTS:

Provide:
1. Assessment Summary
2. Affordability Explanation
3. Eligibility Explanation
4. Risk Explanation
5. Practical Next Steps

Clearly state that this is an educational prototype assessment and
does not represent a formal lending decision by a real financial
institution.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text

    except errors.ServerError as error:
        if error.code == 503:
            return (
                "AI advisory is temporarily unavailable because the "
                "Gemini service is experiencing high demand. "
                "Please try again later."
            )

        raise


if __name__ == "__main__":
    assessment = assess_loan(
        customer_id="CUS001",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    advisory = generate_advisory(assessment)

    print(advisory)
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors


# Load environment variables from the .env file
load_dotenv()

# Read the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Stop the program with a clear message if the key is missing
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# Create the Gemini client
client = genai.Client(api_key=api_key)


def generate_advisory(assessment):
    """
    Generate a human-readable advisory explanation
    from the deterministic loan assessment.
    """

    prompt = f"""
You are an AI credit advisory assistant.

Your job is to explain the loan assessment provided below in clear,
professional and easy-to-understand language.

Use only the information contained in the Loan Assessment below.

Do not introduce external banking rules, industry benchmarks,
credit-score ranges, FOIR standards, regulatory requirements,
or lending policies that are not explicitly provided.

Do not invent reasons for the customer's risk level.

Do not change, override, or independently recalculate the decision.
The eligibility decision and risk assessment were produced by a
deterministic rule-based system.

Loan Assessment:
Customer: {assessment["customer_name"]}
Loan Product: {assessment["product_name"]}
Requested Amount: INR {assessment["requested_amount"]}
Tenure: {assessment["requested_tenure"]} months
Estimated EMI: INR {assessment["estimated_emi"]}
FOIR: {assessment["foir"]}%
Eligibility Decision: {assessment["decision"]}
Eligibility Reasons: {assessment["reasons"]}
Risk Level: {assessment["risk_level"]}
Risk Factors: {assessment["risk_factors"]}

Provide:
1. A short assessment summary.
2. An explanation of the affordability position.
3. An explanation of the risk indicators.
4. Practical suggestions for the applicant.

Do not claim that this assessment represents a real bank approval.
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
    from engine.assessment import assess_loan

    assessment = assess_loan(
        customer_id="CUS001",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    advisory = generate_advisory(assessment)

    print(advisory)
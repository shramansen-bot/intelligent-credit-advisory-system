def check_age_eligibility(customer_age, min_age, max_age):
    if min_age <= customer_age <= max_age:
        return True

    return False


def check_credit_score(credit_score, min_credit_score):
    if credit_score >= min_credit_score:
        return True

    return False

def check_employment_type(employment_type, allowed_employment_types):
    if employment_type in allowed_employment_types:
        return True

    return False

def check_kyc(kyc_status):
    if kyc_status == "Verified":
        return True

    return False

def check_income_proof(income_proof_verified):
    if income_proof_verified:
        return True

    return False


def check_fraud_flag(fraud_flag):
    if fraud_flag:
        return False

    return True


def check_loan_amount(
    requested_amount,
    min_loan_amount,
    max_loan_amount
):
    if min_loan_amount <= requested_amount <= max_loan_amount:
        return True

    return False


def check_tenure(
    requested_tenure,
    min_tenure_months,
    max_tenure_months
):
    if min_tenure_months <= requested_tenure <= max_tenure_months:
        return True

    return False


def check_foir(foir, max_foir_percent):
    if foir <= max_foir_percent:
        return True

    return False

def evaluate_eligibility(
    customer,
    product,
    requested_amount,
    requested_tenure,
    foir
):
    reasons = []

    if not check_age_eligibility(
        customer["age"],
        product["min_age"],
        product["max_age"]
    ):
        reasons.append("Customer age is outside the permitted range.")

    if not check_credit_score(
        customer["credit_score"],
        product["min_credit_score"]
    ):
        reasons.append("Credit score is below the minimum requirement.")

    if not check_employment_type(
        customer["employment_type"],
        product["allowed_employment_types"]
    ):
        reasons.append("Employment type is not supported by this product.")

    if not check_kyc(customer["kyc_status"]):
        reasons.append("KYC verification is incomplete.")

    if not check_income_proof(customer["income_proof_verified"]):
        reasons.append("Income proof has not been verified.")

    if not check_fraud_flag(customer["fraud_flag"]):
        reasons.append("Applicant has been flagged for fraud review.")

    if not check_loan_amount(
        requested_amount,
        product["min_loan_amount"],
        product["max_loan_amount"]
    ):
        reasons.append("Requested loan amount is outside the permitted range.")

    if not check_tenure(
        requested_tenure,
        product["min_tenure_months"],
        product["max_tenure_months"]
    ):
        reasons.append("Requested tenure is outside the permitted range.")

    if not check_foir(
        foir,
        product["max_foir_percent"]
    ):
        reasons.append("FOIR exceeds the maximum permitted limit.")

    if len(reasons) == 0:
        decision = "ELIGIBLE"
    else:
        decision = "NOT ELIGIBLE"

    return {
        "decision": decision,
        "reasons": reasons
    }

if __name__ == "__main__":
    age_result = check_age_eligibility(31, 21, 60)

    credit_result = check_credit_score(748, 700)

    employment_result = check_employment_type(
        "Salaried",
        ["Salaried", "Self-Employed"]
    )

    kyc_result = check_kyc("Verified")

    income_proof_result = check_income_proof(True)

    fraud_result = check_fraud_flag(False)

    amount_result = check_loan_amount(
        500000,
        50000,
        1000000
    )

    tenure_result = check_tenure(
        60,
        12,
        60
    )

    foir_result = check_foir(
        35.59,
        50
    )

    print("Age eligible:", age_result)
    print("Credit score eligible:", credit_result)
    print("Employment eligible:", employment_result)
    print("KYC verified:", kyc_result)
    print("Income proof verified:", income_proof_result)
    print("Fraud check passed:", fraud_result)
    print("Loan amount eligible:", amount_result)
    print("Tenure eligible:", tenure_result)
    print("FOIR eligible:", foir_result)
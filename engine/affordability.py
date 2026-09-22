def calculate_emi(principal, annual_interest_rate, tenure_months):
    monthly_rate = annual_interest_rate / (12 * 100)

    emi = principal * (
        monthly_rate * (1 + monthly_rate) ** tenure_months
    ) / (
        (1 + monthly_rate) ** tenure_months - 1
    )

    return round(emi, 2)


def calculate_foir(
    monthly_net_income,
    existing_monthly_obligations,
    proposed_emi
):
    total_obligations = existing_monthly_obligations + proposed_emi

    foir = (total_obligations / monthly_net_income) * 100

    return round(foir, 2)


def calculate_disposable_income(
    monthly_net_income,
    monthly_expenses,
    existing_monthly_obligations,
    proposed_emi
):
    disposable_income = (
        monthly_net_income
        - monthly_expenses
        - existing_monthly_obligations
        - proposed_emi
    )

    return round(disposable_income, 2)


def calculate_max_affordable_emi(
    monthly_net_income,
    existing_monthly_obligations,
    max_foir_percent
):
    max_total_obligations = (
        monthly_net_income * max_foir_percent / 100
    )

    max_affordable_emi = (
        max_total_obligations - existing_monthly_obligations
    )

    return round(max(0, max_affordable_emi), 2)


# -----------------------------
# Temporary testing section
# -----------------------------

if __name__ == "__main__":
    emi = calculate_emi(500000, 12, 60)

    foir = calculate_foir(
        monthly_net_income=72000,
        existing_monthly_obligations=14500,
        proposed_emi=emi
    )

    disposable_income = calculate_disposable_income(
        monthly_net_income=72000,
        monthly_expenses=26000,
        existing_monthly_obligations=14500,
        proposed_emi=emi
    )

    max_affordable_emi = calculate_max_affordable_emi(
        monthly_net_income=72000,
        existing_monthly_obligations=14500,
        max_foir_percent=50
    )

    print("Monthly EMI:", emi)
    print("FOIR:", foir, "%")
    print("Disposable Income:", disposable_income)
    print("Maximum Affordable EMI:", max_affordable_emi)
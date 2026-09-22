from engine.affordability import (
    calculate_emi,
    calculate_foir,
    calculate_disposable_income,
    calculate_max_affordable_emi,
)


def test_calculate_emi():
    result = calculate_emi(500000, 12, 60)
    assert result == 11122.22


def test_calculate_foir():
    result = calculate_foir(
        monthly_net_income=72000,
        existing_monthly_obligations=14500,
        proposed_emi=11122.22
    )

    assert result == 35.59


def test_calculate_disposable_income():
    result = calculate_disposable_income(
        monthly_net_income=72000,
        monthly_expenses=26000,
        existing_monthly_obligations=14500,
        proposed_emi=11122.22
    )

    assert result == 20377.78


def test_calculate_max_affordable_emi():
    result = calculate_max_affordable_emi(
        monthly_net_income=72000,
        existing_monthly_obligations=14500,
        max_foir_percent=50
    )

    assert result == 21500.0
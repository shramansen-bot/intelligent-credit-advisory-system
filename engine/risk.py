def assess_risk(credit_score, foir):
    risk_points = 0
    risk_factors = []

    # Credit score risk
    if credit_score < 700:
        risk_points += 2
        risk_factors.append("Credit score is below 700.")
    elif credit_score < 750:
        risk_points += 1
        risk_factors.append("Credit score is moderate.")

    # FOIR risk
    if foir > 50:
        risk_points += 2
        risk_factors.append("FOIR is above 50%.")
    elif foir > 40:
        risk_points += 1
        risk_factors.append("FOIR is moderately high.")

    # Final risk classification
    if risk_points >= 3:
        risk_level = "HIGH"
    elif risk_points >= 1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_level": risk_level,
        "risk_points": risk_points,
        "risk_factors": risk_factors
    }


if __name__ == "__main__":
    result = assess_risk(
        credit_score=748,
        foir=35.76
    )

    print(result)
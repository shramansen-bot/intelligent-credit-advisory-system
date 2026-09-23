import streamlit as st

from engine.data_loader import load_customers, load_loan_products
from engine.assessment import assess_loan
from engine.ai_advisor import generate_advisory


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Intelligent Credit Advisory System",
    page_icon="💳",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "assessment" not in st.session_state:
    st.session_state.assessment = None

if "advisory" not in st.session_state:
    st.session_state.advisory = None


# =========================================================
# HEADER
# =========================================================

st.title("💳 Intelligent Credit Advisory System")

st.caption(
    "Explainable loan eligibility, affordability, risk assessment "
    "and AI-powered credit advisory."
)

st.info(
    "Educational prototype only. The results shown by this system "
    "do not represent a formal lending decision by any real bank, "
    "NBFC, financial institution, or regulatory authority."
)


# =========================================================
# LOAD DATA
# =========================================================

customers = load_customers()
products = load_loan_products()


customer_options = {
    customer["name"]: customer["customer_id"]
    for customer in customers
}

product_options = {
    product["product_name"]: product["product_id"]
    for product in products
}


# =========================================================
# APPLICATION INPUTS
# =========================================================

st.header("Loan Application")

left_column, right_column = st.columns(2)


with left_column:

    selected_customer_name = st.selectbox(
        "Select Customer",
        options=list(customer_options.keys())
    )

    requested_amount = st.number_input(
        "Requested Loan Amount (INR)",
        min_value=10000,
        max_value=5000000,
        value=500000,
        step=10000
    )


with right_column:

    selected_product_name = st.selectbox(
        "Select Loan Product",
        options=list(product_options.keys())
    )

    requested_tenure = st.number_input(
        "Requested Tenure (Months)",
        min_value=6,
        max_value=120,
        value=60,
        step=6
    )


selected_customer_id = customer_options[
    selected_customer_name
]

selected_product_id = product_options[
    selected_product_name
]


# Find complete selected customer
selected_customer = next(
    customer
    for customer in customers
    if customer["customer_id"] == selected_customer_id
)


# Find complete selected product
selected_product = next(
    product
    for product in products
    if product["product_id"] == selected_product_id
)


# =========================================================
# CUSTOMER AND PRODUCT INFORMATION
# =========================================================

st.divider()

profile_column, product_column = st.columns(2)


with profile_column:

    st.subheader("Customer Profile")

    st.write(
        f"**Employment:** "
        f"{selected_customer['employment_type']}"
    )

    st.write(
        f"**Monthly Net Income:** "
        f"₹{selected_customer['monthly_net_income']:,.2f}"
    )

    st.write(
        f"**Existing Monthly Obligations:** "
        f"₹{selected_customer['existing_monthly_obligations']:,.2f}"
    )

    st.write(
        f"**Credit Score:** "
        f"{selected_customer['credit_score']}"
    )

    st.write(
        f"**KYC Status:** "
        f"{selected_customer['kyc_status']}"
    )


with product_column:

    st.subheader("Loan Product Information")

    st.write(
        f"**Interest Rate:** "
        f"{selected_product['annual_interest_rate']}% p.a."
    )

    st.write(
        f"**Loan Amount Range:** "
        f"₹{selected_product['min_loan_amount']:,.0f} "
        f"to ₹{selected_product['max_loan_amount']:,.0f}"
    )

    st.write(
        f"**Tenure Range:** "
        f"{selected_product['min_tenure_months']} "
        f"to {selected_product['max_tenure_months']} months"
    )

    st.write(
        f"**Minimum Credit Score:** "
        f"{selected_product['min_credit_score']}"
    )

    st.write(
        f"**Maximum FOIR:** "
        f"{selected_product['max_foir_percent']}%"
    )


# =========================================================
# ASSESSMENT BUTTON
# =========================================================

st.divider()

assess_button = st.button(
    "Assess Loan",
    type="primary",
    use_container_width=True
)


if assess_button:

    assessment = assess_loan(
        customer_id=selected_customer_id,
        product_id=selected_product_id,
        requested_amount=requested_amount,
        requested_tenure=requested_tenure
    )

    st.session_state.assessment = assessment

    # Clear an old AI advisory when a new assessment is made.
    st.session_state.advisory = None


# =========================================================
# DISPLAY ASSESSMENT
# =========================================================

assessment = st.session_state.assessment


if assessment:

    if "error" in assessment:

        st.error(
            assessment["error"]
        )

    else:

        st.header("Assessment Result")

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Estimated EMI",
                f"₹{assessment['estimated_emi']:,.2f}"
            )


        with col2:

            st.metric(
                "FOIR",
                f"{assessment['foir']:.2f}%"
            )


        with col3:

            st.metric(
                "Eligibility",
                assessment["decision"]
            )


        with col4:

            st.metric(
                "Risk Level",
                assessment["risk_level"]
            )


        # =================================================
        # ELIGIBILITY
        # =================================================

        st.subheader("Eligibility Explanation")


        if assessment["reasons"]:

            for reason in assessment["reasons"]:

                st.warning(
                    reason
                )

        else:

            st.success(
                "All configured eligibility checks passed."
            )


        # =================================================
        # RISK
        # =================================================

        st.subheader("Risk Indicators")

        st.write(
            f"**Risk Points:** "
            f"{assessment['risk_points']}"
        )


        if assessment["risk_factors"]:

            for factor in assessment["risk_factors"]:

                st.write(
                    f"• {factor}"
                )

        else:

            st.success(
                "No additional risk factors were identified "
                "by the prototype risk model."
            )


        # =================================================
        # AI ADVISORY
        # =================================================

        st.divider()

        st.header("AI Credit Advisory")

        st.write(
            "The advisory uses the deterministic assessment together "
            "with relevant sections retrieved from the synthetic "
            "lending-policy knowledge base."
        )


        advisory_button_text = (
            "Retry AI Advisory"
            if st.session_state.advisory
            else "Generate AI Advisory"
        )


        generate_button = st.button(
            advisory_button_text,
            use_container_width=True
        )


        if generate_button:

            with st.spinner(
                "Retrieving relevant policy information "
                "and generating the advisory..."
            ):

                advisory = generate_advisory(
                    assessment
                )

                st.session_state.advisory = advisory


        if st.session_state.advisory:

            st.markdown(
                st.session_state.advisory
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Intelligent Credit Advisory System | "
    "Educational AI & Financial Technology Prototype"
)
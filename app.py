import streamlit as st

from engine.data_loader import load_customers, load_loan_products
from agents.workflow import run_loan_advisory


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

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None


# =========================================================
# HEADER
# =========================================================

st.title("💳 Intelligent Credit Advisory System")

st.caption(
    "LangGraph-orchestrated multi-agent loan eligibility, "
    "affordability, risk analysis, policy retrieval and "
    "AI-powered credit advisory."
)

st.info(
    "Educational prototype only. The results shown by this system "
    "do not represent a formal lending decision by any real bank, "
    "NBFC, financial institution, or regulatory authority."
)


# =========================================================
# MULTI-AGENT ARCHITECTURE
# =========================================================

with st.expander(
    "View Multi-Agent Architecture",
    expanded=False
):
    st.code(
        """
                     Supervisor Agent
                           |
                           v
                  Data Retrieval Agent
                           |
                           v
                     Supervisor
                           |
                           v
                   Risk Analysis Agent
                           |
                           v
                     Supervisor
                           |
                           v
             Underwriting Decision Agent
                           |
                           v
                     Supervisor
                           |
                           v
                   Policy / RAG Agent
                           |
                           v
                     Supervisor
                           |
                           v
                  Explanation Agent
                           |
                           v
                     Supervisor
                           |
                           v
                          END
        """,
        language="text"
    )

    st.write(
        "The workflow is orchestrated using LangGraph. "
        "The Supervisor Agent inspects the shared workflow state "
        "and conditionally routes execution to the appropriate "
        "specialized agent."
    )

    st.write(
        "After each specialized agent completes its task, control "
        "returns to the Supervisor Agent. The Supervisor then "
        "determines which stage should execute next."
    )

    st.write(
        "Financial calculations, risk classification and eligibility "
        "decisions remain deterministic. Gemini is used for policy "
        "embeddings and grounded natural-language explanation."
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

    st.write(
        f"**Income Proof Verified:** "
        f"{selected_customer['income_proof_verified']}"
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
# MULTI-AGENT ASSESSMENT BUTTON
# =========================================================

st.divider()

run_button = st.button(
    "Run Multi-Agent Loan Assessment",
    type="primary",
    use_container_width=True
)


# =========================================================
# RUN LANGGRAPH WORKFLOW
# =========================================================

if run_button:

    try:

        with st.spinner(
            "Running the supervisor-routed multi-agent "
            "credit advisory workflow..."
        ):

            workflow_result = run_loan_advisory(
                customer_id=selected_customer_id,
                product_id=selected_product_id,
                requested_amount=requested_amount,
                requested_tenure=requested_tenure
            )

            st.session_state.workflow_result = workflow_result

    except Exception as error:

        st.session_state.workflow_result = None

        st.error(
            f"The multi-agent workflow could not be completed: "
            f"{error}"
        )


# =========================================================
# DISPLAY WORKFLOW RESULT
# =========================================================

result = st.session_state.workflow_result


if result:

    st.header("Assessment Result")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Estimated EMI",
            f"₹{result['estimated_emi']:,.2f}"
        )


    with col2:

        st.metric(
            "FOIR",
            f"{result['foir']:.2f}%"
        )


    with col3:

        st.metric(
            "Eligibility",
            result["decision"]
        )


    with col4:

        st.metric(
            "Risk Level",
            result["risk_level"]
        )


    # =====================================================
    # ELIGIBILITY EXPLANATION
    # =====================================================

    st.subheader("Eligibility Explanation")


    if result["reasons"]:

        for reason in result["reasons"]:

            st.warning(
                reason
            )

    else:

        st.success(
            "All configured eligibility checks passed."
        )


    # =====================================================
    # RISK INDICATORS
    # =====================================================

    st.subheader("Risk Indicators")

    st.write(
        f"**Risk Points:** "
        f"{result['risk_points']}"
    )


    if result["risk_factors"]:

        for factor in result["risk_factors"]:

            st.write(
                f"• {factor}"
            )

    else:

        st.success(
            "No additional risk factors were identified "
            "by the prototype risk model."
        )


    # =====================================================
    # AI CREDIT ADVISORY
    # =====================================================

    st.divider()

    st.header("AI Credit Advisory")

    st.write(
        "The Explanation Agent uses the deterministic assessment "
        "together with policy sections retrieved by the Policy / "
        "RAG Agent. The AI does not independently determine "
        "loan eligibility."
    )

    st.markdown(
        result["advisory"]
    )


    # =====================================================
    # RETRIEVED POLICY CONTEXT
    # =====================================================

    with st.expander(
        "View Retrieved Policy Context",
        expanded=False
    ):

        for index, policy_item in enumerate(
            result["retrieved_policy"],
            start=1
        ):

            st.markdown(
                f"### Retrieved Policy Section {index}"
            )

            st.write(
                f"**Similarity Score:** "
                f"{policy_item['similarity']:.4f}"
            )

            st.write(
                policy_item["text"]
            )

            if index < len(
                result["retrieved_policy"]
            ):
                st.divider()


    # =====================================================
    # MULTI-AGENT AUDIT TRAIL
    # =====================================================

    st.divider()

    st.header("Multi-Agent Execution & Audit Trail")

    st.write(
        "The audit trail records both Supervisor routing decisions "
        "and the actions performed by each specialized agent during "
        "the assessment."
    )


    for index, entry in enumerate(
        result["audit_trail"],
        start=1
    ):

        with st.expander(
            f"{index}. {entry['agent']}",
            expanded=False
        ):

            st.write(
                f"**Action:** {entry['action']}"
            )

            details = entry.get(
                "details",
                {}
            )

            if details:

                st.write(
                    "**Recorded Details:**"
                )

                st.json(
                    details
                )


    # =====================================================
    # WORKFLOW COMPLETION
    # =====================================================

    st.divider()

    st.subheader("Workflow Completion")

    completed_agents = list(
        dict.fromkeys(
            entry["agent"]
            for entry in result["audit_trail"]
        )
    )

    st.success(
        f"Multi-agent workflow completed successfully "
        f"across {len(completed_agents)} specialized agents."
    )

    st.write(
        " → ".join(
            completed_agents
        )
    )

    st.caption(
        f"{len(result['audit_trail'])} total workflow and "
        f"routing events were recorded in the audit trail."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Intelligent Credit Advisory System | "
    "LangGraph Multi-Agent Educational AI & "
    "Financial Technology Prototype"
)
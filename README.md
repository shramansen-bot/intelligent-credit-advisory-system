# Intelligent Credit Advisory System

An explainable, multi-agent credit assessment and loan advisory prototype built with Python, LangGraph, Streamlit, Retrieval-Augmented Generation (RAG), and Google Gemini.

The system combines deterministic financial calculations and rule-based underwriting with supervisor-routed agent orchestration, semantic policy retrieval, an auditable execution trail, and grounded Generative AI explanations.

> **Disclaimer:** This project is an educational prototype. The customer records, loan products, lending policies, thresholds, and assessment rules used in this repository are synthetic and do not represent the policies of any real bank, NBFC, financial institution, or regulatory authority.

---

## 1. Project Overview

Loan assessment involves multiple responsibilities including customer-data retrieval, affordability analysis, credit-risk evaluation, eligibility checking, lending-policy retrieval, explanation generation, and auditability.

This project demonstrates how these responsibilities can be separated into specialized agents and orchestrated using LangGraph.

The system contains six logical agents:

1. Supervisor Agent
2. Data Retrieval Agent
3. Risk Analysis Agent
4. Underwriting Decision Agent
5. Policy / RAG Agent
6. Explanation Agent

The Supervisor Agent controls the workflow by inspecting the shared application state and selecting the next agent through LangGraph conditional routing.

Core financial calculations and eligibility decisions remain deterministic.

Gemini does not decide whether a customer is eligible for a loan. It is used for semantic embeddings and for generating a grounded natural-language explanation of an already-completed assessment.

---

## 2. Problem Statement and Solution Approach

Credit assessment requires information from multiple sources and involves several distinct analytical responsibilities.

A useful credit advisory system should be able to:

- Retrieve relevant customer and product information
- Evaluate affordability
- Calculate EMI and FOIR
- Analyze risk indicators
- Apply underwriting and eligibility rules
- Retrieve relevant lending-policy information
- Explain the assessment
- Maintain an auditable record of workflow execution

The Intelligent Credit Advisory System addresses these requirements using a supervisor-routed multi-agent architecture.

### Deterministic Decision Layer

Python modules perform:

- EMI calculation
- FOIR calculation
- Credit-score evaluation
- KYC checks
- Income-proof verification
- Employment-type checks
- Fraud-review checks
- Loan-amount validation
- Loan-tenure validation
- Risk scoring
- Eligibility determination

These modules produce the actual assessment result.

### Multi-Agent Orchestration Layer

LangGraph coordinates specialized agents through shared state.

Each agent performs a specific responsibility and returns control to the Supervisor Agent.

The Supervisor inspects the updated state and determines which agent should execute next.

### RAG and Explanation Layer

Relevant sections of a synthetic lending-policy knowledge base are retrieved using Gemini embeddings and cosine similarity.

The retrieved policy context and deterministic assessment are then supplied to the Explanation Agent.

Gemini generates a user-friendly explanation but is explicitly instructed not to modify the calculated decision.

---

## 3. Key Features

### Supervisor-Routed Multi-Agent Workflow

The application uses LangGraph to orchestrate six logical agents.

The Supervisor Agent performs deterministic routing based on the contents of the shared workflow state.

After every specialized agent completes its task, execution returns to the Supervisor.

### Explainable Loan Eligibility

Instead of returning only:

```text
ELIGIBLE
```

or:

```text
NOT ELIGIBLE
```

the system identifies the specific eligibility rules that failed.

Example:

```text
Credit score is below the minimum requirement.
FOIR exceeds the maximum permitted limit.
```

### Affordability Analysis

The deterministic financial engine supports:

- Estimated monthly EMI
- FOIR
- Disposable income
- Maximum affordable EMI

### Risk Assessment

A separate prototype risk model classifies applications as:

```text
LOW
MEDIUM
HIGH
```

Risk classification and eligibility are deliberately kept separate.

### Retrieval-Augmented Generation

Relevant policy sections are retrieved from a synthetic lending-policy knowledge base using semantic embeddings.

The retrieved sections are supplied as context to the Explanation Agent.

### Agent Audit Trail

Every agent records information about its execution.

The audit trail includes:

- Supervisor routing decisions
- Data retrieval activity
- Affordability and risk calculations
- Underwriting results
- Policy retrieval activity
- Explanation generation

A complete successful workflow currently produces 11 execution and routing events across six logical agents.

### Persistent Embedding Cache

Policy embeddings are stored locally after initial generation.

This prevents document embeddings from being regenerated every time the application starts.

The generated cache is excluded from Git and can be rebuilt automatically.

### Interactive Streamlit Interface

Users can:

- Select a synthetic customer
- Select a synthetic loan product
- Enter a requested loan amount
- Select a requested tenure
- Run the complete multi-agent assessment
- View EMI and FOIR
- View eligibility and rejection reasons
- View risk classification and risk factors
- View the AI Credit Advisory
- Inspect retrieved policy context
- Inspect the complete agent execution and audit trail
- View the multi-agent architecture

---

## 4. Multi-Agent System Architecture

The application uses a shared LangGraph state and a Supervisor Agent for conditional routing.

```text
                     START
                       |
                       v
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
```

The specialized agents do not directly decide which agent runs next.

Instead, each specialized agent returns control to the Supervisor.

LangGraph conditional edges then route execution according to the Supervisor's `next_agent` decision.

---

## 5. Agent Responsibilities

### Supervisor Agent

The Supervisor Agent inspects the shared workflow state and determines the next required stage.

Typical routing sequence:

```text
data_retrieval
      |
      v
risk_analysis
      |
      v
underwriting
      |
      v
policy_rag
      |
      v
explanation
      |
      v
end
```

The routing logic is deterministic rather than LLM-controlled.

This makes workflow execution predictable, testable, and auditable.

### Data Retrieval Agent

Responsible for:

- Loading synthetic customer data
- Loading synthetic loan-product data
- Selecting the requested customer
- Selecting the requested loan product
- Recording retrieval information in the audit trail

### Risk Analysis Agent

Responsible for:

- EMI calculation
- FOIR calculation
- Credit-risk scoring
- Risk classification
- Risk-factor identification

The agent reuses the existing deterministic affordability and risk modules.

### Underwriting Decision Agent

Responsible for applying configured eligibility rules.

Checks include:

- Age
- Credit score
- Employment type
- KYC status
- Income-proof verification
- Fraud-review status
- Requested amount
- Requested tenure
- FOIR

The output is either:

```text
ELIGIBLE
```

or:

```text
NOT ELIGIBLE
```

together with applicable reasons.

### Policy / RAG Agent

Responsible for constructing an assessment-specific retrieval query and retrieving relevant policy sections.

The retrieval pipeline uses:

- Gemini embeddings
- Locally cached policy embeddings
- Cosine similarity
- Top-k semantic retrieval

### Explanation Agent

Responsible for producing a natural-language explanation of the completed assessment.

It receives:

- Customer information
- Product information
- EMI
- FOIR
- Eligibility result
- Eligibility reasons
- Risk classification
- Risk factors
- Retrieved policy context

The Explanation Agent is instructed not to override or independently recalculate the deterministic assessment.

---

## 6. Shared LangGraph State

The agents communicate through a shared `LoanAdvisoryState`.

The state contains information such as:

```text
customer_id
product_id
requested_amount
requested_tenure

customer
product

estimated_emi
foir

risk_level
risk_points
risk_factors

decision
reasons

retrieved_policy
advisory

next_agent
audit_trail
```

Each agent reads the fields it requires and returns new information to the shared state.

The Supervisor uses the presence or absence of state fields to determine the next route.

---

## 7. Project Structure

```text
intelligent-credit-advisory-system/
|
|-- app.py
|
|-- agents/
|   |-- __init__.py
|   |-- state.py
|   |-- supervisor_agent.py
|   |-- data_retrieval_agent.py
|   |-- risk_analysis_agent.py
|   |-- underwriting_agent.py
|   |-- policy_agent.py
|   |-- explanation_agent.py
|   `-- workflow.py
|
|-- data/
|   |-- customers.json
|   `-- loan_products.json
|
|-- engine/
|   |-- __init__.py
|   |-- affordability.py
|   |-- assessment.py
|   |-- data_loader.py
|   |-- eligibility.py
|   |-- risk.py
|   |-- ai_advisor.py
|   |-- policy_loader.py
|   `-- policy_retriever.py
|
|-- knowledge_base/
|   `-- lending_policy.txt
|
|-- tests/
|   |-- test_affordability.py
|   |-- test_agents.py
|   |-- test_ai_advisor.py
|   |-- test_assessment.py
|   `-- test_risk.py
|
|-- vector_store/
|   `-- policy_embeddings.json
|
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

`vector_store/policy_embeddings.json` is generated locally and is intentionally excluded from version control.

---

## 8. Technology Stack

- Python
- LangGraph
- Streamlit
- Google Gemini API
- Google GenAI Python SDK
- Gemini Embeddings
- Retrieval-Augmented Generation
- Pytest
- python-dotenv
- JSON
- Git
- GitHub

---

## 9. Prerequisites

Before running the project, ensure the following are installed:

- Python
- Git
- pip
- A Google Gemini API key for live RAG and AI advisory functionality

A Python virtual environment is recommended.

---

## 10. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/shramansen-bot/intelligent-credit-advisory-system.git
```

Move into the project directory:

```bash
cd intelligent-credit-advisory-system
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

> **PowerShell note:** On some Windows systems, the execution policy may prevent `Activate.ps1` from running. The project can still be used without changing the system execution policy.

Install dependencies without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the tests without activation:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run Streamlit without activation:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

#### macOS/Linux

```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

If the virtual environment is activated:

```bash
python -m pip install -r requirements.txt
```

---

## 11. Environment Configuration

The project uses an environment variable for the Gemini API key.

A template is provided:

```text
.env.example
```

Create a new `.env` file in the project root.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with a valid Gemini API key.

### Gemini API Key Requirements

A Gemini API key is required when the application needs to:

- Generate policy-document embeddings
- Generate query embeddings
- Perform semantic policy retrieval
- Generate the AI Credit Advisory

The deterministic Python modules and mocked automated tests do not require a live Gemini API key.

### Security

Never commit the real `.env` file.

The repository's `.gitignore` excludes:

```text
.env
```

Only `.env.example`, containing no real secret, should be committed.

---

## 12. Running the Application

With the virtual environment activated:

```bash
streamlit run app.py
```

If PowerShell activation is unavailable:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit normally starts the application at:

```text
http://localhost:8501
```

Use the address displayed by Streamlit in the terminal.

---

## 13. Running the Multi-Agent Workflow Directly

The LangGraph workflow can also be executed without Streamlit:

```bash
python -m agents.workflow
```

On Windows without virtual-environment activation:

```powershell
.\.venv\Scripts\python.exe -m agents.workflow
```

This displays:

- Customer
- Loan product
- EMI
- FOIR
- Eligibility
- Risk level
- Complete agent audit trail
- AI advisory

This is useful for testing the orchestration layer independently from the UI.

---

## 14. Application Workflow

The user:

1. Selects a synthetic customer.
2. Selects a synthetic loan product.
3. Enters a requested loan amount.
4. Selects a requested tenure.
5. Clicks **Run Multi-Agent Loan Assessment**.

LangGraph then begins the workflow.

The Supervisor first routes execution to the Data Retrieval Agent.

The Data Retrieval Agent loads the selected customer and product and returns control to the Supervisor.

The Supervisor routes to the Risk Analysis Agent, which calculates EMI, FOIR, risk points, risk factors, and risk level.

Control returns to the Supervisor, which routes to the Underwriting Decision Agent.

The Underwriting Decision Agent applies deterministic eligibility rules and returns the decision and reasons.

The Supervisor then routes to the Policy / RAG Agent.

The Policy / RAG Agent retrieves relevant sections from the synthetic lending-policy knowledge base.

The Supervisor routes to the Explanation Agent.

The Explanation Agent generates a grounded natural-language advisory.

Finally, control returns to the Supervisor, which detects that all required outputs are present and routes the graph to `END`.

---

## 15. Eligibility Checks

The prototype evaluates conditions including:

- Customer age
- Credit score
- Employment type
- KYC verification
- Income-proof verification
- Fraud-review flag
- Requested loan amount
- Requested tenure
- FOIR

An applicant is classified as `ELIGIBLE` only when all applicable configured eligibility checks pass.

If one or more checks fail, the system returns:

```text
NOT ELIGIBLE
```

together with the corresponding reasons.

---

## 16. Affordability Calculation

### EMI

The application calculates estimated EMI using the standard reducing-balance loan formula.

The calculation is performed deterministically in Python.

### FOIR

For this prototype:

```text
       Existing Monthly Obligations + Proposed Loan EMI
FOIR = ------------------------------------------------- x 100
                       Monthly Net Income
```

The calculated FOIR is compared with the maximum FOIR configured for the selected synthetic loan product.

---

## 17. Risk Assessment

Risk assessment is intentionally separate from eligibility.

The prototype assigns risk points based on configured credit-score and FOIR thresholds.

The resulting classifications are:

```text
0 points       -> LOW
1 to 2 points  -> MEDIUM
3+ points      -> HIGH
```

A risk classification does not independently determine eligibility.

These thresholds are synthetic and exist only for demonstration.

---

## 18. RAG and Policy Retrieval

The project implements a lightweight Retrieval-Augmented Generation workflow.

The synthetic policy document is stored at:

```text
knowledge_base/lending_policy.txt
```

The retrieval workflow is:

```text
Synthetic Policy Document
          |
          v
 Section-Based Chunking
          |
          v
 Gemini Document Embeddings
          |
          v
 Local Embedding Cache
          |
          v
Assessment-Based Retrieval Query
          |
          v
 Gemini Query Embedding
          |
          v
    Cosine Similarity
          |
          v
 Top Relevant Policy Sections
          |
          v
    Explanation Agent
```

Cosine similarity compares the assessment-specific query embedding with the policy-section embeddings.

The highest-scoring sections are supplied to the Explanation Agent.

### Local Embedding Cache

Generated policy embeddings are stored at:

```text
vector_store/policy_embeddings.json
```

This file is generated automatically and excluded from GitHub through `.gitignore`.

If the cache does not exist, a new embedding index is generated when semantic retrieval is first required.

---

## 19. AI Grounding and Decision Safety

The Generative AI component is not the underwriting decision engine.

The Explanation Agent receives an already-completed deterministic assessment.

Its prompt restricts the model to:

1. The deterministic assessment information.
2. The retrieved synthetic policy context.

The AI is instructed not to:

- Change the eligibility result
- Recalculate or modify EMI
- Recalculate or modify FOIR
- Change risk points
- Change the risk level
- Invent rejection reasons
- Introduce unsupported lending rules
- Introduce unsupported regulatory requirements

This design separates deterministic financial decision logic from Generative AI explanation.

---

## 20. Audit Trail and Explainability

Every agent contributes an audit entry to the shared workflow state.

The Supervisor also records every routing decision.

For a complete workflow, the expected execution sequence is:

```text
1.  Supervisor Agent -> data_retrieval
2.  Data Retrieval Agent
3.  Supervisor Agent -> risk_analysis
4.  Risk Analysis Agent
5.  Supervisor Agent -> underwriting
6.  Underwriting Decision Agent
7.  Supervisor Agent -> policy_rag
8.  Policy / RAG Agent
9.  Supervisor Agent -> explanation
10. Explanation Agent
11. Supervisor Agent -> end
```

The Streamlit interface exposes these events through expandable audit entries.

The current audit trail exists in the workflow state for the active assessment.

It is not currently persisted to an external database.

---

## 21. Lazy Gemini Initialization

Gemini clients are initialized only when Gemini functionality is required.

Importing the deterministic modules does not require a Gemini API key.

This allows deterministic modules and mocked automated tests to operate without connecting to Gemini.

When live embedding or explanation functionality is requested, the application checks for `GEMINI_API_KEY` and initializes the required client.

---

## 22. Testing

The project includes automated tests using `pytest`.

Run:

```bash
python -m pytest
```

On Windows PowerShell systems where virtual-environment activation is blocked:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The test suite covers:

- EMI calculation
- FOIR calculation
- Disposable-income calculation
- Maximum-affordable-EMI calculation
- Eligible applications
- Ineligible applications
- Invalid customer handling
- Invalid product handling
- LOW risk classification
- MEDIUM risk classification
- HIGH risk classification
- AI advisory integration using mocked external components
- Data Retrieval Agent behavior
- Risk Analysis Agent behavior
- Underwriting Decision Agent behavior
- Supervisor initial routing
- Complete supervisor-routed LangGraph execution
- Supervisor routing order
- Multi-agent audit-trail sequencing

External Gemini operations are mocked in the relevant automated workflow tests.

Therefore, the automated test suite can run without a live Gemini request or API key.

Current expected result:

```text
17 passed
```

---

## 23. Synthetic Data

All customer profiles in:

```text
data/customers.json
```

are fictional.

All loan products in:

```text
data/loan_products.json
```

are synthetic.

The policy document:

```text
knowledge_base/lending_policy.txt
```

was created specifically for this educational prototype.

The system must not be interpreted as representing actual lending criteria used by a real financial institution.

---

## 24. External Services

### Google Gemini API

The project uses Gemini services for:

- Text embeddings for semantic policy retrieval
- Grounded natural-language advisory generation

A valid API key must be supplied through:

```text
GEMINI_API_KEY
```

when these live capabilities are used.

External Gemini calls are not required for the deterministic financial modules or mocked automated test suite.

---

## 25. Error Handling

### Gemini Service Availability

If the Gemini generation service is temporarily unavailable because of high demand, the Explanation Agent handles the service error and returns a user-facing message.

For example:

```text
AI advisory is temporarily unavailable because the Gemini service
is experiencing high demand. Please try again later.
```

The deterministic assessment, underwriting decision, risk result, retrieved state, and audit trail remain separate from the availability of the Generative AI explanation service.

### Missing API Key

If Gemini functionality is requested without a configured API key, the application reports that the required environment configuration is missing.

### Invalid Customer or Product

The Data Retrieval Agent validates that the requested customer and loan product exist.

Invalid identifiers result in an explicit error rather than silently continuing with incorrect data.

---

## 26. How the Solution Addresses the Problem

The project separates major credit-advisory responsibilities into specialized components.

| Requirement / Concept | Implementation |
|---|---|
| Multi-agent orchestration | LangGraph |
| Workflow supervision | Deterministic Supervisor Agent |
| Conditional routing | LangGraph conditional edges |
| Customer/product retrieval | Data Retrieval Agent |
| DTI/FOIR-style affordability analysis | Risk Analysis Agent |
| Credit and affordability risk | Risk Analysis Agent |
| Underwriting | Underwriting Decision Agent |
| Policy retrieval | Policy / RAG Agent |
| Semantic search | Gemini Embeddings + cosine similarity |
| Explainability | Explanation Agent |
| Application interface | Streamlit |
| Workflow traceability | In-memory agent audit trail |
| Automated validation | Pytest |

The implementation focuses on a self-contained educational prototype while preserving clear separation between deterministic decision logic and Generative AI explanation.

---

## 27. Known Limitations

- Customer profiles are synthetic.
- Loan products are synthetic.
- Lending-policy rules are synthetic.
- The application is not connected to a real bank or NBFC.
- It is not connected to a real credit bureau.
- It does not perform real KYC verification.
- It does not perform real fraud verification.
- The risk model is intentionally simplified.
- Gemini functionality requires internet access and an external API.
- Gemini responses may be temporarily unavailable because of external service errors or high demand.
- Semantic retrieval may not retrieve every potentially relevant policy section.
- The embedding cache is not automatically invalidated when the policy document changes.
- The application currently uses predefined customer profiles rather than collecting a complete real applicant application.
- The audit trail is held in application/workflow state and is not persisted to a database.
- The project does not currently expose a FastAPI backend.
- The project does not currently use PostgreSQL, pgvector, or Redis.
- The knowledge base contains a synthetic policy rather than live regulatory or institution-specific policy documents.
- The system is not intended for real lending decisions.

---

## 28. Future Enhancements

Possible extensions include:

- Persistent PostgreSQL audit logging
- PostgreSQL system-of-record integration
- pgvector-backed policy retrieval
- Redis-backed workflow/session memory
- FastAPI backend
- Persistent customer/application history
- Automatic embedding-cache invalidation
- Multiple policy documents
- Regulatory-document ingestion
- Expanded policy-retrieval testing
- More detailed affordability analysis
- Additional loan products
- User-entered applicant profiles
- Authentication
- Role-based access
- Persistent workflow observability
- Explainability dashboards
- Cloud deployment
- More advanced retrieval strategies
- Human-review workflow stages
- Additional LangGraph routing and recovery paths

---

## 29. Responsible Use

This application demonstrates how deterministic financial logic, multi-agent orchestration, Retrieval-Augmented Generation, and Generative AI can work together while keeping the core assessment explainable.

The system is intended exclusively for educational and demonstration purposes.

It should not be used to approve, reject, price, or otherwise make real-world lending decisions.

---

## 30. Summary

The Intelligent Credit Advisory System demonstrates an end-to-end educational credit-advisory workflow built around four principles:

**Deterministic Decisions**  
Financial calculations, risk scoring, and eligibility rules are implemented in Python rather than delegated to a language model.

**Specialized Agents**  
Different responsibilities are separated across Supervisor, Data Retrieval, Risk Analysis, Underwriting, Policy/RAG, and Explanation agents.

**Grounded AI**  
Gemini explains the completed assessment using retrieved policy context instead of independently making the lending decision.

**Auditability**  
Supervisor routing decisions and specialized-agent actions are recorded in an inspectable execution trail.

Together, these components provide a transparent prototype of a supervisor-routed, explainable, multi-agent credit advisory system.
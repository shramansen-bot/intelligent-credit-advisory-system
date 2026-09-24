# Intelligent Credit Advisory System

An explainable multi-agent AI prototype for loan eligibility assessment, affordability analysis, risk evaluation, policy retrieval, and grounded credit advisory.

The system combines deterministic financial logic with LangGraph-based multi-agent orchestration, PostgreSQL, pgvector, Redis, FastAPI, Streamlit, and Google Gemini.

> **Educational prototype only.** This project is not connected to a real bank, NBFC, credit bureau, or regulatory authority and must not be used for real-world lending decisions.

---

## 1. Problem Statement

Credit assessment involves multiple responsibilities such as customer-data retrieval, affordability calculation, risk analysis, underwriting, policy interpretation, explanation, and auditability.

This project implements these responsibilities as a supervisor-routed multi-agent system.

The solution is designed to demonstrate:

- Multi-agent credit-advisory orchestration
- Customer and loan-product data retrieval
- EMI and FOIR-based affordability analysis
- Credit-risk classification
- Deterministic underwriting
- Retrieval-Augmented Generation (RAG)
- RBI regulatory-guidance retrieval
- Explainable AI-generated advisory
- PostgreSQL application and audit persistence
- Redis caching
- FastAPI backend services
- Streamlit user interface

The Generative AI component does **not** make the final eligibility decision. Core financial calculations, risk logic, and underwriting remain deterministic.

---

## 2. Key Features

### Multi-Agent LangGraph Workflow

The system contains six logical agents:

1. Supervisor Agent
2. Data Retrieval Agent
3. Risk Analysis Agent
4. Underwriting Decision Agent
5. Policy / RAG Agent
6. Explanation Agent

The Supervisor controls the execution sequence through LangGraph conditional routing.

### Deterministic Financial Assessment

The system calculates:

- Estimated EMI
- FOIR
- Risk points
- Risk level
- Eligibility decision
- Eligibility/rejection reasons

These calculations are implemented in Python rather than delegated to an LLM.

### PostgreSQL System of Record

PostgreSQL stores:

- Customers
- Loan products
- Loan applications
- Multi-agent audit logs
- Policy chunks and embeddings

### pgvector Semantic Retrieval

Policy-document embeddings are stored using PostgreSQL's `pgvector` extension.

The Policy / RAG Agent retrieves relevant policy sections using vector similarity.

### Regulatory-Guidance Knowledge Base

The RAG knowledge base contains:

- Internal synthetic lending policy
- Educational summary of RBI Key Facts Statement guidance
- Educational summary of RBI Fair Practices Code guidance

The RBI knowledge files are concise educational summaries based on public regulatory guidance. They are not represented as verbatim reproductions of RBI documents.

### Gemini Integration

Google Gemini is used for:

- Policy embeddings
- Query embeddings
- Grounded natural-language credit advisory

### Persistent Audit Trail

Every specialist-agent action and Supervisor routing decision is recorded.

A complete standard workflow produces 11 execution/routing events across six logical agents.

Audit events are persisted in PostgreSQL and linked to the corresponding loan application.

### Redis Cache

Completed assessment responses are temporarily cached in Redis by application ID.

Redis is treated as a cache rather than the system of record. If Redis is unavailable, the main assessment workflow can continue using PostgreSQL.

### FastAPI Backend

FastAPI provides the service layer between the Streamlit frontend and the credit-advisory workflow.

### Streamlit Interface

Users can:

- Select a synthetic customer
- Select a synthetic loan product
- Enter requested loan amount
- Enter requested tenure
- Run the multi-agent assessment
- View EMI and FOIR
- View eligibility and risk
- View the AI advisory
- Inspect retrieved policy context
- Inspect the multi-agent audit trail
- View the generated application ID

---

## 3. System Architecture

```text
                     User
                       |
                       v
                Streamlit UI
                       |
                    HTTP
                       |
                       v
                   FastAPI
                       |
                       v
               LangGraph Workflow
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


        PostgreSQL + pgvector
                 ^
                 |
              FastAPI
                 |
                 v
            Redis Cache
```

PostgreSQL acts as the persistent system of record.

pgvector provides vector storage and semantic policy retrieval.

Redis provides temporary caching.

FastAPI exposes the application services.

Streamlit provides the user interface.

---

## 4. Multi-Agent Workflow

The LangGraph workflow follows this route:

```text
START
  |
  v
Supervisor
  |
  v
Data Retrieval
  |
  v
Supervisor
  |
  v
Risk Analysis
  |
  v
Supervisor
  |
  v
Underwriting
  |
  v
Supervisor
  |
  v
Policy / RAG
  |
  v
Supervisor
  |
  v
Explanation
  |
  v
Supervisor
  |
  v
END
```

Each specialist agent returns control to the Supervisor.

The Supervisor examines the shared workflow state and determines the next stage.

The routing sequence is deterministic, making execution predictable, testable, and auditable.

---

## 5. Agent Responsibilities

### Supervisor Agent

Controls workflow routing based on the current LangGraph state.

Typical routing:

```text
data_retrieval
      ↓
risk_analysis
      ↓
underwriting
      ↓
policy_rag
      ↓
explanation
      ↓
end
```

The Supervisor also records routing events in the audit trail.

### Data Retrieval Agent

Retrieves the selected customer and loan product from PostgreSQL.

It provides the data required by downstream agents and records the retrieval operation in the audit trail.

### Risk Analysis Agent

Responsible for:

- EMI calculation
- FOIR calculation
- Risk-point calculation
- Risk classification
- Risk-factor identification

### Underwriting Decision Agent

Applies deterministic eligibility rules.

Checks include:

- Age
- Credit score
- Employment type
- KYC status
- Income-proof verification
- Fraud-review status
- Requested loan amount
- Requested tenure
- FOIR

The resulting decision is:

```text
ELIGIBLE
```

or:

```text
NOT ELIGIBLE
```

with corresponding reasons.

### Policy / RAG Agent

Constructs an assessment-specific semantic query and retrieves relevant policy context.

It retrieves context from both:

- Internal lending policy
- RBI regulatory-guidance knowledge

This prevents regulatory context from being unintentionally crowded out by internal policy results.

### Explanation Agent

Produces the final natural-language credit advisory.

It receives the already-completed deterministic assessment and retrieved policy context.

The Explanation Agent does not independently change:

- Eligibility
- EMI
- FOIR
- Risk points
- Risk level
- Rejection reasons

---

## 6. Affordability Calculation

### EMI

Estimated EMI is calculated using the standard reducing-balance loan formula.

The calculation is deterministic.

### FOIR

This prototype uses:

```text
       Existing Monthly Obligations + Proposed Loan EMI
FOIR = ------------------------------------------------- × 100
                       Monthly Net Income
```

The resulting FOIR is compared with the configured maximum FOIR for the selected loan product.

---

## 7. Risk Assessment

Risk assessment is kept separate from the final eligibility decision.

The prototype assigns risk points using configured credit-score and affordability conditions.

The resulting risk classifications are:

```text
0 points       -> LOW
1 to 2 points  -> MEDIUM
3+ points      -> HIGH
```

These thresholds are synthetic and are used only for this educational prototype.

---

## 8. RAG and Policy Retrieval

The Policy / RAG Agent uses semantic retrieval to find policy context relevant to the current assessment.

```text
Policy Knowledge Files
        |
        v
     Chunking
        |
        v
Gemini Embeddings
        |
        v
PostgreSQL + pgvector
        |
        v
Assessment Query
        |
        v
Gemini Query Embedding
        |
        v
Vector Similarity Search
        |
        v
Relevant Policy Context
        |
        v
Explanation Agent
```

The policy knowledge base contains:

```text
knowledge_base/
|-- lending_policy.txt
`-- rbi/
    |-- rbi_key_facts_statement.txt
    `-- rbi_fair_practices_code.txt
```

The internal policy contains synthetic lending criteria used by the prototype.

The RBI files contain educational summaries of public regulatory guidance and are used as additional grounding context.

Synthetic underwriting thresholds in this project must not be interpreted as RBI-prescribed lending thresholds.

---

## 9. PostgreSQL Database

The project uses the following tables:

### `customers`

Stores synthetic customer profiles.

### `loan_products`

Stores synthetic loan-product definitions and eligibility parameters.

### `loan_applications`

Stores submitted applications and completed assessment results.

### `audit_logs`

Stores Supervisor routing events and specialist-agent activity for each application.

### `policy_chunks`

Stores policy chunks, source metadata, and 768-dimensional Gemini embeddings using pgvector.

---

## 10. Redis

Redis provides temporary assessment caching.

Completed assessments are cached using the generated application ID.

Redis is not the permanent system of record.

If Redis is unavailable, assessment execution and PostgreSQL persistence can continue.

---

## 11. FastAPI

The FastAPI backend exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service information |
| GET | `/health` | API and Redis health |
| GET | `/customers` | Retrieve available customers |
| GET | `/loan-products` | Retrieve available loan products |
| POST | `/assess` | Run and persist a loan assessment |
| GET | `/assessments/{application_id}/cache` | Retrieve a cached assessment |

Interactive FastAPI documentation is available while the server is running at:

```text
http://127.0.0.1:8000/docs
```

---

## 12. Project Structure

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
|-- api/
|   |-- __init__.py
|   `-- main.py
|
|-- data/
|   |-- customers.json
|   `-- loan_products.json
|
|-- engine/
|   |-- __init__.py
|   |-- affordability.py
|   |-- ai_advisor.py
|   |-- assessment.py
|   |-- database.py
|   |-- database_repository.py
|   |-- data_loader.py
|   |-- eligibility.py
|   |-- policy_loader.py
|   |-- policy_retriever.py
|   `-- redis_client.py
|
|-- knowledge_base/
|   |-- lending_policy.txt
|   `-- rbi/
|       |-- rbi_fair_practices_code.txt
|       `-- rbi_key_facts_statement.txt
|
|-- scripts/
|   |-- init_database.py
|   |-- seed_database.py
|   `-- ingest_rbi_policies.py
|
|-- tests/
|   |-- test_affordability.py
|   |-- test_agents.py
|   |-- test_ai_advisor.py
|   |-- test_api.py
|   |-- test_assessment.py
|   `-- test_risk.py
|
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

The local `.venv`, `.env`, Python caches, test caches, and generated vector-store cache are intentionally excluded from version control.

---

## 13. Technology Stack

- Python
- LangGraph
- Google Gemini
- Gemini Embeddings
- PostgreSQL
- pgvector
- Redis
- FastAPI
- Uvicorn
- Streamlit
- HTTPX
- Pytest
- python-dotenv
- Git / GitHub

---

## 14. Prerequisites

Before running the project, install:

- Python
- Git
- PostgreSQL
- pgvector for the installed PostgreSQL server
- Docker Desktop or another accessible Redis installation
- A Google Gemini API key

The project was developed and tested on Windows with Python 3.14.

---

## 15. Installation

Clone the repository:

```bash
git clone https://github.com/shramansen-bot/intelligent-credit-advisory-system.git
```

Enter the project directory:

```bash
cd intelligent-credit-advisory-system
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install the dependencies.

### Windows PowerShell

Activation is optional. Dependencies can be installed directly with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS/Linux

Activate the environment:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -r requirements.txt
```

---

## 16. Environment Configuration

The repository contains:

```text
.env.example
```

Create a local `.env` file based on this template.

Required configuration:

```env
GEMINI_API_KEY=your_gemini_api_key_here

DB_HOST=localhost
DB_PORT=5432
DB_NAME=credit_advisory_db
DB_USER=postgres
DB_PASSWORD=your_postgresql_password_here

REDIS_HOST=localhost
REDIS_PORT=6379

API_BASE_URL=http://127.0.0.1:8000
```

Replace placeholders with the appropriate local values.

Never commit the real `.env` file.

The repository's `.gitignore` excludes `.env`.

---

## 17. PostgreSQL and pgvector Setup

Create a PostgreSQL database named:

```text
credit_advisory_db
```

The PostgreSQL server must have the `pgvector` extension installed before database initialization.

After configuring the database credentials in `.env`, initialize the database.

### Windows

```powershell
.\.venv\Scripts\python.exe -m scripts.init_database
```

### macOS/Linux

```bash
python -m scripts.init_database
```

The initialization script:

- Enables the `vector` extension
- Creates `customers`
- Creates `loan_products`
- Creates `loan_applications`
- Creates `audit_logs`
- Creates `policy_chunks`

---

## 18. Seed the Database

Seed the synthetic customers and loan products.

### Windows

```powershell
.\.venv\Scripts\python.exe -m scripts.seed_database
```

### macOS/Linux

```bash
python -m scripts.seed_database
```

The seeding operation is designed to insert or update the supplied synthetic customer and product records.

---

## 19. Ingest Policy Knowledge

The internal lending policy is indexed by the policy-retrieval layer when required.

To ingest the RBI regulatory-guidance knowledge files into PostgreSQL + pgvector, run:

### Windows

```powershell
.\.venv\Scripts\python.exe -m scripts.ingest_rbi_policies
```

### macOS/Linux

```bash
python -m scripts.ingest_rbi_policies
```

This process:

1. Loads the RBI educational guidance files.
2. Splits them into sections.
3. Generates Gemini embeddings.
4. Stores the chunks and embeddings in PostgreSQL using pgvector.

A valid `GEMINI_API_KEY` and internet connection are required for live embedding generation.

---

## 20. Start Redis

The project uses Redis as a cache.

A simple Docker-based Redis instance can be started with:

```bash
docker run -d --name credit-advisory-redis -p 6379:6379 redis:7-alpine
```

If the container already exists but is stopped:

```bash
docker start credit-advisory-redis
```

Check Redis:

```bash
docker exec credit-advisory-redis redis-cli ping
```

Expected response:

```text
PONG
```

Redis is designed as a non-critical cache. PostgreSQL remains the persistent system of record.

---

## 21. Run FastAPI

FastAPI must be running before the Streamlit frontend performs assessments.

### Windows

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

### macOS/Linux

```bash
python -m uvicorn api.main:app --reload
```

The API is normally available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Keep this terminal running.

---

## 22. Run Streamlit

Open another terminal.

### Windows

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS/Linux

```bash
python -m streamlit run app.py
```

Streamlit normally opens at:

```text
http://localhost:8501
```

The Streamlit application retrieves customers and loan products from FastAPI and submits assessments through the `/assess` endpoint.

---

## 23. Typical Usage

1. Start PostgreSQL.
2. Start Redis.
3. Start FastAPI.
4. Start Streamlit.
5. Select a customer.
6. Select a loan product.
7. Enter the requested loan amount.
8. Enter the requested tenure.
9. Click **Run Multi-Agent Loan Assessment**.

The result displays:

- Application ID
- Estimated EMI
- FOIR
- Eligibility
- Eligibility reasons
- Risk level
- Risk factors
- AI credit advisory
- Retrieved policy context
- Multi-agent audit trail

The application and audit events are persisted in PostgreSQL.

---

## 24. Auditability

A successful standard workflow records the following logical sequence:

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

These events are returned to the UI and persisted in the PostgreSQL `audit_logs` table against the generated application ID.

---

## 25. AI Grounding and Decision Separation

Generative AI is deliberately separated from deterministic underwriting.

Gemini receives the completed assessment and retrieved policy context.

The AI is not responsible for changing:

- EMI
- FOIR
- Eligibility
- Risk points
- Risk level
- Rejection reasons

This design allows natural-language explanation while keeping the core lending logic deterministic and auditable.

If the Gemini generation service is temporarily unavailable, the system can return a fallback advisory message without changing the deterministic assessment result.

---

## 26. Synthetic Data and Responsible Use

The customer records in:

```text
data/customers.json
```

are fictional.

The loan products in:

```text
data/loan_products.json
```

are synthetic.

The internal lending rules in:

```text
knowledge_base/lending_policy.txt
```

are synthetic.

The RBI knowledge files are educational summaries of public regulatory guidance.

The project does not represent actual underwriting criteria used by any bank, NBFC, or regulatory authority.

---

## 27. Testing

The project uses `pytest`.

### Windows

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### macOS/Linux

```bash
python -m pytest
```

The automated tests cover areas including:

- EMI calculation
- FOIR calculation
- Affordability logic
- Risk classification
- Eligibility assessment
- Multi-agent behavior
- Supervisor routing
- LangGraph execution
- AI advisory integration with mocked external components
- FastAPI behavior
- Redis availability/unavailability behavior
- API validation and error handling

Current validated test result:

```text
28 passed
```

The test environment may display dependency deprecation warnings under Python 3.14. These warnings do not represent test failures.

---

## 28. External Services

### Google Gemini

Used for:

- Document embeddings
- Query embeddings
- Grounded natural-language explanation

Configured using:

```text
GEMINI_API_KEY
```

### PostgreSQL

Used as the persistent system of record for application data, audit logs, customers, loan products, and policy chunks.

### pgvector

Used to store and search policy embeddings.

### Redis

Used for temporary caching of completed assessment responses.

---

## 29. Known Limitations

- Customer profiles are synthetic.
- Loan products and internal underwriting rules are synthetic.
- The system is not connected to a real bank or NBFC.
- The system is not connected to a real credit bureau.
- It does not perform real KYC verification.
- It does not perform real fraud verification.
- The risk model is intentionally simplified.
- Gemini functionality depends on an external API and internet connectivity.
- The RBI knowledge files are educational summaries rather than a complete regulatory corpus.
- Semantic retrieval may not retrieve every potentially relevant policy section.
- The prototype is not intended for real lending decisions.

---

## 30. Future Enhancements

Possible future improvements include:

- Integration with real authorized financial-data sources
- Integration with authorized credit-bureau services
- Expanded regulatory knowledge corpus
- Authentication and role-based access
- Human-review workflow stages
- More advanced risk models
- More advanced retrieval and reranking
- Production deployment and observability

These enhancements are outside the scope of the current educational prototype.

---

## 31. Submission Notes

The repository is designed to contain all project source code and setup instructions required to understand and run the prototype.

Sensitive credentials are not stored in the repository.

The real `.env` file is excluded through `.gitignore`.

A safe `.env.example` template is provided for evaluator configuration.

Generated caches, virtual environments, Python cache files, and local development artifacts are excluded from version control.

---

## 32. Summary

The Intelligent Credit Advisory System demonstrates an end-to-end explainable credit-advisory workflow using:

**Deterministic Financial Logic**  
EMI, FOIR, risk analysis, and underwriting are performed using explicit Python rules.

**Multi-Agent Orchestration**  
LangGraph coordinates Supervisor, Data Retrieval, Risk Analysis, Underwriting, Policy/RAG, and Explanation agents.

**Grounded Generative AI**  
Gemini provides semantic embeddings and natural-language explanation using retrieved policy context.

**Persistent Data and Auditability**  
PostgreSQL stores customer/product data, applications, policy vectors, and agent audit events.

**Service-Oriented Architecture**  
FastAPI separates the backend workflow from the Streamlit interface.

**Caching**  
Redis provides temporary assessment caching without replacing PostgreSQL as the system of record.

Together, these components provide a transparent, auditable, supervisor-routed multi-agent prototype for intelligent credit advisory.

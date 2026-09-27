# DataPilot — Autonomous AI Data Analyst

> An agentic AI data analytics platform that turns raw datasets and natural-language questions into validated analysis, SQL, visualizations, insights, recommendations, and downloadable reports.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![NiceGUI](https://img.shields.io/badge/NiceGUI-Frontend-4B8BBE)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?logo=plotly)
![MCP](https://img.shields.io/badge/MCP-Tool_Integration-purple)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)

---

## Overview

**DataPilot** is an autonomous AI-powered analytics platform designed to behave like a data analyst.

Instead of requiring users to manually write SQL, Python, or build charts, DataPilot accepts a dataset and a natural-language analytical question. Its agent workflow determines the appropriate analytical steps, executes them through controlled tools, validates the results, and presents the findings through tables, charts, explanations, recommendations, and reports.

### Example

A user can ask:

> **"Which product categories generate the highest sales, and what factors are associated with better performance?"**

DataPilot can:

- Inspect and profile the dataset
- Understand the analytical objective
- Generate an execution plan
- Generate and execute SQL/Python analysis
- Create relevant visualizations
- Validate analytical outputs
- Reflect and retry when execution fails
- Produce evidence-based insights
- Generate business recommendations

---

# Key Features

### 🤖 Agentic Analytical Workflow

Built with **LangGraph**, DataPilot separates analytical responsibilities across specialized nodes including:

- Planner
- Supervisor
- Schema Profiler
- Python Analyst
- Code Generator
- Analysis Engine
- Validator
- Reflection
- Visualization Generator
- Visualization Executor
- Report Agent

### 🔍 Automated Data Understanding

The system profiles uploaded data before analysis, helping the agent understand:

- Columns and data types
- Dataset structure
- Missing values
- Available analytical fields
- Relevant dimensions and measures

### 🧮 SQL & Python Analysis

DataPilot can select appropriate analytical approaches and generate executable SQL or Python-based analysis depending on the task.

### 📊 Automated Visualization

The platform generates analytical visualizations using **Plotly**, including charts such as:

- Bar charts
- Line charts
- Scatter plots
- Comparative visualizations

### ✅ Validation & Reflection

Generated analytical work is not simply returned directly.

DataPilot includes validation and reflection stages that help identify:

- Invalid SQL
- Incorrect analytical outputs
- Visualization problems
- Execution failures
- Unsupported conclusions

When appropriate, the workflow can retry failed analytical steps.

### 📑 Explainable Reports

Results are presented with supporting tables, visualizations, analytical facts, insights, and recommendations rather than returning only raw model-generated text.

### 🔌 MCP-Based Data Access

DataPilot uses **Model Context Protocol (MCP)** components to provide structured access to analytical data and tools.

### 🐳 Dockerized Architecture

The complete application runs through Docker Compose with separate containers for:

- FastAPI backend
- NiceGUI frontend
- PostgreSQL database

---

# Demo & Interface

### Main Interface

![DataPilot Interface](screenshots/FrontUI.png)

### Data Analysis

![Analysis](screenshots/Analysis1.png)

### Analytical Visualization

![Analysis Chart](screenshots/Analysis2barchart.png)

### SQL Generation

![SQL Query](screenshots/SQLquery.png)

### Validation

![Validation](screenshots/Validation.png)

### Business Recommendations

![Business Recommendations](screenshots/Buisnessrecommendation.png)

---

# System Architecture

```text
                         ┌──────────────────────┐
                         │      User Query      │
                         │ Natural Language     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    NiceGUI Frontend  │
                         │   UI + Visualization │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   LangGraph Agent    │
                         │      Workflow        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
       Schema Profiling        Planning              Analysis
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ SQL / Python / MCP   │
                         │     Execution        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Validation /         │
                         │ Reflection / Retry   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Charts + Insights +  │
                         │ Recommendations      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Final Report    │
                         └──────────────────────┘

                         PostgreSQL
                              ▲
                              │
                         MCP / Data
                         Access Layer
```
![System Architecture](screenshots/System_Architecture.png)
---

# Analytical Workflow

```text
Dataset
   ↓
Schema Profiling
   ↓
Understand User Question
   ↓
Planning
   ↓
Generate SQL / Python Analysis
   ↓
Execute
   ↓
Validate Results
   ↓
Reflect / Retry if Required
   ↓
Generate Visualizations
   ↓
Extract Analytical Facts
   ↓
Generate Insights
   ↓
Generate Recommendations
   ↓
Present Final Analysis
```

The goal is to make the analytical process **structured, traceable, and less dependent on a single LLM response**.

---

# Tech Stack

| Layer | Technologies |
|---|---|
| Language | Python 3.10+ |
| Frontend | NiceGUI |
| Backend | FastAPI, Uvicorn |
| Agent Orchestration | LangGraph, LangChain |
| LLM Providers | Groq, Google Gemini |
| Database | PostgreSQL 17 |
| Data Analysis | Pandas, NumPy, DuckDB |
| Visualization | Plotly |
| Tool Integration | MCP / FastMCP |
| Validation | SQL/Python validation components |
| Reporting | ReportLab |
| Deployment | Docker, Docker Compose |
| Testing | Pytest |

---

# Docker Architecture

DataPilot is designed as a multi-container application:

```text
┌─────────────────────────────────────────────┐
│              Docker Compose                 │
│                                             │
│  ┌────────────────┐                         │
│  │ NiceGUI        │ :8501                   │
│  │ Frontend       │                         │
│  └───────┬────────┘                         │
│          │                                  │
│          ▼                                  │
│  ┌────────────────┐                         │
│  │ FastAPI        │ :8000                   │
│  │ Backend        │                         │
│  └───────┬────────┘                         │
│          │                                  │
│          ▼                                  │
│  ┌────────────────┐                         │
│  │ PostgreSQL 17  │ :5432                   │
│  │ Persistent DB  │                         │
│  └────────────────┘                         │
│                                             │
└─────────────────────────────────────────────┘
```

The frontend communicates with the backend using the Docker service name:

```text
http://backend:8000
```

while users access the application through:

```text
http://localhost:8501
```

---

# Quickstart

## 1. Clone the repository

```bash
git clone https://github.com/aryanfarswan/DataPilot---Automonous-Data-Analyst-Agent
cd DataPilot
```

## 2. Configure environment variables

Create a `.env` file containing the required API credentials and database configuration.

Example:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

GEMINI_FALLBACK_MODEL=gemini-3.8-flash

DATABASE_URL=postgresql://postgres:postgres@postgres:5432/autonomous_data_analyst
```

> Never commit API keys or other secrets to GitHub.

## 3. Run with Docker

```bash
docker compose build
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

## 4. Open the application

Frontend:

```text
http://localhost:8501
```

Backend API documentation:

```text
http://localhost:8000/docs
```

Stop the application:

```bash
docker compose down
```

---

# Local Development

### Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI:

```bash
uvicorn backend.main:app --reload
```

### Frontend

Install frontend dependencies:

```bash
pip install -r NiceGUI_frontend/requirements.txt
```

Run NiceGUI:

```bash
python NiceGUI_frontend/main.py
```

For local development, the frontend can communicate with the backend through:

```env
BACKEND_URL=http://localhost:8000
```

---

# Repository Structure

```text
DataPilot/
│
├── backend/
│   ├── agents/
│   │   ├── nodes/
│   │   ├── graph.py
│   │   ├── sandbox.py
│   │   ├── schemas.py
│   │   └── state.py
│   │
│   ├── database/
│   ├── mcp/
│   ├── mcp_server/
│   ├── services/
│   │   ├── python/
│   │   ├── reporting/
│   │   ├── sql/
│   │   └── visualization/
│   │
│   ├── tests/
│   ├── config.py
│   └── main.py
│
├── NiceGUI_frontend/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── state/
│   ├── styles/
│   ├── config.py
│   └── main.py
│
├── screenshots/
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
└── README.md
```

---

# Testing & Validation

DataPilot includes automated tests covering important components of the analytical workflow.

Current test areas include:

```text
backend/tests/
├── test_analytical_pipeline.py
├── test_components.py
├── test_fallback.py
├── test_mcp.py
├── test_provider_errors.py
├── test_report_semantics.py
├── test_sql_quality_validator.py
└── test_visualization_integration.py
```

The project has also been manually tested using a retail/Blinkit dataset for:

- Dataset profiling
- Natural-language analytical questions
- SQL generation
- Category-level analysis
- Sales analysis
- Visualization generation
- Analytical validation
- Business recommendations

Example query:

> **"Generate a SQL query to calculate total sales, average sales, and number of items for each Item Type, rank the Item Types by total sales, and return the top 5 categories."**

---

# Example Analytical Questions

DataPilot is designed to handle questions such as:

### Sales Analysis

> Which product categories generate the highest sales?

### Comparative Analysis

> How does sales performance differ across outlet types?

### Relationship Analysis

> Is Item Visibility associated with Item Sales?

### Business Analysis

> What factors are associated with better-performing outlets?

### SQL Generation

> Generate a SQL query showing the top five product categories by total sales.

The system determines the analytical workflow rather than requiring the user to manually specify SQL, Python, or visualization logic.

---

# Engineering Challenges

### Reliable LLM-Generated Analysis

LLM-generated code can contain syntax, execution, or analytical errors. DataPilot therefore separates generation from execution and adds validation and reflection stages.

### Analytical Grounding

Recommendations should be connected to computed results rather than generated independently. The reporting workflow uses analytical facts and outputs as the basis for downstream insights.

### Tool-Oriented Agent Design

Instead of relying on one large prompt, the system separates responsibilities across specialized agent nodes.

### Containerized Multi-Service Deployment

The application requires coordinated communication between the frontend, backend, and PostgreSQL services. Docker Compose provides a reproducible environment for these components.

---

# Current Limitations

- Analytical quality still depends partly on the underlying LLM.
- Complex or ambiguous business questions may require user clarification.
- Large datasets can increase execution time and resource requirements.
- Generated recommendations should be reviewed before being used for high-impact business decisions.
- The application currently focuses on structured/tabular analytics.

---

# Future Enhancements

Potential future improvements include:

- Cloud deployment
- Authentication and multi-user workspaces
- More data source connectors
- Larger-scale distributed execution
- Additional statistical and machine-learning capabilities
- Advanced analytical lineage and provenance
- Improved evaluation benchmarks
- More specialized domain-specific analytical agents

---

# License

MIT License.

---

# Author

**Aryan Farswan**

B.Tech — Artificial Intelligence & Machine Learning

Interested in **Data Science, Machine Learning, Generative AI, Agentic AI, and Data Analytics**.

- [Github](https://github.com/aryanfarswan)
- [LinkedIn](https://www.linkedin.com/in/aryanfarswanofficial/)

---

## DataPilot in One Line

> **DataPilot turns natural-language questions into structured, validated, explainable data analysis.**

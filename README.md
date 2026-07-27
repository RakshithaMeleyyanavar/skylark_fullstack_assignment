# Monday.com Conversational Business Intelligence Agent

An AI-powered Business Intelligence Agent that enables founders and business leaders to ask natural language questions about their Monday.com business data and receive real-time insights.

## Project Overview

This application connects directly to Monday.com using the GraphQL API (Read-Only) and provides conversational business intelligence across multiple boards without relying on locally stored CSV data.

The system automatically:
- Fetches live data from Monday.com
- Cleans and normalizes inconsistent business records
- Handles missing and incomplete values gracefully
- Performs cross-board analytics
- Answers founder-level business questions using an AI agent
- Generates leadership-ready insights and summaries

---

## Features

### Live Monday.com Integration
- Read-only GraphQL API integration
- Dynamic live data fetching
- No hardcoded datasets
- Automatic authentication

### Data Cleaning & Resilience
- Missing value handling
- Date normalization
- Text normalization
- Duplicate detection
- Data quality reporting

### Conversational BI
Example questions:

- How is our pipeline performing?
- Show won deals this quarter.
- Which sector has the highest revenue?
- Compare deal conversion by owner.
- Which work orders are delayed?
- Show cross-board owner performance.
- What data quality issues exist?

### Cross Board Analytics
Combines

- Deal Funnel Board
- Work Order Tracker Board

to generate unified business insights.

### Leadership Dashboard

Provides

- Pipeline health
- Revenue summary
- Data quality metrics
- Cross-board comparisons
- Operational insights

---

## Architecture

```
User
   │
   ▼
Streamlit Web UI
   │
   ▼
AI Agent
   │
   ├──────────────┐
   ▼              ▼
Business Logic   Query Understanding
   │
   ▼
Monday GraphQL Client
   │
   ▼
Monday.com API
   │
   ▼
Deal Funnel Board
Work Order Board
```

---

## Project Structure

```
.
├── app.py
├── agent.py
├── monday_client.py
├── tools.py
├── join_logic.py
├── cache.py
├── data_cleaning.py
├── data_quality.py
├── leadership_summary.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Technology Stack

- Python 3.x
- Streamlit
- Monday.com GraphQL API
- Requests
- Pandas
- Python Dotenv

---

## Installation

Clone repository

```bash
git clone https://github.com/RakshithaMeleyyanavar/skylark_fullstack_assignment.git
cd skylark_fullstack_assignment
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file

```env
MONDAY_API_TOKEN=YOUR_TOKEN
DEAL_FUNNEL_BOARD_ID=YOUR_BOARD_ID
WORK_ORDER_BOARD_ID=YOUR_BOARD_ID
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

---

## Run Application

```bash
streamlit run app.py
```

Application runs at

```
http://localhost:8501
```

---

## Read-Only Security

This project intentionally performs only GraphQL **query** operations.

The application:

- Never performs mutations
- Never edits Monday.com data
- Never deletes records
- Never modifies business information

Monday.com remains the single source of truth.

---

## Data Quality Handling

The agent automatically handles

- Missing values
- Empty records
- Inconsistent dates
- Mixed text formatting
- Duplicate entries
- Invalid values

while informing users about potential data quality issues.

---

## Leadership Insights

The system generates:

- Revenue summaries
- Pipeline health
- Win/Loss analysis
- Owner performance
- Sector performance
- Cross-board metrics
- Data completeness reports

---

## Design Decisions

- Monday.com used as the only source of truth.
- Read-only GraphQL architecture for safety.
- In-memory caching for improved performance.
- Modular architecture separating API, business logic, data cleaning, and UI.
- Conversational interface designed for founder-level business questions.

---

## Future Improvements

- Multi-board support
- Authentication & user roles
- Dashboard export (PDF/Excel)
- Historical trend analysis
- Scheduled leadership reports
- Advanced AI reasoning with Retrieval-Augmented Generation (RAG)

---

## Assignment Mapping

| Requirement | Status |
|------------|--------|
| Monday.com Integration | ✅ |
| Read-only API | ✅ |
| Live Data Fetching | ✅ |
| Data Cleaning | ✅ |
| Missing Value Handling | ✅ |
| Cross-board Analytics | ✅ |
| Conversational Interface | ✅ |
| Leadership Insights | ✅ |
| Hosted Prototype | ✅ |
| Source Code | ✅ |
| README | ✅ |

---

## Author

**Rakshitha Meleyyanavar**

BE Computer Science Engineering

BNM Institute of Technology

GitHub:
https://github.com/RakshithaMeleyyanavar

# 🚀 Monday.com Conversational Business Intelligence Agent

> AI-powered Business Intelligence Agent for founders and business leaders to query Monday.com data using natural language and receive real-time business insights.

---

## 📌 Project Overview

This project is a conversational Business Intelligence (BI) Agent that connects directly to **Monday.com** via the **GraphQL API (Read-Only)** and answers founder-level business questions using live organizational data.

Instead of relying on manually exported CSV or Excel files, the application dynamically fetches data from Monday.com boards, cleans inconsistent records, performs cross-board analysis, and generates actionable business insights.

---

## 🎥 Demo Video

📹 **Working Demo:**  
https://drive.google.com/file/d/1p2F4PB9Y_A26-F5kcDcZmhCgQT0MxTA0/view?usp=drive_link

The demo showcases:

- ✅ Live Monday.com integration
- ✅ Conversational AI interface
- ✅ Cross-board analytics
- ✅ Data cleaning & resilience
- ✅ Leadership dashboard
- ✅ Business intelligence workflow
- ✅ End-to-end application demonstration

---

# ✨ Features

## 🔗 Live Monday.com Integration

- Read-only GraphQL API
- Live data fetching
- Dynamic board querying
- Secure authentication
- No hardcoded CSV files

---

## 🧹 Data Cleaning & Resilience

The application automatically handles:

- Missing values
- Null fields
- Duplicate records
- Date normalization
- Text normalization
- Inconsistent naming
- Data quality reporting

---

## 💬 Conversational Business Intelligence

Example business questions:

- How is our sales pipeline performing?
- Show won deals this quarter.
- Which sector generated the highest revenue?
- Compare conversion rates by owner.
- Which work orders are delayed?
- Show owner-wise performance.
- What are the current data quality issues?

---

## 📊 Cross Board Analytics

The system combines information from:

- 📁 Deal Funnel Board
- 📁 Work Order Tracker Board

to generate unified business insights.

---

## 📈 Leadership Dashboard

Provides:

- Revenue Summary
- Pipeline Health
- Sector Performance
- Win / Loss Analysis
- Owner Performance
- Operational Metrics
- Cross-board Insights
- Data Quality Metrics

---

# 🏗️ System Architecture

```text
                    User
                      │
                      ▼
            Streamlit Web Application
                      │
                      ▼
             Conversational AI Agent
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
 Business Logic              Query Understanding
        │
        ▼
   Monday GraphQL Client
        │
        ▼
     Monday.com API
        │
 ┌──────┴────────┐
 ▼               ▼
Deal Funnel   Work Orders
```

---

# 📂 Project Structure

```text
.
├── app.py
├── agent.py
├── monday_client.py
├── tools.py
├── cache.py
├── join_logic.py
├── data_cleaning.py
├── data_quality.py
├── leadership_summary.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# ⚙️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Frontend | Streamlit |
| API | Monday.com GraphQL API |
| AI | Google Gemini |
| HTTP | Requests |
| Data Processing | Pandas |
| Environment | Python Dotenv |
| Caching | In-Memory TTL Cache |

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/RakshithaMeleyyanavar/skylark_fullstack_assignment.git

cd skylark_fullstack_assignment
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file.

```env
MONDAY_API_TOKEN=YOUR_MONDAY_API_TOKEN

DEAL_FUNNEL_BOARD_ID=YOUR_DEAL_BOARD_ID

WORK_ORDER_BOARD_ID=YOUR_WORK_ORDER_BOARD_ID

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

---

## Run the Application

```bash
streamlit run app.py
```

Application will be available at

```
http://localhost:8501
```

---

# 🔒 Security

This application is intentionally designed as a **Read-Only Business Intelligence Agent**.

The system:

- ✅ Executes GraphQL **Query** operations only
- ❌ Never performs GraphQL Mutations
- ❌ Never edits Monday.com data
- ❌ Never deletes records
- ❌ Never modifies business information

Monday.com remains the **single source of truth**.

---

# 🧠 Data Quality Handling

The application automatically detects and handles:

- Missing values
- Empty records
- Duplicate entries
- Invalid data
- Mixed date formats
- Text inconsistencies
- Incomplete information

Whenever issues are detected, they are communicated clearly to the user.

---

# 📊 Business Intelligence Outputs

The AI agent generates:

- Revenue Reports
- Pipeline Health
- Win / Loss Analysis
- Sector Performance
- Owner Performance
- Cross-board Analytics
- Leadership Updates
- Data Completeness Reports

---

# 🎯 Design Decisions

- Monday.com serves as the single source of truth.
- Read-only GraphQL architecture ensures data safety.
- Live API integration eliminates stale local datasets.
- Modular architecture improves maintainability.
- In-memory caching reduces unnecessary API calls.
- Conversational interface designed for founder-level decision making.

---

# 🔮 Future Enhancements

- Authentication & User Roles
- Multi-board Support
- Dashboard Export (PDF / Excel)
- Historical Trend Analysis
- Scheduled Leadership Reports
- RAG-based Knowledge Retrieval
- AI Recommendations & Forecasting

---

# ✅ Assignment Requirement Mapping

| Requirement | Status |
|------------|:------:|
| Monday.com Integration | ✅ |
| Read-only API | ✅ |
| Live Data Fetching | ✅ |
| Data Cleaning | ✅ |
| Missing Value Handling | ✅ |
| Cross-board Analytics | ✅ |
| Conversational Interface | ✅ |
| Leadership Dashboard | ✅ |
| Hosted Prototype | ✅ |
| Source Code | ✅ |
| README Documentation | ✅ |
| Demo Video | ✅ |

---

# 👩‍💻 Author

**Rakshitha Meleyyanavar**

Bachelor of Engineering (Computer Science)

BNM Institute of Technology

📧 GitHub Repository

https://github.com/RakshithaMeleyyanavar/skylark_fullstack_assignment

---

## ⭐ Thank You

Thank you for reviewing this submission.

This project was developed as part of the **Skylark Drones Full Stack Technical Assignment**, demonstrating live Monday.com integration, conversational AI, data resilience, cross-board analytics, and founder-focused business intelligence.

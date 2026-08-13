# Architecture & System Design

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         USER INTERFACES                                     │
│  ┌──────────────────┬──────────────────────────────────┐   │
│  │   CLI Mode       │    Streamlit Web UI              │   │
│  │  (index.py)      │      (app.py)                    │   │
│  └────────┬─────────┴──────────────────┬───────────────┘   │
└───────────┼────────────────────────────┼──────────────────┘
            │                            │
            └────────────┬───────────────┘
                         │
            ┌────────────▼──────────────┐
            │  AGENT LAYER             │
            │  (agent.py)              │
            │  • Query Processing      │
            │  • Tool Selection        │
            │  • Response Generation   │
            └────────────┬──────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌─────────────────┐  ┌──────────────┐  ┌────────────────┐
│ TOOLS LAYER     │  │ RAG SYSTEM   │  │ CONFIG         │
│ (tools.py)      │  │ (rag_system) │  │ (config.py)    │
│                 │  │              │  │                │
│ • fetch_order   │  │ • Policy     │  │ • Settings     │
│ • get_orders    │  │   Retrieval  │  │ • Validation   │
│ • verify_order  │  │ • FAISS      │  │                │
│ • policy_lookup │  │   Vector DB  │  │                │
│ • refund        │  │ • Embeddings │  │                │
│ • escalate      │  │              │  │                │
└────────┬────────┘  └──────────────┘  └────────────────┘
         │
         ▼
    ┌──────────────────┐
    │ DATABASE LAYER   │
    │ (database.py)    │
    │                  │
    │ ┌──────────────┐ │
    │ │ Orders Table │ │
    │ └──────────────┘ │ 
    │                  │
    └────────┬─────────┘
             │
             ▼
  
```

## 📊 Data Flow

### 1. **Query Processing Flow**
```
User Query
    │
    ▼
Agent Receives Query
    │
    ▼
Context Analysis (RAG)
    │
    ▼
Tool Selection Heuristics
    │
    ├─ Order Keywords? → fetch_order_status
    ├─ Policy Keywords? → search_company_policy
    ├─ Refund Keywords? → initiate_refund
    └─ Escalation Keywords? → escalate_issue
    │
    ▼
Execute Tools (Database Queries)
    │
    ▼
Format Tool Results
    │
    ▼
Generate Response (LLM)
    │
    ▼
Return to User
```

### 2. **RAG Workflow**
```
Customer Query
    │
    ▼
FAISS Similarity Search
    │
    ▼
Retrieve Top 3 Policies
    │
    ▼
Format as Context
    │
    ▼
Send to LLM with Context
    │
    ▼
Generate Policy-Aware Response
```

### 3. **Order Tracking Workflow**
```
"Track order ORD001"
    │
    ▼
Extract Order ID
    │
    ▼
fetch_order_status() Tool
    │
    ▼
Database Query
    │
    ▼
Format Order Details
    │
    ▼
Include in LLM Prompt
    │
    ▼
Generate Formatted Response
```


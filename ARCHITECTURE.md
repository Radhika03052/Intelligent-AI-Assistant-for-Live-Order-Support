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
    │ ┌──────────────┐ │
    │ │ Policies Tbl │ │
    │ └──────────────┘ │
    │ ┌──────────────┐ │
    │ │ Inquiries Tbl│ │
    │ └──────────────┘ │
    └────────┬─────────┘
             │
             ▼
   ┌──────────────────┐
   │ SQLite Database  │
   │ (customer_       │
   │  support.db)     │
   └──────────────────┘
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

## 🔧 Component Details

### Agent (agent.py)
**Responsibility**: Orchestrate the entire support workflow

**Key Methods**:
- `process_query()` - Main entry point for query processing
- `_extract_tool_calls()` - Identify which tools to use
- `_format_tool_results()` - Prepare tool outputs for LLM
- `_create_system_prompt()` - Define agent behavior

**Decision Logic**:
```python
if "order" in query:
    use fetch_order_status()
elif "policy" in query:
    use search_company_policy()
elif "refund" in query:
    use initiate_refund()
else:
    use RAG + general response
```

### Tools (tools.py)
**Responsibility**: Execute specific operations on data

**Tool Categories**:

**Order Tools**:
- `fetch_order_status(order_id)` - Get order details
- `get_customer_orders(email)` - List customer orders
- `verify_order_ownership(order_id, email)` - Security check
- `initiate_refund(order_id, reason)` - Process refund

**Policy Tools**:
- `search_company_policy(category)` - Find policy by category
- `get_all_company_policies()` - Get all policies

**Support Tools**:
- `escalate_issue(order_id, description)` - Create escalation ticket

### RAG System (rag_system.py)
**Responsibility**: Policy retrieval and context generation

**Architecture**:
1. **Document Loading** - Extract policies from database
2. **Chunking** - Split into 200-char chunks
3. **Embedding** - Convert to vectors (Google Embeddings)
4. **Indexing** - Store in FAISS
5. **Retrieval** - Find top 3 similar policies
6. **Formatting** - Prepare context for LLM

**Vector Store**: FAISS (Facebook AI Similarity Search)
- Fast similarity search
- Persistent storage (policy_faiss_index/)
- Supports semantic search on policies

### Database (database.py)
**Responsibility**: Data persistence and queries

**Tables**:

**Orders**:
```sql
order_id (PK) | customer_name | customer_email | status | 
total_amount | tracking_number | estimated_arrival | items
```

**Policies**:
```sql
policy_id (PK) | title | content | category | created_at
```

**Inquiries** (Audit Log):
```sql
inquiry_id (PK) | customer_id | query | response | 
timestamp | resolved
```

## 🔐 Security Considerations

### Authentication
- ✅ Order ownership verification before sharing details
- ✅ Customer email validation
- ✅ API key management via environment variables

### Data Protection
- ✅ SQLite database (local storage)
- ✅ No sensitive data logged
- ✅ Secure API key handling

### Tool Execution Safety
- ✅ Input validation on all parameters
- ✅ Limited tool set with specific purposes
- ✅ Tool execution tracked in logs

## 📈 Performance Characteristics

### Response Time Breakdown
- Query Reception: ~100ms
- Tool Selection: ~50ms
- Database Query: ~100ms (indexed)
- RAG Retrieval: ~300ms (FAISS)
- LLM Response: ~1500ms (API call)
- **Total**: ~2-3 seconds

### Scalability
- **Concurrent Users**: Limited by API rate limits
- **Database Size**: Can handle millions of orders
- **Policy Documents**: Supports unlimited policies
- **Chat History**: Keeps last 4 messages in memory

## 🔄 Integration Points

### External APIs
1. **Google Generative AI**
   - Endpoint: api.google.ai
   - Model: gemini-2.5-flash
   - Used for: LLM responses, embeddings

### Local Resources
1. **SQLite Database**
   - File: customer_support.db
   - Size: ~1MB (with sample data)

2. **FAISS Index**
   - Directory: policy_faiss_index/
   - Size: ~500KB
   - Cached for performance

## 🎯 Extension Points

### Adding New Tools
1. Define function in `tools.py`
2. Add to `AVAILABLE_TOOLS` list
3. Update `_extract_tool_calls()` in `agent.py`

### Adding New Policies
1. Insert into database via `add_sample_policies()`
2. FAISS index updates automatically
3. RAG system includes new policies

### Customizing Agent Behavior
1. Edit `_create_system_prompt()` in `agent.py`
2. Adjust `_extract_tool_calls()` logic
3. Modify LLM temperature and model

## 🚀 Deployment Architecture

### Development
```
Local Machine
├── Python Virtual Env
├── SQLite Database
├── FAISS Index (local)
└── Google API Key (env var)
```

### Production
```
Server/Cloud
├── Containerized (Docker)
├── SQLite → PostgreSQL
├── FAISS Index → Vector DB (Pinecone)
├── Secrets Management → Vault
└── Monitoring → Datadog
```

## 📊 State Management

### Session State (Streamlit)
```python
st.session_state = {
    "agent": CustomerSupportAgent,
    "messages": [],  # Chat history
    "customer_email": str,
    "rag_system": PolicyRAG,
}
```

### Agent State
```python
agent.conversation_history = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
]
```

### Tool Execution State
```python
result = {
    "tools_used": [tool_names],
    "tool_results": [{
        "tool": name,
        "input": params,
        "output": result,
    }],
}
```

## 🔌 Configuration Hierarchy

1. **Defaults** (code)
2. **Environment Variables** (overrides defaults)
3. **`.env` file** (if exists, overrides env vars)
4. **Runtime Config** (agent can change)

## 📝 Logging & Monitoring

### Inquiry Logging
Every query is logged:
```python
log_inquiry(
    customer_id,
    query_text,
    response_text,
    timestamp
)
```

### Tool Execution Tracking
```python
{
    "tool": "fetch_order_status",
    "timestamp": "2025-08-12T10:30:00",
    "input": {"order_id": "ORD001"},
    "output": {status: "success"},
    "execution_time": 150,
}
```

## 🧪 Testing Strategy

### Unit Tests
- Tool functions in isolation
- Database operations
- RAG retrieval

### Integration Tests
- Agent → Tools → Database
- Agent → RAG → LLM

### E2E Tests
- CLI workflow
- Streamlit UI workflow
- Sample queries

---

**System designed for extensibility, maintainability, and performance.** 🚀

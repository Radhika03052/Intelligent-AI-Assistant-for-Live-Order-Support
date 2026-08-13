"""
Configuration settings for the AI Customer Support Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AQ.Ab8RN6LgiObW1xSvVL_4kCBKZDBfFBn-qk6LTzjPpGFEtedo1g")

# Model Configuration
EMBEDDING_MODEL = "gemini-embedding-2-preview"
LLM_MODEL = "gemini-2.5-flash"

# Vector Database Configuration
VECTOR_CHUNK_SIZE = 200
VECTOR_CHUNK_OVERLAP = 20
VECTOR_SEARCH_K = 5

# Database Configuration
DATABASE_FILE = "orders.db"
POLICIES_FILE = "company_policies.txt"

# RAG Configuration
POLICY_RETRIEVAL_TOP_K = 5

# UI Configuration
STREAMLIT_THEME = "light"
STREAMLIT_PAGE_TITLE = "AI Customer Support Bot"
STREAMLIT_PAGE_ICON = "🤖"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "bot_logs.log"

# Support Contact Information
SUPPORT_EMAIL = "support@company.com"
SUPPORT_PHONE = "1-800-SUPPORT"
SUPPORT_HOURS = "24/7 (Phone: Mon-Fri 9AM-5PM EST)"

# Tool Configuration
ENABLE_TRACKING = True
ENABLE_REFUNDS = True
ENABLE_ORDER_HISTORY = True
ENABLE_POLICY_LOOKUP = True

# Refund Policy
REFUND_WINDOW_DAYS = 30
REFUND_PROCESSING_DAYS = "5-7"

# Shipping Configuration
SHIPPING_OPTIONS = {
    "standard": {"days": "5-7", "cost": 0, "min_order": 50},
    "express": {"days": "2-3", "cost": 9.99, "min_order": 0},
    "overnight": {"days": "1", "cost": 24.99, "min_order": 0},
}

# Sample test customers
TEST_CUSTOMERS = [
    {"email": "john@example.com", "name": "John Smith"},
    {"email": "sarah@example.com", "name": "Sarah Johnson"},
    {"email": "mike@example.com", "name": "Mike Chen"},
    {"email": "emma@example.com", "name": "Emma Davis"},
    {"email": "alex@example.com", "name": "Alex Wilson"},
]

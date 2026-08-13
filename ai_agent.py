import re
import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load configuration
load_dotenv()

DATABASE_FILE = "orders.db"
POLICIES_FILE = "company_policies.txt"
EMBEDDINGS_STORAGE_DIR = "pdf_embeddings"

# Pre-packaged natural language policy rewrites (in own words, no bullet points, preserved meaning)
LOCAL_POLICY_REWRITES = {
    "SHIPPING POLICIES": (
        "We offer standard shipping which takes five to seven business days, express shipping in two to three business days, "
        "and next-day overnight delivery. Shipping is available throughout Canada and all fifty US states, with free standard "
        "shipping provided for any orders exceeding fifty dollars."
    ),
    "RETURN AND REFUND POLICY": (
        "Customers can return most items with no questions asked within a thirty-day window from the purchase date, "
        "provided the items are unused and kept in their original packaging. We process refunds within five to seven business "
        "days after receiving the returned items, and return shipping is complimentary for orders valued over one hundred dollars."
    ),
    "CANCELLATION POLICY": (
        "Orders can be cancelled for a full refund within twenty-four hours of purchase. If the order is still in the "
        "processing stage, it can be cancelled subject to a five percent fee. However, once an order is shipped or out "
        "for delivery, it cannot be cancelled; in these cases, you must either refuse the delivery or follow our return policy. "
        "To initiate a cancellation, you can contact our support team via email or phone, and refunds are typically processed "
        "in three to five business days."
    ),
    "WARRANTY COVERAGE": (
        "All of our products include a standard one-year manufacturer warranty covering malfunctions and defects, "
        "though physical damage is not covered. You can also purchase an extended two-year warranty for nineteen dollars "
        "and ninety-nine cents, which is recognized internationally in more than fifty countries."
    ),
    "CUSTOMER SUPPORT": (
        "Our support team is available via live chat on our website or through twenty-four-seven email support, "
        "with an average response time of about two hours. Additionally, phone assistance is available at one-eight hundred "
        "support during weekdays from nine to five Eastern Time."
    ),
    "PAYMENT METHODS": (
        "We accept standard credit cards including Visa, Mastercard, and American Express, as well as digital payments "
        "through PayPal and Apple Pay. Customers can also choose buy-now-pay-later financing, pay with corporate accounts, "
        "or redeem gift cards at checkout."
    ),
    "BULK ORDERS AND CORPORATE ACCOUNTS": (
        "For bulk purchases, we offer a ten percent discount on orders containing ten or more items and a fifteen percent "
        "discount for orders of fifty or more items. Corporate clients also receive the support of a dedicated account "
        "manager and can request custom invoicing options."
    ),
    "PRODUCT GUARANTEES": (
        "We guarantee complete satisfaction with our products, offering a full refund if you are not pleased. Additionally, "
        "we provide a price match policy within seven days of purchase, charge no hidden fees, and offer a transparent "
        "calculator to determine your exact shipping costs."
    ),
    "INTERNATIONAL SHIPPING": (
        "We ship internationally to more than one hundred countries, with all customs fees and duties computed during checkout. "
        "International shipments include tracking options and generally take between ten to thirty business days to arrive."
    ),
    "DELIVERY ISSUES": (
        "If your shipment does not arrive on the promised date, we will issue a twenty percent refund. In the event of a lost "
        "package, we provide a free replacement within sixty days, and any items that arrive damaged are either replaced "
        "or refunded immediately."
    ),
    "LOYALTY PROGRAM": (
        "Members of our loyalty program earn one point for every dollar spent, which can be redeemed for a ten-dollar credit "
        "once you accumulate one hundred points. Membership is completely free with no annual fees, and it grants access to "
        "early product releases and exclusive discounts."
    )
}

# Mapping of keywords to policy sections
POLICY_KEYWORD_MAP = {
    "shipping": ["SHIPPING POLICIES", "INTERNATIONAL SHIPPING"],
    "ship": ["SHIPPING POLICIES", "INTERNATIONAL SHIPPING"],
    "delivery": ["SHIPPING POLICIES", "INTERNATIONAL SHIPPING", "DELIVERY ISSUES"],
    "deliver": ["SHIPPING POLICIES", "INTERNATIONAL SHIPPING", "DELIVERY ISSUES"],
    "arrive": ["SHIPPING POLICIES", "INTERNATIONAL SHIPPING", "DELIVERY ISSUES"],
    "late": ["DELIVERY ISSUES"],
    "delay": ["DELIVERY ISSUES"],
    "lost": ["DELIVERY ISSUES"],
    "damaged": ["DELIVERY ISSUES"],
    "return": ["RETURN AND REFUND POLICY", "PRODUCT GUARANTEES"],
    "refund": ["RETURN AND REFUND POLICY", "PRODUCT GUARANTEES"],
    "exchange": ["RETURN AND REFUND POLICY"],
    "money back": ["RETURN AND REFUND POLICY", "PRODUCT GUARANTEES"],
    "cancel": ["CANCELLATION POLICY"],
    "cancellation": ["CANCELLATION POLICY"],
    "warranty": ["WARRANTY COVERAGE"],
    "defect": ["WARRANTY COVERAGE"],
    "malfunction": ["WARRANTY COVERAGE"],
    "support": ["CUSTOMER SUPPORT"],
    "contact": ["CUSTOMER SUPPORT"],
    "help": ["CUSTOMER SUPPORT"],
    "email": ["CUSTOMER SUPPORT"],
    "phone": ["CUSTOMER SUPPORT"],
    "chat": ["CUSTOMER SUPPORT"],
    "pay": ["PAYMENT METHODS"],
    "payment": ["PAYMENT METHODS"],
    "credit card": ["PAYMENT METHODS"],
    "paypal": ["PAYMENT METHODS"],
    "apple pay": ["PAYMENT METHODS"],
    "bulk": ["BULK ORDERS AND CORPORATE ACCOUNTS"],
    "corporate": ["BULK ORDERS AND CORPORATE ACCOUNTS"],
    "wholesale": ["BULK ORDERS AND CORPORATE ACCOUNTS"],
    "guarantee": ["PRODUCT GUARANTEES", "WARRANTY COVERAGE"],
    "satisfy": ["PRODUCT GUARANTEES"],
    "loyalty": ["LOYALTY PROGRAM"],
    "points": ["LOYALTY PROGRAM"],
    "member": ["LOYALTY PROGRAM"],
}

def classify_query(question):
    """Classify the question to decide routing: order_tracking, order_history, policy, or complex"""
    question_lower = question.lower()
    
    # Check for order ID
    has_order_id = bool(re.search(r'ORD\d+', question.upper()))
    
    # Check for order history patterns
    has_history_words = any(phrase in question_lower for phrase in ["my orders", "order history", "what did i buy", "list my orders", "all my orders", "purchased"])
    
    # Check for specific tracking intent words (excluding generic policy keywords like shipping/delivery/ship/deliver unless accompanied by tracking intent)
    has_tracking_words = any(w in question_lower for w in ["where is", "track", "status", "arrived", "tracking number", "tracking id", "location", "when will", "where is my"])
    
    # Check for policy words (returns, cancellations, warranty, support, payment, bulk, guarantees, loyalty, shipping/delivery speed)
    has_policy_words = any(w in question_lower for w in [
        "policy", "return", "refund", "cancel", "warranty", "guarantee", 
        "support", "payment", "bulk", "loyalty", "ship", "shipping", 
        "delivery", "deliver"
    ])
    
    # Routing decision
    if has_history_words:
        return "order_history"
    elif has_order_id and has_policy_words:
        return "complex"
    elif has_order_id:
        return "order_tracking"
    elif has_tracking_words and has_policy_words:
        return "complex"
    elif has_tracking_words:
        return "order_tracking"
    elif has_policy_words:
        return "policy"
    
    # Fallback checks
    if any(w in question_lower for w in ["order", "package", "item", "product"]):
        return "complex"
        
    return "general"

def execute_db_query(query, params=()):
    """Execute a query against the SQLite orders database"""
    if not os.path.exists(DATABASE_FILE):
        return []
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_order_by_id(order_id):
    """Retrieve order details from DB by ID"""
    rows = execute_db_query("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    if rows:
        row = rows[0]
        try:
            items = json.loads(row['items'])
        except:
            items = row['items']
        row['items'] = items
        return row
    return None

def get_orders_by_email(email):
    """Retrieve all orders for a customer email"""
    rows = execute_db_query("SELECT * FROM orders WHERE customer_email = ? ORDER BY order_date DESC", (email,))
    for row in rows:
        try:
            items = json.loads(row['items'])
        except:
            items = row['items']
        row['items'] = items
    return rows

def load_pdf_index(pdf_name, api_key):
    """Load previously saved FAISS index for a PDF"""
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_community.vectorstores import FAISS
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview",
            google_api_key=api_key
        )
        index_path = os.path.join(EMBEDDINGS_STORAGE_DIR, pdf_name)
        if os.path.exists(index_path):
            return FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
        return None
    except Exception as e:
        print(f"Error loading PDF index: {str(e)}")
        return None

def get_uploaded_pdfs():
    """Get list of all uploaded PDFs"""
    if not os.path.exists(EMBEDDINGS_STORAGE_DIR):
        return []
    return [d for d in os.listdir(EMBEDDINGS_STORAGE_DIR) if os.path.isdir(os.path.join(EMBEDDINGS_STORAGE_DIR, d))]

def search_uploaded_pdfs(query, api_key, top_k=3):
    """Search across all uploaded PDFs"""
    uploaded_pdfs = get_uploaded_pdfs()
    all_results = []
    
    for pdf_name in uploaded_pdfs:
        try:
            vector_db = load_pdf_index(pdf_name, api_key)
            if vector_db:
                retriever = vector_db.as_retriever(search_kwargs={"k": top_k})
                docs = retriever.invoke(query)
                for doc in docs:
                    all_results.append((doc.page_content, pdf_name))
        except Exception as e:
            # Catch API key errors or loading errors gracefully
            print(f"Error searching PDF {pdf_name}: {str(e)}")
    
    return all_results

def local_policy_search(question):
    """Extract matching policy sections and rewrite them locally using natural language paragraph templates"""
    question_lower = question.lower()
    matched_sections = []
    
    # Find matching sections based on keywords
    for keyword, sections in POLICY_KEYWORD_MAP.items():
        if keyword in question_lower:
            for section in sections:
                if section not in matched_sections:
                    matched_sections.append(section)
    
    # If no keywords matched, try matching section names directly
    if not matched_sections:
        for section in LOCAL_POLICY_REWRITES.keys():
            if section.lower() in question_lower:
                matched_sections.append(section)
                
    if not matched_sections:
        return "I searched our policies but the requested information is not available in the company policy document. Please contact support@company.com for assistance."
        
    # Retrieve and merge the natural paragraphs for the matched sections
    paragraphs = []
    for section in matched_sections:
        paragraphs.append(LOCAL_POLICY_REWRITES[section])
        
    # Join into a single coherent paragraph
    return " ".join(paragraphs)

def call_gemini_api(prompt):
    """Invoke Gemini API to answer the prompt, adhering strictly to policy formatting rules"""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        return "ERROR: GOOGLE_API_KEY is not set. Please set it in your .env file to enable policy querying."
        
    try:
        from langchain_google_genai import GoogleGenerativeAI
        
        llm = GoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.0
        )
        return llm.invoke(prompt)
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return f"ERROR: Gemini API call failed: {e}"

def get_policy_context():
    pass

def format_policy_response_with_gemini(question, pdf_texts):
    """Query Gemini with strict guidelines on rewriting policies to a natural paragraph using ONLY uploaded PDFs."""
    if not pdf_texts:
        return "The uploaded policy documents do not contain enough information to answer this question."
        
    policies_content = "\n\n".join(pdf_texts)
    
    prompt = f"""You are a helpful company assistant. Answer the user's question using ONLY the provided company policy text.
Strict Rules:
1. Search and analyze the policy content below from the uploaded PDFs to locate relevant sections.
2. If relevant information is present in multiple PDFs, combine and analyze the information before generating the answer.
3. If the uploaded PDFs contain conflicting policies, clearly mention the conflict and explain which document or policy appears applicable if the documents provide enough context to determine this.
4. Convert the relevant information into a single natural, clear paragraph that directly answers the question, similar to how a human company-policy assistant would explain the policy to an employee.
5. Do NOT simply copy sentences or policy points from the file. Rewrite them in your own words while preserving the original meaning.
6. Do NOT provide the policy information as bullet points unless the user explicitly asks for bullet points.
7. Answer only what is relevant to the question. Do not mention unrelated policies.
8. Do not add assumptions, personal opinions, external knowledge, general knowledge, or any rules not present in the uploaded PDFs.
9. The uploaded PDF documents are the ONLY authoritative source. Do not use any other information.
10. If the answer cannot be found in the uploaded PDFs, do not guess or fabricate an answer. You must respond EXACTLY with: "The uploaded policy documents do not contain enough information to answer this question."

Uploaded Company Policies:
{policies_content}

User Question: {question}

Response:"""
    
    response = call_gemini_api(prompt)
    if response and response.startswith("ERROR:"):
        return response
    if response:
        return response.strip()
    return "The uploaded policy documents do not contain enough information to answer this question."

def handle_order_tracking_query(question, customer_email=None):
    """Identify order, execute database tool, show tool execution, and return status details"""
    order_ids = re.findall(r'ORD\d+', question.upper())
    order_id = order_ids[0] if order_ids else None
    
    if not order_id and customer_email:
        # Look up customer's latest order from DB
        orders = get_orders_by_email(customer_email)
        if orders:
            order_id = orders[0]['order_id']
            
    if not order_id:
        return "I couldn't locate an order ID in your request. Please specify your order ID (e.g., ORD001) so I can retrieve your status details.", []
        
    # Tool Execution Visualizer
    tool_indicator = f"🔧 check_order(\"{order_id}\")"
    
    order = get_order_by_id(order_id)
    if not order:
        response = f"I checked our records for order {order_id}, but that order does not exist in our system. Please check your order ID and try again."
        return f"{tool_indicator}\n\n{response}", [tool_indicator]
        
    # Build natural response
    items_list = ", ".join(order['items']) if isinstance(order['items'], list) else str(order['items'])
    
    response = (
        f"Your order {order_id} containing {items_list} is currently {order['status'].lower()}. "
        f"It is shipped via BlueDart with tracking ID {order.get('tracking_number') or 'N/A'}, and "
        f"the estimated delivery is {order['estimated_delivery']}."
    )
    
    # If the user asked about customer ID or other details, we can append a suggestion
    response += " Would you like to know more about this order or check other details?"
    
    return f"{tool_indicator}\n\n{response}", [tool_indicator]

def handle_order_history_query(customer_email):
    """Retrieve customer's order history from SQLite and format it"""
    if not customer_email:
        return "Please sign in with your email address to check your order history.", []
        
    tool_indicator = f"🔧 check_customer_orders(\"{customer_email}\")"
    orders = get_orders_by_email(customer_email)
    
    if not orders:
        return f"{tool_indicator}\n\nI couldn't find any order history associated with the email address {customer_email}.", [tool_indicator]
        
    orders_list = []
    for o in orders:
        items = ", ".join(o['items']) if isinstance(o['items'], list) else str(o['items'])
        orders_list.append(f"Order {o['order_id']} ({items}) - Status: {o['status']} (Total: ${o['total_price']})")
        
    response = f"I found {len(orders)} orders for your account: " + "; ".join(orders_list) + "."
    return f"{tool_indicator}\n\n{response}", [tool_indicator]

def run_agent(question, customer_email=None, pdf_texts=None):
    """Main router function that classifies the query, executes RAG/tools, and formats output"""
    query_type = classify_query(question)
    tool_calls = []
    
    if query_type == "order_tracking":
        response, tools = handle_order_tracking_query(question, customer_email)
        tool_calls.extend(tools)
        
    elif query_type == "order_history":
        response, tools = handle_order_history_query(customer_email)
        tool_calls.extend(tools)
        
    elif query_type == "policy":
        response = format_policy_response_with_gemini(question, pdf_texts)
        
    elif query_type == "complex":
        # Complex needs both policy lookup and order status!
        order_response, tools = handle_order_tracking_query(question, customer_email)
        tool_calls.extend(tools)
        
        policy_response = format_policy_response_with_gemini(question, pdf_texts)
        
        # Strip out tool indicator if present, format combined response
        order_clean = order_response.replace(tools[0], "").strip() if tools else order_response
        
        # Remove suffix if already inside order_clean to prevent duplication
        suffix = " Would you like to know more about this order or check other details?"
        if order_clean.endswith(suffix):
            order_clean = order_clean[:-len(suffix)].strip()
            
        response = f"{tools[0] if tools else ''}\n\n{order_clean}\n\nRegarding our policies: {policy_response}"
        response = response.strip()
        
    else:
        # General response
        response = "I can help you track your orders, check your order history, or answer questions about company shipping, returns, warranty, and support policies. What would you like to know?"
        
    # Append the universal suffix
    suffix = " Would you like to know more about this order or check other details?"
    
    # Clean up any trailing suffix occurrences to prevent duplicate suffixing
    if response.endswith(suffix):
        response = response[:-len(suffix)].strip()
    if response.endswith(suffix.strip()):
        response = response[:-len(suffix.strip())].strip()
        
    response = response.strip() + suffix
    return response

def save_conversation_log(email, question, answer):
    """Log the conversation details to SQLite db"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (customer_email, question, answer)
            VALUES (?, ?, ?)
        """, (email or "anonymous@example.com", question, answer))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

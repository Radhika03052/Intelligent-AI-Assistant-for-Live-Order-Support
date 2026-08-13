"""
AI CUSTOMER SUPPORT BOT - Streamlit Web Interface
Real-Time Order Tracking with Function Calling & RAG Policies
"""

import streamlit as st
from orders_db import (
    init_orders_database,
    get_orders_by_email
)
from ai_agent import run_agent, save_conversation_log
import pypdf
import io

# Page configuration
st.set_page_config(
    page_title="Intelligent AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_orders_database()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "customer_email" not in st.session_state:
    st.session_state.customer_email = None

# ============================================================================
# STREAMLIT UI
# ============================================================================

# Header
st.title("🤖 Intelligent AI Assistant for Live Order Support")
st.caption("Real-Time Order Tracking with Live Database Queries and RAG Policies")

# Sidebar - Sign In
with st.sidebar:
    st.header("👤 Sign In")
    email_input = st.text_input(
        "Enter your email address:",
        placeholder="your.email@example.com",
        value=st.session_state.customer_email or ""
    )
    
    if email_input and email_input != st.session_state.customer_email:
        st.session_state.customer_email = email_input
        st.session_state.messages = []
        st.success(f"✓ Signed in as {email_input}")
    
    st.divider()
    
    # Show test customers
    st.subheader("🧪 Test Customers")
    test_customers = [
        ("john@example.com", "ORD001 - Laptop"),
        ("sarah@example.com", "ORD002 - Mouse"),
        ("mike@example.com", "ORD003 - Monitor"),
        ("emma@example.com", "ORD004 - Headphones"),
        ("alex@example.com", "ORD005 - Phone Case"),
    ]
    
    for email, order_info in test_customers:
        if st.button(f"👤 {email}", key=email):
            st.session_state.customer_email = email
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    st.subheader("📄 Upload Policies")
    uploaded_pdfs = st.file_uploader("Upload Company Policy PDFs", type="pdf", accept_multiple_files=True)
    pdf_texts = []
    if uploaded_pdfs:
        for pdf in uploaded_pdfs:
            try:
                reader = pypdf.PdfReader(io.BytesIO(pdf.read()))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                if text.strip():
                    pdf_texts.append(f"--- Document: {pdf.name} ---\n{text}")
            except Exception as e:
                st.error(f"Error reading {pdf.name}: {e}")
        if pdf_texts:
            st.success(f"Loaded {len(uploaded_pdfs)} PDF(s).")
            
    st.divider()
    
    # Show orders for current customer
    if st.session_state.customer_email:
        st.subheader("📦 Your Orders")
        orders = get_orders_by_email(st.session_state.customer_email)
        if orders:
            # Show all order numbers first
            st.write("**Your Order Numbers:**")
            for order in orders:
                st.markdown(f"• **{order['order_id']}** - {order['status']}")
            
            st.divider()
            
            # Show detailed order information
            st.write("**Order Details:**")
            for order in orders:
                with st.expander(f"📍 {order['order_id']} - {order['status']} - ${order['total_price']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Order Info**")
                        st.write(f"Date: {order['order_date']}")
                        st.write(f"Status: **{order['status']}**")
                        st.write(f"Total: **${order['total_price']:.2f}**")
                    
                    with col2:
                        st.write("**Shipping Info**")
                        st.write(f"Carrier: BlueDart")
                        st.write(f"Tracking: {order.get('tracking_number', 'N/A')}")
                        st.write(f"Arrival: {order['estimated_delivery']}")
                    
                    st.divider()
                    st.write("**Items Ordered:**")
                    items_list = order['items']
                    for item in (items_list if isinstance(items_list, list) else [items_list]):
                        st.write(f"  • {item}")
                    
                    st.divider()
                    st.write("**Shipping Address:**")
                    st.write(order['shipping_address'])

# Main content
if not st.session_state.customer_email:
    st.info("👈 **Please sign in with your email address or click a test customer in the sidebar to get started**")
    
    
    
  

else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your orders, shipping, returns, or policies..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Checking database and policies..."):
                # Get response from our unified chatbot logic
                response = run_agent(prompt, st.session_state.customer_email, pdf_texts=pdf_texts)
                
                st.markdown(response)
                
                # Save to database
                save_conversation_log(st.session_state.customer_email, prompt, response)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("📧 support@company.com")
with col2:
    st.caption("📞 1-800-SUPPORT")
with col3:
    st.caption("💬 24/7 Support Available")

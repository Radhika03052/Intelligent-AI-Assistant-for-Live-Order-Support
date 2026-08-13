"""
AI CUSTOMER SUPPORT BOT - CLI Chatbot
Uses unified ai_agent.py for RAG and tool calls.
"""

import sys
from orders_db import init_orders_database
from ai_agent import run_agent, save_conversation_log

def run_chatbot():
    """
    Main CLI chatbot that uses the unified ai_agent.py:
    1. Prompts for customer email
    2. Runs input queries through the agent
    3. Handles database-based order queries and policy questions
    4. Logs conversations
    """
    # Initialize database
    init_orders_database()
    
    print("=" * 80)
    print("🤖 AI CUSTOMER SUPPORT BOT - CLI INTERFACE")
    print("=" * 80)
    print("\nThis bot features:")
    print("✓ REAL-TIME order tracking (queries SQLite database)")
    print("✓ Policy search & rewrite (no bullet points, own words)")
    print("✓ Visible tool call tags (e.g. 🔧 check_order)")
    print("✓ Robust fallback to local rules if Gemini API is offline\n")
    
    # Get customer info
    customer_email = input("Enter your email: ").strip()
    if not customer_email:
        customer_email = "john@example.com"
        print(f"Using test email: {customer_email}")
    
    print(f"\n👤 Welcome! (Customer: {customer_email})")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("\n💬 Your question: ").strip()
        
        if question.lower() == "quit":
            print("\nThank you for using our support. Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n⏳ Processing your request...")
        
        # Run unified agent
        response = run_agent(question, customer_email)
        
        # Display response
        print(f"\n{response}")
        
        # Save to database
        save_conversation_log(customer_email, question, response)
        print("\n   ✓ Conversation saved to database")

if __name__ == "__main__":
    run_chatbot()

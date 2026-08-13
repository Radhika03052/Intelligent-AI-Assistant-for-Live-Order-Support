"""
Demo script to test the AI Customer Support Bot
Shows various interactions and capabilities
"""

from orders_db import init_orders_database, get_order_by_id, get_orders_by_email
from tools import execute_tool
import json

def print_section(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def demo():
    print_section("🤖 AI CUSTOMER SUPPORT BOT - DEMO")
    
    # Initialize database
    print("\n[1] Initializing orders database...")
    init_orders_database()
    print("✓ Database initialized with sample orders")
    
    # Demo: Track an order
    print_section("📦 DEMO: Order Tracking")
    print("\nScenario: Customer wants to track order ORD001")
    
    order_id = "ORD001"
    print(f"\nCalling: get_tracking_status('{order_id}')")
    result = execute_tool("get_tracking_status", {"order_id": order_id})
    result_dict = json.loads(result)
    
    print("\nResult:")
    print(f"  Order ID: {result_dict['order_id']}")
    print(f"  Status: {result_dict['current_status']}")
    print(f"  Tracking: {result_dict['tracking_number']}")
    print(f"  Estimated Delivery: {result_dict['estimated_delivery']}")
    print(f"  Items: {', '.join(result_dict['items'])}")
    
    # Demo: Check customer orders
    print_section("👤 DEMO: Customer Order History")
    print("\nScenario: Customer wants to see all their orders")
    
    email = "john@example.com"
    print(f"\nCalling: check_customer_orders('{email}')")
    result = execute_tool("check_customer_orders", {"customer_email": email})
    result_dict = json.loads(result)
    
    print("\nResult:")
    print(f"  Customer: {result_dict['customer_email']}")
    print(f"  Total Orders: {result_dict['order_count']}")
    for order in result_dict['orders']:
        print(f"    - {order['order_id']}: {order['status']} (${order['total_price']})")
    
    # Demo: Apply refund
    print_section("💰 DEMO: Refund Processing")
    print("\nScenario: Customer wants to return delivered order")
    
    order_id = "ORD002"
    reason = "Item not as expected"
    print(f"\nCalling: apply_refund('{order_id}', '{reason}')")
    result = execute_tool("apply_refund", {"order_id": order_id, "reason": reason})
    result_dict = json.loads(result)
    
    print("\nResult:")
    print(f"  Success: {result_dict['success']}")
    if result_dict['success']:
        print(f"  Refund Amount: ${result_dict['refund_amount']}")
        print(f"  Processing Time: {result_dict['processing_time']}")
    else:
        print(f"  Message: {result_dict['message']}")
    
    # Demo: Update order status (admin)
    print_section("⚙️ DEMO: Update Order Status (Admin)")
    print("\nScenario: Admin updates order status to 'In Transit'")
    
    order_id = "ORD003"
    new_status = "Shipped"
    print(f"\nCalling: update_order('{order_id}', '{new_status}')")
    result = execute_tool("update_order", {"order_id": order_id, "new_status": new_status})
    result_dict = json.loads(result)
    
    print("\nResult:")
    print(f"  Success: {result_dict['success']}")
    print(f"  Message: {result_dict['message']}")
    
    # Show all sample orders
    print_section("📋 ALL SAMPLE ORDERS IN DATABASE")
    print("\nTest Customers: john@example.com, sarah@example.com, mike@example.com, emma@example.com, alex@example.com")
    for i in range(1, 6):
        order = get_order_by_id(f"ORD00{i}")
        if order:
            print(f"\n{order['order_id']}: {order['status']}")
            print(f"  Customer: {order['customer_name']} ({order['customer_email']})")
            print(f"  Items: {', '.join(order['items'])}")
            print(f"  Total: ${order['total_price']}")
            print(f"  Delivery: {order['estimated_delivery']}")
    
    print_section("✓ DEMO COMPLETE")
    print("\nYou can now run:")
    print("  - CLI: python index.py")
    print("  - Web UI: streamlit run app.py")

if __name__ == "__main__":
    demo()

import json
from orders_db import get_order_by_id, get_orders_by_email, update_order_status
from datetime import datetime

def get_tracking_status(order_id: str) -> dict:
    """
    Get real-time tracking status for an order.
    Used as a tool that the AI can call via function calling.
    """
    order = get_order_by_id(order_id)
    
    if not order:
        return {
            "success": False,
            "message": f"Order {order_id} not found in our system"
        }
    
    status_messages = {
        "Processing": "Your order is being prepared in our warehouse",
        "Shipped": "Your order is on its way to you!",
        "In Transit": "Your order is out for delivery",
        "Delivered": "Your order has been delivered",
        "Cancelled": "This order has been cancelled"
    }
    
    return {
        "success": True,
        "order_id": order["order_id"],
        "current_status": order["status"],
        "status_message": status_messages.get(order["status"], order["status"]),
        "items": order["items"],
        "total_price": order["total_price"],
        "tracking_number": order["tracking_number"],
        "estimated_delivery": order["estimated_delivery"],
        "shipping_address": order["shipping_address"]
    }

def check_customer_orders(customer_email: str) -> dict:
    """
    Retrieve all orders for a customer.
    Used as a tool for customer verification and order lookup.
    """
    orders = get_orders_by_email(customer_email)
    
    if not orders:
        return {
            "success": False,
            "message": f"No orders found for email {customer_email}"
        }
    
    return {
        "success": True,
        "customer_email": customer_email,
        "order_count": len(orders),
        "orders": [
            {
                "order_id": o["order_id"],
                "order_date": o["order_date"],
                "status": o["status"],
                "total_price": o["total_price"],
                "items": o["items"]
            }
            for o in orders
        ]
    }

def update_order(order_id: str, new_status: str) -> dict:
    """
    Update order status (admin function).
    """
    valid_statuses = ["Processing", "Shipped", "In Transit", "Delivered", "Cancelled"]
    
    if new_status not in valid_statuses:
        return {
            "success": False,
            "message": f"Invalid status. Allowed statuses: {', '.join(valid_statuses)}"
        }
    
    order = get_order_by_id(order_id)
    if not order:
        return {
            "success": False,
            "message": f"Order {order_id} not found"
        }
    
    update_order_status(order_id, new_status)
    return {
        "success": True,
        "message": f"Order {order_id} updated to {new_status}",
        "order_id": order_id,
        "new_status": new_status
    }

def apply_refund(order_id: str, reason: str) -> dict:
    """
    Process refund for an order.
    """
    order = get_order_by_id(order_id)
    
    if not order:
        return {
            "success": False,
            "message": f"Order {order_id} not found"
        }
    
    if order["status"] == "Delivered" or order["status"] == "Cancelled":
        return {
            "success": True,
            "message": f"Refund of ${order['total_price']:.2f} approved for order {order_id}",
            "order_id": order_id,
            "refund_amount": order["total_price"],
            "reason": reason,
            "processing_time": "5-7 business days"
        }
    
    return {
        "success": False,
        "message": "Refund cannot be processed for orders that are still in transit"
    }

# Define tools for LangChain function calling
TOOLS = [
    {
        "name": "get_tracking_status",
        "description": "Get real-time tracking status and delivery information for a specific order. Returns current status, tracking number, estimated delivery date, and shipping address.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to track (e.g., 'ORD001')"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "check_customer_orders",
        "description": "Retrieve all orders for a customer using their email address. Shows order history with statuses and totals.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_email": {
                    "type": "string",
                    "description": "Customer email address"
                }
            },
            "required": ["customer_email"]
        }
    },
    {
        "name": "apply_refund",
        "description": "Process a refund for a delivered order. Returns refund amount and processing time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to refund"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the refund"
                }
            },
            "required": ["order_id", "reason"]
        }
    },
    {
        "name": "update_order",
        "description": "Update the status of an order (admin only). Valid statuses: Processing, Shipped, In Transit, Delivered, Cancelled",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to update"
                },
                "new_status": {
                    "type": "string",
                    "description": "New status for the order"
                }
            },
            "required": ["order_id", "new_status"]
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Execute a tool based on its name and input.
    """
    if tool_name == "get_tracking_status":
        result = get_tracking_status(tool_input["order_id"])
    elif tool_name == "check_customer_orders":
        result = check_customer_orders(tool_input["customer_email"])
    elif tool_name == "apply_refund":
        result = apply_refund(tool_input["order_id"], tool_input["reason"])
    elif tool_name == "update_order":
        result = update_order(tool_input["order_id"], tool_input["new_status"])
    else:
        result = {"success": False, "message": f"Unknown tool: {tool_name}"}
    
    return json.dumps(result)

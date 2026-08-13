import sqlite3
from datetime import datetime, timedelta
import json

DATABASE_FILE = "orders.db"

def init_orders_database():
    """Initialize the orders database with sample data"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            order_date DATETIME,
            items TEXT,
            total_price REAL,
            status TEXT,
            shipping_address TEXT,
            tracking_number TEXT,
            estimated_delivery DATETIME
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if orders already exist
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        # Insert sample orders
        sample_orders = [
            ("ORD001", "John Smith", "john@example.com", 
             datetime.now() - timedelta(days=3),
             json.dumps(["Laptop", "USB Cable"]), 1299.99, "Shipped",
             "123 Main St, New York, NY 10001",
             "1Z999AA10123456784", datetime.now() + timedelta(days=3)),
            
            ("ORD002", "Sarah Johnson", "sarah@example.com",
             datetime.now() - timedelta(days=7),
             json.dumps(["Wireless Mouse", "Keyboard"]), 89.99, "Delivered",
             "456 Oak Ave, Los Angeles, CA 90001",
             "1Z999AA10123456785", datetime.now() - timedelta(days=1)),
            
            ("ORD003", "Mike Chen", "mike@example.com",
             datetime.now() - timedelta(hours=5),
             json.dumps(["Monitor", "HDMI Cable", "Stand"]), 399.99, "Processing",
             "789 Pine Rd, Chicago, IL 60601",
             None, datetime.now() + timedelta(days=5)),
            
            ("ORD004", "Emma Davis", "emma@example.com",
             datetime.now() - timedelta(days=1),
             json.dumps(["Headphones"]), 149.99, "In Transit",
             "321 Elm St, Houston, TX 77001",
             "1Z999AA10123456786", datetime.now() + timedelta(days=2)),
            
            ("ORD005", "Alex Wilson", "alex@example.com",
             datetime.now() - timedelta(days=14),
             json.dumps(["Smartphone Case", "Screen Protector"]), 29.99, "Delivered",
             "654 Maple Ln, Phoenix, AZ 85001",
             "1Z999AA10123456787", datetime.now() - timedelta(days=10)),
        ]
        
        for order in sample_orders:
            cursor.execute("""
                INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, order)
    
    conn.commit()
    conn.close()

def get_order_by_id(order_id):
    """Fetch order details by order ID"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "order_id": row[0],
            "customer_name": row[1],
            "customer_email": row[2],
            "order_date": row[3],
            "items": json.loads(row[4]),
            "total_price": row[5],
            "status": row[6],
            "shipping_address": row[7],
            "tracking_number": row[8],
            "estimated_delivery": row[9]
        }
    return None

def get_orders_by_email(email):
    """Fetch all orders for a customer by email"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE customer_email = ?", (email,))
    rows = cursor.fetchall()
    conn.close()
    
    orders = []
    for row in rows:
        orders.append({
            "order_id": row[0],
            "customer_name": row[1],
            "customer_email": row[2],
            "order_date": row[3],
            "items": json.loads(row[4]),
            "total_price": row[5],
            "status": row[6],
            "shipping_address": row[7],
            "tracking_number": row[8],
            "estimated_delivery": row[9]
        })
    return orders

def update_order_status(order_id, new_status):
    """Update order status"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

def save_conversation(customer_email, question, answer):
    """Save conversation to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (customer_email, question, answer)
        VALUES (?, ?, ?)
    """, (customer_email, question, answer))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_orders_database()
    print("Database initialized successfully!")
    print("\nSample Orders:")
    for i in range(1, 6):
        order = get_order_by_id(f"ORD00{i}")
        if order:
            print(f"\n{order['order_id']}: {order['status']} - Estimated Delivery: {order['estimated_delivery']}")

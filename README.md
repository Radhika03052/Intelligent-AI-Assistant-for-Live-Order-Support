# 🤖 Intelligent AI Assistant for Live Order Support

An **AI-powered customer support assistant** that combines **Retrieval-Augmented Generation (RAG)** for company policies with **LLM function calling** for real-time order tracking, order history, and refund processing.

## 🚀 Features

* 📚 **RAG-Based Policy Lookup** — Retrieves accurate information from company policies.
* 📦 **Live Order Tracking** — Provides order status, tracking information, and estimated delivery.
* 🧾 **Customer Order History** — Retrieves all orders associated with a customer email.
* 💰 **Refund Processing** — Processes refunds for eligible orders.
* 🤖 **LLM Function Calling** — Automatically selects and executes the appropriate tool.
* 💬 **Conversation Logging** — Stores customer conversations in a SQLite database.
* 🌐 **Streamlit Web Interface** — Provides an interactive chatbot UI.

## 🛠️ Technologies Used

* **Python**
* **LangChain**
* **Google Generative AI**
* **RAG (Retrieval-Augmented Generation)**
* **FAISS Vector Database**
* **SQLite**
* **Streamlit**

## 📁 Project Structure

```text
Intelligent-AI-Assistant-for-Live-Order-Support/
│
├── index.py                  # CLI chatbot
├── app.py                    # Streamlit web interface
├── orders_db.py              # Database operations
├── tools.py                  # AI tool definitions
├── company_policies.txt      # RAG knowledge base
├── requirements.txt          # Python dependencies
├── orders.db                 # SQLite database
└── README.md                 # Project documentation
```

## ⚙️ Installation

### **1. Create Virtual Environment**

```bash
python -m venv myenv
```

### **2. Activate Virtual Environment**

**Windows:**

```bash
myenv\Scripts\activate
```

**macOS/Linux:**

```bash
source myenv/bin/activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Configure API Key**

Set your **Google Generative AI API key** using an environment variable.

## ▶️ Running the Project

### **CLI Version**

```bash
python streamlit_app.py
```

### **Streamlit Web Interface**

```bash
streamlit streamlit_app.py
```

## 🔧 Available AI Tools

| **Tool**                | **Purpose**                               |
| ----------------------- | ----------------------------------------- |
| `get_tracking_status`   | Retrieves live order tracking information |
| `check_customer_orders` | Retrieves customer order history          |
| `apply_refund`          | Processes eligible order refunds          |
| `update_order`          | Updates the order status                  |

## 🧠 LLM Workflow

```text
                    ┌─────────────────────┐
                    │    User Question    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │        LLM          │
                    │  Intent Analysis    │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Policy Question  │      │  Order Request   │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │   RAG / FAISS    │      │  Function Call   │
        │ Policy Retrieval │      │  Tool Selection  │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Relevant Policy  │      │  Tool Execution  │
        │    Retrieved     │      │  SQLite Database │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │        LLM          │
                    │ Generate Response   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Save Conversation   │
                    │      in SQLite      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Response to User  │
                    └─────────────────────┘
```

### **Workflow Steps**

1. **User Input** — The customer enters their email and question.
2. **Intent Analysis** — The **LLM analyzes the customer's request**.
3. **Policy Retrieval** — Policy-related questions are processed using **RAG and FAISS**.
4. **Function Calling** — Order-related requests trigger the appropriate **AI tool**.
5. **Database Operation** — The selected tool retrieves or updates information from **SQLite**.
6. **Response Generation** — The **LLM generates a natural-language response** using the retrieved information.
7. **Conversation Logging** — The question and response are stored in the **SQLite database**.

## 💬 Example Interactions

### **📦 Order Tracking**

**User:**

```text
Where is my order ORD001?
```

**AI Assistant:**

```text
Your order ORD001 has been shipped.
Tracking Number: 1Z999AA10123456784
Estimated Delivery: Within 3 days.
```

The LLM automatically calls:

```text
get_tracking_status
```

### **💰 Refund Request**

**User:**

```text
I want to return my order ORD002.
```

The assistant:

1. Retrieves the **return/refund policy using RAG**.
2. Checks the order information.
3. Determines whether the order is eligible.
4. Calls **apply_refund** if applicable.
5. Provides the customer with the refund details.

### **📚 Policy Question**

**User:**

```text
What is your return policy?
```

The assistant uses **RAG** to search the company policy knowledge base and provides the relevant policy information.

## 🗄️ Database

The project uses **SQLite** to store order and conversation information.

### **Orders Table**

```text
order_id
customer_name
customer_email
order_date
items
total_price
status
shipping_address
tracking_number
estimated_delivery
```

### **Conversations Table**

```text
id
customer_email
question
answer
timestamp
```

## 🔐 Security

* **API keys** should be stored using environment variables.
* **Customer email verification** should be implemented before accessing orders.
* **Authentication** should be added for production deployments.
* **Rate limiting** should be implemented to prevent API abuse.
* Customer information should be handled securely.

## 📈 Future Enhancements

* 🔹 **Advanced AI Routing**
* 🔹 **Multi-language Customer Support**
* 🔹 **Voice-Based Support**
* 🔹 **WhatsApp/Telegram Integration**
* 🔹 **Advanced Analytics Dashboard**
* 🔹 **Persistent Vector Database**
* 🔹 **Authentication and Role-Based Access**
* 🔹 **Automated Email Notifications**
* 🔹 **Cloud Deployment**

## 🎯 Project Objective

The objective of this project is to develop an **intelligent AI customer support system** that combines **RAG-based knowledge retrieval**, **LLM function calling**, and **real-time database operations** to provide **fast, accurate, and personalized live order support**.

## 📌 Key Highlights

> **RAG + LLM + Function Calling + SQLite + Streamlit**

The system demonstrates how modern **Generative AI applications** can combine **knowledge retrieval** with **real-time actions** to build practical customer support solutions.

## 📄 License

This project is provided **as-is for educational and demonstration purposes**.

---

**Project Name:** `Intelligent-AI-Assistant-for-Live-Order-Support`
**Version:** `1.0.0`
**Last Updated:** `August 2026`

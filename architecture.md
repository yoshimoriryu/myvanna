# Secure by Design: The Air-Gapped Architecture

## The Core Principle: Zero Trust

The entire security model of this project is built on a single, critical principle: **the AI agent never has direct access to the database.**

This "air gap" between the reasoning engine (the AI) and the execution engine (the database) is the foundation of the system's security.

---

## Visualization: The Two-Building Analogy

Imagine the system as two physically separate, secure facilities:

### 🏙️ Building A: The Chatbot Zone (Public)

This is where the LangGraph agent lives. It's brilliant at understanding language and talking to users. However, for maximum security, **it is not given the keys to the sensitive data.**

### 🏦 Building B: The Data Vault (Private)

This is where the PostgreSQL database resides. It's a high-security vault. Only processes with the highest level of trust are allowed inside.

---

## The Bridge: The Secure API Microservice

The `secure_api` is the only bridge between these two buildings. It acts as an armored, single-lane checkpoint.


```mermaid
+------------------------------------------+         +--------------------------------------+
|        BUILDING A: CHATBOT ZONE          |         |       BUILDING B: SECURE VAULT       |
|                                          |         |                                      |
|  [User] <> [LangGraph Chatbot]           |         |       [Private PostgreSQL DB]        |
|                |                         |         |                  ^                   |
|                | (Generates a SQL query) |         |                  | (Direct, trusted  |
|                v                         |         |                  |  connection)      |
|         (The agent has NO DB keys)       |         |                  |                   |
|                                          |         |                  |                   |
+------------------------------------------+         |   +-----------------------------+    |
                 |                                   |   | [Secure API Microservice]   |    |
                 | (HTTP Request: "Please run this") |   | (THE ONLY THING WITH DB KEYS) |  |
                 +-------------------------------------> |                             |    |
                                                         +-----------------------------+    |
                  <------------------------------------+                                    |
                   (HTTP Response: "Here are the safe                                       |
                                    results")        |                                      |
                                                     +--------------------------------------+

                  <-------------------- THE AIR GAP -------------------->
              (The Chatbot can never cross this line to touch the database)
```
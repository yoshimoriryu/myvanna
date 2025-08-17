# Product Requirements Document: MyVanna Secure Data Chatbot

## 1. Introduction & Executive Summary

MyVanna is a production-ready, multi-agent chatbot designed to provide secure, natural language access to private PostgreSQL databases. Its core purpose is to allow users to ask questions in plain English and receive accurate answers, without ever exposing the underlying database to direct AI access.

The system is built on a "zero trust," air-gapped architecture that separates the AI reasoning engine (Vanna AI, LangGraph, Google Gemini) from the data execution engine (a secure FastAPI). This ensures that sensitive data remains protected while still leveraging the power of modern LLMs for data analysis and retrieval. This document outlines the key features, user personas, and technical requirements for the MyVanna project.

**Problem:** Businesses need to empower non-technical users to query databases without granting them direct access or requiring them to learn SQL. Existing solutions often create security risks by tightly coupling AI models with database credentials.

**Solution:** MyVanna provides a secure, decoupled architecture where an AI agent generates SQL, which is then passed to a separate, hardened API for execution. This provides a secure bridge between natural language and structured data.

## 2. Goals & Objectives

*   **Primary Goal:** To provide a secure, reliable, and intuitive natural language interface for querying private PostgreSQL databases.
*   **Security:** Implement a "zero trust" architecture that prevents the AI from having any direct database access. All queries must be executed through a secure, auditable API layer.
*   **Modularity:** Develop a reusable core engine that can be easily configured for different data domains.
*   **Usability:** Create a simple chatbot interface that allows users to ask questions and receive clear, understandable answers.
*   **Testability:** Ensure the system is covered by a comprehensive, multi-layered, and automated test suite to guarantee reliability.

## 3. Features

*   **Multi-Agent Chatbot:** A sophisticated, LangGraph-orchestrated agent that can route user intent, select data domains, generate SQL, and synthesize natural language answers.
*   **Secure, Air-Gapped SQL Execution:** A dedicated FastAPI endpoint that receives SQL queries, executes them against the database, and returns the results. It is the only component with database credentials.
*   **Metadata-Driven Domain Routing:** A configurable `domain_metadata.json` file allows the system to support multiple, distinct data domains and route user questions to the correct one based on rich descriptions.
*   **Automated Data Training:** A scriptable, idempotent process to synchronize training data (DDL, documentation, and SQL examples) to a Qdrant vector store.
*   **Isolated Test Environment:** A complete, Dockerized test suite that runs on separate ports to prevent conflicts with the development environment.
*   **Production-Ready Configuration:** A flexible configuration system that supports both local development (HTTP) and production deployments (HTTPS).

## 4. User Personas

*   **Data Analyst (Technical User):**
    *   **Needs:** Wants to quickly query data without writing boilerplate SQL. Uses the chatbot for initial exploration before diving deeper. Values accuracy and the ability to see the generated SQL.
    *   **Goals:** Speed up their workflow and handle simple data requests more efficiently.

*   **Business Stakeholder (Non-Technical User):**
    *   **Needs:** Wants to get answers to business questions without needing to ask a technical team. Needs answers to be in plain English.
    *   **Goals:** Self-serve data insights to make informed business decisions.

*   **Developer/Administrator (Technical User):**
    *   **Needs:** Wants to securely manage and deploy the chatbot. Needs a system that is easy to configure, monitor, and extend with new data domains.
    *   **Goals:** Provide a secure data access tool to the organization while maintaining strict security and governance controls.

## 5. User Stories

*   **As a Business Stakeholder,** I want to ask "How many students are enrolled in each course?" and get a simple, easy-to-understand answer.
*   **As a Data Analyst,** I want to ask a complex question and see the generated SQL so I can verify its accuracy or modify it for further analysis.
*   **As an Administrator,** I want to add a new "Finance" data domain by adding a new metadata entry, DDL files, and training data, without changing any application code.
*   **As an Administrator,** I want to run a single script to execute all integration and unit tests to ensure the system is functioning correctly before deploying an update.
*   **As a Security Engineer,** I want to know that the LLM/agent never has direct access to the database credentials, and all queries are passed through a secure API.

## 6. Architecture & Technical Design

The system is designed with a secure, air-gapped architecture that separates the AI components from the data components.

*   **AI Orchestration:** LangGraph
*   **AI/RAG Engine:** Vanna AI
*   **LLM & Embeddings:** Google Gemini
*   **Vector Store:** Qdrant (secured with an API key)
*   **Data Source:** PostgreSQL
*   **Secure API:** FastAPI
*   **Environment Management:** Docker Compose

The architecture is visualized in the `architecture.md` document, which highlights the "two-building" analogy: the public-facing "Chatbot Zone" and the private, high-security "Data Vault."

## 7. Success Metrics

*   **Adoption Rate:** Number of active users per week.
*   **Query Success Rate:** Percentage of user questions that result in a successful SQL execution and a valid answer.
*   **User Satisfaction (Future):** A rating system (e.g., thumbs up/down) on the quality and accuracy of the answers.
*   **Security:** Zero security incidents related to unauthorized data access.
*   **Domain Scalability:** Time required to add and train a new data domain.

## 8. Future Work & Roadmap

*   **V1.1: Enhanced User Interface:** Move from a command-line interface to a web-based UI (e.g., using Streamlit or React) to improve usability for non-technical users.
*   **V1.2: Caching Layer:** Implement a caching mechanism in the secure API to store the results of frequently asked questions, reducing database load and improving response time.
*   **V1.3: User-Feedback Loop:** Add a feature for users to rate answers and provide corrections, which can be used to generate additional training data and improve the model's accuracy over time.
*   **V2.0: Expanded Data Source Support:** Add support for other data sources beyond PostgreSQL, such as Snowflake, BigQuery, or Databricks.
*   **V2.1: Advanced Analytics:** Integrate capabilities for generating data visualizations (charts, graphs) in addition to textual answers.

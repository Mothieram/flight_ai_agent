# ✈️ Flight Tracker AI with Apache Airflow & Gemini

This project demonstrates a complete ETL pipeline using **Apache Airflow** to extract real-time flight data and power an **agentic AI** system using **Gemini**. The AI acts as a smart assistant that can answer user queries about flights in natural language.

---

## 🚀 Features

- ⛽ **ETL Pipeline** using Apache Airflow  
  - Extracts flight data from the AviationStack API
  - Transforms and filters key attributes (flight number, status, departure/arrival time)
  - Loads into a PostgreSQL database

- 🧠 **Agentic AI Assistant** using Gemini  
  - Accepts user queries like "Where is flight AI202?"
  - Accesses the flight data dynamically from the database
  - Responds in natural language with insights (e.g., delays, ETA, gate info)

---

## 🛠️ Tech Stack

| Component        | Tech Used                   |
|------------------|-----------------------------|
| ETL Workflow     | Apache Airflow              |
| Data Source      | AviationStack API           |
| Storage          | PostgreSQL                  |
| Agentic AI       | Gemini (Google's LLM)       |
| Backend Logic    | Python (with SQLAlchemy)    |
| Deployment       | Docker + Airflow Container  |

📈 Future Improvements
Add a Streamlit or React dashboard for visualization

Enable notification triggers for delays

Multi-language support using Gemini's multilingual capabilities

Store historical trends for predictive insights




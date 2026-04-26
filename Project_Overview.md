# AI-Powered Weekly Review Analyzer — Project Overview

This project is a sophisticated AI Agent designed to automate the collection and analysis of app reviews, turning raw feedback into professional product insight reports delivered directly to stakeholders.

---

## 🛠️ Technology Stack & Tools

### 1. AI & LLM Reasoning
- **Google Gemini (text-embedding-004)**: Used for high-dimensional vector embeddings to understand the semantic meaning of reviews.
- **Groq (Llama 3.1 70B)**: Used for ultra-fast, high-reasoning summarization. It identifies themes, generates action items, and validates quotes.

### 2. NLP & Machine Learning
- **UMAP**: Dimension reduction technique used to simplify high-dimensional embeddings for better clustering.
- **HDBSCAN**: Density-based clustering algorithm that groups similar reviews into "Themes" without needing to specify the number of clusters.
- **spaCy (en_core_web_sm)**: Used for PII scrubbing (anonymizing names/emails) and POS-based heuristic filtering.
- **langdetect**: Ensures only English reviews are processed for high-quality analysis.

### 3. Delivery & Integration (MCP)
- **Model Context Protocol (MCP)**: A secure protocol used to interact with external tools.
- **Google Docs Server**: Automatically appends reports to a shared document.
- **Gmail Server**: Sends high-fidelity HTML reports to product managers and leadership.

### 4. Web & Orchestration
- **FastAPI**: Provides a modern, high-performance web backend for the dashboard.
- **Vanilla CSS (Glassmorphism)**: A premium, futuristic frontend dashboard for triggering runs and viewing logs.
- **SQLite**: Handles the "Audit Store" to ensure idempotency (preventing duplicate reports).
- **Railway.app**: The production environment hosting the persistent agent and web dashboard.

---

## 🚀 Implementation Phases

### Phase 1: Setup & Data Models
Established the core architecture, Pydantic data models for reviews and themes, and the configuration system (`products.yaml`, `settings.yaml`).

### Phase 2: Ingestion Layer
Implemented robust scrapers for the **Apple App Store** and **Google Play Store**, including deduplication and a PII scrubber to protect user privacy.

### Phase 3: NLP Reasoning Layer
The core "brain" of the agent. Integrated Gemini embeddings with UMAP/HDBSCAN clustering. Added a **Heuristic Substance Filter** to remove low-quality reviews (e.g., "Good app", "Worst").

### Phase 4: Report Renderer
Created beautiful templates:
- **Markdown**: Optimized for Google Docs.
- **HTML/Jinja2**: Premium email design for stakeholders.

### Phase 5: MCP Delivery Integration
Integrated the Model Context Protocol to bridge the gap between the AI Agent and productivity tools (Google Workspace) without exposing sensitive OAuth tokens in the code.

### Phase 6: Audit Store & Full Orchestration
Finalized the production loop. Added a SQLite run log to track history and created the `main.py` entry point for both CLI and Web execution.

---

## 📂 Project Structure
```text
Railway_Deployment/
├── agent/            # Orchestrator & Loop Logic
├── api/              # FastAPI Backend
├── audit/            # SQLite Idempotency Store
├── config/           # Product & System Settings
├── delivery_mcp/     # MCP Client & Tools (Docs/Gmail)
├── ingestion/        # Store Scrapers & PII Scrubbing
├── nlp/              # Embeddings, Clustering, Summarization
├── public/           # Dashboard UI (HTML/CSS)
├── report/           # Markdown & HTML Templates
└── Procfile          # Railway Start Command
```

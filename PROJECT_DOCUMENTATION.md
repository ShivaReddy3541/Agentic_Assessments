# Comprehensive Project Documentation - Agentic_Assessments
**Maintainer**: ShivaReddy3541  
**Project Title**: Agentic_Assessments: Multi-Agent Research, Security Analysis, and Reporting Workspace  
**System Version**: 1.0.0 (Production Verified)  
**Date**: September 2026  

---

## 1. Project Title
**Agentic_Assessments: an autonomous multi-agent workspace for grounded Document RAG, live web intelligence, dynamic security triage, and task-aware workflow orchestration.**

---

## 2. Abstract
Agentic_Assessments is a coordinated multi-agent platform for turning mixed evidence into explainable assessments. The **Document Research Agent (RAG)**, **Autonomous Web Research Agent**, **Security Analyst Agent**, and **Master Report Generator Agent** collaborate through a central orchestrator, dynamic task decomposition, and shared blackboard memory.

The system allows enterprise operators and security researchers to upload technical specifications (PDF, DOCX, TXT), perform semantic context-grounded Q&A with 128-dimensional dense vector embeddings and exact source citations, dispatch autonomous web intelligence gathering across live search indices, triage complex multi-vector cybersecurity logs (SSH brute force, SQL injection, port scanning, privilege escalation, ransomware C2 beaconing, lateral movement, AWS IAM tampering), and execute automated multi-agent collaboration workflows that synthesize exhaustive 11-section executive master reports.

---

## 3. Problem Statement
Modern cybersecurity triage and technology intelligence workflows are constrained by fragmentation:
1. **Siloed Document Knowledge**: Internal security architecture documents, compliance guidelines, and standard operating procedures (SOPs) are static and difficult to query accurately in high-pressure incident response scenarios.
2. **Dynamic External Threat Landscape**: New vulnerabilities (CVEs), phishing kits (AiTM), and attack frameworks emerge daily, requiring analysts to constantly perform manual web searches and filter low-credibility sources.
3. **Telemetry Volume & Alert Fatigue**: Security Operations Centers (SOCs) receive thousands of raw syslog, auth, firewall, and cloud audit events daily, making manual correlation, severity classification, and immediate playbook generation time-consuming.
4. **Lack of Automated Multi-Agent Collaboration**: Existing AI assistants act as isolated chatbots rather than collaborating autonomously as a team of specialized domain agents passing structured state and verifying each other's outputs.

---

## 4. Objectives & Assignment Requirements Mapping

> **Cross-Reference**: For the complete 35-section master explanation, see [`AEGISMIND_AI_COMPLETE_PROJECT_EXPLANATION.md`](AEGISMIND_AI_COMPLETE_PROJECT_EXPLANATION.md). For setup and quickstart, see [`README.md`](README.md).

| Assignment Requirement | Technical Objective | Implemented Solution | Verified Status | Relevant Codebase Modules |
| :--- | :--- | :--- | :---: | :--- |
| **Requirement 1** | Read PDFs/documents, retrieve relevant content, answer queries with citations. | **Document Research Agent (RAG)**: Multi-format document parser (PDF, DOCX, TXT), recursive character chunker, 128-d dense semantic vector embeddings (L2-normalized cosine similarity) + Okapi BM25 hybrid ranking, and **genuine live Google Gemini model generation** with strict in-line citation attribution. | **`FULL`** *(End-to-end verified with live Google Gemini)* | `backend/agents/document_agent.py`<br>`backend/rag/parsers.py`<br>`backend/rag/chunker.py`<br>`backend/rag/vector_store.py` |
| **Requirement 2** | Search for information, summarize findings, generate structured research reports with references. | **Autonomous Web Research Agent**: Multi-source search retriever (DuckDuckGo + Wikipedia), secondary outbound HTTP crawler (`fetch_source_page` extracting 2,000 chars), domain credibility ranker, structured key findings extractor across 4 domains. | **`FULL`** | `backend/agents/research_agent.py`<br>`backend/services/search_service.py` |
| **Requirement 3** | Analyze security logs/alerts, identify threats, classify severity (LOW/MED/HIGH/CRITICAL), suggest mitigations. | **Security Analyst Agent**: Multi-format log parser & dynamic rule engine, custom SQLi and preset log triage, attack classifier, confidence scorer, dynamic IOC extractor, and prioritized mitigation playbook generator with 7 built-in presets. | **`FULL`** | `backend/agents/security_agent.py`<br>`sample_data/logs/` |
| **Requirement 4** | Build a collaborative system where 23 specialized agents collaborate to complete complex tasks automatically. | **Central Multi-Agent Orchestrator**: Dynamic task-aware agent planner, shared blackboard memory engine, inter-agent context passing pipeline, Document  Security causal dependency, and 11-section Master Report synthesis. | **`FULL`** | `backend/agents/orchestrator.py`<br>`backend/agents/report_agent.py`<br>`frontend/src/pages/WorkflowStudio.jsx` |

---

## 5. Technologies Used

### Backend Architecture
- **Language**: Python 3.11+ / Python 3.14 (Full compatibility verified on Windows)
- **API Framework**: FastAPI 0.110+ with asynchronous request routing and CORS middleware
- **Data Validation & Schemas**: Pydantic v2.6+
- **ASGI Server**: Uvicorn 0.28+
- **HTTP Client**: HTTPX 0.27+ with asynchronous connection pooling
- **Document Processing**: `pypdf` 6.16+ (pure Python PDF extraction), `python-docx` 1.2+ (Word document parsing)
- **Database / State Persistence**: SQLite 3 with WAL mode and thread-safe connection pooling
- **Testing Framework**: Pytest 9.1+ with `pytest-asyncio`

### Frontend Architecture
- **Framework**: React 18.3+ with React Hooks and functional components
- **Build Tool / Bundler**: Vite 5.4+ with Rollup WASM compatibility
- **Styling**: Tailwind CSS 3.4+ with a light operations-console design system
- **Iconography**: Lucide React 0.46+
- **Typography**: DM Sans (interface) & Space Mono (technical data)

### AI & Vector Retrieval Engine
- **LLM Providers Supported**: Google Gemini (`gemini-3.5-flash-lite`, `gemini-flash-lite-latest`, `gemini-3.1-flash-lite`), OpenAI (`gpt-4o-mini`, `gpt-4o`), Groq (`llama-3.3-70b-versatile`), Ollama (`llama3`, `mistral`), and an intelligent zero-dependency semantic heuristic fallback engine.
- **Vector Retrieval**: 128-dimensional dense semantic vector embeddings with subword semantic hashing, L2 normalization, and vector dot-product cosine similarity, combined with Okapi BM25 ranking ($k_1=1.5, b=0.75$).

---

## 6. System Architecture

```
                                  
                                     React + Vite Frontend UI    
                                     (Tailwind CSS, Glassmorphic)
                                  
                                                   HTTP / REST
                                  
                                      FastAPI Application Core   
                                  
                                                         
                           
                       Multi-Agent Orchestrator          Direct Agent Endpoints
                       (Blackboard State Engine)        
                           
                                                         
        
                                                                                
   
 Document/RAG Agent       Research Agent     Security Analyst Agt   Report Generator Agt 
           
  Text Extraction      Query Expansion      Dynamic Rule Engine   Cross-agent Synthe.
  128-d Dense Embed    Live Web Scraping    Threat Classifier     11-Section Schema  
  BM25 Hybrid Rank     Text Summarizer      Severity Scoring      Citations & Evid.  
  Source Citations     Reference Tracker    Mitigation Matrix     Export Formats     
   
                                                                                
        
                                   
                     
                      SQLite & In-Memory Storage  
                      (Docs, Reports, Workflows)  
                     
```

---

## 7. Agent Architecture

### 1. Document Research Agent (`document_agent.py`)
- **Input**: Binary files (`.pdf`, `.docx`, `.txt`, `.md`), user natural language questions, document ID filters.
- **Processing**: Extracts clean text, recursively splits into 650-character chunks with 120-character overlap, generates 128-dimensional dense semantic embedding vectors, computes hybrid similarity score (60% dense cosine + 40% BM25), filters below 0.22 relevance threshold.
- **LLM Interaction**: Injects retrieved context passages into a specialized RAG prompt that enforces strict grounding and forbids extrapolation.
- **Output**: `DocumentQueryResponse` containing the synthesized answer, confidence status (`context_found: true/false`), chunk counts, and `DocumentQueryCitation` objects with exact page and chunk coordinates.

### 2. Research Agent (`research_agent.py`)
- **Input**: High-level research topic or technical question, search depth (`brief` or `comprehensive`), maximum source count.
- **Processing**: Breaks topics into search sub-queries, executes multi-source search (Live DuckDuckGo HTML scraping, Tavily API, and Curated Cyber Intel index), evaluates domain credibility (e.g. NIST 99%, CISA 98%, MITRE 98%, OWASP 95%), extracts structured findings and direct evidence quotes.
- **LLM Interaction**: Synthesizes verified intelligence into executive summaries and strategic recommendations.
- **Output**: `ResearchReport` containing executive summary, structured key findings, verified source list with URLs, and strategic takeaways.

### 3. Security Analyst Agent (`security_agent.py`)
- **Input**: Raw security telemetry text (syslog, auth logs, Apache/Nginx web logs, Windows Event Auditing, IDS alerts, firewall logs, AWS CloudTrail JSON) or one of 7 built-in preset attack scenarios.
- **Processing**: Features `SecurityRuleEngine` for dynamic regex-based IOC extraction (IPs, accounts, ports, commands), anomaly pattern matching (brute force, SQL injection, port scanning, privilege escalation, ransomware C2 beaconing, lateral movement, IAM tampering), dynamic severity calculation (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and confidence scoring.
- **LLM Interaction**: Uses a dedicated SOC threat hunting prompt for additional contextual enrichment when configured.
- **Output**: `SecurityAnalysisResult` containing threat title, attack type, severity badge, confidence percentage, extracted IOCs, evidence quotes, and prioritized mitigation playbook steps (`IMMEDIATE`, `INVESTIGATION`, `LONG_TERM`, `DETECTION_RULE`) with copyable bash/firewall commands.

### 4. Report Generator Agent (`report_agent.py`)
- **Input**: Workflow ID, user task prompt, document excerpts, external research findings, security analysis telemetry results.
- **Processing**: Formats and unifies cross-agent intelligence into a standardized 11-section executive master security assessment.
- **LLM Interaction**: Synthesizes high-impact executive summaries and strategic conclusions.
- **Output**: `MasterReport` containing complete markdown content, structured JSON metadata, threat summaries, and remediation roadmap.

---

## 8. Agent Collaboration & Dynamic Orchestration

### Inter-Agent Communication Pattern: Shared Blackboard Architecture
The central orchestrator dynamically plans agent execution based on the task prompt and utilizes a **Blackboard State Engine** (`WorkflowState.shared_blackboard`). As each agent completes its specialized phase, it posts its structured results to a designated blackboard channel, and downstream agents actively consume upstream intelligence:
1. **Dynamic Planning**: Inspects the user task prompt to determine whether research, document RAG, and/or security triage are required.
2. **Channel 1 (`external_research`)**: Populated by the Research Agent with external threat intelligence, CVE references, and mitigation baselines.
3. **Channel 2 (`document_findings`)**: Document Agent consumes Research Agent's top findings to perform targeted semantic vector retrieval across internal corporate policies.
4. **Channel 3 (`security_analysis`)**: Security Analyst Agent cross-references live telemetry against internal policy thresholds (from Channel 2) and known attack patterns (from Channel 1).
5. **Channel 4 (`master_synthesis`)**: Report Agent reads all three channels to construct the unified 11-section Master Report.

---

## 9. RAG Pipeline
```
Document Upload (PDF / DOCX / TXT)
      
      
Text Extraction & Normalization (`parsers.py` via pypdf & docx)
      
      
Recursive Chunking (`chunker.py`: 650 chars, 120 overlap)
      
      
128-d Dense Semantic Vector Embedding (`vector_store.py`)
      
      
User Natural Language Question
      
      
Hybrid Retrieval & Fusion (60% Dense Cosine + 40% BM25)
      
       If Score < 0.22  "Cannot find answer in uploaded documents."
      
       If Relevant Chunks Found
            
            
      Prompt Construction with Source Coordinates
            
            
      LLM Generation with Citation Attribution
            
            
      Output: Answer + Verified Passages + Page Coordinates
```

---

## 10. Research Pipeline
```
High-Level Topic / Research Objective
      
      
Search Sub-Query Formulation
      
      
Multi-Source Search Execution (Live DuckDuckGo Scraping / Tavily / Intel Index)
      
      
Domain Credibility Scoring & Source Ranking
      
      
Key Findings & Direct Evidence Extraction
      
      
LLM Executive Summary & Strategic Takeaways Synthesis
      
      
Structured Research Report with Clickable References
```

---

## 11. Security Analysis Pipeline
```
Raw Telemetry Input (Syslog / Auth / Web / Windows / CloudTrail)
      
      
Record Splitting & Token Normalization
      
      
Dynamic Behavioral Rule Engine & Pattern Correlation (`SecurityRuleEngine`)
      
      
Threat Title & Attack Type Classification
      
      
Severity Assignment (LOW / MEDIUM / HIGH / CRITICAL) & Confidence %
      
      
IOC Extraction (IPs, Users, Binaries, Ports, Commands)
      
      
Prioritized Mitigation Playbook (IMMEDIATE, INVESTIGATION, LONG_TERM, DETECTION_RULE)
```

---

## 12. Multi-Agent Workflow
The Central Orchestrator (`orchestrator.py`) provides an asynchronous state machine:
- **Task-Aware Planning**: Dynamically schedules required agents based on user objective.
- **State Management**: Every workflow instance receives a unique UUID (`wf_...`), start timestamp, step execution list, blackboard dictionary, and final master report object.
- **Error Resilience**: If an individual step fails, the orchestrator logs the step exception, captures partial blackboard state, and updates status to `FAILED` with explicit error descriptions.
- **Monitoring**: Frontend visualizer polls or inspects workflow state in real time.

---

## 13. API Documentation

| HTTP Method | Endpoint Path | Description | Request Body / Params | Response Model |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & LLM status | None | JSON status object |
| `GET` | `/api/stats` | Global metrics & counts | None | `SystemStats` |
| `POST` | `/api/documents/upload` | Upload & index PDF/DOCX/TXT | `multipart/form-data` (`file`) | `DocumentUploadResponse` |
| `GET` | `/api/documents` | List all indexed documents | None | `List[DocumentMetadata]` |
| `DELETE` | `/api/documents/{id}` | Delete document & chunks | Path: `doc_id` | JSON success confirmation |
| `POST` | `/api/documents/query` | Grounded RAG Q&A query | `DocumentQueryRequest` (`query`, `doc_ids`, `top_k`) | `DocumentQueryResponse` |
| `POST` | `/api/research` | Conduct web research | `ResearchRequest` (`query`, `depth`, `max_sources`) | `ResearchReport` |
| `GET` | `/api/research/history`| List past research reports | None | `List[ResearchReport]` |
| `POST` | `/api/security/analyze` | Analyze security logs | `SecurityAnalysisRequest` (`raw_logs`, `log_type`, `preset_id`)| `SecurityAnalysisResult` |
| `GET` | `/api/security/presets`| Fetch 7 sample attack logs | None | `List[SecurityPreset]` |
| `GET` | `/api/security/history`| List past security analyses| None | `List[SecurityAnalysisResult]`|
| `POST` | `/api/agent/workflow` | Launch multi-agent workflow | `WorkflowRequest` (`task_prompt`, `document_ids`, `security_logs`)| `WorkflowState` |
| `GET` | `/api/agent/workflow/{id}`| Get workflow status & report | Path: `workflow_id` | `WorkflowState` |
| `GET` | `/api/agent/workflows` | List all workflow runs | None | `List[WorkflowState]` |
| `GET` | `/api/reports` | List all generated reports | None | `List[ReportSummary]` |
| `GET` | `/api/reports/{id}` | Get complete report by ID | Path: `report_id` | `MasterReport` |

---

## 14. Database & Storage Architecture
Storage is implemented via thread-safe SQLite (`backend/data/platform.db`) with 6 optimized relational tables:
1. `documents`: Document ID, filename, file type, file size, chunk count, upload timestamp, full raw text.
2. `document_chunks`: Chunk ID, document foreign key, document name, chunk index, page number, chunk text content.
3. `research_tasks`: Research ID, search topic, serialized JSON payload, creation timestamp.
4. `security_analyses`: Analysis ID, threat title, attack type, severity enum, confidence rating, serialized JSON, timestamp.
5. `workflow_states`: Workflow ID, task prompt, execution status enum, complete blackboard state JSON, creation timestamp.
6. `reports`: Report ID, workflow foreign key, title, report type, severity, full markdown content, serialized JSON, timestamp.

---

## 15. Frontend Architecture & Pages

1. **Dashboard (`Dashboard.jsx`)**:
   - High-level platform metrics (Documents, Chunks, Research, Threats, Workflows, Reports).
   - 1-Click Launchers for all 4 specialized modules.
   - Platform Health Radar and recent reports feed.
2. **Document Studio (`DocumentStudio.jsx`)**:
   - Drag-and-drop document upload with format validation and live indexing feedback.
   - Indexed Document Library with chunk inspection and delete capability.
   - Interactive Q&A chat console with similarity scores, source citation cards, and groundness badges.
3. **Research Hub (`ResearchHub.jsx`)**:
   - Research topic query box with depth toggles and quick suggestion chips.
   - Live research progression stepper.
   - Verified Source Gallery with credibility meters and outbound links.
   - Structured key findings cards and strategic recommendations.
4. **Security Analyzer (`SecurityAnalyzer.jsx`)**:
   - Dual-mode input: Raw log textarea + 7 built-in attack sample presets.
   - Threat banner with Severity badge (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and Confidence percentage.
   - Extracted IOC indicator tags (IPs, accounts, commands).
   - Prioritized remediation playbook cards with copyable terminal commands.
5. **Multi-Agent Studio (`WorkflowStudio.jsx`)**:
   - Multi-agent collaborative prompt editor and 3 preset complex scenarios.
   - Real-time 4-stage pipeline visualizer (`PENDING`  `RUNNING`  `COMPLETED`).
   - Shared Blackboard Memory inspector showing inter-agent data flow.
   - Complete 11-section Master Report reader and markdown download.
6. **Reports Library (`ReportsLibrary.jsx`)**:
   - Comprehensive archive of all generated reports with search and severity filter.
   - Split-pane full-screen report reader with 1-click Markdown, JSON, and Print export.

---

## 16. LLM Integration & Prompt Engineering
Each agent employs a specialized, highly structured system prompt:
- **Document Agent System Prompt**: Restricts generation strictly to retrieved document passages, mandates citation notation (`[DocName, Page X]`), and forces explicit declaration when context is absent.
- **Research Agent System Prompt**: Focuses on objective synthesis of external web intelligence, attribution to sources, and structured category/evidence extraction.
- **Security Analyst System Prompt**: Enforces strict JSON output conforming to the SOC threat hunter schema (threat title, attack type, severity, confidence, IOCs, evidence, playbooks).
- **Master Report System Prompt**: Employs a Chief Information Security Officer (CISO) persona to formulate executive summaries, threat correlations, and strategic conclusions.

---

## 17. Security Considerations
- **API Secret Management**: API keys are managed exclusively server-side through `.env` and are never exposed to client-side bundles.
- **Upload Validation & Size Constraints**: File uploads are restricted to `.pdf`, `.docx`, `.doc`, `.txt`, `.md`, and `.json`, with an enforced maximum file size of 25 MB.
- **Non-Executable Storage**: Uploaded files are parsed in memory and raw text is stored in SQLite without file execution.
- **Prompt Injection Containment**: Document context and raw log streams are isolated inside fenced XML/markdown delimiters with strict boundary instructions to prevent prompt override attacks.

---

## 18. Testing & Quality Assurance

### Automated Test Suite Results
The test suite in `backend/tests/` verifies all system layers using Pytest and `pytest-asyncio`:

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 24 items

backend/tests/test_api_endpoints.py::test_health_and_stats_endpoints PASSED [  4%]
backend/tests/test_api_endpoints.py::test_security_presets_api PASSED    [  8%]
backend/tests/test_api_endpoints.py::test_document_upload_and_query_api PASSED [ 12%]
backend/tests/test_research_api PASSED            [ 16%]
backend/tests/test_security_analyze_api PASSED    [ 20%]
backend/tests/test_workflow_api PASSED            [ 25%]
backend/tests/test_document_agent.py::test_dense_semantic_embedding_generation PASSED [ 29%]
backend/tests/test_document_agent.py::test_real_pdf_ingestion_and_retrieval PASSED [ 33%]
backend/tests/test_document_agent.py::test_document_query_unrelated_content_not_found PASSED [ 37%]
backend/tests/test_orchestrator.py::test_dynamic_agent_planning PASSED   [ 41%]
backend/tests/test_orchestrator.py::test_multi_agent_collaboration_and_context_passing PASSED [ 45%]
backend/tests/test_orchestrator.py::test_orchestrator_state_retrieval PASSED [ 50%]
backend/tests/test_remediation.py::test_r1_pdf_rag_ingestion_and_grounded_answer PASSED [ 54%]
backend/tests/test_remediation.py::test_r1_out_of_domain_query_rejected PASSED [ 58%]
backend/tests/test_remediation.py::test_r2_source_page_crawler PASSED    [ 62%]
backend/tests/test_remediation.py::test_r2_multi_domain_research_no_static_leakage PASSED [ 66%]
backend/tests/test_remediation.py::test_r3_r4_document_to_security_causal_dependency PASSED [ 70%]
backend/tests/test_remediation.py::test_r4_full_orchestration_workflow_and_master_report PASSED [ 75%]
backend/tests/test_research_agent.py::test_research_agent_workflow PASSED [ 79%]
backend/tests/test_research_agent.py::test_research_history_listing PASSED [ 83%]
backend/tests/test_security_agent.py::test_security_analysis_ssh_brute_force PASSED [ 87%]
backend/tests/test_security_agent.py::test_security_analysis_custom_arbitrary_logs PASSED [ 91%]
backend/tests/test_security_agent.py::test_security_rule_engine_standalone PASSED [ 95%]
backend/tests/test_security_agent.py::test_security_presets_available PASSED [100%]

======================= 24 passed in 155.79s (0:02:35) ========================
```

**Final Test Count**: **24 Tests Executed, 24 Passed (100% Pass Rate)**.

---

## 19. Assignment Requirement Mapping Table

| Requirement | Implementation Details | Verified Test File | Primary Implementation Files |
| :--- | :--- | :--- | :--- |
| **Requirement 1** (Document RAG Agent) | Ingestion of real PDF/DOCX/TXT, recursive chunking, 128-d dense embeddings, hybrid vector search, grounded Q&A with exact citations. | `backend/tests/test_document_agent.py` | `backend/agents/document_agent.py`<br>`backend/rag/parsers.py`<br>`backend/rag/chunker.py`<br>`backend/rag/vector_store.py` |
| **Requirement 2** (Web Research Agent) | Autonomous web search (Live DuckDuckGo scraping & Tavily), source credibility scoring, key findings extraction, citation tracking. | `backend/tests/test_research_agent.py` | `backend/agents/research_agent.py`<br>`backend/services/search_service.py` |
| **Requirement 3** (Security Analyst Agent) | Multi-format log triage & dynamic rule engine, custom log analysis, attack classification, severity scoring, IOC extraction, remediation playbooks (7 presets). | `backend/tests/test_security_agent.py` | `backend/agents/security_agent.py`<br>`sample_data/logs/` |
| **Requirement 4** (Multi-Agent Orchestrator) | Task-aware orchestrator, shared blackboard state engine, inter-agent context passing, 11-section master report synthesis. | `backend/tests/test_orchestrator.py` | `backend/agents/orchestrator.py`<br>`backend/agents/report_agent.py`<br>`frontend/src/pages/WorkflowStudio.jsx` |

---

## 20. Step-by-Step Viva & Professor Demonstration Guide

### Demo 1: Document Intelligence & Grounded RAG (Requirement 1)
1. Open the UI at `http://127.0.0.1:5173/` and click the **Document RAG** tab.
2. Select or upload `enterprise_cloud_security_controls.pdf` (or `cloud_security_architecture.txt`).
3. Click sample question: *"What are the mandatory MFA and IAM access requirements?"* and click **Ask**.
4. Observe the grounded answer citing FIDO2/WebAuthn, short-lived STS tokens, and the exact chunk/page citations with similarity scores.
5. Enter an unrelated query (e.g., *"How to make pizza dough?"*) and observe that the agent explicitly reports that the information cannot be found in the uploaded documents.

### Demo 2: Autonomous Web Research (Requirement 2)
1. Click the **Research Hub** tab.
2. Select the suggested topic: *"Current challenges in Zero Trust Architecture and AiTM phishing defenses"*.
3. Click **Investigate**.
4. Observe the synthesized findings, strategic takeaways, and verified source cards showing credibility ratings (NIST 99%, CISA 98%, MITRE 98%).

### Demo 3: Security Telemetry & Threat Analysis (Requirement 3)
1. Click the **Security Analyzer** tab.
2. Select the preset: **"SSH Brute-Force & Account Takeover"** (or paste custom logs).
3. Click **Execute Threat Analysis**.
4. Review the **CRITICAL** severity badge, 96% confidence score, extracted IOCs (`198.51.100.42`, `deploy`, `root`), and the 4 prioritized mitigation playbooks with copyable bash commands.

### Demo 4: Multi-Agent Collaboration (Requirement 4)
1. Click the **Multi-Agent Studio** tab.
2. Click **Execute Multi-Agent Workflow**.
3. Watch the visual pipeline stepper progress across all 4 steps:
   - Step 1: Research Agent (External Threat & Intel Research)
   - Step 2: Document Agent (Internal Architecture & Policy Retrieval consuming Research context)
   - Step 3: Security Analyst Agent (Security Telemetry & Threat Analysis cross-correlated with internal policy)
   - Step 4: Report Agent (Multi-Agent Synthesis & Master Report Generation)
4. Click on the **Inter-Agent Shared Blackboard State** sub-tabs to inspect the raw JSON data passed between agents.
5. Review the comprehensive **11-Section Master Security Assessment** and click **Download Markdown**.

---

## 21. Limitations
1. **Local Vector Store Scale**: The in-memory hybrid vector store is optimized for documents up to several hundred megabytes; enterprise deployments with billions of embeddings would require a distributed vector database like Milvus or Pinecone.
2. **Search Rate Limits**: Public search APIs (e.g. DuckDuckGo / Tavily free tier) have rate limitations during high-frequency concurrent querying.
3. **Synchronous Workflow Execution**: Very long-running multi-agent workflows (over 2 minutes) currently run within standard HTTP timeouts; integrating Redis task queues (Celery/Temporal) would enhance extreme asynchronous scaling.

---

## 22. Future Enhancements
1. **Automated SIEM & SOAR Integration**: Adding direct webhooks to Splunk, Microsoft Sentinel, and AWS Security Hub to trigger automated playbooks.
2. **Dynamic Agent Spawning**: Enabling the Orchestrator to spawn arbitrary numbers of sub-agents dynamically based on query complexity.
3. **Graph-Based RAG (GraphRAG)**: Constructing knowledge graph entity relationships across uploaded architecture documents.

---

## 23. Conclusion
Agentic_Assessments successfully satisfies and exceeds all four requirements of **Applied Agentic AI Assignment 2**. The platform demonstrates that specialized AI agents operating under a central orchestrator with shared blackboard memory can perform end-to-end research, document intelligence, and cybersecurity threat triage autonomously, producing high-impact, verifiable results for enterprise cyber defense.



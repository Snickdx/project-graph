# Requirements Graph Generator

This project generates a Neo4j graph database from an Excel spreadsheet containing software engineering requirements and their relationships, with advanced RAG (Retrieval Augmented Generation) capabilities for natural language querying.

## 🏗️ Project Structure

```
SE ReqGraph/
├── 📁 scripts/           # Python scripts and tools
│   ├── rag_query.py      # Original RAG system with LLM
│   ├── hybrid_rag.py     # Fast hybrid RAG with embeddings
│   ├── excel_to_json.py  # Excel to JSON converter
│   ├── test_rag.py       # RAG testing utilities
│   └── ...
├── 📁 data/              # Data files and spreadsheets
│   ├── graph_model_sample.xlsx
│   └── project graph.xlsx
├── 📁 exports/           # Generated exports and outputs
│   └── *.json            # JSON exports from Excel
├── 📁 docs/              # Documentation and diagrams
│   ├── graph.png         # Graph model visualization
│   └── ...
├── 📁 config/            # Configuration files and templates
│   ├── .env              # Environment variables (not in repo)
│   ├── .env.example      # Environment variables template
│   ├── full.cypher       # Complete Cypher queries
│   └── ...
├── 📁 tests/             # Test files and utilities
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Prerequisites

- Python 3.9+
- Neo4j Database (configured for Neo4j Aura)
- Ollama (for local LLM) or OpenAI API key
- Excel file with requirements data (see structure below)

## 🚀 Quick Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
   - Copy `config/.env.example` to `config/.env`
   - Update your Neo4j credentials in `config/.env`
   - Verify `EXCEL_FILE` points to your data file (defaults to converted project graph)

3. **Set up AI models (choose one):**

   **Option A: Local LLM (Recommended)**
   ```bash
   # Install Ollama from https://ollama.ai/download/windows
   ollama pull llama2
   ```
   
   **Option B: OpenAI API**
   ```bash
   # Add OPENAI_API_KEY to your config/.env file
   ```

4. **Run the project:**
   
   **Option A: Interactive Runner (Recommended)**
   ```bash
   python run.py
   ```
   This opens an interactive menu with all project functions.
   
   **Option B: Manual Script Execution**
   ```bash
   # Initialize database
   python scripts/init.py
   
   # Run fast RAG system
   python scripts/hybrid_rag.py
   ```

Note: The `config/.env` file is ignored by git to keep your credentials secure.

## Excel File Structure

The Excel file (`graph_model_sample.xlsx`) contains multiple sheets representing different entities in the requirements graph. Each sheet must have an `id` column, and includes additional columns specific to that entity type. Below is the structure for each sheet with example data:

### Project Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique project identifier | PROJ-001 |
| name | Project name | Customer Portal Redesign |
| start_date | Project start date | 2025-01-01 |
| end_date | Project end date | 2025-12-31 |
| description | Project description | Modernization of customer portal interface |

### Budget Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique budget identifier | BUD-001 |
| amount | Total budget amount | 500000 |
| currency | Currency code | USD |
| fiscal_year | Budget year | 2025 |

### Line_Item Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique line item identifier | LI-001 |
| description | Item description | Development Team |
| amount | Cost amount | 250000 |
| category | Budget category | Labor |

### Stakeholder Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique stakeholder identifier | STK-001 |
| name | Stakeholder name | John Smith |
| department | Department name | IT |
| email | Contact email | john.smith@company.com |

### Role Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique role identifier | ROLE-001 |
| name | Role name | Product Owner |
| responsibilities | Role responsibilities | Product backlog management |

### Feature Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique feature identifier | FEAT-001 |
| name | Feature name | Single Sign-On |
| priority | Priority level | High |
| status | Implementation status | In Progress |

### Functional_Requirement Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique functional requirement ID | FR-001 |
| description | Detailed description | Users can log in using Google accounts |
| acceptance_criteria | Testing criteria | Successful Google OAuth login flow |
| type | Requirement type | Security |
| priority | Priority level | Critical |

### Domain_Knowledge Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique domain knowledge ID | DK-001 |
| area | Knowledge domain area | Authentication Protocols |
| description | Knowledge description | OAuth 2.0 implementation expertise |
| level | Proficiency level | Expert |
| source | Knowledge source | Certification, Experience |

### Constraint Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique constraint ID | CON-001 |
| type | Constraint type | Technical |
| description | Constraint description | Must comply with GDPR |

### Goal Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique goal ID | GOAL-001 |
| description | Goal description | Improve user login experience |
| success_metric | Success measure | 50% reduction in login issues |

### Task Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique task ID | TASK-001 |
| name | Task name | Implement OAuth flow |
| assignee | Task owner | dev.team@company.com |
| status | Current status | In Progress |
| due_date | Completion date | 2025-03-01 |

### Artifact Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique artifact ID | ART-001 |
| name | Artifact name | API Documentation |
| type | Artifact type | Documentation |
| location | Storage location | docs/api/v1/ |

### Decision Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique decision ID | DEC-001 |
| description | Decision details | Use OAuth 2.0 for authentication |
| date | Decision date | 2025-02-15 |
| rationale | Decision reasoning | Industry standard, better security |

### Additional Sheets
The following sheets follow similar patterns with appropriate columns for their specific needs:
- Client
- Qual_Scenario (Quality Scenarios)
- Goal_Quotation
- Priority_Level
- KPI
- Evaluation
- Timeline
- Milestone
- Context
- Business
- Technical
- Adjacent_System
- Input_From_Product
- Output_From_Product

Note: All sheets must include the `id` column. Additional columns can be added as needed for specific project requirements.

## 💡 Usage

### 1. Initialize the Graph Database
```bash
python scripts/init.py
```
- Reads Excel data from `data/` folder
- Creates nodes and relationships in Neo4j
- Populates the complete requirements graph

### 2. Query with Natural Language (RAG)

**🚀 Fast Hybrid RAG (Recommended)**
```bash
python scripts/hybrid_rag.py
```
- ⚡ **< 1 second** response for common queries
- 🧠 Uses embeddings + pre-built templates
- 🔄 LLM fallback for complex questions

**🤖 Original RAG (Full LLM)**
```bash
python scripts/rag_query.py
```
- 🐌 3-5 seconds per query
- 🧠 Full LLM processing for all queries
- 🔧 More flexible for unusual questions

### 3. Data Management

**Export to JSON:**
```bash
python scripts/excel_to_json.py
```
- Converts Excel to structured JSON
- Includes data quality analysis
- Exports to `exports/` folder

**Update Excel Data:**
- Modify files in `data/` folder
- Re-run initialization script

### 4. Example Natural Language Queries
- "Who are the stakeholders?"
- "What functional requirements exist?"
- "Show me all features and their priorities"
- "Which stakeholders have domain knowledge in authentication?"
- "What requirements are related to security?"

## Relationship Rules

The script creates relationships between different types of nodes following predefined rules, including:

- Project → Budget (HAS_BUDGET)
- Budget → Line_Item (HAS_LINE_ITEM)
- Project → Stakeholder (HAS_STAKEHOLDER)
- Stakeholder → Role (PLAYS_ROLE)
- Stakeholder → Domain_Knowledge (HAS_DOMAIN_KNOWLEDGE)
- Project → Functional_Requirement (HAS_FUNCTIONAL_REQUIREMENT)
- Functional_Requirement → Stakeholder (RAISED_BY)
- Functional_Requirement → Feature (SATISFIED_BY)
- Functional_Requirement → Domain_Knowledge (REQUIRES_DOMAIN_KNOWLEDGE)
- And many more (see `init.py` for complete list)

## 📁 Key Files & Directories

### Scripts (`scripts/`)
- **`hybrid_rag.py`**: Fast RAG system with embeddings (⚡ recommended)
- **`rag_query.py`**: Original RAG system with full LLM processing
- **`excel_to_json.py`**: Excel to JSON converter with data analysis
- **`init.py`**: Database initialization script
- **`test_rag*.py`**: Testing utilities for RAG systems

### Data (`data/`)
- **`graph_model_sample.xlsx`**: Main Excel template with requirements data
- **`project graph.xlsx`**: Alternative project data file

### Configuration (`config/`)
- **`.env`**: Your environment configuration (not in version control)
- **`.env.example`**: Environment variables template
- **`full.cypher`**: Complete Cypher query set for manual operations

### Documentation (`docs/`)
- **`graph.png`**: Visual representation of the graph model
- Additional documentation and diagrams

### Exports (`exports/`)
- **`*.json`**: Generated JSON exports from Excel data
- Data analysis reports and summaries

### Root Directory
- **`.env`**: Your environment configuration (not in version control)
- **`.gitignore`**: Git ignore rules
- **`requirements.txt`**: Python dependencies
- **`README.md`**: This documentation

## License

This project is proprietary and confidential.
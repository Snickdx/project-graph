# Requirements Graph Generator

This project generates a Neo4j graph database from an Excel spreadsheet containing software engineering requirements and their relationships.

## Prerequisites

- Python 3.9+
- Neo4j Database (configured for Neo4j Aura)
- Excel file with requirements data (see structure below)

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Update the `.env` file with your Neo4j credentials:
```env
NEO4J_URI=your-neo4j-uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=your-instance-id
AURA_INSTANCENAME=your-instance-name
EXCEL_FILE=graph_model_sample.xlsx
```

3. Prepare your Excel file according to the expected structure (see below).

Note: The `.env` file is ignored by git to keep your credentials secure. Never commit sensitive credentials to version control.

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

### Requirement Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique requirement ID | REQ-001 |
| description | Requirement description | System must support OAuth 2.0 |
| type | Requirement type | Security |
| priority | Priority level | Critical |

### Functional_Requirement Sheet
| Column | Description | Example |
|--------|-------------|---------|
| id | Unique functional requirement ID | FR-001 |
| description | Detailed description | Users can log in using Google accounts |
| acceptance_criteria | Testing criteria | Successful Google OAuth login flow |

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

## Usage

Run the initialization script:

```bash
python init.py
```

This will:
1. Read the Excel file
2. Create nodes for each entry in the sheets
3. Create relationships between nodes based on predefined rules
4. Generate a complete requirements graph in Neo4j

## Relationship Rules

The script creates relationships between different types of nodes following predefined rules, including:

- Project → Budget (HAS_BUDGET)
- Budget → Line_Item (HAS_LINE_ITEM)
- Project → Stakeholder (HAS_STAKEHOLDER)
- Stakeholder → Role (PLAYS_ROLE)
- And many more (see `init.py` for complete list)

## Files

- `init.py`: Main script for creating the graph
- `requirements.txt`: Python dependencies
- `graph_model_sample.xlsx`: Excel template for requirements data
- `init.cypher`: Cypher queries for graph initialization
- `full.cypher`: Complete Cypher query set
- `graph.png`: Visual representation of the graph model
- `.env`: Configuration file with credentials (not in version control)
- `.env.example`: Template for environment variables
- `.gitignore`: Specifies which files Git should ignore

## License

This project is proprietary and confidential.
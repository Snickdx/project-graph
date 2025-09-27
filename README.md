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

The Excel file (`graph_model_sample.xlsx`) should contain the following sheets:

- Project
- Budget
- Line_Item
- Stakeholder
- Role
- Client
- Feature
- Requirement
- Functional_Requirement
- Constraint
- Qual_Scenario
- Artifact
- Decision
- Goal
- Goal_Quotation
- Priority_Level
- KPI
- Evaluation
- Timeline
- Milestone
- Task
- Context
- Business
- Technical
- Adjacent_System
- Input_From_Product
- Output_From_Product

Each sheet should have at minimum an `id` column, and can contain additional properties as needed.

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
import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === CONFIG ===
EXCEL_FILE = os.getenv("EXCEL_FILE")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
AURA_INSTANCEID = os.getenv("AURA_INSTANCEID")
AURA_INSTANCENAME = os.getenv("AURA_INSTANCENAME")

# === CONNECT TO NEO4J ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def run_query(query, params=None):
    with driver.session() as session:
        session.run(query, params or {})

# === LOAD SHEETS ===
xls = pd.ExcelFile(EXCEL_FILE)
sheets = {name: pd.read_excel(EXCEL_FILE, sheet_name=name).fillna("") for name in xls.sheet_names}

# === CREATE NODES ===
for sheet, df in sheets.items():
    for _, row in df.iterrows():
        if "id" not in row or row["id"] == "":
            continue
        props = {k: str(v) for k, v in row.items() if v != "" and k != "id"}
        query = f"""
        MERGE (n:{sheet} {{id: $id}})
        SET n += $props
        """
        run_query(query, {"id": str(row["id"]), "props": props})

print("✅ Nodes created.")

# === GET THE SINGLE PROJECT ID ===
project_df = sheets.get("Project")
if project_df is None or project_df.empty:
    raise ValueError("❌ No Project found in the Excel file")
PROJECT_ID = str(project_df.iloc[0]["id"])

# === RELATIONSHIP RULES (anchored to one project) ===
rules = [
    ("Project", "Budget", "HAS_BUDGET"),
    ("Budget", "Line_Item", "HAS_LINE_ITEM"),
    ("Project", "Stakeholder", "HAS_STAKEHOLDER"),
    ("Stakeholder", "Role", "PLAYS_ROLE"),
    ("Project", "Client", "HAS_CLIENT"),
    ("Client", "Stakeholder", "OWNED_BY"),
    ("Project", "Feature", "DELIVERS"),
    ("Project", "Requirement", "HAS_REQUIREMENT"),
    ("Requirement", "Functional_Requirement", "HAS_FUNCTIONAL"),
    ("Requirement", "Stakeholder", "RAISED_BY"),
    ("Requirement", "Feature", "SATISFIED_BY"),
    ("Project", "Constraint", "HAS_CONSTRAINT"),
    ("Feature", "Constraint", "HAS_CONSTRAINT"),
    ("Qual_Scenario", "Constraint", "SATISFIES"),
    ("Project", "Qual_Scenario", "HAS_QUAL_SCENARIO"),
    ("Feature", "Artifact", "PRODUCES"),
    ("Artifact", "Stakeholder", "USED_BY"),
    ("Project", "Artifact", "HAS_ARTIFACT"),
    ("Project", "Decision", "HAS_DECISION"),
    ("Decision", "Stakeholder", "MADE_BY"),
    ("Decision", "Feature", "AFFECTS"),
    ("Project", "Goal", "HAS_GOAL"),
    ("Stakeholder", "Goal_Quotation", "STATES"),
    ("Goal_Quotation", "Goal", "EXPRESSES"),
    ("Goal", "Priority_Level", "HAS_PRIORITY"),
    ("Goal", "Feature", "SUPPORTED_BY"),
    ("Goal", "Stakeholder", "OWNED_BY"),
    ("KPI", "Goal", "MEASURES"),
    ("Evaluation", "Project", "EVALUATES"),
    ("Project", "Timeline", "HAS_TIMELINE"),
    ("Project", "Milestone", "HAS_MILESTONE"),
    ("Feature", "Task", "IMPLEMENTED_BY"),
    ("Project", "Task", "HAS_TASK"),
    ("Project", "Context", "OPERATES_IN"),
    ("Context", "Business", "CAN_BE"),
    ("Context", "Technical", "CAN_BE"),
    ("Context", "Adjacent_System", "INTERFACES_WITH"),
    ("Adjacent_System", "Input_From_Product", "RECEIVES"),
    ("Adjacent_System", "Output_From_Product", "SENDS"),
]

# === RELATIONSHIP CREATION ===
for start_label, end_label, rel_type in rules:
    start_df = sheets.get(start_label)
    end_df = sheets.get(end_label)
    if start_df is None or end_df is None or start_df.empty or end_df.empty:
        continue
    for _, srow in start_df.iterrows():
        for _, erow in end_df.iterrows():
            if srow["id"] != "" and erow["id"] != "":
                query = f"""
                MATCH (a:{start_label} {{id: $start_id}})
                MATCH (b:{end_label} {{id: $end_id}})
                MERGE (a)-[:`{rel_type}`]->(b)
                """
                run_query(query,{
                    "start_id": str(srow["id"]),
                    "end_id": str(erow["id"])
                })

print(f"✅ Relationships created for Project {PROJECT_ID}")

driver.close()

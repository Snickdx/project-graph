import pandas as pd
import os

# Load the existing Excel file
excel_file = "graph_model_sample.xlsx"

# Check if file exists
if os.path.exists(excel_file):
    # Read all sheets from the existing file
    xls = pd.ExcelFile(excel_file)
    sheets_data = {}
    
    for sheet_name in xls.sheet_names:
        if sheet_name != "Requirement":  # Skip the Requirement sheet
            sheets_data[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print(f"Loaded existing sheets (excluding Requirement): {list(sheets_data.keys())}")
else:
    # Create new sheets data if file doesn't exist
    sheets_data = {}
    print("Creating new Excel file structure")

# Add or update Domain_Knowledge sheet
domain_knowledge_data = {
    'id': ['DK-001', 'DK-002', 'DK-003', 'DK-004', 'DK-005'],
    'area': ['Authentication Protocols', 'Database Design', 'UI/UX Design', 'Security Compliance', 'API Development'],
    'description': [
        'OAuth 2.0 implementation expertise',
        'Relational database optimization',
        'User interface design principles',
        'GDPR and data protection regulations',
        'RESTful API design and implementation'
    ],
    'level': ['Expert', 'Advanced', 'Intermediate', 'Expert', 'Advanced'],
    'source': ['Certification, Experience', 'Experience', 'Training, Projects', 'Certification', 'Experience']
}
sheets_data['Domain_Knowledge'] = pd.DataFrame(domain_knowledge_data)

# Update or create sample data for other key sheets if they don't exist
if 'Project' not in sheets_data:
    project_data = {
        'id': ['PROJ-001'],
        'name': ['Customer Portal Redesign'],
        'start_date': ['2025-01-01'],
        'end_date': ['2025-12-31'],
        'description': ['Modernization of customer portal interface']
    }
    sheets_data['Project'] = pd.DataFrame(project_data)

if 'Stakeholder' not in sheets_data:
    stakeholder_data = {
        'id': ['STK-001', 'STK-002', 'STK-003', 'STK-004'],
        'name': ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Lisa Anderson'],
        'department': ['IT', 'Design', 'Security', 'Development'],
        'email': ['john.smith@company.com', 'sarah.johnson@company.com', 'mike.chen@company.com', 'lisa.anderson@company.com']
    }
    sheets_data['Stakeholder'] = pd.DataFrame(stakeholder_data)

if 'Functional_Requirement' not in sheets_data:
    functional_requirement_data = {
        'id': ['FR-001', 'FR-002', 'FR-003', 'FR-004'],
        'description': [
            'Users can log in using Google accounts',
            'System must encrypt all sensitive data',
            'Interface must be mobile responsive',
            'API must handle 1000 concurrent requests'
        ],
        'acceptance_criteria': [
            'Successful Google OAuth login flow',
            'AES-256 encryption for all PII data',
            'Responsive design works on mobile devices',
            'Load testing shows 1000+ concurrent users'
        ],
        'type': ['Authentication', 'Security', 'UI/UX', 'Performance'],
        'priority': ['Critical', 'High', 'Medium', 'High']
    }
    sheets_data['Functional_Requirement'] = pd.DataFrame(functional_requirement_data)

if 'Feature' not in sheets_data:
    feature_data = {
        'id': ['FEAT-001', 'FEAT-002', 'FEAT-003'],
        'name': ['Single Sign-On', 'Data Encryption', 'Mobile Interface'],
        'priority': ['High', 'Critical', 'Medium'],
        'status': ['In Progress', 'Planned', 'In Progress']
    }
    sheets_data['Feature'] = pd.DataFrame(feature_data)

if 'Role' not in sheets_data:
    role_data = {
        'id': ['ROLE-001', 'ROLE-002', 'ROLE-003', 'ROLE-004'],
        'name': ['Product Owner', 'Security Architect', 'UI Designer', 'Backend Developer'],
        'responsibilities': [
            'Product backlog management',
            'Security requirements and compliance',
            'User interface design and testing',
            'API development and database design'
        ]
    }
    sheets_data['Role'] = pd.DataFrame(role_data)

# Add other essential sheets with minimal data if they don't exist
essential_sheets = {
    'Budget': {'id': ['BUD-001'], 'amount': [500000], 'currency': ['USD'], 'fiscal_year': [2025]},
    'Line_Item': {'id': ['LI-001'], 'description': ['Development Team'], 'amount': [250000], 'category': ['Labor']},
    'Client': {'id': ['CLI-001'], 'name': ['ABC Corporation'], 'contact_person': ['Jane Doe']},
    'Constraint': {'id': ['CON-001'], 'type': ['Technical'], 'description': ['Must comply with GDPR']},
    'Goal': {'id': ['GOAL-001'], 'description': ['Improve user login experience'], 'success_metric': ['50% reduction in login issues']},
    'Task': {'id': ['TASK-001'], 'name': ['Implement OAuth flow'], 'assignee': ['dev.team@company.com'], 'status': ['In Progress'], 'due_date': ['2025-03-01']},
    'Artifact': {'id': ['ART-001'], 'name': ['API Documentation'], 'type': ['Documentation'], 'location': ['docs/api/v1/']},
    'Decision': {'id': ['DEC-001'], 'description': ['Use OAuth 2.0 for authentication'], 'date': ['2025-02-15'], 'rationale': ['Industry standard, better security']},
    'Qual_Scenario': {'id': ['QS-001'], 'scenario': ['Peak load handling'], 'description': ['System handles 1000 concurrent users']},
    'Goal_Quotation': {'id': ['GQ-001'], 'quotation': ['Users want faster login'], 'source': ['User survey']},
    'Priority_Level': {'id': ['PL-001'], 'level': ['Critical'], 'weight': [1]},
    'KPI': {'id': ['KPI-001'], 'name': ['Login Success Rate'], 'target': ['99.5%']},
    'Evaluation': {'id': ['EVAL-001'], 'type': ['Performance'], 'result': ['Passed']},
    'Timeline': {'id': ['TL-001'], 'phase': ['Development'], 'start_date': ['2025-01-01'], 'end_date': ['2025-06-30']},
    'Milestone': {'id': ['MS-001'], 'name': ['MVP Release'], 'date': ['2025-06-30']},
    'Context': {'id': ['CTX-001'], 'type': ['Business'], 'description': ['E-commerce platform']},
    'Business': {'id': ['BUS-001'], 'aspect': ['Customer retention'], 'impact': ['High']},
    'Technical': {'id': ['TECH-001'], 'aspect': ['Database performance'], 'requirement': ['Sub-second response']},
    'Adjacent_System': {'id': ['ADJ-001'], 'name': ['Payment Gateway'], 'interface': ['REST API']},
    'Input_From_Product': {'id': ['INP-001'], 'data_type': ['User credentials'], 'format': ['JSON']},
    'Output_From_Product': {'id': ['OUT-001'], 'data_type': ['Authentication token'], 'format': ['JWT']}
}

for sheet_name, data in essential_sheets.items():
    if sheet_name not in sheets_data:
        sheets_data[sheet_name] = pd.DataFrame(data)

# Write all sheets to the Excel file
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    for sheet_name, df in sheets_data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Added sheet: {sheet_name} with {len(df)} rows")

print(f"\n✅ Updated Excel file '{excel_file}' with new structure")
print("✅ Removed 'Requirement' sheet")
print("✅ Added 'Domain_Knowledge' sheet")
print(f"✅ Total sheets: {len(sheets_data)}")
print(f"Sheet names: {list(sheets_data.keys())}")
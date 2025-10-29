#!/usr/bin/env python3
"""
Project Graph Converter
========================
Converts the specific "project graph.xlsx" file to JSON, removes requirements,
adds domain knowledge, and exports back to Excel.
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

def load_project_graph_excel(file_path):
    """Load the project graph Excel file"""
    try:
        print(f"📂 Loading Excel file: {file_path}")
        
        # Get all sheet names first
        xl_file = pd.ExcelFile(file_path)
        sheet_names = xl_file.sheet_names
        print(f"📋 Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
        
        # Load all sheets
        sheets_data = {}
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if not df.empty:
                    # Convert to records and clean NaN values and timestamps
                    records = df.fillna('').to_dict('records')
                    
                    # Clean up non-JSON serializable data types
                    cleaned_records = []
                    for record in records:
                        cleaned_record = {}
                        for key, value in record.items():
                            if pd.isna(value):
                                cleaned_record[key] = ''
                            elif hasattr(value, 'isoformat'):  # datetime/timestamp
                                cleaned_record[key] = value.isoformat() if not pd.isna(value) else ''
                            else:
                                cleaned_record[key] = str(value) if value != '' else ''
                        cleaned_records.append(cleaned_record)
                    
                    sheets_data[sheet_name] = cleaned_records
                    print(f"  ✅ {sheet_name}: {len(records)} records")
                else:
                    print(f"  ⚠️ {sheet_name}: Empty sheet")
            except Exception as e:
                print(f"  ❌ {sheet_name}: Error loading - {e}")
        
        return sheets_data, sheet_names
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None, None

def remove_requirements_add_domain_knowledge(sheets_data):
    """Remove requirement entities and add domain knowledge"""
    print("\n🔄 Updating data structure...")
    
    changes = []
    
    # Remove any requirement-related sheets
    requirement_sheets = [key for key in sheets_data.keys() 
                         if 'requirement' in key.lower() or 'req' in key.lower()]
    
    for sheet in requirement_sheets:
        removed_count = len(sheets_data[sheet])
        del sheets_data[sheet]
        changes.append(f"Removed {sheet} sheet ({removed_count} records)")
        print(f"  ❌ Removed {sheet}: {removed_count} records")
    
    # Add comprehensive Domain Knowledge data if not exists
    if 'Domain_Knowledge' not in sheets_data:
        domain_knowledge_data = [
            {
                "id": "DK-001",
                "area": "Authentication Protocols",
                "description": "OAuth 2.0, SAML, and multi-factor authentication implementation expertise",
                "level": "Expert",
                "source": "Industry Certification, 5+ years experience"
            },
            {
                "id": "DK-002", 
                "area": "Database Design",
                "description": "Relational and NoSQL database architecture, optimization, and scaling",
                "level": "Intermediate",
                "source": "Formal training, project experience"
            },
            {
                "id": "DK-003",
                "area": "Cloud Architecture",
                "description": "AWS, Azure, and Google Cloud platform design and deployment",
                "level": "Expert", 
                "source": "Cloud certification, enterprise projects"
            },
            {
                "id": "DK-004",
                "area": "Security Compliance",
                "description": "GDPR, SOX, PCI-DSS compliance and security audit processes",
                "level": "Advanced",
                "source": "Compliance training, audit experience"
            },
            {
                "id": "DK-005",
                "area": "API Integration",
                "description": "RESTful API design, GraphQL, and microservices architecture",
                "level": "Intermediate",
                "source": "Development experience, technical documentation"
            },
            {
                "id": "DK-006",
                "area": "Project Management",
                "description": "Agile methodologies, Scrum, and software project lifecycle management",
                "level": "Advanced",
                "source": "PMP certification, 10+ projects managed"
            },
            {
                "id": "DK-007",
                "area": "Business Analysis", 
                "description": "Requirements gathering, stakeholder management, and process analysis",
                "level": "Expert",
                "source": "BA certification, cross-industry experience"
            },
            {
                "id": "DK-008",
                "area": "Quality Assurance",
                "description": "Test automation, performance testing, and quality metrics",
                "level": "Intermediate",
                "source": "QA training, testing framework experience"
            }
        ]
        
        sheets_data['Domain_Knowledge'] = domain_knowledge_data
        changes.append(f"Added Domain_Knowledge sheet ({len(domain_knowledge_data)} records)")
        print(f"  ✅ Added Domain_Knowledge: {len(domain_knowledge_data)} records")
    
    # Add missing relationships if Relationships sheet exists
    if 'Relationships' in sheets_data:
        original_rel_count = len(sheets_data['Relationships'])
        
        # Add stakeholder-domain knowledge relationships
        stakeholder_ids = []
        if 'Stakeholder' in sheets_data:
            stakeholder_ids = [s.get('id', '') for s in sheets_data['Stakeholder'] if s.get('id')]
        
        domain_knowledge_ids = [dk['id'] for dk in sheets_data['Domain_Knowledge']]
        
        # Add some example relationships
        new_relationships = []
        if stakeholder_ids:
            # Map stakeholders to domain knowledge areas
            stakeholder_dk_mapping = [
                (stakeholder_ids[0] if len(stakeholder_ids) > 0 else 'STK-001', 'DK-001'),  # Auth expert
                (stakeholder_ids[0] if len(stakeholder_ids) > 0 else 'STK-001', 'DK-007'),  # BA expert
                (stakeholder_ids[1] if len(stakeholder_ids) > 1 else 'STK-002', 'DK-002'),  # DB expert
                (stakeholder_ids[1] if len(stakeholder_ids) > 1 else 'STK-002', 'DK-003'),  # Cloud expert
                (stakeholder_ids[2] if len(stakeholder_ids) > 2 else 'STK-003', 'DK-004'),  # Security expert
                (stakeholder_ids[2] if len(stakeholder_ids) > 2 else 'STK-003', 'DK-006'),  # PM expert
            ]
            
            for stakeholder_id, dk_id in stakeholder_dk_mapping:
                new_relationships.append({
                    'from_entity': stakeholder_id,
                    'from_type': 'Stakeholder',
                    'relationship_type': 'HAS_DOMAIN_KNOWLEDGE',
                    'to_entity': dk_id,
                    'to_type': 'Domain_Knowledge',
                    'description': f'Stakeholder {stakeholder_id} has expertise in {dk_id}'
                })
        
        # Add the new relationships
        sheets_data['Relationships'].extend(new_relationships)
        new_rel_count = len(sheets_data['Relationships'])
        added_relationships = new_rel_count - original_rel_count
        
        if added_relationships > 0:
            changes.append(f"Added {added_relationships} domain knowledge relationships")
            print(f"  ✅ Added {added_relationships} new relationships")
    
    else:
        # Create relationships sheet if it doesn't exist
        new_relationships = []
        
        # Add basic relationships based on available data
        if 'Stakeholder' in sheets_data and 'Domain_Knowledge' in sheets_data:
            stakeholder_ids = [s.get('id', '') for s in sheets_data['Stakeholder'] if s.get('id')]
            
            for i, stakeholder_id in enumerate(stakeholder_ids[:3]):  # Limit to first 3
                dk_areas = ['DK-001', 'DK-007', 'DK-006']  # Auth, BA, PM
                if i < len(dk_areas):
                    new_relationships.append({
                        'from_entity': stakeholder_id,
                        'from_type': 'Stakeholder', 
                        'relationship_type': 'HAS_DOMAIN_KNOWLEDGE',
                        'to_entity': dk_areas[i],
                        'to_type': 'Domain_Knowledge',
                        'description': f'Stakeholder {stakeholder_id} has domain expertise'
                    })
        
        if new_relationships:
            sheets_data['Relationships'] = new_relationships
            changes.append(f"Created Relationships sheet ({len(new_relationships)} relationships)")
            print(f"  ✅ Created Relationships: {len(new_relationships)} records")
    
    return sheets_data, changes

def export_to_json(sheets_data, changes, original_file):
    """Export the updated data to JSON format"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create structured JSON
    json_data = {
        "metadata": {
            "source_file": original_file,
            "export_timestamp": datetime.now().isoformat(),
            "total_sheets": len(sheets_data),
            "sheet_names": list(sheets_data.keys()),
            "update_reason": "Removed requirements, added domain knowledge and relationships",
            "changes_made": changes
        },
        "nodes": sheets_data,
        "summary": {
            "total_nodes": sum(len(entities) for entities in sheets_data.values() if isinstance(entities, list)),
            "node_counts": {sheet: len(entities) for sheet, entities in sheets_data.items() if isinstance(entities, list)}
        }
    }
    
    # Save JSON file
    output_file = Path("exports") / f"project_graph_updated_{timestamp}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON exported: {output_file}")
    return str(output_file)

def convert_json_to_excel(json_file):
    """Convert the JSON back to Excel using our existing converter"""
    print(f"\n🔄 Converting JSON back to Excel...")
    
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            "scripts/json_to_excel.py", 
            json_file
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Excel conversion completed successfully!")
            print(result.stdout)
        else:
            print("⚠️ Excel conversion completed with warnings:")
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error during Excel conversion: {e}")
        return False

def main():
    """Main conversion process"""
    print("="*70)
    print("🔄 Project Graph Converter")
    print("   Remove Requirements → Add Domain Knowledge → Export Excel")
    print("="*70)
    
    # File paths
    script_dir = Path(__file__).parent.parent
    input_file = script_dir / "data" / "project graph.xlsx"
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Step 1: Load Excel data
    sheets_data, sheet_names = load_project_graph_excel(input_file)
    if not sheets_data:
        return
    
    # Step 2: Update structure  
    updated_data, changes = remove_requirements_add_domain_knowledge(sheets_data)
    
    # Step 3: Export to JSON
    json_file = export_to_json(updated_data, changes, input_file.name)
    
    # Step 4: Convert back to Excel
    excel_success = convert_json_to_excel(json_file)
    
    # Summary
    print("\n" + "="*70)
    print("✅ CONVERSION COMPLETE!")
    print("="*70)
    print(f"📊 Changes made:")
    for change in changes:
        print(f"  • {change}")
    
    print(f"\n📁 Files created:")
    print(f"  • JSON: {json_file}")
    if excel_success:
        print(f"  • Excel: Check data/ folder for converted file")
    
    print(f"\n🎯 Next steps:")
    print(f"  • Review the updated Excel file in data/ folder")
    print(f"  • Use the JSON file for further processing if needed")
    print(f"  • Import into Neo4j using scripts/init.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Process cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
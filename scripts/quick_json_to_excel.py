#!/usr/bin/env python3
"""
Quick JSON to Excel converter for project graph
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def convert_project_json_to_excel():
    """Convert the project graph JSON to Excel"""
    
    # File paths
    json_file = Path("exports/project_graph_updated_20251026_005958.json")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = Path(f"data/project_graph_converted_{timestamp}.xlsx")
    
    print(f"Converting: {json_file} -> {excel_file}")
    
    # Load JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create Excel writer
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # Process nodes (entity sheets)
        if 'nodes' in data:
            for sheet_name, records in data['nodes'].items():
                if records and isinstance(records, list):  # Only create sheet if there are records
                    df = pd.DataFrame(records)
                    # Ensure 'id' column is first if it exists
                    if 'id' in df.columns:
                        cols = ['id'] + [col for col in df.columns if col != 'id']
                        df = df[cols]
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  ✅ Created sheet: {sheet_name} ({len(records)} records)")
    
    print(f"✅ Excel file created: {excel_file}")
    
    # Show summary
    if 'nodes' in data:
        total_records = sum(len(records) for records in data['nodes'].values() if isinstance(records, list))
        sheet_count = len([k for k, v in data['nodes'].items() if v and isinstance(v, list)])
        print(f"📊 Total records: {total_records}")
        print(f"📋 Total sheets: {sheet_count}")
        
        # Show what was included
        print("\n📊 Sheets created:")
        for sheet_name, records in data['nodes'].items():
            if records and isinstance(records, list):
                print(f"  • {sheet_name}: {len(records)} records")

if __name__ == "__main__":
    convert_project_json_to_excel()
#!/usr/bin/env python3
"""
JSON to Excel Converter
========================
Converts JSON exports back to Excel format with proper sheet structure.
This is the reverse operation of excel_to_json.py.

Usage:
    python json_to_excel.py [input_json] [output_excel]
    
If no arguments provided, it will process the latest JSON export.
"""

import json
import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

def load_json_export(json_file_path):
    """Load and parse JSON export file"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded JSON file: {json_file_path}")
        return data
    except FileNotFoundError:
        print(f"❌ JSON file not found: {json_file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return None

def convert_json_to_excel(json_data, output_path):
    """Convert JSON data to Excel format"""
    print("🔄 Converting JSON to Excel format...")
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Process nodes (entity sheets)
        if 'nodes' in json_data:
            for sheet_name, records in json_data['nodes'].items():
                if records:  # Only create sheet if there are records
                    df = pd.DataFrame(records)
                    # Ensure 'id' column is first if it exists
                    if 'id' in df.columns:
                        cols = ['id'] + [col for col in df.columns if col != 'id']
                        df = df[cols]
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  ✅ Created sheet: {sheet_name} ({len(records)} records)")
                else:
                    print(f"  ⚠️  Skipping empty sheet: {sheet_name}")
        
        # Process relationships if they exist
        if 'relationships' in json_data and json_data['relationships']:
            df_relationships = pd.DataFrame(json_data['relationships'])
            df_relationships.to_excel(writer, sheet_name='Relationships', index=False)
            print(f"  ✅ Created sheet: Relationships ({len(json_data['relationships'])} records)")
    
    print(f"✅ Excel file created: {output_path}")

def get_latest_json_export(exports_dir):
    """Find the most recent JSON export file"""
    exports_path = Path(exports_dir)
    if not exports_path.exists():
        return None
    
    json_files = list(exports_path.glob("*.json"))
    if not json_files:
        return None
    
    # Sort by modification time and return the latest
    latest_file = max(json_files, key=os.path.getmtime)
    return str(latest_file)

def main():
    """Main conversion function"""
    script_dir = Path(__file__).parent.parent
    exports_dir = script_dir / 'exports'
    data_dir = script_dir / 'data'
    
    # Determine input and output files
    if len(sys.argv) >= 2:
        input_json = sys.argv[1]
        if not os.path.isabs(input_json):
            input_json = exports_dir / input_json
    else:
        # Find latest JSON export
        input_json = get_latest_json_export(exports_dir)
        if not input_json:
            print("❌ No JSON export files found in exports/ directory")
            return
    
    if len(sys.argv) >= 3:
        output_excel = sys.argv[2]
        if not os.path.isabs(output_excel):
            output_excel = data_dir / output_excel
    else:
        # Generate output filename based on input
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_excel = data_dir / f"converted_from_json_{timestamp}.xlsx"
    
    print("="*60)
    print("🔄 JSON to Excel Converter")
    print("="*60)
    print(f"Input JSON:  {input_json}")
    print(f"Output Excel: {output_excel}")
    print("-"*60)
    
    # Load JSON data
    json_data = load_json_export(input_json)
    if not json_data:
        return
    
    # Show metadata info
    if 'metadata' in json_data:
        metadata = json_data['metadata']
        print(f"📊 Source: {metadata.get('source_file', 'Unknown')}")
        print(f"📅 Export Date: {metadata.get('export_timestamp', 'Unknown')}")
        print(f"📋 Sheets: {metadata.get('total_sheets', 'Unknown')}")
        if 'sheet_names' in metadata:
            print(f"📝 Sheet Names: {', '.join(metadata['sheet_names'][:5])}...")
        print("-"*60)
    
    # Create output directory if needed
    output_excel.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to Excel
    convert_json_to_excel(json_data, output_excel)
    
    print("-"*60)
    print("✅ Conversion completed successfully!")
    print(f"📁 Output saved to: {output_excel}")
    
    # Show summary
    if 'nodes' in json_data:
        total_records = sum(len(records) for records in json_data['nodes'].values() if records)
        print(f"📊 Total records converted: {total_records}")
        print(f"📋 Total sheets created: {len([k for k, v in json_data['nodes'].items() if v])}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Conversion cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
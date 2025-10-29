#!/usr/bin/env python3
"""
Update JSON Export - Remove Features, Keep Domain Knowledge
===========================================================
This script updates the existing JSON export to match the current graph model:
- Removes all Feature-related data
- Keeps Domain_Knowledge data
- Updates metadata to reflect changes
"""

import json
import os
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

def update_json_structure(data):
    """Remove Feature entities and relationships, keep Domain_Knowledge"""
    print("🔄 Updating JSON structure...")
    
    changes_made = []
    
    # Remove Feature from nodes
    if 'nodes' in data and 'Feature' in data['nodes']:
        feature_count = len(data['nodes']['Feature'])
        del data['nodes']['Feature']
        changes_made.append(f"Removed {feature_count} Feature entities")
        print(f"  ❌ Removed Feature entities: {feature_count} records")
    
    # Keep Domain_Knowledge (no changes needed)
    if 'nodes' in data and 'Domain_Knowledge' in data['nodes']:
        dk_count = len(data['nodes']['Domain_Knowledge'])
        print(f"  ✅ Kept Domain_Knowledge entities: {dk_count} records")
        changes_made.append(f"Kept {dk_count} Domain_Knowledge entities")
    
    # Remove Feature-related relationships
    if 'relationships' in data:
        original_rel_count = len(data['relationships'])
        data['relationships'] = [
            rel for rel in data['relationships'] 
            if not (rel.get('from_type') == 'Feature' or rel.get('to_type') == 'Feature')
        ]
        removed_rel_count = original_rel_count - len(data['relationships'])
        if removed_rel_count > 0:
            changes_made.append(f"Removed {removed_rel_count} Feature relationships")
            print(f"  ❌ Removed Feature relationships: {removed_rel_count} records")
    
    # Update metadata
    if 'metadata' in data:
        # Update sheet names
        if 'sheet_names' in data['metadata']:
            original_sheets = data['metadata']['sheet_names'][:]
            data['metadata']['sheet_names'] = [
                sheet for sheet in data['metadata']['sheet_names'] 
                if sheet != 'Feature'
            ]
            if 'Feature' in original_sheets:
                changes_made.append("Removed Feature from sheet names")
                print(f"  ❌ Removed Feature from sheet names")
        
        # Update sheet count
        if 'total_sheets' in data['metadata']:
            data['metadata']['total_sheets'] = len(data['metadata']['sheet_names'])
        
        # Add update timestamp and change log
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['update_reason'] = "Removed Feature entities to match current graph model"
        data['metadata']['changes_made'] = changes_made
    
    # Update summary statistics if they exist
    if 'summary' in data:
        if 'node_counts' in data['summary']:
            if 'Feature' in data['summary']['node_counts']:
                del data['summary']['node_counts']['Feature']
        
        # Recalculate total nodes
        if 'nodes' in data:
            total_nodes = sum(len(entities) for entities in data['nodes'].values())
            data['summary']['total_nodes'] = total_nodes
    
    print(f"✅ Structure update completed")
    return data, changes_made

def save_updated_json(data, output_path):
    """Save updated JSON data"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated JSON saved: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")
        return False

def main():
    """Main update function"""
    script_dir = Path(__file__).parent.parent
    exports_dir = script_dir / 'exports'
    
    # Find the latest JSON export
    json_files = list(exports_dir.glob("*.json"))
    if not json_files:
        print("❌ No JSON export files found in exports/ directory")
        return
    
    # Get the most recent file
    input_file = max(json_files, key=os.path.getmtime)
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = exports_dir / f"updated_graph_model_{timestamp}.json"
    
    print("="*70)
    print("🔄 JSON Structure Update - Remove Features, Keep Domain Knowledge")
    print("="*70)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print("-"*70)
    
    # Load JSON data
    data = load_json_export(input_file)
    if not data:
        return
    
    # Show current structure
    if 'nodes' in data:
        print("📊 Current structure:")
        for entity_type, entities in data['nodes'].items():
            count = len(entities) if entities else 0
            status = "✅" if entity_type == "Domain_Knowledge" else "❌" if entity_type == "Feature" else "➡️"
            print(f"  {status} {entity_type}: {count} records")
    
    print("-"*70)
    
    # Update structure
    updated_data, changes = update_json_structure(data)
    
    # Save updated JSON
    if save_updated_json(updated_data, output_file):
        print("-"*70)
        print("✅ Update completed successfully!")
        print(f"📁 Updated file: {output_file}")
        print("\n📋 Changes made:")
        for change in changes:
            print(f"  • {change}")
        
        # Show final structure
        if 'nodes' in updated_data:
            print("\n📊 Final structure:")
            for entity_type, entities in updated_data['nodes'].items():
                count = len(entities) if entities else 0
                print(f"  ✅ {entity_type}: {count} records")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Update cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
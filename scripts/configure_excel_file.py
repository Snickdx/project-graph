#!/usr/bin/env python3
"""
Excel File Configuration Helper
===============================
Helps configure which Excel file to use for database initialization
"""

import os
import sys
from pathlib import Path

def get_available_excel_files():
    """Get list of available Excel files"""
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "data"
    
    excel_files = []
    if data_dir.exists():
        for file in data_dir.iterdir():
            if file.suffix.lower() in ['.xlsx', '.xls']:
                relative_path = f"data/{file.name}"
                excel_files.append({
                    'path': relative_path,
                    'name': file.name,
                    'size': file.stat().st_size,
                    'full_path': str(file)
                })
    
    return sorted(excel_files, key=lambda x: x['name'])

def read_current_config():
    """Read current EXCEL_FILE configuration"""
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / "config" / ".env"
    
    current_file = None
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('EXCEL_FILE='):
                    current_file = line.split('=', 1)[1].strip().strip('"')
                    break
    
    return current_file

def update_env_file(new_excel_file):
    """Update the .env file with new Excel file path"""
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / "config" / ".env"
    
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update EXCEL_FILE line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('EXCEL_FILE='):
            lines[i] = f'EXCEL_FILE="{new_excel_file}"\n'
            updated = True
            break
    
    # If EXCEL_FILE line doesn't exist, add it
    if not updated:
        lines.append(f'EXCEL_FILE="{new_excel_file}"\n')
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated config/.env with: EXCEL_FILE=\"{new_excel_file}\"")
    return True

def main():
    """Main configuration helper"""
    print("="*60)
    print("📊 Excel File Configuration Helper")
    print("="*60)
    
    # Show current configuration
    current_file = read_current_config()
    print(f"📋 Current configuration: {current_file or 'Not set'}")
    
    # Show available files
    excel_files = get_available_excel_files()
    
    if not excel_files:
        print("❌ No Excel files found in data/ directory")
        return
    
    print(f"\n📁 Available Excel files ({len(excel_files)} found):")
    print("-" * 60)
    
    for i, file_info in enumerate(excel_files, 1):
        size_mb = file_info['size'] / (1024 * 1024)
        current_marker = " 👈 CURRENT" if file_info['path'] == current_file else ""
        print(f"  {i}. {file_info['name']}")
        print(f"     Path: {file_info['path']}")
        print(f"     Size: {size_mb:.1f} MB{current_marker}")
        print()
    
    # Get user choice
    try:
        choice = input(f"Select file to use (1-{len(excel_files)}) or press Enter to keep current: ").strip()
        
        if not choice:
            print("✅ Keeping current configuration")
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(excel_files):
            selected_file = excel_files[choice_num - 1]
            
            print(f"\n🔄 Switching to: {selected_file['name']}")
            print(f"   Path: {selected_file['path']}")
            
            if update_env_file(selected_file['path']):
                print("\n✅ Configuration updated successfully!")
                print("\n🎯 Next steps:")
                print("1. 🔄 Re-initialize database: python scripts/init.py")
                print("2. 🧪 Test RAG system: python scripts/hybrid_rag.py")
                print("3. 🌐 Try web demo: python scripts/start_web_demo.py")
            
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
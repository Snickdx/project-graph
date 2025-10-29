#!/usr/bin/env python3
"""
Project Runner - Quick access to main project functions
=======================================================
This script provides easy access to the most common project operations.
"""

import os
import sys
import subprocess

def print_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("🚀 Requirements Graph Project - Quick Runner")
    print("="*60)
    print("1. 🏗️  Initialize Database          (scripts/init.py)")
    print("2. ⚡ Fast RAG Query System        (scripts/hybrid_rag.py)")
    print("3. 🤖 Full RAG Query System        (scripts/rag_query.py)")
    print("4. 📊 Excel to JSON Converter      (scripts/excel_to_json.py)")
    print("5. 📈 JSON to Excel Converter      (scripts/json_to_excel.py)")
    print("6. 🔄 Update JSON Structure        (scripts/update_json_structure.py)")
    print("7. 📋 Configure Excel File          (scripts/configure_excel_file.py)")
    print("8. 🌐 Web Demo Interface            (scripts/start_web_demo.py)")
    print("9. 🔍 Validate Database Schema     (scripts/validate_schema.py)")
    print("10. 🔄 Reset Database                (scripts/reset_database.py)")
    print("11. 🧪 Test RAG Systems             (scripts/test_rag_complete.py)")
    print("12. 📋 View Project Structure       (docs/project_structure.md)")
    print("13. 📁 Open Data Folder")
    print("14. 📤 Open Exports Folder")
    print("15. ❌ Exit")
    print("-"*60)

def run_script(script_path, description):
    """Run a Python script"""
    print(f"\n🚀 Running {description}...")
    print(f"   Script: {script_path}")
    print("-"*40)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
        else:
            print(f"⚠️  {description} completed with warnings/errors")
    except Exception as e:
        print(f"❌ Error running {description}: {e}")

def open_folder(folder_path, description):
    """Open a folder in the file explorer"""
    try:
        if os.path.exists(folder_path):
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
            print(f"📁 Opened {description}: {folder_path}")
        else:
            print(f"❌ Folder not found: {folder_path}")
    except Exception as e:
        print(f"❌ Error opening folder: {e}")

def view_file(file_path, description):
    """View a file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"\n📋 {description}")
            print("="*60)
            print(content[:2000])  # Show first 2000 characters
            if len(content) > 2000:
                print("\n... (file truncated, see full file for complete content)")
            print("="*60)
        else:
            print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main runner function"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    while True:
        print_menu()
        choice = input("Choose an option (1-9): ").strip()
        
        if choice == "1":
            script_path = os.path.join(script_dir, "scripts", "init.py")
            run_script(script_path, "Database Initialization")
            
        elif choice == "2":
            script_path = os.path.join(script_dir, "scripts", "hybrid_rag.py")
            run_script(script_path, "Fast Hybrid RAG System")
            
        elif choice == "3":
            script_path = os.path.join(script_dir, "scripts", "rag_query.py")
            run_script(script_path, "Full RAG Query System")
            
        elif choice == "4":
            script_path = os.path.join(script_dir, "scripts", "excel_to_json.py")
            run_script(script_path, "Excel to JSON Converter")
            
        elif choice == "5":
            script_path = os.path.join(script_dir, "scripts", "json_to_excel.py")
            run_script(script_path, "JSON to Excel Converter")
            
        elif choice == "6":
            script_path = os.path.join(script_dir, "scripts", "update_json_structure.py")
            run_script(script_path, "Update JSON Structure")
            
        elif choice == "7":
            script_path = os.path.join(script_dir, "scripts", "configure_excel_file.py")
            run_script(script_path, "Excel File Configuration")
            
        elif choice == "8":
            script_path = os.path.join(script_dir, "scripts", "start_web_demo.py")
            run_script(script_path, "Web Demo Interface")
            
        elif choice == "9":
            script_path = os.path.join(script_dir, "scripts", "validate_schema.py")
            run_script(script_path, "Database Schema Validator")
            
        elif choice == "10":
            script_path = os.path.join(script_dir, "scripts", "reset_database.py")
            run_script(script_path, "Database Reset and Re-initialization")
            
        elif choice == "11":
            script_path = os.path.join(script_dir, "scripts", "test_rag_complete.py")
            run_script(script_path, "Complete RAG System Tests")
            
        elif choice == "12":
            file_path = os.path.join(script_dir, "docs", "project_structure.md")
            view_file(file_path, "Project Structure Documentation")
            
        elif choice == "13":
            folder_path = os.path.join(script_dir, "data")
            open_folder(folder_path, "Data Folder")
            
        elif choice == "14":
            folder_path = os.path.join(script_dir, "exports")
            open_folder(folder_path, "Exports Folder")
            
        elif choice == "15":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-15.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
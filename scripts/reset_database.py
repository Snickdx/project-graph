#!/usr/bin/env python3
"""
Database Cleanup and Re-initialization
=======================================
Cleans the Neo4j database and re-initializes with the updated schema
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env file
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(script_dir, 'config', '.env')
load_dotenv(env_path)

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ Neo4j driver not available. Install with: pip install neo4j")
    sys.exit(1)

def clean_database():
    """Clean all data from the database"""
    print("🧹 Cleaning database...")
    
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    
    try:
        with driver.session() as session:
            # Delete all nodes and relationships
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleaned successfully")
            
            # Verify cleanup
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"📊 Remaining nodes: {count}")
    
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False
    finally:
        driver.close()
    
    return True

def reinitialize_database():
    """Re-initialize the database with updated data"""
    print("🔄 Re-initializing database...")
    
    try:
        import subprocess
        import sys
        
        # Run the init script
        init_script = os.path.join(script_dir, "scripts", "init.py")
        result = subprocess.run([sys.executable, init_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database re-initialized successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Error during re-initialization:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running initialization: {e}")
        return False

def main():
    """Main cleanup and re-initialization process"""
    print("="*60)
    print("🔄 Database Cleanup and Re-initialization")
    print("="*60)
    
    # Check configuration
    if not all([os.getenv("NEO4J_URI"), os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")]):
        print("❌ Neo4j configuration missing. Check config/.env file")
        return
    
    print(f"🔗 Neo4j URI: {os.getenv('NEO4J_URI')}")
    
    # Confirm action
    response = input("\n⚠️  This will DELETE ALL DATA in the database. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    print("\n" + "-"*60)
    
    # Step 1: Clean database
    if not clean_database():
        print("❌ Cleanup failed. Aborting.")
        return
    
    print("-"*60)
    
    # Step 2: Re-initialize
    if not reinitialize_database():
        print("❌ Re-initialization failed.")
        return
    
    print("-"*60)
    print("✅ Process completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Test queries: python scripts/hybrid_rag.py")
    print("2. Run web demo: python scripts/start_web_demo.py")
    print("3. Validate schema: python scripts/validate_schema.py")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Process cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
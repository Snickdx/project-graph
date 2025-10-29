#!/usr/bin/env python3
"""
Database Schema Validator
==========================
Validates that the Neo4j database schema matches the expected structure
and identifies any missing properties or nodes.
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

def check_database_connection():
    """Test Neo4j connection"""
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            
        driver.close()
        return test_value == 1
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def get_database_schema():
    """Get the actual database schema"""
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    
    schema_info = {
        'node_labels': {},
        'relationships': [],
        'properties': {}
    }
    
    try:
        with driver.session() as session:
            # Get all node labels and their counts
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            
            for label in labels:
                # Count nodes for each label
                count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = count_result.single()["count"]
                schema_info['node_labels'][label] = count
                
                # Get properties for each label
                props_result = session.run(f"MATCH (n:{label}) RETURN keys(n) as props LIMIT 1")
                props_record = props_result.single()
                if props_record and props_record["props"]:
                    schema_info['properties'][label] = props_record["props"]
                else:
                    schema_info['properties'][label] = []
            
            # Get relationship types
            rel_result = session.run("CALL db.relationshipTypes()")
            schema_info['relationships'] = [record["relationshipType"] for record in rel_result]
            
    except Exception as e:
        print(f"❌ Error getting schema: {e}")
    finally:
        driver.close()
    
    return schema_info

def validate_expected_schema():
    """Check if the expected schema matches reality"""
    print("🔍 Validating Database Schema")
    print("="*50)
    
    if not check_database_connection():
        print("❌ Cannot connect to database")
        return False
    
    schema = get_database_schema()
    
    print("📊 Current Database Schema:")
    print("-"*30)
    
    # Node labels and counts
    print("🏷️  Node Labels:")
    for label, count in schema['node_labels'].items():
        print(f"  • {label}: {count} nodes")
    
    print("\n🔗 Relationship Types:")
    for rel_type in schema['relationships']:
        print(f"  • {rel_type}")
    
    print("\n📝 Node Properties:")
    for label, props in schema['properties'].items():
        print(f"  • {label}: {', '.join(props) if props else 'No properties'}")
    
    # Check for common issues
    print("\n⚠️  Potential Issues:")
    issues_found = []
    
    # Check if Feature has priority property
    if 'Feature' in schema['properties']:
        feature_props = schema['properties']['Feature']
        if 'priority' not in feature_props:
            issues_found.append("Feature nodes missing 'priority' property")
        if 'status' not in feature_props:
            issues_found.append("Feature nodes missing 'status' property")
    
    # Check if removed entities still exist
    removed_entities = ['Requirement', 'Functional_Requirement']
    for entity in removed_entities:
        if entity in schema['node_labels']:
            issues_found.append(f"Removed entity '{entity}' still exists in database")
    
    # Check if Domain_Knowledge exists
    if 'Domain_Knowledge' not in schema['node_labels']:
        issues_found.append("Domain_Knowledge nodes not found - may need database re-initialization")
    
    if issues_found:
        for issue in issues_found:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ No issues detected")
    
    return len(issues_found) == 0

def suggest_fixes():
    """Suggest fixes for common issues"""
    print("\n🔧 Suggested Fixes:")
    print("-"*20)
    print("1. 🔄 Re-initialize database with updated schema:")
    print("   python scripts/init.py")
    print()
    print("2. 📊 Use updated Excel file with correct structure:")
    print("   data/project_graph_converted_20251026_010031.xlsx")
    print()
    print("3. 🧹 Clear database before re-initialization:")
    print("   In Neo4j Browser: MATCH (n) DETACH DELETE n")
    print()
    print("4. ✅ Validate queries match actual data structure")

def main():
    """Main validation function"""
    print("="*60)
    print("🔍 Database Schema Validation Tool")
    print("="*60)
    
    try:
        is_valid = validate_expected_schema()
        
        if not is_valid:
            suggest_fixes()
        else:
            print("\n✅ Database schema looks good!")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
"""
Simple RAG Test Script
======================
Test the graph connection and basic query functionality
"""

import os
from dotenv import load_dotenv

# Load environment variables from config/.env file
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(script_dir, 'config', '.env')
load_dotenv(env_path)

def test_neo4j_connection():
    """Test Neo4j connection"""
    print("🔗 Testing Neo4j connection...")
    
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
        
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            record = result.single()
            total_nodes = record["total_nodes"]
            
        driver.close()
        print(f"✅ Neo4j connected successfully - {total_nodes} nodes found")
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def test_basic_cypher_queries():
    """Test some basic Cypher queries"""
    print("\n🔍 Testing basic Cypher queries...")
    
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
        
        queries_to_test = [
            "MATCH (p:Project) RETURN p.name as project_name LIMIT 5",
            "MATCH (s:Stakeholder) RETURN s.name as stakeholder_name LIMIT 5",
            "MATCH (f:Functional_Requirement) RETURN f.description as requirement LIMIT 3",
            "MATCH (dk:Domain_Knowledge) RETURN dk.area as knowledge_area LIMIT 3",
            "MATCH (s:Stakeholder)-[r:HAS_DOMAIN_KNOWLEDGE]->(dk:Domain_Knowledge) RETURN s.name, dk.area LIMIT 3"
        ]
        
        with driver.session() as session:
            for query in queries_to_test:
                print(f"\n🔧 Running: {query}")
                result = session.run(query)
                records = list(result)
                if records:
                    for record in records:
                        print(f"   📄 {dict(record)}")
                else:
                    print("   📭 No results found")
        
        driver.close()
        print("\n✅ Basic queries completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_ollama_availability():
    """Test if Ollama is available"""
    print("\n🤖 Testing Ollama availability...")
    
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is available")
            print(f"📋 Available models:\n{result.stdout}")
            return True
        else:
            print(f"❌ Ollama command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Ollama command not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama command timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing Ollama: {e}")
        return False

def test_langchain_imports():
    """Test if LangChain imports work"""
    print("\n📦 Testing LangChain imports...")
    
    try:
        from langchain.llms import Ollama
        from langchain.chains import GraphCypherQAChain
        from langchain.graphs import Neo4jGraph
        from langchain.prompts import PromptTemplate
        print("✅ All LangChain imports successful")
        return True
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False

def run_full_test():
    """Run all tests"""
    print("🧪 Running RAG System Tests")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_env_vars),
        ("LangChain Imports", test_langchain_imports),
        ("Neo4j Connection", test_neo4j_connection),
        ("Basic Cypher Queries", test_basic_cypher_queries),
        ("Ollama Availability", test_ollama_availability)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        results[test_name] = test_func()
    
    print(f"\n{'=' * 20} TEST SUMMARY {'=' * 20}")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! RAG system is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
    
    return all_passed

def test_env_vars():
    """Test if required environment variables are set"""
    print("🔧 Testing environment variables...")
    
    required_vars = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

if __name__ == "__main__":
    run_full_test()
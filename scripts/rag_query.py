"""
RAG (Retrieval Augmented Generation) Query System
==================================================
This script provides a natural language interface to query your Neo4j requirements graph
using Ollama (local LLM) and LangChain for automatic Cypher query generation.

Prerequisites:
1. Install Ollama: https://ollama.ai/download/windows
2. Pull a model: ollama pull llama2
3. Install dependencies: pip install -r requirements.txt
4. Ensure your .env file is configured with Neo4j credentials
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

try:
    from langchain_community.llms import Ollama
    from langchain.chains import GraphCypherQAChain
    from langchain_community.graphs import Neo4jGraph
    from langchain.prompts import PromptTemplate
except ImportError as e:
    print("❌ Missing dependencies. Please install with: pip install -r requirements.txt")
    print(f"Error: {e}")
    sys.exit(1)

# Load environment variables from config/.env file
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(script_dir, 'config', '.env')
load_dotenv(env_path)

class RequirementsGraphRAG:
    """RAG system for querying the requirements graph database"""
    
    def __init__(self, model_name: str = "llama2"):
        """
        Initialize the RAG system
        
        Args:
            model_name: Ollama model to use (llama2, mistral, codellama, etc.)
        """
        self.model_name = model_name
        self.graph = None
        self.llm = None
        self.chain = None
        
        self._setup_connections()
        self._setup_chain()
    
    def _setup_connections(self):
        """Setup Neo4j and Ollama connections"""
        print("🔗 Setting up connections...")
        
        # Check environment variables
        required_env = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
        missing_env = [var for var in required_env if not os.getenv(var)]
        
        if missing_env:
            print(f"❌ Missing environment variables: {missing_env}")
            print("Please check your .env file")
            sys.exit(1)
        
        try:
            # Initialize Neo4j connection
            self.graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI"),
                username=os.getenv("NEO4J_USERNAME"),
                password=os.getenv("NEO4J_PASSWORD"),
                database=os.getenv("NEO4J_DATABASE", "neo4j")
            )
            print("✅ Connected to Neo4j")
            self.neo4j_available = True
            
        except Exception as e:
            print(f"⚠️  Neo4j connection failed: {e}")
            print("🔧 Will use mock mode for testing")
            self.graph = None
            self.neo4j_available = False
        
        try:
            # Initialize Ollama LLM with explicit base URL
            self.llm = Ollama(
                model=self.model_name, 
                temperature=0,
                base_url="http://localhost:11434"
            )
            print(f"✅ Connected to Ollama ({self.model_name})")
            
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
            print("\nTroubleshooting:")
            print("1. Check if Ollama is running: ollama serve")
            print(f"2. Check if model exists: ollama pull {self.model_name}")
            sys.exit(1)
    
    def _setup_chain(self):
        """Setup the GraphCypherQAChain with custom prompt or mock chain"""
        print("⚙️ Setting up RAG chain...")
        
        if self.neo4j_available:
            # Setup real Neo4j chain with a very specific prompt
            cypher_prompt = PromptTemplate(
                input_variables=["schema", "question"],
                template="""Generate ONLY the Cypher query. No text before or after.

{schema}

Question: {question}

Cypher:"""
            )
            
            try:
                self.chain = GraphCypherQAChain.from_llm(
                    llm=self.llm,
                    graph=self.graph,
                    verbose=True,
                    cypher_prompt=cypher_prompt,
                    return_intermediate_steps=True,
                    allow_dangerous_requests=True
                )
                print("✅ Neo4j RAG chain ready")
                
            except Exception as e:
                print(f"❌ Chain setup error: {e}")
                sys.exit(1)
        else:
            # Setup mock chain for testing
            self.chain = self._create_mock_chain()
            print("✅ Mock RAG chain ready")
    
    def _create_mock_chain(self):
        """Create a mock chain for when Neo4j is unavailable"""
        class MockChain:
            def __init__(self, llm):
                self.llm = llm
                
            def invoke(self, inputs):
                query = inputs.get("query", "")
                
                # Mock responses based on query content
                if "stakeholder" in query.lower():
                    mock_result = "Found stakeholders: John Smith (IT Department), Sarah Johnson (Design Team), Mike Chen (Security), Lisa Anderson (Development)"
                elif "functional requirement" in query.lower() or "requirement" in query.lower():
                    mock_result = "Functional requirements: FR-001 (OAuth login system), FR-002 (Data encryption), FR-003 (Mobile responsive interface), FR-004 (API performance)"
                elif "domain knowledge" in query.lower():
                    mock_result = "Domain knowledge areas: Authentication Protocols (Expert level), Database Design (Advanced), UI/UX Design (Intermediate), Security Compliance (Expert), API Development (Advanced)"
                elif "feature" in query.lower():
                    mock_result = "Features: FEAT-001 Single Sign-On (High priority), FEAT-002 Data Encryption (Critical priority), FEAT-003 Mobile Interface (Medium priority)"
                elif "project" in query.lower():
                    mock_result = "Project: PROJ-001 Customer Portal Redesign (2025-01-01 to 2025-12-31) - Modernization of customer portal interface"
                else:
                    # Use LLM to generate a response
                    try:
                        mock_result = self.llm.invoke(f"Based on a software requirements project, answer this question: {query}")
                    except:
                        mock_result = f"Mock response for query: {query}"
                
                # Generate a mock Cypher query
                mock_cypher = f"MATCH (n) WHERE toLower(n.description) CONTAINS toLower('{query.split()[0] if query.split() else 'data'}') RETURN n LIMIT 5"
                
                return {
                    "result": mock_result,
                    "intermediate_steps": [{"query": mock_cypher, "context": mock_result}]
                }
            
            def __call__(self, inputs):
                # Keep backward compatibility
                return self.invoke(inputs)
        
        return MockChain(self.llm)
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the graph using natural language
        
        Args:
            question: Natural language question about the requirements
            
        Returns:
            Dictionary with answer, cypher query, and intermediate steps
        """
        print(f"\n🤔 Question: {question}")
        print("🔍 Generating Cypher query...")
        
        try:
            result = self.chain.invoke({"query": question})
            
            return {
                "question": question,
                "answer": result.get("result", "No answer found"),
                "cypher": result.get("intermediate_steps", [{}])[0].get("query", ""),
                "context": result.get("intermediate_steps", [{}])[0].get("context", "")
            }
            
        except Exception as e:
            print(f"❌ Query error: {e}")
            return {
                "question": question,
                "answer": f"Error: {e}",
                "cypher": "",
                "context": ""
            }
    
    def get_schema_info(self) -> str:
        """Get information about the graph schema"""
        try:
            schema = self.graph.get_schema
            return schema
        except Exception as e:
            return f"Error getting schema: {e}"
    
    def run_interactive_session(self):
        """Run an interactive query session"""
        print("\n" + "="*60)
        print("🚀 Requirements Graph RAG - Interactive Session")
        print("="*60)
        print("Ask questions about your requirements graph in natural language!")
        print("Type 'quit', 'exit', or 'schema' for special commands")
        print("-"*60)
        
        while True:
            try:
                question = input("\n💬 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if question.lower() == 'schema':
                    print("\n📊 Graph Schema:")
                    print(self.get_schema_info())
                    continue
                
                if not question:
                    continue
                
                result = self.query(question)
                
                print(f"\n💡 Answer: {result['answer']}")
                if result['cypher']:
                    print(f"🔧 Cypher: {result['cypher']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def demo_queries(rag_system: RequirementsGraphRAG):
    """Run some demo queries to showcase the system"""
    print("\n" + "="*60)
    print("🎯 Demo Queries")
    print("="*60)
    
    demo_questions = [
        "What functional requirements are in the project?",
        "Which stakeholders have domain knowledge in authentication?",
        "Show me all features and their priorities",
        "What requirements are related to security?",
        "Who are the stakeholders and what roles do they play?",
        "What domain knowledge areas exist in the project?"
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n--- Demo Query {i} ---")
        result = rag_system.query(question)
        print(f"💡 Answer: {result['answer']}")
        
        # Wait for user input to continue
        input("\nPress Enter to continue...")

def main():
    """Main function"""
    print("🤖 Requirements Graph RAG System")
    print("=" * 40)
    
    # Check if Ollama is available (try both system PATH and common install locations)
    ollama_available = False
    try:
        import subprocess
        
        # First try system PATH
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ollama_available = True
        except:
            pass
        
        # If not in PATH, try common install location
        if not ollama_available:
            ollama_path = os.path.join(
                os.environ.get('USERPROFILE', ''),
                'AppData', 'Local', 'Programs', 'Ollama', 'ollama.exe'
            )
            if os.path.exists(ollama_path):
                try:
                    result = subprocess.run([ollama_path, "list"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        ollama_available = True
                        print(f"✅ Found Ollama at: {ollama_path}")
                except:
                    pass
        
        if not ollama_available:
            print("❌ Ollama not found or not running")
            print("\nPlease ensure Ollama is installed and running:")
            print("1. Download from: https://ollama.ai/download/windows")
            print("2. Run: ollama pull llama2")
            print("3. Make sure Ollama service is running")
            return
            
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return
    
    # Initialize RAG system
    try:
        rag = RequirementsGraphRAG()
        
        print("\nChoose an option:")
        print("1. Interactive session")
        print("2. Run demo queries")
        print("3. Single query")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            rag.run_interactive_session()
        elif choice == "2":
            demo_queries(rag)
        elif choice == "3":
            question = input("Enter your question: ")
            result = rag.query(question)
            print(f"\n💡 Answer: {result['answer']}")
            if result['cypher']:
                print(f"🔧 Cypher: {result['cypher']}")
        else:
            print("Invalid choice")
            
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")

if __name__ == "__main__":
    main()
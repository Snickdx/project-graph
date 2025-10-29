"""
Fast Hybrid RAG System with Embeddings
======================================
This system uses embeddings to quickly match user questions to pre-built Cypher templates,
with fallback to LLM generation for complex queries.
"""

import os
import sys
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables from config/.env file
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(script_dir, 'config', '.env')
load_dotenv(env_path)

try:
    from sentence_transformers import SentenceTransformer
    from langchain_ollama import OllamaLLM
    from langchain_neo4j import Neo4jGraph
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    print("❌ Missing dependencies. Please install:")
    print("pip install sentence-transformers scikit-learn")
    print(f"Error: {e}")
    sys.exit(1)

class FastHybridRAG:
    """Fast RAG system using embeddings + templates with LLM fallback"""
    
    def __init__(self, model_name: str = "llama2"):
        """Initialize the hybrid RAG system"""
        self.model_name = model_name
        self.embedding_model = None
        self.graph = None
        self.llm = None
        self.query_templates = {}
        self.template_embeddings = None
        self.template_keys = []
        
        print("🚀 Initializing Fast Hybrid RAG System...")
        self._setup_connections()
        self._setup_query_templates()
        self._setup_embeddings()
        print("✅ Hybrid RAG system ready!")
    
    def _setup_connections(self):
        """Setup Neo4j and Ollama connections"""
        print("🔗 Setting up connections...")
        
        # Neo4j connection
        try:
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
            self.neo4j_available = False
        
        # Ollama connection (for fallback)
        try:
            self.llm = OllamaLLM(
                model=self.model_name,
                temperature=0,
                base_url="http://localhost:11434"
            )
            print(f"✅ Connected to Ollama ({self.model_name}) for fallback")
        except Exception as e:
            print(f"⚠️  Ollama connection failed: {e}")
            self.llm = None
    
    def _setup_query_templates(self):
        """Setup pre-built query templates for common questions"""
        print("📋 Setting up query templates...")
        
        self.query_templates = {
            # Stakeholder queries
            "list all stakeholders": {
                "cypher": "MATCH (s:Stakeholder) RETURN s.name, s.department, s.email ORDER BY s.name",
                "description": "Get all stakeholders with their details"
            },
            "who are the stakeholders": {
                "cypher": "MATCH (s:Stakeholder) RETURN s.name ORDER BY s.name",
                "description": "Get stakeholder names"
            },
            "show stakeholder roles": {
                "cypher": "MATCH (s:Stakeholder)-[:PLAYS_ROLE]->(r:Role) RETURN s.name, r.name, r.responsibilities",
                "description": "Get stakeholders and their roles"
            },
            
            # Goals and Constraints queries (replacing requirements)
            "what are the goals": {
                "cypher": "MATCH (g:Goal) RETURN g.id, g.name, g.description ORDER BY g.name LIMIT 10",
                "description": "Get project goals"
            },
            "show project constraints": {
                "cypher": "MATCH (c:Constraint) RETURN c.id, c.name, c.description ORDER BY c.name LIMIT 10",
                "description": "Get project constraints"
            },
            "what are the requirements": {
                "cypher": "MATCH (g:Goal) RETURN g.name, g.description ORDER BY g.name",
                "description": "Get project goals (requirements alternative)"
            },
            
            # Features queries
            "what features exist": {
                "cypher": "MATCH (f:Feature) RETURN f.id, f.name, f.description ORDER BY f.name",
                "description": "Get all features with descriptions"
            },
            "show all features": {
                "cypher": "MATCH (f:Feature) RETURN f.id, f.name, f.description ORDER BY f.name",
                "description": "Get features list"
            },
            
            # Domain Knowledge queries
            "what domain knowledge exists": {
                "cypher": "MATCH (dk:Domain_Knowledge) RETURN dk.area, dk.level, dk.description ORDER BY dk.area",
                "description": "Get all domain knowledge areas"
            },
            "who has domain knowledge": {
                "cypher": "MATCH (s:Stakeholder)-[:HAS_DOMAIN_KNOWLEDGE]->(dk:Domain_Knowledge) RETURN s.name, dk.area, dk.level",
                "description": "Get stakeholders and their domain expertise"
            },
            "authentication expertise": {
                "cypher": "MATCH (s:Stakeholder)-[:HAS_DOMAIN_KNOWLEDGE]->(dk:Domain_Knowledge) WHERE dk.area CONTAINS 'Authentication' RETURN s.name, dk.area, dk.level",
                "description": "Find authentication experts"
            },
            
            # Project queries
            "project information": {
                "cypher": "MATCH (p:Project) RETURN p.name, p.description, p.start_date, p.end_date",
                "description": "Get project details"
            },
            
            # Budget queries
            "budget information": {
                "cypher": "MATCH (b:Budget) RETURN b.amount, b.currency, b.fiscal_year ORDER BY b.fiscal_year",
                "description": "Get budget details"
            },
            "whats in the budget": {
                "cypher": "MATCH (b:Budget)-[:HAS_LINE_ITEM]->(li:Line_Item) RETURN b.amount as budget, li.description, li.amount, li.category ORDER BY li.amount DESC",
                "description": "Get budget breakdown with line items"
            },
            "budget breakdown": {
                "cypher": "MATCH (li:Line_Item) RETURN li.description, li.amount, li.category ORDER BY li.amount DESC",
                "description": "Get budget line items"
            },
            
            # Relationship queries
            "requirements by stakeholder": {
                "cypher": "MATCH (s:Stakeholder)-[:RAISED_BY]-(r:Functional_Requirement) RETURN s.name, r.description",
                "description": "Get requirements raised by each stakeholder"
            },
            "features satisfying requirements": {
                "cypher": "MATCH (r:Functional_Requirement)-[:SATISFIED_BY]->(f:Feature) RETURN r.description, f.name",
                "description": "Get which features satisfy which requirements"
            },
            
            # Quality scenarios queries
            "quality scenarios": {
                "cypher": "MATCH (qs:Qual_Scenario) RETURN qs.scenario, qs.description ORDER BY qs.scenario",
                "description": "Get all quality scenarios"
            },
            "what are the quality scenarios": {
                "cypher": "MATCH (qs:Qual_Scenario) RETURN qs.scenario, qs.description ORDER BY qs.scenario",
                "description": "Get project quality scenarios"
            },
            
            # Analysis queries
            "stakeholder expertise analysis": {
                "cypher": "MATCH (s:Stakeholder)-[:HAS_DOMAIN_KNOWLEDGE]->(dk:Domain_Knowledge) RETURN dk.area, count(s) as expert_count ORDER BY expert_count DESC",
                "description": "Count experts per domain area"
            },
            "requirement complexity": {
                "cypher": "MATCH (r:Functional_Requirement)-[:REQUIRES_DOMAIN_KNOWLEDGE]->(dk:Domain_Knowledge) RETURN r.description, count(dk) as knowledge_areas_needed ORDER BY knowledge_areas_needed DESC",
                "description": "Requirements by complexity (domain knowledge needed)"
            }
        }
        
        print(f"✅ Loaded {len(self.query_templates)} query templates")
    
    def _setup_embeddings(self):
        """Setup embeddings for fast query matching"""
        print("🧠 Setting up embeddings...")
        
        try:
            # Use a fast, lightweight embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast and good
            
            # Create embeddings for all template questions
            self.template_keys = list(self.query_templates.keys())
            template_texts = [key + " " + self.query_templates[key]["description"] for key in self.template_keys]
            
            self.template_embeddings = self.embedding_model.encode(template_texts)
            print(f"✅ Generated embeddings for {len(self.template_keys)} templates")
            
        except Exception as e:
            print(f"❌ Embedding setup failed: {e}")
            print("Please install: pip install sentence-transformers")
            sys.exit(1)
    
    def find_best_template(self, question: str, threshold: float = 0.5) -> Tuple[str, float, Dict]:
        """Find the best matching template using embedding similarity"""
        # Encode the user question
        question_embedding = self.embedding_model.encode([question])
        
        # Calculate similarity with all templates
        similarities = cosine_similarity(question_embedding, self.template_embeddings)[0]
        
        # Find the best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        best_template_key = self.template_keys[best_idx]
        best_template = self.query_templates[best_template_key]
        
        return best_template_key, best_similarity, best_template
    
    def execute_cypher(self, cypher: str) -> List[Dict]:
        """Execute a Cypher query and return results"""
        if not self.neo4j_available:
            return [{"error": "Neo4j not available"}]
        
        try:
            with self.graph._driver.session() as session:
                result = session.run(cypher)
                return [dict(record) for record in result]
        except Exception as e:
            return [{"error": f"Query execution failed: {e}"}]
    
    def query(self, question: str, similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Query the system using hybrid approach:
        1. Try to match with templates using embeddings (fast)
        2. Fall back to LLM generation if no good match (slow but flexible)
        """
        print(f"\n🤔 Question: {question}")
        start_time = os.times().elapsed if hasattr(os, 'times') else 0
        
        # Step 1: Try template matching with embeddings
        template_key, similarity, template = self.find_best_template(question)
        
        print(f"🎯 Best template match: '{template_key}' (similarity: {similarity:.3f})")
        
        if similarity >= similarity_threshold:
            print("⚡ Using fast template-based approach")
            cypher = template["cypher"]
            results = self.execute_cypher(cypher)
            
            # Format results into natural language
            if results and not any("error" in result for result in results):
                answer = self._format_results(question, results, template["description"])
            else:
                answer = f"No results found or error: {results}"
            
            return {
                "question": question,
                "method": "template",
                "template_used": template_key,
                "similarity": similarity,
                "cypher": cypher,
                "results": results,
                "answer": answer,
                "execution_time": "< 1 second"
            }
        
        else:
            print("🐌 Using LLM fallback (slower but more flexible)")
            # Step 2: Fall back to LLM generation
            if self.llm:
                try:
                    # Generate Cypher using LLM
                    llm_prompt = f"""Write ONLY a Cypher query. No explanations or text.

Question: {question}

Schema: Project, Stakeholder, Role, Feature, Functional_Requirement, Domain_Knowledge, Qual_Scenario
Relations: HAS_STAKEHOLDER, PLAYS_ROLE, HAS_DOMAIN_KNOWLEDGE, HAS_FUNCTIONAL_REQUIREMENT, RAISED_BY, SATISFIED_BY

Query:"""
                    
                    cypher = self.llm.invoke(llm_prompt).strip()
                    results = self.execute_cypher(cypher)
                    answer = self._format_results(question, results, "LLM generated query")
                    
                    return {
                        "question": question,
                        "method": "llm_fallback",
                        "template_used": None,
                        "similarity": similarity,
                        "cypher": cypher,
                        "results": results,
                        "answer": answer,
                        "execution_time": "3-5 seconds"
                    }
                except Exception as e:
                    return {
                        "question": question,
                        "method": "error",
                        "error": f"LLM fallback failed: {e}",
                        "answer": "Sorry, I couldn't process your question."
                    }
            else:
                return {
                    "question": question,
                    "method": "no_match",
                    "template_used": template_key,
                    "similarity": similarity,
                    "answer": f"No good template match (similarity: {similarity:.3f}). Try rephrasing your question or asking about: stakeholders, requirements, features, or domain knowledge."
                }
    
    def _format_results(self, question: str, results: List[Dict], description: str) -> str:
        """Format query results into natural language"""
        if not results:
            return "No results found."
        
        if any("error" in result for result in results):
            return f"Error executing query: {results[0].get('error', 'Unknown error')}"
        
        # Format based on result content
        formatted_lines = []
        for result in results[:10]:  # Limit to 10 results
            if result:
                # Create a readable line from the result
                values = [str(v) for v in result.values() if v is not None]
                if values:
                    formatted_lines.append(" | ".join(values))
        
        if formatted_lines:
            return f"Found {len(results)} result(s):\n" + "\n".join(formatted_lines)
        else:
            return "Results found but no displayable data."
    
    def list_available_queries(self) -> List[str]:
        """List all available template queries"""
        return list(self.query_templates.keys())
    
    def interactive_session(self):
        """Run an interactive query session"""
        print("\n" + "="*60)
        print("🚀 Fast Hybrid RAG - Interactive Session")
        print("="*60)
        print("Ask questions about your requirements graph!")
        print("✨ Most common questions will be answered instantly using templates")
        print("🤖 Complex questions will use the LLM (slower)")
        print("\nType 'help' to see available templates, 'quit' to exit")
        print("-"*60)
        
        while True:
            try:
                question = input("\n💬 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if question.lower() == 'help':
                    print("\n📋 Available template queries:")
                    for i, template_key in enumerate(self.template_keys, 1):
                        print(f"{i:2d}. {template_key}")
                    continue
                
                if not question:
                    continue
                
                result = self.query(question)
                
                print(f"\n💡 Answer: {result['answer']}")
                print(f"⚡ Method: {result['method']} ({result.get('execution_time', 'unknown time')})")
                
                if result['method'] == 'template':
                    print(f"📋 Template: {result['template_used']}")
                
                if 'cypher' in result:
                    print(f"🔧 Cypher: {result['cypher']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Fast Hybrid RAG System")
    print("=" * 40)
    
    try:
        rag = FastHybridRAG()
        
        print("\nChoose an option:")
        print("1. Interactive session")
        print("2. Run sample queries")
        print("3. Single query")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            rag.interactive_session()
        elif choice == "2":
            sample_questions = [
                "who are the stakeholders",
                "what are the requirements",
                "show all features",
                "what domain knowledge exists",
                "who has authentication expertise"
            ]
            
            print("\n🎯 Running sample queries...")
            for question in sample_questions:
                print(f"\n{'-'*40}")
                result = rag.query(question)
                print(f"Q: {question}")
                print(f"A: {result['answer']}")
                print(f"Method: {result['method']} ({result.get('execution_time', 'unknown')})")
                
        elif choice == "3":
            question = input("Enter your question: ")
            result = rag.query(question)
            print(f"\n💡 Answer: {result['answer']}")
            print(f"⚡ Method: {result['method']} ({result.get('execution_time', 'unknown')})")
            if 'cypher' in result:
                print(f"🔧 Cypher: {result['cypher']}")
        else:
            print("Invalid choice")
            
    except Exception as e:
        print(f"❌ Error initializing hybrid RAG system: {e}")

if __name__ == "__main__":
    main()
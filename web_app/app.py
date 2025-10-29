#!/usr/bin/env python3
"""
Minimal Flask Web Demo for LLM RAG System
==========================================
A clean web interface to demonstrate the hybrid RAG system with real-time streaming.
Uses Bootstrap for styling and Server-Sent Events for live responses.
"""

from flask import Flask, render_template, request, Response, jsonify
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path to import our RAG system
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Load environment variables from config/.env
env_path = parent_dir / 'config' / '.env'
load_dotenv(env_path)

# Try to import our hybrid RAG system
try:
    from scripts.hybrid_rag import FastHybridRAG
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ RAG system not available: {e}")
    RAG_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'demo-secret-key-change-in-production')

# Global RAG instance
rag_system = None

def init_rag_system():
    """Initialize the RAG system"""
    global rag_system
    if RAG_AVAILABLE and rag_system is None:
        try:
            print("🚀 Initializing RAG system...")
            rag_system = FastHybridRAG()
            print("✅ RAG system ready!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {e}")
            return False
    return RAG_AVAILABLE

@app.route('/')
def index():
    """Main chat interface"""
    rag_ready = init_rag_system()
    return render_template('index.html', rag_available=rag_ready)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'rag_available': RAG_AVAILABLE,
        'rag_initialized': rag_system is not None
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and return streaming response"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Return SSE response
    return Response(
        stream_llm_response(message),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

def stream_llm_response(message):
    """Stream LLM response using Server-Sent Events"""
    try:
        # Send start event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your query...'})}\n\n"
        time.sleep(0.1)
        
        if not RAG_AVAILABLE or rag_system is None:
            # Fallback response if RAG not available
            fallback_response = """
            🤖 **Demo Mode**: RAG system not available.
            
            Your question: "{}"
            
            **This would normally:**
            1. Search the Neo4j requirements graph
            2. Use hybrid embedding + template matching
            3. Generate contextual responses with domain knowledge
            4. Stream results in real-time
            
            **To enable full functionality:**
            - Configure Neo4j in config/.env
            - Install required dependencies
            - Initialize the RAG system
            """.format(message)
            
            # Stream the fallback response word by word
            words = fallback_response.split()
            current_text = ""
            
            for word in words:
                current_text += word + " "
                yield f"data: {json.dumps({'type': 'token', 'content': current_text})}\n\n"
                time.sleep(0.1)  # Simulate streaming
            
        else:
            # Use actual RAG system
            yield f"data: {json.dumps({'type': 'status', 'message': 'Querying knowledge graph...'})}\n\n"
            
            try:
                # Get response from RAG system
                response_data = rag_system.query(message)
                
                if 'error' in response_data:
                    error_msg = f"❌ Error: {response_data['error']}"
                    yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
                else:
                    # Stream the response
                    full_response = response_data.get('response', 'No response generated')
                    method_used = response_data.get('method', 'unknown')
                    confidence = response_data.get('confidence', 0)
                    
                    # Add metadata
                    metadata = f"**Method**: {method_used} | **Confidence**: {confidence:.2f}\n\n"
                    response_text = metadata + full_response
                    
                    # Stream word by word
                    words = response_text.split()
                    current_text = ""
                    
                    for word in words:
                        current_text += word + " "
                        yield f"data: {json.dumps({'type': 'token', 'content': current_text})}\n\n"
                        time.sleep(0.05)  # Faster streaming for real responses
                        
            except Exception as e:
                error_msg = f"❌ RAG Error: {str(e)}"
                yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
        
        # Send completion event
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': f'Stream error: {str(e)}'})}\n\n"

@app.route('/examples')
def get_examples():
    """Get example queries"""
    examples = [
        "Who are the stakeholders in this project?",
        "What domain knowledge do stakeholders have?",
        "Show me all the features",
        "What are the project goals?",
        "List all constraints and risks",
        "How are stakeholders connected to features?"
    ]
    return jsonify({'examples': examples})

if __name__ == '__main__':
    print("="*60)
    print("🌐 Starting Flask Web Demo")
    print("="*60)
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🔧 Environment loaded from: {env_path}")
    print(f"🤖 RAG System Available: {RAG_AVAILABLE}")
    
    # Check Neo4j configuration
    neo4j_uri = os.getenv('NEO4J_URI')
    if neo4j_uri:
        print(f"🔗 Neo4j URI: {neo4j_uri}")
    else:
        print("⚠️ Neo4j not configured - demo mode only")
    
    print("-"*60)
    print("🚀 Starting server...")
    print("🌐 Open: http://localhost:5000")
    print("❌ Stop with: Ctrl+C")
    print("="*60)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
"""
Component Indexer for Multi-Modal RAG System
Indexes React/Tailwind components into Pinecone vector database
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
import openai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ComponentIndexer:
    """Indexes UI components into Pinecone vector database"""
    
    def __init__(self):
        """Initialize the component indexer with API credentials"""
        # OpenAI setup
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.llm_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        # Pinecone setup
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "ui-components")
        self.index = None
        
    def initialize_index(self, dimension: int = 1536):
        """
        Initialize or connect to Pinecone index
        
        Args:
            dimension: Embedding vector dimension (default 1536 for text-embedding-3-small)
        """
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx['name'] for idx in existing_indexes]
            
            if self.index_name not in index_names:
                print(f"Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
                    )
                )
            else:
                print(f"Index {self.index_name} already exists")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"Connected to index: {self.index_name}")
            
        except Exception as e:
            print(f"Error initializing index: {e}")
            raise
    
    def generate_component_summary(self, component_code: str, component_name: str) -> str:
        """
        Generate a natural language summary of a component using GPT-4o
        
        Args:
            component_code: The React/Tailwind component code
            component_name: Name of the component
            
        Returns:
            Natural language description of the component
        """
        try:
            prompt = f"""Analyze this React/Tailwind CSS component and provide a detailed description.
Focus on:
1. Visual appearance (colors, layout, spacing)
2. Structure (e.g., "3-column grid", "centered card", "navbar with links")
3. Interactive elements (buttons, inputs, etc.)
4. Use case and purpose

Component Name: {component_name}

Code:
{component_code}

Provide a concise but comprehensive description in 2-3 sentences."""

            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert UI/UX analyzer specializing in React and Tailwind CSS."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary for {component_name}: {e}")
            return f"A React component named {component_name}"
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def index_component(
        self,
        component_id: str,
        component_name: str,
        component_code: str,
        component_type: str = "general",
        tags: List[str] = None
    ) -> bool:
        """
        Index a single component into Pinecone
        
        Args:
            component_id: Unique identifier for the component
            component_name: Human-readable name
            component_code: The actual React/Tailwind code
            component_type: Category (e.g., "button", "card", "navbar")
            tags: Additional tags for filtering
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate summary
            print(f"Generating summary for {component_name}...")
            summary = self.generate_component_summary(component_code, component_name)
            
            # Generate embedding from summary
            print(f"Generating embedding for {component_name}...")
            embedding = self.generate_embedding(summary)
            
            # Prepare metadata
            metadata = {
                "component_id": component_id,
                "name": component_name,
                "type": component_type,
                "code": component_code,
                "summary": summary,
                "tags": tags or []
            }
            
            # Upsert to Pinecone
            print(f"Upserting {component_name} to Pinecone...")
            self.index.upsert(
                vectors=[
                    {
                        "id": component_id,
                        "values": embedding,
                        "metadata": metadata
                    }
                ]
            )
            
            print(f"Successfully indexed: {component_name}")
            return True
            
        except Exception as e:
            print(f"Error indexing component {component_name}: {e}")
            return False
    
    def index_component_library(self, library_path: str) -> Dict[str, int]:
        """
        Index all components from a directory
        
        Args:
            library_path: Path to directory containing component files
            
        Returns:
            Dictionary with success/failure counts
        """
        stats = {"success": 0, "failed": 0}
        library_path = Path(library_path)
        
        if not library_path.exists():
            print(f"Library path does not exist: {library_path}")
            return stats
        
        # Look for component files (JSON format with metadata)
        component_files = list(library_path.glob("*.json"))
        
        print(f"Found {len(component_files)} component files to index")
        
        for comp_file in component_files:
            try:
                with open(comp_file, 'r') as f:
                    component_data = json.load(f)
                
                success = self.index_component(
                    component_id=component_data.get("id", comp_file.stem),
                    component_name=component_data.get("name", comp_file.stem),
                    component_code=component_data.get("code", ""),
                    component_type=component_data.get("type", "general"),
                    tags=component_data.get("tags", [])
                )
                
                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                    
            except Exception as e:
                print(f"Error processing {comp_file}: {e}")
                stats["failed"] += 1
        
        return stats
    
    def search_similar_components(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar components based on a text query
        
        Args:
            query: Search query (natural language description)
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of matching components with scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            components = []
            for match in results.matches:
                components.append({
                    "id": match.id,
                    "score": match.score,
                    "name": match.metadata.get("name", "Unknown"),
                    "type": match.metadata.get("type", "general"),
                    "code": match.metadata.get("code", ""),
                    "summary": match.metadata.get("summary", ""),
                    "tags": match.metadata.get("tags", [])
                })
            
            return components
            
        except Exception as e:
            print(f"Error searching components: {e}")
            return []


def main():
    """Main function to demonstrate component indexing"""
    print("=== Component Indexer for Multi-Modal RAG ===\n")
    
    # Initialize indexer
    indexer = ComponentIndexer()
    indexer.initialize_index()
    
    # Index component library
    library_path = "./component_library"
    print(f"\nIndexing components from: {library_path}")
    stats = indexer.index_component_library(library_path)
    
    print(f"\n=== Indexing Complete ===")
    print(f"Successful: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    
    # Test search
    print("\n=== Testing Search ===")
    test_query = "A button with rounded corners and blue background"
    print(f"Query: {test_query}")
    results = indexer.search_similar_components(test_query, top_k=3)
    
    print(f"\nFound {len(results)} matches:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']} (score: {result['score']:.3f})")
        print(f"   Type: {result['type']}")
        print(f"   Summary: {result['summary'][:100]}...")


if __name__ == "__main__":
    main()

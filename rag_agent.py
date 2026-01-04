"""
Multi-Modal RAG Agent for UI Image to Code Conversion
Uses GPT-4o Vision for image analysis and Pinecone for component retrieval
"""

import os
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai
from component_indexer import ComponentIndexer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MultiModalRAGAgent:
    """
    Multi-Modal RAG Agent that converts UI mockups to React/Tailwind code
    """
    
    def __init__(self):
        """Initialize the Multi-Modal RAG Agent"""
        # OpenAI setup
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vision_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        # Component indexer for retrieval
        self.indexer = ComponentIndexer()
        try:
            self.indexer.initialize_index()
            print("Connected to Pinecone index")
        except Exception as e:
            print(f"Warning: Could not initialize Pinecone index: {e}")
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 for API transmission
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_ui_mockup(self, image_path: str) -> Dict[str, Any]:
        """
        Step 1: Analyze UI mockup using GPT-4o Vision
        Identifies key layout elements and visual characteristics
        
        Args:
            image_path: Path to the UI mockup image
            
        Returns:
            Dictionary containing visual analysis results
        """
        print("\n=== Step 1: Visual Analysis ===")
        print(f"Analyzing UI mockup: {image_path}")
        
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Create vision prompt
            prompt = """Analyze this UI mockup image in detail. Provide:

1. **Overall Layout**: Describe the main structure (e.g., "single column", "two-column with sidebar", "grid layout")

2. **Key Components**: List each major UI element you see:
   - Navigation bars or headers
   - Hero sections or main content areas
   - Buttons (describe style, color, size)
   - Cards or panels
   - Forms or input fields
   - Grids or lists
   - Footer elements

3. **Visual Characteristics**:
   - Color scheme (dominant colors)
   - Typography style
   - Spacing and padding
   - Border radius and shadows
   - Icons or images present

4. **Component Breakdown**: For each section, describe in natural language what component would be needed.

Format your response as a structured analysis that can be used to search for matching code components."""

            response = self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            print(f"\nVisual Analysis:\n{analysis}\n")
            
            # Extract component queries from analysis
            queries = self._extract_component_queries(analysis)
            
            return {
                "full_analysis": analysis,
                "component_queries": queries,
                "image_path": image_path
            }
            
        except Exception as e:
            print(f"Error analyzing UI mockup: {e}")
            raise
    
    def _extract_component_queries(self, analysis: str) -> List[str]:
        """
        Extract search queries from visual analysis
        
        Args:
            analysis: Full visual analysis text
            
        Returns:
            List of search queries for component retrieval
        """
        try:
            prompt = f"""Based on this UI analysis, extract 3-5 specific search queries to find matching React/Tailwind components.

Each query should describe a specific component type needed (e.g., "blue rounded button", "three-column feature grid with icons", "navigation bar with links").

UI Analysis:
{analysis}

Return only the search queries, one per line."""

            response = self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": "You are a UI component expert. Extract specific, searchable component descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            queries_text = response.choices[0].message.content.strip()
            queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
            
            print(f"Extracted {len(queries)} component queries:")
            for i, query in enumerate(queries, 1):
                print(f"  {i}. {query}")
            
            return queries
            
        except Exception as e:
            print(f"Error extracting queries: {e}")
            return []
    
    def retrieve_components(
        self,
        queries: List[str],
        top_k_per_query: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Step 2: Retrieve matching components from Pinecone
        
        Args:
            queries: List of search queries from visual analysis
            top_k_per_query: Number of components to retrieve per query
            
        Returns:
            List of retrieved components with scores
        """
        print("\n=== Step 2: Component Retrieval ===")
        print(f"Retrieving components for {len(queries)} queries")
        
        all_components = []
        seen_ids = set()
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}: {query}")
            
            try:
                results = self.indexer.search_similar_components(
                    query=query,
                    top_k=top_k_per_query
                )
                
                for result in results:
                    # Avoid duplicates
                    if result['id'] not in seen_ids:
                        seen_ids.add(result['id'])
                        all_components.append({
                            **result,
                            "query": query
                        })
                        print(f"  - Found: {result['name']} (score: {result['score']:.3f})")
                
            except Exception as e:
                print(f"  Error retrieving for query '{query}': {e}")
        
        print(f"\nTotal unique components retrieved: {len(all_components)}")
        return all_components
    
    def assemble_final_code(
        self,
        image_path: str,
        visual_analysis: str,
        retrieved_components: List[Dict[str, Any]]
    ) -> str:
        """
        Step 3: Assemble final React component code
        Combines retrieved components with visual analysis
        
        Args:
            image_path: Path to original UI mockup
            visual_analysis: Full visual analysis from Step 1
            retrieved_components: Components retrieved from Pinecone
            
        Returns:
            Complete React/Tailwind component code
        """
        print("\n=== Step 3: Code Assembly ===")
        print("Assembling final React component...")
        
        try:
            # Encode image for reference
            base64_image = self.encode_image(image_path)
            
            # Prepare component context
            component_context = self._format_component_context(retrieved_components)
            
            # Create assembly prompt
            prompt = f"""You are an expert React/Tailwind CSS developer. Generate a complete, functional React component that matches the UI mockup image.

**Visual Analysis:**
{visual_analysis}

**Available Component Code for Reference:**
{component_context}

**Instructions:**
1. Create a single, cohesive React component that recreates the UI mockup
2. Use Tailwind CSS classes for all styling
3. Combine and adapt the retrieved components as needed
4. Ensure the layout, colors, spacing, and visual hierarchy match the mockup
5. Include proper component structure with props
6. Make the component responsive using Tailwind breakpoints
7. Add appropriate hover states and transitions

**Output Format:**
- Provide ONLY the React component code
- Start with imports if needed
- Use modern React functional component syntax
- Include JSX with Tailwind classes
- Add brief comments for complex sections

Generate the complete React component now:"""

            response = self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2500,
                temperature=0.4
            )
            
            generated_code = response.choices[0].message.content
            
            # Clean up code formatting
            generated_code = self._clean_code_output(generated_code)
            
            print("\n✓ Code assembly complete!")
            return generated_code
            
        except Exception as e:
            print(f"Error assembling code: {e}")
            raise
    
    def _format_component_context(self, components: List[Dict[str, Any]]) -> str:
        """
        Format retrieved components for the assembly prompt
        
        Args:
            components: List of retrieved components
            
        Returns:
            Formatted string with component code and descriptions
        """
        context_parts = []
        
        for i, comp in enumerate(components[:8], 1):  # Limit to top 8 to avoid token limits
            context_parts.append(f"""
### Component {i}: {comp['name']}
**Type:** {comp['type']}
**Description:** {comp['summary']}
**Code:**
```jsx
{comp['code']}
```
""")
        
        return "\n".join(context_parts)
    
    def _clean_code_output(self, code: str) -> str:
        """
        Clean up generated code output
        
        Args:
            code: Raw generated code
            
        Returns:
            Cleaned code string
        """
        # Remove markdown code fences if present
        if "```" in code:
            lines = code.split('\n')
            cleaned_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or not line.strip().startswith("```"):
                    cleaned_lines.append(line)
            
            code = '\n'.join(cleaned_lines)
        
        return code.strip()
    
    def generate_code_from_mockup(
        self,
        image_path: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Convert UI mockup to React/Tailwind code
        
        Args:
            image_path: Path to UI mockup image
            output_path: Optional path to save generated code
            
        Returns:
            Dictionary containing all results
        """
        print("=" * 60)
        print("MULTI-MODAL RAG AGENT - UI TO CODE CONVERSION")
        print("=" * 60)
        
        try:
            # Step 1: Visual Analysis
            analysis_result = self.analyze_ui_mockup(image_path)
            
            # Step 2: Component Retrieval
            retrieved_components = self.retrieve_components(
                analysis_result['component_queries']
            )
            
            # Step 3: Code Assembly
            generated_code = self.assemble_final_code(
                image_path,
                analysis_result['full_analysis'],
                retrieved_components
            )
            
            # Save output if path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(generated_code)
                print(f"\n✓ Code saved to: {output_path}")
            
            result = {
                "success": True,
                "analysis": analysis_result['full_analysis'],
                "queries": analysis_result['component_queries'],
                "retrieved_components": len(retrieved_components),
                "generated_code": generated_code,
                "output_path": str(output_path) if output_path else None
            }
            
            print("\n" + "=" * 60)
            print("CONVERSION COMPLETE!")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"\n✗ Error in conversion pipeline: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main function to demonstrate the RAG agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rag_agent.py <image_path> [output_path]")
        print("\nExample:")
        print("  python rag_agent.py mockup.png generated_component.jsx")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "generated_component.jsx"
    
    # Verify image exists
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    # Create agent and generate code
    agent = MultiModalRAGAgent()
    result = agent.generate_code_from_mockup(image_path, output_path)
    
    if result['success']:
        print(f"\n📊 Summary:")
        print(f"  - Components retrieved: {result['retrieved_components']}")
        print(f"  - Output saved to: {result['output_path']}")
        print(f"\n📝 Generated Code Preview:")
        print("-" * 60)
        code_preview = result['generated_code'][:500]
        print(code_preview)
        if len(result['generated_code']) > 500:
            print("...")
    else:
        print(f"\n✗ Conversion failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Example Usage Script for Multi-Modal RAG System
Demonstrates various usage patterns and API capabilities
"""

from main import MultiModalRAGSystem
from component_indexer import ComponentIndexer
from rag_agent import MultiModalRAGAgent
from validator import CodeValidator
from pathlib import Path


def example_1_basic_conversion():
    """
    Example 1: Basic mockup to code conversion
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Mockup Conversion")
    print("=" * 70)
    
    system = MultiModalRAGSystem()
    
    # Note: Replace with your actual mockup image path
    mockup_path = "example_mockup.png"
    
    if not Path(mockup_path).exists():
        print(f"⚠ Mockup image not found: {mockup_path}")
        print("  Please provide a valid mockup image to run this example")
        return
    
    result = system.convert_mockup_to_code(
        mockup_image_path=mockup_path,
        validate=True
    )
    
    system.print_summary(result)


def example_2_custom_output_no_validation():
    """
    Example 2: Custom output path without validation (faster)
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Fast Conversion Without Validation")
    print("=" * 70)
    
    system = MultiModalRAGSystem()
    
    mockup_path = "example_mockup.png"
    
    if not Path(mockup_path).exists():
        print(f"⚠ Mockup image not found: {mockup_path}")
        return
    
    result = system.convert_mockup_to_code(
        mockup_image_path=mockup_path,
        output_code_path="./output/CustomComponent.jsx",
        validate=False  # Skip validation for speed
    )
    
    if result['success']:
        print(f"\n✓ Code generated: {result['output_path']}")
        print(f"  Components retrieved: {result['retrieved_components']}")


def example_3_index_custom_components():
    """
    Example 3: Index custom component library
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Indexing Custom Component Library")
    print("=" * 70)
    
    indexer = ComponentIndexer()
    indexer.initialize_index()
    
    # Example: Add a custom component programmatically
    custom_component = {
        "id": "custom-alert",
        "name": "Alert Box",
        "type": "notification",
        "tags": ["alert", "notification", "warning"],
        "code": """export default function Alert({ message, type = 'info' }) {
  const colors = {
    info: 'bg-blue-100 text-blue-800 border-blue-300',
    success: 'bg-green-100 text-green-800 border-green-300',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    error: 'bg-red-100 text-red-800 border-red-300'
  };
  
  return (
    <div className={`p-4 rounded-lg border ${colors[type]}`}>
      {message}
    </div>
  );
}"""
    }
    
    success = indexer.index_component(
        component_id=custom_component['id'],
        component_name=custom_component['name'],
        component_code=custom_component['code'],
        component_type=custom_component['type'],
        tags=custom_component['tags']
    )
    
    if success:
        print(f"\n✓ Successfully indexed: {custom_component['name']}")
        
        # Test search
        print("\nTesting search for 'notification box'...")
        results = indexer.search_similar_components("notification box", top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result['name']} (score: {result['score']:.3f})")


def example_4_search_and_retrieve():
    """
    Example 4: Search component library
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Searching Component Library")
    print("=" * 70)
    
    indexer = ComponentIndexer()
    try:
        indexer.initialize_index()
    except Exception as e:
        print(f"⚠ Could not connect to index: {e}")
        print("  Run 'python main.py --index-only' first")
        return
    
    # Example searches
    queries = [
        "rounded blue button with hover effect",
        "three column grid layout",
        "navigation bar with logo",
        "form input field with validation"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = indexer.search_similar_components(query, top_k=2)
        
        for result in results:
            print(f"  → {result['name']} ({result['type']}) - score: {result['score']:.3f}")


def example_5_validate_existing_code():
    """
    Example 5: Validate pre-existing code
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Validating Existing Code")
    print("=" * 70)
    
    # Sample React component
    sample_code = """export default function FeatureCard({ title, description }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}"""
    
    # Save sample code
    code_path = Path("./tmp_validation_test.jsx")
    with open(code_path, 'w') as f:
        f.write(sample_code)
    
    print(f"Created sample code at: {code_path}")
    
    # Create a simple mockup for comparison (would normally be a real image)
    mockup_path = "example_mockup.png"
    
    if not Path(mockup_path).exists():
        print(f"\n⚠ Mockup image not found: {mockup_path}")
        print("  Skipping validation (need mockup image for comparison)")
        return
    
    validator = CodeValidator()
    result = validator.validate_generated_code(
        sample_code,
        mockup_path,
        component_name="sample_component"
    )
    
    if result['success']:
        print(f"\n✓ Validation complete!")
        print(f"  Fidelity Score: {result['fidelity_score']:.3f}")
        print(f"  Quality: {result['quality']}")


def example_6_programmatic_api():
    """
    Example 6: Using the programmatic API
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Programmatic API Usage")
    print("=" * 70)
    
    # Create RAG agent directly
    agent = MultiModalRAGAgent()
    
    mockup_path = "example_mockup.png"
    
    if not Path(mockup_path).exists():
        print(f"⚠ Mockup image not found: {mockup_path}")
        return
    
    # Step-by-step execution
    print("\nStep 1: Analyzing mockup...")
    analysis = agent.analyze_ui_mockup(mockup_path)
    print(f"  Extracted {len(analysis['component_queries'])} queries")
    
    print("\nStep 2: Retrieving components...")
    components = agent.retrieve_components(analysis['component_queries'])
    print(f"  Retrieved {len(components)} components")
    
    print("\nStep 3: Assembling code...")
    code = agent.assemble_final_code(
        mockup_path,
        analysis['full_analysis'],
        components
    )
    print(f"  Generated {len(code.split(chr(10)))} lines of code")
    
    # Save result
    output_path = Path("./output/programmatic_component.jsx")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"\n✓ Code saved to: {output_path}")


def main():
    """Run all examples"""
    print("=" * 70)
    print("MULTI-MODAL RAG SYSTEM - USAGE EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates various ways to use the system.")
    print("Note: Some examples require a valid mockup image file.")
    
    examples = [
        ("Basic Conversion", example_1_basic_conversion),
        ("Custom Output (No Validation)", example_2_custom_output_no_validation),
        ("Index Custom Components", example_3_index_custom_components),
        ("Search Components", example_4_search_and_retrieve),
        ("Validate Existing Code", example_5_validate_existing_code),
        ("Programmatic API", example_6_programmatic_api),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nTo run a specific example, modify this script or run individual functions.")
    print("\nRunning Example 3 (Indexing) and Example 4 (Search) as demonstration...\n")
    
    # Run safe examples that don't require external files
    example_3_index_custom_components()
    example_4_search_and_retrieve()


if __name__ == "__main__":
    main()

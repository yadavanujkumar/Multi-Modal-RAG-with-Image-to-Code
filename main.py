"""
Main Entry Point for Multi-Modal RAG UI Agent System
Orchestrates the complete pipeline: Indexing → Analysis → Retrieval → Assembly → Validation
"""

import os
import sys
from pathlib import Path
from typing import Optional
import argparse
from dotenv import load_dotenv

from component_indexer import ComponentIndexer
from rag_agent import MultiModalRAGAgent
from validator import CodeValidator

# Load environment variables
load_dotenv()


class MultiModalRAGSystem:
    """
    Complete Multi-Modal RAG System for UI Image to Code Conversion
    """
    
    def __init__(self):
        """Initialize the system components"""
        print("Initializing Multi-Modal RAG System...")
        self.indexer = ComponentIndexer()
        self.rag_agent = MultiModalRAGAgent()
        self.validator = CodeValidator()
        print("✓ System initialized\n")
    
    def setup_component_library(self, library_path: str = "./component_library"):
        """
        Initialize and index component library
        
        Args:
            library_path: Path to component library directory
        """
        print("=" * 70)
        print("STEP 0: COMPONENT LIBRARY SETUP")
        print("=" * 70)
        
        # Initialize Pinecone index
        self.indexer.initialize_index()
        
        # Index components
        if Path(library_path).exists():
            stats = self.indexer.index_component_library(library_path)
            print(f"\n✓ Component library indexed: {stats['success']} successful, {stats['failed']} failed")
        else:
            print(f"\n⚠ Warning: Component library not found at {library_path}")
            print("  Continuing without indexing (may affect retrieval quality)")
        
        print()
    
    def convert_mockup_to_code(
        self,
        mockup_image_path: str,
        output_code_path: Optional[str] = None,
        validate: bool = True,
        skip_indexing: bool = False
    ) -> dict:
        """
        Complete pipeline to convert UI mockup to code
        
        Args:
            mockup_image_path: Path to UI mockup image
            output_code_path: Path to save generated code (optional)
            validate: Whether to run validation with Playwright
            skip_indexing: Skip component library indexing (if already done)
            
        Returns:
            Dictionary with complete results
        """
        # Verify mockup exists
        if not Path(mockup_image_path).exists():
            return {
                "success": False,
                "error": f"Mockup image not found: {mockup_image_path}"
            }
        
        # Setup component library (unless skipped)
        if not skip_indexing:
            self.setup_component_library()
        
        # Set default output path
        if output_code_path is None:
            mockup_name = Path(mockup_image_path).stem
            output_code_path = f"./generated_components/{mockup_name}_component.jsx"
        
        # Run RAG pipeline
        rag_result = self.rag_agent.generate_code_from_mockup(
            mockup_image_path,
            output_code_path
        )
        
        if not rag_result['success']:
            return rag_result
        
        # Run validation if requested
        validation_result = None
        if validate:
            print("\n")
            component_name = Path(output_code_path).stem
            validation_result = self.validator.validate_generated_code(
                rag_result['generated_code'],
                mockup_image_path,
                component_name
            )
        
        # Combine results
        return {
            "success": True,
            "mockup_path": mockup_image_path,
            "output_path": output_code_path,
            "analysis": rag_result['analysis'],
            "queries": rag_result['queries'],
            "retrieved_components": rag_result['retrieved_components'],
            "generated_code": rag_result['generated_code'],
            "validation": validation_result
        }
    
    def print_summary(self, result: dict):
        """
        Print a formatted summary of results
        
        Args:
            result: Results dictionary from conversion
        """
        print("\n" + "=" * 70)
        print("MULTI-MODAL RAG SYSTEM - EXECUTION SUMMARY")
        print("=" * 70)
        
        if not result.get('success'):
            print(f"\n✗ ERROR: {result.get('error', 'Unknown error')}")
            return
        
        print(f"\n📷 Input Mockup: {result['mockup_path']}")
        print(f"💾 Generated Code: {result['output_path']}")
        print(f"\n📊 Pipeline Statistics:")
        print(f"  • Visual queries extracted: {len(result.get('queries', []))}")
        print(f"  • Components retrieved: {result.get('retrieved_components', 0)}")
        print(f"  • Code lines generated: {len(result['generated_code'].split(chr(10)))}")
        
        if result.get('validation'):
            val = result['validation']
            if val.get('success'):
                print(f"\n✅ Validation Results:")
                print(f"  • Fidelity Score: {val['fidelity_score']:.3f}")
                print(f"  • Quality Rating: {val['quality']}")
                print(f"  • Rendered Output: {val['screenshot_path']}")
            else:
                print(f"\n⚠ Validation Error: {val.get('error', 'Unknown')}")
        
        print("\n" + "=" * 70)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Modal RAG UI Agent - Convert UI mockups to React/Tailwind code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single mockup with validation
  python main.py mockup.png
  
  # Convert with custom output path
  python main.py mockup.png -o custom_component.jsx
  
  # Convert without validation (faster)
  python main.py mockup.png --no-validate
  
  # Index component library only
  python main.py --index-only
  
  # Skip re-indexing if already done
  python main.py mockup.png --skip-indexing
        """
    )
    
    parser.add_argument(
        'mockup',
        nargs='?',
        help='Path to UI mockup image file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output path for generated code (default: ./generated_components/<name>_component.jsx)'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation step (faster, but no fidelity score)'
    )
    
    parser.add_argument(
        '--index-only',
        action='store_true',
        help='Only index component library, do not convert mockup'
    )
    
    parser.add_argument(
        '--skip-indexing',
        action='store_true',
        help='Skip component library indexing (use if already indexed)'
    )
    
    parser.add_argument(
        '--library-path',
        default='./component_library',
        help='Path to component library directory (default: ./component_library)'
    )
    
    args = parser.parse_args()
    
    # Check if API keys are set
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set in environment")
        print("Please set it in .env file or export it")
        sys.exit(1)
    
    if not os.getenv('PINECONE_API_KEY') and not args.no_validate:
        print("Warning: PINECONE_API_KEY not set")
        print("Component retrieval may not work properly")
    
    # Initialize system
    system = MultiModalRAGSystem()
    
    # Index-only mode
    if args.index_only:
        system.setup_component_library(args.library_path)
        print("\n✓ Indexing complete!")
        return
    
    # Require mockup path if not index-only
    if not args.mockup:
        parser.print_help()
        print("\nError: mockup image path is required (unless using --index-only)")
        sys.exit(1)
    
    # Run conversion
    result = system.convert_mockup_to_code(
        mockup_image_path=args.mockup,
        output_code_path=args.output,
        validate=not args.no_validate,
        skip_indexing=args.skip_indexing
    )
    
    # Print summary
    system.print_summary(result)
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()

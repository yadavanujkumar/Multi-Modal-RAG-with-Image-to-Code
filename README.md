# Multi-Modal RAG UI Agent: Image to Code Converter

A complete Python system that converts UI mockups into functional React/Tailwind CSS code using GPT-4o Vision, Pinecone vector search, and automated Playwright validation.

## 🎯 Overview

This Multi-Modal RAG (Retrieval-Augmented Generation) system takes a UI screenshot and generates production-ready React components with Tailwind CSS styling. It uses:

- **GPT-4o Vision** for visual analysis of UI mockups
- **Pinecone Vector Database** for semantic component retrieval
- **Playwright** for automated rendering and validation
- **SSIM/GPT-4o** for fidelity scoring

## 🏗️ Architecture

The system follows a three-step agentic pipeline:

1. **Visual Analysis (Step 1)**: GPT-4o Vision analyzes the UI mockup and identifies key layout elements, components, and visual characteristics
2. **Component Retrieval (Step 2)**: Semantic search queries retrieve matching React/Tailwind components from Pinecone vector database
3. **Code Assembly (Step 3)**: GPT-4o stitches retrieved components into a cohesive, functional React component
4. **Validation (The "Closer")**: Playwright renders the generated code and compares it with the original mockup using structural similarity metrics

## 📋 Requirements

### Dependencies

- Python 3.8+
- OpenAI API key (GPT-4o access)
- Pinecone API key
- Playwright (automatically installs Chromium)

### Installation

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Multi-Modal-RAG-with-Image-to-Code.git
cd Multi-Modal-RAG-with-Image-to-Code

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=ui-components

# Validation Configuration
SIMILARITY_THRESHOLD=0.7
FIDELITY_SCORE_METHOD=ssim  # Options: ssim, gpt4o
```

## 🚀 Quick Start

### Basic Usage

Convert a UI mockup to React code:

```bash
python main.py path/to/mockup.png
```

This will:
1. Index the component library (first run only)
2. Analyze the mockup image
3. Retrieve matching components
4. Generate React/Tailwind code
5. Validate with Playwright
6. Save output to `./generated_components/`

### Advanced Usage

```bash
# Custom output path
python main.py mockup.png -o components/MyComponent.jsx

# Skip validation (faster)
python main.py mockup.png --no-validate

# Skip re-indexing (if library already indexed)
python main.py mockup.png --skip-indexing

# Index component library only
python main.py --index-only

# Use custom component library path
python main.py mockup.png --library-path ./my_components
```

## 📦 Component Library

The system includes a sample component library in `./component_library/` with examples:

- **Buttons**: Primary, secondary, rounded buttons
- **Cards**: Feature cards with icons and descriptions
- **Navigation**: Headers, navbars with links
- **Layouts**: Grid systems, hero sections
- **Forms**: Input fields, text areas

### Adding Custom Components

Add new components as JSON files:

```json
{
  "id": "unique-component-id",
  "name": "Component Name",
  "type": "button|card|navbar|layout|form",
  "tags": ["tag1", "tag2"],
  "code": "export default function ComponentName() { ... }"
}
```

Then re-index:

```bash
python main.py --index-only
```

## 🧩 Module Structure

### `component_indexer.py`

Component Indexing Pipeline:
- Indexes React/Tailwind components into Pinecone
- Generates semantic summaries using GPT-4o
- Creates vector embeddings for similarity search
- Provides search functionality

**Key Methods:**
- `initialize_index()`: Setup Pinecone index
- `generate_component_summary()`: Create natural language descriptions
- `index_component()`: Store component with embeddings
- `search_similar_components()`: Semantic component search

### `rag_agent.py`

Multi-Modal RAG Agent:
- **Step 1**: Visual analysis with GPT-4o Vision
- **Step 2**: Component retrieval from Pinecone
- **Step 3**: Code assembly and generation

**Key Methods:**
- `analyze_ui_mockup()`: Extract visual features from image
- `retrieve_components()`: Find matching components
- `assemble_final_code()`: Generate complete React component

### `validator.py`

Automated Validation:
- Creates HTML wrappers for React components
- Renders with Playwright (headless Chrome)
- Calculates fidelity scores (SSIM or GPT-4o comparison)
- Provides quality ratings

**Key Methods:**
- `create_html_wrapper()`: Generate standalone HTML
- `render_component()`: Playwright screenshot capture
- `calculate_ssim_score()`: Structural similarity measurement
- `calculate_gpt4o_score()`: AI-powered visual comparison

### `main.py`

Orchestration & CLI:
- Complete pipeline execution
- Command-line interface
- Result summarization

## 🎨 Example Workflow

```python
from main import MultiModalRAGSystem

# Initialize system
system = MultiModalRAGSystem()

# Convert mockup to code
result = system.convert_mockup_to_code(
    mockup_image_path="hero_section_mockup.png",
    output_code_path="HeroSection.jsx",
    validate=True
)

# Check results
if result['success']:
    print(f"Fidelity Score: {result['validation']['fidelity_score']:.3f}")
    print(f"Generated Code:\n{result['generated_code']}")
```

## 📊 Output Structure

```
./
├── generated_components/       # Generated React code
│   └── mockup_component.jsx
├── validation_results/         # Validation outputs
│   ├── mockup_component.html
│   └── mockup_component_rendered.png
└── component_library/          # Component index
    ├── button-primary.json
    ├── card-feature.json
    └── ...
```

## 🔍 Validation Metrics

### SSIM (Structural Similarity Index)

- **Range**: 0.0 to 1.0
- **0.8-1.0**: Excellent match
- **0.6-0.8**: Good match
- **0.4-0.6**: Fair match
- **< 0.4**: Needs improvement

### GPT-4o Comparison

Provides detailed analysis:
- Layout fidelity (0-10)
- Visual style fidelity (0-10)
- Component accuracy (0-10)
- Overall score (0-100)
- Qualitative feedback

## 🛠️ Individual Module Usage

### Index Components Only

```bash
python component_indexer.py
```

### Generate Code Only (No Validation)

```bash
python rag_agent.py mockup.png output.jsx
```

### Validate Existing Code

```bash
python validator.py generated_code.jsx original_mockup.png
```

## 🐛 Troubleshooting

### Common Issues

**"Pinecone index not found"**
- Run `python main.py --index-only` first
- Check PINECONE_API_KEY in .env

**"Playwright browser not installed"**
```bash
playwright install chromium
```

**"OpenAI API rate limit"**
- Wait and retry
- Check API quota at platform.openai.com

**Low fidelity scores**
- Try different mockup images (clearer, higher resolution)
- Add more relevant components to library
- Use `gpt4o` validation method for better analysis

## 📝 Technical Details

### Technologies

- **OpenAI GPT-4o**: Vision & text generation
- **Pinecone**: Vector database for semantic search
- **Playwright**: Browser automation
- **Pillow & scikit-image**: Image processing
- **NumPy**: Numerical operations

### Performance

- **Indexing**: ~5-10s per component
- **Visual Analysis**: ~10-15s
- **Retrieval**: ~2-3s for 5 queries
- **Code Assembly**: ~15-20s
- **Validation**: ~5-10s

**Total Pipeline**: ~40-60 seconds per mockup

### Limitations

- Requires clear, well-designed mockups
- Best with standard UI patterns
- Limited to React/Tailwind stack
- GPT-4o API costs apply
- Complex interactions may need manual refinement

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional component library entries
- Support for other frameworks (Vue, Angular)
- More sophisticated validation metrics
- UI mockup preprocessing
- Batch processing capabilities

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o Vision capabilities
- Pinecone for vector database infrastructure
- Playwright team for browser automation
- Tailwind CSS for utility-first styling

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yadavanujkumar/Multi-Modal-RAG-with-Image-to-Code/issues)
- Documentation: See individual module docstrings

---

**Built with ❤️ using GPT-4o Vision, Pinecone, and Playwright**
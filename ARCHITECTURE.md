# Technical Architecture

## System Overview

The Multi-Modal RAG UI Agent is a sophisticated pipeline that combines computer vision, semantic search, and code generation to convert UI mockups into production-ready React components.

## Architecture Diagram

```
┌─────────────────┐
│  UI Mockup      │
│  (PNG/JPG)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              STEP 1: VISUAL ANALYSIS                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ GPT-4o Vision API                                  │  │
│  │ • Analyze layout structure                         │  │
│  │ • Identify components (buttons, cards, nav, etc.)  │  │
│  │ • Extract visual characteristics (colors, spacing) │  │
│  │ • Generate natural language descriptions           │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              STEP 2: COMPONENT RETRIEVAL                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Query Extraction                                   │  │
│  │ • Convert visual descriptions to search queries    │  │
│  └─────────────────┬─────────────────────────────────┘  │
│                    │                                     │
│  ┌─────────────────▼─────────────────────────────────┐  │
│  │ Pinecone Vector Search                             │  │
│  │ • Semantic similarity search                       │  │
│  │ • Retrieve top-k matching components               │  │
│  │ • Filter by type and tags                          │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              STEP 3: CODE ASSEMBLY                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ GPT-4o Code Generation                             │  │
│  │ Input:                                             │  │
│  │   • Original mockup image                          │  │
│  │   • Visual analysis                                │  │
│  │   • Retrieved component code snippets              │  │
│  │                                                    │  │
│  │ Output:                                            │  │
│  │   • Complete React functional component            │  │
│  │   • Tailwind CSS classes for styling              │  │
│  │   • Responsive design patterns                     │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         STEP 4: AUTOMATED VALIDATION (THE CLOSER)        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ HTML Wrapper Generation                            │  │
│  │ • Create standalone HTML with React/Tailwind CDN   │  │
│  └─────────────────┬─────────────────────────────────┘  │
│                    │                                     │
│  ┌─────────────────▼─────────────────────────────────┐  │
│  │ Playwright Rendering                               │  │
│  │ • Headless Chrome browser                          │  │
│  │ • Render React component                           │  │
│  │ • Capture full-page screenshot                     │  │
│  └─────────────────┬─────────────────────────────────┘  │
│                    │                                     │
│  ┌─────────────────▼─────────────────────────────────┐  │
│  │ Fidelity Score Calculation                         │  │
│  │ Method 1: SSIM (Structural Similarity)             │  │
│  │   • Fast, quantitative                             │  │
│  │   • Range: 0.0 - 1.0                               │  │
│  │                                                    │  │
│  │ Method 2: GPT-4o Vision Comparison                 │  │
│  │   • Qualitative analysis                           │  │
│  │   • Detailed feedback on differences               │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Generated      │
│  React Code     │
│  + Validation   │
│  Report         │
└─────────────────┘
```

## Component Details

### 1. Component Indexer (`component_indexer.py`)

**Purpose**: Pre-processes and indexes React/Tailwind components into Pinecone vector database

**Key Operations**:
1. Load component from JSON file
2. Generate natural language summary using GPT-4o
3. Create embedding vector using text-embedding-3-small
4. Store in Pinecone with metadata

**Data Flow**:
```
Component JSON → GPT-4o Summary → Embedding Model → Pinecone
```

**Pinecone Schema**:
```python
{
    "id": "button-primary",
    "values": [0.12, -0.34, ...],  # 1536-dim embedding
    "metadata": {
        "component_id": "button-primary",
        "name": "Primary Button",
        "type": "button",
        "code": "export default function...",
        "summary": "A blue rounded button...",
        "tags": ["button", "primary", "blue"]
    }
}
```

### 2. RAG Agent (`rag_agent.py`)

**Purpose**: Orchestrates the three-step conversion process

#### Step 1: Visual Analysis
- **Input**: UI mockup image (PNG/JPG)
- **Process**: GPT-4o Vision analyzes image structure
- **Output**: 
  - Full text analysis of layout and components
  - 3-5 extracted search queries

#### Step 2: Component Retrieval
- **Input**: Search queries from Step 1
- **Process**: 
  - Convert each query to embedding
  - Cosine similarity search in Pinecone
  - Retrieve top-k matches per query
  - Deduplicate results
- **Output**: List of relevant components with code

#### Step 3: Code Assembly
- **Input**: 
  - Original mockup image
  - Visual analysis
  - Retrieved component code
- **Process**: GPT-4o generates cohesive React component
- **Output**: Complete functional React component

**Prompt Engineering Strategy**:
- System prompts establish expert persona
- Structured output formatting
- Few-shot examples through retrieved components
- Explicit styling constraints (Tailwind only)

### 3. Validator (`validator.py`)

**Purpose**: Automated quality assurance through visual comparison

#### Rendering Pipeline
1. **HTML Wrapper**: Creates standalone HTML with:
   - React 18 UMD
   - ReactDOM UMD
   - Babel standalone (JSX transformation)
   - Tailwind CSS CDN
   - Sample props for component

2. **Playwright Execution**:
   - Launch headless Chromium
   - Navigate to local HTML file
   - Wait for React rendering (2s)
   - Capture full-page screenshot

3. **Fidelity Scoring**:

   **SSIM Method** (fast, quantitative):
   ```python
   # Structural Similarity Index
   # Measures: luminance, contrast, structure
   # Range: 0.0 (different) to 1.0 (identical)
   score = ssim(original, rendered)
   ```

   **GPT-4o Method** (slow, qualitative):
   ```python
   # AI-powered visual comparison
   # Analyzes: layout, style, components
   # Provides: scores + detailed feedback
   score = gpt4o_compare(original, rendered)
   ```

### 4. Main Orchestrator (`main.py`)

**Purpose**: Command-line interface and pipeline coordination

**CLI Commands**:
```bash
# Full pipeline
python main.py mockup.png

# Custom output
python main.py mockup.png -o output.jsx

# Skip validation
python main.py mockup.png --no-validate

# Index only
python main.py --index-only

# Skip re-indexing
python main.py mockup.png --skip-indexing
```

## Data Structures

### Component JSON Format
```json
{
  "id": "unique-id",
  "name": "Human Readable Name",
  "type": "button|card|navbar|layout|form|section|input",
  "tags": ["tag1", "tag2"],
  "code": "export default function Component() { ... }"
}
```

### Pipeline Result Format
```python
{
    "success": bool,
    "mockup_path": str,
    "output_path": str,
    "analysis": str,  # Full visual analysis
    "queries": List[str],  # Search queries
    "retrieved_components": int,  # Count
    "generated_code": str,  # React code
    "validation": {
        "success": bool,
        "fidelity_score": float,  # 0.0-1.0
        "quality": str,  # Excellent|Good|Fair|Needs Improvement
        "detailed_analysis": str,
        "screenshot_path": str
    }
}
```

## API Dependencies

### OpenAI API
- **GPT-4o** (`gpt-4o`):
  - Vision analysis (multi-modal)
  - Query extraction
  - Code generation
  - Visual comparison
  - Token limit: 4096 output tokens
  
- **Embeddings** (`text-embedding-3-small`):
  - Dimension: 1536
  - Max input: 8191 tokens
  - Use: Semantic search

### Pinecone API
- **Index Type**: Serverless
- **Metric**: Cosine similarity
- **Region**: Configurable (default: us-east-1)
- **Vector Dimension**: 1536

### Playwright
- **Browser**: Chromium (headless)
- **Viewport**: 1280x720 (configurable)
- **Wait Strategy**: Timeout-based (2000ms)

## Performance Characteristics

### Latency Breakdown
```
Component Indexing (per component):
├── GPT-4o Summary: 3-5s
├── Embedding Generation: 0.5-1s
└── Pinecone Upsert: 0.2-0.5s
Total: ~5-10s per component

Pipeline Execution (per mockup):
├── Visual Analysis: 10-15s
├── Query Extraction: 3-5s
├── Retrieval (5 queries): 2-3s
├── Code Assembly: 15-20s
└── Validation: 5-10s
Total: ~40-60s per mockup
```

### Token Usage
```
Per Mockup Conversion:
├── Visual Analysis: ~1000 tokens (completion)
├── Query Extraction: ~200 tokens
├── Code Assembly: ~2000 tokens
└── Validation (GPT-4o method): ~500 tokens
Total: ~3700 tokens per mockup

Embedding Tokens:
├── Per Component Summary: ~150 tokens
└── Per Search Query: ~20 tokens
```

### Cost Estimation (OpenAI)
```
Assuming GPT-4o pricing: $5/1M input, $15/1M output
Embedding pricing: $0.13/1M tokens

Per mockup conversion:
- GPT-4o: ~$0.06
- Embeddings: ~$0.0001
Total: ~$0.06 per mockup

Per component indexing:
- GPT-4o: ~$0.02
- Embeddings: ~$0.00002
Total: ~$0.02 per component
```

## Scalability Considerations

### Horizontal Scaling
- Component indexing: Parallelizable (batch processing)
- Multiple mockup processing: Queue-based architecture
- Pinecone: Auto-scales with serverless

### Optimization Strategies
1. **Caching**: Store visual analysis results
2. **Batch Processing**: Index components in batches
3. **Lazy Loading**: Only retrieve top-3 components per query
4. **Async Processing**: Use asyncio for parallel API calls

## Security Considerations

1. **API Key Management**:
   - Store in `.env` file (gitignored)
   - Never commit to version control
   - Rotate keys regularly

2. **Code Injection**:
   - Generated code runs in isolated browser context
   - No server-side execution of generated code
   - Sandbox validation environment

3. **Data Privacy**:
   - Mockup images sent to OpenAI API
   - Component code stored in Pinecone
   - Review terms of service for both providers

## Extensibility

### Adding New Component Types
1. Create JSON file in `component_library/`
2. Run `python main.py --index-only`

### Custom Validation Metrics
Extend `validator.py`:
```python
def calculate_custom_score(img1, img2):
    # Implement custom comparison logic
    return score
```

### Supporting New Frameworks
Modify prompts in `rag_agent.py`:
- Change component syntax (Vue, Angular, Svelte)
- Update HTML wrapper in `validator.py`
- Adjust component library format

## Troubleshooting

### Common Issues

**Issue**: Low fidelity scores
- **Cause**: Complex mockups, limited component library
- **Solution**: Add more similar components, use higher resolution mockups

**Issue**: Slow performance
- **Cause**: API latency, network issues
- **Solution**: Enable caching, reduce top_k, skip validation

**Issue**: Generation errors
- **Cause**: Token limits, malformed prompts
- **Solution**: Simplify mockup, reduce retrieved components

## Future Enhancements

1. **Interactive Refinement**: Allow users to provide feedback and regenerate
2. **Component Variants**: Support dark mode, responsive breakpoints
3. **Asset Extraction**: Detect and extract images, icons from mockups
4. **Accessibility**: Generate ARIA labels, keyboard navigation
5. **Testing**: Generate unit tests for components
6. **Version Control**: Track component library changes
7. **Web Interface**: Build web UI for easier interaction

## References

- [OpenAI GPT-4o Documentation](https://platform.openai.com/docs/models/gpt-4o)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Playwright Python Docs](https://playwright.dev/python/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Documentation](https://react.dev/)

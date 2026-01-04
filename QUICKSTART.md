# Quick Start Guide

Get up and running with the Multi-Modal RAG UI Agent in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key with GPT-4o access
- Pinecone API key (free tier works)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yadavanujkumar/Multi-Modal-RAG-with-Image-to-Code.git
cd Multi-Modal-RAG-with-Image-to-Code
```

### 2. Run Setup Script (Recommended)

```bash
python setup.py
```

This will:
- Check Python version
- Install dependencies
- Install Playwright browsers
- Create `.env` configuration file
- Create output directories

### 3. Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# Get your OpenAI key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# Get your Pinecone key from: https://www.pinecone.io/
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
```

### 4. Index Component Library

```bash
python main.py --index-only
```

This indexes the sample React/Tailwind components (~30 seconds).

## Your First Conversion

### Step 1: Prepare a UI Mockup

Use any UI screenshot or mockup image (PNG, JPG). Examples:
- Landing page hero section
- Navigation bar
- Feature card grid
- Sign-up form

### Step 2: Convert to Code

```bash
python main.py path/to/your/mockup.png
```

The system will:
1. ✓ Analyze the UI mockup with GPT-4o Vision
2. ✓ Search for matching components in vector database
3. ✓ Generate React/Tailwind code
4. ✓ Render and validate with Playwright
5. ✓ Save output to `./generated_components/`

### Step 3: Check Results

```bash
# View generated code
cat generated_components/mockup_component.jsx

# View validation screenshot
open validation_results/mockup_component_rendered.png
```

## Example Commands

### Basic Usage

```bash
# Convert with full pipeline
python main.py ui_mockup.png

# Custom output location
python main.py ui_mockup.png -o MyComponent.jsx

# Skip validation (faster, no fidelity score)
python main.py ui_mockup.png --no-validate
```

### Working with Component Library

```bash
# Re-index after adding components
python main.py --index-only

# Convert without re-indexing (faster)
python main.py mockup.png --skip-indexing
```

## Expected Output

### Console Output
```
============================================================
MULTI-MODAL RAG AGENT - UI TO CODE CONVERSION
============================================================

=== Step 1: Visual Analysis ===
Analyzing UI mockup: mockup.png
Visual Analysis:
[Detailed description of the UI elements...]

Extracted 5 component queries:
  1. navigation bar with logo and links
  2. hero section with gradient background
  3. three-column feature grid with icons
  ...

=== Step 2: Component Retrieval ===
Retrieving components for 5 queries
Total unique components retrieved: 8

=== Step 3: Code Assembly ===
Assembling final React component...
✓ Code assembly complete!

=== AUTOMATED VALIDATION - THE CLOSER ===
Rendering component with Playwright...
✓ Screenshot saved
Calculating fidelity score...

=== VALIDATION RESULTS ===
Fidelity Score: 0.847 (Excellent)
```

### Generated Files

```
generated_components/
└── mockup_component.jsx          # Your React code

validation_results/
├── mockup_component.html         # Rendered HTML
└── mockup_component_rendered.png # Screenshot
```

## Common Issues & Solutions

### Issue: "OPENAI_API_KEY not set"

**Solution**: Edit `.env` file and add your API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "Playwright browser not installed"

**Solution**: Install Chromium:
```bash
playwright install chromium
```

### Issue: "Pinecone index not found"

**Solution**: Index components first:
```bash
python main.py --index-only
```

### Issue: Low fidelity scores

**Solutions**:
- Use higher resolution mockups
- Ensure mockup is clear and well-designed
- Add more relevant components to library
- Try GPT-4o validation method:
  ```bash
  # In .env file
  FIDELITY_SCORE_METHOD=gpt4o
  ```

## Next Steps

### 1. Explore Examples

```bash
python examples.py
```

See 6 different usage patterns:
- Basic conversion
- Custom output paths
- Indexing custom components
- Searching components
- Validating existing code
- Using the programmatic API

### 2. Add Custom Components

Create `component_library/my-component.json`:
```json
{
  "id": "my-component",
  "name": "My Component",
  "type": "card",
  "tags": ["custom"],
  "code": "export default function MyComponent() { ... }"
}
```

Then re-index:
```bash
python main.py --index-only
```

### 3. Read the Documentation

- **README.md**: Complete usage guide
- **ARCHITECTURE.md**: Technical deep-dive
- Module docstrings: In-code documentation

## Tips for Best Results

### Mockup Quality
- ✓ Use high-resolution images (1200px+ width)
- ✓ Clear, well-designed UIs
- ✓ Standard UI patterns (buttons, cards, grids)
- ✗ Avoid hand-drawn sketches
- ✗ Avoid very complex or unique designs

### Component Library
- Start with provided examples
- Add components matching your design system
- Use descriptive names and tags
- Keep code clean and well-formatted

### Iterative Refinement
1. Generate initial code
2. Review fidelity score
3. Add missing components to library
4. Regenerate if needed
5. Manually adjust minor details

## Getting Help

### Documentation
- `python main.py --help` - CLI help
- Module docstrings - API reference
- ARCHITECTURE.md - Technical details

### Troubleshooting
1. Check `.env` configuration
2. Verify API keys are valid
3. Ensure dependencies installed
4. Check console output for errors

### GitHub Issues
Report bugs or request features:
https://github.com/yadavanujkumar/Multi-Modal-RAG-with-Image-to-Code/issues

## Performance Tips

### Speed Optimization
```bash
# Skip validation (fastest)
python main.py mockup.png --no-validate

# Skip re-indexing
python main.py mockup.png --skip-indexing

# Use SSIM instead of GPT-4o for validation
# In .env: FIDELITY_SCORE_METHOD=ssim
```

### Cost Optimization
- Use SSIM validation (free) instead of GPT-4o
- Index components once, reuse for multiple mockups
- Skip validation for prototyping

### Quality Optimization
- Use GPT-4o validation for detailed feedback
- Add more components to library
- Use high-quality mockups
- Iterate based on validation results

## Development Workflow

```bash
# 1. Setup (once)
python setup.py
python main.py --index-only

# 2. Development loop
python main.py new_mockup.png     # Generate
# Review output
# Add missing components if needed
python main.py --index-only        # Re-index
python main.py new_mockup.png     # Regenerate

# 3. Production
python main.py final_mockup.png -o ProductionComponent.jsx
```

## Success Criteria

You're ready to go when:
- ✓ `python main.py --help` shows usage
- ✓ `.env` has valid API keys
- ✓ `python main.py --index-only` succeeds
- ✓ First conversion completes with fidelity score > 0.6

## Resources

- **OpenAI Platform**: https://platform.openai.com/
- **Pinecone Console**: https://app.pinecone.io/
- **Playwright Docs**: https://playwright.dev/python/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **React Docs**: https://react.dev/

---

**Ready to convert your first UI mockup? Let's go!**

```bash
python main.py your_mockup.png
```

"""
Automated Validation Module using Playwright
Renders generated code and compares with original mockup
"""

import os
import base64
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from playwright.sync_api import sync_playwright
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CodeValidator:
    """
    Validates generated React/Tailwind code using Playwright
    Compares rendered output with original mockup
    """
    
    def __init__(self):
        """Initialize the code validator"""
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vision_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.fidelity_method = os.getenv("FIDELITY_SCORE_METHOD", "ssim")
        self.output_dir = Path("./validation_results")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_html_wrapper(self, react_code: str, output_path: str) -> str:
        """
        Create standalone HTML file with React component
        
        Args:
            react_code: React component code
            output_path: Path to save HTML file
            
        Returns:
            Path to created HTML file
        """
        # Extract component name from code
        component_name = "GeneratedComponent"
        if "export default function" in react_code:
            try:
                start = react_code.index("export default function") + 23
                end = react_code.index("(", start)
                component_name = react_code[start:end].strip()
            except (ValueError, IndexError):
                pass
        
        # Create HTML with React, ReactDOM, and Tailwind CDN
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Preview</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        {react_code}
        
        // Sample props for rendering
        const sampleProps = {{
            children: "Click Me",
            title: "Sample Title",
            subtitle: "Sample subtitle text goes here",
            description: "This is a sample description for the component",
            ctaText: "Get Started",
            ctaLink: "#",
            logo: "https://via.placeholder.com/150x50/3B82F6/FFFFFF?text=Logo",
            links: [
                {{ label: "Home", href: "#" }},
                {{ label: "About", href: "#" }},
                {{ label: "Services", href: "#" }},
                {{ label: "Contact", href: "#" }}
            ],
            features: [
                {{ 
                    icon: "⚡", 
                    title: "Fast", 
                    description: "Lightning fast performance" 
                }},
                {{ 
                    icon: "🔒", 
                    title: "Secure", 
                    description: "Bank-level security" 
                }},
                {{ 
                    icon: "🚀", 
                    title: "Scalable", 
                    description: "Grows with your needs" 
                }}
            ],
            onClick: () => console.log("Clicked!"),
            onChange: (e) => console.log("Changed:", e.target.value),
            value: "",
            label: "Input Label",
            placeholder: "Enter text here",
            type: "text",
            icon: "⭐"
        }};
        
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(React.createElement({component_name}, sampleProps));
    </script>
</body>
</html>"""
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def render_component(self, html_path: str, screenshot_path: str) -> bool:
        """
        Render HTML component using Playwright and take screenshot
        
        Args:
            html_path: Path to HTML file
            screenshot_path: Path to save screenshot
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\nRendering component from: {html_path}")
            
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                
                # Navigate to HTML file
                html_path_abs = Path(html_path).resolve()
                page.goto(f"file://{html_path_abs}")
                
                # Wait for React to render
                page.wait_for_timeout(2000)
                
                # Take screenshot
                screenshot_path = Path(screenshot_path)
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                browser.close()
                
            print(f"✓ Screenshot saved to: {screenshot_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error rendering component: {e}")
            return False
    
    def calculate_ssim_score(
        self,
        original_image_path: str,
        rendered_image_path: str
    ) -> float:
        """
        Calculate Structural Similarity Index (SSIM) between images
        
        Args:
            original_image_path: Path to original mockup
            rendered_image_path: Path to rendered component screenshot
            
        Returns:
            SSIM score (0-1, higher is better)
        """
        try:
            # Load images
            img1 = Image.open(original_image_path).convert('RGB')
            img2 = Image.open(rendered_image_path).convert('RGB')
            
            # Resize to same dimensions (use smaller dimensions)
            min_width = min(img1.width, img2.width)
            min_height = min(img1.height, img2.height)
            
            img1 = img1.resize((min_width, min_height), Image.Resampling.LANCZOS)
            img2 = img2.resize((min_width, min_height), Image.Resampling.LANCZOS)
            
            # Convert to numpy arrays
            img1_array = np.array(img1)
            img2_array = np.array(img2)
            
            # Calculate SSIM for each channel
            ssim_scores = []
            for i in range(3):  # RGB channels
                score = ssim(
                    img1_array[:, :, i],
                    img2_array[:, :, i],
                    data_range=255
                )
                ssim_scores.append(score)
            
            # Average across channels
            avg_ssim = np.mean(ssim_scores)
            
            return float(avg_ssim)
            
        except Exception as e:
            print(f"Error calculating SSIM: {e}")
            return 0.0
    
    def calculate_gpt4o_score(
        self,
        original_image_path: str,
        rendered_image_path: str
    ) -> Dict[str, Any]:
        """
        Use GPT-4o Vision to compare images and provide fidelity score
        
        Args:
            original_image_path: Path to original mockup
            rendered_image_path: Path to rendered component screenshot
            
        Returns:
            Dictionary with score and detailed comparison
        """
        try:
            # Encode both images
            with open(original_image_path, "rb") as f:
                original_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            with open(rendered_image_path, "rb") as f:
                rendered_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            prompt = """Compare these two UI images:
1. The ORIGINAL mockup (first image)
2. The RENDERED output (second image)

Evaluate how well the rendered output matches the original mockup across these dimensions:

**Layout Fidelity (0-10)**: How well does the structure and positioning match?
**Visual Style Fidelity (0-10)**: How close are colors, fonts, spacing, shadows?
**Component Accuracy (0-10)**: Are all the UI elements present and correct?

Provide:
1. A score for each dimension
2. An overall fidelity score (0-100, where 100 is perfect match)
3. Brief notes on what matches well and what differs

Format your response as:
Layout: X/10
Visual Style: Y/10
Components: Z/10
Overall Score: N/100
Notes: [your analysis]"""

            response = self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{original_b64}"}
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{rendered_b64}"}
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            # Extract overall score
            score = 0.0
            for line in analysis.split('\n'):
                if 'Overall Score:' in line:
                    try:
                        score_str = line.split(':')[1].strip().split('/')[0]
                        score = float(score_str) / 100.0
                    except (ValueError, IndexError):
                        pass
            
            return {
                "score": score,
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"Error calculating GPT-4o score: {e}")
            return {
                "score": 0.0,
                "analysis": f"Error: {str(e)}"
            }
    
    def validate_generated_code(
        self,
        react_code: str,
        original_mockup_path: str,
        component_name: str = "component"
    ) -> Dict[str, Any]:
        """
        Complete validation pipeline
        
        Args:
            react_code: Generated React component code
            original_mockup_path: Path to original UI mockup
            component_name: Name for output files
            
        Returns:
            Validation results with fidelity score
        """
        print("\n" + "=" * 60)
        print("AUTOMATED VALIDATION - THE CLOSER")
        print("=" * 60)
        
        try:
            # Create HTML wrapper
            html_path = self.output_dir / f"{component_name}.html"
            print(f"\nCreating HTML wrapper...")
            self.create_html_wrapper(react_code, html_path)
            print(f"✓ HTML created: {html_path}")
            
            # Render component and take screenshot
            screenshot_path = self.output_dir / f"{component_name}_rendered.png"
            print(f"\nRendering component with Playwright...")
            render_success = self.render_component(str(html_path), str(screenshot_path))
            
            if not render_success:
                return {
                    "success": False,
                    "error": "Failed to render component"
                }
            
            # Calculate fidelity score
            print(f"\nCalculating fidelity score using method: {self.fidelity_method}")
            
            if self.fidelity_method == "ssim":
                fidelity_score = self.calculate_ssim_score(
                    original_mockup_path,
                    str(screenshot_path)
                )
                detailed_analysis = f"SSIM Score: {fidelity_score:.3f}"
                
            elif self.fidelity_method == "gpt4o":
                gpt_result = self.calculate_gpt4o_score(
                    original_mockup_path,
                    str(screenshot_path)
                )
                fidelity_score = gpt_result["score"]
                detailed_analysis = gpt_result["analysis"]
            
            else:
                # Default to SSIM
                fidelity_score = self.calculate_ssim_score(
                    original_mockup_path,
                    str(screenshot_path)
                )
                detailed_analysis = f"SSIM Score: {fidelity_score:.3f}"
            
            # Determine quality level
            if fidelity_score >= 0.8:
                quality = "Excellent"
            elif fidelity_score >= 0.6:
                quality = "Good"
            elif fidelity_score >= 0.4:
                quality = "Fair"
            else:
                quality = "Needs Improvement"
            
            result = {
                "success": True,
                "fidelity_score": fidelity_score,
                "quality": quality,
                "detailed_analysis": detailed_analysis,
                "html_path": str(html_path),
                "screenshot_path": str(screenshot_path),
                "original_mockup": original_mockup_path
            }
            
            print("\n" + "=" * 60)
            print("VALIDATION RESULTS")
            print("=" * 60)
            print(f"Fidelity Score: {fidelity_score:.3f} ({quality})")
            print(f"\nDetailed Analysis:")
            print(detailed_analysis)
            print(f"\nOriginal mockup: {original_mockup_path}")
            print(f"Rendered output: {screenshot_path}")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"\n✗ Validation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main function to demonstrate validation"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python validator.py <code_file> <original_mockup>")
        print("\nExample:")
        print("  python validator.py generated_component.jsx mockup.png")
        sys.exit(1)
    
    code_file = sys.argv[1]
    mockup_file = sys.argv[2]
    
    # Load generated code
    if not Path(code_file).exists():
        print(f"Error: Code file not found: {code_file}")
        sys.exit(1)
    
    with open(code_file, 'r') as f:
        react_code = f.read()
    
    # Validate
    validator = CodeValidator()
    result = validator.validate_generated_code(
        react_code,
        mockup_file,
        component_name=Path(code_file).stem
    )
    
    if result['success']:
        print(f"\n✓ Validation complete!")
        print(f"  Score: {result['fidelity_score']:.3f}")
        print(f"  Quality: {result['quality']}")
    else:
        print(f"\n✗ Validation failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

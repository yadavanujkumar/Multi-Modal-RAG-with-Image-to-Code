#!/usr/bin/env python3
"""
Setup Script for Multi-Modal RAG UI Agent System
Helps with initial configuration and environment setup
"""

import os
import sys
from pathlib import Path
import subprocess


def check_python_version():
    """Check if Python version is 3.8+"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling Python dependencies...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True
        )
        print("  ✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error installing dependencies: {e}")
        return False


def install_playwright():
    """Install Playwright browsers"""
    print("\nInstalling Playwright browsers...")
    
    try:
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            capture_output=True
        )
        print("  ✓ Playwright Chromium installed")
        return True
    except subprocess.CalledProcessError:
        print("  ⚠ Could not install Playwright browsers automatically")
        print("  Please run: playwright install chromium")
        return False
    except FileNotFoundError:
        print("  ⚠ Playwright not found in PATH")
        print("  Please run: playwright install chromium")
        return False


def setup_env_file():
    """Create .env file from template"""
    print("\nSetting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        response = input("  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("  ⊙ Keeping existing .env file")
            return True
    
    if not env_example.exists():
        print("  ✗ .env.example not found")
        return False
    
    # Copy template
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("  ✓ Created .env file from template")
    print("  ⚠ Please edit .env and add your API keys:")
    print("     - OPENAI_API_KEY")
    print("     - PINECONE_API_KEY")
    print("     - PINECONE_ENVIRONMENT")
    
    return True


def create_directories():
    """Create necessary directories"""
    print("\nCreating output directories...")
    
    directories = [
        "generated_components",
        "validation_results",
        "output"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
    
    print(f"  ✓ Created {len(directories)} directories")
    return True


def check_api_keys():
    """Check if API keys are configured"""
    print("\nChecking API key configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    all_set = True
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("  ⚠ OPENAI_API_KEY not configured")
        all_set = False
    else:
        print("  ✓ OPENAI_API_KEY set")
    
    if not pinecone_key or pinecone_key == "your_pinecone_api_key_here":
        print("  ⚠ PINECONE_API_KEY not configured")
        all_set = False
    else:
        print("  ✓ PINECONE_API_KEY set")
    
    return all_set


def test_imports():
    """Test if all required packages can be imported"""
    print("\nTesting package imports...")
    
    packages = [
        ("openai", "OpenAI"),
        ("pinecone", "Pinecone"),
        ("PIL", "Pillow"),
        ("playwright.sync_api", "Playwright"),
        ("numpy", "NumPy"),
        ("skimage", "scikit-image"),
    ]
    
    all_ok = True
    for module, name in packages:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} not found")
            all_ok = False
    
    return all_ok


def run_index_test():
    """Test component indexing"""
    print("\nTesting component indexing...")
    
    api_keys_set = check_api_keys()
    if not api_keys_set:
        print("  ⊙ Skipping index test (API keys not set)")
        return True
    
    response = input("  Run component library indexing now? (y/N): ")
    if response.lower() != 'y':
        print("  ⊙ Skipping indexing test")
        return True
    
    try:
        print("\n  Indexing components...")
        subprocess.run(
            [sys.executable, "main.py", "--index-only"],
            check=True
        )
        print("  ✓ Indexing test successful")
        return True
    except subprocess.CalledProcessError:
        print("  ✗ Indexing test failed")
        return False


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("\n1. Configure API keys in .env file:")
    print("   - Get OpenAI API key from: https://platform.openai.com/api-keys")
    print("   - Get Pinecone API key from: https://www.pinecone.io/")
    
    print("\n2. Index the component library:")
    print("   python main.py --index-only")
    
    print("\n3. Convert a UI mockup to code:")
    print("   python main.py path/to/mockup.png")
    
    print("\n4. See examples:")
    print("   python examples.py")
    
    print("\n5. Read the documentation:")
    print("   cat README.md")
    
    print("\nFor help:")
    print("   python main.py --help")
    
    print("\n" + "=" * 70)


def main():
    """Main setup routine"""
    print("=" * 70)
    print("MULTI-MODAL RAG UI AGENT - SETUP")
    print("=" * 70)
    print("\nThis script will help you set up the system.\n")
    
    # Run setup steps
    steps = [
        ("Python version check", check_python_version),
        ("Install dependencies", install_dependencies),
        ("Install Playwright", install_playwright),
        ("Setup .env file", setup_env_file),
        ("Create directories", create_directories),
        ("Test imports", test_imports),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"  ✗ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Optional: Test indexing
    run_index_test()
    
    # Summary
    print("\n" + "=" * 70)
    print("SETUP SUMMARY")
    print("=" * 70)
    
    for step_name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {step_name}")
    
    # Next steps
    print_next_steps()
    
    # Return success if all critical steps passed
    critical_steps = results[:4]  # First 4 are critical
    all_critical_passed = all(success for _, success in critical_steps)
    
    sys.exit(0 if all_critical_passed else 1)


if __name__ == "__main__":
    main()

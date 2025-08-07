#!/usr/bin/env python3
"""
Setup script for Atomberg Share of Voice Analysis
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    # Basic packages that should work without external dependencies
    basic_packages = [
        'requests',
        'beautifulsoup4',
        'pandas',
        'numpy'
    ]
    
    for package in basic_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    directories = [
        'data',
        'reports',
        'reports/charts',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}/")

def check_environment():
    """Check Python environment"""
    print("🐍 Checking Python environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")

def main():
    """Main setup function"""
    print("🚀 Atomberg SoV Analysis - Setup")
    print("=" * 40)
    
    check_environment()
    setup_directories()
    
    print("\n✨ Setup completed!")
    print("\nNext steps:")
    print("1. Run demo: python demo.py")
    print("2. Run full analysis: python main.py --keywords 'smart fan' --platforms youtube,twitter")
    print("3. View report: cat ATOMBERG_SOV_REPORT.md")

if __name__ == "__main__":
    main()

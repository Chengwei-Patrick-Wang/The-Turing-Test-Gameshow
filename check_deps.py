#!/usr/bin/env python3
"""
Dependency check script
Verifies all Python dependencies are installed correctly
"""

import sys

def check_dependencies():
    """Check if all required Python packages are installed"""
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'openai': 'OpenAI SDK'
    }
    
    print("Checking Python dependencies...\n")
    
    all_ok = True
    for module_name, display_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - NOT INSTALLED")
            all_ok = False
    
    print()
    
    if all_ok:
        print("✅ All Python dependencies are installed!")
        print("\nNext steps:")
        print("  1. Set API key: export LITELLM_API_KEY='your-key'")
        print("  2. Test connection: python test_ai.py")
        print("  3. Run gameshow: ./start.sh")
        return True
    else:
        print("❌ Some dependencies are missing!")
        print("\nTo install them:")
        print("  pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    print("="*50)
    print("  Python Dependency Check")
    print("="*50)
    print()
    
    success = check_dependencies()
    sys.exit(0 if success else 1)

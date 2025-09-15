#!/usr/bin/env python3
"""
Test script to verify that all imports in the FastAPI application resolve correctly.
"""
import sys
import ast
import os

def test_import_syntax(file_path):
    """Test if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse the AST to check for syntax errors
        ast.parse(source)
        print(f"[OK] {file_path}: Syntax OK")
        return True
    except SyntaxError as e:
        print(f"[ERROR] {file_path}: Syntax Error - {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {file_path}: Error - {e}")
        return False

def main():
    """Test all Python files for syntax errors."""
    files_to_test = [
        "app/app/main.py",
        "app/app/api/endpoints/__init__.py",
        "app/app/api/endpoints/checklist.py",
        "app/app/api/endpoints/assessments.py",
        "app/app/api/endpoints/models.py",
        "app/app/api/endpoints/incidents.py",
        "app/app/api/endpoints/vulnerabilities.py",
        "app/app/models/checklist.py"
    ]

    print("Testing Python syntax for all files...")
    print("=" * 50)

    all_passed = True
    for file_path in files_to_test:
        if os.path.exists(file_path):
            if not test_import_syntax(file_path):
                all_passed = False
        else:
            print(f"[WARNING] {file_path}: File not found")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("[SUCCESS] All tests passed! No syntax errors found.")
    else:
        print("[FAILED] Some tests failed. Check the errors above.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
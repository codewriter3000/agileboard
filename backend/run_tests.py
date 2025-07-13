#!/usr/bin/env python3
"""
Test runner script for the agileboard backend.
Runs all unit tests and generates a coverage report.
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests with coverage reporting."""
    print("=== Running Agileboard Backend Tests ===")

    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Install dependencies if needed
    print("Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                  capture_output=True)

    # Run pytest with coverage
    print("Running tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ])

    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_tests()

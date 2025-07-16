#!/usr/bin/env python3
"""
Docker test runner script for the agileboard backend.
Runs tests in Docker containers with proper database setup.
"""

import subprocess
import sys
import os


def run_tests():
    """Run tests in Docker containers."""
    print("=== Running Agileboard Backend Tests in Docker ===")

    # Change to project root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Build the backend image
    print("Building backend Docker image...")
    result = subprocess.run([
        "docker-compose", "build", "backend"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Failed to build backend image")
        print(result.stderr)
        sys.exit(1)

    # Start the database
    print("Starting database...")
    result = subprocess.run([
        "docker-compose", "up", "-d", "db"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Failed to start database")
        print(result.stderr)
        sys.exit(1)

    # Run the tests
    print("Running tests...")
    result = subprocess.run([
        "docker-compose", "run", "--rm", "backend",
        "python", "-m", "pytest", "tests/", "-v", "--tb=short"
    ])

    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_tests()

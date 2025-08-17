#!/usr/bin/env python3
"""
Test runner script for the Sudoku backend.
Provides convenient commands for running different types of tests.
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    try:
        subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {description} - FAILED")
        return False


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print(
            """
🧪 Sudoku Backend Test Runner

Usage: python test.py <command>

Commands:
  all          Run all tests with coverage (parallel)
  quick        Run all tests without coverage (parallel)
  sequential   Run all tests sequentially (no parallel)
  core         Run core functionality tests
  api          Run API endpoint tests
  models       Run database model tests
  schemas      Run schema validation tests
  coverage     Run all tests with detailed coverage report
  security     Run security-related tests only
  sudoku       Run sudoku engine tests only

Examples:
  python test.py all
  python test.py coverage
  python test.py sequential    # Use when debugging test issues
  python test.py core
        """
        )
        return

    command = sys.argv[1].lower()

    # Base command
    base_cmd = ["uv", "run", "pytest"]

    if command == "all":
        cmd = base_cmd + ["--cov=app", "--cov-report=term-missing", "-v", "-n", "auto"]
        run_command(cmd, "Running all tests with coverage (parallel)")

    elif command == "quick":
        cmd = base_cmd + ["-v", "-n", "auto"]
        run_command(cmd, "Running all tests (quick, parallel)")

    elif command == "sequential":
        cmd = base_cmd + ["--cov=app", "--cov-report=term-missing", "-v"]
        run_command(cmd, "Running all tests sequentially (no parallel)")

    elif command == "core":
        cmd = base_cmd + ["tests/test_core/", "-v"]
        run_command(cmd, "Running core functionality tests")

    elif command == "api":
        cmd = base_cmd + ["tests/test_api/", "-v"]
        run_command(cmd, "Running API endpoint tests")

    elif command == "models":
        cmd = base_cmd + ["tests/test_models/", "-v"]
        run_command(cmd, "Running database model tests")

    elif command == "schemas":
        cmd = base_cmd + ["tests/test_schemas/", "-v"]
        run_command(cmd, "Running schema validation tests")

    elif command == "coverage":
        cmd = base_cmd + [
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=90",
            "-v",
            "-n",
            "auto",
        ]
        success = run_command(cmd, "Running comprehensive coverage analysis (parallel)")
        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")

    elif command == "security":
        cmd = base_cmd + ["tests/test_core/test_security.py", "-v"]
        run_command(cmd, "Running security tests")

    elif command == "sudoku":
        cmd = base_cmd + ["tests/test_core/test_sudoku.py", "-v"]
        run_command(cmd, "Running Sudoku engine tests")

    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python test.py' for usage information")
        return


if __name__ == "__main__":
    main()

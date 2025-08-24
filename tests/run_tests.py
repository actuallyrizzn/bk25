#!/usr/bin/env python3
"""
BK25 Test Runner

Run different types of tests with various configurations
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def run_unit_tests():
    """Run unit tests only"""
    cmd = [
        "python", "-m", "pytest", "tests/unit/",
        "-m", "unit",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests only"""
    cmd = [
        "python", "-m", "pytest", "tests/integration/",
        "-m", "integration",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests only"""
    cmd = [
        "python", "-m", "pytest", "tests/e2e/",
        "-m", "e2e",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "End-to-End Tests")


def run_api_tests():
    """Run API tests only"""
    cmd = [
        "python", "-m", "pytest", "tests/api/",
        "-m", "api",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "API Tests")


def run_all_tests():
    """Run all tests with coverage"""
    cmd = [
        "python", "-m", "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-fail-under=90",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "All Tests with Coverage")


def run_fast_tests():
    """Run fast tests (unit tests only)"""
    cmd = [
        "python", "-m", "pytest", "tests/unit/",
        "-m", "unit",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(cmd, "Fast Tests (Unit Only)")


def run_performance_tests():
    """Run performance and stress tests"""
    cmd = [
        "python", "-m", "pytest",
        "-m", "performance",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(cmd, "Performance Tests")


def run_slow_tests():
    """Run slow tests"""
    cmd = [
        "python", "-m", "pytest",
        "-m", "slow",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(cmd, "Slow Tests")


def run_tests_with_parallel():
    """Run tests with parallel execution"""
    cmd = [
        "python", "-m", "pytest",
        "-n", "auto",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Parallel Tests")


def run_tests_with_rerun():
    """Run tests with automatic rerun on failure"""
    cmd = [
        "python", "-m", "pytest",
        "--reruns", "3",
        "--reruns-delay", "1",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Tests with Rerun")


def run_tests_with_debug():
    """Run tests with debug output"""
    cmd = [
        "python", "-m", "pytest",
        "--tb=long",
        "-v",
        "-s",
        "--log-cli-level=DEBUG"
    ]
    return run_command(cmd, "Tests with Debug Output")


def check_test_dependencies():
    """Check if test dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "httpx",
        "fastapi"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing test dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install -r requirements-dev.txt")
        return False
    
    print("✅ All test dependencies are installed")
    return True


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="BK25 Test Runner")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "api", "all", "fast", "performance", "slow"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Automatically rerun failed tests"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run tests with debug output"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check test dependencies"
    )
    
    args = parser.parse_args()
    
    print("🧪 BK25 Test Runner")
    print("=" * 80)
    
    # Check dependencies if requested
    if args.check_deps:
        if not check_test_dependencies():
            sys.exit(1)
        return
    
    # Check dependencies before running tests
    if not check_test_dependencies():
        print("\n❌ Cannot run tests without required dependencies")
        sys.exit(1)
    
    success = False
    
    # Run tests based on type
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "e2e":
        success = run_e2e_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "fast":
        success = run_fast_tests()
    elif args.type == "performance":
        success = run_performance_tests()
    elif args.type == "slow":
        success = run_slow_tests()
    elif args.type == "all":
        # Apply additional options
        if args.parallel:
            success = run_tests_with_parallel()
        elif args.rerun:
            success = run_tests_with_rerun()
        elif args.debug:
            success = run_tests_with_debug()
        else:
            success = run_all_tests()
    
    # Print summary
    print("\n" + "=" * 80)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

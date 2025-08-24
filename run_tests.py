#!/usr/bin/env python3
"""
BK25 Comprehensive Test Runner
Executes all test categories: Unit, Integration, and End-to-End
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional

class TestRunner:
    """Comprehensive test runner for BK25"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        self.results_dir = self.project_root / "test_results"
        
        # Test categories
        self.test_categories = {
            "unit": {
                "description": "Unit Tests",
                "pattern": "test_*.py",
                "exclude": ["test_*_integration.py", "test_*_e2e.py", "test_fastapi_app.py"]
            },
            "integration": {
                "description": "Integration Tests", 
                "pattern": "test_*_integration.py"
            },
            "e2e": {
                "description": "End-to-End Tests",
                "pattern": "test_fastapi_app.py"
            }
        }
        
        # Test results
        self.results = {}
        
    def setup_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Create test results directory
        self.results_dir.mkdir(exist_ok=True)
        
        # Check if we're in a virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("⚠️  Warning: Not running in a virtual environment")
            print("   Consider activating your virtual environment first")
        
        # Check Python version
        python_version = sys.version_info
        print(f"🐍 Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check if required packages are installed
        required_packages = ["pytest", "pytest-asyncio", "pytest-cov", "fastapi", "httpx"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("   Install with: pip install -r requirements.txt")
            return False
        
        print("✅ Test environment ready")
        return True
    
    def discover_tests(self, category: str) -> List[Path]:
        """Discover test files for a category"""
        if category not in self.test_categories:
            return []
        
        pattern = self.test_categories[category]["pattern"]
        exclude_patterns = self.test_categories[category].get("exclude", [])
        
        test_files = []
        for test_file in self.tests_dir.glob(pattern):
            # Check if file should be excluded
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if test_file.name.startswith(exclude_pattern.replace("*", "")):
                    should_exclude = True
                    break
            
            if not should_exclude:
                test_files.append(test_file)
        
        return test_files
    
    def run_test_category(self, category: str, verbose: bool = False) -> Dict:
        """Run tests for a specific category"""
        if category not in self.test_categories:
            return {"success": False, "error": f"Unknown category: {category}"}
        
        category_info = self.test_categories[category]
        print(f"\n🚀 Running {category_info['description']}...")
        
        # Discover test files
        test_files = self.discover_tests(category)
        if not test_files:
            print(f"⚠️  No test files found for category: {category}")
            return {"success": True, "tests_found": 0, "message": "No tests to run"}
        
        print(f"📁 Found {len(test_files)} test files:")
        for test_file in test_files:
            print(f"   - {test_file.name}")
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            "--tb=short",
            "--disable-warnings",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:test_results/htmlcov",
            "--cov-report=xml:test_results/coverage.xml",
            "--junit-xml=test_results/junit.xml",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add test files
        cmd.extend([str(f) for f in test_files])
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            end_time = time.time()
            
            # Parse results
            success = result.returncode == 0
            duration = end_time - start_time
            
            # Extract test summary
            test_summary = self._parse_test_output(result.stdout, result.stderr)
            
            return {
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_summary": test_summary,
                "tests_found": len(test_files)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out",
                "duration": 300
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_test_output(self, stdout: str, stderr: str) -> Dict:
        """Parse pytest output to extract test summary"""
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Look for pytest summary line
        lines = stdout.split('\n')
        for line in lines:
            if "passed" in line and "failed" in line:
                # Parse line like "5 passed, 1 failed in 2.34s"
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        if "passed" in line and part in line.split("passed")[0]:
                            summary["passed"] = int(part)
                        elif "failed" in line and part in line.split("failed")[0]:
                            summary["failed"] = int(part)
                        elif "skipped" in line and part in line.split("skipped")[0]:
                            summary["skipped"] = int(part)
                        elif "error" in line and part in line.split("error")[0]:
                            summary["errors"] = int(part)
                
                summary["total"] = summary["passed"] + summary["failed"] + summary["skipped"] + summary["errors"]
                break
        
        return summary
    
    def run_all_tests(self, verbose: bool = False, categories: Optional[List[str]] = None) -> Dict:
        """Run all test categories"""
        print("🧪 BK25 Comprehensive Test Suite")
        print("=" * 50)
        
        if not self.setup_environment():
            return {"success": False, "error": "Environment setup failed"}
        
        # Determine which categories to run
        if categories is None:
            categories = list(self.test_categories.keys())
        
        # Run tests for each category
        all_results = {}
        total_start_time = time.time()
        
        for category in categories:
            if category in self.test_categories:
                result = self.run_test_category(category, verbose)
                all_results[category] = result
                
                # Print category results
                if result["success"]:
                    if "test_summary" in result:
                        summary = result["test_summary"]
                        print(f"✅ {self.test_categories[category]['description']} completed")
                        print(f"   Duration: {result['duration']:.2f}s")
                        print(f"   Tests: {summary['total']} total, {summary['passed']} passed, {summary['failed']} failed")
                    else:
                        print(f"✅ {self.test_categories[category]['description']} completed")
                        print(f"   Duration: {result['duration']:.2f}s")
                        print(f"   Message: {result.get('message', 'N/A')}")
                else:
                    print(f"❌ {self.test_categories[category]['description']} failed")
                    if "error" in result:
                        print(f"   Error: {result['error']}")
                    print(f"   Duration: {result.get('duration', 0):.2f}s")
        
        total_duration = time.time() - total_start_time
        
        # Generate overall summary
        overall_success = all(all_results[cat]["success"] for cat in all_results)
        total_tests = sum(all_results[cat].get("test_summary", {}).get("total", 0) for cat in all_results)
        total_passed = sum(all_results[cat].get("test_summary", {}).get("passed", 0) for cat in all_results)
        total_failed = sum(all_results[cat].get("test_summary", {}).get("failed", 0) for cat in all_results)
        
        # Print overall results
        print("\n" + "=" * 50)
        print("📊 OVERALL TEST RESULTS")
        print("=" * 50)
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Overall Success: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        
        # Print category breakdown
        print(f"\nCategory Breakdown:")
        for category, result in all_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = f"{result.get('duration', 0):.2f}s"
            category_name = self.test_categories[category]["description"]
            print(f"  {category_name}: {status} ({duration})")
        
        # Save results
        self._save_results(all_results, overall_success, total_duration)
        
        return {
            "success": overall_success,
            "total_duration": total_duration,
            "categories": all_results,
            "summary": {
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed
            }
        }
    
    def _save_results(self, results: Dict, overall_success: bool, total_duration: float):
        """Save test results to files"""
        # Save detailed results
        results_file = self.results_dir / "test_results.json"
        import json
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "overall_success": overall_success,
                "total_duration": total_duration,
                "categories": results
            }, f, indent=2, default=str)
        
        # Save summary report
        summary_file = self.results_dir / "test_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("BK25 Test Suite Results\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Overall Success: {'PASSED' if overall_success else 'FAILED'}\n")
            f.write(f"Total Duration: {total_duration:.2f}s\n\n")
            
            for category, result in results.items():
                category_name = self.test_categories[category]["description"]
                status = "PASS" if result["success"] else "FAIL"
                duration = f"{result.get('duration', 0):.2f}s"
                
                f.write(f"{category_name}: {status} ({duration})\n")
                
                if "test_summary" in result:
                    summary = result["test_summary"]
                    f.write(f"  Tests: {summary['total']} total, {summary['passed']} passed, {summary['failed']} failed\n")
        
        print(f"\n📁 Results saved to: {self.results_dir}")
        print(f"   Detailed: {results_file}")
        print(f"   Summary: {summary_file}")
    
    def run_coverage_report(self):
        """Generate detailed coverage report"""
        print("\n📊 Generating coverage report...")
        
        try:
            # Generate HTML coverage report
            cmd = [
                sys.executable, "-m", "coverage", "html",
                "--directory=test_results/htmlcov",
                "--title=BK25 Coverage Report"
            ]
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Coverage report generated")
                print(f"   View at: {self.results_dir}/htmlcov/index.html")
            else:
                print("⚠️  Coverage report generation had issues")
                print(f"   Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Failed to generate coverage report: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="BK25 Comprehensive Test Runner")
    parser.add_argument(
        "--categories", "-c",
        nargs="+",
        choices=["unit", "integration", "e2e"],
        help="Test categories to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-r",
        action="store_true",
        help="Generate coverage report after tests"
    )
    
    args = parser.parse_args()
    
    # Create and run test runner
    runner = TestRunner()
    
    try:
        results = runner.run_all_tests(
            verbose=args.verbose,
            categories=args.categories
        )
        
        # Generate coverage report if requested
        if args.coverage and results["success"]:
            runner.run_coverage_report()
        
        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

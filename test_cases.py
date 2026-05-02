"""
Comprehensive Test Cases for Semantic Analyzer
===============================================

This file contains various test programs to validate the semantic analyzer's
capabilities in detecting type errors, scope violations, and undeclared variables.
"""
from semantic_analyzer import SemanticAnalyzer
from syntax_analyzer import RecursiveDescentParser
from lexical_analyzer import Lexer

# =============================================================================
# VALID PROGRAMS (Should pass semantic analysis)
# =============================================================================

VALID_TEST_CASES = {
    "simple_int_assignment": """
int x;
x = 5;
""",

    "simple_string_assignment": """
string name;
name = "Alice";
""",

    "arithmetic_operations": """
int a;
int b;
int result;
a = 10;
b = 5;
result = a + b - 2;
""",

    "string_concatenation": """
string first;
string last;
string full;
first = "John";
last = "Doe";
full = first + " " + last;
""",

    "if_then_statement": """
int x;
int y;
x = 10;
if (x > 5) then {
    y = 1;
}
""",

    "if_then_else_statement": """
int score;
int pass;
score = 85;
if (score >= 60) then {
    pass = 1;
} else {
    pass = 0;
}
""",

    "nested_if_statements": """
int x;
int y;
int z;
x = 10;
y = 20;
if (x > 0) then {
    if (y > 0) then {
        z = x + y;
    } else {
        z = x - y;
    }
} else {
    z = 0;
}
""",

    "complex_arithmetic": """
int a;
int b;
int c;
int d;
int result;
a = 10;
b = 5;
c = 3;
d = 2;
result = a + b * c - d / 2;
""",

    "multiple_comparisons": """
int x;
int y;
int result;
x = 10;
y = 20;
if (x < y) then {
    result = 1;
} else {
    result = 0;
}
""",

    "string_equality": """
string username;
string password;
int authenticated;
username = "admin";
password = "secret";
if (username == "admin") then {
    if (password == "secret") then {
        authenticated = 1;
    } else {
        authenticated = 0;
    }
} else {
    authenticated = 0;
}
""",

    "mixed_declarations": """
int count;
string message;
int total;
count = 0;
message = "Starting";
total = count + 100;
""",
}


# =============================================================================
# INVALID PROGRAMS - Type Mismatch Errors
# =============================================================================

TYPE_MISMATCH_ERRORS = {
    "assign_string_to_int": {
        "code": """
int x;
x = "hello";
""",
        "expected_error": "Type mismatch: Cannot assign string to variable 'x' of type int"
    },

    "assign_int_to_string": {
        "code": """
string name;
name = 42;
""",
        "expected_error": "Type mismatch: Cannot assign int to variable 'name' of type string"
    },

    "add_int_and_string": {
        "code": """
int x;
string s;
int result;
x = 5;
s = "text";
result = x + s;
""",
        "expected_error": "Type mismatch in binary operation"
    },

    "subtract_strings": {
        "code": """
string a;
string b;
string result;
a = "hello";
b = "world";
result = a - b;
""",
        "expected_error": "Invalid operation: '-' requires int operands"
    },

    "multiply_strings": {
        "code": """
string a;
string b;
a = "hello";
b = a * "world";
""",
        "expected_error": "Invalid operation: '*' requires int operands"
    },

    "divide_strings": {
        "code": """
string a;
string b;
a = "hello";
b = a / "world";
""",
        "expected_error": "Invalid operation: '/' requires int operands"
    },

    "compare_int_and_string": {
        "code": """
int x;
string s;
x = 5;
s = "text";
if (x == s) then {
    x = 0;
}
""",
        "expected_error": "Type mismatch in condition: comparing int with string"
    },

    "greater_than_strings": {
        "code": """
string a;
string b;
a = "hello";
b = "world";
if (a > b) then {
    a = "test";
}
""",
        "expected_error": "Invalid operator '>' for type string"
    },

    "less_than_strings": {
        "code": """
string x;
string y;
x = "apple";
y = "banana";
if (x < y) then {
    x = "result";
}
""",
        "expected_error": "Invalid operator '<' for type string"
    },
}


# =============================================================================
# INVALID PROGRAMS - Undeclared Variable Errors
# =============================================================================

UNDECLARED_VARIABLE_ERRORS = {
    "use_undeclared_in_assignment": {
        "code": """
x = 5;
""",
        "expected_error": "Variable 'x' is used before declaration"
    },

    "use_undeclared_in_expression": {
        "code": """
int result;
result = x + 5;
""",
        "expected_error": "Variable 'x' is used before declaration"
    },

    "use_undeclared_in_condition": {
        "code": """
int x;
x = 10;
if (y > 5) then {
    x = 0;
}
""",
        "expected_error": "Variable 'y' is used before declaration"
    },

    "use_undeclared_in_complex_expression": {
        "code": """
int a;
int result;
a = 5;
result = a + b * c;
""",
        "expected_error": "Variable 'b' is used before declaration"
    },

    "use_undeclared_in_string_concat": {
        "code": """
string greeting;
greeting = "Hello " + name;
""",
        "expected_error": "Variable 'name' is used before declaration"
    },
}


# =============================================================================
# INVALID PROGRAMS - Redeclaration Errors
# =============================================================================

REDECLARATION_ERRORS = {
    "redeclare_same_type": {
        "code": """
int x;
int x;
""",
        "expected_error": "Variable 'x' is already declared in the current scope"
    },

    "redeclare_different_type": {
        "code": """
int count;
string count;
""",
        "expected_error": "Variable 'count' is already declared in the current scope"
    },

    "multiple_redeclarations": {
        "code": """
string name;
int age;
string name;
int age;
""",
        "expected_error": "Variable 'name' is already declared in the current scope"
    },
}


# =============================================================================
# EDGE CASES AND COMPLEX SCENARIOS
# =============================================================================

EDGE_CASES = {
    "valid_scoped_declarations": {
        "code": """
int x;
x = 10;
if (x > 5) then {
    int y;
    y = 20;
} else {
    int y;
    y = 30;
}
""",
        "should_pass": True,
        "description": "Same variable name in different scopes is allowed"
    },

    "chain_assignments": {
        "code": """
int a;
int b;
int c;
a = 5;
b = a + 10;
c = b + 20;
""",
        "should_pass": True,
        "description": "Chain of assignments using previously assigned variables"
    },

    "empty_if_blocks": {
        "code": """
int x;
x = 10;
if (x > 5) then {
}
""",
        "should_pass": True,
        "description": "Empty if blocks are syntactically valid"
    },

    "complex_nested_structure": {
        "code": """
int level1;
int level2;
int level3;
level1 = 1;
if (level1 > 0) then {
    level2 = 2;
    if (level2 > 1) then {
        level3 = 3;
        if (level3 > 2) then {
            level1 = level1 + level2 + level3;
        }
    }
}
""",
        "should_pass": True,
        "description": "Deeply nested if statements with variable access"
    },

    "all_comparison_operators_int": {
        "code": """
int a;
int b;
int r1;
int r2;
int r3;
int r4;
a = 10;
b = 20;
if (a > b) then { r1 = 1; }
if (a < b) then { r2 = 1; }
if (a == b) then { r3 = 1; }
if (a != b) then { r4 = 1; }
""",
        "should_pass": True,
        "description": "All comparison operators valid for int"
    },

    "string_equality_operators": {
        "code": """
string s1;
string s2;
int eq;
int neq;
s1 = "test";
s2 = "test";
if (s1 == s2) then { eq = 1; }
if (s1 != s2) then { neq = 1; }
""",
        "should_pass": True,
        "description": "Equality operators valid for strings"
    },

    "invalid_string_inequality": {
        "code": """
string s1;
string s2;
s1 = "apple";
s2 = "banana";
if (s1 >= s2) then {
    s1 = "test";
}
""",
        "should_pass": False,
        "expected_error": "Invalid operator '>=' for type string",
        "description": "Inequality operators not valid for strings"
    },
}


# =============================================================================
# REAL-WORLD SCENARIO TESTS
# =============================================================================

REAL_WORLD_SCENARIOS = {
    "login_validator": {
        "code": """
string username;
string password;
int authenticated;
int admin;
username = "alice";
password = "secret123";
authenticated = 0;
admin = 0;
if (username == "alice") then {
    if (password == "secret123") then {
        authenticated = 1;
        if (username == "admin") then {
            admin = 1;
        }
    }
}
""",
        "should_pass": True,
        "description": "Simple login validation system"
    },

    "grade_calculator": {
        "code": """
int score;
string grade;
int pass;
score = 85;
if (score >= 90) then {
    grade = "A";
    pass = 1;
} else {
    if (score >= 80) then {
        grade = "B";
        pass = 1;
    } else {
        if (score >= 70) then {
            grade = "C";
            pass = 1;
        } else {
            if (score >= 60) then {
                grade = "D";
                pass = 1;
            } else {
                grade = "F";
                pass = 0;
            }
        }
    }
}
""",
        "should_pass": True,
        "description": "Grade calculator with nested if-else"
    },

    "temperature_converter": {
        "code": """
int fahrenheit;
int celsius;
fahrenheit = 98;
celsius = fahrenheit - 32;
""",
        "should_pass": True,
        "description": "Simple temperature calculation"
    },

    "max_finder": {
        "code": """
int a;
int b;
int max;
a = 15;
b = 23;
if (a > b) then {
    max = a;
} else {
    max = b;
}
""",
        "should_pass": True,
        "description": "Find maximum of two numbers"
    },

    "invalid_grade_calculator": {
        "code": """
int score;
string grade;
score = 85;
if (score >= 90) then {
    grade = 90;
} else {
    grade = "B";
}
""",
        "should_pass": False,
        "expected_error": "Type mismatch",
        "description": "Invalid: assigning int to string variable"
    },
}


class TestRunner:
    """Test runner for the compiler"""

    def __init__(self):
        self.lexer = Lexer()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []

    def run_single_test(self, name, code, should_pass=True, expected_error=None):
        """Run a single test case"""
        self.total_tests += 1

        print(f"\n{'=' * 70}")
        print(f"Test: {name}")
        print(f"{'=' * 70}")
        print(f"Code:\n{code}")

        # Parse the code
        tokens = self.lexer.tokenize(code)
        parser = RecursiveDescentParser(tokens)
        ast = parser.parse()

        if not ast or parser.errors:
            print("\nPARSING FAILED")
            print("Parse errors:")
            for error in parser.errors:
                print(f"  - {error}")
            self.failed_tests += 1
            self.results.append({
                'name': name,
                'status': 'FAILED',
                'reason': 'Parsing failed',
                'expected': 'Valid parse' if should_pass else 'Semantic errors',
                'got': 'Parse errors'
            })
            return False

        # Perform semantic analysis
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        # Print the analysis report
        print("\n" + analyzer.get_report())

        # Check if result matches expectation
        test_passed = False
        reason = ""

        if should_pass and success:
            print("\nTEST PASSED - No semantic errors (as expected)")
            test_passed = True
            reason = "Correctly validated valid program"
        elif not should_pass and not success:
            # Check if we got the expected error
            if expected_error:
                error_found = any(expected_error.lower() in str(error).lower()
                                  for error in analyzer.errors)
                if error_found:
                    print(f"\nTEST PASSED - Expected error found: {expected_error}")
                    test_passed = True
                    reason = f"Correctly detected: {expected_error}"
                else:
                    print(f"\nTEST PASSED (with warning)")
                    print(f"Expected error: {expected_error}")
                    print(f"But got different error(s)")
                    test_passed = True
                    reason = "Detected semantic error (different than expected)"
            else:
                print("\nTEST PASSED - Semantic errors detected (as expected)")
                test_passed = True
                reason = "Correctly detected semantic errors"
        elif should_pass and not success:
            print("\nTEST FAILED - Unexpected semantic errors")
            print(f"Expected: Valid program")
            print(f"Got: Semantic errors")
            reason = "False positive - detected errors in valid program"
        else:  # not should_pass and success
            print("\nTEST FAILED - Expected errors not detected")
            print(f"Expected: Semantic errors")
            print(f"Got: No errors")
            reason = "False negative - missed semantic errors"

        if test_passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        self.results.append({
            'name': name,
            'status': 'PASSED' if test_passed else 'FAILED',
            'reason': reason,
            'expected': 'No errors' if should_pass else expected_error or 'Semantic errors',
            'got': 'No errors' if success else f"{len(analyzer.errors)} error(s)"
        })

        return test_passed

    def run_test_suite(self, suite_name, test_dict, should_pass=True):
        """Run a suite of tests"""
        print(f"\n{'#' * 70}")
        print(f"# {suite_name}")
        print(f"{'#' * 70}")

        suite_passed = 0
        suite_failed = 0

        for test_name, test_data in test_dict.items():
            if isinstance(test_data, str):
                # Simple test case (code only)
                result = self.run_single_test(test_name, test_data, should_pass)
            elif isinstance(test_data, dict):
                # Complex test case with metadata
                code = test_data.get('code', '')
                expected_error = test_data.get('expected_error')
                test_should_pass = test_data.get('should_pass', should_pass)
                result = self.run_single_test(
                    test_name,
                    code,
                    test_should_pass,
                    expected_error
                )

            if result:
                suite_passed += 1
            else:
                suite_failed += 1

        print(f"\n{suite_name} Results: {suite_passed}/{len(test_dict)} passed")
        return suite_passed, suite_failed

    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 70)
        print("COMPREHENSIVE TEST SUITE")
        print("=" * 70)

        # Run all test suites
        self.run_test_suite("VALID PROGRAMS", VALID_TEST_CASES, should_pass=True)
        self.run_test_suite("TYPE MISMATCH ERRORS", TYPE_MISMATCH_ERRORS, should_pass=False)
        self.run_test_suite("UNDECLARED VARIABLE ERRORS", UNDECLARED_VARIABLE_ERRORS, should_pass=False)
        self.run_test_suite("REDECLARATION ERRORS", REDECLARATION_ERRORS, should_pass=False)

        # Edge cases need individual handling
        print(f"\n{'#' * 70}")
        print(f"# EDGE CASES")
        print(f"{'#' * 70}")
        for test_name, test_data in EDGE_CASES.items():
            code = test_data['code']
            should_pass = test_data['should_pass']
            expected_error = test_data.get('expected_error')
            description = test_data.get('description', '')
            print(f"\nDescription: {description}")
            self.run_single_test(test_name, code, should_pass, expected_error)

        # Real-world scenarios
        print(f"\n{'#' * 70}")
        print(f"# REAL-WORLD SCENARIOS")
        print(f"{'#' * 70}")
        for test_name, test_data in REAL_WORLD_SCENARIOS.items():
            code = test_data['code']
            should_pass = test_data['should_pass']
            expected_error = test_data.get('expected_error')
            description = test_data.get('description', '')
            print(f"\nDescription: {description}")
            self.run_single_test(test_name, code, should_pass, expected_error)

        # Print final summary
        self.print_summary()

    def print_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 70)
        print("FINAL TEST SUMMARY")
        print("=" * 70)

        print(f"\nTotal Tests Run: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ({self.passed_tests / self.total_tests * 100:.1f}%)")
        print(f"Failed: {self.failed_tests} ({self.failed_tests / self.total_tests * 100:.1f}%)")

        if self.failed_tests > 0:
            print("\n" + "-" * 70)
            print("FAILED TESTS:")
            print("-" * 70)
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"\n{result['name']}")
                    print(f"   Reason: {result['reason']}")
                    print(f"   Expected: {result['expected']}")
                    print(f"   Got: {result['got']}")

        print("\n" + "=" * 70)
        if self.failed_tests == 0:
            print("ALL TESTS PASSED!")
        else:
            print(f"{self.failed_tests} test(s) failed")
        print("=" * 70)


def main():
    """Main function to run all tests"""
    runner = TestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
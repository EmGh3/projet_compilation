"""
An interactive program that performs lexical analysis, syntax analysis,
and semantic analysis on user input.
"""

from typing import Optional
from lexical_analyzer import Lexer
from syntax_analyzer import RecursiveDescentParser, Program
from semantic_analyzer import SemanticAnalyzer
import sys


class InteractiveCompiler:
    """Interactive compiler that performs all three analysis phases"""

    def __init__(self):
        self.lexer = Lexer()

    def print_banner(self):
        """Print welcome banner"""
        print("=" * 80)
        print(" " * 20 + "INTERACTIVE COMPILER FRONTEND")
        print("=" * 80)
        print("\nThis compiler performs three phases of analysis:")
        print("  1. Lexical Analysis  - Tokenizes the input")
        print("  2. Syntax Analysis   - Builds Abstract Syntax Tree (AST)")
        print("  3. Semantic Analysis - Type checking and scope resolution")
        print("\n" + "=" * 80)
        print("\nSupported Language Features:")
        print("  • Variable declarations: int x; string name;")
        print("  • Assignments: x = 5; name = \"Alice\";")
        print("  • Arithmetic: +, -, *, / (for integers)")
        print("  • String concatenation: +")
        print("  • Comparisons: ==, !=, <, >, <=, >=")
        print("  • If-then-else: if (condition) then { ... } else { ... }")
        print("  • Negative numbers: -5, -10, etc.")
        print("\n" + "=" * 80)
        print("\nCommands:")
        print("  'exit' or 'quit' - Exit the program")
        print("  'help'           - Show this help message")
        print("=" * 80 + "\n")

    def print_help(self):
        """Print help message"""
        print("\n" + "=" * 80)
        print("How to use this compiler")
        print("=" * 80)
        print("\nYou can enter multi-line programs. Type your code and press Enter.")
        print("To execute, type 'run' on a new line.")
        print("\nOr enter a complete program in one line:")
        print("\n" + "=" * 80 + "\n")

    def get_multiline_input(self) -> Optional[str]:
        """Get multi-line input from user"""
        print("\nEnter your code (type 'run' on a new line to execute, or 'cancel' to abort):")
        print("-" * 80)

        lines = []
        line_num = 1

        try:
            while True:
                try:
                    line = input(f"{line_num:3d} | ")

                    # Check for special commands
                    if line.strip().lower() == 'run':
                        break
                    elif line.strip().lower() == 'cancel':
                        print("Input cancelled.")
                        return None

                    lines.append(line)
                    line_num += 1

                except EOFError:
                    # Ctrl+D pressed
                    break

        except KeyboardInterrupt:
            print("\n\nInput cancelled.")
            return None

        code = '\n'.join(lines)
        print("-" * 80)
        return code if code.strip() else None

    def analyze_code(self, code: str):
        """Perform all three phases of analysis"""
        print("\n" + "=" * 80)
        print("COMPILATION RESULTS")
        print("=" * 80)


        # Phase 1: Lexical Analysis
        print("\n[PHASE 1: LEXICAL ANALYSIS]")
        print("-" * 80)

        try:
            tokens = self.lexer.tokenize(code)
            print(f"✓ Lexical analysis successful! Generated {len(tokens)} tokens.")
            print("\nTokens:")
            for i, token in enumerate(tokens, 1):
                print(f"  {i:3d}. {token}")

            lexical_success = True

        except Exception as e:
            print(f"✗ Lexical analysis failed!")
            print(f"Error: {str(e)}")
            lexical_success = False
            return

        # Phase 2: Syntax Analysis
        print("\n" + "=" * 80)
        print("[PHASE 2: SYNTAX ANALYSIS]")
        print("-" * 80)

        parser = RecursiveDescentParser(tokens)
        ast = parser.parse()

        if ast and not parser.errors:
            print("✓ Syntax analysis successful! AST generated.")
            print("\nAbstract Syntax Tree (AST):")
            print(ast)
            syntax_success = True
        else:
            print("✗ Syntax analysis failed!")
            print("\nParse Errors:")
            for error in parser.errors:
                print(f"  • {error}")
            syntax_success = False
            return

        # Phase 3: Semantic Analysis
        print("\n" + "=" * 80)
        print("[PHASE 3: SEMANTIC ANALYSIS]")
        print("-" * 80)

        analyzer = SemanticAnalyzer()
        semantic_success = analyzer.analyze(ast)

        # Print symbol table
        print(str(analyzer.symbol_table))

        # Print results
        if semantic_success:
            print("\n✓ Semantic analysis successful! No errors found.")
            print("\n" + "=" * 80)
            print("COMPILATION SUCCESSFUL!")
            print("=" * 80)
            print("\nAll three phases completed without errors:")
            print("  ✓ Lexical Analysis")
            print("  ✓ Syntax Analysis")
            print("  ✓ Semantic Analysis")
        else:
            print("\n✗ Semantic analysis failed!")
            print("\nSemantic Errors:")
            for i, error in enumerate(analyzer.errors, 1):
                print(f"  {i}. {error}")

            print("\n" + "=" * 80)
            print("❌ COMPILATION FAILED")
            print("=" * 80)
            print("\nPhase Results:")
            print("  ✓ Lexical Analysis  - Success")
            print("  ✓ Syntax Analysis   - Success")
            print("  ✗ Semantic Analysis - Failed")

        # Print warnings if any
        if analyzer.warnings:
            print("\nWarnings:")
            for i, warning in enumerate(analyzer.warnings, 1):
                print(f"  {i}. {warning}")

        print("\n" + "=" * 80 + "\n")


    def run(self):
        """Main interactive loop"""
        self.print_banner()

        while True:
            try:
                print("\nOptions:")
                print("  1. Enter multiple line of code")
                print("  2. Show help")
                print("  3. Exit")

                choice = input("\nEnter your choice (1-3) or type single line of code directly: ").strip()

                # Check for direct commands
                if choice.lower() in ['exit', 'quit', '3']:
                    break

                elif choice.lower() == 'clear':
                    # Clear screen (works on Unix-like systems)
                    print("\033[2J\033[H")
                    self.print_banner()
                    continue

                elif choice.lower() in ['help', '2']:
                    self.print_help()
                    continue

                elif choice == '1' or choice == '':
                    # Get multi-line input
                    code = self.get_multiline_input()
                    if code:
                        self.analyze_code(code)

                else:
                    # Treat input as code
                    if choice.strip():
                        self.analyze_code(choice)

            except KeyboardInterrupt:
                print("\n\nUse 'exit' or 'quit' to exit the program.\n")
                continue

            except Exception as e:
                print(f"\nAn unexpected error occurred: {str(e)}")
                print("Please try again.\n")


def main():
    """Main entry point"""
    compiler = InteractiveCompiler()
    compiler.run()


if __name__ == "__main__":
    main()
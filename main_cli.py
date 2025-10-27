import os
import sys
import threading
import time
from typing import Optional, Set

import sqlparse
from colorama import init, Fore, Style

from db import get_connection, SchemaAnalyzer
from openai_client import generate_sql_query
from query_executor import execute_query
from utils import pretty_print_results

# Initialize colorama for cross-platform color support
init(autoreset=True)


class Spinner:
    """A simple spinner that runs in a separate thread."""

    def __init__(self, message: str):
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        """Internal method to display the spinner."""
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        idx = 0
        while self.running:
            sys.stdout.write(f'\r{Fore.CYAN}{spinner_chars[idx]} {self.message}{Style.RESET_ALL}')
            sys.stdout.flush()
            idx = (idx + 1) % len(spinner_chars)
            time.sleep(0.1)

    def __enter__(self):
        """Start the spinner."""
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the spinner."""
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the line and print completion
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.write(f'{Fore.GREEN}✓{Style.RESET_ALL} {self.message}\n')
        sys.stdout.flush()


def extract_mentioned_tables(prompt: str, available_tables: Set[str]) -> Set[str]:
    """
    Extract table names mentioned in the prompt with improved detection.

    Args:
        prompt: User's natural language prompt
        available_tables: Set of available table names in the database

    Returns:
        Set of table names mentioned in the prompt
    """
    mentioned = set()
    prompt_lower = prompt.lower()

    # Split prompt into words for better matching
    words = prompt_lower.split()

    for table in available_tables:
        table_lower = table.lower()

        # Check for exact match
        if table_lower in words:
            mentioned.add(table)
            continue

        # Check for table name within the prompt
        if table_lower in prompt_lower:
            mentioned.add(table)
            continue

        # Check for plural form (simple pluralization)
        if f"{table_lower}s" in prompt_lower:
            mentioned.add(table)
            continue

        # Check if prompt contains the table name with underscores replaced by spaces
        if '_' in table_lower and table_lower.replace('_', ' ') in prompt_lower:
            mentioned.add(table)

    return mentioned


def display_help():
    """Display help information about available commands with improved formatting."""
    help_text = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
║           PROMPT2QUERY CLI - HELP & COMMANDS              ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}Available Commands:{Style.RESET_ALL}
  {Fore.LIGHTGREEN_EX}help{Style.RESET_ALL}      - Display this help message
  {Fore.LIGHTGREEN_EX}tables{Style.RESET_ALL}    - List all available tables in the database
  {Fore.LIGHTGREEN_EX}schema{Style.RESET_ALL}    - Show complete database schema with relationships
  {Fore.LIGHTGREEN_EX}describe <table>{Style.RESET_ALL} - Show detailed schema for a specific table
  {Fore.LIGHTGREEN_EX}history{Style.RESET_ALL}   - Show query history for this session
  {Fore.LIGHTGREEN_EX}clear{Style.RESET_ALL}     - Clear the terminal screen
  {Fore.LIGHTGREEN_EX}exit{Style.RESET_ALL}      - Exit the application (or use 'quit')

{Fore.CYAN}Natural Language Queries:{Style.RESET_ALL}
  For any other input, enter your query in plain English.

{Fore.YELLOW}Examples:{Style.RESET_ALL}
  {Fore.LIGHTYELLOW_EX}> Show me all users who joined last month{Style.RESET_ALL}
  {Fore.LIGHTYELLOW_EX}> What are the top 5 products by revenue?{Style.RESET_ALL}
  {Fore.LIGHTYELLOW_EX}> Count orders by status for the last quarter{Style.RESET_ALL}
  {Fore.LIGHTYELLOW_EX}> Find customers who haven't ordered in 6 months{Style.RESET_ALL}

{Fore.CYAN}Tips:{Style.RESET_ALL}
  • Be specific about time ranges, columns, and conditions
  • Mention table names when querying multiple related tables
  • Results can be exported to CSV in the 'exports' directory
  • Use Ctrl+C to cancel any operation
"""
    print(help_text)


def display_tables(schema_analyzer: SchemaAnalyzer):
    """Display list of available tables with row counts if available."""
    print(f"\n{Fore.CYAN}╔════════════════════════════════════════╗")
    print(f"║     AVAILABLE DATABASE TABLES          ║")
    print(f"╚════════════════════════════════════════╝{Style.RESET_ALL}\n")

    tables = sorted(schema_analyzer.tables.keys())

    if not tables:
        print(f"{Fore.YELLOW}No tables found in the database.{Style.RESET_ALL}")
        return

    for i, table_name in enumerate(tables, 1):
        print(f"  {Fore.GREEN}{i:2d}.{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{table_name}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Total tables: {len(tables)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}Use 'describe <table>' for detailed information{Style.RESET_ALL}\n")


def display_schema(schema_description: str):
    """Display the complete database schema with improved formatting."""
    print(f"\n{Fore.CYAN}╔════════════════════════════════════════╗")
    print(f"║        DATABASE SCHEMA OVERVIEW        ║")
    print(f"╚════════════════════════════════════════╝{Style.RESET_ALL}\n")
    print(schema_description)
    print()


def describe_table(table_name: str, schema_analyzer: SchemaAnalyzer):
    """Display detailed information about a specific table."""
    table_name_cleaned = table_name.strip().lower()

    # Find matching table (case-insensitive)
    matching_table = None
    for table in schema_analyzer.tables.keys():
        if table.lower() == table_name_cleaned:
            matching_table = table
            break

    if not matching_table:
        print(f"{Fore.RED}Table '{table_name}' not found.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Use 'tables' command to see available tables.{Style.RESET_ALL}\n")
        return

    print(f"\n{Fore.CYAN}Table: {Fore.LIGHTCYAN_EX}{matching_table}{Style.RESET_ALL}\n")

    table_info = schema_analyzer.tables[matching_table]

    if 'columns' in table_info:
        print(f"{Fore.GREEN}Columns:{Style.RESET_ALL}")
        for col in table_info['columns']:
            print(f"  • {Fore.LIGHTGREEN_EX}{col['name']}{Style.RESET_ALL} ({col['type']})")

    print()


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_special_commands(
        command: str,
        schema_analyzer: SchemaAnalyzer,
        schema_description: str,
        query_history: list
) -> bool:
    """
    Handle special CLI commands.

    Args:
        command: User input command
        schema_analyzer: Database schema analyzer
        schema_description: Full schema description
        query_history: List of executed queries

    Returns:
        bool: True if command was handled, False if it's a regular query
    """
    command_lower = command.lower().strip()

    # Handle exit commands
    if command_lower in ('exit', 'quit', 'q'):
        return True

    # Handle help
    if command_lower == 'help':
        display_help()
        return True

    # Handle tables list
    if command_lower == 'tables':
        display_tables(schema_analyzer)
        return True

    # Handle schema display
    if command_lower == 'schema':
        display_schema(schema_description)
        return True

    # Handle clear screen
    if command_lower == 'clear':
        clear_screen()
        return True

    # Handle describe table
    if command_lower.startswith('describe '):
        table_name = command[9:].strip()
        describe_table(table_name, schema_analyzer)
        return True

    # Handle query history
    if command_lower == 'history':
        display_query_history(query_history)
        return True

    return False


def display_query_history(query_history: list):
    """Display the query history for this session."""
    if not query_history:
        print(f"\n{Fore.YELLOW}No queries executed in this session yet.{Style.RESET_ALL}\n")
        return

    print(f"\n{Fore.CYAN}╔════════════════════════════════════════╗")
    print(f"║          QUERY HISTORY                 ║")
    print(f"╚════════════════════════════════════════╝{Style.RESET_ALL}\n")

    for i, query_info in enumerate(query_history, 1):
        print(f"{Fore.GREEN}{i}.{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{query_info['prompt'][:60]}...{Style.RESET_ALL}")
        print(f"   {Fore.LIGHTMAGENTA_EX}{query_info['sql'][:80]}...{Style.RESET_ALL}\n")


def display_welcome_banner():
    """Display an attractive welcome banner."""
    banner = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🚀 PROMPT2QUERY CLI v2.0 🚀                  ║
║                                                            ║
║         Natural Language to SQL Query Generator            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}✓ Database connected successfully{Style.RESET_ALL}
{Fore.GREEN}✓ Schema analyzed and ready{Style.RESET_ALL}
{Fore.GREEN}✓ Export directory prepared{Style.RESET_ALL}

{Fore.YELLOW}Type 'help' for available commands or start querying in natural language!{Style.RESET_ALL}
"""
    print(banner)


def confirm_execution() -> bool:
    """
    Prompt user to confirm query execution with improved UX.

    Returns:
        bool: True if user confirms, False otherwise
    """
    while True:
        response = input(f"\n{Fore.YELLOW}Execute this query? [Y/n/e(dit)]:{Style.RESET_ALL} ").lower().strip()

        if response in ('', 'y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        elif response in ('e', 'edit'):
            print(f"{Fore.CYAN}Query editing not yet implemented. Skipping execution.{Style.RESET_ALL}")
            return False
        else:
            print(f"{Fore.RED}Invalid input. Please enter 'y' (yes), 'n' (no), or 'e' (edit).{Style.RESET_ALL}")


def main_cli():
    """Main CLI function with improved error handling and UX."""
    query_history = []

    try:
        # Initialize database connection
        with Spinner("Connecting to database..."):
            conn = get_connection()

        # Create exports directory at startup
        os.makedirs('exports', exist_ok=True)

        # Analyze database schema
        with Spinner("Analyzing database schema..."):
            schema_analyzer = SchemaAnalyzer(conn)
            schema_description = schema_analyzer.analyze()

        # Display welcome banner
        display_welcome_banner()

        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.GREEN}prompt2query >>{Style.RESET_ALL} ").strip()

                # Handle empty input
                if not user_input:
                    continue

                # Handle special commands
                if handle_special_commands(user_input, schema_analyzer, schema_description, query_history):
                    if user_input.lower() in ('exit', 'quit', 'q'):
                        break
                    continue

                # Handle table analysis for the query
                mentioned_tables = extract_mentioned_tables(user_input, schema_analyzer.tables.keys())
                if mentioned_tables:
                    with Spinner("Analyzing table relationships..."):
                        suggested_joins = schema_analyzer.suggest_joins(mentioned_tables)

                    if suggested_joins:
                        print(f"{Fore.CYAN}💡 Suggested JOIN patterns:{Style.RESET_ALL}")
                        for join in suggested_joins:
                            print(f"  {Fore.LIGHTBLUE_EX}→ {join}{Style.RESET_ALL}")

                # Generate SQL query
                with Spinner("Generating SQL query..."):
                    sql_query = generate_sql_query(user_input, schema_description)

                # Display generated query
                print(f"\n{Fore.MAGENTA}📝 Generated SQL Query:{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}{'─' * 60}{Style.RESET_ALL}")
                formatted_query = sqlparse.format(
                    sql_query,
                    reindent=True,
                    keyword_case='upper',
                    strip_comments=True
                )
                print(f"{Fore.LIGHTMAGENTA_EX}{formatted_query}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}{'─' * 60}{Style.RESET_ALL}")

                # Confirm execution
                if confirm_execution():
                    with Spinner("Executing query..."):
                        results_and_columns = execute_query(sql_query, conn)

                    print(f"{Fore.GREEN}✓ Query executed successfully!{Style.RESET_ALL}\n")
                    pretty_print_results(results_and_columns)

                    # Add to history
                    query_history.append({
                        'prompt': user_input,
                        'sql': sql_query
                    })
                else:
                    print(f"{Fore.YELLOW}⚠ Query execution skipped.{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠ Operation cancelled by user.{Style.RESET_ALL}")
                continue
            except Exception as e:
                print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
                print(
                    f"{Fore.LIGHTBLACK_EX}If this persists, try rephrasing your query or check the database connection.{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        return 1
    finally:
        # Cleanup
        try:
            conn.close()
        except:
            pass

        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"Thank you for using Prompt2Query CLI! 👋")
        print(f"{'═' * 60}{Style.RESET_ALL}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main_cli())
import os
from contextlib import contextmanager

import sqlparse
from colorama import init, Fore, Style
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from db import get_connection, SchemaAnalyzer
from openai_client import generate_sql_query
from query_executor import execute_query
from utils import pretty_print_results

# Initialize colorama for cross-platform color support
init()
console = Console()


@contextmanager
def thinking_spinner(message: str):
    """Context manager for showing a thinking spinner."""
    with Live(Panel(f"{message}"), refresh_per_second=20) as live:
        try:
            yield live
        finally:
            live.stop()


def extract_mentioned_tables(prompt: str, available_tables: set) -> set:
    """
    Extract table names mentioned in the prompt.

    Args:
        prompt: User's natural language prompt
        available_tables: Set of available table names in the database

    Returns:
        Set of table names mentioned in the prompt
    """
    mentioned = set()
    prompt_lower = prompt.lower()

    for table in available_tables:
        # Check for both singular and plural forms of table names
        if table.lower() in prompt_lower or f"{table.lower()}s" in prompt_lower:
            mentioned.add(table)

    return mentioned


def display_help():
    """Display help information about available commands."""
    print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}help{Style.RESET_ALL} - Display this help message")
    print(f"  {Fore.GREEN}tables{Style.RESET_ALL} - List all available tables")
    print(f"  {Fore.GREEN}schema{Style.RESET_ALL} - Show complete database schema")
    print(f"  {Fore.GREEN}clear{Style.RESET_ALL} - Clear the screen")
    print(f"  {Fore.GREEN}exit{Style.RESET_ALL} - Exit the application")
    print("\nFor any other input, enter your query in natural language.")
    print("Examples:")
    print(f"  {Fore.YELLOW}> Show me all users who joined last month{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}> What are the top 5 products by revenue?{Style.RESET_ALL}")
    print()


def display_tables(schema_analyzer: SchemaAnalyzer):
    """Display list of available tables."""
    print(f"\n{Fore.CYAN}Available Tables:{Style.RESET_ALL}")
    for table_name in sorted(schema_analyzer.tables.keys()):
        print(f"  {Fore.GREEN}{table_name}{Style.RESET_ALL}")
    print()


def display_schema(schema_description: str):
    """Display the complete database schema."""
    print(f"\n{Fore.CYAN}Database Schema:{Style.RESET_ALL}")
    print(schema_description)
    print()


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_special_commands(command: str, schema_analyzer: SchemaAnalyzer, schema_description: str) -> bool:
    """
    Handle special CLI commands.

    Returns:
        bool: True if command was handled, False if it's a regular query
    """
    command_lower = command.lower().strip()

    if command_lower == 'help':
        display_help()
        return True
    elif command_lower == 'tables':
        display_tables(schema_analyzer)
        return True
    elif command_lower == 'schema':
        display_schema(schema_description)
        return True
    elif command_lower == 'clear':
        clear_screen()
        return True
    elif command_lower in ('exit', 'quit'):
        return True

    return False


def main_cli():
    """Main CLI function."""
    # Initialize database connection
    conn = get_connection()

    # Create exports directory at startup
    os.makedirs('exports', exist_ok=True)

    # Analyze database schema
    with thinking_spinner("Analyzing database schema...") as live:
        schema_analyzer = SchemaAnalyzer(conn)
        schema_description = schema_analyzer.analyze()

    # Display welcome message
    print(f"\n{Fore.GREEN}Welcome to Prompt2Query CLI!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Type 'help' for available commands.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Enter your prompt (or type 'exit' to quit):{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Query results can be exported to CSV in the 'exports' directory.{Style.RESET_ALL}\n")

    while True:
        try:
            # Get user input
            user_input = input(f"{Fore.GREEN}>>{Style.RESET_ALL} ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle special commands
            if handle_special_commands(user_input, schema_analyzer, schema_description):
                if user_input.lower() in ('exit', 'quit'):
                    break
                continue

            # Handle table analysis for the query
            mentioned_tables = extract_mentioned_tables(user_input, schema_analyzer.tables.keys())
            if mentioned_tables:
                with thinking_spinner("Analyzing possible JOIN patterns...") as live:
                    suggested_joins = schema_analyzer.suggest_joins(mentioned_tables)

                if suggested_joins:
                    print(f"\n{Fore.CYAN}Suggested JOIN patterns:{Style.RESET_ALL}")
                    for join in suggested_joins:
                        print(f"  {Fore.LIGHTBLUE_EX}{join}{Style.RESET_ALL}")

            # Generate SQL query
            print("\n")
            with thinking_spinner("Generating SQL query...") as live:
                sql_query = generate_sql_query(user_input, schema_description)

            # Display generated query
            print(f"\n{Fore.MAGENTA}Generated SQL Query:{Style.RESET_ALL}")
            formatted_query = sqlparse.format(sql_query,
                                              reindent=True,
                                              keyword_case='upper',
                                              strip_comments=True)
            print(f"{Fore.LIGHTMAGENTA_EX}{formatted_query}{Style.RESET_ALL}")

            # Confirm execution
            confirm = input(f"\n{Fore.YELLOW}Execute this query? (y/n):{Style.RESET_ALL} ").lower()
            if confirm == "y":
                with thinking_spinner("Executing query...") as live:
                    results_and_columns = execute_query(sql_query, conn)

                print(f"\n{Fore.GREEN}Query Result:{Style.RESET_ALL}")
                pretty_print_results(results_and_columns)
            else:
                print(f"{Fore.RED}Query execution skipped.{Style.RESET_ALL}")

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            continue
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}-------------------------------{Style.RESET_ALL}\n")

    # Cleanup
    conn.close()
    print(f"\n{Fore.GREEN}Thank you for using Prompt2Query CLI!{Style.RESET_ALL}")


if __name__ == "__main__":
    main_cli()

# query_executor.py
import psycopg2
from typing import Tuple, List, Union


def execute_query(query, connection) -> Tuple[Union[List, str], List[str]]:
    """
    Execute a query and return both results and column names.

    Returns:
        Tuple containing:
        - Either a list of results or an error message string
        - List of column names (empty if error)
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        try:
            results = cursor.fetchall()
            # Get column names from cursor description
            column_names = [desc[0] for desc in cursor.description]
        except psycopg2.ProgrammingError:
            results = "No results to fetch (possibly a non-SELECT query)."
            column_names = []
        connection.commit()
        cursor.close()
        return results, column_names
    except Exception as e:
        cursor.close()
        return f"Error executing query: {e}", []


# utils.py
from tabulate import tabulate
from typing import Union, List, Tuple


def pretty_print_results(results_data: Union[Tuple[List, List[str]], Tuple[str, List[str]]]) -> None:
    """
    Pretty print query results with column names.

    Args:
        results_data: Tuple containing:
            - Either list of results or error message string
            - List of column names
    """
    results, column_names = results_data

    if isinstance(results, str):
        print(results)
        return

    if not results:
        print("No results found.")
        return

    if all(len(row) == 1 for row in results):
        # Single column results
        print(f"\n{column_names[0]}:")
        for row in results:
            print(row[0])
    else:
        # Multi-column results
        print(tabulate(results, headers=column_names, tablefmt="psql"))
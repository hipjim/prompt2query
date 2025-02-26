# utils.py
from tabulate import tabulate
from typing import Union, List, Tuple
import csv
from datetime import datetime
import os


def export_to_csv(results_data: Tuple[List, List[str]], filename: str = None) -> str:
    """
    Export query results to a CSV file.

    Args:
        results_data: Tuple containing:
            - List of results
            - List of column names
        filename: Optional filename, if None will generate timestamp-based name

    Returns:
        Path to the created CSV file
    """
    results, column_names = results_data

    if isinstance(results, str):
        raise ValueError(f"Cannot export error message to CSV: {results}")

    if not results:
        raise ValueError("No results to export")

    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"query_results_{timestamp}.csv"

    # Ensure filename has .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'

    # Create 'exports' directory if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    filepath = os.path.join('exports', filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)  # Write headers
        writer.writerows(results)  # Write data

    return filepath


def pretty_print_results(results_data: Tuple[List, List[str]], export_option: bool = True) -> None:
    """
    Pretty print query results with column names and optional CSV export.

    Args:
        results_data: Tuple containing (results list, column names list)
        export_option: Whether to offer CSV export option after displaying results
    """
    """
    Pretty print query results with column names and optional CSV export.

    Args:
        results_data: Tuple containing:
            - Either list of results or error message string
            - List of column names
        export_option: Whether to offer CSV export option
    """
    results, column_names = results_data

    if isinstance(results, str):
        print(results)
        return

    if not results:
        print("No results found.")
        return

    if all(len(row) == 1 for row in results):
        print(f"\n{column_names[0]}:")
        for row in results:
            print(row[0])
    else:
        print(tabulate(results, headers=column_names, tablefmt="psql"))

    if export_option and not isinstance(results, str) and results:
        while True:
            export = input("\nWould you like to export these results to CSV? (y/n): ").lower()
            if export == 'y':
                filename = input("Enter filename (press Enter for automatic name): ").strip()
                try:
                    filepath = export_to_csv(results_data, filename or None)
                    print(f"\nResults exported to: {filepath}")
                except Exception as e:
                    print(f"\nError exporting to CSV: {e}")
                break
            elif export == 'n':
                break
            else:
                print("Please enter 'y' or 'n'")
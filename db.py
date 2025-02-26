import psycopg2

from config import DB_HOST, DB_DATABASE, DB_USER, DB_PASSWORD, DB_PORT
from typing import Dict, List, Set, Tuple


def get_connection():
    """Establishes and returns a PostgreSQL database connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn


class SchemaAnalyzer:
    """Analyzes database schema to infer relationships and provide context to the LLM."""

    def __init__(self, connection):
        self.connection = connection
        self.tables: Dict[str, List[str]] = {}  # table_name -> [columns]
        self.foreign_keys: List[Tuple[str, str, str, str]] = []  # [(table, column, ref_table, ref_column)]
        self.primary_keys: Dict[str, str] = {}  # table_name -> primary_key_column

    def analyze(self) -> str:
        """
        Analyzes the database schema and returns a detailed description
        formatted specifically to help the LLM understand the structure.
        """
        self._extract_table_info()
        self._extract_relationships()
        return self._generate_schema_description()

    def _extract_table_info(self):
        """Extract detailed information about tables and their columns."""
        cursor = self.connection.cursor()

        # Get tables and columns with types
        cursor.execute("""
            SELECT 
                t.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default
            FROM information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name
            WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name, c.ordinal_position;
        """)

        for table, column, data_type, is_nullable, default in cursor.fetchall():
            if table not in self.tables:
                self.tables[table] = []
            self.tables[table].append({
                'name': column,
                'type': data_type,
                'nullable': is_nullable == 'YES',
                'default': default
            })

        # Get primary keys
        cursor.execute("""
            SELECT 
                tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'public';
        """)

        for table, column in cursor.fetchall():
            self.primary_keys[table] = column

        cursor.close()

    def _extract_relationships(self):
        """Extract foreign key relationships between tables."""
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public';
        """)

        self.foreign_keys = cursor.fetchall()
        cursor.close()

    def _generate_schema_description(self) -> str:
        """
        Generate a detailed schema description optimized for LLM understanding.
        """
        description = ["DATABASE SCHEMA DESCRIPTION", ""]

        # Tables and their columns
        description.append("TABLES AND COLUMNS:")
        for table_name, columns in self.tables.items():
            description.append(f"\n{table_name.upper()} TABLE")
            description.append("Columns:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                pk = " (PRIMARY KEY)" if self.primary_keys.get(table_name) == col['name'] else ""
                description.append(f"- {col['name']}: {col['type']} {nullable}{pk}")

        # Relationships
        if self.foreign_keys:
            description.append("\nTABLE RELATIONSHIPS:")
            for table, column, ref_table, ref_column in self.foreign_keys:
                description.append(f"- {table}.{column} -> {ref_table}.{ref_column}")

        # Common Joins
        description.append("\nCOMMON JOIN PATTERNS:")
        for fk in self.foreign_keys:
            description.append(
                f"- To get data from {fk[0]} with {fk[2]}:"
                f"\n  JOIN {fk[2]} ON {fk[0]}.{fk[1]} = {fk[2]}.{fk[3]}"
            )

        return "\n".join(description)

    def suggest_joins(self, tables: Set[str]) -> List[str]:
        """
        Suggest possible JOIN clauses for the given set of tables.
        """
        joins = []
        tables = list(tables)

        for i in range(len(tables)):
            for j in range(i + 1, len(tables)):
                t1, t2 = tables[i], tables[j]
                for table, column, ref_table, ref_column in self.foreign_keys:
                    if (t1 == table and t2 == ref_table) or (t2 == table and t1 == ref_table):
                        joins.append(f"LEFT JOIN {ref_table} ON {table}.{column} = {ref_table}.{ref_column}")

        return joins
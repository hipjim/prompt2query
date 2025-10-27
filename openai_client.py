import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def generate_sql_query(user_prompt, schema):
    """
    Generate a SQL query from a natural language prompt using improved prompt engineering.
    """
    system_prompt = """You are an expert SQL query generator. Your task is to:
1. Analyze the given database schema
2. Generate precise PostgreSQL queries that match the user's intent
3. Include only SELECT statements (no CREATE, INSERT, UPDATE, or DELETE)
4. Always qualify column names with table names to avoid ambiguity
5. Use appropriate JOIN conditions based on likely relationships
6. Include proper WHERE clauses to filter results
7. When doing a text search always search using ignore case
8. Return ONLY the SQL query with no explanations or markdown

Common patterns to follow:
- Use table_name.column_name syntax for all column references
- Include INNER JOIN only when you're certain about relationships
- Use LEFT JOIN when relationships might be optional
- Add appropriate GROUP BY clauses for aggregate functions
- Include ORDER BY for better result presentation"""

    user_prompt_template = """Database Schema:
{schema}

Request: {prompt}

Important:
- Return only the SQL query
- No explanations or markdown
- Use proper table/column qualification
- Ensure syntactically valid PostgreSQL
- Consider NULL values in comparisons
- Use appropriate JOIN types"""

    full_prompt = user_prompt_template.format(
        schema=schema,
        prompt=user_prompt
    )

    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ],
        response_format={"type": "text"}  # Ensure plain text response
    )

    query = response.choices[0].message.content.strip()
    return clean_query(query)


def clean_query(query):
    query = query.strip()
    lines = query.splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    query = " ".join(line.strip() for line in lines if line.strip())

    keywords = ["SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "GROUP BY",
                "ORDER BY", "HAVING", "LIMIT", "AND", "OR", "IN", "NOT", "AS"]

    for keyword in keywords:
        query = query.replace(f" {keyword.lower()} ", f" {keyword} ")
        query = query.replace(f" {keyword.title()} ", f" {keyword} ")

    return query

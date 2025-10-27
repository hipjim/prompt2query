# Prompt2Query: Natural Language to SQL Query CLI 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI-412991.svg)](https://openai.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

> **Transform natural language into SQL queries instantly.** Interact with your database using plain English - no SQL expertise required!

Prompt2Query is an intelligent CLI tool that leverages AI to translate natural language commands into optimized SQL queries, making database querying accessible to everyone.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Processing** | Describe what you want in plain English, get precise SQL |
| 🎨 **Beautiful CLI Interface** | Color-coded, intuitive command-line experience |
| 🔍 **Smart Schema Analysis** | Automatic detection of table relationships and join patterns |
| 👀 **Query Preview & Confirmation** | Review and approve generated SQL before execution |
| 📊 **Export to CSV** | Save query results to CSV files instantly |
| 📚 **Query History** | Track all queries executed in your session |
| 🔗 **Relationship Suggestions** | Intelligent JOIN pattern recommendations |
| 🛡️ **Safe Execution** | Always confirm before running queries |

---

## 🎬 Quick Demo

```bash
prompt2query >> Show me all users who joined in the last 30 days

✓ Generating SQL query...

📝 Generated SQL Query:
────────────────────────────────────────────────────────
SELECT *
FROM users
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY created_at DESC;
────────────────────────────────────────────────────────

Execute this query? [Y/n/e(dit)]: y

✓ Query executed successfully!

| id  | username      | email                | created_at          |
|-----|---------------|----------------------|---------------------|
| 142 | john_doe      | john@example.com     | 2024-10-15 14:23:01 |
| 143 | jane_smith    | jane@example.com     | 2024-10-18 09:45:33 |
...
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.7+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL** ([Download](https://www.postgresql.org/download/))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/hipjim/prompt2query.git
   cd prompt2query
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for faster/cheaper queries

   # PostgreSQL Configuration
   DB_HOST=localhost
   DB_DATABASE=your_database_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```

5. **Run the application**
   ```bash
   python main_cli.py
   ```

---

## 📖 Usage Guide

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Display help information and usage examples | `help` |
| `tables` | List all tables in the database | `tables` |
| `schema` | Show complete database schema with relationships | `schema` |
| `describe <table>` | Show detailed schema for a specific table | `describe users` |
| `history` | View all queries executed in current session | `history` |
| `clear` | Clear the terminal screen | `clear` |
| `exit` / `quit` | Exit the application | `exit` |

### Example Natural Language Queries

#### Basic Queries
```
>> Show me all products
>> List users registered today
>> Count total orders
```

#### Filtering & Conditions
```
>> Find users who joined last month
>> Show orders with status 'pending'
>> Get products with price greater than $100
```

#### Aggregations
```
>> What's the average order value?
>> Count orders by status
>> Sum total revenue for this year
```

#### Complex Queries
```
>> Show top 10 customers by total spending
>> Find products that haven't been ordered in 6 months
>> List users who have made more than 5 purchases
>> Calculate monthly revenue for the last quarter
```

#### Joins & Relationships
```
>> Show all orders with customer details
>> List products and their categories
>> Find users and their recent orders
```

---

## 🏗️ Architecture

```
prompt2query/
├── main_cli.py           # Main CLI application & user interface
├── improved_cli.py       # Enhanced version with advanced features
├── db.py                 # Database connection & schema analysis
├── openai_client.py      # OpenAI API integration & prompt engineering
├── query_executor.py     # SQL query execution & result handling
├── utils.py              # Utility functions (formatting, CSV export)
├── requirements.txt      # Python dependencies
├── .env                  # Configuration (not in repo)
└── exports/              # Generated CSV exports
```

### Component Details

#### **main_cli.py / improved_cli.py**
- User interface and interaction loop
- Command parsing and routing
- Visual feedback with spinners and progress indicators

#### **db.py**
- PostgreSQL connection management
- Schema introspection and analysis
- Foreign key relationship detection
- JOIN pattern suggestions

#### **openai_client.py**
- OpenAI API communication
- Prompt engineering for SQL generation
- Context management with schema information

#### **query_executor.py**
- Safe SQL query execution
- Result fetching and formatting
- Error handling and recovery

#### **utils.py**
- Result formatting (tables, JSON)
- CSV export functionality
- Color-coded console output

---

## 🎨 Features in Detail

### Smart Schema Analysis
The tool automatically analyzes your database structure:
- Detects all tables and their columns
- Identifies primary and foreign keys
- Suggests optimal JOIN patterns
- Provides relationship insights

### Query History
Track your database exploration:
- View all queries from current session
- Review prompts and generated SQL
- Learn SQL patterns from examples

### Safe Execution
Safety features built-in:
- Preview SQL before execution
- Confirm sensitive operations
- Graceful error handling
- Transaction support (coming soon)

### Export Capabilities
Save your results:
- Export to CSV format
- Organized in `exports/` directory
- Timestamp-based filenames
- Preserves data types

---

## 🔧 Configuration

### OpenAI Models

Choose the right model for your needs:

| Model | Speed | Cost | Quality | Best For |
|-------|-------|------|---------|----------|
| `gpt-4` | Slower | Higher | Excellent | Complex queries, production |
| `gpt-3.5-turbo` | Fast | Lower | Good | Simple queries, development |

### Database Configuration

Supports various PostgreSQL setups:
- Local development databases
- Remote hosted databases (AWS RDS, etc.)
- Docker containers
- Cloud-managed instances

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
   ```bash
   git clone https://github.com/hipjim/prompt2query.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Add new features
   - Fix bugs
   - Improve documentation
   - Add tests

4. **Commit with clear messages**
   ```bash
   git commit -m 'Add: Amazing new feature that does X'
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linter
flake8 .

# Format code
black .
```

---

## 🗺️ Roadmap

- [ ] **Multi-database support** (MySQL, SQLite, MongoDB)
- [ ] **Query optimization suggestions**
- [ ] **Visual query builder**
- [ ] **Saved query templates**
- [ ] **Collaboration features** (share queries)
- [ ] **Data visualization** (charts, graphs)
- [ ] **Query performance metrics**
- [ ] **Natural language result descriptions**
- [ ] **Voice input support**
- [ ] **Web interface**

---

## 🐛 Troubleshooting

### Common Issues

**API Key Error**
```
Error: OpenAI API key not found
Solution: Ensure OPENAI_API_KEY is set in your .env file
```

**Database Connection Failed**
```
Error: Could not connect to database
Solution: Check DB credentials in .env and ensure PostgreSQL is running
```

**Module Not Found**
```
Error: No module named 'openai'
Solution: Run: pip install -r requirements.txt
```

---

## 📚 Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Tutorial](https://www.w3schools.com/sql/)
- [Python SQLAlchemy Guide](https://docs.sqlalchemy.org/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Prompt2Query Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 🙏 Acknowledgments

- **[OpenAI](https://openai.com/)** - For powerful language models that make natural language SQL possible
- **[Rich](https://github.com/Textualize/rich)** - For beautiful terminal formatting and UI components
- **[Colorama](https://github.com/tartley/colorama)** - For cross-platform colored terminal output
- **[SQLParse](https://github.com/andialbrecht/sqlparse)** - For SQL query formatting and parsing
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - For clean environment variable management

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/hipjim/prompt2query/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hipjim/prompt2query/discussions)
- **Project**: [https://github.com/hipjim/prompt2query](https://github.com/hipjim/prompt2query)

---

<div align="center">

**Made with ❤️ by the Prompt2Query team**

If you find this project useful, please consider giving it a ⭐️

[⬆ Back to Top](#prompt2query-natural-language-to-sql-query-cli-)

</div>
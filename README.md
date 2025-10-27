# Prompt2Query: Natural Language to SQL Query CLI

![Prompt2Query Banner](https://raw.githubusercontent.com/hipjim/prompt2query/main/assets/banner.svg)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Prompt2Query is a powerful command-line agent that translates natural language into SQL queries using AI, allowing users to interact with databases without writing complex SQL code.

## 🌟 Features

- **Natural Language Processing**: Convert plain English commands into precise SQL queries
- **Interactive CLI**: User-friendly command-line interface with color coding
- **Schema Analysis**: Automatic detection of table relationships and join patterns
- **Query Preview**: Review generated SQL before execution
- **Export Functionality**: Save results to CSV files
- **Database Insights**: Explore table schemas and relationships with simple commands

## 🖥️ Demo

![Prompt2Query Demo](https://raw.githubusercontent.com/yourusername/prompt2query/main/assets/demo.gif)

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- PostgreSQL database
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/prompt2query.git
   cd prompt2query
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys and database credentials:
   ```
   # OpenAI configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # PostgreSQL configuration
   DB_HOST=localhost
   DB_DATABASE=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_PORT=5432
   ```

### Usage

Run the main CLI application:
```bash
python main_cli.py
```

#### Available Commands

- `help` - Display help information
- `tables` - List all available tables
- `schema` - Show complete database schema
- `clear` - Clear the screen
- `exit` - Exit the application

#### Example Queries

```
>> Show me all users who joined last month
>> What are the top 5 products by revenue?
>> Find customers who have purchased more than 3 products
```

## 🛠️ Architecture

The application consists of several components:

- **main_cli.py**: Main entry point with CLI interface
- **db.py**: Database connection and schema analysis
- **openai_client.py**: Integration with OpenAI API for natural language processing
- **query_executor.py**: SQL query execution logic
- **utils.py**: Utility functions for formatting and exporting results

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Contact

Project Link: [https://github.com/hipjim/prompt2query](https://github.com/hipjim/prompt2query)

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for their powerful language models
- [Rich](https://github.com/Textualize/rich) for beautiful terminal formatting
- [SQLParse](https://github.com/andialbrecht/sqlparse) for SQL formatting

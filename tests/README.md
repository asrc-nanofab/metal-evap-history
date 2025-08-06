# Tests

This directory contains tests and debugging utilities for the metal evaporation history application.

## Structure

- `test_database.py` - Database connection and data integrity tests
- `test_data_service.py` - Data service functionality tests
- `__init__.py` - Makes this a Python package

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_database.py
```

### Run with verbose output:
```bash
pytest -v
```

### Run debug function directly:
```bash
python tests/test_database.py
```

## Test Functions

### Database Tests (`test_database.py`)
- `test_database_connection()` - Tests database connectivity
- `test_tables_exist()` - Verifies all required tables exist
- `test_data_integrity()` - Checks data relationships and structure
- `debug_database_contents()` - Debug function to inspect database contents

### Data Service Tests (`test_data_service.py`)
- `test_format_tool_data_empty()` - Tests formatting empty data
- `test_format_tool_data_with_data()` - Tests formatting with mock data
- `test_get_view_data_structure()` - Tests the main data retrieval function

## Debugging

The `debug_database_contents()` function can be used to inspect what's in the database:

```python
from tests.test_database import debug_database_contents
debug_database_contents()
```

This will log information about all tables and their contents. 
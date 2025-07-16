# Tau2 Domains

This folder contains the domains for the Tau2 project.

## Domain Structure

Each domain has its own folder with the following structure:

- `data_model.py`: Defines the data models for the domain. 
    - This implements the `DB` class, which is a base class for all domain databases.
- `user_data_model.py`: Defines the data models for the user data for the domain. (Optional)
    - This implements the `DB` class, which is a base class for all domain user databases.
- `tools.py`: Defines the tools for the domain. 
    - Implements `ToolKitBase` class, which is a base class for all domain toolkits. 
- `user_tools.py`: Defines the user tools for the domain. (Optional)
    - Implements `ToolKitBase` class, which is a base class for all domain toolkits. 
- `environment.py`: Defines the environment for the domain. 
    - Implements `get_environment()` functions that returns an `Environment` instance for the domain.
    - Implements `get_tasks()` functions that returns a list of tasks for the domain.
- `utils.py`: Defines the utility functions for the domain.

## Data Storage

All the data for the domain is stored in:
- `tasks.json`: A JSON file containing the tasks for the domain.
- `policy.md`: A markdown file containing the policy for the domain.
- `db.json` or `db.toml`: A JSON or TOML file containing the database for the domain.
- `user_db.json` or `user_db.toml`: A JSON or TOML file containing the user database for the domain. (Optional)


## Tests
All the tests for the domain are stored in:
- `test_tools_<domain_name>.py`: Contains tests for the tools for the domain.
- `test_user_tools_<domain_name>.py`: Contains tests for the user tools for the domain (if any)